from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Form, UploadFile, status
from sqlalchemy.orm import Session
from api.schemas.common import ResponseModel
from api.services.auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
    get_user_by_email,
)
from api.models.user import User
from api.db.database import get_session
from api.services.storage import upload_file

router = APIRouter()
DEFAULT_IMAGE_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register(
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_session),
):
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Username already registered.")
    image_url = DEFAULT_IMAGE_URL
    if profile_image:
        image_url = await upload_file(profile_image)
    user = User(
        email=email,
        password_hash=hash_password(password),
        profile_image=image_url,
        name=name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ResponseModel(
        status="success",
        message="User registered successfully.",
        data={"user_id": user.id},
    )


@router.post("/login/", status_code=status.HTTP_200_OK)
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials.")
    # Expire in 2 days
    access_token = create_access_token(
        data={"sub": user.email}, expires_minutes=60 * 24 * 2
    )
    return ResponseModel(
        status="success",
        message="User logged in successfully.",
        data={"token": access_token},
    )


@router.get("/me/")
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return ResponseModel(
        status="success",
        message="User profile retrieved.",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "profile_image": current_user.profile_image,
            "created_at": current_user.created_at,
        },
    )


@router.put("/me/")
async def update_user_profile(
    name: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    current_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """Update the current user's profile."""
    if name:
        current_user.name = name

    if profile_image:
        uploaded_url = await upload_file(profile_image)
        current_user.profile_image = uploaded_url

    if current_password and new_password:
        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(
                status_code=400, detail="Current password is incorrect."
            )

        current_user.password_hash = hash_password(new_password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return ResponseModel(
        status="success",
        message="User profile updated successfully.",
        data={
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "profile_image": current_user.profile_image,
            "created_at": current_user.created_at,
        },
    )


@router.get("/author/{author_id}/")
def get_author_profile(author_id: int, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.id == author_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ResponseModel(
        status="success",
        message="User profile retrieved.",
        data={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "profile_image": user.profile_image,
            "created_at": user.created_at,
        },
    )
