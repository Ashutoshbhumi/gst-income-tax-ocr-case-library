from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Client
from ..schemas import ClientCreate
from ..security import current_user
from ..services.audit_service import audit
router=APIRouter(prefix="/api/clients",tags=["clients"])

@router.post("")
def create(data:ClientCreate,db:Session=Depends(get_db),user=Depends(current_user)):
    c=Client(**data.model_dump()); db.add(c); db.flush(); audit(db,user,"CREATE","Client",c.id); db.commit()
    return {"id":c.id,"name":c.name,"pan":c.pan,"gstin":c.gstin}
@router.get("")
def list_clients(db:Session=Depends(get_db),user=Depends(current_user)):
    return [{"id":c.id,"name":c.name,"pan":c.pan,"gstin":c.gstin,"email":c.contact_email} for c in db.query(Client).order_by(Client.name).all()]
