from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LatencyBreakdown(BaseModel):
    asr_ms: float = 0.0
    llm_ttft_ms: float = 0.0
    tts_ttfb_ms: float = 0.0
    total_ms: float = 0.0

class AgendaItem(BaseModel):
    id: str
    title: str
    completed: bool = False
    duration_min: int = 15

class ActionItem(BaseModel):
    id: str
    task: str
    assignee: str
    deadline: str
    priority: str = "High" # High, Medium, Low
    status: str = "todo" # todo, in_progress, done

class SpeakerTurn(BaseModel):
    speaker: str
    role: str
    text: str
    timestamp: str
    is_decision: bool = False

class MeetingState(BaseModel):
    meeting_title: str
    meeting_id: str
    start_time: str
    agenda: List[AgendaItem]
    speakers: List[Dict[str, str]]
    turns: List[SpeakerTurn]
    action_items: List[ActionItem]
    decisions: List[str]

class MeetingVoiceRequest(BaseModel):
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    speaker: str = "Alex Mercer (Tech Lead)"
    tts_provider: str = "elevenlabs"

class MeetingVoiceResponse(BaseModel):
    reply: str
    speaker_turn: SpeakerTurn
    action_items_added: List[ActionItem] = Field(default_factory=list)
    decision_logged: Optional[str] = None
    audio_base64: Optional[str] = None
    latency: LatencyBreakdown
