from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlarmCreateRequest(BaseModel):
    title: str
    message: Optional[str] = None
    alarm_time: datetime
    review_id: Optional[int] = None

class AlarmUpdateRequest(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    alarm_time: Optional[datetime] = None
    is_done: Optional[bool] = None

class AlarmResponse(BaseModel):
    alarm_id: int
    title: str
    message: Optional[str] = None
    alarm_time: datetime
    review_id: Optional[int] = None
    is_done: bool
    created_at: datetime