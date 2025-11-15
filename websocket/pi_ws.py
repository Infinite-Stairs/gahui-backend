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



#0,1 신호 받는 라즈베리파이 코드, 웹소켓 보유 가정
# import asyncio
# import websockets
# import json

# SERVER_URL = "ws://YOUR_SERVER_IP:8000/ws/pi"

# async def listen():
#     async with websockets.connect(SERVER_URL) as ws:
#         print("Connected to server")

#         while True:
#             msg = await ws.recv()
#             data = json.loads(msg)

#             game_active = data.get("game_active")
#             print("Received:", game_active)

#             if game_active == 1:
#                 print("🔥 게임 시작 → 하드웨어 ON")
#                 # GPIO 동작 코드
#             elif game_active == 0:
#                 print("🛑 게임 종료 → 하드웨어 OFF")
#                 # GPIO 끄기

# asyncio.run(listen())

