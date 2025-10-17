from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import event 
from typing import List

from database import engine, get_db, create_db_tables 
from user_models import UserResponse, UserCreate 
import user_CRUDs

from project_models import ProjectCreate, ProjectResponse, ProjectInvite
import project_crud

@event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.autocommit = True 
    
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_tables()

DBSession = Depends(get_db) 

@app.post('/users', response_model=UserResponse)
async def create_user_endpoint(user_data: UserCreate, db: Session = DBSession):
    user = user_CRUDs.create_user(db=db, user=user_data)
    return user

@app.get('/users', response_model=List[UserResponse])
async def get_users_endpoint(db: Session = DBSession):
    users = user_CRUDs.get_all_users(db)
    return users

@app.get('/users/{user_id}', response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = DBSession):
    user = user_CRUDs.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@app.delete('/users/{user_id}')
async def delete_user_endpoint(user_id: int, db: Session = DBSession):
    deleted = user_CRUDs.delete_user(db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='User not found')
    return {'message': 'User was deleted'}

@app.post('/projects', response_model=ProjectResponse)
async def create_project_endpoint(project_data: ProjectCreate, creator_id: int, db: Session = DBSession):
    creator = user_CRUDs.get_user(db, user_id=creator_id)
    if creator is None:
        raise HTTPException(status_code=404, detail="Creator user not found")
        
    project = project_crud.create_project(db=db, project_data=project_data, creator_id=creator_id)

    members_data = []
    for link in project.members_association:
        members_data.append({
            "user_id": link.user_id,
            "username": link.user.username,
            "is_creator": link.is_creator
        })
        
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        members=members_data
    )


@app.post('/projects/invite', status_code=201)
async def invite_user_endpoint(invite: ProjectInvite, db: Session = DBSession):
    link = project_crud.invite_user_to_project(db, invite)
    if link is None:
        raise HTTPException(status_code=400, detail="Project not found")
    
    return {"message": "User invited to project"}

@app.get('/projects/{project_id}', response_model=ProjectResponse)
async def get_project_endpoint(project_id: int, db: Session = DBSession):
    project = project_crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    members_data = []
    for link in project.members_association:
        members_data.append({
            "user_id": link.user_id,
            "username": link.user.username,
            "is_creator": link.is_creator
        })
    
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        members=members_data
    )

@app.delete('/projects/{project_id}')
async def delete_project_endpoint(project_id: int, db: Session = DBSession):
    deleted = project_crud.delete_project_by_id(db, project_id=project_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail='Project not found')
        
    return {'message': f'Project was deleted'}