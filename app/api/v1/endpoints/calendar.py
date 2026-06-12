from fastapi import APIRouter

from app.api.v1.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarEventUpdate
)

from app.services.calendar_service import (
    create_event,
    get_events,
    get_event_by_id,
    update_event,
    delete_event,
)

router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
)


@router.get("")
def read_calendar(
    year: int | None = None,
    month: int | None = None,
):
    return {
        "calendar_events": get_events(year, month)
    }


@router.get("/{event_id}")
def read_event(event_id: int):
    return get_event_by_id(event_id)


@router.post("")
def create_calendar_event(
    payload: CalendarEventCreate,
):
    return create_event(payload)


@router.patch("/{event_id}")
def update_calendar_event(
    event_id: int,
    payload: CalendarEventUpdate,
):
    return update_event(event_id, payload)


@router.delete("/{event_id}")
def delete_calendar_event(
    event_id: int,
):
    return delete_event(event_id)