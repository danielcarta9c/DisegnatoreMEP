from enum import StrEnum


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


JsonPrimitive = str | int | float | bool | None
