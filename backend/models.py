from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class LatencyMetrics(BaseModel):
    asr_ms: float = 0.0
    llm_ttft_ms: float = 0.0
    tts_ttfb_ms: float = 0.0
    total_ms: float = 0.0
    mode: str = "streaming"

class ToolExecutionResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    latency_ms: float = 0.0

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class VoiceProcessRequest(BaseModel):
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    system_prompt: Optional[str] = None
    use_rag: bool = False
    streaming: bool = True
    tts_provider: Optional[str] = "elevenlabs"
    response_length: str = "medium"
    endpoint_silence_ms: int = 600

class VoiceProcessResponse(BaseModel):
    transcript: str
    reply: str
    audio_base64: Optional[str] = None
    latency: LatencyMetrics
    tools_executed: List[ToolExecutionResult] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    rag_used: bool = False
    rag_chunks: List[str] = Field(default_factory=list)

class LiveKitTokenRequest(BaseModel):
    room_name: str
    participant_identity: str
    participant_name: Optional[str] = None

class LiveKitTokenResponse(BaseModel):
    server_url: str
    token: str
    room_name: str
    participant_identity: str
