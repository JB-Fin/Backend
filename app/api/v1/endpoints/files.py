from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse

from app.services.file_service import (
    save_upload_file,
    get_output_file_path,
    get_uploaded_file_path,
    list_uploaded_files,
)

router = APIRouter()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    try:
        saved_file = save_upload_file(file)

        return {
            "message": "파일 업로드 완료",
            "data": saved_file,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}",
        )

@router.get("")
def get_files():
    try:
        return {
            "message": "업로드 파일 목록 조회 완료",
            "data": list_uploaded_files(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 목록 조회 중 오류가 발생했습니다: {str(e)}",
        )

@router.get("/download/{file_name}")
def download_file(file_name: str):
    try:
        file_path = get_output_file_path(file_name)

        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"파일 다운로드 실패: {str(e)}",
        )

@router.get("/uploaded/{file_name}")
def download_uploaded_file(file_name: str):
    try:
        file_path = get_uploaded_file_path(file_name)

        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"업로드 파일 다운로드 실패: {str(e)}",
        )