"""Deterministic React code generation stage."""

from __future__ import annotations

import copy
import inspect
import re
from typing import Any, Callable, Dict

from pipeline.models import PipelineMode


def _apply_responsive_pass(code: str) -> str:
    """Apply a deterministic responsive pass on top of strict pixel output."""

    class_match = re.search(r'className="([^"]+)"', code)
    if not class_match:
        return code

    original_classes = class_match.group(1).split()
    updated_classes = list(original_classes)

    for idx, css_class in enumerate(original_classes):
        width_match = re.fullmatch(r'w-\[(\d+(?:\.\d+)?)px\]', css_class)
        if width_match:
            max_width_class = f"max-w-[{width_match.group(1)}px]"
            updated_classes[idx] = "w-full"
            if max_width_class not in updated_classes:
                updated_classes.append(max_width_class)
            break

    if "overflow-x-auto" not in updated_classes:
        updated_classes.append("overflow-x-auto")

    replacement = 'className="' + " ".join(updated_classes) + '"'
    return code[: class_match.start()] + replacement + code[class_match.end() :]


def _quality_metrics(code: str) -> Dict[str, Any]:
    return {
        "chars": len(code),
        "lines": len(code.splitlines()),
        "div_count": len(re.findall(r"<div\\b", code)),
        "span_count": len(re.findall(r"<span\\b", code)),
        "semantic_count": len(re.findall(r"<(?:section|article|header|main|footer|nav|button|ul|li|p|h[1-6])\\b", code)),
        "svg_count": len(re.findall(r"<svg\\b", code)),
        "icon_comment_count": code.count("/* Icon:"),
        "image_ref_comment_count": code.count("imageRef:"),
        "https_url_count": len(re.findall(r"https://", code)),
        "fixed_px_utility_count": len(
            re.findall(r"\b(?:w|h|pt|pr|pb|pl|gap|text|leading|tracking)-\[[0-9]+(?:\.[0-9]+)?px\]", code)
        ),
    }


def run(
    design_ir: Dict[str, Any],
    framework: str,
    mode: PipelineMode,
    run_label: str | None,
    generate_react_code_fn: Callable[[Dict[str, Any], str, bool], str],
    sanitize_component_name_fn: Callable[[str], str],
) -> Dict[str, Any]:
    """Generate React/React-Tailwind code deterministically from IR."""

    if framework not in {"react", "react_tailwind"}:
        raise ValueError(f"Unsupported framework for deterministic React stage: {framework}")

    root_node = copy.deepcopy(design_ir["root_node"])
    source_name = run_label or root_node.get("name", "Component")
    component_name = sanitize_component_name_fn(source_name)

    use_tailwind = framework == "react_tailwind"
    hard_fidelity_profile = mode in {
        PipelineMode.STRICT_PIXEL,
        PipelineMode.STRICT_PIXEL_PLUS_RESPONSIVE,
    }

    supports_hard_fidelity = False
    try:
        supports_hard_fidelity = "hard_fidelity_profile" in inspect.signature(generate_react_code_fn).parameters
    except (TypeError, ValueError):
        supports_hard_fidelity = False

    if supports_hard_fidelity:
        code = generate_react_code_fn(
            root_node,
            component_name,
            use_tailwind,
            hard_fidelity_profile=hard_fidelity_profile,
        )
    else:
        code = generate_react_code_fn(root_node, component_name, use_tailwind)

    if mode == PipelineMode.STRICT_PIXEL_PLUS_RESPONSIVE:
        code = _apply_responsive_pass(code)

    return {
        "component_name": component_name,
        "framework": framework,
        "code": code,
        "quality_metrics": _quality_metrics(code),
    }
