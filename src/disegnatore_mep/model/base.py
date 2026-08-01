from pydantic import BaseModel, ConfigDict, Field


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
