"""Come e' fatta una voce di catalogo, e cosa dichiara di se'.

Due vocabolari, e non sono la stessa cosa:

- **`functions`**, cosa il componente *fa* nell'impianto — generare calore,
  intercettare, accumulare. E' aperto: una famiglia nuova porta la propria
  etichetta.
- **`traits`**, i **fatti** che una regola deve conoscere per ragionare sul
  componente **senza nominarlo** (D-069, D-090): si manutiene, sporca il
  circuito, non si chiude mai. E' **chiuso**: un fatto scritto male non sparisce
  in silenzio, fa fallire il caricamento del catalogo.

La differenza sta tutta in una frase: una funzione dice *chi sei*, una proprieta'
dice *cosa e' vero di te*. «Tutto cio' che si manutiene vuole le proprie valvole»
e' una regola generale solo se esiste qualcuno che dichiara di manutenersi.

I nomi delle proprieta' evitano di proposito le parole con cui si chiamano i
componenti: la prova in `tests/catalog/test_traits.py` li confronta parola per
parola con gli identificativi e i nomi di catalogo, nelle due direzioni.
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
    """Si smonta **in esercizio**, e per farlo va chiuso il fluido attorno.

    I due pezzi della frase contano entrambi. *In esercizio*: un'unita' su una
    linea frigorifera o un ventilatore su un canale si sostituiscono a impianto
    fermo, non chiudendo un rubinetto, e quindi non hanno questa proprieta'.
    *Va chiuso il fluido attorno*: distingue un filtro, che si pulisce a
    impianto pieno e percio' vuole le proprie valvole, da una valvola di
    intercettazione o da un ritegno, che si sostituiscono a tratta gia' chiusa e
    non chiedono a loro volta due valvole — se lo facessero, quelle due ne
    vorrebbero altre quattro, senza fine.
    """

    FOULS_CIRCUIT = "fouls_circuit"
    """Produce fanghi, ossidi o residui che viaggiano con l'acqua di ritorno."""

    NEEDS_DEBRIS_PROTECTION = "needs_debris_protection"
    """Ha organi che i residui rovinano: va protetto su cio' che gli entra."""

    PRODUCES_AIR = "produces_air"
    """Scalda il fluido e quindi ne libera l'aria che teneva disciolta."""

    NEEDS_OVERPRESSURE_PROTECTION = "needs_overpressure_protection"
    """Chiude dentro di se' un volume di fluido che, scaldandosi, spinge oltre
    il limite ammesso: gli serve una via che si apra da sola."""

    HOLDS_ITS_OWN_VOLUME = "holds_its_own_volume"
    """Ha un volume di fluido **proprio**, distinto da quello del circuito.

    E' il criterio che separa un serbatoio da un tratto di tubo: il tubo
    contiene fluido solo perche' ce lo si fa passare, il serbatoio ne tiene una
    riserva anche quando nulla circola — e percio' lo si deve poter svuotare da
    solo, senza svuotare l'impianto.

    Chi la dichiara deve anche dire **quale** fluido tiene in serbo, in
    `stored_medium`: senza, «svuotare il serbatoio» e «svuotare un circuito che
    lo attraversa» sono la stessa frase, e lo scarico finisce sul serpentino
    invece che sulla riserva.
    """

    SHUTOFF_ORDINARY = "shutoff_ordinary"
    """Regime ordinario: se lo si deve chiudere, basta un organo comune."""

    SHUTOFF_NEVER = "shutoff_never"
    """Non lo si chiude mai: fra lui e cio' che protegge non ci va nulla di
    chiudibile. E' un vincolo di sicurezza, non una comodita' di esercizio."""

    SHUTOFF_LOCKABLE_ONLY = "shutoff_lockable_only"
    """Lo si chiude solo con un organo bloccabile o piombabile, che non si
    chiude per distrazione."""

    ATTACHMENT_INLINE = "attachment_inline"
    """Sta sul percorso del tubo: il fluido ci passa dentro o ci arriva."""

    ATTACHMENT_BRANCH = "attachment_branch"
    """Pende dal tubo con una propria derivazione, e non e' un organo di
    passaggio."""


SHUTOFF_REGIMES: frozenset[ComponentTrait] = frozenset(
    {
        ComponentTrait.SHUTOFF_ORDINARY,
        ComponentTrait.SHUTOFF_NEVER,
        ComponentTrait.SHUTOFF_LOCKABLE_ONLY,
    }
)
"""I tre modi in cui un componente si lascia chiudere. Uno e' obbligatorio:
senza, un valore sottinteso deciderebbe al posto di chi compila il catalogo
(D-094)."""

FITTING_FUNCTIONS: frozenset[str] = frozenset({"junction", "branch_off"})
"""I due mestieri di un raccordo: unire due tubazioni, o aprire una derivazione.

Non e' un elenco di pezzi, e non lo diventera': sono **funzioni**, e quale voce
di catalogo le porti su un dato fluido lo dice il catalogo (D-069). Un raccordo
non e' un apparecchio, e chi cammina lungo un tubo ci passa attraverso."""

ATTACHMENT_STYLES: frozenset[ComponentTrait] = frozenset(
    {ComponentTrait.ATTACHMENT_INLINE, ComponentTrait.ATTACHMENT_BRANCH}
)
"""In linea oppure su stacco. Uno e' obbligatorio: e' il primo vincolo con cui
si costruisce la sequenza dei pezzi lungo un tubo (D-094)."""


class PortDefinition(StrictModel):
    """Semantica di una porta. La geometria vive nel manifesto del simbolo.

    **Una porta porta una tubazione sola** (D-100), e non e' configurabile: due
    tubazioni sullo stesso attacco vorrebbero dire due tubi sullo stesso
    bocchello. Dove due tubazioni si incontrano c'e' un pezzo che le unisce, con
    la propria sigla. Il catalogo poteva dichiarare un massimo per porta, e i due
    posti in cui dichiarava due erano esattamente i due punti in cui il modello
    stava rappresentando un raccordo che non aveva.
    """

    id: str = Field(pattern=ID_PATTERN)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    flow: PortFlow
    required: bool = True

    stub: bool = False
    """Questo attacco e' uno **stacco**: non fa parte del percorso del fluido.

    Chi cammina lungo una tubazione — per sapere se un pezzo si puo' chiudere, o
    cosa c'e' fra una sicurezza e la macchina — deve saperlo, altrimenti a ogni
    raccordo perde la strada e infila la derivazione al posto della corsa.

    Un attacco che dichiara `serves` e' uno stacco per definizione. Questo campo
    serve agli stacchi **senza** una funzione dichiarata: il braccio di un
    raccordo e' uno stacco, ma cosa ci pendera' lo decide l'impianto, non il
    pezzo.
    """

    serves: str | None = None
    """La funzione per cui questo attacco esiste, se e' un attacco **di servizio**.

    Un volano a quattro tubi non ha quattro attacchi (D-101): ha i quattro del
    flusso principale, che qui non dichiarano niente, e poi quelli di servizio —
    lo scarico, lo sfiato, la sede della sonda, la ricarica, il vaso — che
    esistono ciascuno per una funzione precisa e la dichiarano qui.

    E' cosi' che un accessorio di servizio si posa **sul proprio attacco** invece
    di essere infilato nella tubazione principale: la regola dice quale funzione
    deve comparire, la macchina dice su quale suo attacco quella funzione si
    attacca. La regola continua a non nominare nessun componente.
    """

    @property
    def is_service(self) -> bool:
        """Attacco di servizio: esiste per una funzione dichiarata."""
        return self.serves is not None

    @property
    def off_the_run(self) -> bool:
        """Non e' sul percorso del fluido: e' uno stacco, di qualunque specie."""
        return self.stub or self.is_service


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
    """Cio' che e' vero del componente. Obbligatorio, e senza valore
    sottinteso: un componente che non dice come si chiude non si carica."""

    carries_on_board: list[str] = Field(default_factory=list)
    """Le funzioni che la macchina **integra di fabbrica**, quando ne integra.

    E' un fatto della macchina e lo dichiara il suo catalogo, macchina per
    macchina: le monoblocco comuni portano a bordo il circolatore primario
    (D-106), e la fonte dice esplicitamente che l'integrazione **varia** —
    «possono essere integrati nella macchina alcuni elementi del circuito
    idraulico» (SRC-019, p. 15). Una regola non aggiunge cio' che la macchina
    dichiara di avere: per la soddisfazione di rete, una funzione portata a
    bordo da un membro conta come presente.

    Non e' l'elenco dei mestieri (`functions`): un mestiere dice cosa il
    componente fa nell'impianto, questo dice quali pezzi **non vanno
    disegnati** perche' stanno gia' dentro il mantello.
    """

    stored_medium: str | None = Field(default=None, pattern=ID_PATTERN)
    """Il fluido che il componente tiene **in serbo**, quando ne tiene uno.

    Non e' una proprieta' del vocabolario chiuso ma il suo complemento: la
    proprieta' dice *che* c'e' una riserva, questo dice *di che cosa*. Serve
    perche' un serbatoio e' spesso attraversato anche da un altro fluido — un
    serpentino e' uno scambiatore che passa dentro la riserva, non la riserva —
    e senza distinguerli lo scarico va a finire sul circuito sbagliato.

    Si dichiara se e solo se il componente dichiara di tenere un volume proprio,
    e dev'essere uno dei fluidi delle sue porte: un serbatoio che tenesse in
    serbo un fluido che non tocca sarebbe una dichiarazione senza appigli.
    """

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
    def shutoff_regime(self) -> ComponentTrait:
        """Come lo si chiude. Esiste sempre: lo garantisce la validazione."""
        return next(iter(self.trait_set & SHUTOFF_REGIMES))

    @property
    def attachment(self) -> ComponentTrait:
        """In linea o su stacco. Esiste sempre: lo garantisce la validazione."""
        return next(iter(self.trait_set & ATTACHMENT_STYLES))

    @property
    def is_a_fitting(self) -> bool:
        """Non e' un apparecchio: e' un raccordo, e il fluido ci passa e basta.

        Serve a chi **cammina** lungo una tubazione. Un raccordo non interrompe
        la linea sul disegno — il suo segno e' un pallino, non un corpo — quindi
        il simbolo non lo dichiara in linea; ma la corsa ci passa attraverso, e
        una camminata che si fermasse li' direbbe che una macchina non si puo'
        chiudere solo perche' fra lei e la sua valvola c'e' un T.

        Si riconosce dal **mestiere**, mai dal nome: unire due tubazioni, o
        aprire una derivazione. Sono le uniche due cose che un raccordo fa.
        """
        return bool(FITTING_FUNCTIONS & set(self.functions))

    @property
    def attaches_on_a_branch(self) -> bool:
        """Pende da uno stacco invece di stare sul percorso del tubo.

        Chi lo fa non spezza la tubazione: si appende all'attacco di servizio
        della macchina, o a una derivazione della tubazione (D-101)."""
        return self.attachment is ComponentTrait.ATTACHMENT_BRANCH

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
            raise ValueError(f"{self.id} dichiara due volte la stessa proprietà: {', '.join(seen)}")
        return self

    @model_validator(mode="after")
    def exactly_one_shutoff_regime(self) -> "ComponentDefinition":
        return self._exactly_one(
            SHUTOFF_REGIMES,
            "il regime di intercettazione",
            "come lo si chiude, e non esiste un valore sottinteso",
        )

    @model_validator(mode="after")
    def exactly_one_attachment_style(self) -> "ComponentDefinition":
        return self._exactly_one(
            ATTACHMENT_STYLES,
            "come si attacca",
            "se il tubo ci passa dentro o se pende da uno stacco",
        )

    def _exactly_one(
        self, group: frozenset[ComponentTrait], label: str, because: str
    ) -> "ComponentDefinition":
        declared = sorted(self.trait_set & group)
        if not declared:
            raise ValueError(
                f"{self.id} non dichiara {label}: ogni componente deve dire "
                f"{because}. Dichiararne una fra: {', '.join(sorted(group))}"
            )
        if len(declared) > 1:
            raise ValueError(
                f"{self.id} dichiara più di una scelta per {label}: {', '.join(declared)}"
            )
        return self

    @model_validator(mode="after")
    def on_board_is_not_the_job(self) -> "ComponentDefinition":
        """Cio' che sta a bordo non e' un mestiere del componente.

        Dichiarare la stessa funzione nei due elenchi vorrebbe dire che il
        pezzo la fa **e** la porta integrata: una delle due e' falsa, e la
        contraddizione va fermata al caricamento invece che scoperta quando
        una regola conta due volte la stessa cosa.
        """
        repeated = sorted(
            {item for item in self.carries_on_board if self.carries_on_board.count(item) > 1}
        )
        if repeated:
            raise ValueError(
                f"{self.id} dichiara due volte a bordo: {', '.join(repeated)}"
            )
        both = sorted(set(self.carries_on_board) & set(self.functions))
        if both:
            raise ValueError(
                f"{self.id} dichiara {', '.join(both)} sia come mestiere sia come "
                f"integrazione di bordo: un mestiere lo si fa nell'impianto, "
                f"un'integrazione sta dentro il mantello — una delle due"
            )
        empty = [item for item in self.carries_on_board if not item.strip()]
        if empty:
            raise ValueError(f"{self.id} dichiara a bordo una funzione senza nome")
        return self

    @model_validator(mode="after")
    def a_reserve_says_what_it_holds(self) -> "ComponentDefinition":
        """Chi tiene una riserva dice di che cosa, e chi non ne tiene tace.

        Il difetto che questa regola rende impossibile: un bollitore dichiarava
        di tenere un volume proprio senza dire quale, e lo scarico gli e' finito
        sul ritorno del serpentino — cioe' svuotava il circuito di
        riscaldamento, mentre l'acqua sanitaria restava dentro.
        """
        holds = self.has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
        if holds and self.stored_medium is None:
            raise ValueError(
                f"{self.id} dichiara {ComponentTrait.HOLDS_ITS_OWN_VOLUME} senza "
                f"dire quale fluido tiene in serbo: senza, svuotare la riserva e "
                f"svuotare un circuito che la attraversa sono la stessa cosa. "
                f"Dichiarare stored_medium fra: "
                f"{', '.join(sorted({port.medium for port in self.ports}))}"
            )
        if not holds and self.stored_medium is not None:
            raise ValueError(
                f"{self.id} dichiara di tenere in serbo {self.stored_medium} ma non "
                f"dichiara {ComponentTrait.HOLDS_ITS_OWN_VOLUME}: un fluido tenuto "
                f"in serbo da chi non ha una riserva non vuol dire niente"
            )
        media = {port.medium for port in self.ports}
        if self.stored_medium is not None and self.stored_medium not in media:
            raise ValueError(
                f"{self.id} dichiara di tenere in serbo {self.stored_medium}, che "
                f"non e' il fluido di nessuna delle sue porte "
                f"({', '.join(sorted(media))}): la riserva non avrebbe da dove "
                f"riempirsi ne' dove svuotarsi"
            )
        return self

    @model_validator(mode="after")
    def what_is_serviced_is_not_what_never_closes(self) -> "ComponentDefinition":
        """Le due proprieta' si contraddicono, e la contraddizione e' silenziosa.

        `maintainable` significa «per smontarlo va chiuso il fluido attorno»;
        `shutoff_never` significa «non lo si chiude mai». Un componente che
        dichiarasse entrambe chiederebbe alla regola dell'intercettazione una
        valvola che un'altra proprieta' vieta, e la fila uscirebbe sbagliata
        senza che nessuno se ne accorga.
        """
        if self.has_trait(ComponentTrait.MAINTAINABLE) and self.has_trait(
            ComponentTrait.SHUTOFF_NEVER
        ):
            raise ValueError(
                f"{self.id} dichiara insieme {ComponentTrait.MAINTAINABLE} e "
                f"{ComponentTrait.SHUTOFF_NEVER}: la prima chiede le valvole che "
                f"la seconda vieta"
            )
        return self


__all__ = [
    "ATTACHMENT_STYLES",
    "FITTING_FUNCTIONS",
    "SHUTOFF_REGIMES",
    "ComponentDefinition",
    "ComponentTrait",
    "PortDefinition",
]
