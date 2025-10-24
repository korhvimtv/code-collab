from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import event
from typing import List

import task_crud
from database import engine, get_db, create_db_tables
from task_models import TaskCreate, TaskResponse, TaskProject, TaskUpdate, TaskInvite
from user_models import UserResponse, UserCreate, UserUpdate
import user_crud

from project_models import ProjectCreate, ProjectResponse, ProjectInvite, ProjectUpdate
import project_crud

@event.listens_for(engine, 'connect')
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.autocommit = True
app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_tables()

DBSession = Depends(get_db) 

@app.post('/users', response_model=UserResponse)
async def create_user_endpoint(user_data: UserCreate, db: Session = DBSession):
    user = user_crud.create_user(db=db, user=user_data)
    return user

@app.get('/users', response_model=List[UserResponse])
async def get_users_endpoint(db: Session = DBSession):
    users = user_crud.get_all_users(db)
    return users

@app.get('/users/{user_id}', response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = DBSession):
    user = user_crud.get_user(db, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    return user

@app.put('/users/{user_id}', response_model=UserResponse)
async def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = DBSession):
    user = user_crud.update_user(db, user_id=user_id, user=user)

    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    return {'message': 'User updated'}

@app.delete('/users/{user_id}')
async def delete_user_endpoint(user_id: int, db: Session = DBSession):
    deleted = user_crud.delete_user(db, user_id=user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='User not found')

    return {'message': 'User was deleted'}

@app.post('/projects', response_model=ProjectResponse)
async def create_project_endpoint(project_data: ProjectCreate, creator_id: int, db: Session = DBSession):
    creator = user_crud.get_user(db, user_id=creator_id)

    if creator is None:
        raise HTTPException(status_code=404, detail='Creator user not found')
        
    project = project_crud.create_project(db=db, project_data=project_data, creator_id=creator_id)

    members_data = []
    for link in project.members_association:
        members_data.append({
            'user_id': link.user_id,
            'username': link.user.username,
            'is_creator': link.is_creator
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
        raise HTTPException(status_code=400, detail='Project not found')
    
    return {'message': 'User invited to project'}

@app.get('/projects/{project_id}', response_model=ProjectResponse)
async def get_project_endpoint(project_id: int, db: Session = DBSession):
    project = project_crud.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')
        
    members_data = []
    for link in project.members_association:
        members_data.append({
            'user_id': link.user_id,
            'username': link.user.username,
            'is_creator': link.is_creator
        })
    
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        members=members_data
    )

@app.put('projets/{project_id}')
async def update_project_endpoint(project_id: int, project: ProjectUpdate, db: Session = DBSession):
    project = project_crud.update_project(db, project_id, project=project)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    return {'message': 'Project was updated'}

@app.delete('/projects/{project_id}')
async def delete_project_endpoint(project_id: int, db: Session = DBSession):
    deleted = project_crud.delete_project_by_id(db, project_id=project_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail='Project not found')
        
    return {'message': f'Project was deleted'}

@app.post('/tasks', response_model=TaskResponse)
async def create_task_endpoint(task_data: TaskCreate, creator_id: int, user_id: int, db: Session = DBSession):
    project = project_crud.get_project_by_id(db, project_id=creator_id)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    task = task_crud.create_task(db=db, task_data=task_data, project_id=creator_id, user_id=user_id)

    members_data = []
    for link in project.members_association:
        members_data.append({
            'user_id': link.user_id,
            'username': link.user.username,
            'is_creator': link.is_creator
        })

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        deadline=task.deadline,

        project=TaskProject(
            project_id=project.id,
            project_title=project.title,
        ),

        members=members_data
    )

@app.get('/task/{task_id}', response_model=TaskResponse)
async def get_task_endpoint(task_id: int, db: Session = DBSession):
    task = task_crud.get_tasks_by_id(db, task_id=task_id)

    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    association = task.project_association[0] if task.project_association else None

    if association is None:
        raise HTTPException(status_code=500, detail='Task is not linked to any project or member.')

    project = association.project

    members_data = []
    for link in task.project_association:
        members_data.append({
            'user_id': link.user_id,
            'username': link.user.username,
        })

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        deadline=task.deadline,

        project=TaskProject(
            project_id=project.id,
            project_title=project.title,
        ),

        members=members_data
    )

@app.put('/task/{task_id}')
async def update_task_endpoint(task_id: int, task: TaskUpdate, db: Session = DBSession):
    task = task_crud.update_task(db, task_id=task_id, task=task)

    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': 'Task was updated'}

@app.post('/task/{task_id}')
async def invite_user_endpoint(task_id: int, invite: TaskInvite, db: Session = DBSession):
    link = task_crud.invite_user_to_task(db, invite=invite)

    if link is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': 'User was selected'}

@app.delete('/task/{task_id}')
async def delete_task_endpoint(task_id: int, db: Session = DBSession):
    deleted = task_crud.delete_task_by_id(db, task_id=task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': f'Task was deleted'}