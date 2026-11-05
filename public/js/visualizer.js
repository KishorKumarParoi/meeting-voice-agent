class AudioWaveVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.animationId = null;
    this.isActive = false;
    this.phase = 0;
    this.color = "#8b5cf6";
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.drawIdle();
  }
  resize() {
    if (!this.canvas) return;
    this.canvas.width = this.canvas.offsetWidth * window.devicePixelRatio || 600;
    this.canvas.height = this.canvas.offsetHeight * window.devicePixelRatio || 110;
  }
  start(color = "#8b5cf6") {
    this.color = color;
    this.isActive = true;
    this.animate();
  }
  stop() {
    this.isActive = false;
    if (this.animationId) cancelAnimationFrame(this.animationId);
    this.drawIdle();
  }
  drawIdle() {
    if (!this.ctx) return;
    const w = this.canvas.width, h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);
    this.ctx.beginPath();
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    this.ctx.lineWidth = 2;
    this.ctx.moveTo(0, h / 2);
    this.ctx.lineTo(w, h / 2);
    this.ctx.stroke();
  }
  animate() {
    if (!this.isActive) return;
    const w = this.canvas.width, h = this.canvas.height;
    this.ctx.clearRect(0, 0, w, h);
    this.phase += 0.08;
    this.ctx.beginPath();
    this.ctx.lineWidth = 3;
    this.ctx.strokeStyle = this.color;
    this.ctx.shadowColor = this.color;
    this.ctx.shadowBlur = 10;
    for (let x = 0; x < w; x += 4) {
      const y = (h / 2) + Math.sin(x * 0.02 + this.phase) * 22 * Math.sin(x / w * Math.PI);
      if (x === 0) this.ctx.moveTo(x, y);
      else this.ctx.lineTo(x, y);
    }
    this.ctx.stroke();
    this.animationId = requestAnimationFrame(() => this.animate());
  }
}
