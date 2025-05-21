from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..models import User
from ..config import get_db, ALGORITHM
from ..utils.encryption import encryption
from pydantic import BaseModel, Field
import jwt
import uuid
import os

router = APIRouter()

# Generate a secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(32).hex())

class UserCreate(BaseModel):
    pgp_key: str = Field(..., min_length=100)  # Minimum length for a valid PGP key
    is_seller: bool = False

class UserResponse(BaseModel):
    id: str
    is_seller: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token for user authentication"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserResponse)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with PGP key
    """
    try:
        # Verify PGP key is valid
        if not encryption.verify_pgp_key(user.pgp_key):
            raise HTTPException(
                status_code=400,
                detail="Invalid PGP key"
            )

        # Check if PGP key already exists
        existing_user = db.query(User).filter(User.pgp_key == user.pgp_key).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="PGP key already registered"
            )

        # Create new user
        db_user = User(
            id=str(uuid.uuid4()),
            pgp_key=user.pgp_key,
            is_seller=user.is_seller
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    pgp_key: str,
    db: Session = Depends(get_db)
):
    """
    Login with PGP key and receive JWT token
    """
    # Find user by PGP key
    user = db.query(User).filter(User.pgp_key == pgp_key).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid PGP key"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "is_seller": user.is_seller},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Dependency for protected routes
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

# Dependency for seller-only routes
async def get_current_seller(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_seller:
        raise HTTPException(
            status_code=403,
            detail="Seller privileges required"
        )
    return current_user
