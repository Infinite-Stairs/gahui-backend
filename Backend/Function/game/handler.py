import asyncio
import requests  # [추가] 옆집(Func2) 서버와 통신하기 위해 필요
from datetime import date
from sqlalchemy.orm import Session
from db.models import GameResult
from utils.logger import logger
# from websocket.manager import send_to_pi # [삭제] 웹소켓 방식 대신 HTTP 사용

BASE_CALORIE = 0.2

# [핵심] Func2 (센서/하드웨어 서버)의 주소 (포트 8000)
FUNC2_CONTROL_URL = "http://127.0.0.1:8000/api/control"

class GameHandler:
    """
    게임 상태 및 스텝 카운팅 관리
    """

    def __init__(self): 
        self.is_playing = False
        self.measure_active = False
        self.current_sensor_type = None

    def start_game(self):
        """게임 시작"""
        self.is_playing = True
        self.current_sensor_type = None
        logger.info("[GAME] 게임 시작 - 센서 타입 초기화")
        
        # [수정] Func2(하드웨어 서버)에게 "아두이노 켜!" 신호 전송
        self.send_hardware_signal(True)

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
            
            # [수정] Func2(하드웨어 서버)에게 "아두이노 꺼!" 신호 전송
            self.send_hardware_signal(False)

            return result

        except Exception as e:
            logger.error(f"[GAME] DB 저장 실패: {e}")
            db.rollback()
            return None

    # =========================================================
    # [새로운 기능] Func2 (8000번 포트)로 제어 신호 보내기
    # =========================================================
    def send_hardware_signal(self, is_active: bool):
        """
        Func1(8001) -> Func2(8000)로 HTTP 요청을 보냄
        is_active: True(시작), False(종료)
        """
        try:
            # Func2의 /api/control 엔드포인트 호출
            # 쿼리 파라미터로 run=true 또는 run=false 전달
            response = requests.post(
                FUNC2_CONTROL_URL, 
                params={"run": is_active}, 
                timeout=1
            )
            
            if response.status_code == 200:
                logger.info(f"[Hardware] 신호 전송 성공: {is_active}")
            else:
                logger.warning(f"[Hardware] 전송 실패 code: {response.status_code}")
                
        except Exception as e:
            logger.error(f"[Hardware] Func2 서버(8000) 연결 실패: {e}")
            logger.error("Func2 서버가 켜져 있는지 확인해주세요.")

# 전역 게임 핸들러 인스턴스
game_handler = GameHandler()