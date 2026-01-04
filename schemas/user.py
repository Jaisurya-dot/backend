from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr
 
class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
