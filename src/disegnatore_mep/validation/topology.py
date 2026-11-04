from collections import Counter

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, ComponentTrait, PortDefinition
from disegnatore_mep.domains.registry import DomainRegistry, default_domain_registry
from disegnatore_mep.model.project import ComponentInstance, PortRef, ProjectModel
from disegnatore_mep.model.types import IssueSeverity, PortFlow

from .issues import ValidationIssue, ValidationReport


def _issue(code: str, message: str, entity_ids: list[str]) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=IssueSeverity.BLOCKING,
        message=message,
        entity_ids=entity_ids,
    )


def _resolve_port(
    ref: PortRef,
    components: dict[str, ComponentInstance],
    catalog: ComponentRegistry,
    connection_id: str,
) -> tuple[PortDefinition | None, list[ValidationIssue]]:
    component = components.get(ref.component_id)
    if component is None:
        return None, [
            _issue(
                "UNKNOWN_COMPONENT",
                f"connection {connection_id}: unknown component {ref.component_id}",
                [connection_id, ref.component_id],
            )
        ]
    try:
        definition = catalog.get(component.definition_id)
    except CatalogError:
        return None, [
            _issue(
                "UNKNOWN_COMPONENT_DEFINITION",
                f"connection {connection_id}: unknown definition {component.definition_id}",
                [connection_id, component.id, component.definition_id],
            )
        ]
    port = next((item for item in definition.ports if item.id == ref.port_id), None)
    if port is None:
        return None, [
            _issue(
                "UNKNOWN_PORT",
                f"connection {connection_id}: unknown port {ref.port_id}",
                [connection_id, component.id, ref.port_id],
            )
        ]
    return port, []


def validate_project(
    project: ProjectModel,
    catalog: ComponentRegistry,
    domains: DomainRegistry | None = None,
) -> ValidationReport:
    domain_registry = domains or default_domain_registry()
    components = {item.id: item for item in project.components}
    networks = {item.id: item for item in project.networks}
    subsystems = {item.id: item for item in project.subsystems}
    usage: Counter[tuple[str, str]] = Counter()
    seen_edges: dict[tuple[str, tuple[str, str], tuple[str, str]], str] = {}
    issues: list[ValidationIssue] = []

    for component in project.components:
        if not catalog.contains(component.definition_id):
            issues.append(
                _issue(
                    "UNKNOWN_COMPONENT_DEFINITION",
                    f"unknown definition {component.definition_id}",
                    [component.id, component.definition_id],
                )
            )

    # Lo spostamento indica un attacco che c'e' e che una tubazione tocca (REL-009):
    # un nome sbagliato fermerebbe le regole a meta' catena.
    collegati = {
        (ref.component_id, ref.port_id)
        for connection in project.connections
        for ref in (connection.endpoint_a, connection.endpoint_b)
    }
    for voce in project.accessori_tolti:
        if voce.altrove is None:
            continue
        pezzo, attacco = voce.altrove.split(".", 1)
        if (pezzo, attacco) not in collegati:
            issues.append(
                _issue(
                    "UNKNOWN_RELOCATION_PORT",
                    f"{voce.pezzo} is moved to {voce.altrove}, and no connection touches that "
                    f"port: name a connected port as component.port",
                    [voce.pezzo, pezzo],
                )
            )

    issues.extend(_dosatori_fuori_posto(project, catalog))
    issues.extend(_sfiati_con_due_rubinetti(project, catalog))
    issues.extend(_vasi_sanitari_dietro_il_ritegno(project, catalog))
    issues.extend(_note_del_progettista(project))

    # Il bordo dichiarato dal progettista nomina funzioni che il catalogo conosce
    # (REL-009, I-192): un nome sbagliato non toglierebbe niente, in silenzio.
    funzioni = {function for definition in catalog.all() for function in definition.functions}
    for component in project.components:
        for campo, voci in (("a_bordo", component.a_bordo), ("non_a_bordo", component.non_a_bordo)):
            for function in voci:
                if function not in funzioni:
                    issues.append(
                        _issue(
                            "UNKNOWN_ON_BOARD_FUNCTION",
                            f"component {component.id}: {campo} names {function}, which no "
                            f"catalog entry does; the functions are the `functions` of the "
                            f"catalog entries",
                            [component.id, function],
                        )
                    )

    for subsystem in project.subsystems:
        for component_id in subsystem.component_ids:
            if component_id not in components:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_COMPONENT",
                        f"unknown component {component_id} in subsystem {subsystem.id}",
                        [subsystem.id, component_id],
                    )
                )
        for network_id in subsystem.network_ids:
            if network_id not in networks:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_NETWORK",
                        f"unknown network {network_id} in subsystem {subsystem.id}",
                        [subsystem.id, network_id],
                    )
                )

    for sheet in project.sheets:
        for subsystem_id in sheet.subsystem_ids:
            if subsystem_id not in subsystems:
                issues.append(
                    _issue(
                        "UNKNOWN_SHEET_SUBSYSTEM",
                        f"unknown subsystem {subsystem_id} in sheet {sheet.id}",
                        [sheet.id, subsystem_id],
                    )
                )
        assigned = {item.subsystem_id for item in sheet.band_assignments}
        for assignment in sheet.band_assignments:
            if assignment.subsystem_id not in subsystems:
                issues.append(
                    _issue(
                        "UNKNOWN_BAND_SUBSYSTEM",
                        f"sheet {sheet.id} assigns unknown subsystem "
                        f"{assignment.subsystem_id} to band {assignment.band.value}",
                        [sheet.id, assignment.subsystem_id],
                    )
                )
        # Un sottosistema dichiarato sulla tavola ma raccolto da nessuna fascia
        # non verrebbe disegnato: sparirebbe in silenzio dall'elaborato, che e'
        # peggio di un errore visibile.
        for subsystem_id in sheet.subsystem_ids:
            if sheet.band_assignments and subsystem_id not in assigned:
                issues.append(
                    _issue(
                        "UNASSIGNED_SUBSYSTEM",
                        f"sheet {sheet.id} carries subsystem {subsystem_id} but no "
                        f"band collects it, so it would not be drawn",
                        [sheet.id, subsystem_id],
                    )
                )

    for connection in project.connections:
        if connection.endpoint_a.component_id == connection.endpoint_b.component_id:
            issues.append(
                _issue(
                    "SELF_LOOP_CONNECTION",
                    f"connection {connection.id} joins component "
                    f"{connection.endpoint_a.component_id} to itself",
                    [connection.id, connection.endpoint_a.component_id],
                )
            )

        endpoint_a = (connection.endpoint_a.component_id, connection.endpoint_a.port_id)
        endpoint_b = (connection.endpoint_b.component_id, connection.endpoint_b.port_id)
        first_endpoint, second_endpoint = sorted((endpoint_a, endpoint_b))
        # `network_id` stays inside the edge key: two connections between the same
        # ports on different networks are legitimately distinct connections, not
        # duplicates. Same-network multiplicity is caught separately below by
        # PORT_CONNECTION_LIMIT.
        edge_key = (connection.network_id, first_endpoint, second_endpoint)
        first_id = seen_edges.get(edge_key)
        if first_id is None:
            seen_edges[edge_key] = connection.id
        else:
            # `entity_ids` stays sorted so the report is order-invariant, but the
            # message names the true first-declared connection as the original
            # and the current (later-declared) connection as the duplicate.
            pair = sorted([connection.id, first_id])
            issues.append(
                _issue(
                    "DUPLICATE_CONNECTION",
                    f"connection {connection.id} duplicates {first_id} on network {connection.network_id}",
                    pair,
                )
            )

        port_a, errors_a = _resolve_port(connection.endpoint_a, components, catalog, connection.id)
        port_b, errors_b = _resolve_port(connection.endpoint_b, components, catalog, connection.id)
        issues.extend(errors_a)
        issues.extend(errors_b)

        if port_a is not None:
            usage[endpoint_a] += 1
        if port_b is not None:
            usage[endpoint_b] += 1

        network = networks.get(connection.network_id)
        if network is None:
            issues.append(
                _issue(
                    "UNKNOWN_NETWORK",
                    f"unknown network {connection.network_id}",
                    [connection.id, connection.network_id],
                )
            )
            continue
        if port_a is None or port_b is None:
            continue
        for issue in domain_registry.get(network.domain).validate_pair(port_a, port_b, network):
            issues.append(
                issue.model_copy(update={"entity_ids": [connection.id, *issue.entity_ids]})
            )

    for component in project.components:
        if not catalog.contains(component.definition_id):
            continue
        definition = catalog.get(component.definition_id)
        for port in definition.ports:
            count = usage[(component.id, port.id)]
            if port.required and count == 0:
                issues.append(
                    _issue(
                        "REQUIRED_PORT_UNCONNECTED",
                        f"required port {port.id} is unconnected",
                        [component.id, port.id],
                    )
                )
            # Una tubazione per attacco, sempre (D-100). Dove due si incontrano
            # ci vuole un pezzo che le unisca, con la propria sigla: due tubi
            # sullo stesso bocchello non esistono, e lasciarli passare faceva
            # scegliere a chi guardava per ultimo quale delle due contasse.
            if count > 1:
                issues.append(
                    _issue(
                        "PORT_CONNECTION_LIMIT",
                        f"port {port.id} has {count} pipes; an attachment carries "
                        f"exactly one. Where two pipes meet there is a piece that "
                        f"joins them, and it has its own tag",
                        [component.id, port.id],
                    )
                )

    unique = {
        (item.code, tuple(item.entity_ids), item.message): item
        for item in issues
    }
    ordered = sorted(unique.values(), key=lambda item: (item.code, item.entity_ids, item.message))
    return ValidationReport(issues=ordered)


TRATTAMENTO_DELL_ACQUA = "water_treatment"


SFIATI_CON_RUBINETTO = frozenset({"air-vent", "air-vent-solar"})
"""Le voci dello sfiato che si disegnano con il loro rubinetto (I-210, I-211)."""


def _sfiati_con_due_rubinetti(project: ProjectModel, catalog: ComponentRegistry) -> list[ValidationIssue]:
    """Lo sfiato porta il suo rubinetto di intercettazione (I-210, I-211).

    Dal 5 ottobre 2026 sfiato e rubinetto sono un pezzo solo, con un simbolo solo: il
    PO, «sostituiamo il simbolo ovunque». Un grafo scritto prima dichiarava la
    valvola sullo stacco e lo sfiato dopo — «sfiato con valvola a sfera» (I-193) —, e
    disegnato oggi avrebbe due rubinetti uno sopra l'altro. Si toglie la valvola; e se
    il progettista vuole lo sfiato senza rubinetto, la voce e' `air-vent-plain`."""
    pezzi = {item.id: item.definition_id for item in project.components}
    issues: list[ValidationIssue] = []
    for connessione in project.connections:
        for sfiato, altro in (
            (connessione.endpoint_a.component_id, connessione.endpoint_b.component_id),
            (connessione.endpoint_b.component_id, connessione.endpoint_a.component_id),
        ):
            if pezzi.get(sfiato) not in SFIATI_CON_RUBINETTO:
                continue
            voce = pezzi.get(altro)
            if voce is None or not catalog.contains(voce) or "isolation" not in catalog.get(voce).functions:
                continue
            issues.append(
                _issue(
                    "AIR_VENT_ISOLATED_TWICE",
                    f"lo sfiato {sfiato} ha gia' il suo rubinetto, e la valvola {altro} sullo "
                    f"stacco ne disegnerebbe un secondo: togli {altro} e collega lo sfiato "
                    f"dov'era la valvola. Se lo sfiato e' senza rubinetto, la voce e' "
                    f"air-vent-plain (I-211)",
                    [sfiato, altro],
                )
            )
    return issues
"""Il mestiere del dosatore di polifosfati (REL-009, I-198)."""


def _dosatori_fuori_posto(project: ProjectModel, catalog: ComponentRegistry) -> list[ValidationIssue]:
    """Il dosatore di polifosfati sta **solo** sull'acqua fredda che entra nell'accumulo
    dell'acqua calda sanitaria (I-198, D-204).

    Il PO: «va installato esclusivamente sulla linea di ingresso dell'acqua fredda
    sanitaria che alimenta il boiler di accumulo dell'ACS. Non deve assolutamente essere
    inserito nell'acqua tecnica». Nell'ACS entra sempre acqua nuova, e il calcare si
    deposita scaldandosi; l'acqua tecnica e' un circuito chiuso, e i polifosfati ci
    farebbero fanghi. Gli attacchi del dosatore sono di acqua fredda, quindi su un
    circuito di riscaldamento il grafo gia' non regge; qui si guarda **dove va l'acqua
    dopo il dosatore**: deve arrivare a chi scalda l'acqua sanitaria — un bollitore, un
    accumulo combinato, una pompa di calore per ACS —, e non deve arrivare a un gruppo di
    riempimento, che la porterebbe nell'acqua tecnica."""
    pezzi = {item.id: item for item in project.components}

    def mestieri(component_id: str) -> frozenset[str]:
        pezzo = pezzi.get(component_id)
        if pezzo is None or not catalog.contains(pezzo.definition_id):
            return frozenset()
        return frozenset(catalog.get(pezzo.definition_id).functions)

    def scalda_l_acs(component_id: str) -> bool:
        pezzo = pezzi[component_id]
        if not catalog.contains(pezzo.definition_id) or "dhw_mixing" in mestieri(component_id):
            return False
        return any(port.medium == "domestic_hot_water" for port in catalog.get(pezzo.definition_id).ports)

    # Il verso di una tubazione nel grafo non dice da che parte va l'acqua: si parte
    # dall'attacco d'uscita del dosatore e si va avanti senza ripassare da lui.
    vicini: dict[str, list[str]] = {}
    uscite: dict[str, list[str]] = {}
    for connessione in project.connections:
        a, b = connessione.endpoint_a, connessione.endpoint_b
        vicini.setdefault(a.component_id, []).append(b.component_id)
        vicini.setdefault(b.component_id, []).append(a.component_id)
        for ref, altro in ((a, b), (b, a)):
            istanza = pezzi.get(ref.component_id)
            if istanza is None or not catalog.contains(istanza.definition_id):
                continue
            porte = {port.id: port for port in catalog.get(istanza.definition_id).ports}
            if ref.port_id in porte and porte[ref.port_id].flow == PortFlow.OUT:
                uscite.setdefault(ref.component_id, []).append(altro.component_id)

    issues: list[ValidationIssue] = []
    for dosatore in sorted(item.id for item in project.components if TRATTAMENTO_DELL_ACQUA in mestieri(item.id)):
        raggiunti: list[str] = []
        visti = {dosatore}
        frontiera = list(uscite.get(dosatore, []))
        while frontiera:
            pezzo = frontiera.pop(0)
            if pezzo in visti or pezzo not in pezzi:
                continue
            visti.add(pezzo)
            raggiunti.append(pezzo)
            if scalda_l_acs(pezzo) or "filling" in mestieri(pezzo):
                continue
            frontiera.extend(vicini.get(pezzo, []))
        riempimenti = [item for item in raggiunti if "filling" in mestieri(item)]
        accumuli = [item for item in raggiunti if scalda_l_acs(item)]
        if riempimenti:
            issues.append(
                _issue(
                    "DOSER_FEEDS_THE_TECHNICAL_WATER",
                    f"il dosatore di polifosfati {dosatore} alimenta il riempimento "
                    f"{', '.join(riempimenti)}: i polifosfati andrebbero nell'acqua tecnica, che e' un "
                    f"circuito chiuso. Il dosatore sta solo sull'acqua fredda che entra nell'accumulo "
                    f"dell'ACS, a valle della derivazione del riempimento (I-198)",
                    [dosatore, *riempimenti],
                )
            )
        if not accumuli:
            issues.append(
                _issue(
                    "DOSER_NOT_ON_THE_DHW_FEED",
                    f"il dosatore di polifosfati {dosatore} non alimenta nessun accumulo di acqua "
                    f"calda sanitaria: sta solo sull'acqua fredda che entra nel bollitore o "
                    f"nell'accumulo dell'ACS (I-198)",
                    [dosatore],
                )
            )
    return issues



DIETRO_IL_RITEGNO = frozenset({"non_return", "safety"})
"""I mestieri che chiudono la via del ritorno verso l'acquedotto: il ritegno, e il gruppo
di sicurezza sanitario che lo porta dentro (D-178)."""


def _vasi_sanitari_dietro_il_ritegno(project: ProjectModel, catalog: ComponentRegistry) -> list[ValidationIssue]:
    """Il vaso sanitario sta **fra il dispositivo di non ritorno e il bollitore** (D-178, I-272).

    Sull'alimentazione fredda di una riserva che si scalda, il ritegno — da solo, o dentro il
    gruppo di sicurezza — toglie all'acqua che dilata la via verso la rete: il vaso che sta dal
    lato dell'acquedotto non la vede, e a ogni ciclo si apre la sicurezza. Si cammina
    dall'attacco di riempimento della riserva verso la rete, lungo la tubazione, e il primo
    vaso appeso deve venire **prima** del primo pezzo che chiude il ritorno; e un pezzo che lo
    chiude ci deve essere. Il caso che lo ha mostrato (I-272): il vaso scritto a mano
    sull'acqua fredda, senza il gruppo. Le regole posano il gruppo sull'attacco del bollitore,
    cioe' fra lui e il vaso; il vaso lo deve posare la regola, e la risposta «il bollitore non
    lo porta dentro» si scrive sul bollitore: `non_a_bordo: ["expansion"]`."""
    pezzi = {item.id: item for item in project.components}

    def definizione(component_id: str) -> ComponentDefinition | None:
        pezzo = pezzi.get(component_id)
        if pezzo is None or not catalog.contains(pezzo.definition_id):
            return None
        return catalog.get(pezzo.definition_id)

    tubi: dict[tuple[str, str], tuple[str, str, str]] = {}
    for connessione in project.connections:
        a, b = connessione.endpoint_a, connessione.endpoint_b
        tubi[(a.component_id, a.port_id)] = (b.component_id, b.port_id, connessione.network_id)
        tubi[(b.component_id, b.port_id)] = (a.component_id, a.port_id, connessione.network_id)

    def chiude_il_ritorno(component_id: str) -> bool:
        voce = definizione(component_id)
        pezzo = pezzi[component_id]
        if voce is None:
            return False
        bordo = (set(voce.carries_on_board) | set(pezzo.a_bordo)) - set(pezzo.non_a_bordo)
        return bool(DIETRO_IL_RITEGNO & (set(voce.functions) | bordo))

    def vaso_in_fondo(radice: str, porta: str, rete: str) -> str | None:
        """Lo stacco dal braccio di un raccordo, sulla stessa rete d'acqua fredda: attraverso
        valvole e raccordi, fino al vaso."""
        visti = {radice}
        frontiera: list[tuple[str, str, str] | None] = [tubi.get((radice, porta))]
        while frontiera:
            dove = frontiera.pop()
            if dove is None or dove[0] in visti:
                continue
            pezzo, entrata, _ = dove
            visti.add(pezzo)
            voce = definizione(pezzo)
            if voce is None:
                continue
            if "expansion" in voce.functions:
                return pezzo
            for port in voce.ports:
                if port.id != entrata and port.medium == "cold_water":
                    seguente = tubi.get((pezzo, port.id))
                    if seguente is not None and seguente[2] == rete:
                        frontiera.append(seguente)
        return None

    issues: list[ValidationIssue] = []
    for riserva in sorted(pezzi):
        voce = definizione(riserva)
        if (
            voce is None
            or voce.fills_from is None
            or ComponentTrait.NEEDS_OVERPRESSURE_PROTECTION not in voce.trait_set
        ):
            continue
        dove = tubi.get((riserva, voce.fills_from))
        if dove is None:
            continue
        rete = dove[2]
        primo_vaso: tuple[int, str] | None = None
        primo_ritegno: tuple[int, str] | None = None
        visti = {riserva}
        passo = 0
        while dove is not None and dove[2] == rete and dove[0] not in visti:
            pezzo, entrata, _ = dove
            visti.add(pezzo)
            corrente = definizione(pezzo)
            if corrente is None:
                break
            linea = [port for port in corrente.ports if port.medium == "cold_water" and port.id != entrata]
            if corrente.is_a_fitting:
                bracci = [port for port in linea if port.id == "branch"]
                linea = [port for port in linea if port.id != "branch"]
                if entrata == "branch":
                    break
                for braccio in bracci:
                    vaso = vaso_in_fondo(pezzo, braccio.id, rete)
                    if vaso is not None and primo_vaso is None:
                        primo_vaso = (passo, vaso)
            elif chiude_il_ritorno(pezzo) and primo_ritegno is None:
                primo_ritegno = (passo, pezzo)
            if len(linea) != 1:
                break
            dove = tubi.get((pezzo, linea[0].id))
            passo += 1
        if primo_vaso is None:
            continue
        if primo_ritegno is not None and primo_vaso[0] < primo_ritegno[0]:
            continue
        vaso = primo_vaso[1]
        dove_sta = (
            f"dal lato dell'acquedotto rispetto a {primo_ritegno[1]}, che chiude il ritorno"
            if primo_ritegno is not None
            else "dove le regole posano il ritegno e il gruppo di sicurezza fra lui e la riserva"
        )
        issues.append(
            _issue(
                "DHW_EXPANSION_UPSTREAM_OF_THE_CHECK",
                f"il vaso sanitario {vaso} sta sull'acqua fredda di {riserva} {dove_sta}: la "
                f"dilatazione non lo trova, e apre la sicurezza. Il vaso sta fra il dispositivo "
                f"di non ritorno e la riserva (D-178), e lo posa la regola: togli il vaso scritto "
                f"a mano e, se {riserva} non lo porta dentro, scrivilo su {riserva} — "
                f"`non_a_bordo: [\"expansion\"]` — o, se l'acqua calda e' centralizzata, "
                f"`\"produzione\": \"centralizzata\"` fra le sue proprieta' (I-272)",
                [vaso, riserva, *([primo_ritegno[1]] if primo_ritegno else [])],
            )
        )
    return issues


MASSIMO_DELLE_NOTE = 5
"""Il tetto delle note di posa (D-232), lo stesso di `graphics.note`."""


def _note_del_progettista(project: ProjectModel) -> list[ValidationIssue]:
    """Le note di posa del progettista (REL-017, I-271) che la tavola non porterebbe: piu'
    di cinque, o in un progetto che non e' esecutivo. Sono avvisi, non blocchi: la tavola
    esce, ma una nota che non c'e' non si deve perdere in silenzio."""
    metadati = project.metadata
    issues: list[ValidationIssue] = []
    if len(metadati.note_di_posa) > MASSIMO_DELLE_NOTE:
        issues.append(
            ValidationIssue(
                code="TOO_MANY_INSTALLATION_NOTES",
                severity=IssueSeverity.WARNING,
                message=(
                    f"metadata.note_di_posa ha {len(metadati.note_di_posa)} note e il riquadro "
                    f"ne porta al massimo {MASSIMO_DELLE_NOTE} (D-232): escono le prime "
                    f"{MASSIMO_DELLE_NOTE}, e nessuna di quelle generate. Le altre si accorpano "
                    f"o si tolgono"
                ),
                entity_ids=[metadati.project_id],
            )
        )
    if (metadati.note_di_posa or metadati.note_tolte) and metadati.livello != "esecutivo":
        issues.append(
            ValidationIssue(
                code="INSTALLATION_NOTES_ONLY_IN_THE_EXECUTIVE",
                severity=IssueSeverity.WARNING,
                message=(
                    "metadata porta note di posa del progettista, e il progetto non e' "
                    "esecutivo-costruttivo: nel definitivo il riquadro delle note non esce "
                    "(D-232). Per farle uscire, metadata.livello = \"esecutivo\""
                ),
                entity_ids=[metadati.project_id],
            )
        )
    return issues
