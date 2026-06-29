from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.cores.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.cores.database import get_db

router = APIRouter(
    prefix="/users",
    tags=["login"]
)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user