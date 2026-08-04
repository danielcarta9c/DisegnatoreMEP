from collections.abc import Sequence
from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from .base import ID_PATTERN, IdentifiedModel, StrictModel
from .types import (
    ApprovalStatus,
    BandRole,
    Domain,
    IntegrationCategory,
    JsonPrimitive,
)

SCHEMA_VERSION = "1.1.0"
"""La sola versione che questo eseguibile costruisce in memoria.

I documenti piu' vecchi vengono migrati al confine, in `io/project_json.py`:
il modello non porta rami condizionali sulla versione.
"""


class ProjectMetadata(StrictModel):
    project_id: str = Field(pattern=ID_PATTERN)
    client: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    commission_code: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    issue_date: date


class EvidenceRef(StrictModel):
    kind: Literal["conversation", "attachment", "engineer", "rule"]
    reference: str = Field(min_length=1)
    note: str | None = None


class NetworkModel(IdentifiedModel):
    name: str = Field(min_length=1)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ComponentInstance(IdentifiedModel):
    definition_id: str = Field(pattern=ID_PATTERN)
    tag: str | None = None
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class PortRef(StrictModel):
    component_id: str = Field(pattern=ID_PATTERN)
    port_id: str = Field(pattern=ID_PATTERN)


class ConnectionModel(IdentifiedModel):
    network_id: str = Field(pattern=ID_PATTERN)
    endpoint_a: PortRef
    endpoint_b: PortRef
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def endpoints_must_differ(self) -> "ConnectionModel":
        if self.endpoint_a == self.endpoint_b:
            raise ValueError("connection endpoints must differ")
        return self


class AssumptionModel(IdentifiedModel):
    text: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    source_message_refs: list[str] = Field(default_factory=list)


class RuleApplicationModel(IdentifiedModel):
    rule_id: str = Field(pattern=ID_PATTERN)
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    category: IntegrationCategory
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    entity_ids: list[str] = Field(default_factory=list)


class SubsystemModel(IdentifiedModel):
    name: str = Field(min_length=1)
    component_ids: list[str] = Field(default_factory=list)
    network_ids: list[str] = Field(default_factory=list)


class BandAssignment(StrictModel):
    """Un sottosistema su una fascia della tavola, con la propria posizione.

    E' il piano di impaginazione che l'AI puo' scegliere (D-042): non coordinate,
    ma un insieme ristretto di scelte discrete che il motore esegue e verifica.
    """

    subsystem_id: str = Field(pattern=ID_PATTERN)
    band: BandRole
    order: int = Field(default=0, ge=0)


class SheetIntentModel(IdentifiedModel):
    title: str = Field(min_length=1)
    subsystem_ids: list[str] = Field(default_factory=list)
    band_assignments: list[BandAssignment] = Field(default_factory=list)

    @model_validator(mode="after")
    def band_assignments_are_coherent(self) -> "SheetIntentModel":
        seen: set[str] = set()
        for assignment in self.band_assignments:
            if assignment.subsystem_id in seen:
                raise ValueError(
                    f"subsystem {assignment.subsystem_id} is assigned to more than "
                    f"one band on sheet {self.id}"
                )
            seen.add(assignment.subsystem_id)
            if assignment.subsystem_id not in self.subsystem_ids:
                raise ValueError(
                    f"band assignment names {assignment.subsystem_id}, which is "
                    f"not listed on sheet {self.id}"
                )
        return self


class ProjectModel(StrictModel):
    schema_version: str = Field(pattern=r"^\d+\.\d+\.\d+$", default=SCHEMA_VERSION)
    metadata: ProjectMetadata
    subsystems: list[SubsystemModel] = Field(default_factory=list)
    networks: list[NetworkModel] = Field(default_factory=list)
    components: list[ComponentInstance] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)
    assumptions: list[AssumptionModel] = Field(default_factory=list)
    rule_applications: list[RuleApplicationModel] = Field(default_factory=list)
    sheets: list[SheetIntentModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def schema_version_is_the_current_one(self) -> "ProjectModel":
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"schema version {self.schema_version} cannot be built directly: "
                f"this build works on {SCHEMA_VERSION}; load the document through "
                f"io.project_json.load_project, which migrates it"
            )
        return self

    @model_validator(mode="after")
    def identifiers_must_be_unique(self) -> "ProjectModel":
        collections: dict[str, Sequence[IdentifiedModel]] = {
            "subsystem": self.subsystems,
            "network": self.networks,
            "component": self.components,
            "connection": self.connections,
            "assumption": self.assumptions,
            "rule application": self.rule_applications,
            "sheet": self.sheets,
        }
        for label, items in collections.items():
            seen: set[str] = set()
            for item in items:
                if item.id in seen:
                    raise ValueError(f"duplicate {label} id: {item.id}")
                seen.add(item.id)
        seen_tags: set[str] = set()
        for component in self.components:
            if component.tag is None:
                continue
            if component.tag in seen_tags:
                raise ValueError(f"duplicate component tag: {component.tag}")
            seen_tags.add(component.tag)
        return self
