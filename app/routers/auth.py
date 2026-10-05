from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, Token
from ..security import hash_password, verify_password, create_access_token, current_user
from ..services.audit_service import audit

router=APIRouter(prefix="/api/auth",tags=["auth"])

@router.post("/register")
def register(data:UserCreate, db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email).first(): raise HTTPException(400,"Email already registered")
    user=User(email=data.email,full_name=data.full_name,password_hash=hash_password(data.password),role=data.role)
    db.add(user); db.commit(); db.refresh(user); audit(db,user,"REGISTER","User",user.id); db.commit()
    return {"id":user.id,"email":user.email,"role":user.role}

@router.post("/login",response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==form.username).first()
    if not user or not verify_password(form.password,user.password_hash): raise HTTPException(401,"Invalid credentials")
    audit(db,user,"LOGIN","User",user.id); db.commit()
    return Token(access_token=create_access_token(user))

@router.get("/me")
def me(user=Depends(current_user)):
    return {"id":user.id,"email":user.email,"full_name":user.full_name,"role":user.role}
