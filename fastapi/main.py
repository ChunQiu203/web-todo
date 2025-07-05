from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请指定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_username(db, user.username)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
#     return crud.create_user(db=db, user=user)

@app.post("/users/", response_model=schemas.User)
def create_or_login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        if db_user.password != user.password:
            raise HTTPException(status_code=400, detail="密码错误")
        return db_user
    return crud.create_user(db=db, user=user)    


@app.get("/users/{username}", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/schedules/", response_model=schemas.Schedule)
def create_schedule_for_user(
    user_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)
):
    return crud.create_schedule(db=db, schedule=schedule, user_id=user_id)

@app.get("/users/{user_id}/schedules/", response_model=list[schemas.Schedule])
def read_schedules(user_id: int, db: Session = Depends(get_db)):
    return crud.get_schedules(db, user_id=user_id)

@app.delete("/schedules/{schedule_id}", response_model=schemas.Schedule)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = crud.delete_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

# 智能助手接口（伪代码，需接入大模型API）
@app.post("/ai/schedule_suggestion/")
def schedule_suggestion(prompt: str):
    # 这里调用大模型API，返回结构化日程建议
    # 例如：return {"title": "...", "start_time": "...", ...}
    return {"message": "这里返回AI生成的日程建议"}

@app.get("/users/{user_id}/schedules/today/", response_model=list[schemas.Schedule])
def get_today_schedules(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    return db.query(models.Schedule).filter(
        models.Schedule.owner_id == user_id,
        models.Schedule.start_time >= today,
        models.Schedule.start_time < tomorrow
    ).all()

@app.get("/users/{user_id}/schedules/week/", response_model=list[schemas.Schedule])
def get_week_schedules(user_id: int, db: Session = Depends(get_db)):
    today = datetime.now().date()
    week = today + timedelta(days=7)
    return db.query(models.Schedule).filter(
        models.Schedule.owner_id == user_id,
        models.Schedule.start_time >= today,
        models.Schedule.start_time < week
    ).all()


