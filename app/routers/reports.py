import csv,io
from fastapi import APIRouter,Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import ClientCase,CaseLaw
from ..security import current_user
from ..services.export_service import table_xlsx, table_pdf
router=APIRouter(prefix="/api/reports",tags=["reports"])

def download(data, media, filename):
    return StreamingResponse(iter([data]),media_type=media,headers={"Content-Disposition":f"attachment; filename={filename}"})

def law_rows(db):
    return [[c.id,c.title,c.forum,c.tax_head,c.sections,c.issue,c.assessment_year,c.citation,c.outcome] for c in db.query(CaseLaw).all()]
def case_rows(db):
    return [[c.id,c.title,c.client_id,c.level,c.status,c.monetary_exposure,c.reply_due_date,c.next_hearing,c.limitation_last_date] for c in db.query(ClientCase).all()]

@router.get("/client-cases.csv")
def client_cases_csv(db:Session=Depends(get_db),user=Depends(current_user)):
    rows=case_rows(db); out=io.StringIO(); w=csv.writer(out); headers=["id","title","client_id","level","status","exposure","reply_due","hearing","limitation"]; w.writerow(headers)
    w.writerows(rows); return download(out.getvalue().encode(),"text/csv","client_cases.csv")
@router.get("/case-laws.csv")
def laws_csv(db:Session=Depends(get_db),user=Depends(current_user)):
    rows=law_rows(db); out=io.StringIO(); w=csv.writer(out); headers=["id","title","forum","tax_head","sections","issue","assessment_year","citation","outcome"]; w.writerow(headers); w.writerows(rows)
    return download(out.getvalue().encode(),"text/csv","case_laws.csv")
@router.get("/client-cases.xlsx")
def client_cases_xlsx(db:Session=Depends(get_db),user=Depends(current_user)):
    headers=["id","title","client_id","level","status","exposure","reply_due","hearing","limitation"]
    return download(table_xlsx(case_rows(db),headers),"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","client_cases.xlsx")
@router.get("/case-laws.xlsx")
def laws_xlsx(db:Session=Depends(get_db),user=Depends(current_user)):
    headers=["id","title","forum","tax_head","sections","issue","assessment_year","citation","outcome"]
    return download(table_xlsx(law_rows(db),headers),"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","case_laws.xlsx")
@router.get("/client-cases.pdf")
def client_cases_pdf(db:Session=Depends(get_db),user=Depends(current_user)):
    headers=["ID","Title","Client","Level","Status","Exposure","Reply","Hearing","Limitation"]
    return download(table_pdf(case_rows(db),headers,"Client Case Report"),"application/pdf","client_cases.pdf")
@router.get("/case-laws.pdf")
def laws_pdf(db:Session=Depends(get_db),user=Depends(current_user)):
    headers=["ID","Title","Forum","Tax","Sections","Issue","AY","Citation","Outcome"]
    return download(table_pdf(law_rows(db),headers,"Case Law Report"),"application/pdf","case_laws.pdf")
@router.get("/calendar.ics")
def calendar(db:Session=Depends(get_db),user=Depends(current_user)):
    from ..services.reminder_service import upcoming
    items=upcoming(db,user.id,365); lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//TaxCase//EN"]
    for i,x in enumerate(items):
        dt=x["date"].replace("-","").replace(":","").split(".")[0]+"Z"
        lines += ["BEGIN:VEVENT",f"UID:taxcase-{i}@local",f"DTSTART:{dt}",f"SUMMARY:{x['type']}: {x['title']}","END:VEVENT"]
    lines.append("END:VCALENDAR")
    return download("\r\n".join(lines).encode(),"text/calendar","taxcase.ics")
