# FUNCTION/api/results.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from db.models import GameResult

router = APIRouter(tags=["results"])


#전체 게임 결과 조회 (리스트)
@router.get("")
def get_all_results(db: Session = Depends(get_db)):
    results = db.query(GameResult).order_by(GameResult.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "steps": r.steps,
            "calories": r.calories,
            "sensor_type": r.sensor_type,
            "play_date": r.play_date,
            "created_at": r.created_at,
        }
        for r in results
    ]


# #단일 게임 결과 조회
# @router.get("/{result_id}")
# def get_result(result_id: int, db: Session = Depends(get_db)):
#     result = db.query(GameResult).filter(GameResult.id == result_id).first()
#     if not result:
#         raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")

#     return {
#         "id": result.id,
#         "steps": result.steps,
#         "calories": result.calories,
#         "sensor_type": result.sensor_type,
#         "play_date": result.play_date,
#         "created_at": result.created_at,
#     }


#특정 날짜 동의 집계 (SUM)
# GET /api/game/results/daily?date_str=2025-11-17
@router.get("/daily")
def get_daily_summary(
    date_str: str = Query(..., description="조회할 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식이 잘못되었습니다. YYYY-MM-DD 사용해주세요.")

    query = (
        db.query(
            func.sum(GameResult.steps).label("total_steps"),
            func.sum(GameResult.calories).label("total_calories"),
        )
        .filter(GameResult.play_date == target_date)
    )

    result = query.first()

    return {
        "date": target_date,
        "total_steps": result.total_steps or 0,
        "total_calories": float(result.total_calories or 0),
    }
