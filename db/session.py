# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL 연결 설정
# DB 정보: user, password, host, port, dbname
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:2302@localhost:5432/game_results"

# PostgreSQL은 connect_args 필요 없음
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

# FastAPI용 DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
