"""Manifesto geometrico di un simbolo.

Il simbolo descrive come il componente è disegnato: riquadro, porte sul
perimetro, area di rispetto e ancoraggi delle etichette. La semantica delle
porte — dominio, fluido, verso, obbligatorietà — vive nella definizione di
componente del catalogo e si unisce a questa per identificativo di porta.
"""

from enum import StrEnum
from typing import TYPE_CHECKING, Literal

from pydantic import ConfigDict, Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, FiniteFloat, StrictModel

from .errors import SymbolError

if TYPE_CHECKING:
    from disegnatore_mep.catalog.registry import ComponentRegistry

    from .standard import GraphicStandard

TOLERANCE_MM = 1e-6

ORTHOGONAL_ROTATIONS = (0, 90, 180, 270)


def rotate_point_mm(
    x_mm: float, y_mm: float, width_mm: float, height_mm: float, degrees: int
) -> tuple[float, float]:
    """Un punto del riquadro dopo una rotazione oraria, con y verso il basso.

    `width_mm` e `height_mm` sono quelli del riquadro **prima** della rotazione;
    a 90 e 270 gradi il riquadro risultante li ha scambiati.
    """
    return {
        0: (x_mm, y_mm),
        90: (height_mm - y_mm, x_mm),
        180: (width_mm - x_mm, height_mm - y_mm),
        270: (y_mm, width_mm - x_mm),
    }[degrees]


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

    def rotated(self, degrees: int) -> "PortFace":
        """La faccia dopo una rotazione oraria, con y verso il basso come in SVG.

        La tabella vive dentro il metodo, come per `opposite`: sopra la classe
        nominerebbe `PortFace` prima che esista.
        """
        clockwise = {
            PortFace.LEFT: PortFace.TOP,
            PortFace.TOP: PortFace.RIGHT,
            PortFace.RIGHT: PortFace.BOTTOM,
            PortFace.BOTTOM: PortFace.LEFT,
        }
        face = self
        for _ in range(degrees // 90):
            face = clockwise[face]
        return face


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

    def rotated(self, degrees: int) -> "KeepOut":
        """L'area di rispetto segue la faccia che protegge."""
        result = self
        for _ in range(degrees // 90):
            result = KeepOut(
                left_mm=result.bottom_mm,
                top_mm=result.left_mm,
                right_mm=result.top_mm,
                bottom_mm=result.right_mm,
            )
        return result


class LabelAnchor(StrictModel):
    """Punto preferito per un tag o una descrizione, anche fuori dal riquadro."""

    id: str = Field(pattern=ID_PATTERN)
    role: Literal["tag", "description", "data"]
    x_mm: FiniteFloat
    y_mm: FiniteFloat


class FlowGlyph(StrictModel):
    """Una freccia di verso legata a una porta (DRAW-005, I-032).

    Il corpo di un simbolo non sa da che parte scorre l'acqua: lo sa il
    catalogo, porta per porta. Il confine di rete ne e' il caso: lo stesso
    segno serve all'acquedotto, da cui l'acqua **esce** verso l'impianto, e
    alle utenze, in cui l'acqua **entra**. Il manifesto dichiara percio' dove
    sta la freccia e quanto e' lunga; chi disegna la punta nel verso locale
    dell'acqua letto dal `PortFlow` della porta — verso la porta se il fluido
    esce dal simbolo, verso l'interno se vi entra — e mai dall'identificativo
    del pezzo o dal bordo del foglio. Senza un verso noto — il foglio di
    riscontro, la legenda — la freccia punta verso la porta.

    La freccia sta sull'asse della porta, centrata in `(x_mm, y_mm)` nel
    riquadro non ruotato, e ruota con il corpo come ruotano le porte."""

    port: str = Field(pattern=ID_PATTERN)
    x_mm: FiniteFloat
    y_mm: FiniteFloat
    length_mm: FiniteFloat = Field(gt=0)
    half_width_mm: FiniteFloat = Field(gt=0)


class UprightGlyph(StrictModel):
    """Un glifo interno dichiarato **leggibile** (DRAW-005, I-033).

    La `P` del manometro, la `T` del termometro, la `F` di un flussostato che
    entrera' domani: una lettera si legge nel verso della tavola, anche quando
    il corpo dello strumento e' girato. Il corpo la disegna in un gruppo
    marcato `data-glyph` con questo identificativo; chi ruota il simbolo la
    contro-ruota attorno a `(x_mm, y_mm)`, cosi' che il glifo segua il proprio
    centro senza girare, mentre corpo e porte girano come sempre."""

    id: str = Field(pattern=ID_PATTERN)
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
    flow_glyphs: list[FlowGlyph] = Field(default_factory=list)
    upright_glyphs: list[UprightGlyph] = Field(default_factory=list)
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

        # Un glifo sta dentro il riquadro: una freccia legata a una porta che
        # non esiste, o una lettera fuori dal corpo, sarebbero disegnate nel
        # vuoto o su un attacco che non c'e'.
        for glyph in self.flow_glyphs:
            if glyph.port not in seen:
                raise ValueError(
                    f"flow glyph refers to unknown port {glyph.port}: the arrow of a "
                    f"port that does not exist would point at nothing"
                )
            if not (
                -TOLERANCE_MM <= glyph.x_mm <= self.width_mm + TOLERANCE_MM
                and -TOLERANCE_MM <= glyph.y_mm <= self.height_mm + TOLERANCE_MM
            ):
                raise ValueError(f"flow glyph of port {glyph.port} falls outside the symbol box")
        glyph_ids: set[str] = set()
        for upright in self.upright_glyphs:
            if upright.id in glyph_ids:
                raise ValueError(f"duplicate upright glyph id: {upright.id}")
            glyph_ids.add(upright.id)
            if not (
                -TOLERANCE_MM <= upright.x_mm <= self.width_mm + TOLERANCE_MM
                and -TOLERANCE_MM <= upright.y_mm <= self.height_mm + TOLERANCE_MM
            ):
                raise ValueError(f"upright glyph {upright.id} falls outside the symbol box")

        if self.inline_gap_mm is not None:
            faces = {port.face for port in self.ports}
            opposed = any(face.opposite in faces for face in faces)
            if len(self.ports) != 2 or not opposed:
                raise ValueError("an inline symbol needs two opposed ports")
            # L'interruzione si misura lungo l'asse che unisce le due porte, non
            # sulla larghezza: lo stesso simbolo ruotato di 90 gradi interrompe
            # la linea per la stessa lunghezza, ma sull'altro asse del riquadro.
            span = self.width_mm if PortFace.LEFT in faces else self.height_mm
            if self.inline_gap_mm > span + TOLERANCE_MM:
                raise ValueError(
                    f"inline gap {self.inline_gap_mm:g}mm exceeds the {span:g}mm "
                    f"span between the two opposed ports"
                )
        return self

    def rotated(self, degrees: int) -> "SymbolManifest":
        """Il manifesto ruotato in senso orario, riquadro scambiato a 90 e 270.

        Costruisce un manifesto nuovo, quindi rivalidato dalle stesse regole di
        questa classe: e' cosi' che l'invariante perimetro-faccia sopravvive alla
        rotazione invece di essere riderivato da ogni consumatore.
        """
        if degrees not in ORTHOGONAL_ROTATIONS:
            raise SymbolError(f"rotation must be 0, 90, 180 or 270 degrees: {degrees}")
        if degrees not in self.allowed_rotations_deg:
            raise SymbolError(
                f"symbol {self.id} may not be drawn rotated by {degrees} degrees: "
                f"allowed {sorted(self.allowed_rotations_deg)} (D-049)"
            )
        if degrees == 0:
            return self

        swapped = degrees in (90, 270)

        def moved(x_mm: float, y_mm: float) -> tuple[float, float]:
            return rotate_point_mm(x_mm, y_mm, self.width_mm, self.height_mm, degrees)

        ports: list[SymbolPort] = []
        for port in self.ports:
            x_mm, y_mm = moved(port.x_mm, port.y_mm)
            ports.append(
                SymbolPort(id=port.id, face=port.face.rotated(degrees), x_mm=x_mm, y_mm=y_mm)
            )

        anchors: list[LabelAnchor] = []
        for anchor in self.label_anchors:
            x_mm, y_mm = moved(anchor.x_mm, anchor.y_mm)
            anchors.append(
                LabelAnchor(id=anchor.id, role=anchor.role, x_mm=x_mm, y_mm=y_mm)
            )

        # I glifi seguono il corpo: il centro della freccia e quello della
        # lettera si spostano come si sposta una porta. La freccia prende poi
        # il verso dalla faccia ruotata della propria porta, la lettera resta
        # dritta attorno al centro spostato.
        flow_glyphs: list[FlowGlyph] = []
        for glyph in self.flow_glyphs:
            x_mm, y_mm = moved(glyph.x_mm, glyph.y_mm)
            flow_glyphs.append(glyph.model_copy(update={"x_mm": x_mm, "y_mm": y_mm}))
        upright_glyphs: list[UprightGlyph] = []
        for upright in self.upright_glyphs:
            x_mm, y_mm = moved(upright.x_mm, upright.y_mm)
            upright_glyphs.append(upright.model_copy(update={"x_mm": x_mm, "y_mm": y_mm}))

        return SymbolManifest(
            id=self.id,
            version=self.version,
            name=self.name,
            width_mm=self.height_mm if swapped else self.width_mm,
            height_mm=self.width_mm if swapped else self.height_mm,
            # Da un manifesto gia' ruotato di r, una rotazione ulteriore d e'
            # ammessa se e solo se r + d lo era in origine.
            allowed_rotations_deg=[
                (value - degrees) % 360 for value in self.allowed_rotations_deg
            ],
            inline_gap_mm=self.inline_gap_mm,
            ports=ports,
            keep_out=self.keep_out.rotated(degrees),
            label_anchors=anchors,
            flow_glyphs=flow_glyphs,
            upright_glyphs=upright_glyphs,
            source=self.source,
        )


def inline_extent_mm(manifest: SymbolManifest) -> float:
    """Quanto un accessorio in linea sporge **attraverso** la tubazione.

    E' il lato del riquadro perpendicolare all'asse delle due porte: l'altezza
    per un pezzo con le porte a destra e a sinistra, la larghezza per uno con
    le porte sopra e sotto."""
    faces = {port.face for port in manifest.ports}
    if PortFace.LEFT in faces or PortFace.RIGHT in faces:
        return manifest.height_mm
    return manifest.width_mm


def functional_room_mm(
    catalog: "ComponentRegistry", medium: str, standard: "GraphicStandard"
) -> float:
    """Lo spazio che due attacchi affiancati devono lasciarsi (DRAW-005, I-039).

    Non e' una costante per tutti i simboli: si **ricava** dagli accessori in
    linea che il catalogo sa posare su quel fluido — il piu' alto attraverso la
    tubazione — piu' la distanza minima di rispetto della griglia. Due attacchi
    piu' vicini di cosi' portano due accessori che si toccano, ed e' cio' che
    la tavola DRAW-004 mostrava con i cinque millimetri della pompa di calore.
    """
    tallest = max(
        (
            inline_extent_mm(catalog.resolve(definition.id).symbol.manifest)
            for definition in catalog.all()
            if catalog.resolve(definition.id).is_inline
            and all(port.medium == medium for port in definition.ports)
        ),
        default=0.0,
    )
    return tallest + standard.min_clearance_mm
