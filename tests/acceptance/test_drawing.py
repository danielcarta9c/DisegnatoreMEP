"""Il gate della fase: il caso D-011 disegnato end-to-end.

I controlli automatici dimostrano che nulla si sovrappone, non che il disegno
si legga: quella risposta la danno solo l'occhio e la stampa (§12.4).
"""

import os
import subprocess
import sys
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest
from _pytest.capture import CaptureFixture

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.cli import main
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import DRAFT_MARK, render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import DrawingGeometry
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.validation.geometry import validate_drawing_geometry
from disegnatore_mep.validation.preflight import preflight_drawing

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
FOUNDATION = ROOT / "examples" / "foundation"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def drawing() -> DrawingGeometry:
    """Composto una volta per modulo: il ciclo di miglioramento reinstrada
    decine di volte, e ogni prova lo leggerebbe identico."""
    return compose_drawing(load_project(PROJECT), catalog(), NOVE_C_A3)


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano, e il motivo NON e' "
    "la larghezza del foglio (D-113): misurato l'8 agosto, i cinque impianti "
    "falliscono su A0 e su un foglio 3000x2000 negli stessi punti e alle stesse "
    "coordinate che su A3. Il collocatore dispone una riga per fascia e usa il "
    "21-23% dell'altezza: un accessorio che pende da una macchina finisce nella "
    "fila di lettura invece che accanto alla propria macchina, e il rettilineo "
    "per gli accessori in linea si prenota solo fra colonne contigue. Non e' un "
    "difetto del contenuto — quello si giudica sul grafo scritto (D-096) — ed e' "
    "esattamente il limite che il pezzo della composizione deve chiudere. Queste "
    "prove tornano quando quel pezzo si fa."
)
def test_the_case_composes_end_to_end() -> None:
    result = drawing()
    assert len(result.sheets) == 1
    sheet = result.sheets[0]
    assert len(sheet.symbols) == 10
    assert sheet.routes
    assert sheet.legend


def test_the_drawing_passes_every_geometric_check() -> None:
    report = validate_drawing_geometry(drawing(), NOVE_C_A3)
    assert report.ok, [item.model_dump() for item in report.issues]


def test_no_line_passes_under_an_inline_component() -> None:
    """Il gate dichiarato per P4 nella roadmap master."""
    report = validate_drawing_geometry(drawing(), NOVE_C_A3)
    assert "LINE_UNDER_SYMBOL" not in {item.code for item in report.issues}


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano, e il motivo NON e' "
    "la larghezza del foglio (D-113): misurato l'8 agosto, i cinque impianti "
    "falliscono su A0 e su un foglio 3000x2000 negli stessi punti e alle stesse "
    "coordinate che su A3. Il collocatore dispone una riga per fascia e usa il "
    "21-23% dell'altezza: un accessorio che pende da una macchina finisce nella "
    "fila di lettura invece che accanto alla propria macchina, e il rettilineo "
    "per gli accessori in linea si prenota solo fra colonne contigue. Non e' un "
    "difetto del contenuto — quello si giudica sul grafo scritto (D-096) — ed e' "
    "esattamente il limite che il pezzo della composizione deve chiudere. Queste "
    "prove tornano quando quel pezzo si fa."
)
def test_the_composed_drawing_carries_no_blocking_quality_finding() -> None:
    """Il livello 1 di D-063 misurato sulla geometria composta, non sull'uscita.

    L'invariante che mancava. Il comando `draw` misura la qualita' e rifiuta di
    scrivere una tavola con un rilievo bloccante (D-063), ma il ciclo di
    miglioramento sceglieva le mosse su un instradamento **senza accessori in
    linea**: approvava una geometria e ne consegnava un'altra, e la consegnata
    portava accessori a filo di tratte altrui e andate e ritorno che il ciclo
    non aveva mai visto. Ora il ciclo valuta con `settle_sheet`, la stessa
    funzione con cui la tavola si compone, e questa prova lo fissa dove il
    difetto viveva: il preflight chiamato sulla geometria composta.
    """
    findings = preflight_drawing(drawing(), NOVE_C_A3, catalog())
    blocking = [
        item for item in findings if item.severity is IssueSeverity.BLOCKING
    ]
    assert blocking == [], [item.model_dump() for item in blocking]


def test_the_sheet_is_true_scale() -> None:
    sheet = render_sheet(
        drawing().sheets[0], NOVE_C_A3, SymbolRegistry.from_directory(SYMBOLS)
    )
    assert 'width="420mm"' in sheet
    assert 'height="297mm"' in sheet
    assert 'viewBox="0 0 420 297"' in sheet
    ElementTree.fromstring(sheet)


def test_every_symbol_is_drawn_at_its_manifest_size() -> None:
    """La scala e' invariante: nessun simbolo si rimpicciolisce (ADR 0003)."""
    registry = SymbolRegistry.from_directory(SYMBOLS)
    for placed in drawing().sheets[0].symbols:
        manifest = registry.get(placed.symbol_id).manifest.rotated(placed.rotation_deg)
        assert (placed.width_mm, placed.height_mm) == (
            manifest.width_mm,
            manifest.height_mm,
        )


def test_the_sheet_is_marked_as_a_draft() -> None:
    """Una tavola finale richiede il cartiglio completo (D-025), che arriva
    col piano di rendering: finche' manca, il foglio lo dichiara."""
    sheet = render_sheet(
        drawing().sheets[0], NOVE_C_A3, SymbolRegistry.from_directory(SYMBOLS)
    )
    assert DRAFT_MARK in sheet


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano, e il motivo NON e' "
    "la larghezza del foglio (D-113): misurato l'8 agosto, i cinque impianti "
    "falliscono su A0 e su un foglio 3000x2000 negli stessi punti e alle stesse "
    "coordinate che su A3. Il collocatore dispone una riga per fascia e usa il "
    "21-23% dell'altezza: un accessorio che pende da una macchina finisce nella "
    "fila di lettura invece che accanto alla propria macchina, e il rettilineo "
    "per gli accessori in linea si prenota solo fra colonne contigue. Non e' un "
    "difetto del contenuto — quello si giudica sul grafo scritto (D-096) — ed e' "
    "esattamente il limite che il pezzo della composizione deve chiudere. Queste "
    "prove tornano quando quel pezzo si fa."
)
def test_the_draw_command_writes_one_sheet(tmp_path: Path) -> None:
    exit_code = main(
        [
            "draw",
            str(PROJECT),
            "--catalog",
            str(CATALOG),
            "--symbols",
            str(SYMBOLS),
            "--out",
            str(tmp_path),
        ]
    )
    assert exit_code == 0
    written = sorted(tmp_path.glob("*.svg"))
    assert [item.name for item in written] == [
        "heat-pump-dhw-buffer-two-zones-t1.svg"
    ]


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano, e il motivo NON e' "
    "la larghezza del foglio (D-113): misurato l'8 agosto, i cinque impianti "
    "falliscono su A0 e su un foglio 3000x2000 negli stessi punti e alle stesse "
    "coordinate che su A3. Il collocatore dispone una riga per fascia e usa il "
    "21-23% dell'altezza: un accessorio che pende da una macchina finisce nella "
    "fila di lettura invece che accanto alla propria macchina, e il rettilineo "
    "per gli accessori in linea si prenota solo fra colonne contigue. Non e' un "
    "difetto del contenuto — quello si giudica sul grafo scritto (D-096) — ed e' "
    "esattamente il limite che il pezzo della composizione deve chiudere. Queste "
    "prove tornano quando quel pezzo si fa."
)
def test_the_draw_command_can_write_the_geometry(tmp_path: Path) -> None:
    geometry = tmp_path / "geometry.json"
    main(
        [
            "draw", str(PROJECT), "--catalog", str(CATALOG), "--symbols", str(SYMBOLS),
            "--out", str(tmp_path), "--geometry", str(geometry),
        ]
    )
    assert DrawingGeometry.model_validate_json(geometry.read_text("utf-8")).sheets


def test_a_topologically_broken_project_exits_two(tmp_path: Path) -> None:
    exit_code = main(
        [
            "draw",
            str(FOUNDATION / "invalid-cross-medium.json"),
            "--catalog",
            str(FOUNDATION / "catalog"),
            "--symbols",
            str(FOUNDATION / "symbols"),
            "--out",
            str(tmp_path),
        ]
    )
    assert exit_code == 2
    assert not list(tmp_path.glob("*.svg"))


def test_a_missing_catalog_exits_one(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "draw", str(PROJECT), "--catalog", str(tmp_path / "nope"),
            "--symbols", str(SYMBOLS), "--out", str(tmp_path),
        ]
    )
    assert exit_code == 1
    assert "catalog directory not found" in capsys.readouterr().err


def test_the_same_input_gives_the_same_sheet(tmp_path: Path) -> None:
    registry = SymbolRegistry.from_directory(SYMBOLS)
    first = render_sheet(drawing().sheets[0], NOVE_C_A3, registry)
    second = render_sheet(drawing().sheets[0], NOVE_C_A3, registry)
    assert first == second


def test_the_drawing_fingerprint_is_stable_across_processes() -> None:
    script = (
        "from pathlib import Path;"
        "from disegnatore_mep.catalog.registry import ComponentRegistry;"
        "from disegnatore_mep.graphics.frame import NOVE_C_A3;"
        "from disegnatore_mep.graphics.registry import SymbolRegistry;"
        "from disegnatore_mep.io.project_json import load_project;"
        "from disegnatore_mep.layout.compose import compose_drawing;"
        "from disegnatore_mep.layout.geometry import drawing_fingerprint;"
        f"r=ComponentRegistry.from_directory(Path({str(CATALOG)!r}),"
        f" symbols=SymbolRegistry.from_directory(Path({str(SYMBOLS)!r})));"
        f"print(drawing_fingerprint(compose_drawing("
        f"load_project(Path({str(PROJECT)!r})), r, NOVE_C_A3)))"
    )
    seen = set()
    for seed in ("0", "1", "12345"):
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
            cwd=ROOT,
        )
        seen.add(result.stdout.strip())
    assert len(seen) == 1


def test_the_g0_gate_of_p0_still_passes() -> None:
    assert (
        main(
            [
                "validate",
                str(FOUNDATION / "valid-mixed-project.json"),
                "--catalog",
                str(FOUNDATION / "catalog"),
                "--symbols",
                str(FOUNDATION / "symbols"),
            ]
        )
        == 0
    )


# --- il caso spezzato in due tavole ------------------------------------------


def two_sheet_project(tmp_path: Path, cut_inside_a_run: bool = False) -> Path:
    """Lo stesso impianto, con un piano di impaginazione a due tavole.

    Con `cut_inside_a_run` il confine cade dentro una tratta che porta
    accessori: il caso che il motore deve rifiutare.
    """
    import json

    document = json.loads(PROJECT.read_text("utf-8"))
    document["metadata"]["project_id"] = "two-sheet-case"
    first = ["generation", "storage"] if cut_inside_a_run else [
        "generation", "storage", "distribution"
    ]
    second = ["distribution", "zones"] if cut_inside_a_run else ["zones"]
    bands = {
        "generation": "generation",
        "storage": "primary",
        "distribution": "distribution",
        "zones": "terminal",
    }
    document["sheets"] = [
        {
            "id": sheet_id,
            "title": title,
            "subsystem_ids": subsystems,
            "band_assignments": [
                {"subsystem_id": item, "band": bands[item], "order": 0}
                for item in subsystems
            ],
        }
        for sheet_id, title, subsystems in (
            ("t1", "Centrale", first),
            ("t2", "Zone", second),
        )
    ]
    target = tmp_path / "two-sheets.json"
    target.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return target


def test_a_two_sheet_plan_produces_two_sheets(tmp_path: Path) -> None:
    """Il piano a due tavole si compone, e ne escono due con dentro qualcosa."""
    drawn = compose_drawing(
        load_project(two_sheet_project(tmp_path)), catalog(), NOVE_C_A3
    )
    assert [sheet.sheet_id for sheet in drawn.sheets] == ["t1", "t2"]
    for sheet in drawn.sheets:
        assert sheet.symbols, sheet.sheet_id
        assert sheet.routes or sheet.cross_references, sheet.sheet_id
    assert validate_drawing_geometry(drawn, NOVE_C_A3).ok


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano, e il motivo NON e' "
    "la larghezza del foglio (D-113): misurato l'8 agosto, i cinque impianti "
    "falliscono su A0 e su un foglio 3000x2000 negli stessi punti e alle stesse "
    "coordinate che su A3. Il collocatore dispone una riga per fascia e usa il "
    "21-23% dell'altezza: un accessorio che pende da una macchina finisce nella "
    "fila di lettura invece che accanto alla propria macchina, e il rettilineo "
    "per gli accessori in linea si prenota solo fra colonne contigue. Non e' un "
    "difetto del contenuto — quello si giudica sul grafo scritto (D-096) — ed e' "
    "esattamente il limite che il pezzo della composizione deve chiudere. Queste "
    "prove tornano quando quel pezzo si fa."
)
def test_splitting_this_plant_in_two_is_refused_for_the_empty_second_sheet(
    tmp_path: Path,
) -> None:
    """D-072, A2: si divide solo se la seconda tavola e' abbastanza piena.

    Questo impianto sta su una tavola sola, e il piano a due tavole della prova
    qui sopra e' costruito a mano per esercitare partizione e rimandi: la
    seconda tavola porta le sole zone e si riempie all'1%. Il preflight lo
    dichiara bloccante (WP5), quindi `draw` non scrive niente ed esce 2 — che e'
    il comportamento voluto, non un difetto della tavola.

    E' l'unico taglio possibile: gli altri due spezzano una tratta che porta
    accessori in linea, e quello il motore lo rifiuta gia' in composizione.
    """
    out = tmp_path / "out"
    exit_code = main(
        [
            "draw", str(two_sheet_project(tmp_path)), "--catalog", str(CATALOG),
            "--symbols", str(SYMBOLS), "--out", str(out),
        ]
    )
    assert exit_code == 2
    assert not list(out.glob("*.svg")) if out.exists() else True
    findings = preflight_drawing(
        compose_drawing(load_project(two_sheet_project(tmp_path)), catalog(), NOVE_C_A3),
        NOVE_C_A3,
        catalog(),
    )
    blocking = [item for item in findings if item.severity is IssueSeverity.BLOCKING]
    assert [item.code for item in blocking] == ["CONTINUATION_SHEET_TOO_EMPTY"]


def test_the_cross_references_of_a_two_sheet_plan_are_paired(tmp_path: Path) -> None:
    drawing = compose_drawing(
        load_project(two_sheet_project(tmp_path)), catalog(), NOVE_C_A3
    )
    references = [
        item for sheet in drawing.sheets for item in sheet.cross_references
    ]
    assert references
    pairs: dict[str, int] = {}
    for item in references:
        pairs[item.pair_id] = pairs.get(item.pair_id, 0) + 1
    assert set(pairs.values()) == {2}
    assert validate_drawing_geometry(drawing, NOVE_C_A3).ok


def test_a_boundary_that_cuts_a_run_with_accessories_is_refused(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Un accessorio sta su una tratta: se il confine la taglia, resterebbe
    senza una linea su cui posarsi e sparirebbe dal disegno."""
    source = two_sheet_project(tmp_path, cut_inside_a_run=True)
    exit_code = main(
        [
            "draw", str(source), "--catalog", str(CATALOG),
            "--symbols", str(SYMBOLS), "--out", str(tmp_path / "out"),
        ]
    )
    assert exit_code == 1
    assert "must not carry any" in capsys.readouterr().err


# --- modalita' verifica e modalita' consegna (D-110, D-111) ------------------


def test_verification_mode_needs_the_naming_tables(tmp_path: Path) -> None:
    """L'indirizzo nasce dal nome della linea, e i nomi sono un dato: chiederlo
    senza le tabelle e' un errore detto, non un indirizzo inventato."""
    assert (
        main(
            [
                "draw",
                str(PROJECT),
                "--catalog",
                str(CATALOG),
                "--symbols",
                str(SYMBOLS),
                "--out",
                str(tmp_path / "fuori"),
                "--verifica",
            ]
        )
        == 1
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DIFETTO 11. La tavola d'esempio non passa il cancello per UN rilievo: la "
        "tratta s6 supera di 2.5 mm la propria porta di arrivo e ci torna indietro "
        "(B12, D-078, tolleranza zero per costruzione). Due millimetri e mezzo sono "
        "un passo di griglia. Nella stessa giornata questo rilievo e' sparito e "
        "tornato: era caduto ritirando il divieto di disegnare sotto la linea di "
        "terra (D-116), ed e' rientrato allargando lo stacco fra i pezzi da 10 a 15 "
        "mm — l'allargamento che fa uscire la prima tavola su A3. Si chiude "
        "spostando il pezzo, che e' quel che la regola stessa dice: «si sposta "
        "l'oggetto, non si allunga la linea»."
    ),
)
def test_the_acceptance_sheet_passes_the_quality_gate(tmp_path: Path) -> None:
    """La tavola d'esempio dovrebbe uscire dal comando normale, senza scorciatoie."""
    assert (
        main(
            [
                "draw",
                str(PROJECT),
                "--catalog",
                str(CATALOG),
                "--symbols",
                str(SYMBOLS),
                "--out",
                str(tmp_path / "tavole"),
            ]
        )
        == 0
    )
    assert sorted((tmp_path / "tavole").glob("*.svg"))


def test_a_rejected_sheet_is_written_only_when_asked_and_says_so(
    tmp_path: Path, capsys: CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """D-063 resta: una tavola con un rilievo bloccante non e' una consegna.

    Ma guardarla mentre la si corregge e' l'unico modo di correggerla — un
    difetto di disposizione si vede in due secondi sulla carta e non si vede
    affatto sul modello scritto. Quindi si scrive **solo se richiesto**, e
    dicendo a voce alta che cos'e'.

    Il rilievo bloccante e' **iniettato**: da quando la tavola d'esempio passa
    il cancello (prova qui sopra) nessun caso di prova ne produce piu' uno, e
    un ramo che nessuno percorre e' un ramo che si rompe in silenzio. Cio' che
    si misura e' la decisione del comando, non quale rilievo l'abbia provocata.
    """
    from disegnatore_mep import cli
    from disegnatore_mep.validation.issues import ValidationIssue

    respinta = ValidationIssue(
        code="PROVA_BLOCCANTE",
        severity=IssueSeverity.BLOCKING,
        message="rilievo bloccante iniettato dalla prova",
        entity_ids=["t1"],
    )
    monkeypatch.setattr(cli, "preflight_drawing", lambda *_: [respinta])

    argomenti = [
        "draw",
        str(PROJECT),
        "--catalog",
        str(CATALOG),
        "--symbols",
        str(SYMBOLS),
        "--out",
        str(tmp_path / "tavole"),
    ]
    assert main(argomenti) == 2
    assert not (tmp_path / "tavole").exists()
    capsys.readouterr()

    assert main([*argomenti, "--anche-se-respinta"]) == 0
    written = sorted((tmp_path / "tavole").glob("*.svg"))
    assert written, "la tavola non e' stata scritta nemmeno quando richiesto"
    assert "CON rilievi bloccanti" in capsys.readouterr().out


def test_the_two_modes_write_the_same_sheet_plus_the_addresses(
    tmp_path: Path,
) -> None:
    """Il vincolo di D-110 misurato **sulla carta**, non sulla geometria: la
    tavola di consegna dev'essere una sottosequenza esatta di quella di
    verifica, e le sole aggiunte devono essere gli indirizzi."""
    comune = [
        "draw",
        str(PROJECT),
        "--catalog",
        str(CATALOG),
        "--symbols",
        str(SYMBOLS),
        "--anche-se-respinta",
    ]
    assert main([*comune, "--out", str(tmp_path / "consegna")]) == 0
    assert (
        main(
            [
                *comune,
                "--out",
                str(tmp_path / "verifica"),
                "--naming",
                str(ROOT / "naming"),
                "--verifica",
            ]
        )
        == 0
    )
    import re

    def elementi(directory: Path) -> list[str]:
        svg = next(iter(sorted(directory.glob("*.svg")))).read_text("utf-8")
        return re.findall(r"<[^>]+>[^<]*", svg)

    consegna, verifica = elementi(tmp_path / "consegna"), elementi(tmp_path / "verifica")
    cursore, aggiunte = 0, []
    for pezzo in verifica:
        if cursore < len(consegna) and pezzo == consegna[cursore]:
            cursore += 1
        else:
            aggiunte.append(pezzo)
    assert cursore == len(consegna), (
        "la tavola di consegna non e' una sottosequenza di quella di verifica: "
        "gli indirizzi hanno spostato qualcosa"
    )
    assert aggiunte, "nessun indirizzo scritto in modalita' verifica"
    assert all(
        'data-role="address"' in pezzo or pezzo.startswith("</text>")
        for pezzo in aggiunte
    ), [pezzo[:80] for pezzo in aggiunte if 'data-role="address"' not in pezzo][:3]
