# Whisper API 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个基于 FastAPI 的本地 Whisper 语音转文字 API 服务

**Architecture:** 使用 FastAPI 构建 REST API，支持同步/异步转录，音频输入支持文件上传和 Base64 编码，异步任务结果存储在本地 JSON 文件

**Tech Stack:** FastAPI, Uvicorn, openai-whisper, python-multipart, aiofiles

---

## 文件结构

```
.
├── requirements.txt       # 依赖
├── index.py               # 主入口
├── whisper_api/
│   ├── __init__.py
│   ├── main.py            # FastAPI 应用
│   ├── routes.py          # API 路由
│   ├── models.py           # 数据模型
│   ├── tasks.py            # 异步任务管理
│   └── whisper.py          # Whisper 转录核心逻辑
└── tasks/                  # 异步任务存储
```

---

## Task 1: 创建 requirements.txt

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: 写入 requirements.txt**

```
fastapi>=0.100.0
uvicorn>=0.23.0
openai-whisper>=20241101
python-multipart>=0.0.6
aiofiles>=23.0.0
```

- [ ] **Step 2: 提交**

```bash
git add requirements.txt && git commit -m "chore: add requirements.txt"
```

---

## Task 2: 创建目录结构和 __init__.py

**Files:**
- Create: `whisper_api/__init__.py`
- Create: `tasks/.gitkeep`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p whisper_api tasks && touch whisper_api/__init__.py tasks/.gitkeep
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/__init__.py tasks/.gitkeep && git commit -m "chore: create project directories"
```

---

## Task 3: 创建数据模型 models.py

**Files:**
- Create: `whisper_api/models.py`

- [ ] **Step 1: 写入 models.py**

```python
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
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/models.py && git commit -m "feat: add data models"
```

---

## Task 4: 创建 Whisper 核心逻辑 whisper.py

**Files:**
- Create: `whisper_api/whisper.py`

- [ ] **Step 1: 写入 whisper.py**

```python
import whisper
import tempfile
import os
import base64

_model_cache = {}

def get_model(model_name: str = "base"):
    if model_name not in _model_cache:
        _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]

def transcribe_audio(audio_data: bytes, model_name: str = "base") -> str:
    model = get_model(model_name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_data)
        temp_path = f.name

    try:
        result = model.transcribe(temp_path, language=None)
        return result["text"].strip()
    finally:
        os.unlink(temp_path)

def transcribe_base64(audio_b64: str, model_name: str = "base") -> str:
    audio_bytes = base64.b64decode(audio_b64)
    return transcribe_audio(audio_bytes, model_name)
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/whisper.py && git commit -m "feat: add whisper transcription logic"
```

---

## Task 5: 创建异步任务管理 tasks.py

**Files:**
- Create: `whisper_api/tasks.py`

- [ ] **Step 1: 写入 tasks.py**

```python
import uuid
import json
import os
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
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/tasks.py && git commit -m "feat: add async task management"
```

---

## Task 6: 创建 API 路由 routes.py

**Files:**
- Create: `whisper_api/routes.py`

- [ ] **Step 1: 写入 routes.py**

```python
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from .models import TranscribeRequest, TranscribeResponse, AsyncTranscribeResponse, TaskResult
from .tasks import create_task, get_task, process_transcribe
from .whisper import transcribe_base64

router = APIRouter(prefix="/v1/transcribe", tags=["transcribe"])

SUPPORTED_MODELS = ["tiny", "base", "small", "medium", "large"]

@router.post("", response_model=TranscribeResponse)
async def transcribe(request: TranscribeRequest):
    if request.model and request.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Unsupported model. Choose from: {SUPPORTED_MODELS}")
    text = transcribe_base64(request.audio, request.model or "base")
    return TranscribeResponse(text=text)

@router.post("/async", response_model=AsyncTranscribeResponse)
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

@router.get("/result/{task_id}", response_model=TaskResult)
async def get_result(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResult(**task)
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/routes.py && git commit -m "feat: add API routes"
```

---

## Task 7: 创建 FastAPI 应用 main.py

**Files:**
- Create: `whisper_api/main.py`

- [ ] **Step 1: 写入 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(title="Whisper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: 提交**

```bash
git add whisper_api/main.py && git commit -m "feat: add FastAPI application"
```

---

## Task 8: 创建主入口 index.py

**Files:**
- Modify: `index.py`

- [ ] **Step 1: 覆盖 index.py**

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("whisper_api.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 2: 提交**

```bash
git add index.py && git commit -m "feat: add main entry point"
```

---

## Task 9: 安装依赖并测试

- [ ] **Step 1: 安装依赖**

```bash
pip install -r requirements.txt
```

- [ ] **Step 2: 启动服务测试**

```bash
python index.py
# 预期：服务在 localhost:8000 启动
```

- [ ] **Step 3: 测试健康检查**

```bash
curl http://localhost:8000/health
# 预期：{"status":"ok"}
```

---

## 执行方式

**1. Subagent-Driven (推荐)** - 每个 Task 由独立 subagent 执行，任务间有 review，适合大项目

**2. Inline Execution** - 在当前 session 执行，带检查点，适合快速实现

你想用哪种方式？
