from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import OCRDocument
from ..security import current_user
from ..config import settings
from ..services.ocr_service import process_document
from ..services.export_service import text_txt,text_docx,text_csv
from ..services.audit_service import audit
import json

router=APIRouter(prefix="/api/ocr",tags=["ocr"])

@router.post("/process")
async def process(file:UploadFile=File(...), lang="eng", db:Session=Depends(get_db), user=Depends(current_user)):
    allowed={".jpg",".jpeg",".png",".pdf"}
    ext=Path(file.filename or "").suffix.lower()
    if ext not in allowed: raise HTTPException(400,"Supported formats: JPG, PNG, PDF")
    data=await file.read()
    if len(data)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"File too large")
    out_dir=Path(settings.storage_dir)/"ocr"/str(user.id); out_dir.mkdir(parents=True,exist_ok=True)
    stored=out_dir/f"{uuid4().hex}{ext}"; stored.write_bytes(data)
    try: text,pages,conf,confidence_lines=process_document(data,ext,lang)
    except Exception as e: raise HTTPException(500,f"OCR processing failed: {e}")
    row=OCRDocument(user_id=user.id,original_name=file.filename,source_path=str(stored),page_count=pages,
                    extracted_text=text,avg_confidence=conf,confidence_json=json.dumps(confidence_lines),language=lang,status="COMPLETED")
    db.add(row); audit(db,user,"OCR_PROCESS","OCRDocument",row.id,{"filename":file.filename}); db.commit(); db.refresh(row)
    return {"id":row.id,"filename":row.original_name,"pages":pages,"confidence":conf,"confidence_lines":confidence_lines,"text":text}

@router.get("/history")
def history(db:Session=Depends(get_db),user=Depends(current_user)):
    rows=db.query(OCRDocument).filter(OCRDocument.user_id==user.id).order_by(OCRDocument.created_at.desc()).all()
    return [{"id":r.id,"filename":r.original_name,"pages":r.page_count,"confidence":r.avg_confidence,"created_at":r.created_at.isoformat()} for r in rows]

@router.get("/{doc_id}")
def get_doc(doc_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    r=db.get(OCRDocument,doc_id)
    if not r or r.user_id!=user.id: raise HTTPException(404,"Document not found")
    return {"id":r.id,"filename":r.original_name,"pages":r.page_count,"confidence":r.avg_confidence,"confidence_lines":json.loads(r.confidence_json or "[]"),"text":r.extracted_text}


@router.get("/{doc_id}/source")
def source(doc_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    r=db.get(OCRDocument,doc_id)
    if not r or r.user_id!=user.id: raise HTTPException(404,"Document not found")
    return FileResponse(r.source_path, filename=r.original_name)
@router.put("/{doc_id}")
def update_doc(doc_id:int,payload:dict,db:Session=Depends(get_db),user=Depends(current_user)):
    r=db.get(OCRDocument,doc_id)
    if not r or r.user_id!=user.id: raise HTTPException(404,"Document not found")
    r.extracted_text=str(payload.get("text","")); db.commit()
    return {"ok":True}

@router.get("/{doc_id}/export/{kind}")
def export_doc(doc_id:int,kind:str,db:Session=Depends(get_db),user=Depends(current_user)):
    r=db.get(OCRDocument,doc_id)
    if not r or r.user_id!=user.id: raise HTTPException(404,"Document not found")
    if kind=="txt": data,media=text_txt(r.extracted_text),"text/plain"
    elif kind=="docx": data,media=text_docx(r.extracted_text),"application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif kind=="csv": data,media=text_csv(r.extracted_text),"text/csv"
    else: raise HTTPException(400,"Use txt, docx or csv")
    return StreamingResponse(iter([data]),media_type=media,headers={"Content-Disposition":f'attachment; filename="{Path(r.original_name).stem}.{kind}"'})
