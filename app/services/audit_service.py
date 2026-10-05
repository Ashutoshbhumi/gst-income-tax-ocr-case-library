import json
from sqlalchemy.orm import Session
from ..models import AuditLog, User

def audit(db:Session, user:User|None, action:str, entity_type:str, entity_id=None, detail=None):
    row=AuditLog(user_id=user.id if user else None, action=action, entity_type=entity_type,
                 entity_id=str(entity_id) if entity_id is not None else None,
                 detail=json.dumps(detail, default=str) if detail is not None else None)
    db.add(row)
