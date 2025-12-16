from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    price: int
    description: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: str
    full_name: str

class UserCreate(UserBase):
    role: str = "student"

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)