# app/websocket/pi_ws.py
from fastapi import WebSocket
from websocket.manager import connect_client, disconnect_client

async def pi_endpoint(websocket: WebSocket):
    await connect_client(websocket, "pi")
    print("[WS] Raspberry Pi connected")

    try:
        while True:
            # Pi가 보낼 일은 없지만 혹시 모를 데이터 수신 처리
            data = await websocket.receive_text()
            print("[WS] Pi sent (ignored):", data)

    except Exception as e:
        print("[WS ERROR] Raspberry Pi disconnected:", e)

    finally:
        await disconnect_client(websocket, "pi")
        print("[WS] Raspberry Pi disconnected")



