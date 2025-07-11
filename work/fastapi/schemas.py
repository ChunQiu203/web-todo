from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime


class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    owner_id: int
    created_at: datetime.datetime


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    schedules: List[Schedule] = []

    class Config:
        orm_mode = True

class AIChatHistoryBase(BaseModel):
    user_id: int
    role: str
    content: str
    created_at: Optional[datetime.datetime] = None
    agent_role: Optional[str] = 'schedule_assistant'  # 新增字段

class AIChatHistoryCreate(AIChatHistoryBase):
    pass

class AIChatHistory(AIChatHistoryBase):
    id: int
    class Config:
        orm_mode = True

class AIChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    use_online: str = "false"
    history: Optional[list[dict]] = None
    agent: Optional[str] = None
