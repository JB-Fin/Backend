import shutil, threading

from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".csv",
    ".xlsx",
    ".pptx",
}

MAX_FILE_SIZE = 20 * 1024 * 1024

FILES_DB = []
FILE_ID_SEQ = 1
_lock = threading.Lock()


def sanitize_filename(filename: str) -> str:
    return Path(filename).name.replace(" ", "_")


def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일명이 없습니다.",
        )

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. 허용 형식: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )


def save_upload_file(file: UploadFile) -> dict:
    global FILE_ID_SEQ

    validate_file(file)
    UPLOAD_DIR.mkdir(exist_ok=True)

    original_filename = sanitize_filename(file.filename)
    file_extension = Path(original_filename).suffix.lower()
    saved_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        file.file.seek(0)

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size

        if file_size > MAX_FILE_SIZE:
            file_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="파일 크기가 너무 큽니다. 최대 20MB까지 업로드할 수 있습니다.",
            )

        with _lock:
            file_id = FILE_ID_SEQ
            FILE_ID_SEQ += 1

            file_info = {
                "file_id": file_id,
                "original_filename": original_filename,
                "saved_filename": saved_filename,
                "filename": saved_filename,
                "file_name": saved_filename,
                "saved_path": str(file_path),
                "file_size": file_size,
                "content_type": file.content_type,
                "uploaded_at": datetime.now(tz=timezone.utc).isoformat(),
            }

            FILES_DB.append(file_info)

        return file_info

    except HTTPException:
        raise

    except Exception as e:
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}",
        )


def get_file_by_id(file_id: int) -> dict:
    for file_info in FILES_DB:
        if file_info["file_id"] == file_id:
            return file_info

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="파일을 찾을 수 없습니다.",
    )


def get_uploaded_file_path(file_name: str) -> Path:
    safe_file_name = sanitize_filename(file_name)
    file_path = UPLOAD_DIR / safe_file_name

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="업로드 파일을 찾을 수 없습니다.",
        )

    return file_path


def get_output_file_path(file_name: str) -> Path:
    safe_file_name = sanitize_filename(file_name)
    file_path = OUTPUT_DIR / safe_file_name

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="결과 파일을 찾을 수 없습니다.",
        )

    return file_path


def list_uploaded_files() -> list[dict]:
    UPLOAD_DIR.mkdir(exist_ok=True)
    return FILES_DB


def list_output_files() -> list[dict]:
    OUTPUT_DIR.mkdir(exist_ok=True)

    files = []

    for file_path in OUTPUT_DIR.iterdir():
        if file_path.is_file():
            files.append(
                {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "file_size": file_path.stat().st_size,
                    "modified_at": datetime.fromtimestamp(
                        file_path.stat().st_mtime,
                        tz=timezone.utc,
                    ).isoformat(),
                }
            )

    return files