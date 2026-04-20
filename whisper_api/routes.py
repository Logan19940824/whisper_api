import base64
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, Depends
from typing import Optional

from .models import TranscribeRequest, TranscribeResponse, AsyncTranscribeResponse, TaskResult
from .tasks import create_task, get_task, process_transcribe
from .whisper import transcribe_audio

router = APIRouter(prefix="/v1/transcribe", tags=["transcribe"])

SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large"]

# 固定的 API tokens (32位)
VALID_TOKENS = [
    "sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3",
    "sk_wh1sper_n1o2p3q4r5s6t7u8v9w0x1y2z3a4",
    "sk_wh1sper_b1c2d3e4f5g6h7i8j9k0l1m2n3o4"
]

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    token = authorization[7:]  # 去掉 "Bearer " 前缀
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid API token")

@router.post("", response_model=TranscribeResponse, dependencies=[Depends(verify_token)])
async def transcribe(
    file: UploadFile = File(None),
    audio: Optional[str] = Form(None),
    model: Optional[str] = Form("base")
):
    if file and audio:
        raise HTTPException(status_code=400, detail="Provide either file or audio, not both")

    if not file and not audio:
        raise HTTPException(status_code=400, detail="Provide either file or audio")

    if model and model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported model. Choose from: {SUPPORTED_MODELS}")

    if file:
        audio_data = await file.read()
    else:
        audio_data = base64.b64decode(audio)

    text = transcribe_audio(audio_data, model or "base")
    return TranscribeResponse(text=text)

@router.post("/async", response_model=AsyncTranscribeResponse, dependencies=[Depends(verify_token)])
async def transcribe_async(
    file: Optional[UploadFile] = File(None),
    audio: Optional[str] = Form(None),
    model: Optional[str] = Form("base")
):
    if file and audio:
        raise HTTPException(status_code=400, detail="Provide either file or audio, not both")

    if not file and not audio:
        raise HTTPException(status_code=400, detail="Provide either file or audio")

    if model and model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported model. Choose from: {SUPPORTED_MODELS}")

    task_id = create_task()

    if file:
        audio_data = await file.read()
        model_name = model or "base"
    else:
        audio_data = base64.b64decode(audio)
        model_name = model or "base"

    asyncio.create_task(process_transcribe(task_id, audio_data, model_name))

    return AsyncTranscribeResponse(task_id=task_id, status="processing")

@router.get("/result/{task_id}", response_model=TaskResult, dependencies=[Depends(verify_token)])
async def get_result(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResult(**task)
