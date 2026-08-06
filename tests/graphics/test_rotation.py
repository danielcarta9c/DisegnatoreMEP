import math
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.errors import SymbolError
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest

PUBLISHED = Path(__file__).resolve().parents[2] / "assets" / "symbols"

OBLONG_INLINE: dict[str, object] = {
    "id": "oblong-inline",
    "version": "1.0.0",
    "name": "Gruppo in linea oblungo",
    "width_mm": 10.0,
    "height_mm": 6.0,
    "allowed_rotations_deg": [0, 90, 180, 270],
    "inline_gap_mm": 10.0,
    "ports": [
        {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
        {"id": "b", "face": "right", "x_mm": 10.0, "y_mm": 3.0},
    ],
    "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
    "source": "CONV-GRAFICA-001",
}


def library() -> SymbolRegistry:
    return SymbolRegistry.from_directory(PUBLISHED)


def rotate_point(
    point: tuple[float, float], manifest: SymbolManifest, degrees: int
) -> tuple[float, float]:
    x, y = point
    width, height = manifest.width_mm, manifest.height_mm
    return {
        0: (x, y),
        90: (height - y, x),
        180: (width - x, height - y),
        270: (y, width - x),
    }[degrees]


def apply_svg_transform(transform: str, point: tuple[float, float]) -> tuple[float, float]:
    """Applica `translate(tx ty) rotate(a)` come lo applicherebbe un renderer SVG."""
    numbers = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", transform)]
    tx, ty, angle = numbers[0], numbers[1], numbers[2]
    radians = math.radians(angle)
    cos, sin = round(math.cos(radians)), round(math.sin(radians))
    x, y = point
    return (x * cos - y * sin + tx, x * sin + y * cos + ty)


def test_faces_turn_clockwise() -> None:
    assert PortFace.LEFT.rotated(90) is PortFace.TOP
    assert PortFace.TOP.rotated(90) is PortFace.RIGHT
    assert PortFace.RIGHT.rotated(90) is PortFace.BOTTOM
    assert PortFace.BOTTOM.rotated(90) is PortFace.LEFT
    assert PortFace.LEFT.rotated(180) is PortFace.RIGHT
    assert PortFace.LEFT.rotated(270) is PortFace.BOTTOM
    assert PortFace.LEFT.rotated(0) is PortFace.LEFT


def test_a_rotated_face_turns_its_outward_direction_with_it() -> None:
    for face in PortFace:
        for degrees in (0, 90, 180, 270):
            expected = (face.outward_angle_deg + degrees) % 360
            assert face.rotated(degrees).outward_angle_deg == expected


def test_every_published_symbol_survives_its_allowed_rotations() -> None:
    """Il manifesto ruotato e' costruito da capo, quindi rivalidato dalle stesse
    regole del §3: se una rotazione producesse una porta fuori faccia, fallirebbe qui."""
    for symbol in library().all():
        manifest = symbol.manifest
        for degrees in manifest.allowed_rotations_deg:
            rotated = manifest.rotated(degrees)
            swapped = degrees in (90, 270)
            assert rotated.width_mm == (manifest.height_mm if swapped else manifest.width_mm)
            assert rotated.height_mm == (manifest.width_mm if swapped else manifest.height_mm)
            assert rotated.port_ids == manifest.port_ids


def test_four_quarter_turns_return_the_original() -> None:
    for symbol in library().all():
        manifest = symbol.manifest
        if 90 not in manifest.allowed_rotations_deg:
            continue
        turned = manifest
        for _ in range(4):
            turned = turned.rotated(90)
        assert turned.model_dump() == manifest.model_dump()


def test_a_disallowed_rotation_is_refused() -> None:
    """D-049 e' un vincolo impiantistico: uno sfiato coricato e' sbagliato."""
    manifest = library().get("air-vent").manifest
    with pytest.raises(SymbolError, match="may not be drawn rotated"):
        manifest.rotated(90)


def test_a_non_orthogonal_rotation_is_refused() -> None:
    manifest = library().get("valve-isolation").manifest
    with pytest.raises(SymbolError, match="rotation must be 0, 90, 180 or 270"):
        manifest.rotated(45)


def test_ports_land_where_the_point_transform_says() -> None:
    manifest = library().get("valve-isolation").manifest
    rotated = manifest.rotated(90)
    for port in manifest.ports:
        expected = rotate_point((port.x_mm, port.y_mm), manifest, 90)
        moved = rotated.port(port.id)
        assert (moved.x_mm, moved.y_mm) == pytest.approx(expected)
        assert moved.face is port.face.rotated(90)


def test_keep_out_follows_the_face_it_protects() -> None:
    manifest = library().get("expansion-connection").manifest
    assert manifest.keep_out.top_mm > 0
    rotated = manifest.rotated(180)
    assert rotated.keep_out.bottom_mm == manifest.keep_out.top_mm
    assert rotated.keep_out.top_mm == 0


def test_keep_out_rotation_is_a_quarter_turn_cycle() -> None:
    original = library().get("expansion-connection").manifest.keep_out
    turned = original
    for _ in range(4):
        turned = turned.rotated(90)
    assert turned == original


def test_label_anchors_move_with_the_symbol() -> None:
    manifest = SymbolManifest.model_validate(
        OBLONG_INLINE | {"label_anchors": [{"id": "tag", "role": "tag", "x_mm": 5.0, "y_mm": -2.0}]}
    )
    rotated = manifest.rotated(90)
    assert (rotated.label_anchors[0].x_mm, rotated.label_anchors[0].y_mm) == pytest.approx(
        rotate_point((5.0, -2.0), manifest, 90)
    )
    assert rotated.label_anchors[0].role == "tag"


def test_the_body_transform_agrees_with_the_point_transform() -> None:
    """La matrice applicata al corpo SVG e quella applicata alle porte devono
    essere la stessa, o il disegno si stacca dai propri attacchi."""
    for symbol in library().all():
        manifest = symbol.manifest
        for degrees in manifest.allowed_rotations_deg:
            if degrees == 0:
                continue
            transform = symbol.rotated(degrees).body_transform
            for corner in ((0.0, 0.0), (manifest.width_mm, manifest.height_mm)):
                assert apply_svg_transform(transform, corner) == pytest.approx(
                    rotate_point(corner, manifest, degrees)
                ), (manifest.id, degrees, transform)


def test_a_rotated_symbol_keeps_its_body_and_wraps_it_once() -> None:
    symbol = library().get("valve-isolation")
    rotated = symbol.rotated(90)
    assert symbol.body in rotated.body
    assert rotated.body.count("<g transform=") == 1
    assert symbol.rotated(0).body == symbol.body
    assert symbol.rotated(0).body_transform == ""


def test_an_inline_symbol_keeps_its_gap_across_a_quarter_turn() -> None:
    """L'interruzione si misura sull'asse delle porte, non sulla larghezza."""
    oblong = SymbolManifest.model_validate(OBLONG_INLINE)
    rotated = oblong.rotated(90)
    assert (rotated.width_mm, rotated.height_mm) == (6.0, 10.0)
    assert rotated.inline_gap_mm == 10.0
    assert {port.face for port in rotated.ports} == {PortFace.TOP, PortFace.BOTTOM}


def test_the_gap_is_still_refused_when_it_exceeds_the_port_axis() -> None:
    with pytest.raises(
        ValidationError, match="exceeds the 10mm span between the two opposed ports"
    ):
        SymbolManifest.model_validate(OBLONG_INLINE | {"inline_gap_mm": 12.0})


def test_a_vertical_inline_symbol_is_measured_on_its_height() -> None:
    vertical = SymbolManifest.model_validate(
        OBLONG_INLINE
        | {
            "width_mm": 6.0,
            "height_mm": 10.0,
            "keep_out": {"top_mm": 2.0, "bottom_mm": 2.0},
            "ports": [
                {"id": "a", "face": "top", "x_mm": 3.0, "y_mm": 0.0},
                {"id": "b", "face": "bottom", "x_mm": 3.0, "y_mm": 10.0},
            ],
        }
    )
    assert vertical.inline_gap_mm == 10.0
