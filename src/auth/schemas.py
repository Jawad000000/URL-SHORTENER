from datetime import datetime
from sqlmodel import Field
from pydantic import BaseModel

class UserAccount(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8, max_length=72)
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_verified: bool
    created_at: datetime

class User_Login(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)