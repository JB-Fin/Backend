from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # 프론트 배포 시 주소 추가
    # "https://jb-fin-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Hello World"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }

app.include_router(api_router, prefix="/api/v1")