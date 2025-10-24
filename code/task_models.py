from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel
from typing import List, Optional

from database import Base 
from user_models import User
from project_models import Project


class TaskProjectAssociation(Base):
    __tablename__ = 'task_project_association'

    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)

    task: Mapped["Task"] = relationship(back_populates='project_association')
    user: Mapped[User] = relationship(back_populates='task_association')
    project: Mapped[Project] = relationship(back_populates='task_association')

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    deadline = Column(DateTime)

    project_association: Mapped[List[TaskProjectAssociation]] = relationship(
        back_populates='task'
    )

    members_associations: Mapped[List[TaskProjectAssociation]] = relationship(
        back_populates='task',
        cascade='all, delete-orphan'
    )

class TaskCreate(BaseModel):
    title: str
    description: str
    deadline: datetime

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class TaskProject(BaseModel):
    project_id: int
    project_title: str

    class Config:
        from_attributes = True

class TaskMember(BaseModel):
    user_id: int
    username: str
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    deadline: datetime

    project: TaskProject
    members: List[TaskMember]

class TaskInvite(BaseModel):
    user_id: int
    project_id: int
    task_id: int