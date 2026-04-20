import uuid
import json
import asyncio
from pathlib import Path
from typing import Optional

TASKS_DIR = Path("tasks")
TASKS_DIR.mkdir(exist_ok=True)

def create_task() -> str:
    task_id = str(uuid.uuid4())
    task_path = TASKS_DIR / f"{task_id}.json"
    task_data = {"task_id": task_id, "status": "processing"}
    task_path.write_text(json.dumps(task_data))
    return task_id

def get_task(task_id: str) -> Optional[dict]:
    task_path = TASKS_DIR / f"{task_id}.json"
    if not task_path.exists():
        return None
    return json.loads(task_path.read_text())

def update_task(task_id: str, status: str, result: dict = None, error: str = None):
    task_path = TASKS_DIR / f"{task_id}.json"
    task_data = {"task_id": task_id, "status": status}
    if result is not None:
        task_data["result"] = result
    if error is not None:
        task_data["error"] = error
    task_path.write_text(json.dumps(task_data))

async def process_transcribe(task_id: str, audio_data: bytes, model_name: str):
    from .whisper import transcribe_audio

    try:
        text = transcribe_audio(audio_data, model_name)
        update_task(task_id, "completed", result={"text": text})
    except Exception as e:
        update_task(task_id, "failed", error=str(e))
