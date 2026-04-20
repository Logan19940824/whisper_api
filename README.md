# Whisper API

基于 OpenAI Whisper 的本地语音转文字 API 服务。

## 快速启动

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 启动服务

```bash
python3 index.py
```

服务启动后运行在 `http://localhost:8000`

## API 接口

### 健康检查

```bash
curl http://localhost:8000/health
```

### 同步转录（Base64）

```bash
curl -X POST http://localhost:8000/v1/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio": "<base64音频数据>", "model": "base"}'
```

### 异步转录（文件上传）

```bash
curl -X POST http://localhost:8000/v1/transcribe/async \
  -F "file=@audio.mp3" \
  -F "model=base"
```

### 异步转录（Base64）

```bash
curl -X POST http://localhost:8000/v1/transcribe/async \
  -F "audio=<base64音频数据>" \
  -F "model=base"
```

### 查询异步任务结果

```bash
curl http://localhost:8000/v1/transcribe/result/<task_id>
```

## 模型选择

可选模型：`tiny` / `base` / `small` / `medium` / `large`

首次使用会下载模型到 `models/` 目录。

## 异步任务存储

异步任务结果存储在 `tasks/` 目录（JSON 文件）。
