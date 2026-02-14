"""Stage timing and quality metrics helpers."""

from __future__ import annotations

import time
from typing import Any, Dict


class StageMetrics:
    """Collects per-stage durations and run-level quality metrics."""

    def __init__(self) -> None:
        self.stage_timings: Dict[str, float] = {}
        self.quality_metrics: Dict[str, Any] = {}

    async def timed(self, stage_name: str, coro):
        start = time.perf_counter()
        result = await coro
        elapsed = time.perf_counter() - start
        self.stage_timings[stage_name] = round(elapsed, 3)
        return result

    def set_quality(self, metrics: Dict[str, Any]) -> None:
        self.quality_metrics.update(metrics)
