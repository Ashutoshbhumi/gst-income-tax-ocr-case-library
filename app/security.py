from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from .models import User

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def hash_password(password:str)->str:
    return pwd_context.hash(password)
def verify_password(plain:str, hashed:str)->bool:
    return pwd_context.verify(plain, hashed)
def create_access_token(user:User)->str:
    expire=datetime.utcnow()+timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub":str(user.id),"role":user.role,"exp":expire}, settings.secret_key, algorithm="HS256")
def current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db))->User:
    exc=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")
    try:
        payload=jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        uid=int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise exc
    user=db.get(User, uid)
    if not user or not user.is_active: raise exc
    return user
def require_roles(*roles):
    def dep(user:User=Depends(current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dep
