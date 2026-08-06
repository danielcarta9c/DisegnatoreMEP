"""Applicare le proposte **approvate**, e nient'altro.

Il passo separato che §9.2 impone. Prende un modello e una lista di proposte gia'
approvate e restituisce un modello nuovo: l'originale non viene toccato, cosi'
rifiutare un'integrazione costa quanto non applicarla.

Ogni applicazione lascia dietro un `RuleApplicationModel`, che e' il campo che
D-039 aveva previsto in P0 e che finora nessun codice scriveva: da li' si risale
a quale regola, in quale versione, ha aggiunto quale pezzo.

**Le regole valgono anche su cio' che le regole aggiungono** (D-090). Un filtro
proposto dalle regole e' a sua volta un pezzo che si smonta in esercizio, e vuole
le proprie valvole come il pezzo che protegge: `saturate` ripete valutazione e
applicazione finche' non resta niente da proporre. Una passata sola non e' un
modello completo, ed e' anche il motivo per cui rieseguire le regole su di essa
non proponeva zero.
"""

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    EvidenceRef,
    PortRef,
    ProjectModel,
    RuleApplicationModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import ApprovalStatus

from .engine import evaluate
from .errors import RuleError
from .proposal import RuleGap, RuleProposal
from .registry import RuleRegistry

ROUNDS = 8
"""Quante passate **produttive** si ammettono al massimo.

Le passate vere sono due — gli accessori, poi i loro organi di chiusura — e un
organo di chiusura non si smonta in esercizio, quindi la catena si spegne da
sola. Il limite esiste per trasformare un ciclo infinito, se un giorno due
regole si rincorressero, in un errore che le nomina.

E' il numero di passate che **aggiungono** qualcosa, non il numero di
valutazioni: dopo l'ultima ce ne vuole una in piu' per accorgersi che non c'e'
altro da fare, e contarla nel limite faceva fallire un modello gia' arrivato."""


def _connection_touching(project: ProjectModel, anchor: PortRef) -> ConnectionModel:
    for connection in project.connections:
        if anchor in (connection.endpoint_a, connection.endpoint_b):
            return connection
    raise RuleError(
        f"no connection touches {anchor.component_id}.{anchor.port_id}: an inline "
        f"accessory needs a pipe to sit on"
    )


def _split(connection: ConnectionModel, proposal: RuleProposal) -> list[ConnectionModel]:
    """Spezza la connessione e mette l'accessorio in mezzo.

    Il verso non si sceglie: una connessione va sempre da una porta che **esce** a
    una che **entra**, quindi il primo pezzo finisce nell'ingresso
    dell'accessorio e il secondo riparte dalla sua uscita. Provare a orientarlo
    rispetto all'ancoraggio produceva connessioni fra due uscite, e il
    validatore topologico le respingeva — correttamente.
    """
    return [
        connection.model_copy(
            update={
                "id": f"{connection.id}-a",
                "endpoint_b": PortRef(
                    component_id=proposal.component_id, port_id=proposal.inlet_port
                ),
            }
        ),
        connection.model_copy(
            update={
                "id": f"{connection.id}-b",
                "endpoint_a": PortRef(
                    component_id=proposal.component_id, port_id=proposal.outlet_port
                ),
            }
        ),
    ]


def _with_member(
    subsystems: list[SubsystemModel], anchor_id: str, component_id: str
) -> list[SubsystemModel]:
    """Il nuovo pezzo entra nel sottosistema del componente a cui si ancora.

    Non e' un dettaglio: un componente senza sottosistema non sta su nessuna
    tavola, e il layout lo rifiuta invece di farlo sparire in silenzio. Un
    accessorio appartiene al gruppo funzionale di cio' che serve — il vaso del
    primario sta col generatore, non in un gruppo suo.
    """
    return [
        item.model_copy(update={"component_ids": [*item.component_ids, component_id]})
        if anchor_id in item.component_ids
        else item
        for item in subsystems
    ]


def apply_proposals(
    project: ProjectModel, proposals: list[RuleProposal]
) -> ProjectModel:
    """Il modello completato. L'originale resta com'era."""
    current = project
    for proposal in proposals:
        connection = _connection_touching(current, proposal.anchor)
        pieces = _split(connection, proposal)
        connections: list[ConnectionModel] = []
        for item in current.connections:
            if item.id == connection.id:
                connections.extend(pieces)
            else:
                connections.append(item)
        current = current.model_copy(
            update={
                "components": [
                    *current.components,
                    ComponentInstance(
                        id=proposal.component_id,
                        definition_id=proposal.definition_id,
                        evidence=[
                            EvidenceRef(
                                kind="rule",
                                reference=f"{proposal.rule_id}@{proposal.rule_version}",
                                note=proposal.rationale,
                            )
                        ],
                    ),
                ],
                "connections": connections,
                "subsystems": _with_member(
                    list(current.subsystems),
                    proposal.anchor.component_id,
                    proposal.component_id,
                ),
                "rule_applications": [
                    *current.rule_applications,
                    RuleApplicationModel(
                        id=f"applied-{proposal.component_id}",
                        rule_id=proposal.rule_id,
                        rule_version=proposal.rule_version,
                        category=proposal.category,
                        status=ApprovalStatus.APPROVED,
                        entity_ids=[proposal.component_id, *[item.id for item in pieces]],
                    ),
                ],
            }
        )
    return current


def saturate(
    project: ProjectModel, catalog: ComponentRegistry, rules: RuleRegistry
) -> tuple[ProjectModel, list[RuleProposal], list[RuleGap]]:
    """Il modello completo, le integrazioni che ci sono volute, i punti aperti.

    «Completo» ha un significato preciso: **rieseguire le regole non propone
    piu' niente**. Ci vuole piu' di una passata perche' un accessorio proposto
    e' a sua volta un pezzo dell'impianto, con le proprie esigenze — e' la forma
    generale di D-090, ed e' cio' che permette alla regola dell'intercettazione
    di valere anche sugli accessori invece che sulle sole macchine.

    I punti aperti si accumulano lungo le passate e si contano una volta sola:
    non si risolvono applicando niente, e un accessorio che il catalogo non ha
    resta mancante anche alla passata dopo.
    """
    current = project
    applied: list[RuleProposal] = []
    gaps: dict[tuple[str, str, str, str], RuleGap] = {}
    found = evaluate(current, catalog, rules)
    for _ in range(ROUNDS):
        for gap in found.gaps:
            gaps.setdefault(gap.key, gap)
        if found.is_empty:
            return current, applied, list(gaps.values())
        current = apply_proposals(current, found.proposals)
        applied.extend(found.proposals)
        found = evaluate(current, catalog, rules)
    for gap in found.gaps:
        gaps.setdefault(gap.key, gap)
    if found.is_empty:
        return current, applied, list(gaps.values())
    # `found` e' la valutazione che ha ancora qualcosa da proporre: il messaggio
    # nomina quelle regole, e non puo' uscire vuoto.
    asking = sorted({item.rule_id for item in found.proposals})
    raise RuleError(
        f"the rules were still proposing after {ROUNDS} productive rounds, and "
        f"the next one asked for {', '.join(asking)}. Two rules that undo each "
        f"other would loop here instead of producing a model nobody can explain"
    )


__all__ = ["ROUNDS", "apply_proposals", "saturate"]
