# Whisper API

基于 OpenAI Whisper 的本地语音转文字 API 服务。

## 环境配置

### 使用 venv（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 使用 conda

```bash
# 创建 conda 环境（Python 3.9）
conda create -n whisper_api python=3.9

# 激活环境
conda activate whisper_api

# 安装 PyTorch CUDA 版本（先卸载 CPU 版本）
pip uninstall torch torchaudio -y
pip install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu121

# 安装其他依赖
pip install -r requirements.txt
```

### 国内镜像加速

如遇安装慢，可使用国内镜像：

```bash
# 清华镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里云镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
```

**永久配置**：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

## 快速启动

### 2. 启动服务

```bash
python3 index.py
```

服务启动后运行在 `http://localhost:8000`

## API 接口

### 健康检查（无需认证）

```bash
curl http://localhost:8000/health
```

**注意**：除健康检查外，所有接口都需要在 Header 中携带 `Authorization: Bearer <token>`

可用 token：
- `sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3`
- `sk_wh1sper_n1o2p3q4r5s6t7u8v9w0x1y2z3a4`
- `sk_wh1sper_b1c2d3e4f5g6h7i8j9k0l1m2n3o4`

### 同步转录（Base64）

```bash
curl -X POST http://localhost:8000/v1/transcribe \
  -H "Authorization: Bearer sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3" \
  -H "Content-Type: application/json" \
  -d '{"audio": "<base64音频数据>", "model": "base"}'
```

### 异步转录（文件上传）

```bash
curl -X POST http://localhost:8000/v1/transcribe/async \
  -H "Authorization: Bearer sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3" \
  -F "file=@audio.mp3" \
  -F "model=base"
```

### 异步转录（Base64）

```bash
curl -X POST http://localhost:8000/v1/transcribe/async \
  -H "Authorization: Bearer sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3" \
  -F "audio=<base64音频数据>" \
  -F "model=base"
```

### 查询异步任务结果

```bash
curl http://localhost:8000/v1/transcribe/result/<task_id> \
  -H "Authorization: Bearer sk_wh1sper_a1b2c3d4e5f6g7h8i9j0k1l2m3"
```

## 模型选择

可选模型：`tiny` / `base` / `small` / `medium` / `large`

首次使用会下载模型到 `models/` 目录。

## 异步任务存储

异步任务结果存储在 `tasks/` 目录（JSON 文件）。
