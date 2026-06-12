from datetime import datetime, timezone
from fastapi import HTTPException, status

CALENDAR_DB = []
EVENT_ID_SEQ = 1

def create_event(data):
    global EVENT_ID_SEQ

    event = {
        "event_id": EVENT_ID_SEQ,
        **data.dict(),
        "created_at": datetime.now(tz=timezone.utc),
    }

    CALENDAR_DB.append(event)

    EVENT_ID_SEQ += 1

    return event

def get_events(year: int = None, month: int = None):

    if year and month:
        return [
            event
            for event in CALENDAR_DB
            if event["start_date"].year == year
            and event["start_date"].month == month
        ]

    return CALENDAR_DB

def get_event_by_id(event_id: int):

    for event in CALENDAR_DB:
        if event["event_id"] == event_id:
            return event

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="일정을 찾을 수 없습니다."
    )

def update_event(event_id: int, update_data):

    event = get_event_by_id(event_id)

    for key, value in update_data.dict(exclude_none=True).items():
        event[key] = value

    return event

def delete_event(event_id: int):

    event = get_event_by_id(event_id)

    CALENDAR_DB.remove(event)

    return {
        "message": "일정이 삭제되었습니다."
    }