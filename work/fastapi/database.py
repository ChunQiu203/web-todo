from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://myuser:PASSword2005@localhost:3306/todolist"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"init_command": "SET time_zone='+08:00'"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
