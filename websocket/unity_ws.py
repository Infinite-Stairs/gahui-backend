# app/websocket/unity_ws.py
from fastapi import WebSocket
import json
from websocket.manager import connect_client, disconnect_client, send_to_pi

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
            # {"state"=1} / {"state"=0}
            state = message.get("state")

            if state==1:
                print("[WS] Unity requested game start")
                # game_handler.handle_game_state(True) 호출 예정
                await send_to_pi({"game_active": 1})

            elif state==0:
                print("[WS] Unity requested game finish")
                # game_handler.handle_game_state(False) 호출 예정
                await send_to_pi({"game_active": 0})

            else:
                print(f"[WS] Unknown action from Unity: {state}")

    except Exception as e:
        print(f"[WS ERROR] Unity disconnected: {e}")

    finally:
        await disconnect_client(websocket, client_type="unity")
        print("[WS] Unity client disconnected")

