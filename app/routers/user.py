from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.cores.security import hash_password, verify_password, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, PasswordUpdate
from app.cores.database import get_db
from fastapi import UploadFile, File
from app.services.resume_service import extract_text_from_pdf

router = APIRouter(
    prefix="/users",
    tags=["login"]
)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=list[UserOut], status_code=status.HTTP_200_OK)
def get_all_user(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.put("", status_code=status.HTTP_200_OK)
def update_password(
    password_data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
):
    user_query = db.query(User).filter(User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_query.delete(synchronize_session=False)
    db.commit()
    return None

@router.post("/resume", status_code=status.HTTP_200_OK)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    file_bytes = file.file.read()
    resume_text = extract_text_from_pdf(file_bytes)

    current_user.resume_text = resume_text
    db.commit()

    return {"message": "Resume uploaded successfully", "characters_extracted": len(resume_text)}