"""La griglia su cui il layout dispone e instrada.

L'instradamento e' ortogonale e cammina su nodi di griglia, quindi una rotta
puo' terminare **solo** su un nodo. Ne segue un requisito che il manifesto del
simbolo non puo' imporre da solo, perche' non conosce il `GraphicStandard`:
ogni coordinata di porta deve essere un multiplo del passo.

Non e' un'estetica. Con una porta a 3 mm su un passo da 2,5 l'instradatore non
raggiunge l'attacco: o si esce dalla griglia, e allora l'allineamento richiesto
dalla specifica §10.2 sparisce, o si aggiunge a ogni attacco un gomito di
raccordo che nessun tecnico disegnerebbe.
"""

from dataclasses import dataclass, field

from disegnatore_mep.graphics.frame import Rect
from disegnatore_mep.graphics.standard import A3_LANDSCAPE, GraphicStandard
from disegnatore_mep.graphics.symbol import SymbolManifest

from .errors import LayoutError

TOLERANCE_MM = 1e-6

Cell = tuple[int, int]


@dataclass(frozen=True)
class GridSpace:
    """Conversione fra millimetri di carta e nodi di griglia, dentro un'area."""

    origin: Rect
    # `GraphicStandard` e' un modello Pydantic, che dataclasses considera
    # mutabile: va passato come factory anche se l'istanza e' condivisa.
    standard: GraphicStandard = field(default_factory=lambda: A3_LANDSCAPE)

    @property
    def step_mm(self) -> float:
        return self.standard.grid_mm

    @property
    def cols(self) -> int:
        return round(self.origin.width_mm / self.step_mm)

    @property
    def rows(self) -> int:
        return round(self.origin.height_mm / self.step_mm)

    def to_cell(self, x_mm: float, y_mm: float) -> Cell:
        """Il nodo corrispondente. Rifiuta una coordinata fuori griglia invece
        di arrotondarla in silenzio."""
        return (
            self._axis_to_index(x_mm - self.origin.x_mm, "x"),
            self._axis_to_index(y_mm - self.origin.y_mm, "y"),
        )

    def _axis_to_index(self, offset_mm: float, axis: str) -> int:
        steps = offset_mm / self.step_mm
        nearest = round(steps)
        if abs(steps - nearest) > TOLERANCE_MM:
            raise LayoutError(
                f"{offset_mm:g}mm on the {axis} axis is not a multiple of the "
                f"{self.step_mm:g}mm grid step: it falls {steps:.3f} steps from "
                f"the origin, between two nodes"
            )
        return int(nearest)

    def to_mm(self, cell: Cell) -> tuple[float, float]:
        return (
            self.origin.x_mm + cell[0] * self.step_mm,
            self.origin.y_mm + cell[1] * self.step_mm,
        )

    def contains(self, cell: Cell) -> bool:
        return 0 <= cell[0] <= self.cols and 0 <= cell[1] <= self.rows


def is_on_grid(value_mm: float, step_mm: float) -> bool:
    steps = value_mm / step_mm
    return abs(steps - round(steps)) <= TOLERANCE_MM


def assert_symbol_is_aligned(
    manifest: SymbolManifest, standard: GraphicStandard = A3_LANDSCAPE
) -> None:
    """Il riquadro e ogni porta cadono su nodi di griglia.

    Solleva `LayoutError` nominando simbolo, porta e coordinata colpevole: una
    diagnostica che dica soltanto «fuori griglia» non basta a correggere il file.
    """
    step = standard.grid_mm
    for label, value in (("width", manifest.width_mm), ("height", manifest.height_mm)):
        if not is_on_grid(value, step):
            raise LayoutError(
                f"symbol {manifest.id}: {label} {value:g}mm is not a multiple of the "
                f"{step:g}mm grid step ({value / step:.2f} steps)"
            )
    for port in manifest.ports:
        for axis, value in (("x", port.x_mm), ("y", port.y_mm)):
            if not is_on_grid(value, step):
                raise LayoutError(
                    f"symbol {manifest.id}, port {port.id}: {axis}={value:g}mm is not "
                    f"a multiple of the {step:g}mm grid step ({value / step:.2f} steps). "
                    f"A port centred on a face needs that face to be an even number "
                    f"of steps, so that its middle falls on a node"
                )
