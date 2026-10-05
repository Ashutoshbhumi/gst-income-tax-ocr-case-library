from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Boolean, Float, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

case_law_tags = Table(
    "case_law_tags", Base.metadata,
    Column("case_law_id", ForeignKey("case_laws.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
client_case_precedents = Table(
    "client_case_precedents", Base.metadata,
    Column("client_case_id", ForeignKey("client_cases.id"), primary_key=True),
    Column("case_law_id", ForeignKey("case_laws.id"), primary_key=True),
)

class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str]=mapped_column(String(200))
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(20), default="JUNIOR")
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    ocr_documents=relationship("OCRDocument", back_populates="owner")
    audit_logs=relationship("AuditLog", back_populates="user")

class OCRDocument(Base):
    __tablename__="ocr_documents"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"), index=True)
    original_name: Mapped[str]=mapped_column(String(255))
    source_path: Mapped[str]=mapped_column(String(500))
    page_count: Mapped[int]=mapped_column(Integer, default=1)
    extracted_text: Mapped[str]=mapped_column(Text, default="")
    avg_confidence: Mapped[float]=mapped_column(Float, default=0)
    confidence_json: Mapped[str]=mapped_column(Text, default="[]")
    language: Mapped[str]=mapped_column(String(20), default="eng")
    status: Mapped[str]=mapped_column(String(30), default="COMPLETED")
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    owner=relationship("User", back_populates="ocr_documents")

class Client(Base):
    __tablename__="clients"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(255), index=True)
    pan: Mapped[str|None]=mapped_column(String(20), index=True)
    gstin: Mapped[str|None]=mapped_column(String(20), index=True)
    contact_email: Mapped[str|None]=mapped_column(String(255))
    notes: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    cases=relationship("ClientCase", back_populates="client")

class Tag(Base):
    __tablename__="tags"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True, index=True)
    category: Mapped[str]=mapped_column(String(50), default="KEYWORD")
    case_laws=relationship("CaseLaw", secondary=case_law_tags, back_populates="tags")

class CaseLaw(Base):
    __tablename__="case_laws"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(500), index=True)
    parties: Mapped[str|None]=mapped_column(String(500))
    tax_head: Mapped[str]=mapped_column(String(30), default="INCOME_TAX", index=True)
    forum: Mapped[str]=mapped_column(String(100), index=True)
    sections: Mapped[str|None]=mapped_column(Text)
    issue: Mapped[str|None]=mapped_column(Text, index=True)
    assessment_year: Mapped[str|None]=mapped_column(String(20), index=True)
    decision_date: Mapped[datetime|None]=mapped_column(DateTime, index=True)
    citation: Mapped[str|None]=mapped_column(String(500), index=True)
    outcome: Mapped[str]=mapped_column(String(50), default="MIXED", index=True)
    summary: Mapped[str|None]=mapped_column(Text)
    created_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags=relationship("Tag", secondary=case_law_tags, back_populates="case_laws")
    documents=relationship("Document", back_populates="case_law")
    versions=relationship("CaseLawVersion", back_populates="case_law", cascade="all, delete-orphan")

class CaseLawVersion(Base):
    __tablename__="case_law_versions"
    id: Mapped[int]=mapped_column(primary_key=True)
    case_law_id: Mapped[int]=mapped_column(ForeignKey("case_laws.id"))
    changed_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    snapshot: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    case_law=relationship("CaseLaw", back_populates="versions")

class ClientCase(Base):
    __tablename__="client_cases"
    id: Mapped[int]=mapped_column(primary_key=True)
    client_id: Mapped[int]=mapped_column(ForeignKey("clients.id"), index=True)
    title: Mapped[str]=mapped_column(String(500))
    tax_head: Mapped[str]=mapped_column(String(30), default="INCOME_TAX")
    level: Mapped[str]=mapped_column(String(100), default="AO")
    pan: Mapped[str|None]=mapped_column(String(20))
    gstin: Mapped[str|None]=mapped_column(String(20))
    relevant_years: Mapped[str|None]=mapped_column(String(200))
    officer_details: Mapped[str|None]=mapped_column(Text)
    key_issues: Mapped[str|None]=mapped_column(Text)
    monetary_exposure: Mapped[float]=mapped_column(Float, default=0)
    status: Mapped[str]=mapped_column(String(50), default="OPEN", index=True)
    notice_date: Mapped[datetime|None]=mapped_column(DateTime)
    reply_due_date: Mapped[datetime|None]=mapped_column(DateTime, index=True)
    next_hearing: Mapped[datetime|None]=mapped_column(DateTime, index=True)
    order_date: Mapped[datetime|None]=mapped_column(DateTime)
    limitation_last_date: Mapped[datetime|None]=mapped_column(DateTime, index=True)
    visibility_user_ids: Mapped[str]=mapped_column(Text, default="")
    created_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    client=relationship("Client", back_populates="cases")
    precedents=relationship("CaseLaw", secondary=client_case_precedents)

class Document(Base):
    __tablename__="documents"
    id: Mapped[int]=mapped_column(primary_key=True)
    case_law_id: Mapped[int|None]=mapped_column(ForeignKey("case_laws.id"), index=True)
    client_case_id: Mapped[int|None]=mapped_column(ForeignKey("client_cases.id"), index=True)
    uploaded_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    filename: Mapped[str]=mapped_column(String(255))
    path: Mapped[str]=mapped_column(String(500))
    document_type: Mapped[str]=mapped_column(String(50), default="OTHER")
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    case_law=relationship("CaseLaw", back_populates="documents")

class PracticeNote(Base):
    __tablename__="practice_notes"
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(String(300))
    content: Mapped[str]=mapped_column(Text)
    issue_type: Mapped[str|None]=mapped_column(String(100))
    created_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class Template(Base):
    __tablename__="templates"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(300))
    forum: Mapped[str|None]=mapped_column(String(100))
    issue_type: Mapped[str|None]=mapped_column(String(100))
    content: Mapped[str]=mapped_column(Text)
    created_by: Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__="tasks"
    id: Mapped[int]=mapped_column(primary_key=True)
    client_case_id: Mapped[int]=mapped_column(ForeignKey("client_cases.id"), index=True)
    assigned_to: Mapped[int]=mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str]=mapped_column(String(300))
    description: Mapped[str|None]=mapped_column(Text)
    due_date: Mapped[datetime|None]=mapped_column(DateTime, index=True)
    completed: Mapped[bool]=mapped_column(Boolean, default=False)
    reminder_days: Mapped[int]=mapped_column(Integer, default=7)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int|None]=mapped_column(ForeignKey("users.id"))
    action: Mapped[str]=mapped_column(String(100), index=True)
    entity_type: Mapped[str]=mapped_column(String(100))
    entity_id: Mapped[str|None]=mapped_column(String(50))
    detail: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow, index=True)
    user=relationship("User", back_populates="audit_logs")
