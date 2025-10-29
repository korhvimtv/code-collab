from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, Dict, Any, List

from models.project_models import Project
from models.user_models import User
from models.task_models import Task, TaskInvite, TaskCreate, TaskResponse, TaskProjectAssociation, TaskUpdate, TaskProject

def create_task(db: Session, task_data: TaskCreate, project_id: int, user_id: int) -> Task:
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        deadline=task_data.deadline
    )
    db.add(db_task)
    db.flush()

    project_link = TaskProjectAssociation(
        user_id=user_id,
        project_id=project_id,
        task_id=db_task.id
    )
    db.add(project_link)

    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_id(db: Session, task_id: int) -> Optional[Task]:
    link = select(Task).where(Task.id == task_id)
    return db.scalar(link)

def update_task(db: Session, task_id: int, task: TaskUpdate) -> Optional[Task]:
    db_task = db.query(Task).filter(Task.id == task_id).first()

    if not db_task:
        return None

    update_data: Dict[str, Any] = task.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def invite_user_to_task(db: Session, invite: TaskInvite) -> Optional[TaskProjectAssociation]:
    link = db.scalar(
        select(TaskProjectAssociation)
        .where(TaskProjectAssociation.user_id == invite.user_id)
        .where(TaskProjectAssociation.project_id == invite.project_id)
        .where(TaskProjectAssociation.task_id == invite.task_id)
    )

    if link:
        return None

    if not db.get(User, invite.user_id) or not db.get(Project, invite.project_id) or not db.get(Task, invite.task_id) :
        return None

    new_task = TaskProjectAssociation(
        user_id=invite.user_id,
        project_id=invite.project_id,
        task_id=invite.task_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def get_tasks_for_project(db: Session, project_id: int) -> List[TaskResponse]:
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    stmt = (
        select(Task)
        .join(TaskProjectAssociation, TaskProjectAssociation.task_id == Task.id)
        .where(TaskProjectAssociation.project_id == project_id)
        .options(
            joinedload(Task.project_association).joinedload(TaskProjectAssociation.user),
            joinedload(Task.project_association).joinedload(TaskProjectAssociation.project)
        )
    )
    
    tasks = db.execute(stmt).unique().scalars().all()
    
    result = []
    for task in tasks:
        if not task.project_association:
            continue
            
        association = task.project_association[0]
        project = association.project
        
        members_data = []
        for link in task.project_association:
            members_data.append({
                'user_id': link.user_id,
                'username': link.user.username,
            })
        
        result.append(TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            completed=bool(getattr(task, 'completed', False)),
            project=TaskProject(
                project_id=project.id,
                project_title=project.title,
            ),
            members=members_data
        ))
    
    return result

def delete_task_by_id(db: Session, task_id: int) -> bool:
    db_task = db.get(Task, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False