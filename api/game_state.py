from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from game.handler import game_handler
from utils.logger import logger
from pydantic import BaseModel
from datetime import date

router = APIRouter(tags=["game"])


class GameStateRequest(BaseModel):
    status: int                   # 1 = start, 0 = finish
    stairCount: int | None = None # 게임 종료 시만 필요


@router.post("/state")
async def update_game_state(request: GameStateRequest, db: Session = Depends(get_db)):
    # 게임 시작 ==========================
    if request.status == 1:
        if game_handler.is_playing:
            raise HTTPException(status_code=400, detail="게임이 이미 진행 중입니다.")

        game_handler.start_game()
        return {"status": "ok", "message": "게임이 시작되었습니다."}

    # 게임 종료 ==========================
    elif request.status == 0:
        if not game_handler.is_playing:
            raise HTTPException(status_code=400, detail="진행 중인 게임이 없습니다.")

        if request.stairCount is None:
            raise HTTPException(status_code=400, detail="stairCount가 필요합니다.")

        # Unity에서 전달한 steps 저장
        steps = request.stairCount
        game_handler.current_steps = steps

        # end_game(db, unity_steps) 로 연결
        result = game_handler.end_game(db, unity_steps=steps)

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

    else:
        raise HTTPException(status_code=400, detail="status는 0 또는 1이어야 합니다.")
