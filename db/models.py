# app/db/models.py
from sqlalchemy import Column, Date, Integer, Float, String
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

    # 라즈베리파이/유니티 통신에서 받은 센서 정보 (선택적)
    sensor_value = Column(Float, nullable=True)                   # 마지막 센서값
    sensor_status = Column(String, nullable=True)                 # 센서 상태 (예: 'active', 'idle')


    def __repr__(self):
        return f"<GameResult(id={self.id}, steps={self.steps}, calories={self.calories}, duration={self.duration})>"
