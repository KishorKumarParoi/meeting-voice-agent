document.addEventListener('DOMContentLoaded', () => {
  const viz = new AudioWaveVisualizer('visualizerCanvas');
  const engine = new VoiceEngine({
    visualizer: viz,
    onStatus: (st) => {
      const b = document.getElementById('micBtn');
      const l = document.getElementById('statusLabel');
      if (st === 'listening') { b.classList.add('recording'); b.innerHTML = '<span>🎙️ Listening...</span>'; l.textContent = 'Listening (Speak now)'; }
      else if (st === 'thinking') { b.classList.remove('recording'); b.innerHTML = '<span>⏳ Reasoning...</span>'; l.textContent = 'LLM Reasoning...'; }
      else if (st === 'speaking') { b.classList.remove('recording'); b.innerHTML = '<span>🔊 Speaking...</span>'; l.textContent = 'Audio Streaming...'; }
      else { b.classList.remove('recording'); b.innerHTML = '<span>🎙️ Push to Talk</span>'; l.textContent = 'Ready for Voice Input'; }
    },
    onTranscript: (t) => addMsg('user', t),
    onReply: (r) => addMsg('agent', r),
    onLatency: (lat) => {
      document.getElementById('asrVal').textContent = lat.asr_ms + ' ms';
      document.getElementById('llmVal').textContent = lat.llm_ttft_ms + ' ms';
      document.getElementById('ttsVal').textContent = lat.tts_ttfb_ms + ' ms';
      document.getElementById('totalVal').textContent = lat.total_ms + ' ms';
    },
    onTool: (tool) => addAct(`⚡ Tool: ${tool.tool_name} (${tool.latency_ms}ms)`)
  });

  document.getElementById('micBtn').addEventListener('click', () => engine.toggle());
  document.getElementById('interruptBtn').addEventListener('click', () => { engine.bargeIn(); addAct('⚠️ Interrupted (Barge-in)'); });
  document.getElementById('quickQueryBtn').addEventListener('click', () => {
    const q = "Extract the action items from our discussion so far.";
    addMsg('user', q);
    engine.sendTurn(q);
  });
  document.getElementById('ragSel').addEventListener('change', (e) => engine.useRag = e.target.value === 'rag');
  document.getElementById('streamSel').addEventListener('change', (e) => engine.streaming = e.target.value === 'streaming');
  document.getElementById('ttsSel').addEventListener('change', (e) => engine.ttsProvider = e.target.value);

  document.getElementById('livekitBtn').addEventListener('click', async () => {
    try {
      const r = await fetch('/api/voice/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_name: 'meeting-voice-agent-room', participant_identity: 'user-' + Math.random().toString(36).substring(2,6) })
      });
      const d = await r.json();
      alert(`LiveKit Connected!\nServer: ${d.server_url}\nRoom: ${d.room_name}`);
      addAct(`🟢 LiveKit Room Joined: ${d.room_name}`);
    } catch(e) { alert('LiveKit token error'); }
  });

  function addMsg(role, txt) {
    const box = document.getElementById('msgList');
    const b = document.createElement('div');
    b.className = 'msg-bubble ' + (role === 'user' ? 'msg-user' : 'msg-agent');
    b.textContent = txt;
    box.appendChild(b);
    box.scrollTop = box.scrollHeight;
  }
  function addAct(txt) {
    const box = document.getElementById('actionList');
    const a = document.createElement('div');
    a.className = 'action-card';
    a.textContent = txt;
    box.prepend(a);
  }
});
