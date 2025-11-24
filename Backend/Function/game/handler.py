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
        self.current_sensor_type = None  # 현재 게임의 센서 타입 (STEP or H_STEP)

    def start_game(self):
        """게임 시작"""
        self.is_playing = True
        self.current_sensor_type = None
        logger.info("[GAME] 게임 시작 - 센서 타입 초기화")

    def add_step(self, sensor_type: str) -> dict:
        """
        STEP 또는 H_STEP 입력 시 센서 타입만 기록
        게임당 하나의 센서 타입만 사용됨
        """
        if not self.is_playing:
            logger.warning(f"[GAME] {sensor_type} 무시 - 게임 진행중 아님")
            return {"sensor_type": self.current_sensor_type}

        # 센서 타입 기록 (첫 입력 시에만 설정)
        if self.current_sensor_type is None:
            self.current_sensor_type = sensor_type
            logger.info(f"[GAME] 센서 타입 설정: {sensor_type}")
        
        return {"sensor_type": self.current_sensor_type}

    def end_game(self, db: Session, unity_steps: int) -> GameResult:
        """
        게임 종료 및 결과 DB 저장
        Unity에서 전달받은 steps와 기록된 센서 타입으로 칼로리 계산
        """
        if not self.is_playing:
            logger.warning("[GAME] 게임 종료 실패 - 진행중인 게임 없음")
            return None

        try:
            # 센서 타입이 없으면 기본값 STEP
            sensor_type = self.current_sensor_type or "STEP"
            
            # 칼로리 계산
            if sensor_type == "H_STEP":
                # H_STEP: 계단 수 * 2 * 0.2
                calories = unity_steps * 2 * BASE_CALORIE
            else:
                # STEP: 계단 수 * 0.2
                calories = unity_steps * BASE_CALORIE

            # DB에 결과 저장
            result = GameResult(
                play_date=date.today(),
                steps=unity_steps,  # Unity에서 전달받은 steps
                calories=calories,
                sensor_type=sensor_type
            )

            db.add(result)
            db.commit()
            db.refresh(result)

            logger.info(
                f"[GAME] 게임 종료 및 저장 완료 - "
                f"ID: {result.id}, "
                f"Steps: {unity_steps}, "
                f"Sensor Type: {sensor_type}, "
                f"칼로리: {result.calories:.2f}"
            )

            # 게임 상태 초기화
            self.is_playing = False
            self.current_sensor_type = None

            return result

        except Exception as e:
            logger.error(f"[GAME] DB 저장 실패: {e}")
            db.rollback()
            return None


# 전역 게임 핸들러 인스턴스
game_handler = GameHandler()