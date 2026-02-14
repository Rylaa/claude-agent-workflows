"""Visual gate checks using pixel diff and hybrid vision-style explanations."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pipeline.models import GateResult, GateStatus


def _status_from_score(score: float, pass_threshold: float, warn_threshold: float) -> GateStatus:
    if score >= pass_threshold:
        return GateStatus.PASS
    if score >= warn_threshold:
        return GateStatus.WARN
    return GateStatus.FAIL


def _byte_similarity_fallback(path_a: Path, path_b: Path) -> float:
    a = path_a.read_bytes()
    b = path_b.read_bytes()
    if not a and not b:
        return 100.0
    if not a or not b:
        return 0.0

    # Deterministic, dependency-free approximation with bounded runtime.
    min_len = min(len(a), len(b))
    max_len = max(len(a), len(b))
    sample_budget = 200_000
    step = max(1, min_len // sample_budget)

    matches = 0
    samples = 0
    for idx in range(0, min_len, step):
        samples += 1
        if a[idx] == b[idx]:
            matches += 1

    if samples == 0:
        return 0.0

    sample_ratio = matches / samples
    length_ratio = min_len / max_len if max_len else 1.0
    return round(sample_ratio * length_ratio * 100.0, 2)


def _normalize_image_for_diff(image):
    from PIL import Image

    rgba = image.convert("RGBA")
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba)
    return composited.convert("RGB")


def _pixel_similarity(path_a: Path, path_b: Path) -> float:
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        return _byte_similarity_fallback(path_a, path_b)

    try:
        with Image.open(path_a) as img_a, Image.open(path_b) as img_b:
            img_a_rgb = _normalize_image_for_diff(img_a)
            img_b_rgb = _normalize_image_for_diff(img_b)

            if img_a_rgb.size != img_b_rgb.size:
                resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
                img_b_rgb = img_b_rgb.resize(img_a_rgb.size, resample=resampling)

            diff = ImageChops.difference(img_a_rgb, img_b_rgb)
            stat = ImageStat.Stat(diff)
            mean_delta = sum(stat.mean) / len(stat.mean) if stat.mean else 255.0
            similarity = max(0.0, 100.0 - ((mean_delta / 255.0) * 100.0))
            return round(similarity, 2)
    except Exception:  # noqa: BLE001
        return _byte_similarity_fallback(path_a, path_b)


def _vision_explanation(path_a: Path, path_b: Path) -> dict:
    """Produce deterministic visual-diff explanations and optional evidence paths."""
    try:
        from PIL import Image, ImageChops, ImageOps
    except ImportError:
        return {
            "issues": ["Vision explanation unavailable: Pillow is not installed."],
            "evidence_paths": [],
        }

    try:
        with Image.open(path_a) as img_a, Image.open(path_b) as img_b:
            img_a_rgb = _normalize_image_for_diff(img_a)
            img_b_rgb = _normalize_image_for_diff(img_b)

            if img_a_rgb.size != img_b_rgb.size:
                resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
                img_b_rgb = img_b_rgb.resize(img_a_rgb.size, resample=resampling)

            diff = ImageChops.difference(img_a_rgb, img_b_rgb)
            gray = diff.convert("L")
            bbox = gray.getbbox()
            width, height = gray.size
            total_pixels = max(1, width * height)

            histogram = gray.histogram()
            unchanged = histogram[0] if histogram else 0
            changed = max(0, total_pixels - unchanged)
            changed_ratio = (changed / total_pixels) * 100.0

            if changed_ratio >= 35.0:
                category = "High structural mismatch"
            elif changed_ratio >= 10.0:
                category = "Layout/spacing mismatch"
            else:
                category = "Color/tone mismatch"

            issues = [
                f"Vision summary: {category} (changed_pixels={changed_ratio:.2f}%).",
            ]
            if bbox:
                x0, y0, x1, y1 = bbox
                issues.append(f"Primary diff region: x={x0}-{x1}, y={y0}-{y1}.")

            evidence_paths: List[str] = []
            try:
                diff_map = ImageOps.autocontrast(gray)
                diff_path = path_b.with_name(path_b.stem + ".diff.png")
                diff_map.save(diff_path)
                evidence_paths.append(str(diff_path))
            except Exception:  # noqa: BLE001
                pass

            return {"issues": issues, "evidence_paths": evidence_paths}
    except Exception as exc:  # noqa: BLE001
        return {
            "issues": [f"Vision explanation failed: {type(exc).__name__}: {exc}"],
            "evidence_paths": [],
        }


def run(
    figma_screenshot_path: Optional[str],
    implementation_screenshot_path: Optional[str],
    pass_threshold: float,
    warn_threshold: float,
    visual_mode: str,
) -> GateResult:
    """Run visual validation gate."""

    evidence_paths: List[str] = []
    issues: List[str] = []

    if figma_screenshot_path:
        evidence_paths.append(figma_screenshot_path)

    if implementation_screenshot_path:
        evidence_paths.append(implementation_screenshot_path)

    if not figma_screenshot_path:
        return GateResult(
            gate_name="visual",
            status=GateStatus.SKIPPED,
            score=0.0,
            threshold=pass_threshold,
            evidence_paths=evidence_paths,
            issues=["Figma reference screenshot unavailable."],
        )

    if not implementation_screenshot_path:
        return GateResult(
            gate_name="visual",
            status=GateStatus.WARN,
            score=warn_threshold,
            threshold=pass_threshold,
            evidence_paths=evidence_paths,
            issues=["Implementation screenshot not provided; visual comparison skipped."],
        )

    figma_path = Path(figma_screenshot_path)
    impl_path = Path(implementation_screenshot_path)

    if not figma_path.exists() or not impl_path.exists():
        missing = []
        if not figma_path.exists():
            missing.append(str(figma_path))
        if not impl_path.exists():
            missing.append(str(impl_path))
        return GateResult(
            gate_name="visual",
            status=GateStatus.FAIL,
            score=0.0,
            threshold=pass_threshold,
            evidence_paths=evidence_paths,
            issues=[f"Missing screenshot files: {', '.join(missing)}"],
        )

    score = _pixel_similarity(figma_path, impl_path)
    status = _status_from_score(score, pass_threshold, warn_threshold)

    if status != GateStatus.PASS and visual_mode.lower() == "hybrid":
        vision = _vision_explanation(figma_path, impl_path)
        issues.extend(vision.get("issues", []))
        evidence_paths.extend(vision.get("evidence_paths", []))

    return GateResult(
        gate_name="visual",
        status=status,
        score=score,
        threshold=pass_threshold,
        evidence_paths=evidence_paths,
        issues=issues,
    )
