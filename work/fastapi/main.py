from fastapi import FastAPI, Depends, HTTPException, Body, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from pytz import timezone
from sqlalchemy import func
import json
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv()

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

from pydantic import BaseModel
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,  
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
import os
# 加载环境变量
from dotenv import load_dotenv
load_dotenv()
# 日志打印
logging.basicConfig(level=logging.INFO)
chat_model__qwen_plus=ChatOpenAI(
    model="qwen-plus",
    api_key=os.environ["ALIYUN_API_KEY"],
    base_url=os.environ["ALIYUN_BASE_URL"],
    temperature=0
)
chat_model_qwen_turbo=ChatOpenAI(
    model="qwen-turbo",
    api_key=os.environ["ALIYUN_API_KEY"],
    base_url=os.environ["ALIYUN_BASE_URL"],
    temperature=0
)
chat_model_zhipu=ChatOpenAI(
    model="glm-4-air",
    api_key=os.environ["ZHIPU_API_KAY"],
    base_url=os.environ["ZHIPU_BASE_URL"],
    temperature=0
)


from langchain_community.chat_models import ChatOllama

chat_model_ollama = ChatOllama(
    model="qwen:1.8b",
    base_url="http://localhost:11434",
    temperature=0
)


@app.get("/ai/history/{user_id}", response_model=List[schemas.AIChatHistory])
def get_ai_history(user_id: int, limit: int = Query(20, le=100), db: Session = Depends(get_db)):
    """获取用户AI历史对话，按时间倒序"""
    return crud.get_ai_chat_history_by_user(db, user_id, limit)

import requests
# 定义 AI 响应接口
class SimpleAgent:
    def __init__(self, name: str, llm: ChatOpenAI,web_url:str = None):
        self.name = name
        self.llm = llm
        self.web_url=web_url
    def fetch_web_content(self):
        if not self.web_url:
            return ""
        try:
            resp = requests.get(self.web_url,timeout=5)
            resp.encoding=resp.apparent_encoding
            # 只取正文，简单处理
            from bs4 import BeautifulSoup
            soup=BeautifulSoup(resp.text,"html.parser")
            text=soup.get_text(separator="\n")
            return text[:2000] #控制长度，防止prompt过长
        except Exception as e:
            return f"[网页抓取失败：{e}]"
    async def run(self, message: str, history: List[dict]) -> str:
        web_content=self.fetch_web_content() if self.web_url else ""
        system_prompt=(
            f"你是一个专业的日程管理助手，有清晰的日程规划和管理能力。并且也可以回答用户的任何问题。"
            f"以下网页中的内容是你的身份角色性格:\n{web_content}\n"
            f"请根据历史记录，专业严谨地回答用户的问题，并且要符合你的身份。"
        )if web_content else(
             "你是一个专业的日程管理助手有清晰的日程规划和管理的能力，对于用户的输入提出专业严谨的建议。请结合用户和你的历史对话内容，理解上下文并连贯地回答用户的问题。"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        chain = prompt | self.llm
        result = await chain.ainvoke({"input": message, "history": history})
        return getattr(result, 'content', None) or str(result)

def classify_question(question: str) -> str:
    # 简单关键词分类，可根据实际需求扩展
    schedule_keywords = ['日程', '安排', '会议', '提醒', '计划', '待办', '任务']
    knowledge_keywords = ['什么', '介绍', '原理', '是谁', '历史', '知识', '定义']
    q = question.lower()
    if any(k in q for k in schedule_keywords):
        return 'schedule'
    if any(k in q for k in knowledge_keywords):
        return 'knowledge'
    return 'other'

AGENT_MAP = {
    'schedule': SimpleAgent("qwen-plus", chat_model__qwen_plus,web_url="https://prts.wiki/w/%E8%A7%81%E8%A1%8C%E8%80%85"),
    'knowledge': SimpleAgent("zhipu", chat_model_zhipu,web_url="https://prts.wiki/w/%E8%A7%81%E8%A1%8C%E8%80%85"),
    'other': SimpleAgent("ollama", chat_model_ollama,web_url="https://prts.wiki/w/%E8%A7%81%E8%A1%8C%E8%80%85")
}

@app.post("/ai/schedule_suggestion/")
async def chat_with_ai(request: schemas.AIChatRequest, db: Session = Depends(get_db)):
    try:
        user_id = request.user_id
        # 读取历史
        history_msgs = []
        if user_id:
            db_history = crud.get_ai_chat_history_by_user(db, user_id, limit=20)
            history_msgs = [
                {"role": h.role, "content": h.content} for h in reversed(db_history)
            ]
        history_msgs = history_msgs + (request.history or [])

        # 自动分类
        qtype = classify_question(request.message)
        agent = AGENT_MAP.get(qtype, AGENT_MAP['other'])
        reply = await agent.run(request.message, history_msgs)

        # 存历史
        if user_id:
            crud.create_ai_chat_history(db, schemas.AIChatHistoryCreate(user_id=user_id, role="user", content=request.message))
            crud.create_ai_chat_history(db, schemas.AIChatHistoryCreate(user_id=user_id, role="assistant", content=reply.strip()))

        return {"reply": reply, "agent": agent.name, "type": qtype}
    except Exception as e:
        logging.error(f"AI 请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 请求失败: {str(e)}")