from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Task
from ..schemas import TaskCreate
from ..security import current_user
from ..services.reminder_service import upcoming
router=APIRouter(prefix="/api/tasks",tags=["tasks"])

@router.post("")
def create(data:TaskCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    t=Task(**data.model_dump()); db.add(t); db.commit(); db.refresh(t)
    return {"id":t.id,"title":t.title,"due_date":t.due_date.isoformat() if t.due_date else None}
@router.get("")
def list_tasks(db:Session=Depends(get_db),user=Depends(current_user)):
    rows=db.query(Task).filter(Task.assigned_to==user.id).order_by(Task.due_date).all()
    return [{"id":t.id,"case_id":t.client_case_id,"title":t.title,"due_date":t.due_date.isoformat() if t.due_date else None,"completed":t.completed} for t in rows]
@router.get("/upcoming")
def upcoming_tasks(db:Session=Depends(get_db),user=Depends(current_user)):
    return upcoming(db,user.id)
@router.post("/{task_id}/complete")
def complete(task_id:int,db:Session=Depends(get_db),user=Depends(current_user)):
    t=db.get(Task,task_id); t.completed=True; db.commit(); return {"ok":True}
