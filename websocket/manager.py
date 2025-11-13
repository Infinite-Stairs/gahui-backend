# app/websocket/manager.py
import asyncio
from typing import List
from fastapi import WebSocket

# 연결된 클라이언트 저장
unity_clients: List[WebSocket] = []
dashboard_clients: List[WebSocket] = []

# WebSocket 전송 유틸
async def send_to_unity(message: dict):
    """모든 Unity 클라이언트에게 메시지 전송"""
    disconnected = []
    for client in unity_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        unity_clients.remove(client)


async def send_to_dashboard(message: dict):
    """모든 Dashboard 클라이언트에게 메시지 전송"""
    disconnected = []
    for client in dashboard_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.append(client)
    for client in disconnected:
        dashboard_clients.remove(client)



# 클라이언트 연결/해제 관리
async def connect_client(websocket: WebSocket, client_type: str):

    """
    클라이언트 연결 등록
    client_type = "unity" | "dashboard"
    """
    await websocket.accept()
    if client_type == "unity":
        unity_clients.append(websocket)
    elif client_type == "dashboard":
        dashboard_clients.append(websocket)


async def disconnect_client(websocket: WebSocket, client_type: str):
    
    """
    클라이언트 연결 해제
    """
    if client_type == "unity" and websocket in unity_clients:
        unity_clients.remove(websocket)
    elif client_type == "dashboard" and websocket in dashboard_clients:
        dashboard_clients.remove(websocket)
