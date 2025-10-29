from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import create_token, verify_password
from crud import user_crud
from models.user_models import User, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    user = user_crud.create_user(db=db, user=user_data)
    return user

@router.post("/login")
async def login(credentials: dict = Body(...), db: Session = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}