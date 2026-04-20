# Whisper 语音转文字 API 服务设计

## 概述

基于 OpenAI Whisper 的本地开发服务器，提供音频转文字功能。

## 技术栈

- **框架**：FastAPI + Uvicorn
- **地址**：`http://localhost:8000`

## API 接口

### 1. 同步转录 `POST /v1/transcribe`

**请求 (文件上传)：**
```
Content-Type: multipart/form-data
file: <audio file>
model: <optional, default "base">
```

**请求 (Base64)：**
```json
{
  "audio": "<base64 encoded audio>",
  "model": "<optional, default base>"
}
```

**响应：**
```json
{
  "text": "转录文本内容"
}
```

### 2. 异步转录 `POST /v1/transcribe/async`

请求格式同同步接口。

**响应：**
```json
{
  "task_id": "uuid-string",
  "status": "processing"
}
```

### 3. 查询异步结果 `GET /v1/transcribe/result/{task_id}`

**响应 (进行中)：**
```json
{
  "task_id": "uuid-string",
  "status": "processing"
}
```

**响应 (完成)：**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "result": {
    "text": "转录文本内容"
  }
}
```

**响应 (失败)：**
```json
{
  "task_id": "uuid-string",
  "status": "failed",
  "error": "错误信息"
}
```

## 模型选择

支持模型：`tiny` / `base` / `small` / `medium` / `large`
默认值：`base`

## 异步任务存储

- 目录：`tasks/`
- 文件命名：`{task_id}.json`
- 文件格式：
```json
{
  "task_id": "uuid",
  "status": "processing|completed|failed",
  "result": {},
  "error": ""
}
```

## 音频格式支持

Whisper 原生支持：mp3, mp4, wav, flac, ogg, webm 等

## 目录结构

```
.
├── index.py          # 主入口
├── whisper_api/      # 核心模块
│   ├── __init__.py
│   ├── main.py       # FastAPI 应用
│   ├── routes.py     # API 路由
│   ├── models.py     # 数据模型
│   └── tasks.py      # 异步任务管理
├── tasks/            # 异步任务存储
└── requirements.txt  # 依赖
```
