def test_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_meeting_state(client):
    r = client.get("/api/meeting/state")
    assert r.status_code == 200
    data = r.json()
    assert "agenda" in data
    assert "action_items" in data
    assert len(data["speakers"]) >= 3

def test_meeting_voice_turn_action(client):
    r = client.post("/api/meeting/voice-turn", json={
        "text": "Assign Sarah Chen to verify multi-region failover by Friday.",
        "speaker": "Alex Mercer",
        "tts_provider": "browser"
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data["reply"]) > 0
    assert len(data["action_items_added"]) > 0
    assert data["action_items_added"][0]["assignee"] == "Sarah Chen"

def test_meeting_export_minutes(client):
    r = client.get("/api/meeting/export")
    assert r.status_code == 200
    assert "Executive Meeting Minutes" in r.text
