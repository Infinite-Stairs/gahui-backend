# app/api/results.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import GameResult

router = APIRouter(prefix="/api/game/results", tags=["results"])

# 전체 게임 결과 조회
@router.get("")
def get_all_results(db: Session = Depends(get_db)):
    
    results = db.query(GameResult).order_by(GameResult.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "steps": r.steps,
            "calories": r.calories,
            "sensor_type": r.sensor_type,
        }
        for r in results
    ]


# 특정 게임 결과 조회

@router.get("/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    
    result = db.query(GameResult).filter(GameResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    
    return {
        "id": result.id,
        "steps": result.steps,
        "calories": result.calories,
        "sensor_type": result.sensor_type,
    }


# 특정 날짜의 누적 계단 수/칼로리 합계 리턴
@router.get("/daily")
def get_daily_summary(date_str: str, db: Session = Depends(get_db)):

    target_date = date.fromisoformat(date_str)

    results = (
        db.query(GameResult)
        .filter(GameResult.play_date == target_date)
        .all()
    )

    total_steps = sum(r.steps for r in results)
    total_calories = sum(r.calories for r in results)

    return {
        "date": target_date,
        "total_steps": total_steps,
        "total_calories": total_calories,
    }
# 대시보드에서 호출
# GET http://서버주소/api/game/results/daily?date_str=2025-11-14


