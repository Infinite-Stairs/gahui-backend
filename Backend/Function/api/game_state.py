# app/api/game_state.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from pydantic import BaseModel

router = APIRouter(tags=["game"])

# ==============================================
# Pydantic 모델
# ==============================================
class ScoreSubmit(BaseModel):
    stairCount: int  # 계단 수

class EndGameRequest(BaseModel):
    stairCount: int  # Unity에서 보내는 계단 수


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
    """
    Unity에서 JSON으로 stairCount 받음
    게임 종료 + DB 저장 처리
    """
    steps = data.stairCount
    result = game_handler.end_game(db=db, unity_steps=steps)

    if result is None:
        raise HTTPException(status_code=500, detail="게임 종료 처리 실패")

    return {
        "status": "ok",
        "message": "게임이 종료되었습니다.",
        "result": {
            "stairCount": result.steps,  # stairCount로 반환
            "calories": result.calories
        }
    }


# ==============================================
# 점수 저장
# ==============================================
@router.post("/score/submit")
async def submit_score(data: ScoreSubmit, db: Session = Depends(get_db)):
    """
    Unity에서 JSON으로 stairCount 받음
    실제 점수 저장 처리
    """
    return {
        "status": "ok",
        "message": "점수 저장 완료",
        "stairCount": data.stairCount
    }
