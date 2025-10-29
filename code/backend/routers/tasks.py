from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth import get_current_user
from crud import task_crud, project_crud
from models.task_models import TaskCreate, TaskResponse, TaskProject, TaskUpdate, TaskInvite
from models.user_models import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(task_data: TaskCreate, project_id: int, user_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not any(link.user_id == current.id for link in project.members_association):
        raise HTTPException(status_code=403, detail="Only members can create tasks")
    task = task_crud.create_task(db, task_data, project_id, user_id)
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        completed=getattr(task, "completed", False),
        project=TaskProject(project_id=project.id, project_title=project.title),
        members=[
            {"user_id": link.user_id, "username": link.user.username, "is_creator": link.is_creator}
            for link in project.members_association
        ]
    )

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.get_tasks_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    association = task.project_association[0] if task.project_association else None
    if not association:
        raise HTTPException(status_code=500, detail="Task not linked to any project.")
    project = association.project
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        completed=getattr(task, "completed", False),
        project=TaskProject(project_id=project.id, project_title=project.title),
        members=[{"user_id": link.user_id, "username": link.user.username} for link in task.project_association]
    )

@router.put("/{task_id}")
async def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    task = task_crud.get_tasks_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = task.project_association[0].project if task.project_association else None
    if not project:
        raise HTTPException(status_code=400, detail="Task not linked to a project")
    is_creator = any(l.user_id == current.id and l.is_creator for l in project.members_association)
    is_task_member = any(l.user_id == current.id for l in task.project_association)
    is_project_member = any(l.user_id == current.id for l in project.members_association)
    updating_only_completed = (data.model_dump(exclude_unset=True).keys() == {"completed"})
    if not (is_creator or is_task_member or (updating_only_completed and is_project_member)):
        raise HTTPException(status_code=403, detail="No permission to update task")
    task_crud.update_task(db, task_id, task=data)
    return {"message": "Task updated"}

@router.post("/{task_id}")
async def invite_to_task(task_id: int, invite: TaskInvite, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    task = task_crud.get_tasks_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = task.project_association[0].project if task.project_association else None
    if not project:
        raise HTTPException(status_code=400, detail="Task not linked to a project")
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only creator can invite to task")
    task_crud.invite_user_to_task(db, invite)
    return {"message": "User invited"}

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    task = task_crud.get_tasks_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    project = task.project_association[0].project if task.project_association else None
    if not project:
        raise HTTPException(status_code=400, detail="Task not linked to a project")
    is_creator = any(l.user_id == current.id and l.is_creator for l in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only creator can delete task")
    task_crud.delete_task_by_id(db, task_id)
    return {"message": "Task deleted"}