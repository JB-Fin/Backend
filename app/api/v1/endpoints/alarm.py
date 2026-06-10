from fastapi import APIRouter, HTTPException, status

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

# dummy_alarms = [{},{},{}]

@router.post("", response_model=AlarmResponse)
def create_new_alarm(request: AlarmCreateRequest):
    try:
        return create_alarm(
            title=request.title,
            message=request.message,
            alarm_time=request.alarm_time,
            review_id=request.review_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알람 생성 중 오류가 발생했습니다: {str(e)}",
        )

@router.get("", response_model=list[AlarmResponse])
def list_alarms():
    try:
        return get_alarms()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알람 목록 조회 중 오류가 발생했습니다: {str(e)}",
        )

@router.patch("/{alarm_id}", response_model=AlarmResponse)
def patch_alarm(alarm_id: int, request: AlarmUpdateRequest):
    try:
        return update_alarm(
            alarm_id=alarm_id,
            update_data=request.model_dump(exclude_unset=True),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"알람 수정 실패: {str(e)}",
        )

@router.delete("/{alarm_id}")
def remove_alarm(alarm_id: int):
    try:
        return delete_alarm(alarm_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"알람 삭제 실패: {str(e)}",
        )