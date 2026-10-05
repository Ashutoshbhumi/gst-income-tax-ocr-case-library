import json, csv, io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CaseLaw, CaseLawVersion, Tag, Document, ClientCase, Client
from ..schemas import CaseLawCreate, ClientCaseCreate
from ..security import current_user, require_roles
from ..services.audit_service import audit

router=APIRouter(prefix="/api/cases",tags=["cases"])

def serialize_case(c):
    return {"id":c.id,"title":c.title,"parties":c.parties,"tax_head":c.tax_head,"forum":c.forum,"sections":c.sections,
            "issue":c.issue,"assessment_year":c.assessment_year,"decision_date":c.decision_date.isoformat() if c.decision_date else None,
            "citation":c.citation,"outcome":c.outcome,"summary":c.summary,"tags":[t.name for t in c.tags]}

@router.post("/law")
def create_law(data:CaseLawCreate,db:Session=Depends(get_db),user=Depends(require_roles("ADMIN","SENIOR"))):
    c=CaseLaw(**data.model_dump(exclude={"tags"}),created_by=user.id)
    for name in data.tags:
        tag=db.query(Tag).filter(Tag.name==name).first() or Tag(name=name)
        c.tags.append(tag)
    db.add(c); db.flush()
    audit(db,user,"CREATE","CaseLaw",c.id); db.commit(); db.refresh(c)
    return serialize_case(c)

@router.get("/law")
def search_law(q:str|None=None,forum:str|None=None,section:str|None=None,issue:str|None=None,
               assessment_year:str|None=None,outcome:str|None=None,tax_head:str|None=None,
               sort:str="date",page:int=1,size:int=20,db:Session=Depends(get_db),user=Depends(current_user)):
    query=db.query(CaseLaw)
    if q:
        like=f"%{q}%"; query=query.filter(or_(CaseLaw.title.ilike(like),CaseLaw.parties.ilike(like),
            CaseLaw.citation.ilike(like),CaseLaw.issue.ilike(like),CaseLaw.sections.ilike(like),CaseLaw.summary.ilike(like)))
    for col,val in [(CaseLaw.forum,forum),(CaseLaw.issue,issue),(CaseLaw.assessment_year,assessment_year),(CaseLaw.outcome,outcome),(CaseLaw.tax_head,tax_head)]:
        if val: query=query.filter(col.ilike(f"%{val}%"))
    if section: query=query.filter(CaseLaw.sections.ilike(f"%{section}%"))
    if sort=="forum": query=query.order_by(CaseLaw.forum)
    elif sort=="outcome": query=query.order_by(CaseLaw.outcome)
    elif sort=="title": query=query.order_by(CaseLaw.title)
    else: query=query.order_by(CaseLaw.decision_date.desc())
    total=query.count(); rows=query.offset((page-1)*size).limit(size).all()
    return {"items":[serialize_case(x) for x in rows],"page":page,"size":size,"total":total}

@router.get("/law/{case_id}")
def law_detail(case_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    c=db.get(CaseLaw,case_id)
    if not c: raise HTTPException(404,"Case law not found")
    return serialize_case(c)|{"documents":[{"id":d.id,"filename":d.filename,"type":d.document_type} for d in c.documents],
                             "versions":[{"id":v.id,"changed_by":v.changed_by,"created_at":v.created_at.isoformat()} for v in c.versions]}

@router.put("/law/{case_id}")
def update_law(case_id:int,data:CaseLawCreate,db:Session=Depends(get_db),user=Depends(require_roles("ADMIN","SENIOR"))):
    c=db.get(CaseLaw,case_id)
    if not c: raise HTTPException(404,"Case law not found")
    snapshot=json.dumps(serialize_case(c),default=str)
    db.add(CaseLawVersion(case_law_id=c.id,changed_by=user.id,snapshot=snapshot))
    for k,v in data.model_dump(exclude={"tags"}).items(): setattr(c,k,v)
    c.tags=[]
    for name in data.tags:
        tag=db.query(Tag).filter(Tag.name==name).first() or Tag(name=name); c.tags.append(tag)
    audit(db,user,"UPDATE","CaseLaw",c.id); db.commit(); return serialize_case(c)

@router.post("/law/{case_id}/documents")
async def attach_doc(case_id:int,file:UploadFile=File(...),document_type="JUDGMENT",db:Session=Depends(get_db),user=Depends(current_user)):
    c=db.get(CaseLaw,case_id)
    if not c: raise HTTPException(404,"Case not found")
    import pathlib,uuid
    data=await file.read(); out=pathlib.Path("storage")/"case_docs"/str(case_id); out.mkdir(parents=True,exist_ok=True)
    p=out/(uuid.uuid4().hex+"_"+(file.filename or "document")); p.write_bytes(data)
    d=Document(case_law_id=case_id,uploaded_by=user.id,filename=file.filename or "document",path=str(p),document_type=document_type)
    db.add(d); audit(db,user,"UPLOAD","Document",case_id,{"filename":file.filename}); db.commit()
    return {"id":d.id,"filename":d.filename}

@router.post("/law/import-csv")
async def import_csv(file:UploadFile=File(...),db:Session=Depends(get_db),user=Depends(require_roles("ADMIN","SENIOR"))):
    raw=(await file.read()).decode("utf-8-sig"); reader=csv.DictReader(io.StringIO(raw)); count=0
    for row in reader:
        c=CaseLaw(title=row.get("title","Untitled"),parties=row.get("parties"),tax_head=row.get("tax_head","INCOME_TAX"),
                  forum=row.get("forum","ITAT"),sections=row.get("sections"),issue=row.get("issue"),
                  assessment_year=row.get("assessment_year"),citation=row.get("citation"),outcome=row.get("outcome","MIXED"),
                  summary=row.get("summary"),created_by=user.id)
        db.add(c); count+=1
    audit(db,user,"IMPORT","CaseLaw",detail={"rows":count}); db.commit(); return {"imported":count}

@router.post("/client")
def create_client_case(data:ClientCaseCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    if not db.get(Client,data.client_id): raise HTTPException(404,"Client not found")
    c=ClientCase(**data.model_dump(),created_by=user.id); db.add(c); db.flush(); audit(db,user,"CREATE","ClientCase",c.id); db.commit()
    return {"id":c.id,"title":c.title,"status":c.status}

@router.get("/client")
def client_cases(status:str|None=None,client_id:int|None=None,db:Session=Depends(get_db),user=Depends(current_user)):
    q=db.query(ClientCase)
    if status:q=q.filter(ClientCase.status==status)
    if client_id:q=q.filter(ClientCase.client_id==client_id)
    rows=q.order_by(ClientCase.next_hearing).all()
    if user.role not in ("ADMIN","SENIOR"):
        rows=[c for c in rows if not c.visibility_user_ids or str(user.id) in {x.strip() for x in c.visibility_user_ids.split(",") if x.strip()}]
    return [{"id":c.id,"title":c.title,"client":c.client.name,"level":c.level,"status":c.status,
             "exposure":c.monetary_exposure,"reply_due":c.reply_due_date.isoformat() if c.reply_due_date else None,
             "hearing":c.next_hearing.isoformat() if c.next_hearing else None,
             "limitation":c.limitation_last_date.isoformat() if c.limitation_last_date else None} for c in rows]

@router.post("/client/{client_case_id}/precedents/{case_id}")
def link_precedent(client_case_id:int,case_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    cc=db.get(ClientCase,client_case_id); cl=db.get(CaseLaw,case_id)
    if not cc or not cl: raise HTTPException(404,"Case or precedent not found")
    if cl not in cc.precedents: cc.precedents.append(cl)
    audit(db,user,"LINK_PRECEDENT","ClientCase",cc.id,{"case_law_id":case_id}); db.commit(); return {"ok":True}
