# app/game/handler.py
from datetime import datetime
from sqlalchemy.orm import Session
from db import models
from utils.logger import logger

#게임 상태 관리 (대기 / 진행 중 / 종료)
#걸음 수 기록
#칼로리 계산
#DB에 결과 저장

class GameHandler:
    """
    게임 세션(한 판)을 관리하는 클래스
    """

    def __init__(self):
        self.is_playing = False
        self.step_count = 0
        self.measure_active = False  # 족저압 측정 상태

    def start_game(self):
        self.is_playing = True
        self.step_count = 0

    def end_game(self, db: Session, user_id: int = 1):
        if not self.is_playing:
            logger.warning("종료 요청 무시: 게임이 실행 중이 아님")
            return None

        self.is_playing = False
        calories = round(self.step_count * 0.05, 2)

        result = models.GameResult(
            user_id=user_id,
            steps=self.step_count,
            calories=calories,
        )

        try:
            db.add(result)
            db.commit()
            db.refresh(result)
            logger.info(f"게임 종료: 총 {self.step_count}걸음, {calories} kcal 저장 완료")
        except Exception as e:
            db.rollback()
            logger.error(f"DB 저장 실패: {e}")

        return result

    def add_step(self, event_type: str = "STEP"):
        if self.is_playing:
            self.step_count += 1
            logger.info(f"{event_type} 감지 → 총 {self.step_count}걸음")
            return {"steps": self.step_count}
        else:
            logger.warning("걸음 무시: 게임이 실행 중이 아님")
            return {"steps": self.step_count}

# 싱글톤 인스턴스
game_handler = GameHandler()


