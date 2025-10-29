from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.auth import get_current_user
from crud import project_crud, user_crud, task_crud
from models.project_models import ProjectCreate, ProjectResponse, ProjectInvite, ProjectUpdate
from models.task_models import TaskResponse
from models.user_models import User

router = APIRouter(prefix="/projects", tags=["Projects"])

def build_project_response(project):
    members_data = []
    for link in getattr(project, "members_association", []) or []:
        u = getattr(link, "user", None)
        members_data.append({
            "user_id": link.user_id,
            "username": getattr(u, "username", ""),
            "is_creator": bool(getattr(link, "is_creator", False))
        })
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        members=members_data
    )

@router.post("/", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    creator = user_crud.get_user(db, user_id=current.id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")
    project = project_crud.create_project(db=db, project_data=project_data, creator_id=current.id)
    return build_project_response(project)

@router.post("/invite")
async def invite_to_project(invite: ProjectInvite, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, invite.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only creator can invite")
    project_crud.invite_user_to_project(db, invite)
    return {"message": "User invited"}

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    projects = project_crud.get_all_projects(db)
    return [build_project_response(p) for p in projects]

@router.get("/search", response_model=List[ProjectResponse])
async def search_projects(title: str = None, db: Session = Depends(get_db)):
    if not title:
        return []
    projects = project_crud.search_projects_by_title(db, title)
    return [build_project_response(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return build_project_response(project)

@router.get("/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    is_member = any(link.user_id == current.id for link in project.members_association)
    if not is_member:
        raise HTTPException(status_code=403, detail="Only members can view tasks")
    return task_crud.get_tasks_for_project(db, project_id)

@router.put("/{project_id}")
async def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    existing = project_crud.get_project_by_id(db, project_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")
    is_creator = any(link.user_id == current.id and link.is_creator for link in existing.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only creator can update")
    project_crud.update_project(db, project_id, project=data)
    return {"message": "Project updated"}

@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    existing = project_crud.get_project_by_id(db, project_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")
    is_creator = any(link.user_id == current.id and link.is_creator for link in existing.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only creator can delete")
    project_crud.delete_project_by_id(db, project_id)
    return {"message": "Project deleted"}