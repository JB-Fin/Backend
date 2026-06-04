from fastapi import APIRouter, UploadFile, File
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
    saved_file = save_upload_file(file)

    return {
        "message": "파일 업로드 완료",
        "data": saved_file,
    }

@router.get("")
def get_files():
    return {
        "message": "업로드 파일 목록 조회 완료",
        "data": list_uploaded_files(),
    }

@router.get("/download/{file_name}")
def download_file(file_name: str):
    file_path = get_output_file_path(file_name)

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )

@router.get("/uploaded/{file_name}")
def download_uploaded_file(file_name: str):
    file_path = get_uploaded_file_path(file_name)

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )