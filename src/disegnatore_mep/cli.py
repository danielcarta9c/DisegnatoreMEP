import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.io.canonical import project_fingerprint
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
from disegnatore_mep.layout.geometry import drawing_fingerprint
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.validation.geometry import validate_drawing_geometry
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

    draw = commands.add_parser("draw")
    draw.add_argument("project", type=Path)
    draw.add_argument("--catalog", type=Path, required=True)
    draw.add_argument("--symbols", type=Path, required=True)
    draw.add_argument("--out", type=Path, required=True)
    draw.add_argument("--geometry", type=Path)
    return parser


def _draw(args: argparse.Namespace) -> int:
    """Compone e scrive una tavola SVG per foglio.

    Codici di uscita coerenti col resto della CLI: `0` disegno prodotto, `2`
    errori bloccanti, `1` errori di caricamento. La tavola esce marcata come
    bozza finche' il cartiglio non e' compilato (D-025).
    """
    project = load_project(args.project)
    symbols = SymbolRegistry.from_directory(args.symbols)
    catalog = ComponentRegistry.from_directory(args.catalog, symbols=symbols)

    report = validate_project(project, catalog)
    if not report.ok:
        print(report.model_dump_json(indent=2))
        return 2

    frame, drawing = compose_on_ordinary_frame(project, catalog)
    geometry_report = validate_drawing_geometry(drawing, frame)
    if not geometry_report.ok:
        print(geometry_report.model_dump_json(indent=2))
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    for sheet in drawing.sheets:
        target = args.out / f"{project.metadata.project_id}-{sheet.sheet_id}.svg"
        target.write_text(render_sheet(sheet, frame, symbols), encoding="utf-8")
    if args.geometry:
        args.geometry.write_text(
            drawing.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    print(drawing_fingerprint(drawing))
    return 0


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
        if args.command == "draw":
            return _draw(args)
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
