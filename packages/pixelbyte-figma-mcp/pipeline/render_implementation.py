"""Render generated React code to a PNG for visual gate comparison."""

from __future__ import annotations

import asyncio
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


_IMPORT_LINE_RE = re.compile(r"(?m)^\s*import\s+[^;]+;\s*$")
_EXPORT_CONST_RE = re.compile(r"(?m)^\s*export\s+const\s+")
_EXPORT_FUNCTION_RE = re.compile(r"(?m)^\s*export\s+function\s+")
_EXPORT_DEFAULT_RE = re.compile(r"(?m)^\s*export\s+default\s+")
_EXPORT_LIST_RE = re.compile(r"(?m)^\s*export\s*\{[^}]+\};?\s*$")


def _rewrite_asset_paths(code: str, asset_manifest: List[Dict[str, Any]]) -> str:
    for item in asset_manifest:
        logical_path = item.get("logical_path")
        local_path = item.get("local_path")
        if not logical_path or not local_path:
            continue
        uri = Path(local_path).expanduser().resolve().as_uri()
        code = code.replace(f'"{logical_path}"', f'"{uri}"')
        code = code.replace(f"'{logical_path}'", f"'{uri}'")
    return code


def _to_babel_compatible_script(code: str) -> str:
    transformed = _IMPORT_LINE_RE.sub("", code)
    transformed = _EXPORT_CONST_RE.sub("const ", transformed)
    transformed = _EXPORT_FUNCTION_RE.sub("function ", transformed)
    transformed = _EXPORT_DEFAULT_RE.sub("const __PBDefaultExport = ", transformed)
    transformed = _EXPORT_LIST_RE.sub("", transformed)
    return transformed


async def _ensure_playwright_chromium(timeout_seconds: int = 240) -> None:
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "playwright",
        "install",
        "chromium",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        process.kill()
        await process.communicate()
        raise RuntimeError("Timed out while installing Playwright Chromium browser.") from exc
    if process.returncode != 0:
        raise RuntimeError("Failed to install Playwright Chromium browser.")


async def _capture_with_playwright(
    html_path: Path,
    output_path: Path,
    viewport_width: int,
    viewport_height: int,
    timeout_ms: int,
) -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
        await page.goto(html_path.as_uri(), wait_until="domcontentloaded", timeout=timeout_ms)
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(output_path), full_page=False)
        await browser.close()


async def render_react_implementation_screenshot(
    generated_code: str,
    component_name: str,
    asset_manifest: List[Dict[str, Any]],
    viewport_width: int,
    viewport_height: int,
    output_path: str,
    use_tailwind: bool = True,
    timeout_ms: int = 45_000,
) -> Dict[str, Any]:
    """Render TSX code in headless browser and capture PNG screenshot."""

    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    width = max(1, int(viewport_width))
    height = max(1, int(viewport_height))

    code = _rewrite_asset_paths(generated_code, asset_manifest)
    script = _to_babel_compatible_script(code)

    tailwind_script = (
        "<script src=\"https://cdn.tailwindcss.com\"></script>" if use_tailwind else ""
    )

    html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width={width}, initial-scale=1.0" />
    {tailwind_script}
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
      html, body {{
        margin: 0;
        padding: 0;
        width: {width}px;
        height: {height}px;
        overflow: hidden;
        background: transparent;
      }}
      #root {{
        width: {width}px;
        height: {height}px;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="text/babel" data-presets="typescript,react">
{script}
const __PBTarget = (typeof {component_name} !== 'undefined')
  ? {component_name}
  : (typeof __PBDefaultExport !== 'undefined' ? __PBDefaultExport : null);
if (!__PBTarget) {{
  throw new Error("Renderable component not found: {component_name}");
}}
const __PBRoot = ReactDOM.createRoot(document.getElementById("root"));
__PBRoot.render(React.createElement(__PBTarget));
    </script>
  </body>
</html>
"""

    with tempfile.TemporaryDirectory(prefix="pb_figma_render_") as temp_dir:
        html_path = Path(temp_dir) / "render.html"
        html_path.write_text(html, encoding="utf-8")

        try:
            await _capture_with_playwright(html_path, output, width, height, timeout_ms)
        except Exception as exc:  # noqa: BLE001
            message = str(exc)
            if "Executable doesn't exist" in message or "download new browsers" in message:
                try:
                    await _ensure_playwright_chromium()
                    await _capture_with_playwright(html_path, output, width, height, timeout_ms)
                except Exception as install_exc:  # noqa: BLE001
                    return {
                        "path": None,
                        "error": f"Implementation screenshot render failed after browser install attempt: {install_exc}",
                    }
            else:
                return {
                    "path": None,
                    "error": f"Implementation screenshot render failed: {exc}",
                }

    return {"path": str(output), "error": None}
