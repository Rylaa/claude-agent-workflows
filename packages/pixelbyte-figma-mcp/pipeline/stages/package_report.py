"""Report packaging stage wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from pipeline.report import package_run_artifacts


def run(
    output_root: Path,
    run_id: str,
    snapshot: Dict[str, Any],
    design_ir: Dict[str, Any],
    asset_materialization: Dict[str, Any],
    component_graph: Dict[str, Any],
    generation: Dict[str, Any],
    static_gate: Dict[str, Any],
    visual_gate: Dict[str, Any],
    summary: Dict[str, Any],
) -> Dict[str, str]:
    """Persist deterministic run artifacts and return artifact paths."""

    return package_run_artifacts(
        output_root=output_root,
        run_id=run_id,
        snapshot=snapshot,
        design_ir=design_ir,
        asset_materialization=asset_materialization,
        component_graph=component_graph,
        generation=generation,
        static_gate=static_gate,
        visual_gate=visual_gate,
        summary=summary,
    )
