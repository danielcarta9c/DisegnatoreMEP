"""Le tre proprieta' che P2 deve garantire, verificate dove la regola vive.

Non si contano totali (D-088): ogni prova cammina la fila dei pezzi **attacco
per attacco**, e chi non e' coperto viene nominato. Le proprieta' sono quelle
del piano, e valgono su un impianto qualunque:

1. ogni attacco di ogni cosa che si smonta in esercizio ha il proprio organo di
   chiusura — accessori compresi, non le sole macchine;
2. fra un dispositivo di sicurezza e cio' che protegge non c'e' nulla che si
   possa chiudere;
3. cio' che si chiude solo con organo bloccabile e' chiuso soltanto da organi
   bloccabili.

Il modello su cui si misurano e' la rigenerazione corrente del caso di
accettazione: un artefatto vecchio mostrato come attuale e' il difetto da cui
nasce il piano di rilancio, e l'ultima prova del file lo presidia.
"""

from collections import defaultdict
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, ComponentTrait
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
COMPLETE = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

CLOSES = frozenset({"isolation", "isolation_locked_open"})
"""Le funzioni degli organi che chiudono il fluido. Sono due perche' un vaso di
espansione pretende quello bloccabile aperto, non quello comune."""

LOCKS_OPEN = "isolation_locked_open"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def rules() -> RuleRegistry:
    return RuleRegistry.from_directory(RULES)


def complete() -> ProjectModel:
    return load_project(COMPLETE)


class Plant:
    """L'impianto come lo si legge camminandolo: attacchi, file, proprieta'."""

    def __init__(self, project: ProjectModel, registry: ComponentRegistry) -> None:
        self.project = project
        self.definitions: dict[str, ComponentDefinition] = {
            item.id: registry.get(item.definition_id) for item in project.components
        }
        self.inline = frozenset(
            item.id
            for item in project.components
            if registry.resolve(item.definition_id).is_inline
            or registry.get(item.definition_id).is_a_fitting
        )
        self.touching: dict[tuple[str, str], list[ConnectionModel]] = defaultdict(list)
        # Gli attacchi che **non** sono sul percorso: gli stacchi di servizio di
        # una macchina e il braccio di una derivazione. Chi cammina lungo un tubo
        # deve saperlo, altrimenti a ogni derivazione infila il ramo al posto
        # della corsa e riporta difetti che non ci sono.
        self.off_the_run: set[tuple[str, str]] = {
            (item.id, port.id)
            for item in project.components
            for port in registry.get(item.definition_id).ports
            if port.off_the_run
        }
        for connection in project.connections:
            for ref in (connection.endpoint_a, connection.endpoint_b):
                self.touching[(ref.component_id, ref.port_id)].append(connection)

        self.medium_of = {
            item.id: item.medium for item in project.networks
        }
        self.network_of = {
            connection.id: connection.network_id for connection in project.connections
        }

    def leaves_the_run(self, connection: ConnectionModel) -> bool:
        """Quella tubazione esce dal percorso: e' uno stacco."""
        return any(
            (ref.component_id, ref.port_id) in self.off_the_run
            for ref in (connection.endpoint_a, connection.endpoint_b)
        )

    def attachments_of(self, component_id: str) -> list[str]:
        """Gli attacchi **del percorso** che una tubazione tocca davvero.

        Gli stacchi di servizio restano fuori: lo scarico di un volano e' gia'
        un rubinetto, e pretendere una valvola sul suo stacco vorrebbe dire
        chiudere il rubinetto con un altro rubinetto."""
        return sorted(
            port
            for owner, port in self.touching
            if owner == component_id and (owner, port) not in self.off_the_run
        )

    def fluids_at(self, component_id: str, port_id: str) -> set[str]:
        """I fluidi delle tubazioni che toccano quell'attacco."""
        return {
            self.medium_of[self.network_of[connection.id]]
            for connection in self.touching[(component_id, port_id)]
        }

    def declaring(self, trait: ComponentTrait) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if definition.has_trait(trait)
        )

    def providing(self, function: str) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if function in definition.functions
        )

    def functions_of(self, component_id: str) -> frozenset[str]:
        return frozenset(self.definitions[component_id].functions)

    def chain_from(
        self,
        component_id: str,
        connection: ConnectionModel,
        seen: frozenset[str] | None = None,
    ) -> list[list[str]]:
        """Le file dei pezzi partendo da un attacco, fino al primo nodo compreso.

        Sono **piu' d'una** dove la strada si biforca. Un raccordo di derivazione
        ha tre bracci: la corsa prosegue di la', ma da qui — camminando a
        ritroso da cio' che pende dallo stacco — si esce in due direzioni, e la
        proprieta' da verificare vale su una di esse. Una camminata che ne
        scegliesse una sola riporterebbe difetti che non ci sono.
        """
        walked = (seen or frozenset()) | {component_id}
        peers = [
            ref.component_id
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if ref.component_id != component_id
        ]
        if not peers or peers[0] in walked:
            return [[]]
        peer = peers[0]
        if peer not in self.inline:
            return [[peer]]
        onward = [
            candidate
            for candidate in self.project.connections
            if candidate.id != connection.id
            and peer
            in (
                candidate.endpoint_a.component_id,
                candidate.endpoint_b.component_id,
            )
            # Dallo stacco non si prosegue: quello e' il ramo, non la corsa.
            and not self.leaves_the_run(candidate)
        ]
        if not onward:
            return [[peer]]
        return [
            [peer, *rest]
            for candidate in onward
            for rest in self.chain_from(peer, candidate, walked)
        ]

    def hanging_from(self, component_id: str) -> list[str]:
        """Cio' che pende dagli stacchi di quel pezzo.

        Uno stacco e' l'attacco di servizio di una macchina — lo scarico di un
        volano — oppure il braccio di una derivazione saldata sul tubo. In tutti
        e due i casi cio' che ci pende non sta sulla corsa, e chi cammina il tubo
        non lo incontrerebbe mai.
        """
        return [
            ref.component_id
            for owner, port_id in self.off_the_run
            if owner == component_id
            for connection in self.touching[(owner, port_id)]
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if ref.component_id != component_id
        ]

    def chains_of(self, component_id: str, port_id: str) -> list[list[str]]:
        return [
            chain
            for connection in self.touching[(component_id, port_id)]
            for chain in self.chain_from(component_id, connection)
        ]

    def closers_of(self, component_id: str, port_id: str) -> list[str]:
        """Il **primo** organo che chiude su ciascuna fila di quell'attacco.

        Il primo e non tutti: e' quello che separa il pezzo dal resto, ed e'
        quello di cui conta la specie."""
        found: list[str] = []
        for chain in self.chains_of(component_id, port_id):
            for item in chain:
                if self.functions_of(item) & CLOSES:
                    found.append(item)
                    break
        return found


def acceptance() -> Plant:
    return Plant(complete(), catalog())


# --- 1. ogni attacco di ogni cosa che si smonta in esercizio ------------------


def test_every_attachment_of_everything_serviceable_can_be_shut() -> None:
    """La prima proprieta', attacco per attacco. Nessun totale."""
    plant = acceptance()
    serviceable = plant.declaring(ComponentTrait.MAINTAINABLE)
    assert serviceable, "nessun pezzo si dichiara smontabile: la prova non direbbe nulla"
    uncovered = [
        f"{component_id}.{port_id}"
        for component_id in serviceable
        for port_id in plant.attachments_of(component_id)
        if not plant.closers_of(component_id, port_id)
    ]
    assert not uncovered, uncovered


def test_the_rule_covers_the_accessories_and_not_only_the_machines() -> None:
    """L'accettazione di P2: vale anche sugli accessori che si dichiarano
    smontabili, compresi quelli che le regole stesse hanno aggiunto.

    Si guarda cio' che nel modello completo non c'era in quello essenziale: sono
    gli accessori proposti dalle regole, e anche loro devono risultare
    intercettati su ogni attacco."""
    plant = acceptance()
    was_there = {item.id for item in load_project(ESSENTIAL).components}
    added = [
        component_id
        for component_id in plant.declaring(ComponentTrait.MAINTAINABLE)
        if component_id not in was_there
    ]
    assert added, "le regole non hanno aggiunto nessun accessorio smontabile"
    uncovered = [
        f"{component_id}.{port_id}"
        for component_id in added
        for port_id in plant.attachments_of(component_id)
        if not plant.closers_of(component_id, port_id)
    ]
    assert not uncovered, uncovered


def test_nothing_that_never_needs_shutting_asks_for_a_valve() -> None:
    """Il verso opposto: un organo di chiusura non chiede a sua volta due
    valvole, altrimenti quelle due ne vorrebbero altre quattro senza fine."""
    plant = acceptance()
    for component_id in plant.providing("isolation") + plant.providing(LOCKS_OPEN):
        assert not plant.definitions[component_id].has_trait(ComponentTrait.MAINTAINABLE)


# --- 2. niente di chiudibile fra una sicurezza e cio' che protegge ------------


def test_nothing_closable_stands_between_a_safety_device_and_what_it_protects() -> None:
    """La seconda proprieta', **per dispositivo di sicurezza**.

    Cio' che una sicurezza protegge e' il pezzo che dichiara di dover essere
    protetto dalla sovrapressione: la prova cerca quel pezzo lungo le file del
    dispositivo e pretende che ci arrivi senza incontrare nulla di chiudibile.
    Dall'altro lato una valvola c'e' e ci deve essere: e' il resto
    dell'impianto."""
    plant = acceptance()
    devices = plant.providing("safety")
    assert devices, "nessun dispositivo di sicurezza: la prova non direbbe nulla"
    unprotected: list[str] = []
    for device in devices:
        reaches = False
        for port_id in plant.attachments_of(device):
            for chain in plant.chains_of(device, port_id):
                for item in chain:
                    if plant.functions_of(item) & CLOSES:
                        break
                    if plant.definitions[item].has_trait(
                        ComponentTrait.NEEDS_OVERPRESSURE_PROTECTION
                    ):
                        reaches = True
                        break
        if not reaches:
            unprotected.append(device)
    assert not unprotected, unprotected


def test_what_never_closes_is_laid_after_everything_that_closes() -> None:
    """Perche' la proprieta' regga su un impianto qualunque, e non per fortuna.

    Le proposte si applicano nell'ordine del registro, e ogni accessorio entra
    **accanto** all'ancoraggio spingendo via chi c'era: l'ultimo posato resta
    attaccato alla macchina. Un organo che non si chiude mai deve percio' venire
    dopo ogni organo di chiusura, altrimenti una valvola finirebbe fra lui e cio'
    che protegge. Se un domani una regola cambia posto nel registro, questa
    prova lo dice prima che lo dica una tavola."""
    registry = catalog()

    def declares(rule: object, trait: ComponentTrait) -> bool:
        return any(
            definition.has_trait(trait)
            for function in rule.then.functions()  # type: ignore[attr-defined]
            for definition in registry.all()
            if function in definition.functions
        )

    ordered = rules().all()
    closes = [
        index
        for index, rule in enumerate(ordered)
        if set(rule.then.functions()) & CLOSES
    ]
    never = [
        index
        for index, rule in enumerate(ordered)
        if declares(rule, ComponentTrait.SHUTOFF_NEVER)
    ]
    assert closes and never, [rule.id for rule in ordered]
    assert max(closes) < min(never), [
        (index, ordered[index].id) for index in sorted(set(closes) | set(never))
    ]


def test_every_tank_can_empty_the_water_it_actually_holds() -> None:
    """Il difetto che ha fatto respingere P2, reso impossibile.

    Uno scarico su un serpentino svuota il circuito che attraversa il serbatoio,
    non il serbatoio: il serpentino e' uno scambiatore che ci passa dentro,
    l'acqua della riserva resta al suo posto. La prova pretende quindi che ogni
    serbatoio abbia uno scarico su una tubazione che serve **la riserva** — o
    porta il fluido tenuto in serbo, o e' il punto da cui la riserva dichiara
    di riempirsi (C2) — e lo verifica per serbatoio invece che contare gli
    scarichi: contarli darebbe due e sarebbe verde anche adesso."""
    plant = acceptance()
    tanks = plant.declaring(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
    assert tanks, "nessun serbatoio: la prova non direbbe nulla"
    stuck: list[str] = []
    for tank in tanks:
        stored = plant.definitions[tank].stored_medium
        assert stored is not None, tank
        # Lo scarico sta sull'attacco che il serbatoio dedica allo scarico, se
        # il costruttore ce l'ha messo — un volano si' — oppure su una
        # derivazione saldata dove la riserva si riempie, che e' come si svuota
        # un bollitore, perche' il bocchello non ce l'ha (SRC-018, C2).
        drained = any(
            "drain" in plant.functions_of(item) for item in plant.hanging_from(tank)
        )
        fill = plant.definitions[tank].fills_from
        for port_id in plant.attachments_of(tank):
            if stored not in plant.fluids_at(tank, port_id) and port_id != fill:
                continue
            for chain in plant.chains_of(tank, port_id):
                for item in chain:
                    if plant.functions_of(item) & CLOSES:
                        break
                    if "drain" in plant.functions_of(item) or any(
                        "drain" in plant.functions_of(hung)
                        for hung in plant.hanging_from(item)
                    ):
                        drained = True
                        break
        if not drained:
            stuck.append(f"{tank} tiene in serbo {stored} e non lo puo' svuotare")
    assert not stuck, stuck


def test_a_drain_stands_on_the_tank_side_of_the_organ_that_closes_it() -> None:
    """Uno scarico dietro una valvola chiusa svuota la tratta, non il serbatoio.

    Per ogni scarico si cammina verso cio' che tiene un volume proprio: ci si
    deve arrivare senza incontrare nulla che si chiuda."""
    plant = acceptance()
    drains = plant.providing("drain")
    assert drains, "nessuno scarico: la prova non direbbe nulla"
    stranded: list[str] = []
    for drain in drains:
        reaches = False
        for port_id in plant.attachments_of(drain):
            for chain in plant.chains_of(drain, port_id):
                for item in chain:
                    if plant.functions_of(item) & CLOSES:
                        break
                    if plant.definitions[item].has_trait(
                        ComponentTrait.HOLDS_ITS_OWN_VOLUME
                    ):
                        reaches = True
                        break
        if not reaches:
            stranded.append(drain)
    assert not stranded, stranded


def test_a_safety_device_is_never_given_a_valve_of_its_own() -> None:
    """La stessa proprieta' dal lato delle proposte: nessuna regola propone un
    organo di chiusura ancorandolo a cio' che non si chiude mai."""
    registry = catalog()
    project = load_project(ESSENTIAL)
    _, proposals, _ = saturate(project, registry, rules())
    definitions = {item.id: item.definition_id for item in project.components}
    for proposal in proposals:
        definitions[proposal.component_id] = proposal.definition_id
    for proposal in proposals:
        if not set(registry.get(proposal.definition_id).functions) & CLOSES:
            continue
        anchor = registry.get(definitions[proposal.anchor.component_id])
        assert anchor.shutoff_regime is not ComponentTrait.SHUTOFF_NEVER, proposal


# --- 3. cio' che si chiude solo con organo bloccabile -------------------------


def test_what_locks_open_is_closed_only_by_an_organ_that_locks_open() -> None:
    """La terza proprieta', **per pezzo che la dichiara**.

    Su ogni suo attacco l'organo che lo separa dal resto deve essere di quelli
    che si bloccano aperti: un rubinetto comune lo escluderebbe per distrazione,
    ed e' esattamente cio' che il regime vieta."""
    plant = acceptance()
    guarded = plant.declaring(ComponentTrait.SHUTOFF_LOCKABLE_ONLY)
    assert guarded, "nessun pezzo dichiara quel regime: la prova non direbbe nulla"
    wrong: list[str] = []
    for component_id in guarded:
        for port_id in plant.attachments_of(component_id):
            closers = plant.closers_of(component_id, port_id)
            if not closers:
                wrong.append(f"{component_id}.{port_id}: nessun organo")
            wrong.extend(
                f"{component_id}.{port_id}: {item}"
                for item in closers
                if LOCKS_OPEN not in plant.functions_of(item)
            )
    assert not wrong, wrong


def test_the_rule_proposes_the_lockable_organ_wherever_the_regime_asks_it() -> None:
    """La stessa proprieta' dove la regola vive, e non solo dove e' finita.

    Si guarda ogni proposta di organo di chiusura: se l'ancoraggio dichiara di
    chiudersi solo con organo bloccabile, l'organo proposto deve esserlo."""
    registry = catalog()
    project = load_project(ESSENTIAL)
    _, proposals, _ = saturate(project, registry, rules())
    definitions = {item.id: item.definition_id for item in project.components}
    for proposal in proposals:
        definitions[proposal.component_id] = proposal.definition_id
    checked = 0
    for proposal in proposals:
        anchor = registry.get(definitions[proposal.anchor.component_id])
        if anchor.shutoff_regime is not ComponentTrait.SHUTOFF_LOCKABLE_ONLY:
            continue
        checked += 1
        assert LOCKS_OPEN in registry.get(proposal.definition_id).functions, proposal
    assert checked, "nessun ancoraggio con quel regime: la prova non direbbe nulla"


# --- il modello completo e' quello che il pacchetto corrente rigenera ---------


# --- l'artefatto che il committente approva ----------------------------------

PM_DOCUMENT = ROOT / "docs" / "prodotto" / "REGOLE_ACCESSORI.md"
BEFORE_P2 = ESSENTIAL
"""L'impianto **prima** delle integrazioni: quello che l'ingegnere ha descritto.

Era il caso a quattro fasce, che era un modello gia' saturato da una passata
vecchia delle regole: un artefatto, non uno stato. Confrontarsi con lui misurava
la differenza fra due versioni del motore invece della crescita che il documento
dichiara."""


def cards() -> list[str]:
    """I titoli delle schede: una riga di secondo livello che comincia con un numero."""
    return [
        line
        for line in PM_DOCUMENT.read_text("utf-8").splitlines()
        if line.startswith("## ") and line[3:4].isdigit()
    ]


def test_the_document_for_the_pm_carries_one_card_per_rule() -> None:
    """Una scheda per regola, e ognuna approvabile o bocciabile da sola."""
    assert PM_DOCUMENT.is_file()
    assert len(cards()) == len(rules().all()), cards()


def test_every_rule_has_its_card_under_the_name_the_engineer_reads() -> None:
    text = PM_DOCUMENT.read_text("utf-8")
    missing = [rule.name for rule in rules().all() if rule.name not in text]
    assert not missing, missing


def test_the_document_for_the_pm_speaks_no_developer_language() -> None:
    """Niente nomi di file, niente identificativi di regola, niente codice: e'
    la condizione perche' un non sviluppatore possa bocciarlo."""
    text = PM_DOCUMENT.read_text("utf-8")
    leaked = [rule.id for rule in rules().all() if rule.id in text]
    leaked += [path.name for path in sorted(RULES.glob("*.json")) if path.name in text]
    leaked += [item.id for item in catalog().all() if item.id in text]
    assert not leaked, leaked


def test_the_document_does_not_overstate_how_much_the_plant_grew() -> None:
    """L'unico numero del documento e' un confronto, e deve dire il vero.

    P1 e' stato respinto per un consuntivo falso: qui la frase «piu' del doppio»
    si misura sui due impianti pubblicati invece che ricordarla a memoria."""
    registry = catalog()

    def organs(path: Path) -> int:
        return sum(
            1
            for item in load_project(path).components
            if set(registry.get(item.definition_id).functions) & CLOSES
        )

    flowing = " ".join(PM_DOCUMENT.read_text("utf-8").split())
    assert "più del doppio" in flowing
    assert organs(COMPLETE) > 2 * organs(BEFORE_P2)


def test_rerunning_the_rules_on_the_complete_case_proposes_nothing() -> None:
    """Idempotenza sul file pubblicato, non solo sul modello in memoria."""
    assert evaluate(complete(), catalog(), rules()).proposals == []


def test_the_stored_complete_case_is_the_current_regeneration() -> None:
    """Mai piu' un artefatto vecchio mostrato come attuale: il file pubblicato
    e' esattamente cio' che il pacchetto corrente rigenera dall'essenziale."""
    regenerated, _, _ = saturate(load_project(ESSENTIAL), catalog(), rules())
    assert canonical_json(regenerated) == COMPLETE.read_text(encoding="utf-8")
