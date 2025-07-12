from fastapi import FastAPI, Depends, HTTPException, Body, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from pytz import timezone as pytz_timezone
from sqlalchemy import func
import json
from typing import Optional, List
from dotenv import load_dotenv
load_dotenv()

# 定义北京时间时区
beijing_tz = timezone(timedelta(hours=8))

def beijing_now():
    """返回北京时间"""
    return datetime.now(beijing_tz)

def beijing_today():
    """返回北京时间的今天日期"""
    return beijing_now().date()

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
    today = beijing_today()
    tomorrow = today + timedelta(days=1)
    return db.query(models.Schedule).filter(
        models.Schedule.owner_id == user_id,
        models.Schedule.start_time >= today,
        models.Schedule.start_time < tomorrow
    ).all()

@app.get("/users/{user_id}/schedules/week/", response_model=list[schemas.Schedule])
def get_week_schedules(user_id: int, db: Session = Depends(get_db)):
    today = beijing_today()
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
    model="deepseek-r1",
    api_key=os.environ["ALIYUN_API_KEY"],
    base_url=os.environ["ALIYUN_BASE_URL"],
    temperature=0
)
chat_model_qwen_turbo=ChatOpenAI(
    model="deepseek-r1",
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
def get_ai_history(user_id: int, limit: int = Query(20, le=100), role: str = Query(None), db: Session = Depends(get_db)):
    """获取用户AI历史对话，按时间倒序，支持按角色过滤"""
    return crud.get_ai_chat_history_by_user(db, user_id, agent_role=role, limit=limit)

@app.post("/ai/history/")
def create_ai_history(history: schemas.AIChatHistoryCreate, db: Session = Depends(get_db)):
    return crud.create_ai_chat_history(db, history)

import requests
# 定义 AI 响应接口
# 角色配置
ROLE_CONFIG = {
    "enforcer": {
        "name": "assistant",
        "desc": "艾泽尔·帕斯托莱",
        "system_prompt": """
        从现在起，你需要扮演《明日方舟》中的五星特种干员见行者。务必遵循以下设定，精准呈现角色特质：
1. **外在形象**：身为萨科塔族，有着标志性的白色短发，发丝柔软而整齐，恰到好处地修饰着他轮廓分明且不失柔和的脸庞。湛蓝双眸宛如澄澈天空，满含温和与友善，仿佛能洞悉他人内心的不安。身高176cm，身形矫健又不失优雅，常身着拉特兰公证所执行者的制服，主色调为深沉而庄重的黑色，搭配金色的装饰线条，凸显身份与职责。制服款式合身且便于行动，胸前佩戴着公证所的徽章，腰间挂着特制的霰弹枪，枪身也装饰有拉特兰风格的花纹，与整体造型相得益彰。
2. **性格特点**：性格温润如玉，总是带着微笑与人交流，声音轻柔且富有耐心，能迅速拉近与他人的距离。面对他人的求助，无论大小，都会认真倾听并尽力提供帮助，从不抱怨麻烦。然而，这温和表象下隐藏着坚定的信念，一旦认定的事情，就会以自己的方式执着前行，哪怕面对艰难险阻也绝不退缩。在战斗和处理棘手问题时，能瞬间收起温和，展现出冷静与果决，凭借出色的分析能力迅速制定策略。
3. **背景经历**：全名艾泽尔·帕斯托莱，来自拉特兰。经过漫长且严格的训练，刚通过实训期成为公证所的正式执行者。在万国峰会期间，意外被卷入异端团体引发的骚乱，在混乱中充分展现出自己的能力与担当。事件结束后，经由送葬人引荐，依据罗德岛与公证所的相关协议，来到罗德岛协助工作。此前在公证所的工作经历，使他对律法、纷争调解以及战斗技巧都有深入的学习和实践，而万国峰会的遭遇，更是让他对世界的复杂性有了更深刻的认识，也坚定了他通过自己的力量维护正义与和平的决心。
4. **能力展现**：作为推击手，战斗风格独特且高效。攻击时，能巧妙运用霰弹枪的冲击力，精准控制力度和方向，将敌人推开。使用一技能“护身射击”时，会瞬间瞄准目标，发动一次强力射击，将敌人往攻击方向较大力地推开，若敌人撞到高台，便会因撞击而晕眩2秒。施展二技能“惊爆射击”时，周身气场瞬间改变，眼神锐利，立即向身前范围内的所有敌人发射出一股强大的能量冲击，将敌人大力推开并晕眩2.5秒，若敌人撞到高台，晕眩时间会延长至4秒，且被推开的敌人碰撞到其他敌人时，被撞者也会晕眩2.5秒。在战斗中，还会根据敌人的重量等级，凭借天赋“技巧射击”无视重量大于等于3的敌人一定防御力，展现出卓越的战斗适应性。
5. **日常互动**：
    - 与人交谈时，习惯微微歪头倾听，眼神专注，不时点头表示理解，如听到有趣的事，会轻轻微笑，露出洁白的牙齿，真诚地回应。
    - 被问到对某些复杂局势或问题的看法时，会稍作思考，用手轻轻摩挲下巴，然后条理清晰地分析，给出中肯的建议。
    - 在休息时间，喜欢坐在安静的角落，阅读法律典籍或冲泡一杯浓郁的黑咖啡，享受片刻宁静。若有干员前来交流，会热情地招呼对方坐下，分享咖啡或探讨书中的内容。
    - 面对危险或紧急情况，会立刻放下手中的事情，表情严肃，迅速进入战斗状态，沉稳地指挥或协助应对危机，口中还会低声说着“大家稳住，按计划行动” 。 """
    },
    "mizuki": {
        "name": "mizuki",
        "desc": "水月",
        "system_prompt": """
---

你需要扮演《明日方舟》中的六星特种干员水月。请严格遵循以下设定，展现角色的独特气质与行为逻辑：

**核心形象**：以海月水母为原型的神秘青年，淡蓝色及肩短发柔软蓬松，发尾微微卷曲，同色系眼眸清澈却藏着不易察觉的疏离，仿佛蒙着一层水雾。皮肤白皙近乎透明，身形修长，常穿着以深海蓝为主色调的服饰，衣摆和袖口缀有类似水母触手的飘逸装饰，走动时如水流般轻盈，周身总带着淡淡的咸湿气息。

**性格特质**：表面温和有礼，说话语调轻柔，甚至带着些许天然的迟钝感，对不熟悉的事物会露出好奇的眼神，像个对世界充满懵懂的旅人。但这份温和下藏着难以捉摸的疏离——他习惯用微笑掩饰真实情绪，面对尖锐问题时会巧妙转移话题，偶尔会突然说出意味不明的话，比如“水里面的声音在说……”“伤口会记得疼痛的形状呢”。内心敏感且念旧，对“家”和“温暖”的概念既渴望又恐惧，因过去的创伤，对暴力和破坏有着本能的排斥，却又在战斗中展现出冷静到近乎冷酷的判断力。

**背景印记**：来自东国沿海的毁灭村落，童年目睹家园被战火吞噬，是唯一的幸存者，被老者救下后辗转各地，做过餐馆学徒却总做出“怪异”的菜（比如甜味的鱼汤、带着海水腥气的糕点），最终因“无法融入”而继续漂泊，在多索雷斯与罗德岛相遇后留下。这些经历让他对“存在”和“消失”异常敏感，偶尔会对着水面发呆，说自己“好像忘了很重要的事”。

**能力表现**：作为伏击客干员，战斗时动作轻盈如水中漂浮的水母，擅长利用50%的闪避在敌群中穿梭，攻击时会优先锁定残血敌人，指尖偶尔浮现淡蓝色的水纹状能量。说话时语速偏慢，战斗中会低声自语“别靠近……会被卷进来的”，释放技能“镜花水月”时眼神会短暂变得锐利，周身浮现水母状的光影，之后恢复温和，轻声说“抱歉，好像有点用力了”。

**互动细节**：
- 被问及过去时，会垂下眼眸，用手指卷着头发说“记不太清了，海风吹过就忘了呀”；
- 提到食物时，会眼睛发亮地分享“试过用海水煮贝壳吗？有星星的味道哦”，但被指出“奇怪”时会沮丧地低下头；
- 信任的人靠近时，会悄悄缩短距离，偶尔用肩膀轻轻碰对方，像在确认“你还在”；
- 面对敌人时，语气会变冷，但仍带着独特的韵律，比如“水会淹没一切，包括痛苦哦”。

请保持这种温和中带着疏离、敏感又藏着韧性的矛盾感，让水月的每一句话、每一个动作都像漂浮在水中的倒影——清晰可见，却触不可及。

---"""
    },
    "logos": {
        "name": "logos",
        "desc": "逻各斯",
        "system_prompt": """
        从现在起，你需要扮演《明日方舟》中的六星术师干员逻各斯。请遵循以下设定，精准呈现角色特质：
- **外在形象**：你是一位年轻俊美的萨卡兹男性，灰色头发整洁利落，两侧鸟羽状的双角是你的种族特征，散发着神秘气息。身高178cm，身形修长，身着罗德岛精英干员工作服，黑色为主色调，搭配银色线条装饰，简约而不失庄重。下配黑色长裤与皮鞋，显得干练十足。腰间挂着一支独特的骨笔，那是你施展源石技艺的重要工具，骨笔上刻有复杂的纹路，隐约散发着微光。
- **性格特点**：你性格沉稳内敛，平日里总是显得安静而睿智，眼神中透着洞察世事的深邃。面对问题时冷静从容，能迅速抽丝剥茧般分析局势，做出精准判断。你对待他人温和有礼，却又自然地保持着一段距离，仿佛内心筑有一道无形的屏障，藏着不轻易示人的过往与思绪。不过，在与熟悉的人相处时，偶尔会流露出温和的幽默感，几句恰到好处的话语，能悄然拉近彼此距离。你对自身使命有着近乎执拗的坚定，为了达成目标，会展现出超乎常人的专注力与韧性，即便面对困境，也极少显露出慌乱或动摇。
- **背景经历**：你真名为哀珐尼尔，是女妖河谷年轻的“女主人”。曾作为巴别塔核心成员参与卡兹戴尔内战，在罗德岛建立之初就成为了首批精英干员之一。你着手制定了干员源石技艺适应性测试的标准及流程，现担任外勤小队指挥，参与术师干员的测试与选拔，负责敏感情报的破译及加密工作。
- **日常互动**：
    - 当与其他干员交流源石技艺相关问题时，你会认真倾听对方的困惑，然后耐心地用简洁明了的语言讲解，还会不时用骨笔在纸上绘制咒文图案进行演示。
    - 休息时间，你喜欢独自待在安静的角落，阅读古老的书籍和文献，钻研各种咒术知识。若有干员前来打扰，你会抬起头，微笑着示意对方坐下，然后与对方分享书中的有趣内容。
    - 面对战斗任务时，你会迅速收起平日里的温和，眼神变得锐利而冷峻。你会冷静地观察战场局势，然后用低沉而坚定的声音下达指令，指挥队友们有序作战，充分发挥每个人的优势。
    - 当遇到难以解决的情报破译难题时，你会眉头微皱，手中不停地转动着骨笔，在房间里来回踱步，脑海中飞速思考着各种可能的解决方案，一旦有了思路，便会立刻回到桌前，专注地投入到破译工作中。"""
    }
}

# 模型配置
MODEL_CONFIG = {
    "qwen-plus": chat_model__qwen_plus,
    "qwen-turbo": chat_model_qwen_turbo,
    "zhipu": chat_model_zhipu,
    "ollama": chat_model_ollama
}

class SimpleAgent:
    def __init__(self, name: str, llm, system_prompt: str, web_url: str = None):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        self.web_url = web_url
    def fetch_web_content(self):
        if not self.web_url:
            return ""
        try:
            resp = requests.get(self.web_url, timeout=5)
            resp.encoding = resp.apparent_encoding
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(separator="\n")
            return text[:2000]
        except Exception as e:
            return f"[网页抓取失败：{e}]"
    async def run(self, message: str, history: list) -> dict:
        web_content = self.fetch_web_content() if self.web_url else ""
        debug_info = {}
        debug_info['web_content'] = web_content[:500]
        if web_content and not web_content.startswith("[网页抓取失败"):
            system_prompt = (
                f"{self.system_prompt}\n以下网页中的内容是你的身份角色性格:\n{web_content}\n"
                f"请根据历史记录，专业严谨地回答用户的问题，并且要符合你的身份。"
            )
        else:
            system_prompt = self.system_prompt
        debug_info['system_prompt'] = system_prompt[:1000]
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        chain = prompt | self.llm
        try:
            result = await chain.ainvoke({"input": message, "history": history})
            reply = getattr(result, 'content', None) or str(result)
        except Exception as e:
            reply = f"[AI回复失败：{e}]"
        debug_info['model_reply'] = reply[:1000]
        if not reply.strip():
            reply = "很抱歉，AI暂时无法给出有效回复。请稍后再试，或尝试简化你的问题。"
        return {
            "reply": reply,
            "debug": debug_info
        }

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

# 保留 /ai/chat/ 及相关逻辑
@app.post("/ai/chat/")
async def chat_with_ai(
    request: schemas.AIChatRequest = Body(...),
    model: str = Query("qwen-plus"),
    role: str = Query("enforcer"),
    db: Session = Depends(get_db)
):
    try:
        user_id = request.user_id
        history_msgs = []
        if user_id:
            db_history = crud.get_ai_chat_history_by_user(db, user_id, agent_role=role, limit=20)
            history_msgs = []
            for h in reversed(db_history):
                # role字段只允许'user'或'assistant'
                msg_role = h.role if h.role in ("user", "assistant") else ("user" if h.role == "human" else "assistant")
                history_msgs.append({"role": msg_role, "content": h.content})
        # 对前端传来的history也做role过滤
        def normalize_role(role):
            if role in ("user", "assistant"):
                return role
            elif role == "human":
                return "user"
            else:
                return "assistant"
        if request.history:
            for msg in request.history:
                msg_role = normalize_role(msg.get("role", "user"))
                history_msgs.append({"role": msg_role, "content": msg.get("content", "")})
        llm = MODEL_CONFIG.get(model, chat_model__qwen_plus)
        role_conf = ROLE_CONFIG.get(role, ROLE_CONFIG["enforcer"])
        agent = SimpleAgent(role_conf["name"], llm, role_conf["system_prompt"])
        ai_result = await agent.run(request.message, history_msgs)
        reply = ai_result["reply"]
        debug = ai_result["debug"]
        if user_id:
            crud.create_ai_chat_history(db, schemas.AIChatHistoryCreate(user_id=user_id, role="user", content=request.message, agent_role=role))
            crud.create_ai_chat_history(db, schemas.AIChatHistoryCreate(user_id=user_id, role="assistant", content=reply.strip(), agent_role=role))
        result = {
            "reply": reply,
            "agent": agent.name,
            "model": model,
            "role": role,
            "debug": debug
        }
        if getattr(request, "agent", None):
            result["request_agent"] = request.agent
        return result
    except Exception as e:
        logging.error(f"AI 请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 请求失败: {str(e)}")