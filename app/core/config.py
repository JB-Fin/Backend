# 환경변수 관리
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Compliance AI Backend"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173, http://127.0.0.1:5173"
    DATABASE_URL: str = "sqlite:///./compliance.db"

    class Config:
        env_file = ".env"


settings = Settings()