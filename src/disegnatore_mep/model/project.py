from collections.abc import Sequence
from datetime import date
from typing import Any, Literal

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer, model_validator

from .base import ID_PATTERN, IdentifiedModel, StrictModel
from .types import (
    ApprovalStatus,
    BandRole,
    Domain,
    IntegrationCategory,
    JsonPrimitive,
    PlantRegime,
)

SCHEMA_VERSION = "1.1.0"
"""La sola versione che questo eseguibile costruisce in memoria.

I documenti piu' vecchi vengono migrati al confine, in `io/project_json.py`:
il modello non porta rami condizionali sulla versione.
"""


DEL_CARTIGLIO: tuple[str, ...] = (
    "address",
    "sheet_title",
    "sheet_number",
    "drawn_by",
    "checked_by",
    "approved_by",
    "header_note",
)
"""I dati del cartiglio che i metadati possono non avere (REL-002)."""


def _senza_i_vuoti(dati: dict[str, Any], nomi: tuple[str, ...]) -> dict[str, Any]:
    for nome in nomi:
        if dati.get(nome) is None:
            dati.pop(nome, None)
    return dati


class ProjectMetadata(StrictModel):
    """Il documento, non l'impianto: sono i dati che il cartiglio scrive.

    I campi dopo `issue_date` sono **facoltativi e additivi** (REL-002, I-127),
    come `plant_regime`: un documento 1.1.0 senza di loro resta valido, e la
    versione dello schema non cambia. **Assente vuol dire non dato**: il
    cartiglio scrive «DA DEFINIRE» dove il dato serve, e la tavola esce in
    bozza (D-025). Nessuno li inventa (D-087).
    """

    project_id: str = Field(pattern=ID_PATTERN)
    client: str = Field(min_length=1)
    project_name: str = Field(min_length=1)
    commission_code: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    issue_date: date
    address: str | None = Field(default=None, min_length=1)
    """L'indirizzo dell'intervento, come la casella del cartiglio lo chiede:
    via, comune e provincia."""
    sheet_title: str | None = Field(default=None, min_length=1)
    """Il titolo della tavola, per un progetto su una tavola sola. Quando il
    progetto dichiara le proprie tavole vale il titolo di ciascuna
    (`SheetIntentModel.title`)."""
    sheet_number: str | None = Field(default=None, min_length=1)
    """Il numero della tavola nell'elenco degli elaborati della commessa, come
    il cartiglio lo stampa: «T3». Per un progetto su piu' tavole vale quello di
    ciascuna (`SheetIntentModel.number`)."""
    drawn_by: str | None = Field(default=None, min_length=1)
    """Chi ha disegnato. Senza, la riga della firma resta vuota."""
    checked_by: str | None = Field(default=None, min_length=1)
    """Chi ha verificato. Senza, la riga della firma resta vuota."""
    approved_by: str | None = Field(default=None, min_length=1)
    """Chi ha approvato. Senza, la riga della firma resta vuota."""
    header_note: str | None = Field(default=None, min_length=1)
    """La dicitura che il cartiglio Nove C porta in testata, a destra: nel file
    del PO e' «Conto Termico con sconto in fattura». Senza, resta vuota."""

    @model_serializer(mode="wrap")
    def _senza_i_dati_non_dati(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Un dato del cartiglio che manca **non si scrive**, nemmeno come `null`.

        E' cio' che tiene l'aggiunta davvero additiva: un documento scritto prima
        di REL-002 esce da `rules --apply-all` **identico byte per byte**, e la
        sua impronta (`io.canonical`) non cambia. I grafi agli atti restano
        quelli su cui i loro piani sono nati."""
        return _senza_i_vuoti(handler(self), DEL_CARTIGLIO)


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
    number: str | None = Field(default=None, min_length=1)
    """Il numero di questa tavola nel cartiglio, «T3» (REL-002). Facoltativo e
    additivo; senza, il cartiglio scrive «DA DEFINIRE»."""
    subsystem_ids: list[str] = Field(default_factory=list)
    band_assignments: list[BandAssignment] = Field(default_factory=list)

    @model_serializer(mode="wrap")
    def _senza_il_numero_non_dato(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Come per i metadati: un numero che non c'e' non si scrive."""
        return _senza_i_vuoti(handler(self), ("number",))

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
    plant_regime: PlantRegime | None = None
    """Il regime della centrale, se il progettista lo ha dichiarato (D-106).

    Assente vuol dire **non dichiarato**, e le regole applicano il corredo
    minimo. Campo facoltativo e additivo: un documento 1.1.0 senza questo
    campo resta valido cosi' com'e', e la versione dello schema non cambia.
    """
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
