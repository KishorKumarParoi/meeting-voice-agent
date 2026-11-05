import time
import json
import base64
import hmac
import hashlib
from typing import Optional, Dict, Any
from backend.config import settings

def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def generate_livekit_token(
    room_name: str,
    participant_identity: str,
    participant_name: Optional[str] = None,
    ttl_seconds: int = 86400
) -> str:
    api_key = settings.LIVEKIT_API_KEY
    api_secret = settings.LIVEKIT_API_SECRET

    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": api_key,
        "sub": participant_identity,
        "name": participant_name or participant_identity,
        "nbf": now - 10,
        "exp": now + ttl_seconds,
        "video": {
            "room": room_name,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True,
            "canPublishData": True
        }
    }
    encoded_header = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(api_secret.encode("utf-8"), f"{encoded_header}.{encoded_payload}".encode("utf-8"), hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_base64url_encode(signature)}"
