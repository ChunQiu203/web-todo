from pydantic import BaseModel
from typing import Optional, List
import datetime

class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    completed: Optional[bool] = False

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    owner_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    schedules: List[Schedule] = []

    class Config:
        orm_mode = True
