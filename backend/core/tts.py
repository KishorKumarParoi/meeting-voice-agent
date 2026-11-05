import time
import base64
import httpx
from typing import Optional, Tuple
from backend.config import settings

async def generate_speech(text: str, provider: str = "elevenlabs") -> Tuple[Optional[str], float]:
    start_time = time.perf_counter()
    if provider == "browser":
        return None, 15.0

    if provider == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    b64 = base64.b64encode(resp.content).decode("utf-8")
                    return f"data:audio/mp3;base64,{b64}", round((time.perf_counter() - start_time) * 1000, 2)
        except Exception:
            pass

    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"},
                    json={"model": "tts-1", "voice": "alloy", "input": text[:350]}
                )
                if resp.status_code == 200:
                    b64 = base64.b64encode(resp.content).decode("utf-8")
                    return f"data:audio/mp3;base64,{b64}", round((time.perf_counter() - start_time) * 1000, 2)
        except Exception:
            pass

    return None, 20.0
