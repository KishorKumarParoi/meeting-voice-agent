from fastapi import APIRouter, Response
from pydantic import BaseModel
from typing import Dict, Any
from backend.models import MeetingVoiceRequest, MeetingVoiceResponse, MeetingState
from backend.scribe_engine import scribe_engine
from backend.core.tts import generate_speech
from backend.core.livekit import generate_livekit_token
from backend.config import settings

router = APIRouter(prefix="/api/meeting", tags=["Meeting Scribe"])

class AgendaToggleRequest(BaseModel):
    agenda_id: str
    completed: bool

class ActionStatusRequest(BaseModel):
    action_id: str
    status: str # todo, in_progress, done

class TokenRequest(BaseModel):
    room_name: str
    participant_identity: str

@router.get("/state", response_model=MeetingState)
async def get_meeting_state():
    return scribe_engine.state

@router.post("/voice-turn", response_model=MeetingVoiceResponse)
async def handle_voice_turn(req: MeetingVoiceRequest):
    text = req.text or "We agree to approve the architecture."
    reply, turn, new_actions, decision, latency = await scribe_engine.process_turn(
        text=text,
        speaker_name=req.speaker,
        tts_provider=req.tts_provider
    )

    audio_base64, tts_ms = await generate_speech(reply, provider=req.tts_provider)
    if tts_ms > 0:
        latency.tts_ttfb_ms = tts_ms
        latency.total_ms = round(latency.asr_ms + latency.llm_ttft_ms + latency.tts_ttfb_ms, 2)

    return MeetingVoiceResponse(
        reply=reply,
        speaker_turn=turn,
        action_items_added=new_actions,
        decision_logged=decision,
        audio_base64=audio_base64,
        latency=latency
    )

@router.post("/agenda/toggle")
async def toggle_agenda(req: AgendaToggleRequest):
    for ag in scribe_engine.state.agenda:
        if ag.id == req.agenda_id:
            ag.completed = req.completed
            return {"status": "updated", "agenda": ag}
    return {"status": "not_found"}

@router.post("/action-item/status")
async def update_action_status(req: ActionStatusRequest):
    for act in scribe_engine.state.action_items:
        if act.id == req.action_id:
            act.status = req.status
            return {"status": "updated", "action_item": act}
    return {"status": "not_found"}

@router.get("/export")
async def export_minutes():
    md = scribe_engine.generate_minutes_markdown()
    return Response(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=meeting-minutes.md"}
    )

@router.post("/token")
async def get_livekit_token(req: TokenRequest):
    tok = generate_livekit_token(req.room_name, req.participant_identity)
    return {
        "server_url": settings.LIVEKIT_URL,
        "token": tok,
        "room_name": req.room_name,
        "participant_identity": req.participant_identity
    }
