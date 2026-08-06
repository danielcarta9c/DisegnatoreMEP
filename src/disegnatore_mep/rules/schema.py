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

Il vincolo che governa il resto: **una regola non puo' nominare un componente**.
Parla di **proprieta' dichiarate** (P1), di funzioni di catalogo, di domini e di
fluidi. Se potesse dire «se c'e' una pompa di calore», il prodotto tornerebbe un
catalogo di schemi tipo, che e' esattamente cio' che il gate G0 ha dimostrato di
non essere.

**P2 chiude l'ultima falla di D-069.** Prima una regola diceva *quale pezzo*
proporre, e quel campo era «l'unica eccezione». Non lo e' piu': una regola
dichiara la **funzione** che deve comparire, e il catalogo risolve con quale
pezzo si ottiene sul fluido di quella rete. E' anche la ragione tecnica per cui
sei regole di intercettazione — una per macchina e per fluido — tornano a essere
**una sola** (D-090).
"""

from enum import StrEnum

from pydantic import Field, model_validator

from disegnatore_mep.catalog.schema import SHUTOFF_REGIMES, ComponentTrait
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
    """Quando una regola si attiva. Proprieta', funzioni, domini e fluidi."""

    network_domain: Domain
    network_medium: str | None = Field(default=None, pattern=ID_PATTERN)
    network_has_function: str | None = None
    network_lacks_function: str | None = None
    anchor_has_trait: ComponentTrait | None = None
    """La **proprieta' dichiarata** del componente a cui la proposta si ancora.

    E' la forma generale: «tutto cio' che si smonta in esercizio», «tutto cio'
    che i residui rovinano». Una regola scritta cosi' non conosce le macchine e
    non va riscritta quando ne entra una nuova in catalogo (D-090)."""

    anchor_has_function: str | None = None
    """La funzione del componente a cui la proposta si ancora.

    Resta per i casi in cui la ragione dell'accessorio non e' un fatto del pezzo
    ma **cio' che il pezzo fa**: la temperatura di mandata si legge dove il
    calore entra nell'acqua, e nessuna proprieta' dice «genera calore»."""

    network_carries_what_the_anchor_stores: bool = False
    """La rete deve portare il fluido che l'ancoraggio tiene **in serbo**.

    Serve dove l'accessorio ha a che fare con la riserva e non con i circuiti
    che la attraversano: uno scarico su un serpentino svuota il circuito di
    riscaldamento e lascia il serbatoio pieno. E' una condizione fra proprieta'
    dichiarate — quello che il pezzo tiene, quello che la rete porta — e non
    nomina ne' un componente ne' un attacco."""

    @model_validator(mode="after")
    def the_anchor_is_identified(self) -> "RuleCondition":
        if self.anchor_has_trait is None and self.anchor_has_function is None:
            raise ValueError(
                "a rule must say what it anchors to, by declared property or by "
                "function: without either it would fire on every component of "
                "the network"
            )
        return self


class RuleProposalTemplate(StrictModel):
    """Cosa si propone e su quale attacco dell'ancoraggio.

    **Una funzione, non un pezzo.** Quale voce di catalogo la porti su quel
    fluido lo sa il catalogo: e' cosi' che una sola regola vale sull'acqua di
    riscaldamento, sulla fredda e sulla sanitaria.
    """

    provides_function: str
    """La funzione che deve comparire su quell'attacco."""

    provides_function_by_shutoff_regime: dict[ComponentTrait, str] = Field(
        default_factory=dict
    )
    """L'organo cambia quando il regime dell'ancoraggio lo impone.

    Cio' che non deve mai restare escluso per distrazione — un vaso di
    espansione — non si chiude con l'organo comune ma con uno bloccabile
    aperto. E' la stessa regola, non un'eccezione scritta nel motore: il
    regime lo dichiara il componente (P1), la regola dice solo quale organo
    ciascun regime pretende.
    """

    placement: Placement
    inlet_port: str = Field(pattern=ID_PATTERN)
    outlet_port: str = Field(pattern=ID_PATTERN)

    def function_for(self, regime: ComponentTrait) -> str:
        """La funzione da proporre a un ancoraggio con quel regime."""
        return self.provides_function_by_shutoff_regime.get(regime, self.provides_function)

    def functions(self) -> tuple[str, ...]:
        """Tutte le funzioni che questa regola puo' proporre, in ordine."""
        return (
            self.provides_function,
            *sorted(set(self.provides_function_by_shutoff_regime.values())),
        )

    @model_validator(mode="after")
    def the_two_ports_differ(self) -> "RuleProposalTemplate":
        if self.inlet_port == self.outlet_port:
            raise ValueError(
                "an inline accessory needs two distinct ports: the run enters one "
                "and leaves the other"
            )
        return self

    @model_validator(mode="after")
    def the_regimes_are_regimes(self) -> "RuleProposalTemplate":
        unknown = sorted(
            item
            for item in self.provides_function_by_shutoff_regime
            if item not in SHUTOFF_REGIMES
        )
        if unknown:
            raise ValueError(
                f"provides_function_by_shutoff_regime is keyed by how a component "
                f"lets itself be shut off, and {', '.join(unknown)} is not one of "
                f"those: {', '.join(sorted(SHUTOFF_REGIMES))}"
            )
        if ComponentTrait.SHUTOFF_NEVER in self.provides_function_by_shutoff_regime:
            raise ValueError(
                f"{ComponentTrait.SHUTOFF_NEVER} means nothing closable may sit "
                f"between it and what it protects: naming an organ for it would "
                f"be the rule contradicting the property"
            )
        return self


class SatisfactionScope(StrEnum):
    """Dove si guarda per sapere che cio' che la regola propone c'e' gia'.

    La **funzione** cercata non si dichiara: e' quella che la regola propone su
    quell'ancoraggio. Prima si scrivevano due volte, e nulla impediva a una
    regola di proporre una cosa e di dichiararsi soddisfatta da un'altra —
    cioe' di riproporre la stessa cosa a ogni passata.
    """

    ON_THE_ATTACHMENT = "on_the_attachment"
    """Sulla tubazione che tocca quell'attacco: l'accessorio e' gia' li'."""

    ON_THE_NETWORK = "on_the_network"
    """Da qualche parte su quella rete: un circuito chiuso vuole **un** vaso di
    espansione, non uno per attacco."""


class SatisfactionCriterion(StrictModel):
    """Come si riconosce che quello che la regola propone c'e' gia' (D-070)."""

    scope: SatisfactionScope


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
    """Il perche' impiantistico, e **in che punto della catena** l'accessorio va
    e perche' proprio li'. Non «l'esempio faceva cosi'», e niente che riguardi
    la taglia del foglio (D-074, D-092)."""

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
    "SatisfactionScope",
]
