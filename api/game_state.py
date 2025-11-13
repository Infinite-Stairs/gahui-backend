# app/api/game_state.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from utils.logger import logger

router = APIRouter(prefix="/api/game", tags=["game"])

@router.post("/start")
async def start_game():
    if game_handler.is_playing:
        logger.warning("게임 시작 요청 무시: 이미 진행 중")
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")
    game_handler.start_game()
    return {"status": "ok", "message": "게임이 시작되었습니다."}

@router.post("/finish")
async def finish_game(db: Session = Depends(get_db)):
    if not game_handler.is_playing:
        logger.warning("게임 종료 요청 무시: 진행 중인 게임 없음")
        raise HTTPException(status_code=400, detail="진행 중인 게임이 없습니다.")
    
    result = game_handler.end_game(db)
    if result is None:
        raise HTTPException(status_code=500, detail="결과 저장 실패")
    
    return {
        "status": "ok",
        "message": "게임이 종료되었습니다.",
        "result": {
            "steps": result.steps,
            "calories": result.calories,
        }
    }
