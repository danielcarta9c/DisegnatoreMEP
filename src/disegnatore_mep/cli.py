import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    rilievi_del_cartiglio,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet, stati_della_tavola
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.io.canonical import canonical_json, project_fingerprint
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.addresses import VERIFY_MARK, with_addresses
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
from disegnatore_mep.layout.geometry import SheetGeometry, drawing_fingerprint
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.revisore import TETTO_DEI_GIRI, revisiona
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.report import CATEGORY_LABELS, build_report
from disegnatore_mep.validation.geometry import validate_drawing_geometry
from disegnatore_mep.validation.issues import ValidationIssue, ValidationReport
from disegnatore_mep.validation.preflight import preflight_drawing
from disegnatore_mep.validation.regole import rilievi_delle_regole
from disegnatore_mep.validation.topology import validate_project

SEVERITY_LABELS: dict[IssueSeverity, str] = {
    IssueSeverity.BLOCKING: "Bloccanti",
    IssueSeverity.APPROVAL: "Da approvare",
    IssueSeverity.WARNING: "Avvisi",
}
"""Le tre classi di esito della §13, in ordine di gravita' e in italiano (D-068)."""

_with_addresses = with_addresses
"""Il velo degli indirizzi vive in `layout.addresses` (DRAW-005, I-030): e' la
sola opzione esplicita che porta gli indirizzi in tavola, e nessuna modalita'
tocca posa o routing. Il nome di prima resta per chi lo importava da qui."""

CARTIGLIO_HELP = (
    "il modello del cartiglio Nove C, assets/cartigli/Cartiglio_NoveC_A3.json "
    "(REL-002): la tavola esce con il cartiglio compilato coi dati del progetto. "
    "Senza, esce con la riserva vuota e la scritta di bozza (D-025)"
)


def _cartiglio(
    project: ProjectModel,
    cartiglio: Cartiglio | None,
    sheet: SheetGeometry,
    frame: SheetFrame,
) -> CartiglioDellaTavola | None:
    """Il cartiglio di una tavola, e quello che c'e' da dirne.

    Un campo da definire o un testo che non entra non fermano la tavola: la
    tavola esce **in bozza**, marcata in testata, e il comando lo dice (D-025)."""
    if cartiglio is None:
        return None
    tavola = CartiglioDellaTavola(
        cartiglio=cartiglio, valori=valori_del_cartiglio(project, sheet.sheet_id)
    )
    for rilievo in rilievi_del_cartiglio(tavola, frame, stati_della_tavola(sheet)):
        print(f"Cartiglio della tavola {sheet.sheet_id}: {rilievo}")
    return tavola


def _carica_cartiglio(args: argparse.Namespace) -> Cartiglio | None:
    path: Path | None = getattr(args, "cartiglio", None)
    return None if path is None else Cartiglio.da_file(path)


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
    draw.add_argument("--cartiglio", type=Path, help=CARTIGLIO_HELP)
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

    # **Il piano di composizione** (D-151, DRAW-015): il disegno non lo cerca un
    # solutore, lo compone il pianificatore e questo comando lo esegue. Prende
    # un progetto gia' completo — l'uscita di `rules --apply-all` — e il piano
    # che dice dove stanno i pezzi.
    piano = commands.add_parser("piano")
    piano.add_argument("project", type=Path)
    piano.add_argument("--piano", type=Path, required=True)
    piano.add_argument("--catalog", type=Path, required=True)
    piano.add_argument("--symbols", type=Path, required=True)
    # Qui `--naming` non e' opzionale come in `draw`: un piano si esegue **per
    # guardarlo**, e la tavola esce con gli indirizzi dei nodi (D-110). E' la
    # scelta con cui sono uscite le due tavole della prova.
    piano.add_argument("--naming", type=Path, required=True)
    piano.add_argument("--out", type=Path, required=True)
    piano.add_argument("--geometry", type=Path)
    piano.add_argument("--cartiglio", type=Path, help=CARTIGLIO_HELP)
    piano.add_argument(
        "--verifica",
        action="store_true",
        help=(
            "modalita' verifica (D-110): stampa accanto a ogni pezzo il suo "
            "indirizzo. Senza, la tavola e' quella di consegna — ed e' quella "
            "che il PO guarda per giudicare il disegno (D-146)"
        ),
    )

    # **Il revisore** (D-153, DRAW-015): esegue il piano, legge i rilievi,
    # corregge il piano e rifa' girare, finche' non resta niente da correggere
    # o finche' un giro non migliora. Ogni correzione porta il nome della
    # regola che la motiva.
    revisore = commands.add_parser("revisiona")
    revisore.add_argument("project", type=Path)
    revisore.add_argument("--piano", type=Path, required=True)
    revisore.add_argument("--catalog", type=Path, required=True)
    revisore.add_argument("--symbols", type=Path, required=True)
    revisore.add_argument("--naming", type=Path, required=True)
    revisore.add_argument("--out", type=Path, required=True)
    revisore.add_argument("--cartiglio", type=Path, help=CARTIGLIO_HELP)
    revisore.add_argument(
        "--tetto",
        type=int,
        default=TETTO_DEI_GIRI,
        help="quanti giri al piu' prima di fermarsi e dirlo",
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


def _print_regole(findings: list[ValidationIssue]) -> None:
    """Le regole del piano misurate, che si leggono accanto al preflight.

    Sono **cinque**: le quattro dettate dal PO il 20 settembre (**D-154**) piu'
    **A4**, aggiunta guardando le tavole — `ORDINE_DELLE_REGOLE` le tiene in
    ordine, e questa funzione non ne conosce l'elenco.

    **Non si sommano ai rilievi del preflight e non ne cambiano il verdetto**:
    il preflight dice se la tavola e' consegnabile (D-063), questo dice se il
    **piano** e' fatto secondo le regole. Una violazione qui e' lavoro per il
    revisore, non un motivo per non scrivere la tavola.
    """
    if not findings:
        print("\nLe regole del piano (D-154): nessuna violazione.")
        return
    print("\nLe regole del piano (D-154)")
    for item in findings:
        print(f"  - {item.message}")
        print(f"    codice: {item.code} · {', '.join(item.entity_ids)}")


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
    # **Una tavola che si dichiara incompleta non si misura come una completa**
    # (D-150). Quando il motore ha dovuto cedere una tratta, la sua spezzata di
    # ripiego passa sotto i simboli e si sovrappone: sono esattamente i difetti
    # che questo controllo esiste per fermare, e fermarli qui vorrebbe dire
    # rimettere la tavola nel cassetto da cui D-150 l'ha tirata fuori.
    #
    # Il contratto non si allenta, si sposta: i rilievi **si stampano per
    # intero**, la tavola resta bloccata, e in `--verifica` esce marcata come
    # esce marcata per qualunque altro rilievo bloccante (D-063). Per una
    # tavola **senza** tratte cedute non cambia niente: il controllo la ferma
    # come l'ha sempre fermata.
    surrendered = [
        route
        for sheet in drawing.sheets
        for route in sheet.routes
        if route.unresolved
    ]
    geometry_report = validate_drawing_geometry(drawing, frame)
    if not geometry_report.ok:
        print(geometry_report.model_dump_json(indent=2))
        if not (surrendered and args.verifica):
            return 2
        print(
            f"\nI rilievi qui sopra si leggono sapendo che {len(surrendered)} "
            f"tratta/e non si e' instradata e porta un segno di ripiego (D-150): "
            f"la tavola esce per essere guardata, non per essere consegnata."
        )

    # Il modello si passa: e' cosi' che la piega di un'autostrada si misura col
    # proprio metro e non con quello di uno stacchetto (DRAW-015, D-151).
    quality = preflight_drawing(drawing, frame, catalog, project)
    _print_preflight(quality)
    blocked = not ValidationReport(issues=quality).ok or not geometry_report.ok
    if blocked and not args.verifica:
        print(
            "\nLa tavola non viene scritta: una tavola finale non esce con un "
            "rilievo bloccante (D-063)."
        )
        return 2

    if args.verifica:
        drawing = with_addresses(drawing, project, catalog, frame, args.naming)

    args.out.mkdir(parents=True, exist_ok=True)
    cartiglio = _carica_cartiglio(args)
    for sheet in drawing.sheets:
        target = args.out / f"{project.metadata.project_id}-{sheet.sheet_id}.svg"
        tavola = _cartiglio(project, cartiglio, sheet, frame)
        target.write_text(render_sheet(sheet, frame, symbols, tavola), encoding="utf-8")
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


def _piano(args: argparse.Namespace) -> int:
    """Esegue un **piano di composizione** e scrive la tavola che ne esce.

    E' il passo 4-5 della catena (`ARCHITETTURA-DEL-PIANO.md`): il
    pianificatore ha composto, il motore esegue e misura. **Non gira nessuna
    ricerca** — ne' la fase del tronco ne' il ciclo di miglioramento — ed e'
    questo il punto di D-151.

    Stampa, nell'ordine: i pezzi che la deduzione ha girato, i rilievi
    raggruppati per severita' come li stampa `draw`, e in fondo le due misure su
    cui si giudica una tavola composta — **le tratte cedute** (D-150) e **i
    rilievi bloccanti** (D-063).

    Codici di uscita coerenti col resto della CLI: `0` tavola scritta, `2`
    rilievi bloccanti o piano che non si instrada, `1` errore di caricamento —
    compreso un piano malformato, che esce come **messaggio** e non come traccia
    di stack (criterio 10).

    **La tavola esce anche con rilievi bloccanti, e il comando torna 2.** Non e'
    un'eccezione a D-063: un piano si esegue per **guardarlo**, la sua tavola
    porta gia' il velo degli indirizzi (D-110) e quindi e' per costruzione una
    tavola di verifica. Una tavola difettosa che non esce non si puo' correggere,
    ed e' il difetto che D-150 e D-146 esistono per non ripetere.
    """
    modello = load_project(args.project)
    simboli = SymbolRegistry.from_directory(args.symbols)
    catalogo = ComponentRegistry.from_directory(args.catalog, symbols=simboli)
    piano = carica_piano(args.piano)

    esito = esegui_piano(
        modello, piano, catalogo, simboli, args.naming, verifica=args.verifica
    )

    if esito.girati:
        print("\nGirati dalla deduzione (C2)")
        for riga in esito.girati:
            print(f"  - {riga}")

    if esito.disegno is None:
        print(f"\nIl piano non si instrada: {esito.errore}")
        # **La diagnostica utile e' dove sono finiti i pezzi**, non il
        # messaggio: chi compone deve poter vedere che cosa ha lasciato in
        # mezzo, e correggere il piano invece di indovinare.
        print("\nPosa applicata (i pezzi del piano sono marcati con *)")
        for item in sorted(esito.posa, key=lambda i: (i.origin.x_mm, i.origin.y_mm)):
            segno = "*" if item.component_id in piano.pezzi else " "
            print(
                f"  {segno} {item.component_id:46} "
                f"{item.width_mm:5.1f}x{item.height_mm:5.1f} "
                f"@({item.origin.x_mm:6.1f},{item.origin.y_mm:6.1f})"
            )
        return 2

    _print_preflight(esito.rilievi)
    _print_regole(rilievi_delle_regole(esito.disegno, esito.frame, catalogo, modello))

    args.out.mkdir(parents=True, exist_ok=True)
    cartiglio = _carica_cartiglio(args)
    for foglio in esito.disegno.sheets:
        target = args.out / f"{modello.metadata.project_id}-{foglio.sheet_id}.svg"
        tavola = _cartiglio(modello, cartiglio, foglio, esito.frame)
        target.write_text(
            render_sheet(foglio, esito.frame, simboli, tavola), encoding="utf-8"
        )
        print(f"\nTavola scritta: {target}")
    if args.geometry:
        args.geometry.parent.mkdir(parents=True, exist_ok=True)
        args.geometry.write_text(
            esito.disegno.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        print(f"Geometria scritta: {args.geometry}")

    bloccanti = esito.bloccanti
    print(
        f"\nTratte cedute: {len(esito.cedute)} · rilievi bloccanti: {len(bloccanti)}"
    )
    if bloccanti:
        print(
            f"\nFoglio scritto in {VERIFY_MARK.lower()}, con i rilievi qui sopra "
            f"ancora aperti: si guarda, non si consegna (D-063)."
        )
        return 2
    return 0


def _revisiona(args: argparse.Namespace) -> int:
    """L'anello chiuso: esegui, misura, correggi il piano, rifai girare (D-153).

    Scrive **una tavola per giro** — cosi' il prima e il dopo si guardano
    accanto, che e' il controllo del PO (D-146) — piu' il **piano corretto**,
    che e' il vero prodotto del revisore.

    Stampa, per ogni giro: le sei misure, i rilievi, e **le correzioni con il
    nome della regola che le motiva**. In fondo dice **perche' si e' fermato** e
    quanti giri sono serviti. Se un giro peggiora, si consegna il precedente e
    le misure peggiorate si nominano: il revisore non peggiora in silenzio.

    Codici di uscita: `0` la revisione si chiude senza rilievi da correggere,
    `2` resta qualcosa (bloccanti, tratte cedute o regole violate), `1` errore
    di caricamento.
    """
    modello = load_project(args.project)
    simboli = SymbolRegistry.from_directory(args.symbols)
    catalogo = ComponentRegistry.from_directory(args.catalog, symbols=simboli)
    piano = carica_piano(args.piano)

    esito = revisiona(
        modello, piano, catalogo, simboli, args.naming, tetto=args.tetto
    )
    args.out.mkdir(parents=True, exist_ok=True)
    cartiglio = _carica_cartiglio(args)

    for giro in esito.giri:
        print(f"\n— giro {giro.numero}: {giro.punteggio.racconto()}")
        if giro.scambio:
            print(
                "  scambio — chiuso un difetto al prezzo di "
                + ", ".join(giro.scambio)
            )
        for rilievo in giro.rilievi:
            print(f"  [{rilievo.severity.value:8}] {rilievo.code}: {rilievo.message}")
        for correzione in giro.correzioni:
            print(f"  > {correzione.racconto()}")
        if giro.esito.disegno is None:
            print(f"  nessuna tavola: {giro.esito.errore}")
            continue
        for foglio in giro.esito.disegno.sheets:
            target = (
                args.out
                / f"{modello.metadata.project_id}-{foglio.sheet_id}-giro{giro.numero}.svg"
            )
            tavola = _cartiglio(modello, cartiglio, foglio, giro.esito.frame)
            target.write_text(
                render_sheet(foglio, giro.esito.frame, simboli, tavola), encoding="utf-8"
            )
            print(f"  tavola: {target}")

    corretto = args.out / f"{args.piano.stem}-rivisto.json"
    corretto.write_text(
        esito.piano_finale.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )

    print(f"\nSi e' fermato perche': {esito.perche_si_e_fermato}")
    print(
        f"Giri di revisione serviti: {esito.giri_serviti} "
        f"(su {len(esito.giri) - 1} provati) · ha migliorato: "
        f"{'si' if esito.ha_migliorato else 'no'}"
    )
    if esito.non_curati:
        print(
            "Rilievi per cui il revisore non ha una cura, e restano a chi compone: "
            + ", ".join(esito.non_curati)
        )
    print(f"Piano rivisto: {corretto}")
    return 0 if esito.giro_migliore.punteggio.chiuso else 2


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
        if args.command == "piano":
            return _piano(args)
        if args.command == "revisiona":
            return _revisiona(args)
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
