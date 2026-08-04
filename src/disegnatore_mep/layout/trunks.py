"""Le tratte che gli accessori in linea hanno spezzato.

Una valvola in linea non e' un nodo del disegno: sta **sopra** una tubazione e
la interrompe (D-027). Nel modello topologico spezza pero' la connessione in
due, e finora nulla legava i due segmenti alla stessa tratta originaria (W4).

Questo modulo la ricostruisce: da un estremo non in linea si cammina
attraverso gli accessori — entrando da una porta e uscendo dall'altra, che il
manifesto garantisce essere opposta — fino al primo componente non in linea.
Il risultato e' cio' che l'instradamento tratta come un unico percorso.
"""

from dataclasses import dataclass

from disegnatore_mep.model.project import ConnectionModel, PortRef, ProjectModel

from .errors import LayoutError


@dataclass(frozen=True)
class Trunk:
    """Una tratta: i due estremi non in linea, e cio' che sta in mezzo."""

    network_id: str
    start: PortRef
    end: PortRef
    connection_ids: tuple[str, ...]
    inline_component_ids: tuple[str, ...]


def _other_end(connection: ConnectionModel, ref: PortRef) -> PortRef:
    return connection.endpoint_b if connection.endpoint_a == ref else connection.endpoint_a


def _incidence(project: ProjectModel) -> dict[str, list[ConnectionModel]]:
    incidence: dict[str, list[ConnectionModel]] = {}
    for connection in project.connections:
        for ref in (connection.endpoint_a, connection.endpoint_b):
            incidence.setdefault(ref.component_id, []).append(connection)
    return incidence


def build_trunks(
    project: ProjectModel, inline_component_ids: frozenset[str]
) -> list[Trunk]:
    """Ricompone le tratte. L'ordine segue quello delle connessioni nel modello.

    `inline_component_ids` arriva da `ResolvedComponent.is_inline`: e' la
    libreria a dire quali componenti spezzano una linea, non un elenco scritto
    qui dentro.
    """
    incidence = _incidence(project)

    for component_id in sorted(inline_component_ids):
        incident = incidence.get(component_id, [])
        if len(incident) != 2:
            raise LayoutError(
                f"inline component {component_id} has {len(incident)} connections: "
                f"an inline accessory breaks exactly one run and needs two"
            )
        if incident[0].network_id != incident[1].network_id:
            raise LayoutError(
                f"inline component {component_id} joins two networks, "
                f"{incident[0].network_id} and {incident[1].network_id}: "
                f"an accessory sits on one run, not between two"
            )

    trunks: list[Trunk] = []
    consumed: set[str] = set()

    for connection in project.connections:
        if connection.id in consumed:
            continue
        anchors = [
            ref
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if ref.component_id not in inline_component_ids
        ]
        if not anchors:
            # Tratta di soli accessori: la chiude il controllo finale, che sa
            # dirne l'elenco completo invece di segnalarne una alla volta.
            continue

        start = anchors[0]
        chain: list[ConnectionModel] = [connection]
        inline_seen: list[str] = []
        cursor = _other_end(connection, start)
        while cursor.component_id in inline_component_ids:
            inline_seen.append(cursor.component_id)
            incident = incidence[cursor.component_id]
            following = incident[0] if incident[1].id == chain[-1].id else incident[1]
            if following.id in {item.id for item in chain}:
                raise LayoutError(
                    f"inline component {cursor.component_id} closes a loop on itself"
                )
            chain.append(following)
            # Si esce dall'accessorio dall'estremo che non sta su di esso. Non
            # si puo' usare `_other_end`: la porta da cui siamo entrati non
            # appartiene alla connessione successiva, che tocca l'altra porta.
            cursor = (
                following.endpoint_b
                if following.endpoint_a.component_id == cursor.component_id
                else following.endpoint_a
            )

        consumed.update(item.id for item in chain)
        trunks.append(
            Trunk(
                network_id=connection.network_id,
                start=start,
                end=cursor,
                connection_ids=tuple(item.id for item in chain),
                inline_component_ids=tuple(inline_seen),
            )
        )

    orphans = sorted({item.id for item in project.connections} - consumed)
    if orphans:
        raise LayoutError(
            f"connections belong to no run because every component on them is an "
            f"inline accessory: {orphans}"
        )
    return trunks
