# Func1/api/game_state.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from pydantic import BaseModel
import sys, os

# =================================================================
# [★핵심 수정] Func1 전용 공유 메모장 가져오기
# 이제 Func2나 복잡한 경로 설정 없이 바로 가져옵니다.
# =================================================================
from global_state import state

router = APIRouter(tags=["game"])

# ==============================================
# Pydantic 모델
# ==============================================
class ScoreSubmit(BaseModel):
    stairCount: int 

class EndGameRequest(BaseModel):
    stairCount: int

# ==============================================
# [직접 전송 함수] state를 통해 아두이노 제어
# ==============================================
def send_direct_to_arduino(command: str):
    """
    Func1/global_state.py에 저장된 시리얼 연결을 통해 즉시 전송
    """
    try:
        # 1. state에 시리얼 연결이 존재하는지, 열려있는지 확인
        if state.serial_connection is not None and state.serial_connection.is_open:
            # 2. 직접 전송 (Write)
            msg = f"{command}\n" # 줄바꿈 문자 포함
            state.serial_connection.write(msg.encode())
            state.serial_connection.flush() # 즉시 전송
            print(f">>> [Direct] 아두이노로 '{command}' 발사 성공! 🚀")
        else:
            print(f">>> [Direct] ⚠️ 시리얼 포트가 연결되어 있지 않습니다. (main.py 확인)")
            
    except Exception as e:
        print(f">>> [Direct] ❌ 전송 실패: {e}")

# ==============================================
# 게임 시작
# ==============================================
@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    # 게임 중복 시작 방지
    if game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")

    game_handler.start_game()

    # [1] 데이터 수집 시작 (논리적 플래그)
    state.is_collecting = True
    
    # [2] 아두이노 물리적 켜기 (직접 명령)
    send_direct_to_arduino("1")

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

    # [1] 데이터 수집 중단 (논리적 플래그)
    state.is_collecting = False
    
    # [2] 아두이노 물리적 끄기 (직접 명령)
    send_direct_to_arduino("0")

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
    return {
        "status": "ok",
        "message": "점수 저장 완료",
        "stairCount": data.stairCount
    }