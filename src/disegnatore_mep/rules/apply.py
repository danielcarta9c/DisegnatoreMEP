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

from disegnatore_mep.assembly import assemble
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

from .engine import BRANCH_OFF, evaluate
from .errors import RuleError
from .proposal import RuleGap, RuleProposal
from .registry import RuleRegistry

"""Il mestiere di cio' che apre una derivazione su una tubazione esistente.

E' una **funzione**, non un pezzo: quale voce di catalogo la porti su un dato
fluido lo risolve il catalogo, come per ogni altra cosa che le regole chiedono
(D-069). Serve nominata qui perche' la derivazione non la chiede una regola: la
chiede la forma dell'impianto, quando un accessorio pende da uno stacco e la
macchina non ha l'attacco dedicato.

Da non confondere con la **confluenza**, che e' un pezzo diverso: li' due
tubazioni si uniscono e tutti e tre gli attacchi sono sul percorso, qui il
braccio esce dal percorso.
"""

BRANCH_PORT = "branch"
"""Il braccio del raccordo a cui si appende cio' che pende dallo stacco."""

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


def _instance(
    component_id: str, definition_id: str, proposal: RuleProposal
) -> ComponentInstance:
    """Il pezzo nuovo, con dietro la regola che lo ha voluto e il suo perche'.

    E' la tracciabilita' a valle di D-039: dalla distinta si risale alla regola,
    e la nota e' la **motivazione** — cio' che l'ingegnere legge — non
    l'identificativo della regola, che sta gia' nel riferimento.
    """
    return ComponentInstance(
        id=component_id,
        definition_id=definition_id,
        evidence=[
            EvidenceRef(
                kind="rule",
                reference=f"{proposal.rule_id}@{proposal.rule_version}",
                note=proposal.rationale,
            )
        ],
    )


def _stub(
    proposal: RuleProposal, network_id: str, holder: PortRef
) -> ConnectionModel:
    """La tubazione corta che regge cio' che pende dallo stacco.

    Non spezza niente: collega l'attacco che regge — quello di servizio della
    macchina, o il braccio del raccordo — all'unico attacco dell'accessorio.
    """
    return ConnectionModel(
        id=f"stub-{proposal.component_id}",
        network_id=network_id,
        endpoint_a=holder,
        endpoint_b=PortRef(
            component_id=proposal.component_id, port_id=proposal.inlet_port
        ),
    )


def _derivation(
    connection: ConnectionModel, proposal: RuleProposal, junction_id: str
) -> list[ConnectionModel]:
    """Il raccordo che apre una derivazione dentro una tubazione esistente.

    La tubazione si spezza in due tronconi che entrano e escono dal raccordo, e
    dal braccio del raccordo pende l'accessorio. E' cio' che si fa in cantiere
    quando la macchina non ha il bocchello: si salda un T sul tubo.
    """
    return [
        connection.model_copy(
            update={
                "id": f"{connection.id}-a",
                "endpoint_b": PortRef(component_id=junction_id, port_id="a"),
            }
        ),
        connection.model_copy(
            update={
                "id": f"{connection.id}-b",
                "endpoint_a": PortRef(component_id=junction_id, port_id="b"),
            }
        ),
    ]


def apply_proposals(
    project: ProjectModel, proposals: list[RuleProposal], catalog: ComponentRegistry
) -> ProjectModel:
    """Il modello completato. L'originale resta com'era.

    Tre modi, e li decide **come l'accessorio si attacca**, che e' una proprieta'
    dichiarata dal catalogo:

    - **in linea**: la tubazione si spezza e il pezzo ci finisce in mezzo;
    - **su stacco, e la macchina ha l'attacco dedicato**: il pezzo ci si collega
      e la tubazione principale non si tocca;
    - **su stacco, e la macchina non ce l'ha**: si apre una derivazione sulla
      tubazione con un raccordo, e il pezzo pende da li'.

    Prima erano uno solo — spezzare — e per questo scarico, vaso, riempimento e
    strumenti finivano in fila dentro il tubo, come se l'acqua ci passasse
    dentro.
    """
    current = project
    for proposal in proposals:
        added = [_instance(proposal.component_id, proposal.definition_id, proposal)]
        network_id = proposal.network_id
        # I pezzi nuovi entrano nel sottosistema dell'ancoraggio; le tubazioni
        # nate o spezzate restano fuori di li' e finiscono nella tracciabilita'.
        pipes: list[str] = []

        if proposal.service_port is not None:
            # La macchina l'attacco ce l'ha: nessuna tubazione viene spezzata.
            stub = _stub(
                proposal,
                network_id,
                PortRef(
                    component_id=proposal.anchor.component_id,
                    port_id=proposal.service_port,
                ),
            )
            connections = [*current.connections, stub]
            pipes.append(stub.id)
        else:
            connection = _connection_touching(current, proposal.anchor)
            if catalog.get(proposal.definition_id).attaches_on_a_branch:
                junction_id = f"tee-{proposal.component_id}"
                added.append(
                    _instance(
                        junction_id,
                        catalog.providing(
                            BRANCH_OFF, _medium_of(current, network_id)
                        ).id,
                        proposal,
                    )
                )
                pieces = _derivation(connection, proposal, junction_id)
                extra = [
                    _stub(
                        proposal,
                        network_id,
                        PortRef(component_id=junction_id, port_id=BRANCH_PORT),
                    )
                ]
            else:
                pieces = _split(connection, proposal)
                extra = []
            connections = []
            for item in current.connections:
                if item.id == connection.id:
                    connections.extend(pieces)
                else:
                    connections.append(item)
            connections.extend(extra)
            pipes.extend(item.id for item in (*pieces, *extra))

        subsystems = list(current.subsystems)
        for component in added:
            subsystems = _with_member(
                subsystems, proposal.anchor.component_id, component.id
            )
        current = current.model_copy(
            update={
                "components": [*current.components, *added],
                "connections": connections,
                "subsystems": subsystems,
                "rule_applications": [
                    *current.rule_applications,
                    RuleApplicationModel(
                        id=f"applied-{proposal.component_id}",
                        rule_id=proposal.rule_id,
                        rule_version=proposal.rule_version,
                        category=proposal.category,
                        status=ApprovalStatus.APPROVED,
                        entity_ids=[*(item.id for item in added), *pipes],
                    ),
                ],
            }
        )
    return current


def _medium_of(project: ProjectModel, network_id: str) -> str:
    """Il fluido di una rete. Il raccordo si sceglie su quello, come ogni pezzo."""
    for network in project.networks:
        if network.id == network_id:
            return network.medium
    raise RuleError(f"unknown network {network_id}")


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
    def assembled(model: ProjectModel) -> ProjectModel:
        """La fila ordinata, prima di consegnare il modello a chiunque.

        Completare dice **cosa** manca; assemblare dice **in che ordine** sta
        sul tubo (D-093). Senza questo passo l'ordine e' quello in cui le regole
        sono state valutate, cioe' l'ordine alfabetico dei loro file.
        """
        return assemble(model, catalog, {item.id: item for item in rules.all()})

    current = project
    applied: list[RuleProposal] = []
    gaps: dict[tuple[str, str, str, str], RuleGap] = {}
    found = evaluate(current, catalog, rules)
    for _ in range(ROUNDS):
        for gap in found.gaps:
            gaps.setdefault(gap.key, gap)
        if found.is_empty:
            return assembled(current), applied, list(gaps.values())
        # Si assembla **dentro** il ciclo: rimettere in fila puo' scoprire un
        # attacco che era coperto solo perche' un pezzo stava dove non doveva.
        current = assembled(apply_proposals(current, found.proposals, catalog))
        applied.extend(found.proposals)
        found = evaluate(current, catalog, rules)
    for gap in found.gaps:
        gaps.setdefault(gap.key, gap)
    if found.is_empty:
        return assembled(current), applied, list(gaps.values())
    # `found` e' la valutazione che ha ancora qualcosa da proporre: il messaggio
    # nomina quelle regole, e non puo' uscire vuoto.
    asking = sorted({item.rule_id for item in found.proposals})
    raise RuleError(
        f"the rules were still proposing after {ROUNDS} productive rounds, and "
        f"the next one asked for {', '.join(asking)}. Two rules that undo each "
        f"other would loop here instead of producing a model nobody can explain"
    )


__all__ = ["ROUNDS", "apply_proposals", "saturate"]
