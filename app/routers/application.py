from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.services.ai_service import analyze_resume_against_jd
from app.cores.database import get_db
from app.cores.security import get_current_user
from app.models.application import Application
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_application = Application(
        user_id=current_user.id,
        **application.model_dump()
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@router.get("", response_model=List[ApplicationOut])
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Application).filter(Application.user_id == current_user.id).all()


@router.get("/{id}", response_model=ApplicationOut)
def get_application(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    return application


@router.put("/{id}", response_model=ApplicationOut)
def update_application(
    id: int,
    updated_application: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application_query = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    )
    application = application_query.first()

    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    update_data = updated_application.model_dump(exclude_unset=True)
    application_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application_query = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    )
    application = application_query.first()

    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    application_query.delete(synchronize_session=False)
    db.commit()
    return None

@router.post("/{id}/analyze", status_code=status.HTTP_200_OK)
def analyze_application(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.query(Application).filter(
        Application.id == id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if not application.jd_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No job description set for this application")

    if not current_user.resume_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No resume uploaded for this user")

    try:
        result = analyze_resume_against_jd(current_user.resume_text, application.jd_text)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    return result