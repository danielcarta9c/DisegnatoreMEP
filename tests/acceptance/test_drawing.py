"""Il gate della fase: il caso D-011 disegnato end-to-end.

I controlli automatici dimostrano che nulla si sovrappone, non che il disegno
si legga: quella risposta la danno solo l'occhio e la stampa (§12.4).
"""

import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

from _pytest.capture import CaptureFixture

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.cli import main
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import DRAFT_MARK, render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import DrawingGeometry
from disegnatore_mep.validation.geometry import validate_drawing_geometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
FOUNDATION = ROOT / "examples" / "foundation"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def drawing() -> DrawingGeometry:
    return compose_drawing(load_project(PROJECT), catalog(), NOVE_C_A3)


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
    source = two_sheet_project(tmp_path)
    out = tmp_path / "out"
    assert (
        main(
            [
                "draw", str(source), "--catalog", str(CATALOG),
                "--symbols", str(SYMBOLS), "--out", str(out),
            ]
        )
        == 0
    )
    assert len(list(out.glob("*.svg"))) == 2


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
