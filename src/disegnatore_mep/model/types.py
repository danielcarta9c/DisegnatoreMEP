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


JsonPrimitive = str | int | FiniteFloat | bool | None
