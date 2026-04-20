from pydantic import BaseModel
from typing import Optional, Literal

class TranscribeRequest(BaseModel):
    audio: str
    model: Optional[Literal["tiny", "base", "small", "medium", "large"]] = "base"

class TranscribeResponse(BaseModel):
    text: str

class AsyncTranscribeResponse(BaseModel):
    task_id: str
    status: str

class TaskResult(BaseModel):
    task_id: str
    status: Literal["processing", "completed", "failed"]
    result: Optional[dict] = None
    error: Optional[str] = None
