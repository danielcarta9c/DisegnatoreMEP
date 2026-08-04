"""Applicare le proposte **approvate**, e nient'altro.

Il passo separato che §9.2 impone. Prende un modello e una lista di proposte gia'
approvate e restituisce un modello nuovo: l'originale non viene toccato, cosi'
rifiutare un'integrazione costa quanto non applicarla.

Ogni applicazione lascia dietro un `RuleApplicationModel`, che e' il campo che
D-039 aveva previsto in P0 e che finora nessun codice scriveva: da li' si risale
a quale regola, in quale versione, ha aggiunto quale pezzo.
"""

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

from .errors import RuleError
from .proposal import RuleProposal


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


__all__ = ["apply_proposals"]
