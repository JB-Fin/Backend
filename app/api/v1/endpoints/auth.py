from fastapi import APIRouter, HTTPException

from app.api.v1.schemas.auth import LoginRequest, LoginResponse

router = APIRouter()

@router.post(
    "/login", 
    response_model=LoginResponse)

def login(request: LoginRequest):
    if not request.user_id or not request.password:
        raise HTTPException(
            status_code=400,
            detail="아이디 또는 비밀번호가 잘못되었습니다."
        )
    return {
        # 현재 더미데이터로 임시 구현
        "access_token": "dummy-access-token",
        "token_type": "bearer",
        "user":{
            "id": request.user_id,
            "name": "김준법",
            "team": "준법자문가 연구소"
        },
    }

@router.post("/logout")
def logout():
    return {
        "message": "로그아웃 완료"
    }