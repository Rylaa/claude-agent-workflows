"""Stage-level JSON cache for deterministic pipeline runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


class StageCache:
    """Simple file-backed cache keyed by stable hashes."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _stable_json(value: Dict[str, Any]) -> str:
        return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

    def build_stage_key(self, base_key: str, stage_name: str, payload: Dict[str, Any]) -> str:
        digest = hashlib.sha256()
        digest.update(base_key.encode("utf-8"))
        digest.update(stage_name.encode("utf-8"))
        digest.update(self._stable_json(payload).encode("utf-8"))
        return digest.hexdigest()

    def _stage_file(self, stage_key: str) -> Path:
        return self.root_dir / f"{stage_key}.json"

    def load(self, stage_key: str) -> Optional[Dict[str, Any]]:
        path = self._stage_file(stage_key)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def save(self, stage_key: str, data: Dict[str, Any]) -> Path:
        path = self._stage_file(stage_key)
        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=True, indent=2), encoding="utf-8")
        temp_path.replace(path)
        return path
