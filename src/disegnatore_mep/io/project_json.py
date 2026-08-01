from pathlib import Path

from disegnatore_mep.model.project import ProjectModel


def load_project(path: Path) -> ProjectModel:
    return ProjectModel.model_validate_json(path.read_text(encoding="utf-8"))


def dump_project(project: ProjectModel, path: Path) -> None:
    path.write_text(project.model_dump_json(indent=2) + "\n", encoding="utf-8")
