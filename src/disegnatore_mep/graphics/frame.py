"""Il telaio della tavola: come il foglio si divide fra cartiglio e disegno.

Le misure vengono dal cartiglio aziendale — `assets/cartigli/Cartiglio_NoveC_A3.pdf`,
fornito come input del progetto — non da una norma. Estratte dalla geometria
vettoriale del PDF:

    squadratura      da (10, 10) a (410, 287), quindi 400 x 277 mm
    banda cartiglio  36 mm a tutta larghezza sul bordo inferiore
                     (34 mm di banda piu' 2 mm di filetto)
    intestazione     filetto a 6 mm dal bordo superiore, largo 392 mm

`standard.py` resta l'autorita' sulla **carta**; questo modulo nomina le
proprie costanti di impaginazione, come `svg.py` gia' fa (D-046).

Le coordinate hanno origine in alto a sinistra, come SVG, non in basso come il
PDF da cui sono state misurate.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import FiniteFloat, StrictModel

from .standard import (
    A1_LANDSCAPE,
    A2_LANDSCAPE,
    A3_LANDSCAPE,
    A4_LANDSCAPE,
    GraphicStandard,
)

TITLE_BLOCK_HEIGHT_MM = 36.0
"""Banda del cartiglio Nove C: 34 mm di banda piu' 2 mm di filetto."""

HEADER_HEIGHT_MM = 6.0
"""Fascia d'intestazione, dal filetto superiore della squadratura."""

LEGEND_WIDTH_MM = 50.0
"""Fascia della legenda sul lato destro (D-052).

Venti passi di griglia: larghi abbastanza per un simbolo e la sua denominazione
italiana accanto, che e' cio' che la legenda deve mostrare.
"""


class Rect(StrictModel):
    """Rettangolo in millimetri di carta, origine in alto a sinistra."""

    x_mm: FiniteFloat
    y_mm: FiniteFloat
    width_mm: FiniteFloat = Field(gt=0)
    height_mm: FiniteFloat = Field(gt=0)

    @property
    def right_mm(self) -> float:
        return self.x_mm + self.width_mm

    @property
    def bottom_mm(self) -> float:
        return self.y_mm + self.height_mm

    def contains(self, other: "Rect") -> bool:
        return (
            other.x_mm >= self.x_mm
            and other.y_mm >= self.y_mm
            and other.right_mm <= self.right_mm
            and other.bottom_mm <= self.bottom_mm
        )

    def overlaps(self, other: "Rect") -> bool:
        """Vero solo se le due aree condividono superficie.

        Toccarsi sul bordo non e' sovrapporsi: corpo e cartiglio sono contigui
        per costruzione, e devono restare accettabili.
        """
        return (
            self.x_mm < other.right_mm
            and other.x_mm < self.right_mm
            and self.y_mm < other.bottom_mm
            and other.y_mm < self.bottom_mm
        )


class SheetFrame(StrictModel):
    """Come una tavola si divide: intestazione, disegno, legenda, cartiglio."""

    standard: GraphicStandard
    header_height_mm: FiniteFloat = Field(default=HEADER_HEIGHT_MM, gt=0)
    title_block_height_mm: FiniteFloat = Field(default=TITLE_BLOCK_HEIGHT_MM, gt=0)
    legend_width_mm: FiniteFloat = Field(default=LEGEND_WIDTH_MM, gt=0)

    @property
    def border_rect_mm(self) -> Rect:
        """La squadratura: l'area utile del foglio."""
        return Rect(
            x_mm=self.standard.margin_left_mm,
            y_mm=self.standard.margin_top_mm,
            width_mm=self.standard.usable_width_mm,
            height_mm=self.standard.usable_height_mm,
        )

    @property
    def header_rect_mm(self) -> Rect:
        border = self.border_rect_mm
        return Rect(
            x_mm=border.x_mm,
            y_mm=border.y_mm,
            width_mm=border.width_mm,
            height_mm=self.header_height_mm,
        )

    @property
    def title_block_rect_mm(self) -> Rect:
        """Spazio riservato al cartiglio. Questo piano non lo disegna."""
        border = self.border_rect_mm
        return Rect(
            x_mm=border.x_mm,
            y_mm=border.bottom_mm - self.title_block_height_mm,
            width_mm=border.width_mm,
            height_mm=self.title_block_height_mm,
        )

    @property
    def body_rect_mm(self) -> Rect:
        """Cio' che resta fra intestazione e cartiglio: disegno piu' legenda."""
        border = self.border_rect_mm
        return Rect(
            x_mm=border.x_mm,
            y_mm=border.y_mm + self.header_height_mm,
            width_mm=border.width_mm,
            height_mm=border.height_mm - self.header_height_mm - self.title_block_height_mm,
        )

    @property
    def legend_rect_mm(self) -> Rect:
        body = self.body_rect_mm
        return Rect(
            x_mm=body.right_mm - self.legend_width_mm,
            y_mm=body.y_mm,
            width_mm=self.legend_width_mm,
            height_mm=body.height_mm,
        )

    @property
    def drawing_rect_mm(self) -> Rect:
        """La superficie su cui il layout dispone e instrada."""
        body = self.body_rect_mm
        return Rect(
            x_mm=body.x_mm,
            y_mm=body.y_mm,
            width_mm=body.width_mm - self.legend_width_mm,
            height_mm=body.height_mm,
        )

    @model_validator(mode="after")
    def areas_are_disjoint(self) -> "SheetFrame":
        bands = self.header_height_mm + self.title_block_height_mm
        if bands >= self.standard.usable_height_mm:
            raise ValueError(
                f"the {self.header_height_mm:g}mm header and the "
                f"{self.title_block_height_mm:g}mm title block leave no drawing area "
                f"in the {self.standard.usable_height_mm:g}mm usable height"
            )
        if self.legend_width_mm >= self.standard.usable_width_mm:
            raise ValueError(
                f"the {self.legend_width_mm:g}mm legend band leaves no drawing area "
                f"in the {self.standard.usable_width_mm:g}mm usable width"
            )
        return self


NOVE_C_A3 = SheetFrame(standard=A3_LANDSCAPE)

NOVE_C_A4 = SheetFrame(standard=A4_LANDSCAPE)
"""L'A4 orizzontale — **non piu' un formato ordinario** (D-184, 25 settembre 2026).

Il cartiglio Nove C e' largo 400 mm e l'A4 ne ha 277 utili: non lo contiene, e
il PO ha deciso che il cartiglio resta a misura su ogni foglio. Il telaio resta
definito perche' le prove della posa lo usano come foglio piccolo; una tavola
**col cartiglio** su questo telaio non si disegna (`cartiglio.disegna_cartiglio`
lo rifiuta).

Le bande sono quelle misurate sull'A3 — 36 mm di cartiglio, 6 di intestazione,
50 di legenda — riportate tali e quali, perche' un cartiglio non si
rimpicciolisce col foglio.
"""

NOVE_C_A2 = SheetFrame(standard=A2_LANDSCAPE)
"""L'A2 orizzontale (D-148). Le bande sono quelle misurate sull'A3: un cartiglio
non cresce col foglio, contiene le stesse righe di testo alla stessa altezza."""

NOVE_C_A1 = SheetFrame(standard=A1_LANDSCAPE)
"""L'A1 orizzontale (D-148), per l'impianto che non entra nemmeno su A2."""

ORDINARY_FRAMES: tuple[SheetFrame, ...] = (NOVE_C_A3, NOVE_C_A2, NOVE_C_A1)
"""I formati ordinari, dal piu' piccolo al piu' grande (D-058, esteso da D-148,
ristretto da D-184).

L'ordine **e'** la regola di scelta: si prende il primo su cui il disegno entra.

**L'A4 non c'e' piu'** (D-184, 25 settembre 2026): il cartiglio Nove C e' largo
400 mm, resta a misura su ogni foglio, e l'A4 ne ha 277 utili. Per una centrale
l'A3 era gia' il primo tentativo (D-135).

**Oltre l'A3 adesso si va** (D-148): il divieto di D-058 e la preferenza di D-019
per piu' A3 coordinate sono sospesi. Un elaborato che esce su A2 e' un elaborato
che esiste; uno che non esce non si stampa e non si rifinisce. Quando i cinque
impianti di prova usciranno tutti, la domanda «quale formato serve davvero» si
riapre — e quel giorno questa tupla e' il posto in cui si risponde.
"""
