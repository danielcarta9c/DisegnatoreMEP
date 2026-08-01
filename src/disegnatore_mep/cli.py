import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.io.canonical import project_fingerprint
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.validation.topology import validate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="disegnatore-mep")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("project", type=Path)
    validate.add_argument("--catalog", type=Path, required=True)

    schema = commands.add_parser("export-schema")
    schema.add_argument("output", type=Path)

    fingerprint = commands.add_parser("fingerprint")
    fingerprint.add_argument("project", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "export-schema":
            args.output.write_text(
                json.dumps(ProjectModel.model_json_schema(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return 0
        project = load_project(args.project)
        if args.command == "fingerprint":
            print(project_fingerprint(project))
            return 0
        catalog = ComponentRegistry.from_directory(args.catalog)
        report = validate_project(project, catalog)
        print(report.model_dump_json(indent=2))
        return 0 if report.ok else 2
    except (OSError, ValidationError, CatalogError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
