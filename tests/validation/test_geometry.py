"""Ogni controllo geometrico della §12.2, col caso che passa e quello che cade."""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import (
    CrossReference,
    DrawingGeometry,
    LegendEntry,
    PlacedLabel,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.validation.geometry import validate_drawing_geometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def good() -> DrawingGeometry:
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    return compose_drawing(load_project(PROJECT), registry, NOVE_C_A3)


def codes(drawing: DrawingGeometry) -> set[str]:
    return {item.code for item in validate_drawing_geometry(drawing, NOVE_C_A3).issues}


def symbol(component_id: str, x_mm: float, y_mm: float) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id="valve-isolation",
        rotation_deg=0,
        origin=Point(x_mm=x_mm, y_mm=y_mm),
        width_mm=7.5,
        height_mm=5.0,
    )


def sheet(**overrides: object) -> SheetGeometry:
    payload: dict[str, object] = {"sheet_id": "t1", "title": "Prova"}
    payload.update(overrides)
    return SheetGeometry.model_validate(payload)


def one(sheet_geometry: SheetGeometry) -> DrawingGeometry:
    return DrawingGeometry(project_id="probe", sheets=[sheet_geometry])


def test_the_real_case_is_clean() -> None:
    assert validate_drawing_geometry(good(), NOVE_C_A3).ok


def test_a_symbol_outside_the_drawing_area_is_caught() -> None:
    assert "SYMBOL_OUTSIDE_DRAWING_AREA" in codes(
        one(sheet(symbols=[symbol("stray", 400.0, 20.0)]))
    )


def test_two_overlapping_symbols_are_caught() -> None:
    assert "SYMBOL_OVERLAP" in codes(
        one(sheet(symbols=[symbol("a", 20.0, 20.0), symbol("b", 22.0, 21.0)]))
    )


def test_two_symbols_that_only_touch_are_accepted() -> None:
    assert "SYMBOL_OVERLAP" not in codes(
        one(sheet(symbols=[symbol("a", 20.0, 20.0), symbol("b", 27.5, 20.0)]))
    )


def test_a_diagonal_segment_is_caught() -> None:
    assert "SEGMENT_NOT_ORTHOGONAL" in codes(
        one(
            sheet(
                routes=[
                    RoutedTrunk(
                        network_id="n",
                        connection_ids=["c1"],
                        segments=[[Point(x_mm=20.0, y_mm=20.0), Point(x_mm=40.0, y_mm=40.0)]],
                    )
                ]
            )
        )
    )


def test_a_line_running_under_a_symbol_is_caught() -> None:
    assert "LINE_UNDER_SYMBOL" in codes(
        one(
            sheet(
                symbols=[symbol("valve", 20.0, 20.0)],
                routes=[
                    RoutedTrunk(
                        network_id="n",
                        connection_ids=["c1"],
                        segments=[
                            [Point(x_mm=21.0, y_mm=22.5), Point(x_mm=26.0, y_mm=22.5)]
                        ],
                    )
                ],
            )
        )
    )


def test_a_label_on_top_of_a_symbol_is_caught() -> None:
    assert "LABEL_COLLISION" in codes(
        one(
            sheet(
                symbols=[symbol("valve", 20.0, 20.0)],
                labels=[
                    PlacedLabel(
                        id="clash",
                        text="VI-01",
                        role="tag",
                        anchor=Point(x_mm=21.0, y_mm=24.0),
                    )
                ],
            )
        )
    )


def test_a_legend_entry_outside_its_band_is_caught() -> None:
    assert "LEGEND_OUTSIDE_ITS_BAND" in codes(
        one(
            sheet(
                legend=[
                    LegendEntry(
                        symbol_id="valve-isolation",
                        name="Valvola di intercettazione",
                        anchor=Point(x_mm=20.0, y_mm=30.0),
                    )
                ]
            )
        )
    )


def test_a_label_repeating_a_legend_denomination_is_caught() -> None:
    """D-052: la legenda dice cosa, il tag dice quanto."""
    assert "LABEL_REPEATS_THE_LEGEND" in codes(
        one(
            sheet(
                legend=[
                    LegendEntry(
                        symbol_id="valve-isolation",
                        name="Valvola di intercettazione",
                        anchor=Point(x_mm=365.0, y_mm=30.0),
                    )
                ],
                labels=[
                    PlacedLabel(
                        id="repeat",
                        text="Valvola di intercettazione",
                        role="tag",
                        anchor=Point(x_mm=20.0, y_mm=30.0),
                    )
                ],
            )
        )
    )


def test_a_cross_reference_without_a_twin_is_caught() -> None:
    lonely = CrossReference(
        id="c1-t1",
        pair_id="c1",
        peer_sheet_id="t2",
        text="→ T2",
        anchor=Point(x_mm=30.0, y_mm=30.0),
    )
    assert "UNPAIRED_CROSS_REFERENCE" in codes(one(sheet(cross_references=[lonely])))


def test_a_paired_cross_reference_is_accepted() -> None:
    def reference(sheet_id: str, peer: str) -> CrossReference:
        return CrossReference(
            id=f"c1-{sheet_id}",
            pair_id="c1",
            peer_sheet_id=peer,
            text=f"→ {peer.upper()}",
            anchor=Point(x_mm=30.0, y_mm=30.0),
        )

    drawing = DrawingGeometry(
        project_id="probe",
        sheets=[
            sheet(sheet_id="t1", cross_references=[reference("t1", "t2")]),
            sheet(sheet_id="t2", cross_references=[reference("t2", "t1")]),
        ],
    )
    assert "UNPAIRED_CROSS_REFERENCE" not in codes(drawing)


def test_the_report_is_ordered_and_deduplicated() -> None:
    drawing = one(sheet(symbols=[symbol("a", 20.0, 20.0), symbol("b", 22.0, 21.0)]))
    issues = validate_drawing_geometry(drawing, NOVE_C_A3).issues
    assert [item.code for item in issues] == sorted(item.code for item in issues)
    keys = [(item.code, tuple(item.entity_ids), item.message) for item in issues]
    assert len(keys) == len(set(keys))
