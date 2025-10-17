from sqlalchemy.orm import Session
from sqlalchemy import select 
from typing import List, Optional

from user_models import User
from user_models import UserCreate

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.execute(select(User).filter(User.id == user_id)).scalars().first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        name=user.name, 
        username=user.username, 
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False