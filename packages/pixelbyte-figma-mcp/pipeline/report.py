"""Artifact packaging helpers for deterministic pipeline runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def package_run_artifacts(
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
    """Persist artifacts in a stable directory layout and return paths."""

    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = run_dir / "snapshot.json"
    ir_path = run_dir / "design-ir.json"
    assets_path = run_dir / "asset-manifest.json"
    graph_path = run_dir / "component-graph.json"
    code_path = run_dir / "generated.tsx"
    static_gate_path = run_dir / "gate-static.json"
    visual_gate_path = run_dir / "gate-visual.json"
    summary_path = run_dir / "summary.json"

    _write_json(snapshot_path, snapshot)
    _write_json(ir_path, design_ir)
    _write_json(assets_path, asset_materialization)
    _write_json(graph_path, component_graph)
    _write_text(code_path, generation.get("code", ""))
    _write_json(static_gate_path, static_gate)
    _write_json(visual_gate_path, visual_gate)
    _write_json(summary_path, summary)

    artifacts = {
        "run_dir": str(run_dir),
        "snapshot": str(snapshot_path),
        "design_ir": str(ir_path),
        "asset_manifest": str(assets_path),
        "component_graph": str(graph_path),
        "generated_code": str(code_path),
        "static_gate": str(static_gate_path),
        "visual_gate": str(visual_gate_path),
        "summary": str(summary_path),
    }

    figma_screenshot_path = visual_gate.get("figma_screenshot_path")
    if figma_screenshot_path:
        artifacts["figma_screenshot"] = str(figma_screenshot_path)

    implementation_screenshot_path = visual_gate.get("implementation_screenshot_path")
    if implementation_screenshot_path:
        artifacts["implementation_screenshot"] = str(implementation_screenshot_path)

    return artifacts
