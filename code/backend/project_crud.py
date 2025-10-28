from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Optional, Dict, Any

from user_models import User
from project_models import Project, UserProjectAssociation, ProjectCreate, ProjectInvite, ProjectUpdate

def create_project(db: Session, project_data: ProjectCreate, creator_id: int) -> Project:
    db_project = Project(
        title=project_data.title,
        description=project_data.description
    )
    db.add(db_project)
    db.flush()
    
    creator_link = UserProjectAssociation(
        user_id=creator_id,
        project_id=db_project.id,
        is_creator=True
    )
    db.add(creator_link)
    
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: int, project: ProjectUpdate) -> Optional[Project]:
    db_project = db.query(Project).filter(Project.id == project_id).first()

    if not db_project:
        return None

    update_data: Dict[str, Any] = project.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def invite_user_to_project(db: Session, invite: ProjectInvite) -> Optional[UserProjectAssociation]:
    link = db.scalar(
        select(UserProjectAssociation)
        .where(UserProjectAssociation.user_id == invite.user_id)
        .where(UserProjectAssociation.project_id == invite.project_id)
    )
    
    if link:
        return None
        
    if not db.get(User, invite.user_id) or not db.get(Project, invite.project_id):
        return None 

    new_link = UserProjectAssociation(
        user_id=invite.user_id,
        project_id=invite.project_id,
        is_creator=invite.is_creator
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

def get_project_by_id(db: Session, project_id: int) -> Optional[Project]:
    link = select(Project).where(Project.id == project_id)
    return db.scalar(link)

def delete_project_by_id(db: Session, project_id: int) -> bool:
    db_project = db.get(Project, project_id)
    
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

def get_projects_for_user(db: Session, user_id: int):
    stmt = (
        select(Project)
        .join(UserProjectAssociation, UserProjectAssociation.project_id == Project.id)
        .where(UserProjectAssociation.user_id == user_id)
    )
    return db.execute(stmt).scalars().all()

def get_all_projects(db: Session):
    return db.execute(select(Project)).scalars().all()

def search_projects_by_title(db: Session, title: str):
    stmt = select(Project).where(Project.title.ilike(f"%{title}%"))
    return db.execute(stmt).scalars().all()