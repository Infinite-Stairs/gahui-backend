# Func1/api/game_state.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from pydantic import BaseModel
import serial
import sys, os

router = APIRouter(tags=["game"])

ARDUINO_PORT = '/dev/ttyACM0'  # 윈도우라면 COM3, 라즈베리파이라면 /dev/ttyACM0 등
BAUD_RATE = 9600

# ==============================================
# Pydantic 모델
# ==============================================
class ScoreSubmit(BaseModel):
    stairCount: int 

class EndGameRequest(BaseModel):
    stairCount: int

# ==============================================
# 게임 시작
# ==============================================
@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    if game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")
    game_handler.start_game()
    return {"status": "ok", "message": "게임이 시작되었습니다."}


# ==============================================
# 게임 종료
# ==============================================
@router.post("/end")
async def end_game(data: EndGameRequest, db: Session = Depends(get_db)):
    steps = data.stairCount
    result = game_handler.end_game(db=db, unity_steps=steps)
    if result is None:
        raise HTTPException(status_code=500, detail="게임 종료 처리 실패")
    
    return {
        "status": "ok",
        "message": "게임이 종료되었습니다.",
        "result": {
            "stairCount": result.steps,
            "calories": result.calories
        }
    }


# ==============================================
# 점수 저장
# ==============================================
@router.post("/score/submit")
async def submit_score(data: ScoreSubmit, db: Session = Depends(get_db)):
    
    # [1] 아두이노로 '0' 전송 로직 (일회성 연결)
    try:
        # with 구문을 쓰면 통신 후 자동으로 close() 해줍니다.
        # timeout=1은 연결이 안 될 경우 1초 뒤에 끊어버려서 서버 멈춤을 방지합니다.
        with serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1) as ser:
            command = "0\n" # 줄바꿈 문자 포함 (아두이노 코드에 따라 필요할 수 있음)
            ser.write(command.encode()) # 바이트로 변환하여 전송
            print(f">>> [Direct] 아두이노로 '0' 전송 성공")
            
    except serial.SerialException as e:
        # 포트가 없거나, 이미 다른 곳에서 사용 중일 때 발생
        print(f">>> [Error] 아두이노 연결 실패: {e}")
        # 아두이노 연결 실패가 점수 저장을 막으면 안 되므로 에러를 띄우지 않고 넘어갑니다.
        # 필요하다면 raise HTTPException(...) 처리를 해도 됩니다.

    # [2] 결과 반환
    return {
        "status": "ok",
        "message": "점수 저장 완료",
        "stairCount": data.stairCount
    }