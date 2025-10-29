from sqlalchemy.orm import Session
from sqlalchemy import select 
from typing import List, Optional, Dict, Any

from models.user_models import User, UserCreate, UserUpdate
from core.auth import create_password_hash


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.execute(select(User).filter(User.id == user_id)).scalars().first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.execute(select(User).offset(skip).limit(limit)).scalars().all()

def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password_hash=create_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        return None

    update_data: Dict[str, Any] = user.model_dump(exclude_unset=True)
    if 'password' in update_data:
        update_data['password_hash'] = create_password_hash(update_data.pop('password'))

    for key, value in update_data.items():
        setattr(db_user, key, value)

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