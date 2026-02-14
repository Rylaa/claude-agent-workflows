"""Component DAG stage."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Set


_COMPONENT_TYPES = {"FRAME", "COMPONENT", "INSTANCE", "GROUP"}


def _build_maps(nodes: List[Dict[str, Any]]) -> tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    by_id = {node["id"]: node for node in nodes if node.get("id")}
    children_map: Dict[str, List[str]] = defaultdict(list)
    for node in nodes:
        parent_id = node.get("parent_id")
        node_id = node.get("id")
        if parent_id and node_id:
            children_map[parent_id].append(node_id)
    return by_id, children_map


def _topological_batches(component_ids: List[str], deps_map: Dict[str, List[str]]) -> Dict[str, int]:
    indegree = {component_id: len(deps_map.get(component_id, [])) for component_id in component_ids}
    dependents: Dict[str, List[str]] = defaultdict(list)
    for component_id, deps in deps_map.items():
        for dep in deps:
            dependents[dep].append(component_id)

    queue = deque(sorted([cid for cid, value in indegree.items() if value == 0]))
    batch_for: Dict[str, int] = {}
    visited = 0
    current_batch = 0

    while queue:
        level_size = len(queue)
        this_level: List[str] = []
        for _ in range(level_size):
            cid = queue.popleft()
            this_level.append(cid)

        for cid in sorted(this_level):
            batch_for[cid] = current_batch
            visited += 1
            for dependent in sorted(dependents.get(cid, [])):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)

        current_batch += 1

    if visited != len(component_ids):
        # Cycle fallback: put all unresolved nodes into deterministic final batch.
        unresolved = sorted(set(component_ids) - set(batch_for))
        for cid in unresolved:
            batch_for[cid] = current_batch

    return batch_for


def run(design_ir: Dict[str, Any]) -> Dict[str, Any]:
    """Build deterministic component dependency graph and batch assignment."""

    nodes = design_ir.get("nodes", [])
    ordering = design_ir.get("ordering", [])
    by_id, children_map = _build_maps(nodes)

    component_ids = [
        node_id
        for node_id in ordering
        if node_id in by_id and by_id[node_id].get("type") in _COMPONENT_TYPES
    ]

    deps_map: Dict[str, List[str]] = {}
    for component_id in component_ids:
        deps: List[str] = []
        for child_id in children_map.get(component_id, []):
            child_node = by_id.get(child_id)
            if child_node and child_node.get("type") in _COMPONENT_TYPES:
                deps.append(child_id)
        deps_map[component_id] = sorted(set(deps))

    batch_for = _topological_batches(component_ids, deps_map)
    component_rows: List[Dict[str, Any]] = []
    for priority, component_id in enumerate(component_ids):
        component_rows.append(
            {
                "component_id": component_id,
                "deps": deps_map.get(component_id, []),
                "batch": batch_for.get(component_id, 0),
                "priority": priority,
            }
        )

    batch_map: Dict[int, List[str]] = defaultdict(list)
    for row in component_rows:
        batch_map[row["batch"]].append(row["component_id"])

    batches = [
        {
            "batch": batch,
            "components": sorted(component_ids),
        }
        for batch, component_ids in sorted(batch_map.items(), key=lambda item: item[0])
    ]

    return {
        "components": component_rows,
        "batches": batches,
    }
