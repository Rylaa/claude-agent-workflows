"""Snapshot fetch stage."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict


async def run(
    file_key: str,
    node_id: str,
    fetch_snapshot_fn: Callable[[str, str], Awaitable[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Fetch a raw Figma snapshot for a specific node."""

    raw = await fetch_snapshot_fn(file_key, node_id)
    nodes = raw.get("nodes", {})
    node = nodes.get(node_id, {}).get("document", {})
    if not node:
        raise ValueError(f"Node '{node_id}' not found in file '{file_key}'.")

    meta = {
        "file_key": file_key,
        "node_id": node_id,
        "figma_version": raw.get("lastModified") or datetime.now(timezone.utc).isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "meta": meta,
        "node": node,
        "raw": raw,
    }
