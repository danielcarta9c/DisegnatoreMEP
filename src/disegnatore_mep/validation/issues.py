from pydantic import Field

from disegnatore_mep.model.base import StrictModel
from disegnatore_mep.model.types import IssueSeverity


class ValidationIssue(StrictModel):
    code: str = Field(pattern=r"^[A-Z][A-Z0-9_]*$")
    severity: IssueSeverity
    message: str = Field(min_length=1)
    entity_ids: list[str] = Field(default_factory=list)
