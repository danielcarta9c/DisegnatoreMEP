"""Il modello geometrico derivato.

Il modello tecnico canonico resta la fonte di verita' e **non contiene
coordinate** (D-026, ADR 0002). Posizioni, spezzate, testi, legenda e rimandi
vivono qui, in un modello separato che si rigenera dal primo: correggere una
tavola significa correggere il modello tecnico o il piano di impaginazione,
mai queste coordinate.
"""

import hashlib
import json

from pydantic import Field

from disegnatore_mep.model.base import FiniteFloat, StrictModel


class Point(StrictModel):
    x_mm: FiniteFloat
    y_mm: FiniteFloat


class PlacedSymbol(StrictModel):
    """Un simbolo posato: dove sta, come e' ruotato, quanto ingombra."""

    component_id: str
    symbol_id: str
    rotation_deg: int
    origin: Point
    width_mm: FiniteFloat = Field(gt=0)
    height_mm: FiniteFloat = Field(gt=0)
    tag: str | None = None

    @property
    def right_mm(self) -> float:
        return self.origin.x_mm + self.width_mm

    @property
    def bottom_mm(self) -> float:
        return self.origin.y_mm + self.height_mm


class RoutedTrunk(StrictModel):
    """Una tratta instradata: la spezzata ortogonale, con le sue interruzioni.

    `segments` e' l'elenco delle polilinee da disegnare: una sola quando la
    tratta non porta accessori in linea, piu' di una quando li porta, perche'
    ogni accessorio interrompe la linea invece di esservi sovrapposto (D-027).
    """

    network_id: str
    medium: str = ""
    """Il fluido, che decide colore e tratto: la rete da sola non basta."""
    supply: bool = True
    """Andata o ritorno. Su una tavola sono due linee distinte, non una."""
    connection_ids: list[str] = Field(default_factory=list)
    segments: list[list[Point]] = Field(default_factory=list)
    crossings: list[Point] = Field(default_factory=list)


class PlacedLabel(StrictModel):
    """Un testo sulla tavola: mai una denominazione, solo valore o sigla (D-052)."""

    id: str
    text: str
    role: str
    anchor: Point
    leader_from: Point | None = None
    """Da dove parte la linea di richiamo, quando il testo sta fuori dal corpo."""


class LegendEntry(StrictModel):
    symbol_id: str
    name: str
    anchor: Point


class NetworkKey(StrictModel):
    """Voce della sezione fluidi della legenda: colore e tratto di un fluido.

    Una per **fluido**, non per rete: primario e secondario portano la stessa
    acqua di riscaldamento e si disegnano uguali.
    """

    medium: str
    name: str
    colour: str
    dash: str
    anchor: Point


class CrossReference(StrictModel):
    id: str
    pair_id: str
    peer_sheet_id: str
    text: str
    anchor: Point


class SheetGeometry(StrictModel):
    sheet_id: str
    title: str
    symbols: list[PlacedSymbol] = Field(default_factory=list)
    routes: list[RoutedTrunk] = Field(default_factory=list)
    labels: list[PlacedLabel] = Field(default_factory=list)
    legend: list[LegendEntry] = Field(default_factory=list)
    network_keys: list[NetworkKey] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)
    ground_line_y_mm: FiniteFloat | None = None
    """Quota della linea di terra: le macchine ci appoggiano sopra."""


class DrawingGeometry(StrictModel):
    project_id: str
    sheets: list[SheetGeometry] = Field(default_factory=list)


def drawing_fingerprint(drawing: DrawingGeometry) -> str:
    """Impronta riproducibile della geometria.

    Stesso modello e stesso piano di impaginazione devono dare la stessa
    tavola: questa e' la misura che lo dimostra, come `project_fingerprint`
    fa per il modello tecnico.
    """
    payload = json.dumps(
        drawing.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
