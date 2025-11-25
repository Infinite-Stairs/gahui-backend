# main_healthcare.py
from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .db_healthcare import init_schema, insert_result, fetch_latest
from .models_healthcare import IngestRequest, IngestResponse
from .compute import compute_all

app = FastAPI(title="Plantar-min API (CoP + stddev)", version="2.0")

# CORS 설정 (프론트에서 자유롭게 호출 가능하도록 전체 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],      # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"],      # 모든 헤더 허용
)

# 서버 시작 시 스키마 생성
init_schema()


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    """
    라즈베리파이(또는 노트북 시리얼 리더)에서 10초 윈도우 요약을 보내는 엔드포인트.
    
    1) 좌/우 퍼센트, CoP, 정상/의심 여부 계산 (compute_all)
    2) DB에 한 레코드로 저장
    3) 프론트/라즈베리에 지표만 응답
    """
    if (req.left_sum_avg + req.right_sum_avg) <= 1e-9:
        raise HTTPException(
            status_code=400,
            detail="No effective pressure (left+right ≈ 0)",
        )

    # 계산
    calc = compute_all(
        req.l1_avg, req.l2_avg, req.l3_avg,
        req.r1_avg, req.r2_avg, req.r3_avg,
        left_sum_avg=req.left_sum_avg,
        right_sum_avg=req.right_sum_avg,
        thr_pct=5.0,
    )

    # DB에 넣을 row 구성
    row = {
        "l1_avg": req.l1_avg,
        "l2_avg": req.l2_avg,
        "l3_avg": req.l3_avg,
        "r1_avg": req.r1_avg,
        "r2_avg": req.r2_avg,
        "r3_avg": req.r3_avg,
        "left_sum_avg": req.left_sum_avg,
        "right_sum_avg": req.right_sum_avg,
        "overall_avg": req.overall_avg,
        "left_std": req.left_std,
        "right_std": req.right_std,
        "left_pct": calc["left_pct"],
        "right_pct": calc["right_pct"],
        "cop_x_pct": calc["cop_x_pct"],
        "cop_y_pct": calc["cop_y_pct"],
        "cop_ok": calc["cop_ok"],
    }

    # DB 저장 (id, created_at 반환)
    meta = insert_result(row)

    # 응답 모델로 변환해서 리턴
    return IngestResponse(
        id=meta["id"],
        created_at=meta["created_at"],
        left_pct=calc["left_pct"],
        right_pct=calc["right_pct"],
        cop_x_pct=calc["cop_x_pct"],
        cop_y_pct=calc["cop_y_pct"],
        cop_ok=calc["cop_ok"],
        left_std=req.left_std,
        right_std=req.right_std,
    )


@app.get("/latest")
def latest(n: int = Query(5, ge=1, le=200)):
    return fetch_latest(n)


@app.get("/metrics")
def metrics(n: int = Query(20, ge=1, le=500)):
    return fetch_latest(n)


#collector.py 자동 작동을 위한 것 - 프론트 필요 없음
is_collecting = False   # 전역 변수

@app.post("/control")
def set_control(run: bool):
    """
    run=True  → 수집 시작
    run=False → 수집 정지
    """
    global is_collecting
    is_collecting = run
    return {"ok": True, "is_collecting": is_collecting}

@app.get("/control")
def get_control():
    """collector가 현재 상태를 조회할 때 쓰는 API"""
    return {"is_collecting": is_collecting}