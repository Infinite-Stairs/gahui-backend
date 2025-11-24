from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from pydantic import BaseModel

router = APIRouter(tags=["game"])


class ScoreRequest(BaseModel):
    stairCount: int


# 게임 시작 ======================================
@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    if game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")

    game_handler.start_game()
    return {"status": "ok", "message": "게임이 시작되었습니다."}


# 게임 종료 ======================================
@router.post("/end")
async def end_game(db: Session = Depends(get_db)):
    if not game_handler.is_playing:
        raise HTTPException(status_code=400, detail="진행 중인 게임이 없습니다.")

    # 게임 종료 처리
    result = game_handler.end_game(db)

    if result is None:
        raise HTTPException(status_code=500, detail="게임 종료 처리 실패")

    return {"status": "ok", "message": "게임이 종료되었습니다."}


# 점수 저장 ======================================
@router.post("/score/submit")
async def submit_score(request: ScoreRequest, db: Session = Depends(get_db)):
    if not game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 진행되지 않았습니다.")

    # Unity에서 전달한 stairCount 저장
    game_handler.current_steps = request.stairCount
    result = game_handler.save_score(db, unity_steps=request.stairCount)

    if result is None:
        raise HTTPException(status_code=500, detail="점수 저장 실패")

    return {
        "status": "ok",
        "message": "점수가 저장되었습니다.",
        "result": {
            "steps": result.steps,
            "calories": result.calories
        }
    }
