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

    I campi dopo `issue_date` sono **facoltativi e additivi** (REL-002, I-130),
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
    esistente: bool = False
    """La rete **c'e' gia'**, e l'intervento non la tocca (REL-007, I-145).

    E' il retrofit che il PO ha descritto: la centrale si progetta, la
    distribuzione dagli accumuli in poi esiste e le sue tubazioni non si
    cambiano. Una rete esistente si disegna come le altre e **non porta il DN**
    (D-193, punto 8). Facoltativo e additivo: assente vuol dire nuova, e un
    documento scritto prima non cambia di un byte."""

    @model_serializer(mode="wrap")
    def _senza_l_esistente_non_detto(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        """Una rete nuova non scrive `esistente`: i grafi agli atti restano
        identici byte per byte, e cosi' la loro impronta (`io.canonical`)."""
        dati: dict[str, Any] = handler(self)
        if not dati.get("esistente"):
            dati.pop("esistente", None)
        return dati


CHIAVI_DEI_DATI_NUMERICI: dict[str, str] = {
    "power_kw": "kW",
    "volume_l": "l",
    "flow_rate_m3h": "m³/h",
    "head_kpa": "kPa",
    "head_m": "m c.a.",
    "delta_t_k": "K",
}
"""I dati tecnici con un nome fisso, e l'unita' in cui si scrivono (REL-006).

Potenza, volume, portata e prevalenza di un pezzo, **come il progettista li ha
dati**: un numero, nell'unita' che il nome dichiara. Le prime quattro sono le
chiavi che la tavola sapeva gia' scrivere accanto a un pezzo
(`layout/labels.py`, D-052); `head_m` e' la prevalenza in metri di colonna
d'acqua, che il progettista da' spesso cosi' e che non si converte in kPa per
non cambiargli il numero. Le legge la tabella delle apparecchiature
(`graphics/tabella.py`).

`delta_t_k` e' il **salto termico di progetto** del circuito di un generatore o
di un'utenza, in kelvin: con `power_kw` da' la portata da cui il calcolatore dei
diametri sceglie il DN (REL-007, D-193). Lo da' il progettista, e se manca
«Capire» lo chiede (I-145): la tavola non lo scrive, perche' il dato che si legge
e' il DN."""

MARCA = "marca"
"""La marca di un pezzo, come il progettista l'ha data (I-144): un testo."""

MODELLO = "modello"
"""Il modello di un pezzo, come il progettista l'ha dato (I-144): un testo. E'
la chiave che «Capire» usava gia' per il nome commerciale."""


class ComponentInstance(IdentifiedModel):
    definition_id: str = Field(pattern=ID_PATTERN)
    tag: str | None = None
    properties: dict[str, JsonPrimitive] = Field(default_factory=dict)
    evidence: list[EvidenceRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def i_dati_con_nome_fisso_hanno_la_loro_forma(self) -> "ComponentInstance":
        """Un dato con un nome fisso ha la forma che il nome promette.

        Un numero positivo per le chiavi con l'unita' — «15 kW» scritto in
        `power_kw` e' un difetto di chi l'ha scritto, e la tabella non deve
        indovinarlo —, un testo non vuoto per marca e modello. Le altre
        proprieta' restano libere, come sono sempre state."""
        for chiave in CHIAVI_DEI_DATI_NUMERICI:
            if chiave not in self.properties:
                continue
            valore = self.properties[chiave]
            if isinstance(valore, bool) or not isinstance(valore, int | float) or valore <= 0:
                raise ValueError(
                    f"component {self.id}: {chiave} must be a positive number in "
                    f"{CHIAVI_DEI_DATI_NUMERICI[chiave]}, not {valore!r}"
                )
        for chiave in (MARCA, MODELLO):
            if chiave not in self.properties:
                continue
            valore = self.properties[chiave]
            if not isinstance(valore, str) or not valore.strip():
                raise ValueError(
                    f"component {self.id}: {chiave} must be a non-empty text, not {valore!r}"
                )
        return self


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


class RichiestaDeiDiametri(StrictModel):
    """Il progettista vuole i diametri, e dice **dove** (REL-007, I-145).

    Il calcolo e' facoltativo: senza questa richiesta nessun tratto porta il DN
    (D-193, punto 8). Con la richiesta, lo portano i tratti delle reti elencate —
    nel retrofit, per esempio, il circuito primario e non la distribuzione
    esistente. Le reti si nominano per identificativo, come le scrive il grafo."""

    reti: list[str] = Field(min_length=1)
    """Le reti su cui calcolare il DN: nessuna e' esistente, nessuna due volte."""

    @model_validator(mode="after")
    def reti_senza_doppioni(self) -> "RichiestaDeiDiametri":
        visti: set[str] = set()
        for rete in self.reti:
            if rete in visti:
                raise ValueError(f"la rete {rete} e' chiesta due volte per i diametri")
            visti.add(rete)
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
    diametri: RichiestaDeiDiametri | None = None
    """La richiesta dei diametri delle tubazioni, se il progettista l'ha fatta
    (REL-007). Facoltativa e additiva come `plant_regime`: assente vuol dire che
    il DN non si calcola, e un documento scritto prima non cambia di un byte."""
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

    @model_validator(mode="after")
    def i_diametri_si_chiedono_su_reti_nuove(self) -> "ProjectModel":
        """La richiesta dei diametri nomina reti che esistono, e nessuna esistente.

        Una rete esistente non si dimensiona (I-145): chiederne il DN e'
        contraddittorio, e va detto a chi ha scritto il grafo invece di
        scegliere per lui una delle due cose."""
        if self.diametri is None:
            return self
        reti = {item.id: item for item in self.networks}
        for rete in self.diametri.reti:
            if rete not in reti:
                raise ValueError(f"i diametri sono chiesti sulla rete {rete}, che il grafo non ha")
            if reti[rete].esistente:
                raise ValueError(
                    f"i diametri sono chiesti sulla rete {rete}, che e' esistente: una rete "
                    f"esistente non si dimensiona"
                )
        return self

    @model_serializer(mode="wrap")
    def _senza_la_richiesta_che_non_c_e(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        """Senza richiesta dei diametri il campo non si scrive, nemmeno come
        `null`: i grafi agli atti restano identici byte per byte."""
        dati: dict[str, Any] = handler(self)
        if dati.get("diametri") is None:
            dati.pop("diametri", None)
        return dati
