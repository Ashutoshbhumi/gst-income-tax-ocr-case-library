from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import ClientCase, Task

def upcoming(db:Session, user_id:int|None=None, days=30):
    now=datetime.utcnow()
    end=now+timedelta(days=days)
    cases=db.query(ClientCase).filter(ClientCase.status!="CLOSED").all()
    items=[]
    for c in cases:
        for label, dt in [("Reply due",c.reply_due_date),("Hearing",c.next_hearing),("Limitation",c.limitation_last_date)]:
            if dt and now <= dt <= end:
                items.append({"type":label,"case_id":c.id,"title":c.title,"date":dt.isoformat()})
    tasks=db.query(Task).filter(Task.completed==False).all()
    for t in tasks:
        if user_id is not None and t.assigned_to != user_id: continue
        if t.due_date and now <= t.due_date <= end:
            items.append({"type":"Task","case_id":t.client_case_id,"title":t.title,"date":t.due_date.isoformat()})
    return sorted(items,key=lambda x:x["date"])
