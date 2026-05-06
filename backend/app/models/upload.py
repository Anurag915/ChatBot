from pydantic import BaseModel


class ExtractedTextResponse(BaseModel):
    text: str
    chunks: list[dict]
    segments: list[dict] | None = None


class UploadResponse(BaseModel):
    file_id: str
    file_name: str
    file_type: str
    extraction: ExtractedTextResponse
