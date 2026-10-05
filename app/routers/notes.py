from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import PracticeNote,Template
from ..schemas import NoteCreate,TemplateCreate
from ..security import current_user
router=APIRouter(prefix="/api/knowledge",tags=["knowledge"])
@router.post("/notes")
def note(data:NoteCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    n=PracticeNote(**data.model_dump(),created_by=user.id); db.add(n); db.commit(); db.refresh(n); return {"id":n.id}
@router.get("/notes")
def notes(db:Session=Depends(get_db),user=Depends(current_user)):
    return [{"id":n.id,"title":n.title,"issue_type":n.issue_type,"content":n.content} for n in db.query(PracticeNote).order_by(PracticeNote.created_at.desc()).all()]
@router.post("/templates")
def template(data:TemplateCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    t=Template(**data.model_dump(),created_by=user.id); db.add(t); db.commit(); db.refresh(t); return {"id":t.id}
@router.get("/templates")
def templates(db:Session=Depends(get_db),user=Depends(current_user)):
    return [{"id":t.id,"name":t.name,"forum":t.forum,"issue_type":t.issue_type,"content":t.content} for t in db.query(Template).all()]
