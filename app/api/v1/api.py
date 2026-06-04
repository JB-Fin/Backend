from fastapi import APIRouter

from app.api.v1.endpoints import auth, files, reviews, history, chat, regulations, languages, alarm

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(regulations.router, prefix="/regulations", tags=["Regulations"])
api_router.include_router(languages.router, prefix="/languages", tags=["Languages"])
api_router.include_router(alarm.router, prefix="/alarms", tags=["Alarms"])