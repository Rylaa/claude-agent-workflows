"""Tests for deterministic pipeline runner and stages."""

from __future__ import annotations

import json
import asyncio
from pathlib import Path
from typing import Any, Dict

import httpx

from pipeline.cache import StageCache
from pipeline.models import GateStatus, PipelineMode, PipelineRunRequest, PipelineStatus
from pipeline.runner import PipelineConfig, PipelineDependencies, PipelineRunner
from pipeline.stages import materialize_assets, normalize_ir, static_gates, visual_gates


def _sample_root_node() -> Dict[str, Any]:
    return {
        "id": "1:2",
        "name": "Root",
        "type": "FRAME",
        "layoutMode": "VERTICAL",
        "absoluteBoundingBox": {"x": 0, "y": 0, "width": 400, "height": 240},
        "fills": [{"type": "IMAGE", "visible": True, "imageRef": "img_ref_1", "scaleMode": "FILL"}],
        "strokes": [],
        "effects": [],
        "children": [
            {
                "id": "1:3",
                "name": "Title",
                "type": "TEXT",
                "absoluteBoundingBox": {"x": 10, "y": 10, "width": 120, "height": 24},
                "fills": [{"type": "SOLID", "visible": True, "color": {"r": 1, "g": 1, "b": 1, "a": 1}}],
                "strokes": [],
                "effects": [],
                "children": [],
            },
            {
                "id": "1:4",
                "name": "Body",
                "type": "FRAME",
                "absoluteBoundingBox": {"x": 10, "y": 40, "width": 320, "height": 160},
                "fills": [],
                "strokes": [],
                "effects": [],
                "children": [],
            },
        ],
    }


class _FakeHTTPResponse:
    def __init__(self, content: bytes = b"png-bytes", status_code: int = 200, mime: str = "image/png") -> None:
        self.content = content
        self.status_code = status_code
        self.headers = {"content-type": mime}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.test")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("error", request=request, response=response)


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str) -> _FakeHTTPResponse:
        if "missing" in url:
            return _FakeHTTPResponse(status_code=404)
        return _FakeHTTPResponse(content=b"image-bytes-123", status_code=200, mime="image/png")


def test_stage_cache_roundtrip(tmp_path: Path):
    cache = StageCache(tmp_path / "cache")
    key = cache.build_stage_key("base", "stage-a", {"x": 1})
    assert cache.load(key) is None

    payload = {"hello": "world"}
    cache.save(key, payload)
    assert cache.load(key) == payload


def test_normalize_ir_preserves_child_order():
    snapshot = {
        "meta": {"file_key": "file123456", "node_id": "1:2", "figma_version": "v1"},
        "node": _sample_root_node(),
        "raw": {},
    }
    tokens = {"colors": [], "typography": [], "spacing": [], "shadows": [], "blurs": []}

    ir = normalize_ir.run(snapshot, tokens)
    assert ir["ordering"][:3] == ["1:2", "1:3", "1:4"]

    by_id = {node["id"]: node for node in ir["nodes"]}
    assert by_id["1:3"]["child_index"] == 0
    assert by_id["1:4"]["child_index"] == 1


async def _resolve_urls(file_key: str, image_refs: list[str]) -> Dict[str, str]:
    return {ref: f"https://example.test/{ref}.png" for ref in image_refs}


def test_materialize_assets_rewrites_urls(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(materialize_assets.httpx, "AsyncClient", _FakeAsyncClient)

    ir = {
        "root_node": _sample_root_node(),
        "assets": {},
    }

    result = asyncio.run(
        materialize_assets.run(
            design_ir=ir,
            file_key="file123456",
            resolve_image_urls_fn=_resolve_urls,
            assets_root=tmp_path / "assets",
        )
    )

    assert result["manifest"]
    assert result["by_image_ref"]["img_ref_1"].startswith("/assets/figma/")
    assert "https://" not in result["design_ir"]["root_node"]["fills"][0].get("imageUrl", "")


def test_static_gate_threshold_boundaries():
    code_ok = "export const A = () => <div className={className} />;"
    gate_pass = static_gates.run(code_ok, asset_manifest=[], pass_threshold=95.0, warn_threshold=85.0)
    assert gate_pass.status in {GateStatus.PASS, GateStatus.WARN}

    code_fail = "/* imageRef: abc */\nconst x = 'https://s3-alpha-sig.figma.com/x';"
    gate_fail = static_gates.run(code_fail, asset_manifest=[], pass_threshold=95.0, warn_threshold=85.0)
    assert gate_fail.status == GateStatus.FAIL


def test_visual_gate_without_implementation_warns(tmp_path: Path):
    figma_path = tmp_path / "figma.png"
    figma_path.write_bytes(b"same-binary-data")

    gate = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=None,
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate.status == GateStatus.WARN


def test_visual_gate_identical_files_pass(tmp_path: Path):
    figma_path = tmp_path / "figma.png"
    impl_path = tmp_path / "impl.png"
    figma_path.write_bytes(b"pixel-perfect")
    impl_path.write_bytes(b"pixel-perfect")

    gate = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate.status == GateStatus.PASS


def test_visual_gate_threshold_boundaries(tmp_path: Path, monkeypatch):
    figma_path = tmp_path / "figma.png"
    impl_path = tmp_path / "impl.png"
    figma_path.write_bytes(b"figma")
    impl_path.write_bytes(b"impl")

    monkeypatch.setattr(visual_gates, "_pixel_similarity", lambda _a, _b: 84.99)
    gate_8499 = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate_8499.status == GateStatus.FAIL

    monkeypatch.setattr(visual_gates, "_pixel_similarity", lambda _a, _b: 85.00)
    gate_8500 = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate_8500.status == GateStatus.WARN

    monkeypatch.setattr(visual_gates, "_pixel_similarity", lambda _a, _b: 94.99)
    gate_9499 = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate_9499.status == GateStatus.WARN

    monkeypatch.setattr(visual_gates, "_pixel_similarity", lambda _a, _b: 95.00)
    gate_9500 = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    assert gate_9500.status == GateStatus.PASS


def test_visual_gate_hybrid_adds_vision_explanation(tmp_path: Path, monkeypatch):
    figma_path = tmp_path / "figma.png"
    impl_path = tmp_path / "impl.png"
    figma_path.write_bytes(b"figma")
    impl_path.write_bytes(b"impl")

    monkeypatch.setattr(visual_gates, "_pixel_similarity", lambda _a, _b: 90.0)
    monkeypatch.setattr(
        visual_gates,
        "_vision_explanation",
        lambda _a, _b: {
            "issues": ["Vision summary: Layout/spacing mismatch (changed_pixels=22.00%)."],
            "evidence_paths": ["/tmp/diff-map.png"],
        },
    )

    gate = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )

    assert gate.status == GateStatus.WARN
    assert any("Vision summary:" in issue for issue in gate.issues)
    assert "/tmp/diff-map.png" in gate.evidence_paths


def test_visual_gate_ignores_alpha_only_differences(tmp_path: Path):
    try:
        from PIL import Image
    except ImportError:
        return

    figma_path = tmp_path / "figma.png"
    impl_path = tmp_path / "impl.png"

    figma_img = Image.new("RGBA", (10, 10), (120, 80, 200, 40))
    impl_img = Image.new("RGBA", (10, 10), (120, 80, 200, 255))
    figma_img.save(figma_path)
    impl_img.save(impl_path)

    gate = visual_gates.run(
        figma_screenshot_path=str(figma_path),
        implementation_screenshot_path=str(impl_path),
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )

    assert gate.status == GateStatus.PASS
    assert gate.score >= 99.0


async def _fetch_snapshot(file_key: str, node_id: str) -> Dict[str, Any]:
    return {
        "lastModified": "2026-02-14T00:00:00Z",
        "nodes": {
            node_id: {
                "document": _sample_root_node(),
            }
        },
    }


async def _extract_tokens(file_key: str, node_id: str, root_node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "colors": [{"hex": "#ffffff"}],
        "typography": [{"fontFamily": "Inter", "fontSize": 16}],
        "spacing": [{"type": "auto-layout", "value": 12}],
        "shadows": [],
        "blurs": [],
    }


def _generate_react_code(node: Dict[str, Any], component_name: str, use_tailwind: bool) -> str:
    image_url = ""
    fills = node.get("fills", [])
    if fills:
        image_url = fills[0].get("imageUrl", "")
    return f"""import React from 'react';

interface {component_name}Props {{
  className?: string;
}}

export const {component_name}: React.FC<{component_name}Props> = ({{ className = '' }}) => {{
  return <div className=\"w-[400px]\" style={{{{ background: 'url(\"{image_url}\") center/cover no-repeat' }}}}></div>;
}};
"""


def _sanitize(name: str) -> str:
    return "".join(ch for ch in name.title() if ch.isalnum()) or "Component"


async def _figma_screenshot(file_key: str, node_id: str, scale: float) -> str:
    path = Path(".qa") / "test-runs" / "pipeline-test-figma.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"figma-image")
    return str(path.resolve())


async def _render_implementation_screenshot(
    generated_code: str,
    component_name: str,
    asset_manifest: list[dict[str, Any]],
    viewport_width: int,
    viewport_height: int,
    output_path: str,
    use_tailwind: bool,
) -> Dict[str, Any]:
    return {"path": None, "error": None}


def test_runner_generates_artifacts_and_warn_status(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(materialize_assets.httpx, "AsyncClient", _FakeAsyncClient)

    deps = PipelineDependencies(
        fetch_snapshot=_fetch_snapshot,
        extract_tokens=_extract_tokens,
        resolve_image_urls=_resolve_urls,
        generate_react_code=_generate_react_code,
        sanitize_component_name=_sanitize,
        get_figma_screenshot=_figma_screenshot,
        render_implementation_screenshot=_render_implementation_screenshot,
    )
    config = PipelineConfig(
        pipeline_version="test",
        cache_root=tmp_path / "cache",
        output_root=tmp_path / "runs",
        cache_enabled=True,
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    runner = PipelineRunner(deps=deps, config=config)

    request = PipelineRunRequest(
        file_key="qyFsYyLyBsutXGGzZ9PLCp",
        node_id="1:2",
        framework="react_tailwind",
        mode=PipelineMode.STRICT_PIXEL,
        use_cache=True,
        target_match=0.95,
        max_visual_iterations=3,
        output_dir=str(tmp_path / "runs"),
    )

    result = asyncio.run(runner.run(request))
    assert result.status in {PipelineStatus.PASS, PipelineStatus.WARN}
    assert Path(result.artifacts["summary"]).exists()
    assert Path(result.artifacts["generated_code"]).exists()


def test_runner_cache_hits_on_second_run(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(materialize_assets.httpx, "AsyncClient", _FakeAsyncClient)

    deps = PipelineDependencies(
        fetch_snapshot=_fetch_snapshot,
        extract_tokens=_extract_tokens,
        resolve_image_urls=_resolve_urls,
        generate_react_code=_generate_react_code,
        sanitize_component_name=_sanitize,
        get_figma_screenshot=_figma_screenshot,
        render_implementation_screenshot=_render_implementation_screenshot,
    )
    config = PipelineConfig(
        pipeline_version="test",
        cache_root=tmp_path / "cache",
        output_root=tmp_path / "runs",
        cache_enabled=True,
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    runner = PipelineRunner(deps=deps, config=config)

    request = PipelineRunRequest(
        file_key="qyFsYyLyBsutXGGzZ9PLCp",
        node_id="1:2",
        framework="react_tailwind",
        mode=PipelineMode.STRICT_PIXEL,
        use_cache=True,
        target_match=0.95,
        max_visual_iterations=3,
        output_dir=str(tmp_path / "runs"),
    )

    first = asyncio.run(runner.run(request))
    second = asyncio.run(runner.run(request))

    assert first.cache_misses
    assert second.cache_hits
    assert len(second.cache_hits) >= len(first.cache_misses) - 1


def _generate_bad_code(node: Dict[str, Any], component_name: str, use_tailwind: bool) -> str:
    return "/* imageRef: still-here */\nconst leak = 'https://s3-alpha-sig.figma.com/x';"


def test_runner_static_fail_enters_exception_lane(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(materialize_assets.httpx, "AsyncClient", _FakeAsyncClient)

    deps = PipelineDependencies(
        fetch_snapshot=_fetch_snapshot,
        extract_tokens=_extract_tokens,
        resolve_image_urls=_resolve_urls,
        generate_react_code=_generate_bad_code,
        sanitize_component_name=_sanitize,
        get_figma_screenshot=_figma_screenshot,
        render_implementation_screenshot=_render_implementation_screenshot,
    )
    config = PipelineConfig(
        pipeline_version="test",
        cache_root=tmp_path / "cache",
        output_root=tmp_path / "runs",
        cache_enabled=False,
        pass_threshold=95.0,
        warn_threshold=85.0,
        visual_mode="hybrid",
    )
    runner = PipelineRunner(deps=deps, config=config)

    request = PipelineRunRequest(
        file_key="qyFsYyLyBsutXGGzZ9PLCp",
        node_id="1:2",
        framework="react_tailwind",
        mode=PipelineMode.STRICT_PIXEL,
        use_cache=False,
        target_match=0.95,
        max_visual_iterations=2,
        output_dir=str(tmp_path / "runs"),
    )

    result = asyncio.run(runner.run(request))
    assert result.status == PipelineStatus.FAIL
    assert result.fallback_count > 0
    assert result.errors
