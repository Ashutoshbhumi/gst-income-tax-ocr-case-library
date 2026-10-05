from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import ClientCase, CaseLaw, Task, AuditLog
from ..security import current_user
from ..services.reminder_service import upcoming
router=APIRouter(prefix="/api/dashboard",tags=["dashboard"])
@router.get("")
def dashboard(db:Session=Depends(get_db),user=Depends(current_user)):
    active=db.query(ClientCase).filter(ClientCase.status!="CLOSED").count()
    total_law=db.query(CaseLaw).count()
    upcoming_items=upcoming(db,user.id,30)
    ageing={}
    from datetime import datetime
    for c in db.query(ClientCase).filter(ClientCase.status!="CLOSED").all():
        age=(datetime.utcnow()-c.created_at).days
        bucket="0-30" if age<=30 else "31-90" if age<=90 else "90+"
        ageing[bucket]=ageing.get(bucket,0)+1
    top=db.query(CaseLaw.forum,func.count(CaseLaw.id)).group_by(CaseLaw.forum).order_by(func.count(CaseLaw.id).desc()).limit(5).all()
    return {"active_cases":active,"case_laws":total_law,"upcoming":upcoming_items[:10],"ageing":ageing,
            "frequent_forums":[{"forum":x,"count":n} for x,n in top]}
