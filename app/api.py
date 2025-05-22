from fastapi import FastAPI
from app.state import get_state
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class SensorData(BaseModel):
    sensor_ready: bool
    last_update: datetime | None
    uptime: float | None
    turbidity: float | None
    temperature: float | None
    total_dissolved_solids: float | None
    pH: float | None

@app.get("/read", response_model=SensorData)
async def read() -> SensorData:
    return get_state()