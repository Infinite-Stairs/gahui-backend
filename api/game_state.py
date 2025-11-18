from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from utils.logger import logger
from pydantic import BaseModel

class FinishGameRequest(BaseModel):
    steps: int

router = APIRouter(prefix="/api/game", tags=["game"])

@router.post("/start")
async def start_game():
    if game_handler.is_playing:
        raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")
    game_handler.start_game()
    return {"status": "ok", "message": "게임이 시작되었습니다."}

@router.post("/finish")
async def finish_game(request: FinishGameRequest, db: Session = Depends(get_db)):
    if not game_handler.is_playing:
        raise HTTPException(status_code=400, detail="진행 중인 게임이 없습니다.")

    # Unity에서 전달한 steps 저장
    game_handler.current_steps = request.steps

    # end_game은 steps를 받지 않음
    result = game_handler.end_game(db, unity_steps=request.steps)

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
