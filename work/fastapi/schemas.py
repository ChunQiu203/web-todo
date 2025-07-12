from pydantic import BaseModel, ConfigDict, validator
from typing import Optional, List
import datetime
from datetime import timezone, timedelta

# 定义北京时间时区
beijing_tz = timezone(timedelta(hours=8))

class ScheduleBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime.datetime
    end_time: datetime.datetime
    
    @validator('start_time', 'end_time', pre=True)
    def ensure_timezone(cls, v):
        """确保时间字段有时区信息，如果没有则添加北京时间"""
        if isinstance(v, datetime.datetime):
            print(f"验证时间字段: {v}, 时区信息: {v.tzinfo}")
            if v.tzinfo is None:
                # 如果没有时区信息，假设是北京时间
                result = v.replace(tzinfo=beijing_tz)
                print(f"添加时区信息后: {result}")
                return result
            elif v.tzinfo != beijing_tz:
                # 如果是其他时区，转换为北京时间
                result = v.astimezone(beijing_tz)
                print(f"转换时区后: {result}")
                return result
            else:
                print(f"时间已经是北京时间: {v}")
                return v
        return v

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
