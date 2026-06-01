from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

from app.services.file_service import save_upload_file, get_output_file_path

router = APIRouter()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    result = save_upload_file(file)

    return {
        "message": "문서 업로드 성공",
        "filename": result["filename"],
        "saved_path": result["saved_path"],
    }

@router.get("/download/{file_name}")
def download_file(file_name: str):
    file_path = get_output_file_path(file_name)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="파일을 찾을 수 없습니다.",
        )

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream",
    )