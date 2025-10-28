from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import event
from typing import List

import task_crud
from database import engine, get_db, create_db_tables, reset_users_table, reset_all_tables
from task_models import TaskCreate, TaskResponse, TaskProject, TaskUpdate, TaskInvite
from user_models import UserResponse, UserCreate, UserUpdate
import user_crud

from project_models import ProjectCreate, ProjectResponse, ProjectInvite, ProjectUpdate
import project_crud

from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from auth import get_current_user, create_token, verify_password
from user_models import User

@event.listens_for(engine, 'connect')
def do_connect(dbapi_connection, connection_record):
    dbapi_connection.autocommit = True
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    return response

@app.on_event("startup")
def on_startup():
    create_db_tables()
@app.post('/admin/reset-users')
def admin_reset_users(db: Session = Depends(get_db)):
    reset_users_table()
    return { 'message': 'users table dropped and recreated' }

@app.get('/admin/reset-users')
def admin_reset_users_get(db: Session = Depends(get_db)):
    reset_users_table()
    return { 'message': 'users table dropped and recreated' }

@app.post('/admin/reset-all')
def admin_reset_all(db: Session = Depends(get_db)):
    reset_all_tables()
    return { 'message': 'all tables dropped and recreated' }

@app.get('/admin/reset-all')
def admin_reset_all_get(db: Session = Depends(get_db)):
    reset_all_tables()
    return { 'message': 'all tables dropped and recreated' }

@app.get('/')
def root():
    return { 'status': 'ok', 'docs': '/docs' }

def build_project_response(project) -> ProjectResponse:
    members_data = []
    for link in getattr(project, 'members_association', []) or []:
        u = getattr(link, 'user', None)
        members_data.append({
            'user_id': link.user_id,
            'username': getattr(u, 'username', ''),
            'is_creator': bool(getattr(link, 'is_creator', False))
        })
    return ProjectResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        members=members_data
    )

DBSession = Depends(get_db) 

@app.post('/auth/register', response_model=UserResponse)
async def register_endpoint(user_data: UserCreate, db: Session = DBSession):
    existing = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail='User with this username or email already exists')
    user = user_crud.create_user(db=db, user=user_data)
    return user

@app.post('/auth/login')
async def login_endpoint(credentials: dict = Body(...), db: Session = DBSession):
    username = credentials.get('username')
    password = credentials.get('password')
    if not username or not password:
        raise HTTPException(status_code=400, detail='Username and password required')
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash or ''):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_token(user.id)
    return { 'access_token': token, 'token_type': 'bearer' }

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

@app.get('/users/by-username/{username}', response_model=UserResponse)
async def get_user_by_username_endpoint(username: str, db: Session = DBSession):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return user

@app.get('/users/{user_id}/projects', response_model=List[ProjectResponse])
async def get_user_projects_endpoint(user_id: int, db: Session = DBSession):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    projects = project_crud.get_projects_for_user(db, user_id)
    return [build_project_response(p) for p in projects]

@app.get('/users/by-username/{username}/projects', response_model=List[ProjectResponse])
async def get_user_projects_by_username_endpoint(username: str, db: Session = DBSession):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    projects = project_crud.get_projects_for_user(db, user.id)
    return [build_project_response(p) for p in projects]

@app.put('/users/{user_id}', response_model=UserResponse)
async def update_user_endpoint(user_id: int, user: UserUpdate, db: Session = DBSession, current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail='Can only update your own profile')
    user = user_crud.update_user(db, user_id=user_id, user=user)

    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    return {'message': 'User updated'}

@app.delete('/users/{user_id}')
async def delete_user_endpoint(user_id: int, db: Session = DBSession, current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail='Can only delete your own profile')
    deleted = user_crud.delete_user(db, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='User not found')
    return {'message': 'User was deleted'}

@app.get('/me', response_model=UserResponse)
async def me_endpoint(current: User = Depends(get_current_user)):
    return current

@app.post('/projects', response_model=ProjectResponse)
async def create_project_endpoint(project_data: ProjectCreate, db: Session = DBSession, current: User = Depends(get_current_user)):
    creator = user_crud.get_user(db, user_id=current.id)

    if creator is None:
        raise HTTPException(status_code=404, detail='Creator user not found')
        
    project = project_crud.create_project(db=db, project_data=project_data, creator_id=current.id)

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
async def invite_user_endpoint(invite: ProjectInvite, db: Session = DBSession, current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, invite.project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail='Only project creator can invite')
    link = project_crud.invite_user_to_project(db, invite)

    if link is None:
        raise HTTPException(status_code=400, detail='Project not found')
    
    return {'message': 'User invited to project'}

@app.get('/projects/{project_id}', response_model=ProjectResponse)
async def get_project_endpoint(project_id: int, db: Session = DBSession):
    project = project_crud.get_project_by_id(db, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    return build_project_response(project)

@app.get('/projects/{project_id}/tasks', response_model=List[TaskResponse])
async def get_project_tasks_endpoint(project_id: int, db: Session = DBSession, current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    is_member = any(link.user_id == current.id for link in project.members_association)
    if not is_member:
        raise HTTPException(status_code=403, detail='Only project members can view tasks')
    
    tasks = task_crud.get_tasks_for_project(db, project_id)
    return tasks

@app.put('/projects/{project_id}')
async def update_project_endpoint(project_id: int, project: ProjectUpdate, db: Session = DBSession, current: User = Depends(get_current_user)):
    existing = project_crud.get_project_by_id(db, project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail='Project not found')
    is_creator = any(link.user_id == current.id and link.is_creator for link in existing.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail='Only project creator can update')
    project = project_crud.update_project(db, project_id, project=project)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    return {'message': 'Project was updated'}

@app.delete('/projects/{project_id}')
async def delete_project_endpoint(project_id: int, db: Session = DBSession, current: User = Depends(get_current_user)):
    existing = project_crud.get_project_by_id(db, project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail='Project not found')
    is_creator = any(link.user_id == current.id and link.is_creator for link in existing.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail='Only project creator can delete')
    deleted = project_crud.delete_project_by_id(db, project_id=project_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail='Project not found')
        
    return {'message': f'Project was deleted'}

@app.get('/me/projects', response_model=List[ProjectResponse])
async def my_projects_endpoint(db: Session = DBSession, current: User = Depends(get_current_user)):
    projects = project_crud.get_projects_for_user(db, current.id)
    return [build_project_response(p) for p in projects]

@app.get('/projects', response_model=List[ProjectResponse])
async def list_projects_endpoint(db: Session = DBSession):
    projects = project_crud.get_all_projects(db)
    return [build_project_response(p) for p in projects]

@app.get('/projects/search', response_model=List[ProjectResponse])
async def search_projects_endpoint(title: str = None, db: Session = DBSession):
    if not title:
        return []
    projects = project_crud.search_projects_by_title(db, title)
    return [build_project_response(p) for p in projects]

@app.get('/users/search', response_model=List[UserResponse])
async def search_users_endpoint(username: str = None, db: Session = DBSession):
    if not username:
        return []
    users = db.query(User).filter(User.username.ilike(f"%{username}%")).all()
    return users

@app.post('/tasks', response_model=TaskResponse)
async def create_task_endpoint(task_data: TaskCreate, project_id: int, user_id: int, db: Session = DBSession, current: User = Depends(get_current_user)):
    project = project_crud.get_project_by_id(db, project_id=project_id)

    if project is None:
        raise HTTPException(status_code=404, detail='Project not found')

    # allow only project members to create tasks
    is_member = any(link.user_id == current.id for link in project.members_association)
    if not is_member:
        raise HTTPException(status_code=403, detail='Only project members can create tasks')
    task = task_crud.create_task(db=db, task_data=task_data, project_id=project_id, user_id=user_id)

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
        completed=getattr(task, 'completed', False),

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
        completed=getattr(task, 'completed', False),

        project=TaskProject(
            project_id=project.id,
            project_title=project.title,
        ),

        members=members_data
    )

@app.put('/task/{task_id}')
async def update_task_endpoint(task_id: int, task: TaskUpdate, db: Session = DBSession, current: User = Depends(get_current_user)):
    existing = task_crud.get_tasks_by_id(db, task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail='Task not found')
    # only members assigned to task, project creator, or any project member (for completed) can update
    project = existing.project_association[0].project if existing.project_association else None
    if project is None:
        raise HTTPException(status_code=400, detail='Task not linked to a project')
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    is_task_member = any(link.user_id == current.id for link in existing.project_association)
    is_project_member = any(link.user_id == current.id for link in project.members_association)
    updating_only_completed = (task.model_dump(exclude_unset=True).keys() == {'completed'})
    if not (is_creator or is_task_member or (updating_only_completed and is_project_member)):
        raise HTTPException(status_code=403, detail='No permission to update task')
    task = task_crud.update_task(db, task_id=task_id, task=task)

    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': 'Task was updated'}

@app.post('/task/{task_id}')
async def invite_user_endpoint(task_id: int, invite: TaskInvite, db: Session = DBSession, current: User = Depends(get_current_user)):
    task = task_crud.get_tasks_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')
    project = task.project_association[0].project if task.project_association else None
    if project is None:
        raise HTTPException(status_code=400, detail='Task not linked to a project')
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail='Only project creator can invite to task')
    link = task_crud.invite_user_to_task(db, invite=invite)

    if link is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': 'User was selected'}

@app.delete('/task/{task_id}')
async def delete_task_endpoint(task_id: int, db: Session = DBSession, current: User = Depends(get_current_user)):
    existing = task_crud.get_tasks_by_id(db, task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail='Task not found')
    project = existing.project_association[0].project if existing.project_association else None
    if project is None:
        raise HTTPException(status_code=400, detail='Task not linked to a project')
    is_creator = any(link.user_id == current.id and link.is_creator for link in project.members_association)
    if not is_creator:
        raise HTTPException(status_code=403, detail='Only project creator can delete task')
    deleted = task_crud.delete_task_by_id(db, task_id=task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail='Task not found')

    return {'message': f'Task was deleted'}