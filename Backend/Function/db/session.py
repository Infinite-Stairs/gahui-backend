# app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Render 환경 변수에서 DATABASE_URL 가져오기
DATABASE_URL = os.environ.get("postgresql://gahui:UTMyUVGeVjcQ3tTbw3Pd3flix2ce8Hft@dpg-d4i0n32li9vc73eg01eg-a/game_results_tpj5")  # Render에 설정한 DB URL

if not DATABASE_URL:
    raise ValueError("DATABASE_URL 환경 변수가 설정되지 않았습니다!")

# PostgreSQL 연결
engine = create_engine(DATABASE_URL)

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
