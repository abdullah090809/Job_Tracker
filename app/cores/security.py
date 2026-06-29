from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.cores.config import settings
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from app.cores.database import get_db
from app.models.user import User
from app.schemas.token import TokenData
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update["exp": expire]
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def get_current_user(token: str = Depends(oauth2_scheme), db: Session= Depends(get_db())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: int = TokenData(payload.get("user_id"))
        if user_id is None:
            raise credentials_exception
    except:
        raise credentials_exception
    user = db.query(User).filter(user_id == User.id).first()
    if not user:
        raise credentials_exception
    return user

                     