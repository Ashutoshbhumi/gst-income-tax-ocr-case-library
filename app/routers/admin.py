from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User,AuditLog
from ..security import require_roles,hash_password
router=APIRouter(prefix="/api/admin",tags=["admin"])
@router.get("/users")
def users(db:Session=Depends(get_db),admin=Depends(require_roles("ADMIN"))):
    return [{"id":u.id,"email":u.email,"name":u.full_name,"role":u.role,"active":u.is_active} for u in db.query(User).all()]
@router.get("/audit")
def audit(db:Session=Depends(get_db),admin=Depends(require_roles("ADMIN"))):
    return [{"id":a.id,"user_id":a.user_id,"action":a.action,"entity":a.entity_type,"entity_id":a.entity_id,"detail":a.detail,"created_at":a.created_at.isoformat()} for a in db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(500).all()]
