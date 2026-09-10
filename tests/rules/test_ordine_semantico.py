"""Il blocco A di DRAW-006-R1: l'ordine non dipende dagli identificativi.

Il PM, sulla PR #24: «L'ordine di uno stacco dipende ancora dall'ID: la
derivazione eredita i vincoli dal primo organo invece che dall'accessorio
terminale. Il manometro puo' quindi precedere il riempimento.»

Le quattro proprieta' che il pacchetto chiede:

1. il **soggetto semantico** di uno stacco e' l'accessorio terminale raggiunto
   attraverso i raccordi e gli organi propri dello stacco, non il primo organo
   incontrato;
2. `before`/`after` ordinano **topologicamente** nel verso del fluido;
   identificativi, ordine nel file e ordine delle connessioni possono spareggiare
   soltanto elementi semanticamente equivalenti;
3. l'ordine semantico e' un **vincolo duro**: non lo si conserva sbagliato
   perche' costa meno;
4. rinominare gli identificativi, invertirne l'ordinamento e mescolare le
   connessioni non cambia ne' l'ordine funzionale ne' il costo.

Le prove sono **generali**: gli impianti si costruiscono qui, nessuna soglia e
nessun identificativo di una tavola entra nelle attese, e le voci di catalogo
usate sono quelle pubblicate — non ci sono eccezioni scritte per una fixture.
"""

import json
import random
from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.assembly.runs import Run, runs_of
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    FITTING_FUNCTIONS,
    SERVICE_ORGAN_FUNCTIONS,
    ComponentDefinition,
)
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleDefinition

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

FILLING = "filling"
PRESSURE_MEASUREMENT = "pressure_measurement"
EXPANSION = "expansion"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


def rule_table() -> dict[str, RuleDefinition]:
    return {item.id: item for item in rules().all()}


# ---------------------------------------------------------------------------
# Gli impianti di prova, costruiti qui
# ---------------------------------------------------------------------------


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def circuito_chiuso() -> ProjectModel:
    """Un generatore, una riserva sanitaria, un terminale e l'acqua fredda.

    E' il piu' piccolo impianto che riceva **tutto** il corredo di rete —
    riempimento, manometro, vaso — e quindi il piu' piccolo su cui l'ordine
    dichiarato di quel corredo significhi qualcosa. L'acqua fredda c'e' perche'
    il riempimento e' un ponte fra due reti (blocco D) e senza una sorgente
    approvata non sarebbe un pezzo ma una domanda.
    """
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-ordine",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 10),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(
                id="anello", name="anello", domain="hydronic", medium="heating_water"
            ),
            NetworkModel(
                id="fredda", name="fredda", domain="hydronic", medium="cold_water"
            ),
            NetworkModel(
                id="sanitaria",
                name="sanitaria",
                domain="hydronic",
                medium="domestic_hot_water",
            ),
        ],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water"),
            ComponentInstance(id="terminale", definition_id="fan-coil"),
            ComponentInstance(id="riserva", definition_id="dhw-heat-pump"),
            ComponentInstance(id="acquedotto", definition_id="cold-water-inlet"),
            ComponentInstance(id="utenze", definition_id="dhw-draw-off"),
        ],
        connections=[
            _pipe("m", "anello", ("generatore", "water_supply"), ("terminale", "in")),
            _pipe("r", "anello", ("terminale", "out"), ("generatore", "water_return")),
            _pipe("f", "fredda", ("acquedotto", "a"), ("riserva", "cold_in")),
            _pipe("s", "sanitaria", ("riserva", "dhw_out"), ("utenze", "a")),
        ],
    )


def anello_semplice() -> ProjectModel:
    """Il solo circuito chiuso: generatore, terminale, andata e ritorno.

    Serve alla prova sul **costo**, che deve confrontare due tavole e non la
    completezza del corredo: meno pezzi ci sono, piu' la prova e' veloce e piu'
    chiaro e' cosa sta misurando.
    """
    base = circuito_chiuso()
    tenuti = {"generatore", "terminale"}
    return base.model_copy(
        update={
            "networks": [item for item in base.networks if item.id == "anello"],
            "components": [item for item in base.components if item.id in tenuti],
            "connections": [
                item
                for item in base.connections
                if {item.endpoint_a.component_id, item.endpoint_b.component_id} <= tenuti
            ],
        }
    )


def completato(project: ProjectModel) -> ProjectModel:
    completed, _, _ = saturate(project, catalog(), rules())
    # Il modello passa dal JSON canonico come nella catena della CLI: e' il
    # modello che il disegno riceve, e l'ordine dev'essere quello.
    return ProjectModel.model_validate(json.loads(canonical_json(completed)))


# ---------------------------------------------------------------------------
# Lettura: la fila dei mestieri, senza nominare nessun pezzo
# ---------------------------------------------------------------------------


def definition_of(model: ProjectModel, component_id: str) -> ComponentDefinition:
    return catalog().get(
        next(item.definition_id for item in model.components if item.id == component_id)
    )


def _speaks_for(model: ProjectModel, component_id: str) -> str:
    """L'accessorio terminale in fondo allo stacco di quel pezzo, se ce n'e' uno.

    La prova lo ricalcola per conto proprio, camminando sul grafo: cosi' misura
    la proprieta' e non l'implementazione che dovrebbe darla.
    """
    definitions = {item.id: definition_of(model, item.id) for item in model.components}
    stubs = {
        (item.id, port.id)
        for item in model.components
        for port in definitions[item.id].ports
        if port.off_the_run
    }
    peers: dict[str, set[str]] = {item.id: set() for item in model.components}
    for pipe in model.connections:
        peers[pipe.endpoint_a.component_id].add(pipe.endpoint_b.component_id)
        peers[pipe.endpoint_b.component_id].add(pipe.endpoint_a.component_id)
    hung: str | None = None
    for pipe in model.connections:
        for mine, other in (
            (pipe.endpoint_a, pipe.endpoint_b),
            (pipe.endpoint_b, pipe.endpoint_a),
        ):
            if mine.component_id == component_id and (
                mine.component_id,
                mine.port_id,
            ) in stubs:
                hung = other.component_id
    if hung is None:
        return component_id
    seen = {component_id, hung}
    cursor = hung
    while True:
        jobs = set(definitions[cursor].functions)
        if not (jobs & FITTING_FUNCTIONS or jobs & SERVICE_ORGAN_FUNCTIONS):
            return cursor
        onward = sorted(peers[cursor] - seen)
        if len(onward) != 1:
            return cursor
        cursor = onward[0]
        seen.add(cursor)


def fila_di_mestieri(model: ProjectModel) -> list[tuple[str, ...]]:
    """Le tratte del modello, ciascuna come fila di **mestieri**.

    Nessun identificativo entra nel risultato: due impianti uguali con nomi
    diversi devono dare la stessa fila, ed e' esattamente cio' che la prova
    confronta. La fila di una tratta si orienta sui mestieri dei suoi due capi,
    cosi' che leggere la tratta al contrario non cambi il risultato.
    """
    found: list[tuple[str, ...]] = []
    for run in runs_of(model, catalog(), rule_table()):
        row = [
            ",".join(
                sorted(definition_of(model, _speaks_for(model, item.component_id)).functions)
            )
            for item in run.pieces
        ]
        head, tail = (
            ",".join(sorted(definition_of(model, ref.component_id).functions))
            for ref in (run.head, run.tail)
        )
        forward: tuple[str, ...] = (head, *row, tail)
        backward: tuple[str, ...] = (tail, *reversed(row), head)
        found.append(min(forward, backward))
    return sorted(found)


def ordine_dal_capo(model: ProjectModel, run: Run, anchor_id: str) -> list[frozenset[str]]:
    """I mestieri dei pezzi della tratta, letti dal capo dato verso l'altro."""
    row = [
        frozenset(definition_of(model, _speaks_for(model, item.component_id)).functions)
        for item in run.pieces
    ]
    return row if run.head.component_id == anchor_id else list(reversed(row))


def _posizione(row: list[frozenset[str]], function: str) -> int:
    for index, jobs in enumerate(row):
        if function in jobs:
            return index
    return -1


# ---------------------------------------------------------------------------
# Rinominare, invertire, mescolare
# ---------------------------------------------------------------------------


def rinominato(project: ProjectModel, prefix: str, invert: bool) -> ProjectModel:
    """Lo stesso impianto con altri identificativi, e l'ordinamento invertito.

    I nomi nuovi sono derivati dalla **posizione** nel file: con `invert`
    l'ordine alfabetico dei nomi e' l'opposto dell'ordine del file, cosi' che
    qualunque residuo di spareggio alfabetico si veda subito.
    """
    total = len(project.components)
    names = {
        item.id: f"{prefix}-{(total - index if invert else index):03d}"
        for index, item in enumerate(project.components)
    }
    return project.model_copy(
        update={
            "components": [
                item.model_copy(update={"id": names[item.id]})
                for item in project.components
            ],
            "connections": [
                item.model_copy(
                    update={
                        "id": f"{prefix}-pipe-{index:03d}",
                        "endpoint_a": PortRef(
                            component_id=names[item.endpoint_a.component_id],
                            port_id=item.endpoint_a.port_id,
                        ),
                        "endpoint_b": PortRef(
                            component_id=names[item.endpoint_b.component_id],
                            port_id=item.endpoint_b.port_id,
                        ),
                    }
                )
                for index, item in enumerate(project.connections)
            ],
            "subsystems": [
                item.model_copy(
                    update={
                        "component_ids": [names[key] for key in item.component_ids]
                    }
                )
                for item in project.subsystems
            ],
        }
    )


def mescolato(project: ProjectModel, seed: int) -> ProjectModel:
    """Lo stesso impianto con le connessioni scritte in un altro ordine."""
    shuffled = list(project.connections)
    random.Random(seed).shuffle(shuffled)
    return project.model_copy(update={"connections": shuffled})


# ---------------------------------------------------------------------------
# A.1 — il soggetto semantico di uno stacco
# ---------------------------------------------------------------------------


def test_la_derivazione_parla_per_l_accessorio_in_fondo_allo_stacco() -> None:
    """Il piede di uno stacco porta i vincoli dell'accessorio, non dell'organo.

    E' il difetto che il PM ha visto: fra la presa e lo strumento c'e' un
    organo, e la derivazione ereditava i vincoli **di quello** — che non ne ha
    — invece di quelli dello strumento. Da li' in poi l'ordine del corredo di
    rete lo decideva l'ordine alfabetico degli identificativi.
    """
    model = completato(circuito_chiuso())
    table = rule_table()
    con_organo = 0
    for run in runs_of(model, catalog(), table):
        for piece in run.pieces:
            if not definition_of(model, piece.component_id).is_a_fitting:
                continue
            terminale = _speaks_for(model, piece.component_id)
            if terminale == piece.component_id:
                continue
            atteso = definition_of(model, terminale)
            assert piece.functions == frozenset(atteso.functions), (
                f"{piece.component_id} parla per {sorted(piece.functions)}: in "
                f"fondo al suo stacco c'e' {sorted(atteso.functions)}"
            )
            fra = _organi_dello_stacco(model, piece.component_id, terminale)
            con_organo += bool(fra)
    assert con_organo, (
        "nessuno stacco dell'impianto di prova porta un organo prima del "
        "proprio accessorio: la prova non proverebbe niente"
    )


def _organi_dello_stacco(
    model: ProjectModel, fitting_id: str, terminale: str
) -> list[str]:
    """Gli organi che stanno fra la presa e il proprio accessorio."""
    peers: dict[str, set[str]] = {item.id: set() for item in model.components}
    for pipe in model.connections:
        peers[pipe.endpoint_a.component_id].add(pipe.endpoint_b.component_id)
        peers[pipe.endpoint_b.component_id].add(pipe.endpoint_a.component_id)
    found: list[str] = []
    seen = {fitting_id}
    cursor = fitting_id
    while cursor != terminale:
        onward = sorted(peers[cursor] - seen)
        candidates = [
            item
            for item in onward
            if set(definition_of(model, item).functions) & SERVICE_ORGAN_FUNCTIONS
            or item == terminale
        ]
        if not candidates:
            break
        cursor = candidates[0]
        seen.add(cursor)
        if cursor != terminale:
            found.append(cursor)
    return found


# ---------------------------------------------------------------------------
# A.2 e A.3 — l'ordine e' un vincolo, e viene dai vincoli dichiarati
# ---------------------------------------------------------------------------


def test_il_manometro_segue_il_riempimento_come_la_sua_regola_dichiara() -> None:
    """`after: filling` e' un vincolo duro, non una preferenza.

    Nessun identificativo compare qui: si legge la regola del manometro, si
    verifica che dichiari di venire dopo il riempimento, e poi si guarda la
    fila. Se un giorno la regola cambiasse, cambierebbe anche l'attesa.
    """
    manometro = next(
        item
        for item in rules().all()
        if PRESSURE_MEASUREMENT in item.then.functions()
    )
    assert FILLING in manometro.ordering.after, (
        "la regola del manometro non dichiara piu' di venire dopo il "
        "riempimento: senza quel vincolo questa prova non misura niente"
    )
    model = completato(circuito_chiuso())
    generatore = next(
        item.id
        for item in model.components
        if "heat_generation" in definition_of(model, item.id).functions
    )
    provata = False
    for run in runs_of(model, catalog(), rule_table()):
        if generatore not in (run.head.component_id, run.tail.component_id):
            continue
        row = ordine_dal_capo(model, run, generatore)
        gauge, filling = _posizione(row, PRESSURE_MEASUREMENT), _posizione(row, FILLING)
        if gauge < 0 or filling < 0:
            continue
        provata = True
        assert filling < gauge, (
            f"camminando dal generatore verso l'impianto il manometro sta a "
            f"{gauge} e il riempimento a {filling}: la regola vuole il "
            f"contrario"
        )
    assert provata, (
        "manometro e riempimento non sono finiti sulla stessa tratta: la prova "
        "non ha guardato quello che nomina"
    )


def _capofila(run: Run) -> dict[str, str]:
    """Il pezzo che guida ciascun blocco della tratta.

    Un accessorio non viaggia solo: gli organi ancorati **a lui** — le valvole
    che lo isolano, una per lato — sono suoi e gli stanno accanto. Il blocco e'
    l'unita' che si mette in fila, e i vincoli d'ordine parlano fra blocchi: la
    valvola del filtro non e' «l'intercettazione» di cui il filtro dichiara di
    venire dopo, e' la sua.
    """
    order = {item.component_id: index for index, item in enumerate(run.pieces)}
    leader: dict[str, str] = {}
    for item in run.pieces:
        current = item
        while current.anchor in order:
            current = run.pieces[order[current.anchor]]
        leader[item.component_id] = current.component_id
    return leader


def test_il_corredo_di_rete_segue_i_propri_vincoli_dichiarati() -> None:
    """Ogni `before`/`after` dichiarato e' rispettato dalla fila che ne esce.

    E' la forma generale della prova precedente: invece di guardare una coppia
    scelta a mano, si rileggono **tutti** i vincoli delle regole applicate e si
    pretende che la fila li rispetti. Una regola nuova entra qui da sola.

    Si confrontano blocchi, non pezzi singoli: gli organi di un accessorio sono
    suoi e viaggiano con lui.
    """
    model = completato(circuito_chiuso())
    controllati = 0
    for run in runs_of(model, catalog(), rule_table()):
        leader = _capofila(run)
        for anchor in (run.head.component_id, run.tail.component_id):
            row = ordine_dal_capo(model, run, anchor)
            pieces = (
                run.pieces
                if run.head.component_id == anchor
                else tuple(reversed(run.pieces))
            )
            for index, piece in enumerate(pieces):
                if piece.anchor != anchor:
                    continue
                mine = leader[piece.component_id]
                for direction, jobs_wanted in (("dopo", piece.after), ("prima", piece.before)):
                    for job in jobs_wanted:
                        for other, jobs in enumerate(row):
                            if job not in jobs:
                                continue
                            if leader[pieces[other].component_id] == mine:
                                continue
                            # Una tratta ha due capi, e «prima» e «dopo» si
                            # contano da quello a cui il pezzo e' ancorato: cio'
                            # che appartiene all'altro capo si conta di la', e
                            # confrontarli non vorrebbe dire niente.
                            if pieces[other].anchor not in (None, anchor):
                                continue
                            wrong = other > index if direction == "dopo" else other < index
                            assert not wrong, (
                                f"{piece.component_id} dichiara di venire "
                                f"{direction} di {job}, e {job} sta a {other} "
                                f"invece che dall'altra parte di {index}"
                            )
                        controllati += 1
    assert controllati, "nessun vincolo d'ordine e' stato messo alla prova"


# ---------------------------------------------------------------------------
# A.4 — rinominare, invertire, mescolare
# ---------------------------------------------------------------------------


def test_l_ordine_funzionale_non_cambia_rinominando_gli_identificativi() -> None:
    """Due impianti uguali con nomi diversi danno la stessa fila di mestieri."""
    base = fila_di_mestieri(completato(circuito_chiuso()))
    altro = fila_di_mestieri(completato(rinominato(circuito_chiuso(), "zz", invert=True)))
    assert base == altro


def test_l_ordine_funzionale_non_cambia_mescolando_le_connessioni() -> None:
    """Scrivere le tubazioni in un altro ordine non cambia la fila."""
    base = fila_di_mestieri(completato(circuito_chiuso()))
    for seed in (1, 7, 13):
        assert fila_di_mestieri(completato(mescolato(circuito_chiuso(), seed))) == base


def test_il_costo_della_tavola_non_cambia_rinominando_gli_identificativi() -> None:
    """Anche la geometria e' invariante: stesso impianto, stesso costo.

    E' il seguito naturale della prova precedente. Se un nome entrasse nella
    posa, due impianti identici darebbero due tavole diverse — e nessuna delle
    due sarebbe spiegabile.
    """
    prima = compose_drawing(completato(anello_semplice()), catalog(), NOVE_C_A3)
    dopo = compose_drawing(
        completato(rinominato(anello_semplice(), "zz", invert=True)), catalog(), NOVE_C_A3
    )
    assert _costo(prima) == _costo(dopo)


def _costo(drawing: object) -> tuple[int, int, float]:
    """Pieghe, incroci e millimetri della tavola: il costo, senza i nomi."""
    sheet = drawing.sheets[0]  # type: ignore[attr-defined]
    bends = sum(
        max(len(segment) - 2, 0) for route in sheet.routes for segment in route.segments
    )
    crossings = sum(len(route.crossings) for route in sheet.routes)
    length = sum(
        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        for route in sheet.routes
        for segment in route.segments
        for before, after in zip(segment, segment[1:], strict=False)
    )
    return bends, crossings, round(length, 3)
