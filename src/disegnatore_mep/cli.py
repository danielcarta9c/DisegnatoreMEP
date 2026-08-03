import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.svg import render_symbol_sheet
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
    # Optional and opt-in: without it the catalog is loaded on its own, exactly
    # as before. With it, ComponentRegistry runs the symbol/catalog cross-check
    # on the arbitrary --catalog directory the CLI advertises, not only on this
    # project's own fixtures.
    validate.add_argument("--symbols", type=Path)

    schema = commands.add_parser("export-schema")
    schema.add_argument("output", type=Path)

    fingerprint = commands.add_parser("fingerprint")
    fingerprint.add_argument("project", type=Path)

    sheet = commands.add_parser("symbols-sheet")
    sheet.add_argument("output", type=Path)
    sheet.add_argument("--symbols", type=Path, required=True)
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
        if args.command == "symbols-sheet":
            registry = SymbolRegistry.from_directory(args.symbols)
            args.output.write_text(render_symbol_sheet(registry), encoding="utf-8")
            return 0
        project = load_project(args.project)
        if args.command == "fingerprint":
            print(project_fingerprint(project))
            return 0
        symbols = SymbolRegistry.from_directory(args.symbols) if args.symbols else None
        catalog = ComponentRegistry.from_directory(args.catalog, symbols=symbols)
        report = validate_project(project, catalog)
        print(report.model_dump_json(indent=2))
        return 0 if report.ok else 2
    # CatalogError e SymbolError sono entrambe sottoclassi di ValueError: nominarle
    # qui era ridondante e insegnava una gerarchia sbagliata.
    except (OSError, ValidationError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
