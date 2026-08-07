from enum import StrEnum

from disegnatore_mep.model.base import FiniteFloat


class Domain(StrEnum):
    HYDRONIC = "hydronic"
    AERAULIC = "aeraulic"
    REFRIGERANT = "refrigerant"
    GAS = "gas"
    CONDENSATE = "condensate"
    CONTROL = "control"


class PortFlow(StrEnum):
    IN = "in"
    OUT = "out"
    BIDIRECTIONAL = "bidirectional"


class BandRole(StrEnum):
    """Le fasce funzionali della tavola, dichiarate da sinistra a destra (D-041).

    L'ordine di dichiarazione **e'** l'ordine di lettura: i generatori a
    sinistra, la distribuzione a destra. Riordinare i membri riordina la tavola.
    """

    GENERATION = "generation"
    PRIMARY = "primary"
    DISTRIBUTION = "distribution"
    TERMINAL = "terminal"

    @property
    def reading_order(self) -> int:
        return list(BandRole).index(self)


class IssueSeverity(StrEnum):
    BLOCKING = "blocking"
    APPROVAL = "approval"
    WARNING = "warning"


class ApprovalStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"


class IntegrationCategory(StrEnum):
    NECESSARY = "necessary"
    RECOMMENDED = "recommended"
    CONDITIONAL = "conditional"


class PlantRegime(StrEnum):
    """Il regime della centrale: sotto o sopra i 35 kW (D-106, D-108).

    E' un **dato del progettista**, non una scelta della skill: la taglia non
    la decide lei (D-104). Chi legge il testo del progettista lo **ricava
    dalle potenze che lui ha dichiarato** e lo scrive qui (D-108): sommare
    potenze gia' scritte e confrontarle con una soglia fissa e' aritmetica,
    non dimensionamento. Le regole, invece, questo campo lo **leggono e
    basta**: nessuna somma, nessuna deduzione dalle proprieta' dei
    componenti.

    La radice e' normativa: la Raccolta R si applica agli impianti con
    potenza dei focolari superiore a 35 kW (cap. R.1.A.1, SRC-012); sotto
    quella soglia vale la buona pratica delle piccole centrali, che e'
    un'altra (riscontro del 7 agosto su SRC-019 e SRC-008).

    Un progetto che non dichiara niente — perche' il testo le potenze non le
    da' — riceve il **corredo minimo**: le regole del regime piccolo si
    applicano, quelle del grande no, e la mancanza si dice. E' la scelta di
    D-106, non un valore inventato.
    """

    UP_TO_35_KW = "up_to_35_kw"
    """Piccola centrale, fino a 35 kW: il corredo minimo delle regole."""

    OVER_35_KW = "over_35_kw"
    """Sopra i 35 kW: il corredo della parte prima (Raccolta R)."""


JsonPrimitive = str | int | FiniteFloat | bool | None
