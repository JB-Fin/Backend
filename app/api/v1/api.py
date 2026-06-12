from fastapi import APIRouter

from app.api.v1.endpoints import auth, files, reviews, chat, languages, alarm, calendar

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(languages.router, prefix="/languages", tags=["Languages"])
api_router.include_router(alarm.router, prefix="/alarms", tags=["Alarms"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"],)
# api_router.include_router(edu_content.router, prefix="/edu-content", tags=["Edu Content"],)