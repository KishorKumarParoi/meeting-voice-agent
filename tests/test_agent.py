def test_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_system_status(client):
    r = client.get("/api/system-status")
    assert r.status_code == 200
    assert r.json()["status"] == "online"

def test_livekit_token(client):
    r = client.post("/api/voice/token", json={"room_name": "test-room", "participant_identity": "tester"})
    assert r.status_code == 200
    assert "token" in r.json()

def test_voice_turn(client):
    r = client.post("/api/voice/process", json={"text": "Extract the action items from our discussion so far.", "tts_provider": "browser"})
    assert r.status_code == 200
    assert len(r.json()["reply"]) > 0
    assert r.json()["latency"]["total_ms"] > 0
