from sqlalchemy.orm import Session
import models, schemas
from typing import List
from datetime import timezone, timedelta

# 定义北京时间时区
beijing_tz = timezone(timedelta(hours=8))

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_schedule(db: Session, schedule: schemas.ScheduleCreate, user_id: int):
    print("create schedule:",schedule.start_time)
    # 确保时间字段有时区信息
    schedule_data = schedule.dict()
    
    # 处理开始时间
    if schedule_data.get('start_time'):
        start_time = schedule_data['start_time']
        if start_time.tzinfo is None:
            # 如果没有时区信息，假设是北京时间
            start_time = start_time.replace(tzinfo=beijing_tz)
        elif start_time.tzinfo != beijing_tz:
            # 如果是其他时区，转换为北京时间
            start_time = start_time.astimezone(beijing_tz)
        # 转换为naive datetime（去除时区信息，但保持北京时间）
        schedule_data['start_time'] = start_time.replace(tzinfo=None)
    
    # 处理结束时间
    if schedule_data.get('end_time'):
        end_time = schedule_data['end_time']
        if end_time.tzinfo is None:
            # 如果没有时区信息，假设是北京时间
            end_time = end_time.replace(tzinfo=beijing_tz)
        elif end_time.tzinfo != beijing_tz:
            # 如果是其他时区，转换为北京时间
            end_time = end_time.astimezone(beijing_tz)
        # 转换为naive datetime（去除时区信息，但保持北京时间）
        schedule_data['end_time'] = end_time.replace(tzinfo=None)
    
    print(f"处理后的时间 - start_time: {schedule_data['start_time']}, end_time: {schedule_data['end_time']}")
    
    db_schedule = models.Schedule(**schedule_data, owner_id=user_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_schedules(db: Session, user_id: int):
    return db.query(models.Schedule).filter(models.Schedule.owner_id == user_id).all()

def get_schedule(db: Session, schedule_id: int):
    return db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()

def delete_schedule(db: Session, schedule_id: int):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
    return db_schedule

def update_schedule_completed(db: Session, schedule_id: int, completed: bool):
    db_schedule = get_schedule(db, schedule_id)
    if db_schedule:
        db_schedule.completed = completed
        db.commit()
        db.refresh(db_schedule)
    return db_schedule

def create_ai_chat_history(db: Session, chat: schemas.AIChatHistoryCreate):
    db_chat = models.AIChatHistory(**chat.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_ai_chat_history_by_user(db: Session, user_id: int, agent_role: str = None, limit: int = 20):
    query = db.query(models.AIChatHistory).filter(models.AIChatHistory.user_id == user_id)
    if agent_role:
        query = query.filter(models.AIChatHistory.agent_role == agent_role)
    return query.order_by(models.AIChatHistory.created_at.asc()).limit(limit).all()
