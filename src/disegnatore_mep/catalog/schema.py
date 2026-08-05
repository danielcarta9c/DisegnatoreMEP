"""Come e' fatta una voce di catalogo, e cosa dichiara di se'.

Due vocabolari, e non sono la stessa cosa:

- **`functions`**, cosa il componente *fa* nell'impianto — generare calore,
  intercettare, accumulare. E' aperto: una famiglia nuova porta la propria
  etichetta.
- **`traits`**, i **fatti** che una regola deve conoscere per ragionare sul
  componente **senza nominarlo** (D-069, D-090): si manutiene, sporca il
  circuito, produce aria, non si isola mai. E' **chiuso**: un fatto scritto male
  non sparisce in silenzio, fa fallire il caricamento del catalogo.

La differenza sta tutta in una frase: una funzione dice *chi sei*, una proprieta'
dice *cosa e' vero di te*. «Tutto cio' che si manutiene vuole le proprie valvole»
e' una regola generale solo se esiste qualcuno che dichiara di manutenersi.
"""

from enum import StrEnum

from pydantic import Field, model_validator

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.types import Domain, PortFlow


class ComponentTrait(StrEnum):
    """Il vocabolario chiuso delle proprieta' dichiarate (P1).

    Ogni voce e' un **fatto sul componente**, mai il nome di un componente: se
    una proprieta' valesse per un pezzo solo, sarebbe quel pezzo scritto in un
    altro modo, e la regola che la legge tornerebbe particolare (D-090).

    Il testo in italiano di ciascuna, per il committente, sta in
    `docs/prodotto/PROPRIETA_COMPONENTI.md`.
    """

    MAINTAINABLE = "maintainable"
    """Si smonta o si sostituisce, **e per farlo va isolato dal fluido**.

    Il seguito della frase non e' un dettaglio: e' cio' che distingue un filtro,
    che si pulisce a impianto pieno e quindi vuole le proprie valvole, da una
    valvola di intercettazione, che si sostituisce ma non chiede a sua volta due
    valvole per essere sostituita. Senza quel taglio, la regola generale
    dell'intercettazione entrerebbe in regresso infinito.
    """

    FOULS_CIRCUIT = "fouls_circuit"
    """Produce fanghi, ossidi o residui che viaggiano con l'acqua di ritorno."""

    NEEDS_DEBRIS_PROTECTION = "needs_debris_protection"
    """Ha organi che i residui rovinano: va protetto su cio' che gli entra."""

    PRODUCES_AIR = "produces_air"
    """Scalda l'acqua e quindi ne libera l'aria disciolta."""

    NEEDS_OVERPRESSURE_PROTECTION = "needs_overpressure_protection"
    """Chiude dentro di se' un volume d'acqua che, scaldandosi, va in pressione."""

    HOLDS_DRAINABLE_VOLUME = "holds_drainable_volume"
    """Contiene un volume di fluido che deve poter essere svuotato."""

    ISOLATION_NORMAL = "isolation_normal"
    """Regime di intercettazione ordinario: lo isola una valvola comune."""

    ISOLATION_NEVER = "isolation_never"
    """Non si isola mai: fra lui e cio' che serve non ci va nulla di chiudibile."""

    ISOLATION_LOCKABLE_ONLY = "isolation_lockable_only"
    """Si isola solo con valvola bloccabile o piombabile, che non si chiude per
    distrazione."""

    ATTACHMENT_INLINE = "attachment_inline"
    """Sta sul percorso del tubo: il fluido ci passa dentro o ci arriva."""

    ATTACHMENT_BRANCH = "attachment_branch"
    """Pende dal tubo con una propria derivazione, e non e' un organo di
    passaggio."""


ISOLATION_REGIMES: frozenset[ComponentTrait] = frozenset(
    {
        ComponentTrait.ISOLATION_NORMAL,
        ComponentTrait.ISOLATION_NEVER,
        ComponentTrait.ISOLATION_LOCKABLE_ONLY,
    }
)
"""I tre modi in cui un componente si lascia isolare. Uno e' obbligatorio: senza,
un default implicito deciderebbe al posto di chi compila il catalogo (D-094)."""

ATTACHMENT_STYLES: frozenset[ComponentTrait] = frozenset(
    {ComponentTrait.ATTACHMENT_INLINE, ComponentTrait.ATTACHMENT_BRANCH}
)
"""In linea oppure su stacco. Uno e' obbligatorio: e' il primo vincolo con cui
l'assemblatore costruisce la catena, e la catena e' un albero solo perche' esiste
lo stacco (D-094)."""


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
    traits: list[ComponentTrait] = Field(min_length=1)
    """Cio' che e' vero del componente. Obbligatorio, e senza default: un
    componente che non dice come si isola non si carica affatto."""

    symbol_id: str = Field(pattern=ID_PATTERN)
    composite: bool = False
    ports: list[PortDefinition] = Field(min_length=1)
    sources: list[str] = Field(min_length=1)

    @property
    def port_ids(self) -> frozenset[str]:
        return frozenset(port.id for port in self.ports)

    @property
    def trait_set(self) -> frozenset[ComponentTrait]:
        return frozenset(self.traits)

    @property
    def isolation_regime(self) -> ComponentTrait:
        """Come lo si isola. Esiste sempre: lo garantisce la validazione."""
        return next(iter(self.trait_set & ISOLATION_REGIMES))

    @property
    def attachment(self) -> ComponentTrait:
        """In linea o su stacco. Esiste sempre: lo garantisce la validazione."""
        return next(iter(self.trait_set & ATTACHMENT_STYLES))

    def has_trait(self, trait: ComponentTrait) -> bool:
        return trait in self.trait_set

    @model_validator(mode="after")
    def port_ids_are_unique(self) -> "ComponentDefinition":
        ids = [port.id for port in self.ports]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate port id")
        return self

    @model_validator(mode="after")
    def traits_are_declared_once(self) -> "ComponentDefinition":
        seen = sorted({item for item in self.traits if self.traits.count(item) > 1})
        if seen:
            raise ValueError(f"{self.id} declares the same trait twice: {', '.join(seen)}")
        return self

    @model_validator(mode="after")
    def exactly_one_isolation_regime(self) -> "ComponentDefinition":
        return self._exactly_one(
            ISOLATION_REGIMES,
            "isolation regime",
            "how it is isolated, and there is no implicit default",
        )

    @model_validator(mode="after")
    def exactly_one_attachment_style(self) -> "ComponentDefinition":
        return self._exactly_one(
            ATTACHMENT_STYLES,
            "attachment style",
            "whether the pipe runs through it or it hangs off a branch",
        )

    def _exactly_one(
        self, group: frozenset[ComponentTrait], label: str, because: str
    ) -> "ComponentDefinition":
        declared = sorted(self.trait_set & group)
        if not declared:
            raise ValueError(
                f"{self.id} declares no {label}: every component must say "
                f"{because}. Declare one of: {', '.join(sorted(group))}"
            )
        if len(declared) > 1:
            raise ValueError(f"{self.id} declares more than one {label}: {', '.join(declared)}")
        return self

    @model_validator(mode="after")
    def never_isolated_is_not_maintainable(self) -> "ComponentDefinition":
        """Le due proprieta' si contraddicono, e la contraddizione e' silenziosa.

        `maintainable` significa «per smontarlo va isolato»; `isolation_never`
        significa «non lo si isola mai». Un componente che dichiarasse entrambe
        chiederebbe alla regola dell'intercettazione una valvola che un'altra
        proprieta' vieta, e la fila uscirebbe sbagliata senza che nessuno se ne
        accorga.
        """
        if self.has_trait(ComponentTrait.MAINTAINABLE) and self.has_trait(
            ComponentTrait.ISOLATION_NEVER
        ):
            raise ValueError(
                f"{self.id} declares both {ComponentTrait.MAINTAINABLE} and "
                f"{ComponentTrait.ISOLATION_NEVER}: the first asks for the "
                f"valves that the second forbids"
            )
        return self


__all__ = [
    "ATTACHMENT_STYLES",
    "ISOLATION_REGIMES",
    "ComponentDefinition",
    "ComponentTrait",
    "PortDefinition",
]
