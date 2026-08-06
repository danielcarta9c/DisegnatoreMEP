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

from .context import RuleContext
from .proposal import RuleGap, RuleProposal, proposed_component_id
from .registry import RuleRegistry
from .schema import RuleCardinality, RuleDefinition, SatisfactionScope


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
        # il serbatoio.
        if rule.when.network_carries_what_the_anchor_stores and not context.stores(
            component_id, network.medium
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
        served: set[str] = set()
        for network in project.networks:
            if not _matches(context, rule, network):
                continue

            # Un ancoraggio su un fluido per cui il catalogo non ha nessun pezzo
            # con quella funzione non si puo' servire — ma non si tace: diventa
            # un punto aperto, uno per rete e per funzione, perche' il pezzo che
            # manca in catalogo e' uno solo. Averne **due** e' un'altra cosa e
            # si ferma: la sceglierebbe il programma.
            anchors: list[PortRef] = []
            for anchor in _anchors(context, rule, network.id):
                if catalog.serving(_function_at(context, rule, anchor), network.medium):
                    anchors.append(anchor)
                    continue
                missing = _gap(context, rule, network, anchor)
                gaps.setdefault(missing.key, missing)
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
                definition = catalog.providing(
                    _function_at(context, rule, anchor), network.medium
                )
                component_id = proposed_component_id(definition.id, anchor)
                if component_id in taken:
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
                        rationale=rule.rationale,
                        source=rule.source,
                    )
                )
    return Evaluation(proposals=proposals, gaps=list(gaps.values()))


__all__ = ["Evaluation", "evaluate"]
