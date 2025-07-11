from sqlalchemy.orm import Session
import models, schemas
from typing import List

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
    db_schedule = models.Schedule(**schedule.dict(), owner_id=user_id)
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

def get_ai_chat_history_by_user(db: Session, user_id: int, limit: int = 20):
    return db.query(models.AIChatHistory).filter(models.AIChatHistory.user_id == user_id).order_by(models.AIChatHistory.created_at.desc()).limit(limit).all()
