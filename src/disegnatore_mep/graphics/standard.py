"""Grandezze grafiche in millimetri di carta.

Unico punto in cui vivono dimensioni, spessori, altezze di testo e distanze.
Nessun altro modulo deve contenere una costante metrica.
"""

from pydantic import Field, model_validator

from disegnatore_mep.model.base import StrictModel


class GraphicStandard(StrictModel):
    sheet_width_mm: float = Field(gt=0)
    sheet_height_mm: float = Field(gt=0)
    margin_left_mm: float = Field(ge=0)
    margin_right_mm: float = Field(ge=0)
    margin_top_mm: float = Field(ge=0)
    margin_bottom_mm: float = Field(ge=0)
    grid_mm: float = Field(gt=0)
    line_thin_mm: float = Field(gt=0)
    line_medium_mm: float = Field(gt=0)
    line_thick_mm: float = Field(gt=0)
    text_small_mm: float = Field(gt=0)
    text_normal_mm: float = Field(gt=0)
    text_title_mm: float = Field(gt=0)
    min_clearance_mm: float = Field(gt=0)

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


A3_LANDSCAPE = GraphicStandard(
    sheet_width_mm=420.0,
    sheet_height_mm=297.0,
    margin_left_mm=20.0,
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
