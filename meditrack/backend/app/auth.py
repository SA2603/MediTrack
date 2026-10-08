import os, bcrypt, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User

SECRET = os.getenv("SECRET_KEY", "dev-only-change-me")
ALG = os.getenv("ALGORITHM", "HS256")
EXPIRE = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
bearer = HTTPBearer(auto_error=False)

def hash_pw(p): return bcrypt.hashpw(p.encode()[:72], bcrypt.gensalt()).decode()
def verify_pw(p, h): return bcrypt.checkpw(p.encode()[:72], h.encode())
def make_token(u):
    exp = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE)
    return jwt.encode({"sub": str(u.id), "role": u.role, "exp": exp}, SECRET, algorithm=ALG)

def current_user(c=Depends(bearer), db: Session = Depends(get_db)):
    if not c: raise HTTPException(401, "Not authenticated")
    try:
        uid = int(jwt.decode(c.credentials, SECRET, algorithms=[ALG])["sub"])
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    u = db.get(User, uid)
    if not u: raise HTTPException(401, "User not found")
    return u

def require(*roles):
    def dep(u=Depends(current_user)):
        if u.role not in roles: raise HTTPException(403, "Forbidden for your role")
        return u
    return dep
