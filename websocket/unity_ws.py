# app/websocket/unity_ws.py
from fastapi import WebSocket
import json
from websocket.manager import connect_client, disconnect_client

async def unity_endpoint(websocket: WebSocket):

    """
    Unity 클라이언트 WebSocket 엔드포인트
    """
    await connect_client(websocket, client_type="unity")
    print("[WS] Unity client connected")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Unity에서 보낸 메시지 예시
            # {"action": "game_start"} / {"action": "game_finish"}
            action = message.get("action")

            if action == "game_start":
                print("[WS] Unity requested game start")
                # game_handler.handle_game_state(True) 호출 예정
            elif action == "game_finish":
                print("[WS] Unity requested game finish")
                # game_handler.handle_game_state(False) 호출 예정
            else:
                print(f"[WS] Unknown action from Unity: {action}")

    except Exception as e:
        print(f"[WS ERROR] Unity disconnected: {e}")

    finally:
        await disconnect_client(websocket, client_type="unity")
        print("[WS] Unity client disconnected")
