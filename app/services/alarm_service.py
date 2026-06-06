from datetime import datetime, timezone
from fastapi import HTTPException, status

ALARMS_DB = []
ALARM_ID_SEQ = 1

def create_alarm(title: str, message: str | None, alarm_time, review_id: int | None):
    global ALARM_ID_SEQ

    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="알람 제목은 필수입니다.",
        )

    alarm = {
        "alarm_id": ALARM_ID_SEQ,
        "title": title,
        "message": message,
        "alarm_time": alarm_time,
        "review_id": review_id,
        "is_done": False,
        "created_at": datetime.now(tz=timezone.utc),
    }

    ALARMS_DB.append(alarm)
    ALARM_ID_SEQ += 1

    return alarm

def get_alarms():
    return ALARMS_DB

def get_alarm_by_id(alarm_id: int):
    for alarm in ALARMS_DB:
        if alarm["alarm_id"] == alarm_id:
            return alarm

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="알람을 찾을 수 없습니다.",
    )

def update_alarm(alarm_id: int, update_data: dict):
    alarm = get_alarm_by_id(alarm_id)
  
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 알람 정보가 없습니다.",
        )

    for key, value in update_data.items():
        if value is not None:
            alarm[key] = value

    return alarm

def delete_alarm(alarm_id: int):
    alarm = get_alarm_by_id(alarm_id)
    ALARMS_DB.remove(alarm)

    return {"message": "알람 삭제 완료"}