
from datetime import datetime
from pydantic import BaseModel, HttpUrl, ConfigDict


class MonitorCreate(BaseModel):
    name: str
    url: HttpUrl


class MonitorResponse(BaseModel):
    id: int
    name: str
    url: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HealthCheckResponse(BaseModel):
    id: int
    monitor_id: int
    status_code: int | None
    response_time: float | None
    is_success: bool | None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)
