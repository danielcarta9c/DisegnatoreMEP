"""Il motore: modello piu' regole, e ne escono proposte.

Funzione pura. Non tocca il modello, non scrive niente, non decide niente: §9.2
dice che il motore non trasforma una proposta in progetto approvato, e il modo
piu' semplice di rispettarlo e' non dargli la possibilita' di farlo.

L'ordine e' quello delle regole nel registro, poi delle reti e dei componenti
nell'ordine del modello. Deterministico e ispezionabile: due esecuzioni danno la
stessa lista, e la lista si legge dall'alto come la si e' scritta.
"""

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import PortRef, ProjectModel

from .context import RuleContext
from .proposal import RuleProposal, proposed_component_id
from .registry import RuleRegistry
from .schema import RuleCardinality, RuleDefinition


def _anchors(context: RuleContext, rule: RuleDefinition, network_id: str) -> list[PortRef]:
    """Gli attacchi su cui questa regola potrebbe posare qualcosa, in ordine."""
    found: list[PortRef] = []
    for component_id in context.components_with(network_id, rule.when.anchor_has_function):
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


def _already_there(context: RuleContext, rule: RuleDefinition, network_id: str, anchor: PortRef) -> bool:
    criterion = rule.satisfied_by
    if criterion.network_has_function is not None and context.network_has(
        network_id, criterion.network_has_function
    ):
        return True
    return criterion.port_carries_function is not None and context.port_carries(
        anchor, criterion.port_carries_function
    )


def evaluate(
    project: ProjectModel, catalog: ComponentRegistry, rules: RuleRegistry
) -> list[RuleProposal]:
    """Le integrazioni che il modello non ha ancora, con il perche' di ciascuna."""
    context = RuleContext.build(project, catalog)
    taken = {item.id for item in project.components}
    proposals: list[RuleProposal] = []

    for rule in rules.all():
        served: set[str] = set()
        for network in project.networks:
            if network.domain != rule.when.network_domain:
                continue
            if rule.when.network_medium is not None and network.medium != rule.when.network_medium:
                continue
            if rule.when.network_has_function is not None and not context.network_has(
                network.id, rule.when.network_has_function
            ):
                continue
            if rule.when.network_lacks_function is not None and context.network_has(
                network.id, rule.when.network_lacks_function
            ):
                continue

            anchors = _anchors(context, rule, network.id)
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
                component_id = proposed_component_id(rule.then.definition_id, anchor)
                if component_id in taken:
                    continue
                taken.add(component_id)
                proposals.append(
                    RuleProposal(
                        rule_id=rule.id,
                        rule_version=rule.version,
                        category=rule.category,
                        component_id=component_id,
                        definition_id=rule.then.definition_id,
                        name=rule.name,
                        network_id=network.id,
                        anchor=anchor,
                        inlet_port=rule.then.inlet_port,
                        outlet_port=rule.then.outlet_port,
                        rationale=rule.rationale,
                        source=rule.source,
                    )
                )
    return proposals


__all__ = ["evaluate"]
