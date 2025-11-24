# app/api/game_state.py

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler

router = APIRouter(tags=["game"])


# 게임 시작 ======================================
@router.post("/start")
async def start_game(db: Session = Depends(get_db)):
    if game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")

    game_handler.start_game()
    return {"status": "ok", "message": "게임이 시작되었습니다."}


# 게임 종료 ======================================
@router.post("/end")
async def end_game(
    steps: int = Form(..., description="Unity 측에서 보낸 걸음 수"),
    db: Session = Depends(get_db)
):
    """Unity에서 steps를 Form-Data로 받음"""
    result = game_handler.end_game(db=db, unity_steps=steps)

    if result is None:
        raise HTTPException(status_code=500, detail="게임 종료 처리 실패")

    return {
        "status": "ok",
        "message": "게임이 종료되었습니다.",
        "result": {
            "steps": result.steps,
            "calories": result.calories
        }
    }


# 점수 저장 ======================================
@router.post("/score/submit")
async def submit_score(
    stairCount: int = Form(..., description="Unity에서 전달한 stairCount 값"),
    db: Session = Depends(get_db)
):
    """임시 점수 저장 테스트 API"""
    return {
        "status": "ok",
        "message": "점수 저장 완료",
        "stairs": stairCount
    }
