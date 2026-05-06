from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    file_id: str


class TimestampData(BaseModel):
    start: float
    end: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    timestamps: list[TimestampData] = []


class SummarizeRequest(BaseModel):
    file_id: str


class SummarizeResponse(BaseModel):
    summary: str
