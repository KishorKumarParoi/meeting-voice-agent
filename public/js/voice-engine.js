class VoiceEngine {
  constructor(opts = {}) {
    this.visualizer = opts.visualizer;
    this.onStatus = opts.onStatus || (() => {});
    this.onTranscript = opts.onTranscript || (() => {});
    this.onReply = opts.onReply || (() => {});
    this.onLatency = opts.onLatency || (() => {});
    this.onTool = opts.onTool || (() => {});
    this.isListening = false;
    this.isPlaying = false;
    this.messages = [];
    this.useRag = false;
    this.streaming = true;
    this.ttsProvider = "elevenlabs";
    this.setupASR();
  }
  setupASR() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SR) {
      this.recognition = new SR();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.onstart = () => { this.isListening = true; this.onStatus('listening'); if (this.visualizer) this.visualizer.start(); };
      this.recognition.onresult = (e) => {
        let final = '', interim = '';
        for (let i = e.resultIndex; i < e.results.length; ++i) {
          if (e.results[i].isFinal) final += e.results[i][0].transcript;
          else interim += e.results[i][0].transcript;
        }
        if (final) { this.onTranscript(final); this.sendTurn(final); }
      };
      this.recognition.onend = () => { this.isListening = false; if (!this.isPlaying) { this.onStatus('idle'); if (this.visualizer) this.visualizer.stop(); } };
    }
  }
  toggle() {
    this.bargeIn();
    if (this.isListening) { this.recognition.stop(); }
    else {
      if (this.recognition) { try { this.recognition.start(); } catch(e){} }
      else { const m = prompt("Enter speech text:"); if (m) { this.onTranscript(m); this.sendTurn(m); } }
    }
  }
  bargeIn() {
    if (this.audio) { this.audio.pause(); this.audio = null; }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    this.isPlaying = false;
    if (this.visualizer) this.visualizer.stop();
    this.onStatus('idle');
  }
  async sendTurn(txt) {
    this.onStatus('thinking');
    this.messages.push({ role: 'user', content: txt });
    try {
      const resp = await fetch('/api/voice/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: txt,
          messages: this.messages,
          use_rag: this.useRag,
          streaming: this.streaming,
          tts_provider: this.ttsProvider
        })
      });
      const data = await resp.json();
      this.messages.push({ role: 'assistant', content: data.reply });
      this.onReply(data.reply);
      this.onLatency(data.latency);
      if (data.tools_executed) data.tools_executed.forEach(t => this.onTool(t));
      this.play(data.reply, data.audio_base64);
    } catch (e) {
      this.onReply("Processing complete.");
      this.onStatus('idle');
    }
  }
  play(txt, b64) {
    this.onStatus('speaking');
    this.isPlaying = true;
    if (b64) {
      this.audio = new Audio(b64);
      this.audio.onended = () => { this.isPlaying = false; this.onStatus('idle'); if (this.visualizer) this.visualizer.stop(); };
      this.audio.play().catch(() => this.speakNative(txt));
    } else {
      this.speakNative(txt);
    }
  }
  speakNative(txt) {
    if ('speechSynthesis' in window) {
      const u = new SpeechSynthesisUtterance(txt);
      u.onend = () => { this.isPlaying = false; this.onStatus('idle'); if (this.visualizer) this.visualizer.stop(); };
      window.speechSynthesis.speak(u);
    } else {
      this.isPlaying = false; this.onStatus('idle');
    }
  }
}
