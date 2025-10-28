from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel
from typing import List, Optional

from database import Base 
from user_models import User 

class UserProjectAssociation(Base):
    __tablename__ = 'user_project_association'
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete="CASCADE"), primary_key=True)
    
    is_creator: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user: Mapped["User"] = relationship(back_populates="projects_association")
    
    project: Mapped["Project"] = relationship(back_populates="members_association")

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    
    members_association: Mapped[List[UserProjectAssociation]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan"
    )

    task_association: Mapped[List["TaskProjectAssociation"]] = relationship(
        back_populates='project',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class ProjectMember(BaseModel):
    user_id: int
    username: str
    is_creator: bool
    
    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    
    members: List[ProjectMember] = []

    class Config:
        from_attributes = True

class ProjectInvite(BaseModel):
    project_id: int
    user_id: int
    is_creator: bool = False