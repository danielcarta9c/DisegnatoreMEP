import math
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _require_finite(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("value must be a finite number")
    return value


FiniteFloat = Annotated[float, AfterValidator(_require_finite)]
"""A float that rejects NaN and +/-Infinity at the model boundary.

Non-finite floats cannot round-trip through JSON: `json.dumps` (with
`allow_nan=False`, as the canonical serializer uses) refuses to emit them,
and no conformant JSON parser accepts the non-standard `NaN`/`Infinity`
literals that a permissive encoder would otherwise produce. A plant
property can never legitimately be non-finite, so it is rejected here
rather than silently reaching the canonical form or the fingerprint.
"""


class StrictModel(BaseModel):
    """Base model rejecting unknown fields and validating on assignment.

    Note: `validate_assignment` applies the new value before model-level
    `mode="after"` validators run. If such a validator rejects the change,
    the instance keeps the rejected value. Treat a model that raised during
    assignment as discarded rather than recovered.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


ID_PATTERN = r"^[a-z][a-z0-9_-]*$"


class IdentifiedModel(StrictModel):
    """Base for entities carrying a stable project-wide identifier."""

    id: str = Field(pattern=ID_PATTERN)
