from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.auth import LoginRequest, LoginResponse, LogoutResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    if (
        request.user_id != "admin"
        or request.password != "1234"
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다."
        )
    return {
        # 현재 더미데이터로 임시 구현
        "access_token": "dummy-access-token",
        "token_type": "bearer",
        "user":{
            "id": "admin",
            "name": "김준법",
            "team": "준법자문가 연구소"
        },
    }

@router.post("/logout", response_model=LogoutResponse)
def logout():
    # JWT 기반이면 클라이언트에서 토큰 삭제.
    # 서버 세션/블랙리스트 방식이면 여기서 토큰 무효화 처리.
    return {
        "message": "로그아웃 완료"
    }