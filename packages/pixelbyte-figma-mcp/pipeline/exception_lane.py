"""Exception-lane fallback for failed pipeline runs."""

from __future__ import annotations

from typing import Dict, List

from pipeline.models import GateResult, PipelineStatus


async def run_exception_lane(
    current_status: PipelineStatus,
    gates: List[GateResult],
    max_iterations: int = 2,
    attempted_iterations: int = 0,
) -> Dict[str, object]:
    """Run constrained fallback attempts for failed runs.

    This implementation preserves determinism by not editing generated code inside
    the exception lane yet. It records fallback attempts and exits with FAIL when
    unresolved issues remain.
    """

    if current_status != PipelineStatus.FAIL:
        return {
            "status": current_status,
            "iterations": 0,
            "fallback_count": 0,
            "errors": [],
            "resolved": True,
        }

    failing_gates = [g for g in gates if g.status.value == "FAIL"]
    if not failing_gates:
        return {
            "status": PipelineStatus.FAIL,
            "iterations": 0,
            "fallback_count": 0,
            "errors": ["Pipeline entered exception lane without failing gates."],
            "resolved": False,
        }

    iterations = attempted_iterations if attempted_iterations > 0 else min(max_iterations, 2)
    errors = ["Exception lane exhausted before reaching a passing gate state."]
    for gate in failing_gates:
        errors.append(f"Unresolved gate: {gate.gate_name}")

    return {
        "status": PipelineStatus.FAIL,
        "iterations": iterations,
        "fallback_count": iterations,
        "errors": errors,
        "resolved": False,
    }
