import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.lines import read_lines
from disegnatore_mep.graph.naming import LineNaming, Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.io.canonical import canonical_json, project_fingerprint
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
from disegnatore_mep.layout.geometry import DrawingGeometry, drawing_fingerprint
from disegnatore_mep.layout.labels import place_addresses
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.report import CATEGORY_LABELS, build_report
from disegnatore_mep.validation.geometry import validate_drawing_geometry
from disegnatore_mep.validation.issues import ValidationIssue, ValidationReport
from disegnatore_mep.validation.preflight import preflight_drawing
from disegnatore_mep.validation.topology import validate_project

SEVERITY_LABELS: dict[IssueSeverity, str] = {
    IssueSeverity.BLOCKING: "Bloccanti",
    IssueSeverity.APPROVAL: "Da approvare",
    IssueSeverity.WARNING: "Avvisi",
}
"""Le tre classi di esito della §13, in ordine di gravita' e in italiano (D-068)."""

VERIFY_MARK = "MODALITÀ VERIFICA"
"""Come si riconosce a colpo d'occhio una tavola che non e' una consegna.

Sta nell'intestazione, dove il progettista la vede prima del disegno: una tavola
con gli indirizzi addosso non e' quella che va in cantiere, e confonderle
costerebbe piu' di quanto la verifica faccia risparmiare (D-110)."""


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

    rules = commands.add_parser("rules")
    rules.add_argument("project", type=Path)
    rules.add_argument("--catalog", type=Path, required=True)
    rules.add_argument("--symbols", type=Path, required=True)
    rules.add_argument("--rules", type=Path, required=True)
    # Le tabelle delle famiglie e dei fluidi. Sono un dato come il catalogo e le
    # regole, e come loro si passano: un punto aperto si dice in italiano, e le
    # parole per dirlo si leggono da li'.
    rules.add_argument("--naming", type=Path, required=True)
    rules.add_argument(
        "--apply-all",
        action="store_true",
        help=(
            "applica tutte le proposte senza chiederlo. Non e' l'approvazione "
            "dell'ingegnere, che vive nella conversazione: e' la scorciatoia per lo "
            "sviluppo e per i casi di prova"
        ),
    )
    rules.add_argument("--out", type=Path)

    draw = commands.add_parser("draw")
    draw.add_argument("project", type=Path)
    draw.add_argument("--catalog", type=Path, required=True)
    draw.add_argument("--symbols", type=Path, required=True)
    draw.add_argument("--out", type=Path, required=True)
    draw.add_argument("--geometry", type=Path)
    # Le tabelle dei nomi servono solo alla modalita' verifica, che stampa gli
    # indirizzi dei nodi: senza indirizzi la tavola e' quella di consegna e le
    # tabelle non le legge nessuno.
    draw.add_argument("--naming", type=Path)
    draw.add_argument(
        "--verifica",
        action="store_true",
        help=(
            "modalita' verifica (D-110): stampa accanto a ogni pezzo il suo "
            "indirizzo, cosi' il progettista punta un pezzo sul disegno e lo "
            "cerca sul grafo. La tavola esce **anche con rilievi bloccanti**, "
            "marcata come tale: serve a guardare, non a consegnare"
        ),
    )
    return parser


def _rules(args: argparse.Namespace) -> int:
    """Propone le integrazioni. Senza `--apply-all` non tocca niente."""
    project = load_project(args.project)
    symbols = SymbolRegistry.from_directory(args.symbols)
    catalog = ComponentRegistry.from_directory(args.catalog, symbols=symbols)
    registry = RuleRegistry.from_directory(args.rules)
    registry.cross_check(catalog)
    naming = Naming.from_directory(args.naming)

    # Si valuta a saturazione anche solo per elencare: cio' che si vede e' cio'
    # che si otterrebbe applicando. Una passata sola mostrerebbe gli accessori e
    # non i loro organi di chiusura, che pure servono.
    completed, proposals, gaps = saturate(project, catalog, registry)
    report = build_report(proposals, gaps, naming)
    for category, label in CATEGORY_LABELS.items():
        entries = report.of(category)
        if not entries:
            continue
        print(f"\n{label}")
        for entry in entries:
            print(f"  - {entry.name} — {entry.where}")
            print(f"    {entry.rationale}")
            print(f"    fonte: {entry.source} · regola: {entry.rule}")
    if report.open_points:
        # Stampati sempre, anche quando tutto il resto e' a posto: un accessorio
        # che non si puo' proporre e' una domanda al progettista, e una domanda
        # che nessuno legge non e' stata fatta.
        print("\nPunti aperti — accessori che servirebbero e che non possiamo proporre")
        for point in report.open_points:
            print(f"  - {point.name} — {point.where}")
            print(f"    {point.what_is_missing}")
            print(f"    perche' servirebbe: {point.rationale}")
            print(f"    fonte: {point.source} · regola: {point.rule}")
    if report.is_empty:
        print("Nessuna integrazione da proporre: il modello e' gia' completo.")

    if not args.apply_all:
        return 0
    if args.out is None:
        print("--apply-all richiede --out: il modello completato va scritto da qualche parte")
        return 1
    verdict = validate_project(completed, catalog)
    if not verdict.ok:
        print(verdict.model_dump_json(indent=2))
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(canonical_json(completed), encoding="utf-8")
    print(f"\nScritte {len(proposals)} integrazioni in {args.out}")
    return 0


def _print_preflight(findings: list[ValidationIssue]) -> None:
    """Le misure di qualita' raggruppate per severita', in italiano (D-068).

    Si stampano anche quando nessuna blocca: un avviso che nessuno legge non
    misura niente, ed e' il modo in cui la tavola del 5 agosto e' uscita.
    """
    if not findings:
        print("\nPreflight di qualita': nessun rilievo.")
        return
    print("\nPreflight di qualita'")
    for severity, title in SEVERITY_LABELS.items():
        group = [item for item in findings if item.severity == severity]
        if not group:
            continue
        print(f"\n{title}")
        for item in group:
            print(f"  - {item.message}")
            print(f"    codice: {item.code} · {', '.join(item.entity_ids)}")


def _with_addresses(
    drawing: DrawingGeometry,
    project: ProjectModel,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    naming_dir: Path,
) -> DrawingGeometry:
    """La stessa tavola, con l'indirizzo di ogni nodo scritto accanto (D-110).

    Le etichette si posano **sopra una tavola gia' finita** e non spostano
    niente: le due modalita' danno percio' la stessa identica tavola, una con un
    velo in piu'. E' il punto della decisione, e va tenuto vero: cio' che il
    progettista verifica dev'essere esattamente cio' che gli viene consegnato.
    """
    lines = read_lines(
        project,
        catalog,
        read_plant(project, catalog, Naming.from_directory(naming_dir)),
        LineNaming.from_directory(naming_dir),
    )
    sheets = []
    for sheet in drawing.sheets:
        sheets.append(
            sheet.model_copy(
                update={
                    "title": f"{sheet.title} · {VERIFY_MARK}",
                    "labels": [
                        *sheet.labels,
                        *place_addresses(
                            sheet.symbols,
                            lines.addresses,
                            frame.standard,
                            routes=sheet.routes,
                            already=sheet.labels,
                            floor_y_mm=sheet.ground_line_y_mm,
                        ),
                    ],
                }
            )
        )
    return drawing.model_copy(update={"sheets": sheets})


def _draw(args: argparse.Namespace) -> int:
    """Compone e scrive una tavola SVG per foglio.

    Due verifiche, in quest'ordine: quella di **correttezza**, che dice se la
    tavola sta in piedi, e il **preflight di qualita'** (D-063, livello 1), che
    dice se e' disegnata bene. Nessuna delle due vive nei test: girano qui,
    dentro il comando, ed e' la ragione per cui esistono.

    Codici di uscita coerenti col resto della CLI: `0` disegno prodotto, `2`
    errori bloccanti — di correttezza o di qualita' —, `1` errori di
    caricamento. La tavola esce marcata come bozza finche' il cartiglio non e'
    compilato (D-025).

    **In modalita' verifica il cancello di qualita' non blocca la scrittura.**
    Non e' un'eccezione a D-063, che vale per la **consegna**: una tavola che il
    progettista guarda per trovarci gli errori deve poter uscire proprio quando
    ne ha, altrimenti gli errori nessuno li vede. Il foglio esce marcato, e i
    rilievi restano stampati per intero.
    """
    project = load_project(args.project)
    symbols = SymbolRegistry.from_directory(args.symbols)
    catalog = ComponentRegistry.from_directory(args.catalog, symbols=symbols)
    if args.verifica and args.naming is None:
        print(
            "--verifica richiede --naming: l'indirizzo di un nodo si scrive con "
            "le tabelle delle famiglie di linea, che sono un dato come il catalogo"
        )
        return 1

    report = validate_project(project, catalog)
    if not report.ok:
        print(report.model_dump_json(indent=2))
        return 2

    frame, drawing = compose_on_ordinary_frame(project, catalog)
    geometry_report = validate_drawing_geometry(drawing, frame)
    if not geometry_report.ok:
        print(geometry_report.model_dump_json(indent=2))
        return 2

    quality = preflight_drawing(drawing, frame, catalog)
    _print_preflight(quality)
    blocked = not ValidationReport(issues=quality).ok
    if blocked and not args.verifica:
        print(
            "\nLa tavola non viene scritta: una tavola finale non esce con un "
            "rilievo bloccante (D-063)."
        )
        return 2

    if args.verifica:
        drawing = _with_addresses(drawing, project, catalog, frame, args.naming)

    args.out.mkdir(parents=True, exist_ok=True)
    for sheet in drawing.sheets:
        target = args.out / f"{project.metadata.project_id}-{sheet.sheet_id}.svg"
        target.write_text(render_sheet(sheet, frame, symbols), encoding="utf-8")
    if args.geometry:
        args.geometry.write_text(
            drawing.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
    print(drawing_fingerprint(drawing))
    if blocked:
        print(
            f"\nFoglio scritto in {VERIFY_MARK.lower()}, con i rilievi qui sopra "
            f"ancora aperti: si guarda, non si consegna (D-063)."
        )
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
        if args.command == "rules":
            return _rules(args)
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
    # qui era ridondante e insegnava una gerarchia sbagliata. `RuleError` invece
    # discende da Exception e va nominata.
    except (OSError, ValidationError, ValueError, RuleError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
