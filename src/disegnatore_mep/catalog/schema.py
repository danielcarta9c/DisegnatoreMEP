from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.types import Domain, PortFlow


class PortDefinition(StrictModel):
    """Semantica di una porta. La geometria vive nel manifesto del simbolo."""

    id: str = Field(pattern=ID_PATTERN)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    flow: PortFlow
    required: bool = True
    max_connections: int = Field(default=1, ge=1)


class ComponentDefinition(StrictModel):
    """Voce di catalogo versionata che descrive un componente e le sue porte.

    Gli identificativi di catalogo sono uno spazio di nomi distinto da quelli
    di progetto portati da `IdentifiedModel`, quindi questo modello dichiara
    un proprio `id` invece di ereditare quella base.
    """

    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    functions: list[str] = Field(min_length=1)
    symbol_id: str = Field(pattern=ID_PATTERN)
    composite: bool = False
    ports: list[PortDefinition] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)

    @property
    def port_ids(self) -> frozenset[str]:
        return frozenset(port.id for port in self.ports)

    @model_validator(mode="after")
    def port_ids_are_unique(self) -> "ComponentDefinition":
        ids = [port.id for port in self.ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate port id")
        return self
