# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from db.session import engine
from db import models
from websocket import unity_ws, dashboard_ws
from api import sensor, game_state, results

# FastAPI 앱 초기화
app = FastAPI(
    title="Smart Step Game API",
    version="1.0.0",
    description="AI 기반 스마트 스텝박스 및 족저압 센서 연동 서버"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발단계에서는 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 (REST API)
app.include_router(sensor.router, prefix="/api/sensor", tags=["Sensor"])
app.include_router(game_state.router, prefix="/api/game/state", tags=["GameState"])
app.include_router(results.router, prefix="/api/game/results", tags=["GameResults"])


# DB 초기화 (테이블 자동 생성)
models.Base.metadata.create_all(bind=engine)


# 🔌 WebSocket 엔드포인트 등록
@app.websocket("/ws/unity")
async def unity_socket(websocket: WebSocket):
    """Unity ↔ Server WebSocket 통신"""
    await unity_ws.unity_endpoint(websocket)


@app.websocket("/ws/dashboard")
async def dashboard_socket(websocket: WebSocket):
    """Dashboard ↔ Server WebSocket 통신"""
    await dashboard_ws.dashboard_endpoint(websocket)


# 서버 기동 확인용 기본 루트
@app.get("/")
async def root():
    return {"status": "ok", "message": "Smart Step Game API Server Running"}


# 실행 (로컬 개발용)
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
