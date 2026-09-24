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

import re

from disegnatore_mep.assembly import assemble
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    EvidenceRef,
    NetworkModel,
    PortRef,
    ProjectModel,
    RuleApplicationModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import ApprovalStatus

from .engine import BRANCH_OFF, Evaluation, evaluate
from .errors import RuleError
from .proposal import RuleGap, RuleProposal
from .registry import RuleRegistry
from .schema import RuleDefinition, SatisfactionScope

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
sola. Da DRAW-005 le due passate sono anche **due fasi** (I-034): le regole
che chiudono un gruppo parlano solo quando le altre non hanno piu' niente da
mettere nel gruppo. Il limite esiste per trasformare un ciclo infinito, se un
giorno due regole si rincorressero, in un errore che le nomina.

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
        # I pezzi nuovi, ciascuno con il componente nel cui sottosistema entra:
        # un accessorio appartiene al gruppo funzionale di cio' che serve, e il
        # ponte fra due reti ha un capo per parte — la sua derivazione fredda
        # sta con l'acqua fredda, non con la macchina all'altro capo.
        added: list[tuple[ComponentInstance, str]] = [
            (
                _instance(proposal.component_id, proposal.definition_id, proposal),
                proposal.anchor.component_id,
            )
        ]
        network_id = proposal.network_id
        # I pezzi nuovi entrano nel sottosistema dell'ancoraggio; le tubazioni
        # nate o spezzate restano fuori di li' e finiscono nella tracciabilita'.
        pipes: list[str] = []
        # Le reti restano quelle, tranne quando un ponte porta il proprio
        # confine: allora ne nasce una, sua e di nessun altro (§A.1).
        networks = list(current.networks)

        if proposal.source_anchor is not None:
            # Un **ponte** fra due reti (DRAW-006-R1, blocco D): il gruppo in
            # mezzo, un capo per parte. La rete della regola riceve l'uscita,
            # quella della sorgente alimenta l'ingresso: il verso non si sceglie
            # qui, lo dichiara il catalogo con il fluido di ciascuna porta.
            #
            # **Il capo di monte porta il proprio confine di rete** (I-061,
            # DRAW-009 §A.1). Il PO, l'11 settembre 2026: «non si deve fare una
            # rete unica di af, non si fa cosi'; si fanno piu' ingressi». Prima
            # questo capo apriva una derivazione sulla linea di un altro utente,
            # e ne usciva una linea sola che attraversava il foglio per servirne
            # due: una linea cosi' **inchioda i pezzi che tocca** — l'utente in
            # fondo non si sposta piu' di un passo di griglia senza che
            # l'instradamento della fredda fallisca. Dove due utenti prendono
            # acqua fredda ci sono due ingressi, ciascuno con la propria rete e
            # ciascuno vicino al proprio utente.
            #
            # L'unione a T con un ingresso solo esiste, per risparmiare sui
            # piccoli componenti a servizio dell'ingresso, ma e' **un'opzione
            # che chiede il progettista** (§A.1.4): non si deduce dal grafo e
            # non la sceglie il codice.
            source_network = _network(
                current, _network_of_port(current, proposal.source_anchor)
            )
            declared = _component(current, proposal.source_anchor.component_id)
            boundary_id = f"inlet-{proposal.component_id}"
            # L'attacco che il confine alimenta: l'ingresso del ponte ordinario,
            # o il terzo attacco di quello in linea (D-175).
            fed_port = proposal.bridge_port or proposal.inlet_port
            own_network = NetworkModel(
                id=f"{source_network.id}-{proposal.component_id}",
                name=source_network.name,
                domain=source_network.domain,
                medium=source_network.medium,
            )
            networks = [*networks, own_network]
            added.append(
                (
                    _instance(boundary_id, declared.definition_id, proposal).model_copy(
                        update={"tag": _next_in_the_series(current, declared)}
                    ),
                    # Il confine entra nel sottosistema dell'**utente**, non in
                    # quello dell'ingresso gia' dichiarato: un confine di rete
                    # non ha una posizione propria, esiste per immettere, e va
                    # posato nelle immediate vicinanze di chi serve (§A.2).
                    proposal.anchor.component_id,
                )
            )
            feed = ConnectionModel(
                id=f"inlet-{proposal.component_id}-{fed_port}",
                network_id=own_network.id,
                endpoint_a=PortRef(
                    component_id=boundary_id, port_id=proposal.source_anchor.port_id
                ),
                endpoint_b=PortRef(
                    component_id=proposal.component_id, port_id=fed_port
                ),
            )
            connections = [*current.connections, feed]
            pipes = [feed.id, own_network.id]
            connection = _connection_touching(
                current.model_copy(update={"connections": connections}), proposal.anchor
            )
            if proposal.bridge_port is not None:
                # Il ponte **in linea** (D-175): la miscelatrice termostatica sta
                # dentro la tubazione dell'acqua calda come ogni organo in linea,
                # e l'acqua fredda le arriva dal proprio confine. Nessuna
                # derivazione: la tubazione della regola si spezza, e basta.
                pieces = _split(connection, proposal)
                extra: list[ConnectionModel] = []
            else:
                # Il capo di valle resta una derivazione sulla tubazione che la
                # regola nomina: li' il ponte si innesta su una rete che c'e'
                # gia' e che non e' sua.
                junction_id = f"tee-{proposal.component_id}-{proposal.outlet_port}"
                added.append(
                    (
                        _instance(
                            junction_id,
                            catalog.providing(BRANCH_OFF, _medium_of(current, network_id)).id,
                            proposal,
                        ),
                        proposal.anchor.component_id,
                    )
                )
                pieces = _derivation(connection, proposal, junction_id)
                # Il verso di una tubazione va da chi esce a chi entra: qui il
                # ponte **esce**, quindi parte dal gruppo e arriva al braccio del
                # raccordo.
                extra = [
                    ConnectionModel(
                        id=f"stub-{proposal.component_id}-{proposal.outlet_port}",
                        network_id=network_id,
                        endpoint_a=PortRef(
                            component_id=proposal.component_id, port_id=proposal.outlet_port
                        ),
                        endpoint_b=PortRef(component_id=junction_id, port_id=BRANCH_PORT),
                    )
                ]
            connections = [
                *(
                    item
                    for existing in connections
                    for item in (pieces if existing.id == connection.id else [existing])
                ),
                *extra,
            ]
            pipes.extend(item.id for item in (*pieces, *extra))
        elif proposal.service_port is not None:
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
                    (
                        _instance(
                            junction_id,
                            catalog.providing(
                                BRANCH_OFF, _medium_of(current, network_id)
                            ).id,
                            proposal,
                        ),
                        proposal.anchor.component_id,
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
        for component, host_id in added:
            subsystems = _with_member(subsystems, host_id, component.id)
        current = current.model_copy(
            update={
                "components": [*current.components, *(item for item, _ in added)],
                "connections": connections,
                "networks": networks,
                "subsystems": subsystems,
                "rule_applications": [
                    *current.rule_applications,
                    RuleApplicationModel(
                        id=f"applied-{proposal.component_id}",
                        rule_id=proposal.rule_id,
                        rule_version=proposal.rule_version,
                        category=proposal.category,
                        status=ApprovalStatus.APPROVED,
                        entity_ids=[*(item.id for item, _ in added), *pipes],
                    ),
                ],
            }
        )
    # Le sigle dei confini si danno qui, dove nascono, e non nella catena: chi
    # applica le proposte a mano — le prove della catena lo fanno — deve
    # ottenere le stesse sigle di `saturate`.
    return _series_in_identifier_order(current)


def _network_of_port(project: ProjectModel, anchor: PortRef) -> str:
    """La rete della tubazione che tocca quell'attacco."""
    return _connection_touching(project, anchor).network_id


def _network(project: ProjectModel, network_id: str) -> NetworkModel:
    for network in project.networks:
        if network.id == network_id:
            return network
    raise RuleError(f"unknown network {network_id}")


def _component(project: ProjectModel, component_id: str) -> ComponentInstance:
    for item in project.components:
        if item.id == component_id:
            return item
    raise RuleError(f"unknown component {component_id}")


def _next_in_the_series(project: ProjectModel, like: ComponentInstance) -> str | None:
    """La sigla successiva della serie di quel pezzo: `AF-01` -> `AF-02`.

    Il PO, sui due ingressi dell'acqua fredda (I-061, DRAW-009 §A.1.2): «sono
    pezzi diversi, con sigle diverse nella serie AF.01, AF.02, ...». Due
    confini che portano la stessa sigla sarebbero lo stesso confine disegnato
    due volte, ed e' esattamente cio' che la regola vieta.

    La serie si legge dalle sigle **gia' nel modello** per quella voce di
    catalogo, mai da un contatore del programma: se il progettista non ne ha
    data nessuna, non se ne inventa una.
    """
    if like.tag is None:
        return None
    shape = re.fullmatch(r"([A-Za-z]+)[-.](\d+)", like.tag)
    if shape is None:
        return None
    prefix, digits = shape.group(1), shape.group(2)
    highest = 0
    for item in project.components:
        if item.definition_id != like.definition_id or item.tag is None:
            continue
        other = re.fullmatch(rf"{re.escape(prefix)}[-.](\d+)", item.tag)
        if other is not None:
            highest = max(highest, int(other.group(1)))
    separator = like.tag[len(prefix)]
    return f"{prefix}{separator}{highest + 1:0{len(digits)}d}"


def _series_in_identifier_order(project: ProjectModel) -> ProjectModel:
    """Le sigle dei confini che i ponti portano con se', date **in ordine di
    identificativo** e non nell'ordine in cui le regole hanno parlato.

    Finche' un solo ponte pescava dall'acqua fredda — il gruppo di riempimento
    — la serie aveva un numero solo da dare. Da **D-175** ce ne sono due, la
    miscelatrice e il riempimento, e `_next_in_the_series` dava il numero a chi
    veniva applicato prima: cioe' all'ordine alfabetico dei **file** delle
    regole. Rinominare un file cambiava le sigle, ed e' esattamente cio' che
    l'assemblatore vieta alla fila (D-093). L'identificativo viene dai dati —
    il pezzo e l'attacco su cui il ponte si ancora — e l'ordine che ne esce e'
    lo stesso comunque le regole si chiamino.

    Tocca soltanto i confini nati da una regola: le sigle del progettista non
    si rinumerano mai.
    """
    added = [
        item
        for item in project.components
        if item.id.startswith("inlet-")
        and item.tag is not None
        and any(evidence.kind == "rule" for evidence in item.evidence)
    ]
    if len(added) < 2:
        return project
    cleared = {item.id for item in added}
    current = project.model_copy(
        update={
            "components": [
                item.model_copy(update={"tag": None}) if item.id in cleared else item
                for item in project.components
            ]
        }
    )
    for item in sorted(added, key=lambda entry: entry.id):
        like = next(
            (
                other
                for other in current.components
                if other.definition_id == item.definition_id
                and other.tag is not None
                and other.id not in cleared
            ),
            item,
        )
        tag = _next_in_the_series(current, like) or item.tag
        current = current.model_copy(
            update={
                "components": [
                    other.model_copy(update={"tag": tag}) if other.id == item.id else other
                    for other in current.components
                ]
            }
        )
        cleared.discard(item.id)
    return current


def _medium_of(project: ProjectModel, network_id: str) -> str:
    """Il fluido di una rete. Il raccordo si sceglie su quello, come ogni pezzo."""
    for network in project.networks:
        if network.id == network_id:
            return network.medium
    raise RuleError(f"unknown network {network_id}")


def evaluate_in_phases(
    project: ProjectModel, catalog: ComponentRegistry, rules: RuleRegistry
) -> Evaluation:
    """Una passata **come la fa la catena**: prima cio' che entra nel gruppo,
    poi cio' che lo chiude (DRAW-005, I-034).

    Un organo di chiusura isola un volume: se parlasse insieme alle regole che
    quel volume lo riempiono — il filtro sul ritorno della macchina — si
    poserebbe fra la macchina e il suo filtro, dove poi non deve stare. Le
    regole che si dichiarano soddisfatte «sul gruppo» aspettano percio' che
    tutte le altre tacciano, e solo allora vedono il gruppo intero. I punti
    aperti della prima fase si riportano anche quando parla la seconda: non si
    risolvono chiudendo niente.

    E' la passata di `saturate`, esposta perche' chi rifa' il ciclo a mano — le
    prove del motore — lo rifaccia con le stesse fasi.
    """
    # Parlano dopo anche le regole che leggono il **dominio di protezione**
    # (I-046): «tagliato fuori da ogni sicurezza» e' vero di ogni generatore
    # finche' la sicurezza di circuito non e' stata posata, e una domanda
    # aperta fatta in quel momento sarebbe una domanda sbagliata.
    closers = RuleRegistry(
        rules=tuple(
            item
            for item in rules.all()
            if item.satisfied_by.scope is SatisfactionScope.ON_THE_GROUP
            or item.when.anchor_cut_off_from is not None
            or _a_group_may_satisfy(item, rules, catalog)
        )
    )
    others = RuleRegistry(
        rules=tuple(item for item in rules.all() if item not in closers.rules)
    )
    first = evaluate(project, catalog, others)
    if not first.is_empty or not closers.rules:
        return first
    second = evaluate(project, catalog, rules)
    return Evaluation(proposals=second.proposals, gaps=[*first.gaps, *second.gaps])


def _a_group_may_satisfy(
    rule: RuleDefinition, rules: RuleRegistry, catalog: ComponentRegistry
) -> bool:
    """Un'altra regola, sullo stesso ancoraggio, puo' posare un **gruppo in
    linea** che si porta dentro cio' che questa chiede.

    Allora questa parla dopo. Un gruppo che sta sulla tubazione porta i propri
    organi su quella tubazione: chiederne uno nella stessa passata in cui il
    gruppo viene proposto produce il doppione che il PM ha tolto — il ritegno
    sanitario accanto al gruppo EN 1487 che lo contiene (DRAW-006-R1, blocco
    C.1).

    «Sullo stesso ancoraggio» e' la meta' che tiene la fase stretta: due regole
    che parlano di pezzi diversi non si soddisfano a vicenda, e mandarle
    entrambe in fase due lascerebbe decidere all'ordine alfabetico dei file
    quale delle due si posa. Chi pende da uno stacco non conta: il filtro dentro
    un gruppo di riempimento appeso a un T non e' il filtro del ritorno della
    macchina. Chi decide non e' un elenco di nomi: e' il catalogo.
    """
    wanted = set(rule.then.functions())
    for other in rules.all():
        if other.id == rule.id:
            continue
        if (other.when.anchor_has_trait, other.when.anchor_has_function) != (
            rule.when.anchor_has_trait,
            rule.when.anchor_has_function,
        ):
            continue
        if other.when.network_medium != rule.when.network_medium:
            continue
        for function in other.then.functions():
            for definition in catalog.all():
                if (
                    function in definition.functions
                    and definition.composite
                    and not definition.attaches_on_a_branch
                    and wanted & set(definition.carries_on_board)
                ):
                    return True
    return False


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
    found = evaluate_in_phases(current, catalog, rules)
    for _ in range(ROUNDS):
        for gap in found.gaps:
            gaps.setdefault(gap.key, gap)
        if found.is_empty:
            return assembled(current), applied, list(gaps.values())
        # Si assembla **dentro** il ciclo: rimettere in fila puo' scoprire un
        # attacco che era coperto solo perche' un pezzo stava dove non doveva.
        current = assembled(apply_proposals(current, found.proposals, catalog))
        applied.extend(found.proposals)
        found = evaluate_in_phases(current, catalog, rules)
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


__all__ = ["ROUNDS", "apply_proposals", "evaluate_in_phases", "saturate"]
