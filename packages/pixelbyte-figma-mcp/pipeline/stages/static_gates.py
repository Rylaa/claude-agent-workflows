"""Static gate checks for deterministic pipeline outputs."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from pipeline.models import GateResult, GateStatus


def _status_from_score(score: float, pass_threshold: float, warn_threshold: float) -> GateStatus:
    if score >= pass_threshold:
        return GateStatus.PASS
    if score >= warn_threshold:
        return GateStatus.WARN
    return GateStatus.FAIL


def run(
    generated_code: str,
    asset_manifest: List[Dict[str, Any]],
    pass_threshold: float,
    warn_threshold: float,
) -> GateResult:
    """Run deterministic static checks against generated source."""

    checks: List[Dict[str, Any]] = []

    checks.append(
        {
            "name": "no_image_ref_placeholders",
            "passed": "imageRef:" not in generated_code,
            "critical": True,
            "message": "Generated code still contains imageRef placeholders.",
        }
    )

    checks.append(
        {
            "name": "no_figma_signed_urls",
            "passed": "s3-alpha-sig.figma.com" not in generated_code,
            "critical": True,
            "message": "Generated code leaks temporary signed Figma URLs.",
        }
    )

    expected_paths = [item.get("logical_path", "") for item in asset_manifest if item.get("logical_path")]
    missing_paths = [path for path in expected_paths if path not in generated_code]
    checks.append(
        {
            "name": "materialized_asset_paths_used",
            "passed": len(missing_paths) == 0,
            "critical": True,
            "message": "Not all materialized asset paths are referenced in generated code.",
        }
    )

    class_name_assigned = bool(re.search(r"className\s*=\s*''", generated_code))
    class_name_used = "{className}" in generated_code
    checks.append(
        {
            "name": "class_name_prop_used",
            "passed": (not class_name_assigned) or class_name_used,
            "critical": False,
            "message": "Component className prop is declared but not used.",
        }
    )

    passed_count = sum(1 for check in checks if check["passed"])
    score = (passed_count / len(checks)) * 100 if checks else 100.0

    critical_failed = [check for check in checks if check["critical"] and not check["passed"]]
    if critical_failed:
        status = GateStatus.FAIL
    else:
        non_critical_failed = [check for check in checks if (not check["critical"]) and not check["passed"]]
        if non_critical_failed:
            status = GateStatus.WARN
        else:
            status = _status_from_score(score, pass_threshold, warn_threshold)

    issues = [check["message"] for check in checks if not check["passed"]]

    return GateResult(
        gate_name="static",
        status=status,
        score=round(score, 2),
        threshold=pass_threshold,
        evidence_paths=[],
        issues=issues,
    )
