# app/websocket/dashboard_ws.py
from fastapi import WebSocket
import json
from websocket.manager import connect_client, disconnect_client

async def dashboard_endpoint(websocket: WebSocket):
    """
    Dashboard 클라이언트 WebSocket 엔드포인트
    """
    await connect_client(websocket, client_type="dashboard")
    print("[WS] Dashboard client connected")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Dashboard → Server 요청 처리 (선택적)
            action = message.get("action")

            if action == "request_status":
                print("[WS] Dashboard requested status update")
                # 여기서 현재 게임 상태, 센서 상태 보내기 가능
            else:
                print(f"[WS] Unknown action from Dashboard: {action}")

    except Exception as e:
        print(f"[WS ERROR] Dashboard disconnected: {e}")

    finally:
        await disconnect_client(websocket, client_type="dashboard")
        print("[WS] Dashboard client disconnected")
