from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

def save_upload_file(file: UploadFile) -> dict:
    UPLOAD_DIR.mkdir(exist_ok=True)

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return {
        "filename": file.filename,
        "saved_path": str(file_path),
    }

def get_output_file_path(file_name: str) -> Path:
    return OUTPUT_DIR / file_name