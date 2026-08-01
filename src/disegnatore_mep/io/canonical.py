import hashlib
import json
from typing import Any

from disegnatore_mep.model.project import ProjectModel

ORDERED_COLLECTIONS = {
    "subsystems",
    "networks",
    "components",
    "connections",
    "assumptions",
    "rule_applications",
    "sheets",
}


def _normalize(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {item_key: _normalize(value[item_key], item_key) for item_key in sorted(value)}
    if isinstance(value, list):
        normalized = [_normalize(item) for item in value]
        if key in ORDERED_COLLECTIONS:
            return sorted(normalized, key=lambda item: item["id"])
        return normalized
    return value


def canonical_json(project: ProjectModel) -> str:
    payload = project.model_dump(mode="json")
    normalized = _normalize(payload)
    return json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def project_fingerprint(project: ProjectModel) -> str:
    return hashlib.sha256(canonical_json(project).encode("utf-8")).hexdigest()
