# app/game/handler.py
from datetime import date
from sqlalchemy.orm import Session
from db.models import GameResult
from utils.logger import logger

# 칼로리 기본값
BASE_CALORIE = 0.2


class GameHandler:
    """
    게임 상태 및 스텝 카운팅 관리
    """

    def __init__(self):
        self.is_playing = False
        self.measure_active = False
        self.current_steps = 0
        self.current_calories = 0.0
        self.current_sensor_type = None  # 마지막 센서 타입 추적

    def start_game(self):
        """게임 시작"""
        self.is_playing = True
        self.current_steps = 0
        self.current_calories = 0.0
        self.current_sensor_type = None
        logger.info("[GAME] 게임 시작 - 카운터 초기화")

    def add_step(self, sensor_type: str) -> dict:
        """
        STEP 또는 H_STEP 추가
        게임 진행 중일 때만 카운팅
        """
        if not self.is_playing:
            logger.warning(f"[GAME] {sensor_type} 무시 - 게임 진행중 아님")
            return {
                "steps": self.current_steps,
                "calories": self.current_calories
            }

        # 계단 수 증가
        self.current_steps += 1
        
        # 칼로리 계산 (H_STEP은 2배)
        step_calories = BASE_CALORIE * (2 if sensor_type == "H_STEP" else 1)
        self.current_calories += step_calories
        
        # 마지막 센서 타입 저장
        self.current_sensor_type = sensor_type

        logger.info(
            f"[GAME] {sensor_type} 추가 - "
            f"총 걸음: {self.current_steps}, "
            f"총 칼로리: {self.current_calories:.2f}"
        )

        return {
            "steps": self.current_steps,
            "calories": self.current_calories,
            "sensor_type": sensor_type
        }

    def end_game(self, db: Session) -> GameResult:
        """
        게임 종료 및 결과 DB 저장
        """
        if not self.is_playing:
            logger.warning("[GAME] 게임 종료 실패 - 진행중인 게임 없음")
            return None

        try:
            # DB에 결과 저장
            result = GameResult(
                play_date=date.today(),
                steps=self.current_steps,
                calories=self.current_calories,
                sensor_type=self.current_sensor_type or "NONE"
            )

            db.add(result)
            db.commit()
            db.refresh(result)

            logger.info(
                f"[GAME] 게임 종료 및 저장 완료 - "
                f"ID: {result.id}, "
                f"걸음: {result.steps}, "
                f"칼로리: {result.calories:.2f}"
            )

            # 게임 상태 초기화
            self.is_playing = False
            self.current_steps = 0
            self.current_calories = 0.0
            self.current_sensor_type = None

            return result

        except Exception as e:
            logger.error(f"[GAME] DB 저장 실패: {e}")
            db.rollback()
            return None


# 전역 게임 핸들러 인스턴스
game_handler = GameHandler()