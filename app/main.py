from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .config import settings
from .database import Base, engine, SessionLocal
from .models import User,Client,CaseLaw
from .security import hash_password
from .routers import auth,ocr,cases,clients,tasks,notes,dashboard,reports,admin

Base.metadata.create_all(bind=engine)
Path(settings.storage_dir).mkdir(parents=True,exist_ok=True)

def seed():
    db=SessionLocal()
    demo=[
        ("admin@example.com","Demo Admin","Admin@123","ADMIN"),
        ("senior@example.com","Demo Senior","Senior@123","SENIOR"),
        ("junior@example.com","Demo Junior","Junior@123","JUNIOR"),
        ("client@example.com","Demo Client","Client@123","CLIENT"),
    ]
    for email,name,pw,role in demo:
        if not db.query(User).filter(User.email==email).first():
            db.add(User(email=email,full_name=name,password_hash=hash_password(pw),role=role))
    db.commit()
    if db.query(CaseLaw).count()==0:
        u=db.query(User).filter(User.email=="senior@example.com").first()
        samples=[
          CaseLaw(title="Sample GST ITC case — replace with verified source",parties="Sample Assessee v. Department",
                  tax_head="GST",forum="ITAT",sections="Section 16",issue="Input tax credit",assessment_year="2024-25",
                  citation="Sample citation",outcome="MIXED",summary="Demonstration record only; replace with verified case-law data.",created_by=u.id),
          CaseLaw(title="Sample Income Tax reassessment case",parties="Sample Assessee v. Department",
                  tax_head="INCOME_TAX",forum="HIGH_COURT",sections="Sections 147/148",issue="Reassessment",
                  assessment_year="2023-24",citation="Sample citation",outcome="ASSESSEE_FAVOURABLE",
                  summary="Demonstration record only; replace with verified case-law data.",created_by=u.id)
        ]
        db.add_all(samples); db.commit()
    db.close()
seed()

app=FastAPI(title=settings.app_name,version="1.0.0",description="SRS-based OCR and Indian tax case library reference implementation")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
templates=Jinja2Templates(directory="app/templates")
for r in [auth,ocr,cases,clients,tasks,notes,dashboard,reports,admin]: app.include_router(r.router)

@app.get("/",response_class=HTMLResponse)
def index(request:Request): return templates.TemplateResponse("index.html",{"request":request})
@app.get("/health")
def health(): return {"status":"ok"}
