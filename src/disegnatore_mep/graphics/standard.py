"""Grandezze grafiche in millimetri di carta.

Unico punto in cui vivono le grandezze della carta: dimensioni del foglio,
margini, griglia, spessori dei tratti, altezze di testo. Un modulo che
disegna puo' nominare le proprie costanti di impaginazione, ma nessun valore
dimensionale puo' restare un numero anonimo nel codice, qui o altrove.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import FiniteFloat, StrictModel


class GraphicStandard(StrictModel):
    sheet_width_mm: FiniteFloat = Field(gt=0)
    sheet_height_mm: FiniteFloat = Field(gt=0)
    margin_left_mm: FiniteFloat = Field(ge=0)
    margin_right_mm: FiniteFloat = Field(ge=0)
    margin_top_mm: FiniteFloat = Field(ge=0)
    margin_bottom_mm: FiniteFloat = Field(ge=0)
    grid_mm: FiniteFloat = Field(gt=0)
    line_thin_mm: FiniteFloat = Field(gt=0)
    line_medium_mm: FiniteFloat = Field(gt=0)
    line_thick_mm: FiniteFloat = Field(gt=0)
    text_small_mm: FiniteFloat = Field(gt=0)
    text_normal_mm: FiniteFloat = Field(gt=0)
    text_title_mm: FiniteFloat = Field(gt=0)
    min_clearance_mm: FiniteFloat = Field(gt=0)

    @property
    def usable_width_mm(self) -> float:
        return self.sheet_width_mm - self.margin_left_mm - self.margin_right_mm

    @property
    def usable_height_mm(self) -> float:
        return self.sheet_height_mm - self.margin_top_mm - self.margin_bottom_mm

    @model_validator(mode="after")
    def geometry_is_coherent(self) -> "GraphicStandard":
        if self.usable_width_mm <= 0 or self.usable_height_mm <= 0:
            raise ValueError("margins leave no usable area")
        if not self.line_thin_mm < self.line_medium_mm < self.line_thick_mm:
            raise ValueError("line weights must increase from thin to thick")
        if not self.text_small_mm < self.text_normal_mm < self.text_title_mm:
            raise ValueError("text heights must increase from small to title")
        return self


# I margini sono quelli del cartiglio Nove C fornito come input del progetto: 10 mm sui
# quattro lati (D-053). Non vengono da ISO 5457, che il registro fonti elenca ancora «da
# acquisire e valutare», e che avrebbe imposto 20 mm di rilegatura a sinistra.
# I due assi restano asimmetrici rispetto alla griglia: la larghezza utile (400 mm) e' un
# numero intero di passi (160), l'altezza (277) no (110,8). I margini non vengono corretti
# per forzare entrambi gli assi sulla griglia: la squadratura e' quella del cartiglio.
A3_LANDSCAPE = GraphicStandard(
    sheet_width_mm=420.0,
    sheet_height_mm=297.0,
    margin_left_mm=10.0,
    margin_right_mm=10.0,
    margin_top_mm=10.0,
    margin_bottom_mm=10.0,
    grid_mm=2.5,
    line_thin_mm=0.18,
    line_medium_mm=0.35,
    line_thick_mm=0.50,
    text_small_mm=1.8,
    text_normal_mm=2.5,
    text_title_mm=3.5,
    min_clearance_mm=2.0,
)

# L'A4 orizzontale e' il formato per i disegni piccoli (D-058). Stessa squadratura a 10 mm
# e stessa taratura di tratti e testi dell'A3: la scala di stampa e' invariante (ADR 0003),
# quindi un simbolo misura lo stesso su entrambi i fogli e cambia solo quanto ce ne sta.
A4_LANDSCAPE = A3_LANDSCAPE.model_copy(
    update={"sheet_width_mm": 297.0, "sheet_height_mm": 210.0}
)
