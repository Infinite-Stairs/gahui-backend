# handler.py
import asyncio
from datetime import date
from sqlalchemy.orm import Session
from db.models import GameResult
from utils.logger import logger
from websocket.manager import send_to_pi  

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
        # Pi WebSocket으로 상태 전송
        asyncio.create_task(self.send_pi_state())

    def add_step(self, sensor_type: str) -> dict:
        if not self.is_playing:
            logger.warning(f"[GAME] {sensor_type} 무시 - 게임 진행중 아님")
            return {"sensor_type": self.current_sensor_type}

        if self.current_sensor_type is None:
            self.current_sensor_type = sensor_type
            logger.info(f"[GAME] 센서 타입 설정: {sensor_type}")
        
        return {"sensor_type": self.current_sensor_type}

    def end_game(self, db: Session, unity_steps: int) -> GameResult:
        if not self.is_playing:
            logger.warning("[GAME] 게임 종료 실패 - 진행중인 게임 없음")
            return None

        try:
            sensor_type = self.current_sensor_type or "STEP"
            
            if sensor_type == "H_STEP":
                calories = unity_steps * 2 * BASE_CALORIE
            else:
                calories = unity_steps * BASE_CALORIE

            result = GameResult(
                play_date=date.today(),
                steps=unity_steps,
                calories=calories,
                sensor_type=sensor_type
            )

            db.add(result)
            db.commit()
            db.refresh(result)

            logger.info(
                f"[GAME] 게임 종료 및 저장 완료 - "
                f"ID: {result.id}, Steps: {unity_steps}, "
                f"Sensor Type: {sensor_type}, 칼로리: {result.calories:.2f}"
            )

            # 게임 상태 초기화
            self.is_playing = False
            self.current_sensor_type = None
            # Pi WebSocket으로 상태 전송
            asyncio.create_task(self.send_pi_state())

            return result

        except Exception as e:
            logger.error(f"[GAME] DB 저장 실패: {e}")
            db.rollback()
            return None

    # ================================
    # Pi WebSocket 전송 기능 추가
    # ================================
    async def send_pi_state(self):
        """Pi WebSocket으로 is_playing 상태 전송"""
        msg = {"game_active": 1 if self.is_playing else 0}
        await send_to_pi(msg)


# 전역 게임 핸들러 인스턴스
game_handler = GameHandler()
