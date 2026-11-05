document.addEventListener('DOMContentLoaded', async () => {
  // 1. Timer
  let seconds = 872;
  const timerElem = document.getElementById('meetingTimer');
  setInterval(() => {
    seconds++;
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    timerElem.textContent = `${m}:${s}`;
  }, 1000);

  // 2. Audio Waveform
  const canvas = document.getElementById('meetingVisualizer');
  const ctx = canvas.getContext('2d');
  let phase = 0;
  let isWaveActive = false;

  function drawWave() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!isWaveActive) {
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.moveTo(0, canvas.height / 2);
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
      return;
    }
    phase += 0.08;
    ctx.beginPath();
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#c084fc';
    ctx.shadowColor = '#c084fc';
    ctx.shadowBlur = 12;
    for (let x = 0; x < canvas.width; x += 4) {
      const y = (canvas.height / 2) + Math.sin(x * 0.03 + phase) * 18 * Math.sin(x / canvas.width * Math.PI);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
    requestAnimationFrame(drawWave);
  }
  drawWave();

  // 3. Load State
  async function refreshState() {
    try {
      const res = await fetch('/api/meeting/state');
      const data = await res.json();
      renderAgenda(data.agenda);
      renderActions(data.action_items);
    } catch(e){}
  }
  await refreshState();

  function renderAgenda(agenda) {
    const box = document.getElementById('agendaList');
    box.innerHTML = '';
    agenda.forEach(ag => {
      const div = document.createElement('div');
      div.className = `agenda-card ${ag.completed ? 'completed' : ''}`;
      div.innerHTML = `
        <input type="checkbox" ${ag.completed ? 'checked' : ''} data-id="${ag.id}">
        <div>
          <div style="font-size: 13px; font-weight: 500;">${ag.title}</div>
          <div style="font-size: 11px; color: #94a3b8;">${ag.duration_min} min</div>
        </div>
      `;
      div.querySelector('input').addEventListener('change', async (e) => {
        await fetch('/api/meeting/agenda/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agenda_id: ag.id, completed: e.target.checked })
        });
        refreshState();
      });
      box.appendChild(div);
    });
  }

  function renderActions(actions) {
    const box = document.getElementById('actionsContainer');
    box.innerHTML = '';
    actions.forEach(a => {
      const div = document.createElement('div');
      div.className = 'act-card';
      div.innerHTML = `
        <div class="act-title">${a.task}</div>
        <div class="act-meta">
          <span class="assignee-chip">👤 ${a.assignee}</span>
          <span>📅 ${a.deadline}</span>
        </div>
      `;
      box.appendChild(div);
    });
  }

  // 4. Voice Turn Handling
  let isListening = false;
  const micBtn = document.getElementById('meetingMicBtn');
  const speakerSelect = document.getElementById('meetingSpeakerSelect');

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (e) => {
      const text = e.results[0][0].transcript;
      submitTurn(text);
    };
    recognition.onend = () => {
      isListening = false;
      micBtn.classList.remove('active');
      micBtn.innerHTML = '<span>🎙️ Push to Speak</span>';
      isWaveActive = false;
      drawWave();
    };
  }

  micBtn.addEventListener('click', () => {
    if (isListening) {
      if (recognition) recognition.stop();
      isListening = false;
      micBtn.classList.remove('active');
    } else {
      if (recognition) {
        recognition.start();
        isListening = true;
        micBtn.classList.add('active');
        micBtn.innerHTML = '<span>🎙️ Listening...</span>';
        isWaveActive = true;
        drawWave();
      } else {
        const manual = prompt('Enter meeting statement:');
        if (manual) submitTurn(manual);
      }
    }
  });

  document.getElementById('simDecisionBtn').addEventListener('click', () => {
    submitTurn("We officially approve the LiveKit low latency voice architecture for production.");
  });

  document.getElementById('simActionBtn').addEventListener('click', () => {
    submitTurn("Sarah Chen is assigned to verify the multi-region failover by Friday.");
  });

  async function submitTurn(text) {
    const speaker = speakerSelect.value;
    addTurnBubble(speaker, text, "10:14 AM", false);

    isWaveActive = true;
    drawWave();

    try {
      const resp = await fetch('/api/meeting/voice-turn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, speaker: speaker, tts_provider: "elevenlabs" })
      });
      const data = await resp.json();

      addTurnBubble("Nimbus Scribe", data.reply, "10:14 AM", true, Boolean(data.decision_logged));
      await refreshState();

      if (data.audio_base64) {
        const audio = new Audio(data.audio_base64);
        audio.play().catch(() => {});
      }
    } catch(e) {
      console.error(e);
    } finally {
      isWaveActive = false;
      drawWave();
    }
  }

  function addTurnBubble(speaker, text, timestamp, isScribe, isDecision) {
    const feed = document.getElementById('transcriptFeed');
    const div = document.createElement('div');
    div.className = `turn-box ${isScribe ? 'scribe-turn' : ''} ${isDecision ? 'decision-turn' : ''}`;
    div.innerHTML = `
      <div class="turn-header">
        <span class="${isScribe ? 'scribe-tag' : 'speaker-tag'}">${speaker}</span>
        <span style="color: #64748b;">${timestamp}</span>
        ${isDecision ? '<span class="decision-badge">⚖️ DECISION</span>' : ''}
      </div>
      <div class="turn-text">${text}</div>
    `;
    feed.appendChild(div);
    feed.scrollTop = feed.scrollHeight;
  }

  // 5. Export Minutes
  document.getElementById('exportMinutesBtn').addEventListener('click', () => {
    window.location.href = '/api/meeting/export';
  });

  // 6. LiveKit WebRTC Token
  document.getElementById('livekitMeetingBtn').addEventListener('click', async () => {
    try {
      const res = await fetch('/api/meeting/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ room_name: 'executive-boardroom', participant_identity: 'alex-' + Math.random().toString(36).substring(2,6) })
      });
      const d = await res.json();
      alert(`LiveKit WebRTC Connected!\nServer: ${d.server_url}\nRoom: ${d.room_name}`);
    } catch(e){ alert('LiveKit connect error'); }
  });
});
