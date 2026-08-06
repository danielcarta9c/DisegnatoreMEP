"""La vista che unisce la semantica del catalogo alla geometria del simbolo.

La verifica incrociata di `ComponentRegistry` dimostra al caricamento che i due
insiemi di porte coincidono, poi butta via l'accoppiamento: senza questa vista
non esiste modo supportato di passare da un componente alla sua geometria. Il
layout ne ha bisogno a ogni passo — per sapere quanto e' grande un componente,
dove sono i suoi attacchi, verso dove guardano e se spezza la linea su cui sta.
"""

from dataclasses import dataclass

from disegnatore_mep.graphics.registry import Symbol
from disegnatore_mep.graphics.symbol import SymbolPort

from .errors import CatalogError
from .schema import ComponentDefinition, PortDefinition


@dataclass(frozen=True)
class ResolvedPort:
    """Le due meta' di una porta: cosa ci passa, e dove sta sul riquadro."""

    definition: PortDefinition
    geometry: SymbolPort

    @property
    def id(self) -> str:
        return self.definition.id


@dataclass(frozen=True)
class ResolvedComponent:
    definition: ComponentDefinition
    symbol: Symbol

    def __post_init__(self) -> None:
        # Riasserito invece di presunto: il registro fa gia' questo controllo,
        # ma una vista costruita a mano non deve poter mentire (D-037).
        if self.definition.port_ids != self.symbol.manifest.port_ids:
            raise CatalogError(
                f"port ids do not match between definition {self.definition.id} "
                f"and symbol {self.symbol.manifest.id}: "
                f"{sorted(self.definition.port_ids)} vs "
                f"{sorted(self.symbol.manifest.port_ids)}"
            )

    @property
    def port_ids(self) -> frozenset[str]:
        return self.definition.port_ids

    @property
    def is_inline(self) -> bool:
        """Se il componente spezza la linea su cui sta (D-027)."""
        return self.symbol.manifest.is_inline

    @property
    def box_mm(self) -> tuple[float, float]:
        return (self.symbol.manifest.width_mm, self.symbol.manifest.height_mm)

    def port(self, port_id: str) -> ResolvedPort:
        definition = next(
            (item for item in self.definition.ports if item.id == port_id), None
        )
        if definition is None:
            raise CatalogError(
                f"unknown port {port_id} on component definition {self.definition.id}"
            )
        # Non puo' fallire: __post_init__ ha gia' provato che gli insiemi
        # coincidono. Tradotto comunque, perche' SymbolError non e' l'errore
        # che i chiamanti di questo modulo catturano.
        return ResolvedPort(
            definition=definition, geometry=self.symbol.manifest.port(port_id)
        )

    def ports(self) -> tuple[ResolvedPort, ...]:
        return tuple(self.port(item.id) for item in self.definition.ports)
