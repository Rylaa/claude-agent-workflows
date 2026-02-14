"""IR normalization stage."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _collect_nodes(
    node: Dict[str, Any],
    parent_id: Optional[str],
    depth: int,
    child_index: int,
    ordering: List[str],
    flattened: List[Dict[str, Any]],
) -> None:
    node_id = node.get("id", "")
    children = node.get("children", [])
    child_ids = [child.get("id", "") for child in children]

    flattened.append(
        {
            "id": node_id,
            "name": node.get("name", ""),
            "type": node.get("type", ""),
            "parent_id": parent_id,
            "depth": depth,
            "child_index": child_index,
            "child_ids": child_ids,
            "children_count": len(children),
            "layout_mode": node.get("layoutMode"),
            "absolute_bounding_box": node.get("absoluteBoundingBox", {}),
            "fills": node.get("fills", []),
            "strokes": node.get("strokes", []),
            "effects": node.get("effects", []),
            "visible": node.get("visible", True),
        }
    )
    ordering.append(node_id)

    for idx, child in enumerate(children):
        _collect_nodes(child, node_id, depth + 1, idx, ordering, flattened)


def _layout_summary(root_node: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mode": root_node.get("layoutMode"),
        "primary_axis_align": root_node.get("primaryAxisAlignItems"),
        "counter_axis_align": root_node.get("counterAxisAlignItems"),
        "padding": {
            "top": root_node.get("paddingTop", 0),
            "right": root_node.get("paddingRight", 0),
            "bottom": root_node.get("paddingBottom", 0),
            "left": root_node.get("paddingLeft", 0),
        },
        "gap": root_node.get("itemSpacing", 0),
        "bounds": root_node.get("absoluteBoundingBox", {}),
    }


def run(snapshot: Dict[str, Any], tokens: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize raw snapshot into a deterministic intermediate representation."""

    root_node = snapshot["node"]
    ordering: List[str] = []
    flattened: List[Dict[str, Any]] = []
    _collect_nodes(root_node, parent_id=None, depth=0, child_index=0, ordering=ordering, flattened=flattened)

    styles = {
        "colors": tokens.get("colors", []),
        "typography": tokens.get("typography", []),
        "effects": {
            "shadows": tokens.get("shadows", []),
            "blurs": tokens.get("blurs", []),
        },
    }

    ir = {
        "meta": snapshot["meta"],
        "nodes": flattened,
        "styles": styles,
        "layout": _layout_summary(root_node),
        "tokens": tokens,
        "assets": {
            "manifest": [],
            "by_image_ref": {},
            "download_errors": [],
        },
        "ordering": ordering,
        "root_node": root_node,
    }
    return ir
