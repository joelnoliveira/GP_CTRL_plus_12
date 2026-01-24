from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Base
from ..schemas import UserLogin, Token, UserCreate, UserResponse
from ..security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_password_hash,
    get_current_user,
)
from datetime import timedelta, datetime
import os
import requests
import json

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SECRET_KEY = os.environ.get("REACT_APP_RECAPTCHA_SECRET_KEY")


def verify_recaptcha(token: str):
    if not RECAPTCHA_SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="reCAPTCHA secret key is not configured in environment variables",
        )

    payload = {"secret": RECAPTCHA_SECRET_KEY, "response": token}

    try:
        response = requests.post(RECAPTCHA_VERIFY_URL, params=payload)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not connect to reCAPTCHA service",
        )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid reCAPTCHA. {result.get('error-codes')}",
        )

    return True


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # verify_recaptcha(user_data.captcha_token)

    if not hasattr(Base.classes, "users"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database tables not reflected yet",
        )

    User = Base.classes.users

    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        role=False,  # Regular user
        created_at=datetime.now(),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    # verify_recaptcha(user_credentials.captcha_token)

    if not hasattr(Base.classes, "users"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database tables not reflected yet",
        )

    # Gets users table and creates a python class
    User = Base.classes.users

    user = db.query(User).filter(User.email == user_credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )

    # Audit log
    AuditLog = Base.classes.audit_logs
    audit_entry = AuditLog(
        user_id=user.id,
        endpoint="/auth/login",
        request_body=json.dumps({"email": user_credentials.email}),
        created_at=datetime.now(),
    )
    db.add(audit_entry)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


# Example endpoint to see if authentication is working
@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)
):
    if not hasattr(Base.classes, "users"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database tables not reflected yet",
        )

    User = Base.classes.users
    user = db.query(User).filter(User.email == current_user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
