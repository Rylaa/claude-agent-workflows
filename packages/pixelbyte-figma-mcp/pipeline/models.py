"""Typed contracts for deterministic pipeline requests, stages, and results."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PipelineMode(str, Enum):
    """Pipeline generation mode."""

    STRICT_PIXEL = "strict_pixel"
    STRICT_PIXEL_PLUS_RESPONSIVE = "strict_pixel_plus_responsive"


class PipelineStatus(str, Enum):
    """Overall pipeline run status."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"


class GateStatus(str, Enum):
    """Per-gate status."""

    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


class PipelineRunRequest(BaseModel):
    """Canonical request used by the deterministic runner."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    file_key: str = Field(..., min_length=10, max_length=64)
    node_id: str = Field(..., min_length=1)
    framework: str = Field(default="react_tailwind")
    mode: PipelineMode = Field(default=PipelineMode.STRICT_PIXEL)
    target_match: float = Field(default=0.95, ge=0.0, le=1.0)
    use_cache: bool = Field(default=True)
    max_visual_iterations: int = Field(default=3, ge=1, le=5)
    output_dir: Optional[str] = Field(default=None)
    run_label: Optional[str] = Field(default=None)
    visual_mode: str = Field(default="hybrid")
    figma_screenshot_scale: float = Field(default=2.0, ge=0.01, le=4.0)
    implementation_screenshot_path: Optional[str] = Field(default=None)
    auto_render_implementation: bool = Field(default=True)


class AssetManifestItem(BaseModel):
    """Materialized asset entry."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    asset_id: str
    source_node_id: str
    image_ref: str
    local_path: str
    logical_path: str
    hash: str
    mime: str


class ComponentGraphNode(BaseModel):
    """Component DAG node metadata."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    component_id: str
    deps: List[str] = Field(default_factory=list)
    batch: int = 0
    priority: int = 0


class GateResult(BaseModel):
    """Single gate outcome."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")

    gate_name: str
    status: GateStatus
    score: float = Field(default=0.0)
    threshold: float = Field(default=0.0)
    evidence_paths: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)


class DesignIR(BaseModel):
    """Normalized design intermediate representation."""

    model_config = ConfigDict(validate_assignment=True, extra="allow")

    meta: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    styles: Dict[str, Any] = Field(default_factory=dict)
    layout: Dict[str, Any] = Field(default_factory=dict)
    tokens: Dict[str, Any] = Field(default_factory=dict)
    assets: Dict[str, Any] = Field(default_factory=dict)
    ordering: List[str] = Field(default_factory=list)


class PipelineRunResult(BaseModel):
    """Complete deterministic pipeline run output."""

    model_config = ConfigDict(validate_assignment=True, extra="allow")

    run_id: str
    status: PipelineStatus
    stage_timings: Dict[str, float] = Field(default_factory=dict)
    quality_metrics: Dict[str, Any] = Field(default_factory=dict)
    artifacts: Dict[str, str] = Field(default_factory=dict)
    fallback_count: int = Field(default=0, ge=0)
    errors: List[str] = Field(default_factory=list)
    gates: List[GateResult] = Field(default_factory=list)
    cache_hits: List[str] = Field(default_factory=list)
    cache_misses: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
