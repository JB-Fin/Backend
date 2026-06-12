from datetime import date, time, datetime
from typing import Optional

from pydantic import BaseModel

class CalendarEventCreate(BaseModel):
    title: str
    category: str
    start_date: date
    end_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    department: Optional[str] = None
    memo: Optional[str] = None


class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = None
    department: Optional[str] = None
    memo: Optional[str] = None


class CalendarEventResponse(BaseModel):
    event_id: int
    title: str
    category: str
    start_date: date
    end_date: date
    start_time: Optional[time]
    end_time: Optional[time]
    location: Optional[str]
    department: Optional[str]
    memo: Optional[str]
    created_at: datetime