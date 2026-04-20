import whisper
import tempfile
import os
import base64
from pathlib import Path

MODEL_CACHE_DIR = Path(__file__).parent.parent / "models"
MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_model_cache = {}

def get_model(model_name: str = "base"):
    if model_name not in _model_cache:
        _model_cache[model_name] = whisper.load_model(model_name, download_root=str(MODEL_CACHE_DIR))
    return _model_cache[model_name]

def transcribe_audio(audio_data: bytes, model_name: str = "base") -> str:
    model = get_model(model_name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_data)
        temp_path = f.name

    try:
        result = model.transcribe(
            temp_path,
            language="zh",
            initial_prompt="请转写这段语音，并在适当位置添加逗号，句号，问号，感叹号等标点符号。例如：今天天气很好，我们去公园吧。你好吗？我很好！"
        )
        return result["text"].strip()
    finally:
        os.unlink(temp_path)

def transcribe_base64(audio_b64: str, model_name: str = "base") -> str:
    audio_bytes = base64.b64decode(audio_b64)
    return transcribe_audio(audio_bytes, model_name)
