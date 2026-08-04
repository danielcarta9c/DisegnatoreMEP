"""Come e' fatta una regola.

La specifica §9 elenca cosa una regola deve dichiarare. Qui quell'elenco diventa
un modello stretto, cosi' che una regola incompleta non si carichi affatto
invece di fallire a meta' valutazione.

Due campi non stavano nella specifica e sono stati aggiunti dopo averli visti
mancare prototipando (§2 del piano P1):

- **`cardinality`**, perche' una regola senza cardinalita' propone lo stesso
  pezzo una volta per ogni attacco. Il vaso di espansione e' uscito due volte da
  una pompa di calore con due ritorni;
- **`satisfied_by`**, perche' senza un criterio di soddisfazione rieseguire le
  regole su un modello gia' completato ripropone tutto da capo.

Il vincolo che governa il resto: **una condizione non puo' nominare un
componente**. Parla di funzioni di catalogo, domini e fluidi. Se potesse dire
«se c'e' una pompa di calore», il prodotto tornerebbe un catalogo di schemi
tipo, che e' esattamente cio' che il gate G0 ha dimostrato di non essere.
"""

from enum import StrEnum

from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.types import Domain, IntegrationCategory, PortFlow


class RuleCardinality(StrEnum):
    """Quante volte una regola puo' proporre lo stesso pezzo."""

    PER_NETWORK = "per_network"
    """Una volta per rete: il vaso di espansione di un circuito chiuso."""

    PER_COMPONENT = "per_component"
    """Una volta per componente ancorante: il filtro a monte di ogni circolatore."""

    PER_PORT = "per_port"
    """Una per attacco: le valvole di sezionamento di un componente sostituibile."""


class Placement(StrEnum):
    """Su quale attacco dell'ancoraggio si posa la proposta.

    La posizione e' **topologica**, mai in millimetri: dove finisca sulla tavola
    lo decide il layout, e il modello tecnico non contiene coordinate (D-026).
    """

    ON_INLET = "on_inlet"
    """Sulla tubazione che entra: il ritorno di un generatore, l'aspirazione di
    una pompa."""

    ON_OUTLET = "on_outlet"
    """Sulla tubazione che esce: la mandata di un generatore."""

    ON_ANY_PORT = "on_any_port"
    """Su ogni attacco, qualunque verso: il sezionamento."""

    @property
    def flows(self) -> tuple[PortFlow, ...]:
        return {
            Placement.ON_INLET: (PortFlow.IN,),
            Placement.ON_OUTLET: (PortFlow.OUT,),
            Placement.ON_ANY_PORT: (PortFlow.IN, PortFlow.OUT, PortFlow.BIDIRECTIONAL),
        }[self]


class RuleCondition(StrictModel):
    """Quando una regola si attiva. Solo funzioni, domini e fluidi."""

    network_domain: Domain
    network_medium: str | None = Field(default=None, pattern=ID_PATTERN)
    network_has_function: str | None = None
    network_lacks_function: str | None = None
    anchor_has_function: str
    """La funzione del componente a cui la proposta si ancora."""


class RuleProposalTemplate(StrictModel):
    """Cosa si propone e su quale attacco dell'ancoraggio."""

    definition_id: str = Field(pattern=ID_PATTERN)
    placement: Placement
    inlet_port: str = Field(pattern=ID_PATTERN)
    outlet_port: str = Field(pattern=ID_PATTERN)

    @model_validator(mode="after")
    def the_two_ports_differ(self) -> "RuleProposalTemplate":
        if self.inlet_port == self.outlet_port:
            raise ValueError(
                "an inline accessory needs two distinct ports: the run enters one "
                "and leaves the other"
            )
        return self


class SatisfactionCriterion(StrictModel):
    """Come si riconosce che quello che la regola propone c'e' gia'.

    In termini di **funzioni**, non di identificativi: «questa rete ha gia' un
    componente che espande», non «esiste il componente vaso-01».
    """

    network_has_function: str | None = None
    port_carries_function: str | None = None
    """L'accessorio e' gia' sulla tubazione che tocca quell'attacco."""

    @model_validator(mode="after")
    def at_least_one_criterion(self) -> "SatisfactionCriterion":
        if self.network_has_function is None and self.port_carries_function is None:
            raise ValueError(
                "a satisfaction criterion that checks nothing makes the engine "
                "propose the same accessory again at every run"
            )
        return self


class RuleDefinition(StrictModel):
    """Una regola, con tutto cio' che §9 le impone di dichiarare."""

    id: str = Field(pattern=ID_PATTERN)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(min_length=1)
    """Italiano: e' quello che l'ingegnere legge nel dossier (D-051)."""

    category: IntegrationCategory
    cardinality: RuleCardinality
    when: RuleCondition
    then: RuleProposalTemplate
    satisfied_by: SatisfactionCriterion
    rationale: str = Field(min_length=1)
    source: str = Field(min_length=1)
    """La fonte, e deve dire il vero: «buona pratica tecnica documentata» con un
    riferimento puntuale vale piu' di una citazione normativa gonfiata (D-066)."""


__all__ = [
    "Placement",
    "RuleCardinality",
    "RuleCondition",
    "RuleDefinition",
    "RuleProposalTemplate",
    "SatisfactionCriterion",
]
