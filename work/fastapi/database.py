from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://myuser:PASSword2005@localhost:3306/todolist"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://dbuser:summeruser@127.0.0.1:3306/summerdb"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "init_command": "SET time_zone='+08:00'",
        "charset": "utf8mb4"
    },
    # 添加时区处理
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
