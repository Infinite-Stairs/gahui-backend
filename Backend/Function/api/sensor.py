# app/api/sensor.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from game.handler import game_handler
from websocket.manager import send_to_unity, send_to_dashboard
from utils.logger import logger

router = APIRouter(prefix="/sensor", tags=["sensor"])

class SensorInput(BaseModel):
    event_type: str  # STEP, H_STEP, measure_start, measure_finish

@router.post("")
async def receive_sensor_event(data: SensorInput):
    event = data.event_type.upper()
    
    if event in ["STEP", "H_STEP"]:
        if not game_handler.is_playing:
            logger.info(f"{event} 무시: 게임이 진행 중이 아님")
            return {"status": "ignored", "reason": "게임이 진행 중이 아닙니다."}
        
        step_data = game_handler.add_step(event)

        # Unity로 최소 신호 전송
        await send_to_unity({"action": "step"})

        return {"status": "ok", "message": f"{event} 감지됨"}

    elif event in ["MEASURE_START", "MEASURE_FINISH"]:
        game_handler.measure_active = (event == "MEASURE_START") #-> 위에 step 도 event 로 받는데 이것도 event 로 받아도되나?
        await send_to_dashboard({
            "action": event.lower()
        })
        logger.info(f"{event} 처리됨")
        return {"status": "ok", "message": f"{event} 처리됨"}

    else:
        logger.warning(f"알 수 없는 센서 이벤트: {event}")
        raise HTTPException(status_code=400, detail=f"잘못된 event_type: {event}")
