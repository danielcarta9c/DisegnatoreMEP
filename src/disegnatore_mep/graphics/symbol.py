"""Manifesto geometrico di un simbolo.

Il simbolo descrive come il componente è disegnato: riquadro, porte sul
perimetro, area di rispetto e ancoraggi delle etichette. La semantica delle
porte — dominio, fluido, verso, obbligatorietà — vive nella definizione di
componente del catalogo e si unisce a questa per identificativo di porta.
"""

from enum import StrEnum
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, FiniteFloat, StrictModel

from .errors import SymbolError

TOLERANCE_MM = 1e-6


class PortFace(StrEnum):
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

    @property
    def outward_angle_deg(self) -> int:
        """Direzione uscente in gradi, con y crescente verso il basso come in SVG."""
        return {
            PortFace.RIGHT: 0,
            PortFace.BOTTOM: 90,
            PortFace.LEFT: 180,
            PortFace.TOP: 270,
        }[self]

    @property
    def opposite(self) -> "PortFace":
        return {
            PortFace.LEFT: PortFace.RIGHT,
            PortFace.RIGHT: PortFace.LEFT,
            PortFace.TOP: PortFace.BOTTOM,
            PortFace.BOTTOM: PortFace.TOP,
        }[self]


class SymbolPort(StrictModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    id: str = Field(pattern=ID_PATTERN)
    face: PortFace
    x_mm: FiniteFloat
    y_mm: FiniteFloat

    @property
    def outward_angle_deg(self) -> int:
        return self.face.outward_angle_deg


class KeepOut(StrictModel):
    """Area di rispetto, per lato: nulla puo' essere disposto dentro questi margini."""

    left_mm: FiniteFloat = Field(default=0.0, ge=0)
    right_mm: FiniteFloat = Field(default=0.0, ge=0)
    top_mm: FiniteFloat = Field(default=0.0, ge=0)
    bottom_mm: FiniteFloat = Field(default=0.0, ge=0)


class LabelAnchor(StrictModel):
    """Punto preferito per un tag o una descrizione, anche fuori dal riquadro."""

    id: str = Field(pattern=ID_PATTERN)
    role: Literal["tag", "description", "data"]
    x_mm: FiniteFloat
    y_mm: FiniteFloat


class SymbolManifest(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    width_mm: FiniteFloat = Field(gt=0)
    height_mm: FiniteFloat = Field(gt=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    inline_gap_mm: FiniteFloat | None = Field(default=None, gt=0)
    ports: list[SymbolPort] = Field(min_length=1)
    keep_out: KeepOut = Field(default_factory=KeepOut)
    label_anchors: list[LabelAnchor] = Field(default_factory=list)
    source: str = Field(min_length=1)

    def port(self, port_id: str) -> SymbolPort:
        for item in self.ports:
            if item.id == port_id:
                return item
        raise SymbolError(f"unknown symbol port: {port_id}")

    @property
    def port_ids(self) -> frozenset[str]:
        return frozenset(item.id for item in self.ports)

    @property
    def is_inline(self) -> bool:
        return self.inline_gap_mm is not None

    def _face_coordinate(self, port: SymbolPort) -> tuple[float, float]:
        expected = {
            PortFace.LEFT: (0.0, port.y_mm),
            PortFace.RIGHT: (self.width_mm, port.y_mm),
            PortFace.TOP: (port.x_mm, 0.0),
            PortFace.BOTTOM: (port.x_mm, self.height_mm),
        }[port.face]
        return expected

    @model_validator(mode="after")
    def geometry_is_coherent(self) -> "SymbolManifest":
        allowed = {0, 90, 180, 270}
        if not set(self.allowed_rotations_deg).issubset(allowed):
            raise ValueError("allowed rotations must be 0, 90, 180 or 270")
        if len(self.allowed_rotations_deg) != len(set(self.allowed_rotations_deg)):
            raise ValueError("duplicate allowed rotation")

        seen: set[str] = set()
        for port in self.ports:
            if port.id in seen:
                raise ValueError(f"duplicate port id: {port.id}")
            seen.add(port.id)
            if not (
                -TOLERANCE_MM <= port.x_mm <= self.width_mm + TOLERANCE_MM
                and -TOLERANCE_MM <= port.y_mm <= self.height_mm + TOLERANCE_MM
            ):
                raise ValueError(f"port {port.id} falls outside the symbol box")
            expected_x, expected_y = self._face_coordinate(port)
            if (
                abs(port.x_mm - expected_x) > TOLERANCE_MM
                or abs(port.y_mm - expected_y) > TOLERANCE_MM
            ):
                raise ValueError(f"port {port.id} is not on its {port.face.value} face")

        # Una faccia che porta una porta deve avere un'area di rispetto: senza,
        # l'instradamento accosterebbe una tubazione a un oggetto vicino. Il
        # manifesto non conosce lo standard grafico e non puo' quindi imporre
        # `min_clearance_mm`: l'invariante che gli appartiene e' "maggiore di
        # zero". Il valore concreto lo fissa chi genera il simbolo (§5).
        port_faces = {port.face for port in self.ports}
        clearance = {
            PortFace.LEFT: self.keep_out.left_mm,
            PortFace.RIGHT: self.keep_out.right_mm,
            PortFace.TOP: self.keep_out.top_mm,
            PortFace.BOTTOM: self.keep_out.bottom_mm,
        }
        for face in PortFace:
            if face in port_faces and clearance[face] <= 0:
                raise ValueError(
                    f"keep_out.{face.value}_mm must be greater than zero: "
                    f"the {face.value} face carries a port"
                )

        anchors: set[str] = set()
        for anchor in self.label_anchors:
            if anchor.id in anchors:
                raise ValueError(f"duplicate label anchor id: {anchor.id}")
            anchors.add(anchor.id)

        if self.inline_gap_mm is not None:
            if self.inline_gap_mm > self.width_mm + TOLERANCE_MM:
                raise ValueError("inline gap cannot exceed the symbol width")
            faces = {port.face for port in self.ports}
            opposed = any(face.opposite in faces for face in faces)
            if len(self.ports) != 2 or not opposed:
                raise ValueError("an inline symbol needs two opposed ports")
        return self
