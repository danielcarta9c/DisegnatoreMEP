from typing import Literal

from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.types import Domain, PortFlow


class SymbolGeometry(StrictModel):
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    clearance_mm: float = Field(ge=0)
    allowed_rotations_deg: list[int] = Field(min_length=1)
    inline_gap_mm: float | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def rotations_are_orthogonal(self) -> "SymbolGeometry":
        allowed = {0, 90, 180, 270}
        if not set(self.allowed_rotations_deg).issubset(allowed):
            raise ValueError("allowed rotations must be 0, 90, 180 or 270")
        if len(self.allowed_rotations_deg) != len(set(self.allowed_rotations_deg)):
            raise ValueError("duplicate allowed rotation")
        return self


class PortDefinition(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    flow: PortFlow
    x_mm: float
    y_mm: float
    angle_deg: Literal[0, 90, 180, 270]
    required: bool = True
    max_connections: int = Field(default=1, ge=1)


class ComponentDefinition(StrictModel):
    """Versioned catalog entry describing a component and its ports.

    Catalog identifiers are a separate namespace from the project-wide
    identifiers carried by `IdentifiedModel`, so this model declares its
    own `id` rather than inheriting that base.
    """

    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    functions: list[str] = Field(min_length=1)
    symbol_id: str = Field(pattern=ID_PATTERN)
    composite: bool = False
    geometry: SymbolGeometry
    ports: list[PortDefinition] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def port_ids_are_unique_and_inside_geometry(self) -> "ComponentDefinition":
        ids = [port.id for port in self.ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate port id")
        for port in self.ports:
            if not 0 <= port.x_mm <= self.geometry.width_mm:
                raise ValueError(f"port outside symbol width: {port.id}")
            if not 0 <= port.y_mm <= self.geometry.height_mm:
                raise ValueError(f"port outside symbol height: {port.id}")
        return self
