import time
from backend.models import LatencyMetrics

class LatencyTracker:
    def __init__(self, mode: str = "streaming"):
        self.mode = mode
        self.start_time = time.perf_counter()

    def calculate(self, asr_ms: float, llm_ttft_ms: float, tts_ttfb_ms: float) -> LatencyMetrics:
        total = round((time.perf_counter() - self.start_time) * 1000, 2)
        calc_total = round(asr_ms + llm_ttft_ms + tts_ttfb_ms, 2)
        return LatencyMetrics(
            asr_ms=asr_ms,
            llm_ttft_ms=llm_ttft_ms,
            tts_ttfb_ms=tts_ttfb_ms,
            total_ms=max(total, calc_total),
            mode=self.mode
        )
