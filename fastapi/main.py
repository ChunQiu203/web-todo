from fastapi import FastAPI, Depends, HTTPException, Body
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

@app.patch("/schedules/{schedule_id}/completed/", response_model=schemas.Schedule)
def update_schedule_completed(schedule_id: int, completed: bool = Body(...), db: Session = Depends(get_db)):
    schedule = crud.update_schedule_completed(db, schedule_id, completed)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule

# # 智能助手接口（伪代码，需接入大模型API）
# @app.post("/ai/schedule_suggestion/")
# def schedule_suggestion(prompt: str):
#     # 这里调用大模型API，返回结构化日程建议
#     # 例如：return {"title": "...", "start_time": "...", ...}
#     return {"message": "这里返回AI生成的日程建议"}

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






# ai
from pydantic import BaseModel
import requests
import logging
import os

# 配置
OLLAMA_BASE_URL = "http://localhost:11434"
# 这里可以配置你的在线AI API密钥，比如OpenAI
ONLINE_AI_API_KEY = os.getenv("AI_API_KEY", "")

# 日志打印
logging.basicConfig(level=logging.INFO)

# 定义前端请求数据格式
class AIChatRequest(BaseModel):
    message: str  # 用户的提问
    use_online: bool = False  # 是否使用在线AI

# 定义 AI 响应接口
@app.post("/ai/schedule_suggestion/")
def chat_with_ai(request: AIChatRequest):
    try:
        if request.use_online and ONLINE_AI_API_KEY:
            return call_online_ai(request.message)
        else:
            return call_ollama_ai(request.message)
    except Exception as e:
        logging.error(f"AI 请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 请求失败")

def call_online_ai(message: str):
    """调用在线AI API"""
    try:
        headers = {
            "Authorization": f"Bearer {ONLINE_AI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一个专业的日程管理助手。请根据用户的需求，提供具体的日程安排建议。建议应该包含：1. 任务标题 2. 建议的时间安排 3. 优先级 4. 相关提醒。请用中文回答。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        
        return {"response": ai_response, "source": "在线AI"}
        
    except requests.exceptions.RequestException as e:
        logging.error(f"在线AI API 请求失败: {str(e)}")
        # 如果在线AI失败，回退到本地AI
        return call_ollama_ai(message)

def call_ollama_ai(message: str):
    """调用本地Ollama AI"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": "deepseek-r1:7b",
                "prompt": f"{message}",
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return {"response": data.get("response", "AI 没有返回内容"), "source": "本地AI"}
    except requests.exceptions.RequestException as e:
        logging.error(f"Ollama 请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail="AI 请求失败")
