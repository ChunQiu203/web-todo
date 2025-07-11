from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
from datetime import timezone, timedelta

# 定义北京时间时区
beijing_tz = timezone(timedelta(hours=8))

def beijing_now():
    """返回北京时间"""
    return datetime.datetime.now(beijing_tz)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(128))
    schedules = relationship("Schedule", back_populates="owner")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    start_time = Column(DateTime(timezone=True))  # 添加时区支持
    end_time = Column(DateTime(timezone=True))    # 添加时区支持
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="schedules")
    created_at = Column(DateTime, default=beijing_now)
    completed = Column(Boolean, default=False)

class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(20))  # 'user' 或 'assistant'
    content = Column(Text)  # 支持超长内容
    created_at = Column(DateTime, default=beijing_now)
    agent_role = Column(String(32), default='schedule_assistant')  # 新增字段，区分不同agent/角色
    user = relationship("User")