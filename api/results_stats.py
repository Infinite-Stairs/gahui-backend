# app/api/results_stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from db.models import GameResult

router = APIRouter(prefix="/api/game/stats", tags=["stats"])

@router.get("/daily")
def get_daily_summary(db: Session = Depends(get_db)):
    """
    날짜별 누적 steps, calories 조회
    """

    rows = (
        db.query(
            func.date(GameResult.created_at).label("date"),
            func.sum(GameResult.steps).label("total_steps"),
            func.sum(GameResult.calories).label("total_calories"),
        )
        .group_by(func.date(GameResult.created_at))
        .order_by(func.date(GameResult.created_at).desc())
        .all()
    )

    return [
        {
            "date": str(row.date),
            "steps": row.total_steps,
            "calories": float(row.total_calories),
        }
        for row in rows
    ]
