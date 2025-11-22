# app/db/models.py
from sqlalchemy import Column, Date, DateTime, Integer, Float, String
from sqlalchemy.sql import func
from .session import Base

class GameResult(Base):
    __tablename__ = "game_results"

    # 고유 id
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 플레이 날짜
    play_date = Column(Date, nullable=False) #YYYY-MM-DD 저장

    # 게임 관련 데이터
    steps = Column(Integer, nullable=False, default=0)           # 계단 수
    calories = Column(Float, nullable=False, default=0.0)         # 소모 칼로리

    sensor_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    def __repr__(self):
        return f"<GameResult(id={self.id}, steps={self.steps}, calories={self.calories}, duration={self.duration})>"
