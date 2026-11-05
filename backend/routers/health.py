from fastapi import APIRouter
from backend.config import settings

router = APIRouter(tags=["Health"])

@router.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "env": settings.ENV}

@router.get("/api/system-status")
async def system_status():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "app_url": settings.APP_URL,
        "providers": {
            "openai_connected": bool(settings.OPENAI_API_KEY),
            "elevenlabs_connected": bool(settings.ELEVENLABS_API_KEY),
            "livekit_connected": bool(settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY and settings.LIVEKIT_API_SECRET)
        },
        "livekit_url": settings.LIVEKIT_URL
    }
