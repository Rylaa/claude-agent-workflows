"""Asset materialization stage."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Set, Tuple

import httpx


def _collect_image_refs(node: Dict[str, Any], refs: Set[str], ref_to_node: Dict[str, str]) -> None:
    node_id = node.get("id", "")
    for fill in node.get("fills", []):
        if fill.get("type") == "IMAGE" and fill.get("visible", True):
            image_ref = fill.get("imageRef")
            if image_ref:
                refs.add(image_ref)
                ref_to_node.setdefault(image_ref, node_id)

    for child in node.get("children", []):
        _collect_image_refs(child, refs, ref_to_node)


def _mime_to_ext(mime_type: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
        "image/svg+xml": "svg",
        "image/gif": "gif",
    }
    return mapping.get(mime_type.lower(), "bin")


def _patch_node_image_urls(node: Dict[str, Any], ref_to_logical_path: Dict[str, str]) -> None:
    for fill in node.get("fills", []):
        if fill.get("type") == "IMAGE" and fill.get("visible", True):
            image_ref = fill.get("imageRef")
            if image_ref and image_ref in ref_to_logical_path:
                fill["imageUrl"] = ref_to_logical_path[image_ref]

    for child in node.get("children", []):
        _patch_node_image_urls(child, ref_to_logical_path)


async def run(
    design_ir: Dict[str, Any],
    file_key: str,
    resolve_image_urls_fn: Callable[[str, List[str]], Awaitable[Dict[str, str]]],
    assets_root: Path,
) -> Dict[str, Any]:
    """Resolve image refs and materialize local assets."""

    root_node = design_ir["root_node"]
    refs: Set[str] = set()
    ref_to_node: Dict[str, str] = {}
    _collect_image_refs(root_node, refs, ref_to_node)

    if not refs:
        design_ir["assets"] = {
            "manifest": [],
            "by_image_ref": {},
            "download_errors": [],
        }
        return {
            "design_ir": design_ir,
            "manifest": [],
            "by_image_ref": {},
            "download_errors": [],
            "url_to_logical_path": {},
        }

    assets_root.mkdir(parents=True, exist_ok=True)
    image_url_map = await resolve_image_urls_fn(file_key, sorted(refs))

    manifest: List[Dict[str, Any]] = []
    by_image_ref: Dict[str, str] = {}
    url_to_logical_path: Dict[str, str] = {}
    download_errors: List[str] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for image_ref in sorted(refs):
            image_url = image_url_map.get(image_ref)
            if not image_url:
                download_errors.append(f"Missing URL for imageRef '{image_ref}'.")
                continue

            try:
                response = await client.get(image_url)
                response.raise_for_status()
                content = response.content
                digest = hashlib.sha256(content).hexdigest()
                mime = response.headers.get("content-type", "application/octet-stream").split(";")[0].strip()
                ext = _mime_to_ext(mime)
                filename = f"{digest[:16]}.{ext}"
                local_path = assets_root / filename
                if not local_path.exists():
                    local_path.write_bytes(content)

                logical_path = f"/assets/figma/{filename}"
                by_image_ref[image_ref] = logical_path
                url_to_logical_path[image_url] = logical_path

                manifest.append(
                    {
                        "asset_id": digest[:16],
                        "source_node_id": ref_to_node.get(image_ref, ""),
                        "image_ref": image_ref,
                        "local_path": str(local_path),
                        "logical_path": logical_path,
                        "hash": digest,
                        "mime": mime,
                    }
                )
            except Exception as exc:  # noqa: BLE001
                download_errors.append(f"Failed to materialize imageRef '{image_ref}': {type(exc).__name__}: {exc}")

    _patch_node_image_urls(root_node, by_image_ref)
    design_ir["root_node"] = root_node
    design_ir["assets"] = {
        "manifest": manifest,
        "by_image_ref": by_image_ref,
        "download_errors": download_errors,
    }

    return {
        "design_ir": design_ir,
        "manifest": manifest,
        "by_image_ref": by_image_ref,
        "download_errors": download_errors,
        "url_to_logical_path": url_to_logical_path,
    }
