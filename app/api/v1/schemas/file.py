from pydantic import BaseModel
from datetime import datetime

class FileUploadResponse(BaseModel):
    file_id: int
    file_name: str
    saved_path: str
    message: str


class FileInfo(BaseModel):
    file_id: int
    file_name: str
    saved_path: str
    uploaded_at: datetime