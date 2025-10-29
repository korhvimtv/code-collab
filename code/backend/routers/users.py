from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.auth import get_current_user
from crud import user_crud, project_crud
from models.user_models import User, UserResponse, UserUpdate
from models.project_models import ProjectResponse

router = APIRouter(prefix="/users", tags=["Users"])

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

@router.get("/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    return user_crud.get_all_users(db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/projects", response_model=List[ProjectResponse])
async def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    projects = project_crud.get_projects_for_user(db, user_id)
    return [build_project_response(p) for p in projects]

@router.get("/by-username/{username}/projects", response_model=List[ProjectResponse])
async def get_user_projects_by_username(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    projects = project_crud.get_projects_for_user(db, user.id)
    return [build_project_response(p) for p in projects]

@router.put("/{user_id}")
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail="Can only update your own profile")
    updated = user_crud.update_user(db, user_id=user_id, user=user)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete your own profile")
    deleted = user_crud.delete_user(db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

@router.get("/search", response_model=List[UserResponse])
async def search_users(username: str = None, db: Session = Depends(get_db)):
    if not username:
        return []
    return db.query(User).filter(User.username.ilike(f"%{username}%")).all()

@router.get("/me", response_model=UserResponse)
async def me(current: User = Depends(get_current_user)):
    return current