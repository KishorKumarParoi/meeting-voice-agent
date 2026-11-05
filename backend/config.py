import os
from pydantic import BaseModel

class Settings(BaseModel):
    ENV: str = os.getenv("ENV", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Meeting Voice Assistant")
    APP_URL: str = os.getenv("APP_URL", "https://meeting.kishor.tech")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "wss://ai-voice-receptionist-0s4kogsi.livekit.cloud")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "APIsmRLJJBVs3pE")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "EF4YK62PhnQoeBDmlbcjKlD7hfY8SGA9lDYSzxAZk8H")

    DEFAULT_ASR_PROVIDER: str = os.getenv("DEFAULT_ASR_PROVIDER", "browser")
    DEFAULT_TTS_PROVIDER: str = os.getenv("DEFAULT_TTS_PROVIDER", "elevenlabs")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4o-mini")
    DEFAULT_ENDPOINT_SILENCE_MS: int = int(os.getenv("DEFAULT_ENDPOINT_SILENCE_MS", "600"))
    ENABLE_RAG_BY_DEFAULT: bool = os.getenv("ENABLE_RAG_BY_DEFAULT", "false").lower() in ("true", "1")

    class Config:
        extra = "allow"

settings = Settings()
