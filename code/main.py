from fastapi import FastAPI, HTTPException
from managers import user_manager
from models import UserCreate, UserResponse

app = FastAPI()

@app.post('/users', response_model=UserResponse)
async def create_user(user_data: UserCreate):
    user = user_manager.add_user(user_data.name, user_data.username, user_data.email)
    return user.to_dict()

@app.get('/users')
async def get_users():
    users = user_manager.get_all_users()
    return [user.to_dict() for user in users]

@app.get('/user/{user_id}', response_model=UserResponse)
async def get_user(user_id: int):
    user = user_manager.get_user_by_id(user_id)
    return user.to_dict()

@app.delete('/user/{user_id}')
async def delete_user(user_id: int):
    user = user_manager.delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return {'message': 'User was deleted'}
