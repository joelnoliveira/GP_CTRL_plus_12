from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Base
from ..schemas import UserLogin, Token, UserCreate, UserResponse
from ..security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, get_current_user
from datetime import timedelta, datetime

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if not hasattr(Base.classes, 'users'):
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database tables not reflected yet")
    
    User = Base.classes.users
    
    #Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    #Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        role=False, #Regular user
        created_at=datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    if not hasattr(Base.classes, 'users'):
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database tables not reflected yet")
    
    #Gets users table and creates a python class
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
    return {"access_token": access_token, "token_type": "bearer"}


#Example endpoint to see if authentication is working
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user_email: str = Depends(get_current_user), db: Session = Depends(get_db)):
    if not hasattr(Base.classes, 'users'):
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database tables not reflected yet")
    
    User = Base.classes.users
    user = db.query(User).filter(User.email == current_user_email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
