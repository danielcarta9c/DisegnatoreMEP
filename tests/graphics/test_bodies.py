"""Il corpo di un simbolo resta nel proprio riquadro e raggiunge le sue porte.

Erano due proprieta' vere ma non presidiate: `PROJECT_STATE.md` le registrava
come debito noto della fase grafica. Un corpo modificato a mano poteva
romperle e continuare a caricare, perche' il registro valida il manifesto e
controlla che l'XML sia ben formato, non che il disegno corrisponda.
"""

import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry

ROOT = Path(__file__).resolve().parents[2]
LIBRARIES = (
    ROOT / "assets" / "symbols",
    ROOT / "examples" / "foundation" / "symbols",
)
TOLERANCE_MM = 1e-6


def _local(tag: str) -> str:
    return tag.rpartition("}")[2]


def geometry(body: str) -> tuple[list[tuple[float, float]], tuple[float, float, float, float]]:
    """Punti notevoli e ingombro del corpo.

    Copre le primitive che la libreria usa davvero: `line`, `rect`, `circle` e
    `path` con comandi a coordinate assolute. Un corpo che introducesse un
    comando relativo sfuggirebbe a questa lettura, ed e' il motivo per cui la
    convenzione della libreria e' di non usarne.
    """
    root = ElementTree.fromstring(f"<g>{body}</g>")
    points: list[tuple[float, float]] = []
    xs: list[float] = []
    ys: list[float] = []
    for element in root.iter():
        tag, get = _local(element.tag), element.get
        if tag == "line":
            pair = [
                (float(get("x1", "0")), float(get("y1", "0"))),
                (float(get("x2", "0")), float(get("y2", "0"))),
            ]
            points += pair
            xs += [item[0] for item in pair]
            ys += [item[1] for item in pair]
        elif tag == "rect":
            x, y, w, h = (float(get(key, "0")) for key in ("x", "y", "width", "height"))
            points += [
                (x, y), (x + w, y), (x, y + h), (x + w, y + h),
                (x, y + h / 2), (x + w, y + h / 2), (x + w / 2, y), (x + w / 2, y + h),
            ]
            xs += [x, x + w]
            ys += [y, y + h]
        elif tag == "circle":
            cx, cy, r = (float(get(key, "0")) for key in ("cx", "cy", "r"))
            xs += [cx - r, cx + r]
            ys += [cy - r, cy + r]
        elif tag == "path":
            numbers = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", get("d", ""))]
            points += list(zip(numbers[0::2], numbers[1::2], strict=False))
            xs += numbers[0::2]
            ys += numbers[1::2]
    return points, (min(xs), max(xs), min(ys), max(ys))


def published() -> list[Symbol]:
    return [
        symbol
        for directory in LIBRARIES
        for symbol in SymbolRegistry.from_directory(directory).all()
    ]


def test_the_libraries_are_not_empty() -> None:
    assert len(published()) == 47


@pytest.mark.parametrize("symbol", published(), ids=lambda item: item.manifest.id)
def test_a_body_stays_inside_its_own_box(symbol: Symbol) -> None:
    manifest = symbol.manifest
    _, (x0, x1, y0, y1) = geometry(symbol.body)
    assert x0 >= -TOLERANCE_MM
    assert y0 >= -TOLERANCE_MM
    assert x1 <= manifest.width_mm + TOLERANCE_MM
    assert y1 <= manifest.height_mm + TOLERANCE_MM


@pytest.mark.parametrize("symbol", published(), ids=lambda item: item.manifest.id)
def test_a_body_reaches_every_port_it_declares(symbol: Symbol) -> None:
    """Un attacco che il disegno non tocca e' una tubazione che finisce nel vuoto."""
    points, _ = geometry(symbol.body)
    for port in symbol.manifest.ports:
        assert any(
            abs(x - port.x_mm) <= TOLERANCE_MM and abs(y - port.y_mm) <= TOLERANCE_MM
            for x, y in points
        ), f"{symbol.manifest.id}.{port.id} at ({port.x_mm:g}, {port.y_mm:g})"
