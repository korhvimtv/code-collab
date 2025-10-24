from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from database import Base
from sqlalchemy.orm import relationship, Mapped
from typing import List, Optional

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, index = True)
    username = Column(String, unique = True, index = True)
    email = Column(String, unique = True, index = True)

    projects_association: Mapped[List["UserProjectAssociation"]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    task_association: Mapped[List["TaskProjectAssociation"]] = relationship(
        back_populates='user',
    )

class UserCreate(BaseModel):
    name: str
    username: str
    email: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str

    class Config:
        from_attributes = True