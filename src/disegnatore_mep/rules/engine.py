"""Il motore: modello piu' regole, e ne escono proposte.

Funzione pura. Non tocca il modello, non scrive niente, non decide niente: §9.2
dice che il motore non trasforma una proposta in progetto approvato, e il modo
piu' semplice di rispettarlo e' non dargli la possibilita' di farlo.

L'ordine e' quello delle regole nel registro, poi delle reti e dei componenti
nell'ordine del modello. Deterministico e ispezionabile: due esecuzioni danno la
stessa lista, e la lista si legge dall'alto come la si e' scritta.

**Cosa il motore non decide.** Una regola dichiara la funzione che deve
comparire; quale voce di catalogo la porti su quel fluido lo risolve il
catalogo, e se le voci sono due si ferma invece di sceglierne una. Il motore non
conosce nessun nome di componente, e non ne conosce nemmeno uno scritto in una
regola: da P2 non ce ne sono piu' (D-069).

**E se le voci sono zero, lo dice.** Una regola le cui condizioni sono vere ma
per cui il catalogo non ha nessun pezzo su quel fluido non «non si applica»: si
applica e non ha niente da offrire. La differenza e' tutta, perche' il primo
caso e' silenzio legittimo e il secondo e' un accessorio che sparisce senza che
nessuno lo sappia — un bollitore a se' stante che resta senza scarico. Esce
percio' un **punto aperto** accanto alle proposte, con la categoria della regola
che lo ha generato.
"""

from dataclasses import dataclass, field

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import NetworkModel, PortRef, ProjectModel
from disegnatore_mep.model.types import PlantRegime

from .context import RuleContext
from .proposal import GapReason, RuleGap, RuleProposal, proposed_component_id
from .registry import RuleRegistry
from .schema import Placement, RuleCardinality, RuleDefinition, SatisfactionScope

BRANCH_OFF = "branch_off"
"""Il mestiere del raccordo che apre una derivazione sulla tubazione."""


@dataclass(frozen=True)
class Evaluation:
    """Cosa il motore ha trovato: cio' che propone e cio' che gli manca."""

    proposals: list[RuleProposal] = field(default_factory=list)
    gaps: list[RuleGap] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Nessuna proposta. I punti aperti non contano: non si risolvono
        applicando qualcosa, e aspettarli farebbe girare a vuoto la
        saturazione."""
        return not self.proposals


def _anchors(context: RuleContext, rule: RuleDefinition, network: NetworkModel) -> list[PortRef]:
    """Gli attacchi su cui questa regola potrebbe posare qualcosa, in ordine."""
    network_id = network.id
    found: list[PortRef] = []
    for component_id in context.anchors_of(
        network_id, rule.when.anchor_has_function, rule.when.anchor_has_trait
    ):
        # Una regola che si occupa della riserva non guarda i circuiti che la
        # attraversano: il serpentino di un bollitore porta acqua di
        # riscaldamento, e uno scarico li' svuota il primario lasciando pieno
        # il serbatoio. La rete che serve la riserva e' quella che porta il
        # fluido tenuto in serbo, oppure quella da cui la riserva dichiara di
        # riempirsi (C2).
        if rule.when.network_carries_what_the_anchor_stores and not (
            context.stores(component_id, network.medium)
            or context.fills_on(component_id, network_id)
        ):
            continue
        if rule.when.network_fills_the_anchor and not context.fills_on(
            component_id, network_id
        ):
            continue
        for port in context.connected_ports(component_id):
            if port.flow not in rule.then.placement.flows:
                continue
            if context.network_of_connection.get(
                context.connection_of_port[(component_id, port.id)]
            ) != network_id:
                continue
            found.append(PortRef(component_id=component_id, port_id=port.id))
    return found


def _regime_allows(rule: RuleDefinition, declared: PlantRegime | None) -> bool:
    """La regola vale nel regime che il progetto dichiara (D-106).

    Il regime non si calcola mai: lo dichiara il progettista, e un progetto
    che non dichiara niente riceve il **corredo minimo** — le regole del
    regime piccolo si applicano, quelle del grande no.
    """
    if rule.when.plant_regime is None:
        return True
    if rule.when.plant_regime is PlantRegime.OVER_35_KW:
        return declared is PlantRegime.OVER_35_KW
    return declared is not PlantRegime.OVER_35_KW


def _common_run_anchor(
    context: RuleContext, rule: RuleDefinition, network: NetworkModel
) -> tuple[PortRef | None, PortRef | None]:
    """La testa del tratto comune della rete, per gli ancoraggi della regola.

    Dal ritorno (o dalla mandata) di ciascun ancoraggio si cammina lungo il
    percorso — contro il fluido per il ritorno, seguendolo per la mandata —
    finche' la strada resta una sola. Le tubazioni che **tutte** le camminate
    condividono sono il tratto comune; il pezzo si posa sulla prima di esse,
    cioe' la piu' vicina agli ancoraggi: a monte della prima ripartizione sul
    ritorno, a valle dell'ultima confluenza sulla mandata. Con un ancoraggio
    solo il tratto comune comincia sul suo stesso attacco, e la posa coincide
    con quella di sempre.

    Restituisce `(ancoraggio, ripiego)`: il primo e' la testa del tratto
    comune, o niente se non esiste; il secondo e' l'attacco del primo
    ancoraggio, che serve a dire **dove** la rete non ha un tratto comune.
    """
    upstream = rule.then.placement is Placement.ON_THE_COMMON_RETURN
    chains: list[tuple[str, ...]] = []
    fallback: PortRef | None = None
    for component_id in context.anchors_of(
        network.id, rule.when.anchor_has_function, rule.when.anchor_has_trait
    ):
        if rule.when.network_carries_what_the_anchor_stores and not (
            context.stores(component_id, network.medium)
            or context.fills_on(component_id, network.id)
        ):
            continue
        if rule.when.network_fills_the_anchor and not context.fills_on(
            component_id, network.id
        ):
            continue
        for port in context.connected_ports(component_id):
            if port.flow not in rule.then.placement.flows:
                continue
            connection_id = context.connection_of_port[(component_id, port.id)]
            if context.network_of_connection.get(connection_id) != network.id:
                continue
            if fallback is None:
                fallback = PortRef(component_id=component_id, port_id=port.id)
            chain = context.run_from(
                connection_id, upstream=upstream, network_id=network.id
            )
            if chain:
                chains.append(chain)
    if not chains or fallback is None:
        return None, None
    shared = set(chains[0]).intersection(*(set(item) for item in chains[1:]))
    if not shared:
        return None, fallback
    head = next(item for item in chains[0] if item in shared)
    leaves, enters = context.pipe_ends[head]
    return (enters if upstream else leaves), fallback


def _limited(
    anchors: list[PortRef], cardinality: RuleCardinality, served: set[str]
) -> list[PortRef]:
    """La cardinalita' dichiarata, applicata.

    Senza, un vaso di espansione esce una volta per ogni ritorno del generatore:
    e' il difetto trovato prototipando, prima che ci fosse del codice da
    correggere.

    `served` porta i componenti gia' serviti da questa regola **su tutte le
    reti**, non solo su quella in esame: un volano sta contemporaneamente sul
    primario e sul secondario, e uno scarico per accumulo deve restare uno.
    """
    if cardinality is RuleCardinality.PER_PORT:
        return anchors
    if cardinality is RuleCardinality.PER_NETWORK:
        return anchors[:1]
    first: list[PortRef] = []
    for anchor in anchors:
        if anchor.component_id in served:
            continue
        served.add(anchor.component_id)
        first.append(anchor)
    return first


def _function_at(context: RuleContext, rule: RuleDefinition, anchor: PortRef) -> str:
    """La funzione che questa regola chiede **su questo ancoraggio**.

    Dipende dal regime di intercettazione dichiarato dall'ancoraggio: cio' che
    non deve mai restare escluso per distrazione vuole un organo bloccabile
    aperto, non quello comune.
    """
    return rule.then.function_for(context.shutoff_regime_of(anchor.component_id))


def _already_there(
    context: RuleContext, rule: RuleDefinition, network_id: str, anchor: PortRef
) -> bool:
    """La funzione che la regola porterebbe qui c'e' gia', nell'ambito dichiarato."""
    function = _function_at(context, rule, anchor)
    if rule.satisfied_by.scope is SatisfactionScope.ON_THE_NETWORK:
        return context.network_has(network_id, function)
    # Un accessorio posato sull'attacco di servizio non sta sulla tubazione
    # principale: camminando lungo quella non lo si troverebbe, e lo si
    # riproporrebbe a ogni passata.
    if context.service_port_is_taken(anchor.component_id, function):
        return True
    return context.port_carries(anchor, function)


def _matches(context: RuleContext, rule: RuleDefinition, network: NetworkModel) -> bool:
    """La rete e' una di quelle di cui la regola parla."""
    if network.domain != rule.when.network_domain:
        return False
    if rule.when.network_medium is not None and network.medium != rule.when.network_medium:
        return False
    if rule.when.network_has_function is not None and not context.network_has(
        network.id, rule.when.network_has_function
    ):
        return False
    return not (
        rule.when.network_lacks_function is not None
        and context.network_has(network.id, rule.when.network_lacks_function)
    )


def _gap(
    context: RuleContext,
    rule: RuleDefinition,
    network: NetworkModel,
    anchor: PortRef,
    reason: GapReason = GapReason.MISSING_PIECE,
) -> RuleGap:
    return RuleGap(
        rule_id=rule.id,
        rule_version=rule.version,
        category=rule.category,
        name=rule.name,
        network_id=network.id,
        medium=network.medium,
        anchor=anchor,
        missing_function=_function_at(context, rule, anchor),
        reason=reason,
        rationale=rule.rationale,
        source=rule.source,
    )


def evaluate(
    project: ProjectModel, catalog: ComponentRegistry, rules: RuleRegistry
) -> Evaluation:
    """Le integrazioni che il modello non ha ancora, con il perche' di ciascuna,
    e i punti in cui una regola si applica ma il catalogo non ha il pezzo."""
    context = RuleContext.build(project, catalog)
    taken = {item.id for item in project.components}
    proposals: list[RuleProposal] = []
    gaps: dict[tuple[str, str, str, str], RuleGap] = {}

    for rule in rules.all():
        # Il regime della centrale si legge come ogni altra proprieta'
        # dichiarata (D-106): una regola dell'altro regime non parla affatto.
        if not _regime_allows(rule, project.plant_regime):
            continue
        served: set[str] = set()
        # Le reti in ordine di nome, non nell'ordine del file: quale rete si
        # serve per prima decide, per le regole a cardinalita' limitata, su
        # quale attacco l'accessorio si posa — e non puo' dipendere da come
        # l'impianto e' stato scritto.
        for network in sorted(project.networks, key=lambda item: item.id):
            if not _matches(context, rule, network):
                continue

            if rule.then.placement.on_a_common_run:
                # Il pezzo non si posa su un attacco dell'ancoraggio ma sul
                # tratto comune della rete. Una rete che non ne ha uno non si
                # serve in silenzio: e' un punto aperto per il progettista.
                found_anchor, fallback = _common_run_anchor(context, rule, network)
                if found_anchor is None and fallback is None:
                    continue
                if found_anchor is None and fallback is not None:
                    missing = _gap(
                        context, rule, network, fallback, GapReason.NO_COMMON_RUN
                    )
                    gaps.setdefault(missing.key, missing)
                    continue
                candidates = [item for item in (found_anchor,) if item is not None]
            else:
                candidates = _anchors(context, rule, network)

            # Un ancoraggio su un fluido per cui il catalogo non ha nessun pezzo
            # con quella funzione non si puo' servire — ma non si tace: diventa
            # un punto aperto, uno per rete e per funzione, perche' il pezzo che
            # manca in catalogo e' uno solo. Averne **due** e' un'altra cosa e
            # si ferma: la sceglierebbe il programma.
            anchors: list[PortRef] = []
            for anchor in candidates:
                if not catalog.serving(
                    _function_at(context, rule, anchor), network.medium
                ):
                    missing = _gap(context, rule, network, anchor)
                    gaps.setdefault(missing.key, missing)
                    continue
                # C2: una riserva che dichiara da dove si riempie riceve le
                # derivazioni **solo li'**. Uno stacco senza attacco dedicato,
                # saldato su un altro attacco della riserva, finirebbe sul
                # circuito sbagliato — lo scarico sull'uscita calda del
                # bollitore era esattamente questo. L'attacco di riempimento
                # verra' servito quando si valuta la sua rete.
                fill = context.fill_port_of(anchor.component_id)
                if fill is not None and anchor.port_id != fill:
                    definition = catalog.providing(
                        _function_at(context, rule, anchor), network.medium
                    )
                    if definition.attaches_on_a_branch and (
                        context.service_port_for(
                            anchor.component_id, _function_at(context, rule, anchor)
                        )
                        is None
                    ):
                        continue
                anchors.append(anchor)
            satisfied = {
                anchor.component_id
                for anchor in anchors
                if _already_there(context, rule, network.id, anchor)
            }
            # Un componente gia' servito su una rete e' servito e basta: il
            # volano sta sul primario e sul secondario, e uno scarico per
            # accumulo deve restare uno anche quando la prima passata non ha
            # proposto nulla perche' c'era gia'.
            served |= satisfied
            if rule.cardinality is RuleCardinality.PER_COMPONENT:
                # Una regola per componente si accontenta di **un** accessorio sul
                # pezzo, su qualunque attacco: guardare il singolo attacco la
                # faceva riproporre l'intercettazione del volano a ogni passata,
                # perche' la valvola era finita sull'altro lato.
                free = [item for item in anchors if item.component_id not in satisfied]
            else:
                free = [
                    anchor
                    for anchor in anchors
                    if not _already_there(context, rule, network.id, anchor)
                ]
            for anchor in _limited(free, rule.cardinality, served):
                function = _function_at(context, rule, anchor)
                definition = catalog.providing(function, network.medium)
                component_id = proposed_component_id(definition.id, anchor)
                if component_id in taken:
                    continue
                # Solo per chi pende da uno stacco, e solo se la macchina
                # dichiara l'attacco per quella funzione: altrimenti resta
                # vuoto e lo stacco si apre sulla tubazione (D-101).
                service_port = (
                    context.service_port_for(anchor.component_id, function)
                    if definition.attaches_on_a_branch
                    else None
                )
                # Lo stacco sulla tubazione vuole un raccordo di derivazione
                # per quel fluido. Se il catalogo non ce l'ha, proporre
                # farebbe crollare l'applicazione a meta' catena: e' lo
                # stesso silenzio del pezzo mancante, e si dichiara allo
                # stesso modo — un punto aperto, non un'eccezione.
                if (
                    definition.attaches_on_a_branch
                    and service_port is None
                    and not catalog.serving(BRANCH_OFF, network.medium)
                ):
                    missing = _gap(context, rule, network, anchor)
                    gaps.setdefault(missing.key, missing)
                    continue
                taken.add(component_id)
                proposals.append(
                    RuleProposal(
                        rule_id=rule.id,
                        rule_version=rule.version,
                        category=rule.category,
                        component_id=component_id,
                        definition_id=definition.id,
                        name=rule.name,
                        network_id=network.id,
                        anchor=anchor,
                        inlet_port=rule.then.inlet_port,
                        outlet_port=rule.then.outlet_port,
                        service_port=service_port,
                        rationale=rule.rationale,
                        source=rule.source,
                    )
                )
    return Evaluation(proposals=proposals, gaps=list(gaps.values()))


__all__ = ["BRANCH_OFF", "Evaluation", "evaluate"]
