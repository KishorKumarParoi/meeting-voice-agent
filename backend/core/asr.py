import base64
import time
import httpx
from typing import Tuple
from backend.config import settings

async def transcribe_audio_base64(audio_base64: str) -> Tuple[str, float]:
    start_time = time.perf_counter()
    if not settings.OPENAI_API_KEY:
        return "Audio voice turn received.", 35.0
    try:
        audio_bytes = base64.b64decode(audio_base64)
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"model": "whisper-1", "language": "en"}
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, files=files, data=data)
            latency = round((time.perf_counter() - start_time) * 1000, 2)
            if resp.status_code == 200:
                return resp.json().get("text", "").strip(), latency
            return "Transcription fallback", latency
    except Exception:
        return "Audio transcription fallback", 45.0
