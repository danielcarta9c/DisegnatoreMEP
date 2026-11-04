from collections.abc import Sequence
from datetime import date
from typing import Annotated, Any, Literal

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
    "livello",
)
"""I dati del cartiglio che i metadati possono non avere (REL-002), e il livello del
progetto (REL-011, D-224)."""


MaterialeDelleTubazioni = Literal["multistrato", "acciaio", "rame"]
"""I materiali delle tubazioni che il calcolo dei diametri conosce (I-279,
`diametri.tubi`)."""

SoggettoDellaNota = Literal["isolamento", "antigelo", "sfiati", "vaso", "sonda"]
"""I soggetti delle cinque note di posa che la skill genera (D-232, `graphics.note`): la
parola con cui una nota del progettista ne prende il posto, e il nome con cui la toglie
(REL-017, I-271)."""


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
    livello: Literal["definitivo", "esecutivo"] | None = None
    """Il livello del progetto (REL-011, D-224, I-254): nel **definitivo** la tavola non
    porta tarature, precarica, pressione di caricamento ne' le note di posa; nell'
    **esecutivo** (esecutivo-costruttivo) si'. Lo chiede l'agente al progettista
    all'inizio. Assente vale definitivo: i grafi agli atti non cambiano."""

    note_di_posa: list[str] = Field(default_factory=list)
    """Le note di posa **del progettista** (REL-017, I-271), com'e' le scrive: escono nel
    riquadro «NOTE» **prima** di quelle che la skill genera, nel suo ordine. Una sua nota
    che comincia con la parola del soggetto di una nota generata — «Isolamento»,
    «Antigelo», «Sfiati», «Vaso», «Sonda» — **ne prende il posto** (`graphics.note`). Il
    tetto di cinque resta (D-232), e solo nell'esecutivo. Vuoto non si scrive."""
    note_tolte: list[SoggettoDellaNota] = Field(default_factory=list)
    """Le note generate che il progettista **toglie senza sostituirle**, per soggetto
    (REL-017, I-271). Vuoto non si scrive."""

    @model_validator(mode="after")
    def le_note_si_scrivono_intere(self) -> "ProjectMetadata":
        vuote = [item for item in self.note_di_posa if not item.strip()]
        if vuote:
            raise ValueError(
                f"note_di_posa holds {len(vuote)} empty note(s): a note is a sentence, "
                f"or it is not written"
            )
        doppie = sorted({item for item in self.note_tolte if self.note_tolte.count(item) > 1})
        if doppie:
            raise ValueError(f"note_tolte names {', '.join(doppie)} more than once")
        return self

    @model_serializer(mode="wrap")
    def _senza_i_dati_non_dati(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Un dato del cartiglio che manca **non si scrive**, nemmeno come `null`.

        E' cio' che tiene l'aggiunta davvero additiva: un documento scritto prima
        di REL-002 esce da `rules --apply-all` **identico byte per byte**, e la
        sua impronta (`io.canonical`) non cambia. I grafi agli atti restano
        quelli su cui i loro piani sono nati. Lo stesso per le note del progettista
        (I-271): senza, i due campi non si scrivono."""
        dati = _senza_i_vuoti(handler(self), DEL_CARTIGLIO)
        for nome in ("note_di_posa", "note_tolte"):
            if not dati.get(nome):
                dati.pop(nome, None)
        return dati


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
    materiale_tubazioni: MaterialeDelleTubazioni | None = None
    """Il materiale delle tubazioni di questa rete, se e' diverso da quello del
    progetto (I-279): il calcolo dei diametri sceglie il tubo commerciale di questo
    materiale. Assente vale quello del progetto, e assente non si scrive."""

    @model_serializer(mode="wrap")
    def _senza_l_esistente_non_detto(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        """Una rete nuova non scrive `esistente`: i grafi agli atti restano
        identici byte per byte, e cosi' la loro impronta (`io.canonical`). Lo stesso
        per il materiale, quando non c'e'."""
        dati: dict[str, Any] = handler(self)
        if not dati.get("esistente"):
            dati.pop("esistente", None)
        if dati.get("materiale_tubazioni") is None:
            dati.pop("materiale_tubazioni", None)
        return dati


CHIAVI_DEI_DATI_NUMERICI: dict[str, str] = {
    "power_kw": "kW",
    "volume_l": "l",
    "flow_rate_m3h": "m³/h",
    "head_kpa": "kPa",
    "head_m": "m c.a.",
    "delta_t_k": "K",
    "potenza_elettrica_kw": "kW",
    "corrente_max_a": "A",
    "prevalenza_utile_kpa": "kPa",
    "prevalenza_utile_m": "m c.a.",
}
"""I dati tecnici con un nome fisso, e l'unita' in cui si scrivono (REL-006).

`potenza_elettrica_kw` e `corrente_max_a` sono i dati **elettrici** di una macchina —
la potenza assorbita e la corrente massima —, che la tabella della tavola
dell'elettrico scrive al posto di quelli idronici (I-277); con loro, come testi,
`alimentazione` e `cavo_minimo` (`graphics.tabella.CARATTERISTICHE_ELETTRICHE`).

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
e' il DN.

`prevalenza_utile_kpa` e' la **prevalenza utile della pompa a bordo** di un
generatore, in kPa, alla portata di progetto — `prevalenza_utile_m` la stessa in metri
di colonna d'acqua, come `head_m` —: con le `lunghezza_m` dei tratti, la skill
verifica che il giro primario non costi di piu' (I-270, `diametri.perdite`). Non si
scrive in tavola, e la tabella non la porta."""

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
    a_bordo: list[str] = Field(default_factory=list)
    """Le funzioni che **questa** macchina porta dentro il mantello, dette dal
    progettista (REL-009, I-192): la valvola di sicurezza, il vaso, il ritegno
    integrati in quella pompa di calore. Le regole le leggono come leggono il
    catalogo (`carries_on_board`), che lo dice per il modello e non per la singola
    macchina. Facoltativo e additivo: vuoto non si scrive, e i grafi agli atti
    restano identici byte per byte."""

    non_a_bordo: list[str] = Field(default_factory=list)
    """Le funzioni che **questa** macchina **non** porta dentro il mantello, dette dal
    progettista (REL-017, I-272): la risposta «no» alla domanda che `completa` fa dove il
    catalogo tace — «il bollitore porta il vaso sanitario dentro?» —. Le regole le leggono
    come leggono `lacks_on_board` del catalogo, e il pezzo lo posano loro, nel loro ordine:
    scritto a mano sarebbe un punto fisso, e il corredo della macchina gli finirebbe fra lui
    e lei. Facoltativo e additivo: vuoto non si scrive."""

    @model_validator(mode="after")
    def il_bordo_si_dice_una_volta(self) -> "ComponentInstance":
        for campo, voci in (("a_bordo", self.a_bordo), ("non_a_bordo", self.non_a_bordo)):
            vuote = [item for item in voci if not item.strip()]
            doppie = sorted({item for item in voci if voci.count(item) > 1})
            if vuote or doppie:
                raise ValueError(
                    f"component {self.id}: {campo} lists each function once, by name "
                    f"(empty: {len(vuote)}, repeated: {doppie})"
                )
        tutte_e_due = sorted(set(self.a_bordo) & set(self.non_a_bordo))
        if tutte_e_due:
            raise ValueError(
                f"component {self.id}: {', '.join(tutte_e_due)} is both in a_bordo and in "
                f"non_a_bordo; the machine carries it or not, one of the two"
            )
        return self

    esistente: bool = False
    """Il pezzo **c'era gia'**, e l'intervento non lo tocca (REL-009, I-195): il
    bollitore rimasto nel suo locale, i collettori d'appartamento. Si disegna come il
    nuovo e la tabella non cambia (D-202): e' un dato per le regole — `completa`
    chiede del corredo che vi posano — e per i diametri. Vuoto non si scrive."""

    @model_serializer(mode="wrap")
    def _senza_il_bordo_non_detto(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        """Un pezzo senza bordo dichiarato non scrive `a_bordo` ne' `non_a_bordo`, e un
        pezzo nuovo non scrive `esistente`."""
        dati: dict[str, Any] = handler(self)
        if not dati.get("a_bordo"):
            dati.pop("a_bordo", None)
        if not dati.get("non_a_bordo"):
            dati.pop("non_a_bordo", None)
        if not dati.get("esistente"):
            dati.pop("esistente", None)
        return dati

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
    esistente: bool = False
    """Il tratto **c'era gia'** (REL-009, I-195): il circuito di carico nuovo fino al
    riattacco, e poi le tubazioni esistenti che scendono al serpentino. Come per il
    pezzo, e' un dato per le regole e per i diametri, non per il disegno (D-202). Un
    accessorio posato su un tratto esistente lo spezza, e le due meta' restano
    esistenti. Vuoto non si scrive."""

    # **La scritta del tratto** (REL-012): tre dati del progettista, facoltativi. La
    # skill non dimensiona l'aria, l'elettrico e il bus (I-225): li scrive come le
    # sono dati. Sulla tavola il tratto porta `scritta` se c'e', altrimenti «sezione
    # · L lunghezza m» (`diametri.scritte`); la distinta dei materiali (REL-013)
    # legge gli stessi campi. Vuoti non si scrivono, e i grafi agli atti restano
    # identici byte per byte.
    sezione: Annotated[str, Field(min_length=1)] | None = None
    """Il diametro o la sezione, come il progettista lo scrive: «Ø200», «Ø6,35
    (1/4")», «3G2,5», «1000×250». Un testo, non un numero: la skill non lo calcola e
    non lo converte."""
    lunghezza_m: Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)] | None = None
    """La lunghezza del tratto in metri, dato del progettista (riserva compresa, se
    lui la comprende). Non e' una misura sulla tavola, che e' uno schema. Zero e'
    il raccordo diretto — il plenum sulla bocca dell'unita' —: la distinta lo legge
    cosi', e la tavola non scrive nessuna lunghezza."""
    scritta: Annotated[str, Field(min_length=1)] | None = None
    """Il testo libero del tratto: se c'e', **vince** su sezione e lunghezza — «di
    fabbrica», «bus · L 9 m». Sezione e lunghezza restano dati della distinta."""

    @model_serializer(mode="wrap")
    def _senza_l_esistente_non_detto(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        dati: dict[str, Any] = handler(self)
        if not dati.get("esistente"):
            dati.pop("esistente", None)
        for campo in ("sezione", "lunghezza_m", "scritta"):
            if dati.get(campo) is None:
                dati.pop(campo, None)
        return dati

    @model_validator(mode="after")
    def endpoints_must_differ(self) -> "ConnectionModel":
        if self.endpoint_a == self.endpoint_b:
            raise ValueError("connection endpoints must differ")
        return self

    @model_validator(mode="after")
    def la_scritta_ha_del_testo(self) -> "ConnectionModel":
        """Sezione e scritta sono testi che si leggono: non solo spazi."""
        for campo in ("sezione", "scritta"):
            valore = getattr(self, campo)
            if valore is not None and not valore.strip():
                raise ValueError(
                    f"connection {self.id}: {campo} must be a readable text, not {valore!r}"
                )
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


class AccessorioTolto(StrictModel):
    """Un accessorio che una regola poserebbe e che il progettista toglie
    (REL-009, I-192).

    La tavola di un impianto costruito dice che cosa c'e', e il progettista sa
    che cosa non c'e': la valvola di sicurezza integrata nella macchina, il
    separatore d'aria che non e' stato montato. La scelta resta scritta nel
    grafo con il suo motivo, e `completa` la rispetta a ogni rilancio."""

    pezzo: str = Field(pattern=ID_PATTERN)
    """L'identificativo che l'accessorio ha nel grafo completo: la voce, il pezzo
    e l'attacco su cui si posa (`safety-valve-pdc-1-water-supply`). E' derivato
    dai dati, non da un contatore: lo stesso accessorio sullo stesso attacco ha
    lo stesso nome a ogni rilancio (`rules.proposal.proposed_component_id`)."""
    motivo: str = Field(min_length=1)
    """Perche' il progettista lo toglie, con le sue parole."""
    altrove: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]*\.[a-z][a-z0-9_-]*$")
    """Dove sta invece, se sta altrove: l'attacco `pezzo.attacco` su cui la regola lo
    posa (`tj-mz.b`), con tutto quello che ne pende — la valvola del vaso, il ponte
    del riempimento. Vuoto, l'accessorio e' tolto e basta."""

    @model_serializer(mode="wrap")
    def _senza_altrove_non_detto(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        dati: dict[str, Any] = handler(self)
        if dati.get("altrove") is None:
            dati.pop("altrove", None)
        return dati


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
    accessori_tolti: list[AccessorioTolto] = Field(default_factory=list)
    """Gli accessori delle regole che il progettista toglie (REL-009, I-192).
    Facoltativo e additivo come `diametri`: vuoto non si scrive."""
    antigelo: Literal["glicole", "valvole"] | None = None
    """Come si protegge dal gelo il tratto esterno delle pompe di calore (REL-011,
    D-230): con il **glicole** nell'acqua, o con le **valvole antigelo** che scaricano il
    tratto esterno. Lo dichiara il progettista. Assente: nelle case (fino a 35 kW) le
    regole mettono le valvole, nelle centrali grandi chiedono. Assente non si scrive."""
    materiale_tubazioni: MaterialeDelleTubazioni | None = None
    """Il materiale delle tubazioni (I-279): **multistrato**, **acciaio** o **rame**. Il
    calcolo dei diametri sceglie il tubo commerciale di questo materiale e la tavola lo
    scrive nella sua notazione — «MS 32×3», «DN 25 (1")», «Cu 28×1». Una rete lo puo'
    cambiare (`NetworkModel.materiale_tubazioni`). Assente vale **multistrato**, lo
    standard di Nove C, e non si scrive."""

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

    @model_validator(mode="after")
    def un_accessorio_tolto_non_e_nel_grafo(self) -> "ProjectModel":
        """Si toglie una volta, e si toglie quello che il grafo non ha gia'.

        Un pezzo che il grafo porta e insieme dichiara tolto e' una
        contraddizione: o l'ha scritto il progettista, e allora c'e', o lo
        poserebbe una regola, e allora si toglie dal grafo di prima stesura."""
        visti: set[str] = set()
        presenti = {item.id for item in self.components}
        for voce in self.accessori_tolti:
            if voce.pezzo in visti:
                raise ValueError(f"l'accessorio {voce.pezzo} e' tolto due volte")
            if voce.pezzo in presenti:
                raise ValueError(
                    f"l'accessorio {voce.pezzo} e' nel grafo e fra quelli tolti: si toglie dal "
                    f"grafo di prima stesura, prima di completare"
                )
            visti.add(voce.pezzo)
        return self

    @model_serializer(mode="wrap")
    def _senza_la_richiesta_che_non_c_e(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        """Senza richiesta dei diametri il campo non si scrive, nemmeno come
        `null`: i grafi agli atti restano identici byte per byte. Lo stesso per gli
        accessori tolti, quando non ce ne sono."""
        dati: dict[str, Any] = handler(self)
        if dati.get("diametri") is None:
            dati.pop("diametri", None)
        if not dati.get("accessori_tolti"):
            dati.pop("accessori_tolti", None)
        if dati.get("antigelo") is None:
            dati.pop("antigelo", None)
        if dati.get("materiale_tubazioni") is None:
            dati.pop("materiale_tubazioni", None)
        return dati
