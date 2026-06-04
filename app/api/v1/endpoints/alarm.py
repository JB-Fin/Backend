from fastapi import APIRouter

from app.api.v1.schemas.alarm import (
    AlarmCreateRequest,
    AlarmUpdateRequest,
    AlarmResponse,
)
from app.services.alarm_service import (
    create_alarm,
    get_alarms,
    update_alarm,
    delete_alarm,
)

router = APIRouter()

@router.post("", response_model=AlarmResponse)
def create_new_alarm(request: AlarmCreateRequest):
    return create_alarm(
        title=request.title,
        message=request.message,
        alarm_time=request.alarm_time,
        review_id=request.review_id,
    )

@router.get("", response_model=list[AlarmResponse])
def list_alarms():
    return get_alarms()

@router.patch("/{alarm_id}", response_model=AlarmResponse)
def patch_alarm(alarm_id: int, request: AlarmUpdateRequest):
    return update_alarm(
        alarm_id=alarm_id,
        update_data=request.model_dump(exclude_unset=True),
    )

@router.delete("/{alarm_id}")
def remove_alarm(alarm_id: int):
    return delete_alarm(alarm_id)