from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .db_healthcare import init_schema, insert_result, fetch_latest
from .models_healthcare import IngestRequest, IngestResponse
from .compute import compute_all


app = FastAPI(title="Plantar-min API (CoP + stddev)", version="2.0")

origins = [
    "https://dowhile001.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],      # 모든 HTTP 메서드 허용 (GET, POST 등)
    allow_headers=["*"],      # 모든 헤더 허용
)

init_schema()


@app.post("/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    if (req.left_sum_avg + req.right_sum_avg) <= 1e-9:
        raise HTTPException(status_code=400, detail="No effective pressure (left+right ≈ 0)")

    calc = compute_all(
        req.l1_avg, req.l2_avg, req.l3_avg,
        req.r1_avg, req.r2_avg, req.r3_avg,
        left_sum_avg=req.left_sum_avg,
        right_sum_avg=req.right_sum_avg,
        thr_pct=5.0,  
    )

    row = {
        "l1_avg": req.l1_avg, "l2_avg": req.l2_avg, "l3_avg": req.l3_avg,
        "r1_avg": req.r1_avg, "r2_avg": req.r2_avg, "r3_avg": req.r3_avg,
        "left_sum_avg": req.left_sum_avg, "right_sum_avg": req.right_sum_avg,
        "overall_avg": req.overall_avg,
        "left_std": req.left_std, "right_std": req.right_std,
        "left_pct": calc["left_pct"], "right_pct": calc["right_pct"],
        "cop_x_pct": calc["cop_x_pct"], "cop_y_pct": calc["cop_y_pct"],
        "cop_ok": calc["cop_ok"],
    }

    meta = insert_result(row)

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

#서버 포트 고정
#uvicorn DB_Health.server.main_healthcare:app --reload --port 8000