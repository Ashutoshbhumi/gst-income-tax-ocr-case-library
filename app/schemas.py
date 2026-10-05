from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "JUNIOR"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ClientCreate(BaseModel):
    name: str
    pan: str|None=None
    gstin: str|None=None
    contact_email: EmailStr|None=None
    notes: str|None=None

class CaseLawCreate(BaseModel):
    title: str
    parties: str|None=None
    tax_head: str="INCOME_TAX"
    forum: str="ITAT"
    sections: str|None=None
    issue: str|None=None
    assessment_year: str|None=None
    decision_date: datetime|None=None
    citation: str|None=None
    outcome: str="MIXED"
    summary: str|None=None
    tags: list[str]=[]

class ClientCaseCreate(BaseModel):
    client_id: int
    title: str
    tax_head: str="INCOME_TAX"
    level: str="AO"
    pan: str|None=None
    gstin: str|None=None
    relevant_years: str|None=None
    officer_details: str|None=None
    key_issues: str|None=None
    monetary_exposure: float=0
    status: str="OPEN"
    notice_date: datetime|None=None
    reply_due_date: datetime|None=None
    next_hearing: datetime|None=None
    order_date: datetime|None=None
    limitation_last_date: datetime|None=None
    visibility_user_ids: str=""

class TaskCreate(BaseModel):
    client_case_id: int
    assigned_to: int
    title: str
    description: str|None=None
    due_date: datetime|None=None
    reminder_days: int=7

class NoteCreate(BaseModel):
    title: str
    content: str
    issue_type: str|None=None

class TemplateCreate(BaseModel):
    name: str
    forum: str|None=None
    issue_type: str|None=None
    content: str
