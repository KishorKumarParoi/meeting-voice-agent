import time
from fastapi import APIRouter
from backend.models import VoiceProcessRequest, VoiceProcessResponse, LiveKitTokenRequest, LiveKitTokenResponse, LatencyMetrics
from backend.agent import agent_instance
from backend.core.asr import transcribe_audio_base64
from backend.core.tts import generate_speech
from backend.core.livekit import generate_livekit_token
from backend.config import settings

router = APIRouter(prefix="/api/voice", tags=["Voice"])

@router.post("/process", response_model=VoiceProcessResponse)
async def process_voice(request: VoiceProcessRequest):
    t0 = time.perf_counter()
    transcript = request.text or ""
    asr_ms = 45.0
    if request.audio_base64 and not transcript:
        transcript, asr_ms = await transcribe_audio_base64(request.audio_base64)
    elif not transcript:
        transcript = "Voice request initialized."

    reply, tools, actions, llm_ttft_ms, rag_chunks = await agent_instance.run_turn(
        user_message=transcript,
        conversation_history=request.messages,
        custom_system_prompt=request.system_prompt,
        use_rag=request.use_rag,
        response_length=request.response_length
    )

    audio_base64, tts_ttfb_ms = await generate_speech(reply, provider=request.tts_provider or settings.DEFAULT_TTS_PROVIDER)
    total_ms = max(round((time.perf_counter() - t0) * 1000, 2), round(asr_ms + llm_ttft_ms + tts_ttfb_ms, 2))

    return VoiceProcessResponse(
        transcript=transcript,
        reply=reply,
        audio_base64=audio_base64,
        latency=LatencyMetrics(asr_ms=asr_ms, llm_ttft_ms=llm_ttft_ms, tts_ttfb_ms=tts_ttfb_ms, total_ms=total_ms, mode="streaming" if request.streaming else "batch"),
        tools_executed=tools,
        action_items=actions,
        rag_used=request.use_rag,
        rag_chunks=rag_chunks
    )

@router.post("/token", response_model=LiveKitTokenResponse)
async def get_token(request: LiveKitTokenRequest):
    tok = generate_livekit_token(request.room_name, request.participant_identity, request.participant_name)
    return LiveKitTokenResponse(server_url=settings.LIVEKIT_URL, token=tok, room_name=request.room_name, participant_identity=request.participant_identity)
