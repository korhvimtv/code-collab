from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str

    class Config:
        from_attributes = True