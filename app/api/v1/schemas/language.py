from pydantic import BaseModel

class LanguageUpdateRequest(BaseModel):
    language: str