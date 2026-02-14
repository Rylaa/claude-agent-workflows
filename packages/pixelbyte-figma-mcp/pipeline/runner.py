"""Deterministic pipeline runner."""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from pipeline.cache import StageCache
from pipeline.exception_lane import run_exception_lane
from pipeline.metrics import StageMetrics
from pipeline.models import GateResult, GateStatus, PipelineRunRequest, PipelineRunResult, PipelineStatus
from pipeline.stages import (
    build_component_dag,
    fetch_snapshot,
    generate_react,
    materialize_assets,
    normalize_ir,
    package_report,
    static_gates,
    visual_gates,
)

_CLASSNAME_LITERAL_RE = re.compile(r'className="([^"]*)"')
_CLASSNAME_TEMPLATE_RE = re.compile(r"className=\{`([^`]*)`\}")
_ARBITRARY_VALUE_RE = re.compile(r"\[([^\[\]]+)\]")


@dataclass
class PipelineDependencies:
    """Dependency injection for external effects and existing codegen functions."""

    fetch_snapshot: Callable[[str, str], Awaitable[Dict[str, Any]]]
    extract_tokens: Callable[[str, str, Dict[str, Any]], Awaitable[Dict[str, Any]]]
    resolve_image_urls: Callable[[str, List[str]], Awaitable[Dict[str, str]]]
    generate_react_code: Callable[[Dict[str, Any], str, bool], str]
    sanitize_component_name: Callable[[str], str]
    get_figma_screenshot: Callable[[str, str, float], Awaitable[Optional[str]]]
    render_implementation_screenshot: Callable[
        [str, str, List[Dict[str, Any]], int, int, str, bool],
        Awaitable[Dict[str, Any]],
    ]


@dataclass
class PipelineConfig:
    """Runtime configuration for deterministic runs."""

    pipeline_version: str = "2.0.0"
    cache_root: Path = Path(".qa/cache")
    output_root: Path = Path(".qa/runs")
    cache_enabled: bool = True
    pass_threshold: float = 95.0
    warn_threshold: float = 85.0
    visual_mode: str = "hybrid"


def _stable_digest(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _normalize_tailwind_arbitrary_classes(code: str) -> str:
    """Deterministically normalize Tailwind arbitrary values for better runtime fidelity."""

    def _normalize_bracket(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        content = re.sub(r",\s*", ",", content)
        content = re.sub(r"(?<=\d)\.0(?=[a-zA-Z%])", "", content)
        content = re.sub(r"\s+", "_", content)
        return f"[{content}]"

    def _normalize_class_attr(match: re.Match[str]) -> str:
        class_value = match.group(1)
        normalized = _ARBITRARY_VALUE_RE.sub(_normalize_bracket, class_value)
        normalized = " ".join(normalized.split())
        return f'className="{normalized}"'

    return _CLASSNAME_LITERAL_RE.sub(_normalize_class_attr, code)


def _add_overflow_hidden_for_rounded(code: str) -> str:
    """Add overflow-hidden to rounded containers to better match clipped Figma frames."""

    def _augment_classes(class_value: str) -> str:
        classes = class_value.split()
        has_rounded = any(token.startswith("rounded") or "rounded-" in token for token in classes)
        has_overflow = any(token.startswith("overflow-") for token in classes)
        if has_rounded and not has_overflow:
            classes.append("overflow-hidden")
        return " ".join(classes)

    def _literal_repl(match: re.Match[str]) -> str:
        return f'className="{_augment_classes(match.group(1))}"'

    def _template_repl(match: re.Match[str]) -> str:
        return "className={`" + _augment_classes(match.group(1)) + "`}"

    result = _CLASSNAME_LITERAL_RE.sub(_literal_repl, code)
    result = _CLASSNAME_TEMPLATE_RE.sub(_template_repl, result)
    return result


class PipelineRunner:
    """Coordinates deterministic stages, caching, and gate-driven outcomes."""

    def __init__(self, deps: PipelineDependencies, config: PipelineConfig) -> None:
        self.deps = deps
        self.config = config
        self.cache = StageCache(config.cache_root)

    async def run(self, request: PipelineRunRequest) -> PipelineRunResult:
        run_identity = {
            "file_key": request.file_key,
            "node_id": request.node_id,
            "framework": request.framework,
            "mode": request.mode.value,
            "pipeline_version": self.config.pipeline_version,
        }
        run_hash = _stable_digest(run_identity)
        run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{run_hash[:10]}"

        output_root = Path(request.output_dir).expanduser().resolve() if request.output_dir else self.config.output_root.resolve()
        output_root.mkdir(parents=True, exist_ok=True)

        metrics = StageMetrics()
        cache_hits: List[str] = []
        cache_misses: List[str] = []
        errors: List[str] = []

        config_hash = _stable_digest(
            {
                "pipeline_version": self.config.pipeline_version,
                "cache_enabled": self.config.cache_enabled,
                "pass_threshold": self.config.pass_threshold,
                "warn_threshold": self.config.warn_threshold,
                "visual_mode": request.visual_mode or self.config.visual_mode,
                "target_match": request.target_match,
                "mode": request.mode.value,
                "framework": request.framework,
            }
        )
        # Always fetch a fresh snapshot first so downstream cache keys can include figma_version.
        snapshot = await metrics.timed(
            "fetch_snapshot",
            fetch_snapshot.run(request.file_key, request.node_id, self.deps.fetch_snapshot),
        )

        figma_version = (
            snapshot.get("meta", {}).get("figma_version")
            or snapshot.get("meta", {}).get("last_modified")
            or "unknown"
        )

        base_cache_key = _stable_digest(
            {
                "file_key": request.file_key,
                "node_id": request.node_id,
                "figma_version": figma_version,
                "pipeline_version": self.config.pipeline_version,
                "config_hash": config_hash,
                "framework": request.framework,
                "mode": request.mode.value,
            }
        )

        async def run_stage_cached(stage_name: str, payload: Dict[str, Any], producer: Callable[[], Awaitable[Dict[str, Any]]]) -> Dict[str, Any]:
            if request.use_cache and self.config.cache_enabled:
                stage_key = self.cache.build_stage_key(base_cache_key, stage_name, payload)
                cached = self.cache.load(stage_key)
                if cached is not None:
                    cache_hits.append(stage_name)
                    metrics.stage_timings.setdefault(stage_name, 0.0)
                    return cached

                cache_misses.append(stage_name)
                result = await metrics.timed(stage_name, producer())
                self.cache.save(stage_key, result)
                return result

            cache_misses.append(stage_name)
            return await metrics.timed(stage_name, producer())

        tokens = await run_stage_cached(
            "extract_tokens",
            {
                "file_key": request.file_key,
                "node_id": request.node_id,
                "figma_version": figma_version,
            },
            lambda: self.deps.extract_tokens(request.file_key, request.node_id, snapshot["node"]),
        )

        design_ir = await run_stage_cached(
            "normalize_ir",
            {
                "node_id": request.node_id,
                "token_hash": _stable_digest(tokens),
            },
            lambda: _wrap_sync(normalize_ir.run(snapshot, tokens)),
        )

        asset_materialization = await run_stage_cached(
            "materialize_assets",
            {
                "node_id": request.node_id,
                "figma_version": figma_version,
            },
            lambda: materialize_assets.run(
                design_ir,
                request.file_key,
                self.deps.resolve_image_urls,
                self.config.cache_root / "assets",
            ),
        )

        design_ir = asset_materialization["design_ir"]

        component_graph = await run_stage_cached(
            "build_component_dag",
            {
                "ordering_hash": _stable_digest({"ordering": design_ir.get("ordering", [])}),
            },
            lambda: _wrap_sync(build_component_dag.run(design_ir)),
        )

        generation = await run_stage_cached(
            "generate_react",
            {
                "framework": request.framework,
                "mode": request.mode.value,
                "run_label": request.run_label or "",
                "asset_manifest_hash": _stable_digest({"manifest": asset_materialization.get("manifest", [])}),
            },
            lambda: _wrap_sync(
                generate_react.run(
                    design_ir,
                    request.framework,
                    request.mode,
                    request.run_label,
                    self.deps.generate_react_code,
                    self.deps.sanitize_component_name,
                )
            ),
        )

        static_gate = await metrics.timed(
            "static_gates",
            _wrap_sync(
                static_gates.run(
                    generation["code"],
                    asset_materialization.get("manifest", []),
                    pass_threshold=self.config.pass_threshold,
                    warn_threshold=self.config.warn_threshold,
                ).model_dump()
            ),
        )

        gate_results: List[GateResult] = [GateResult(**static_gate)]

        visual_mode = request.visual_mode or self.config.visual_mode
        figma_screenshot_path = None
        implementation_screenshot_path = request.implementation_screenshot_path

        if gate_results[0].status == GateStatus.FAIL:
            visual_gate_result = GateResult(
                gate_name="visual",
                status=GateStatus.SKIPPED,
                score=0.0,
                threshold=self.config.pass_threshold,
                evidence_paths=[],
                issues=["Static gates failed; visual gate was not executed."],
            )
            visual_gate = visual_gate_result.model_dump()
        else:
            if not implementation_screenshot_path and request.auto_render_implementation:
                bounds = design_ir.get("layout", {}).get("bounds", {}) if isinstance(design_ir.get("layout"), dict) else {}
                viewport_width = int(round(float(bounds.get("width", 1440) or 1440)))
                viewport_height = int(round(float(bounds.get("height", 900) or 900)))
                render_output = str((output_root / run_id / "implementation.png").resolve())

                try:
                    render_result = await metrics.timed(
                        "render_implementation_screenshot",
                        asyncio.wait_for(
                            self.deps.render_implementation_screenshot(
                                generation["code"],
                                generation["component_name"],
                                asset_materialization.get("manifest", []),
                                viewport_width,
                                viewport_height,
                                render_output,
                                request.framework == "react_tailwind",
                            ),
                            timeout=90.0,
                        ),
                    )
                    implementation_screenshot_path = render_result.get("path")
                    render_error = render_result.get("error")
                    if render_error:
                        errors.append(str(render_error))
                except asyncio.TimeoutError:
                    errors.append("Implementation screenshot render timed out after 90 seconds.")

            figma_screenshot_path = await metrics.timed(
                "capture_figma_screenshot",
                self.deps.get_figma_screenshot(request.file_key, request.node_id, request.figma_screenshot_scale),
            )

            visual_gate_result = visual_gates.run(
                figma_screenshot_path=figma_screenshot_path,
                implementation_screenshot_path=implementation_screenshot_path,
                pass_threshold=self.config.pass_threshold,
                warn_threshold=self.config.warn_threshold,
                visual_mode=visual_mode,
            )
            visual_gate = await metrics.timed("visual_gates", _wrap_sync(visual_gate_result.model_dump()))

        gate_results.append(GateResult(**visual_gate))

        status = _derive_pipeline_status(gate_results)
        fallback_count = 0

        if (
            status == PipelineStatus.FAIL
            and gate_results[-1].gate_name == "visual"
            and gate_results[-1].status == GateStatus.FAIL
            and request.auto_render_implementation
        ):
            baseline_score = float(gate_results[-1].score)
            max_patch_iterations = min(request.max_visual_iterations, 2)
            patch_strategies = [
                _normalize_tailwind_arbitrary_classes,
                _add_overflow_hidden_for_rounded,
            ]

            for iteration in range(1, max_patch_iterations + 1):
                strategy = patch_strategies[min(iteration - 1, len(patch_strategies) - 1)]
                patched_code = strategy(generation["code"])
                if patched_code == generation["code"]:
                    errors.append(
                        f"Exception patch iteration {iteration} produced no code change."
                    )
                    continue

                patched_static = static_gates.run(
                    patched_code,
                    asset_materialization.get("manifest", []),
                    pass_threshold=self.config.pass_threshold,
                    warn_threshold=self.config.warn_threshold,
                )
                if patched_static.status == GateStatus.FAIL:
                    errors.append(
                        f"Exception patch iteration {iteration} failed static gate; patch rejected."
                    )
                    break

                candidate_render_path = str(
                    (output_root / run_id / f"implementation.iter{iteration}.png").resolve()
                )
                try:
                    render_result = await metrics.timed(
                        f"exception_render_{iteration}",
                        asyncio.wait_for(
                            self.deps.render_implementation_screenshot(
                                patched_code,
                                generation["component_name"],
                                asset_materialization.get("manifest", []),
                                int(round(float(design_ir.get("layout", {}).get("bounds", {}).get("width", 1440) or 1440))),
                                int(round(float(design_ir.get("layout", {}).get("bounds", {}).get("height", 900) or 900))),
                                candidate_render_path,
                                request.framework == "react_tailwind",
                            ),
                            timeout=90.0,
                        ),
                    )
                except asyncio.TimeoutError:
                    errors.append(f"Exception patch iteration {iteration} timed out.")
                    break

                candidate_impl_path = render_result.get("path")
                if not candidate_impl_path:
                    errors.append(
                        f"Exception patch iteration {iteration} did not produce an implementation screenshot."
                    )
                    break

                patched_visual = visual_gates.run(
                    figma_screenshot_path=figma_screenshot_path,
                    implementation_screenshot_path=candidate_impl_path,
                    pass_threshold=self.config.pass_threshold,
                    warn_threshold=self.config.warn_threshold,
                    visual_mode=visual_mode,
                )

                if patched_visual.score <= baseline_score:
                    errors.append(
                        f"Exception patch iteration {iteration} did not improve visual score ({patched_visual.score:.2f} <= {baseline_score:.2f})."
                    )
                    continue

                generation["code"] = patched_code
                static_gate = patched_static.model_dump()
                visual_gate = patched_visual.model_dump()
                implementation_screenshot_path = candidate_impl_path
                baseline_score = float(patched_visual.score)
                fallback_count += 1
                gate_results = [GateResult(**static_gate), GateResult(**visual_gate)]
                status = _derive_pipeline_status(gate_results)

                if status != PipelineStatus.FAIL:
                    break

        if status == PipelineStatus.FAIL:
            exception_result = await metrics.timed(
                "exception_lane",
                run_exception_lane(
                    status,
                    gate_results,
                    max_iterations=request.max_visual_iterations,
                    attempted_iterations=fallback_count,
                ),
            )
            fallback_count = int(exception_result.get("fallback_count", fallback_count))
            errors.extend(exception_result.get("errors", []))
            status = exception_result.get("status", PipelineStatus.FAIL)

        quality_metrics = dict(generation.get("quality_metrics", {}))
        quality_metrics["visual_score"] = visual_gate.get("score", 0.0)

        summary_payload = {
            "run_id": run_id,
            "status": status.value if isinstance(status, PipelineStatus) else str(status),
            "request": request.model_dump(),
            "stage_timings": metrics.stage_timings,
            "quality_metrics": quality_metrics,
            "gates": [gate.model_dump() for gate in gate_results],
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "fallback_count": fallback_count,
            "errors": errors,
            "config": {
                "pipeline_version": self.config.pipeline_version,
                "config_hash": config_hash,
                "visual_mode": visual_mode,
            },
        }

        visual_gate["figma_screenshot_path"] = figma_screenshot_path
        visual_gate["implementation_screenshot_path"] = implementation_screenshot_path

        artifacts = await metrics.timed(
            "package_report",
            _wrap_sync(
                package_report.run(
                    output_root=output_root,
                    run_id=run_id,
                    snapshot=snapshot,
                    design_ir=design_ir,
                    asset_materialization=asset_materialization,
                    component_graph=component_graph,
                    generation=generation,
                    static_gate=static_gate,
                    visual_gate=visual_gate,
                    summary=summary_payload,
                )
            ),
        )

        pipeline_status = status if isinstance(status, PipelineStatus) else PipelineStatus(str(status))

        return PipelineRunResult(
            run_id=run_id,
            status=pipeline_status,
            stage_timings=metrics.stage_timings,
            quality_metrics=quality_metrics,
            artifacts=artifacts,
            fallback_count=fallback_count,
            errors=errors,
            gates=gate_results,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            metadata={
                "pipeline_version": self.config.pipeline_version,
                "config_hash": config_hash,
                "visual_mode": visual_mode,
            },
        )


def _derive_pipeline_status(gates: List[GateResult]) -> PipelineStatus:
    if any(gate.status == GateStatus.FAIL for gate in gates):
        return PipelineStatus.FAIL
    if any(gate.status in {GateStatus.WARN, GateStatus.SKIPPED} for gate in gates):
        return PipelineStatus.WARN
    return PipelineStatus.PASS


async def _wrap_sync(value: Dict[str, Any]) -> Dict[str, Any]:
    return value
