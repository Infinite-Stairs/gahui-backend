# app/api/results.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import GameResult

router = APIRouter(prefix="/api/game/results", tags=["results"])


@router.get("")
def get_all_results(db: Session = Depends(get_db)):
    """
    📋 전체 게임 결과 조회
    """
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


@router.get("/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    """
    📄 특정 게임 결과 조회
    """
    result = db.query(GameResult).filter(GameResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    
    return {
        "id": result.id,
        "steps": result.steps,
        "calories": result.calories,
        "sensor_type": result.sensor_type,
    }
