from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from .base import StrictModel
from .types import (
    ApprovalStatus,
    Domain,
    IntegrationCategory,
    JsonPrimitive,
)

ID_PATTERN = r"^[a-z][a-z0-9_-]*$"


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


class NetworkModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    domain: Domain
    medium: str = Field(pattern=ID_PATTERN)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ComponentInstance(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    definition_id: str = Field(pattern=ID_PATTERN)
    tag: str | None = None
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class PortRef(StrictModel):
    component_id: str = Field(pattern=ID_PATTERN)
    port_id: str = Field(pattern=ID_PATTERN)


class ConnectionModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
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


class AssumptionModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    text: str = Field(min_length=1)
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    source_message_refs: list[str] = Field(default_factory=list)


class RuleApplicationModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    rule_id: str = Field(pattern=ID_PATTERN)
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    category: IntegrationCategory
    status: ApprovalStatus = ApprovalStatus.PROPOSED
    entity_ids: list[str] = Field(default_factory=list)


class SubsystemModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    component_ids: list[str] = Field(default_factory=list)
    network_ids: list[str] = Field(default_factory=list)


class SheetIntentModel(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    title: str = Field(min_length=1)
    subsystem_ids: list[str] = Field(default_factory=list)


class ProjectModel(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    metadata: ProjectMetadata
    subsystems: list[SubsystemModel] = Field(default_factory=list)
    networks: list[NetworkModel] = Field(default_factory=list)
    components: list[ComponentInstance] = Field(default_factory=list)
    connections: list[ConnectionModel] = Field(default_factory=list)
    assumptions: list[AssumptionModel] = Field(default_factory=list)
    rule_applications: list[RuleApplicationModel] = Field(default_factory=list)
    sheets: list[SheetIntentModel] = Field(default_factory=list)

    @model_validator(mode="after")
    def identifiers_must_be_unique(self) -> "ProjectModel":
        collections = {
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
        tags = [item.tag for item in self.components if item.tag is not None]
        if len(tags) != len(set(tags)):
            raise ValueError("duplicate component tag")
        return self
