"""Confine di lettura e scrittura del modello di progetto.

La migrazione fra versioni di schema vive qui e non nel modello: in memoria
esiste una sola versione, cosi' nessun consumatore porta rami condizionali su
`schema_version`.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from disegnatore_mep.model.project import SCHEMA_VERSION, ProjectModel

# SCHEMA_VERSION e' definita nel modello, ma riesportata qui: questo e' il
# confine che decide quali versioni si leggono, e chi migra guarda qui.
__all__ = [
    "MIGRATIONS",
    "SCHEMA_VERSION",
    "SUPPORTED_SCHEMA_VERSIONS",
    "dump_project",
    "load_project",
    "migrate_project_document",
]


def _lift_1_0_0_to_1_1_0(document: dict[str, Any]) -> dict[str, Any]:
    """Le tavole acquistano il piano di impaginazione, vuoto (D-042).

    Un documento 1.0.0 non dichiarava quale sottosistema va su quale fascia:
    l'assenza si rappresenta con un elenco vuoto, non con un valore inventato.
    """
    lifted = dict(document)
    lifted["sheets"] = [
        {**sheet, "band_assignments": sheet.get("band_assignments", [])}
        for sheet in document.get("sheets", [])
    ]
    lifted["schema_version"] = "1.1.0"
    return lifted


MIGRATIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "1.0.0": _lift_1_0_0_to_1_1_0,
}
"""Da ogni versione leggibile, il passo che la porta a quella successiva."""

SUPPORTED_SCHEMA_VERSIONS = frozenset({*MIGRATIONS, SCHEMA_VERSION})


def migrate_project_document(document: dict[str, Any]) -> dict[str, Any]:
    """Porta un documento alla versione corrente, applicando i passi in catena."""
    if "schema_version" not in document:
        raise ValueError(
            f"the document declares no schema_version: this build reads "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)}"
        )
    current = document
    seen: set[str] = set()
    while current["schema_version"] != SCHEMA_VERSION:
        version = current["schema_version"]
        if version in seen:
            raise ValueError(f"migration loop at schema version {version}")
        seen.add(version)
        step = MIGRATIONS.get(version)
        if step is None:
            raise ValueError(
                f"unsupported schema version {version}: this build reads "
                f"{sorted(SUPPORTED_SCHEMA_VERSIONS)} and writes {SCHEMA_VERSION}"
            )
        current = step(current)
    return current


def load_project(path: Path) -> ProjectModel:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"{path} does not contain a project object")
    return ProjectModel.model_validate(migrate_project_document(document))


def dump_project(project: ProjectModel, path: Path) -> None:
    path.write_text(project.model_dump_json(indent=2) + "\n", encoding="utf-8")
