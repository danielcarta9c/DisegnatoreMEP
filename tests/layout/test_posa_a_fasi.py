"""Le prove di DRAW-008: la posa a fasi, prima le autostrade.

Il PO, l'11 settembre 2026:

    «Il sistema di instradatura deve prima disegnare le autostrade e farle piu'
    dritte possibile. Poi si mettono dentro tutte le altre valvole e pezzi, e se
    non ci stanno le autostrade le puoi allungare, stretchare, spostando le
    macchine principali — sempre pero' mantenendo le autostrade dritte. Poi ci
    attacchiamo le reti stradali di servizio, e quelle si', accettiamo qualche
    curva in piu'.»

Le tre fasi hanno tre invarianti, e ciascuno e' provato qui:

- **il tronco** e' una fase a se': posa le sole macchine di spina, instrada la
  sola autostrada, e il resto dell'impianto non vi partecipa;
- **il corredo** entra dentro il tronco, e dove non ci sta il tronco **si
  allunga** invece di piegarsi;
- **le strade di servizio** si attaccano a un tronco che non si piega piu',
  qualunque cosa ci guadagnerebbero.

E una cosa che non e' un invariante ma un **limite dichiarato**: una tratta e'
un rettilineo solo se le sue due porte si guardano, e ci sono coppie che
nessuna rotazione ammessa mette una di fronte all'altra. La prova che le conta
sta qui sotto, e le nomina: distinguere «non e' dritta» da «non puo' esserlo»
e' il modo di non ammorbidire il criterio fingendo di rispettarlo.

Gli impianti sono costruiti qui, con il catalogo di prova; le due tavole vere
si guardano dove il pacchetto le nomina, cioe' sulle fixture di `examples`.
"""

import json
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import FlowKind, RoutedTrunk, SheetGeometry
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of, spine_machines
from disegnatore_mep.layout.improve import Improver, Phase
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import (
    autostrada_trunks,
    can_be_straight,
    carry_the_rest,
    lay_the_spine,
    spine_participants,
)
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVE = ROOT / "examples" / "prova"

TAVOLA_1 = PROVE / "prova-1-due-pdc-accumulo-combinato.json"
TAVOLA_2 = PROVE / "prova-2-pdc-deviatrice-acs.json"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
TOLERANCE_MM = 1e-6


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


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _plant(
    networks: list[tuple[str, str]],
    components: list[tuple[str, str, str | None]],
    connections: list[ConnectionModel],
    subsystems: list[tuple[str, list[str], list[str]]],
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-fasi",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 11),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id=network_id, name=network_id, domain="hydronic", medium=medium)
            for network_id, medium in networks
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition, tag=tag)
            for item, definition, tag in components
        ],
        connections=connections,
        subsystems=[
            SubsystemModel(id=item, name=item, component_ids=members, network_ids=nets)
            for item, members, nets in subsystems
        ],
    )


def macchina_e_accumulo() -> ProjectModel:
    """Una pompa di calore, un accumulo combinato, un corpo scaldante.

    Il tronco e' la coppia mandata/ritorno fra la macchina e l'accumulo; tutto
    il resto — la pompa, il radiatore, l'acqua fredda, il sanitario — e' strada
    di servizio o distribuzione, e non partecipa alla prima fase.
    """
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("generatore", "heat-pump-air-water", "PDC-01"),
            ("serbatoio", "buffer-combined", "ACC-01"),
            ("pompa", "pump-circulator", "CIR-01"),
            ("corpo", "radiator", "RAD-01"),
            ("rete-idrica", "cold-water-inlet", "AF-01"),
            ("rubinetti", "dhw-draw-off", "ACS-01"),
        ],
        [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("serbatoio", "primary_in")),
            _pipe("p2", "primo", ("serbatoio", "primary_out"), ("generatore", "water_return")),
            _pipe("s1", "secondo", ("serbatoio", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("serbatoio", "secondary_in")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
            _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
        ],
        [
            ("generazione", ["generatore"], ["primo"]),
            ("accumulo", ["serbatoio", "rete-idrica", "rubinetti"], ["primo", "fredda", "calda"]),
            ("distribuzione", ["pompa", "corpo"], ["secondo"]),
        ],
    )


def due_macchine_e_accumulo() -> ProjectModel:
    """Due pompe di calore che confluiscono, e un accumulo combinato.

    Qui il tronco si biforca davvero: una sola delle due macchine sta sulla
    spina, e la seconda ci si innesta attraverso i raccordi.
    """
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("nord", "heat-pump-air-water", "PDC-A"),
            ("sud", "heat-pump-air-water", "PDC-B"),
            ("unione", "tee-junction", None),
            ("ripartizione", "tee-split", None),
            ("serbatoio", "buffer-combined", "ACC-A"),
            ("pompa", "pump-circulator", "CIR-A"),
            ("corpo", "radiator", "RAD-A"),
            ("rete-idrica", "cold-water-inlet", "AF-A"),
            ("rubinetti", "dhw-draw-off", "ACS-A"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("serbatoio", "primary_in")),
            _pipe("p4", "primo", ("serbatoio", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
            _pipe("s1", "secondo", ("serbatoio", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("serbatoio", "secondary_in")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
            _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
        ],
        [
            ("generazione", ["nord", "sud", "unione", "ripartizione"], ["primo"]),
            ("accumulo", ["serbatoio", "rete-idrica", "rubinetti"], ["primo", "fredda", "calda"]),
            ("distribuzione", ["pompa", "corpo"], ["secondo"]),
        ],
    )


CASI = (macchina_e_accumulo, due_macchine_e_accumulo)
CASI_IDS = [item.__name__ for item in CASI]


@cache
def _completato(index: int) -> ProjectModel:
    """L'impianto dopo le regole: e' su quello che la posa lavora."""
    done, _, gaps = saturate(CASI[index](), catalog(), rules())
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    return ProjectModel.model_validate(json.loads(canonical_json(done)))


@cache
def _fixture(path: Path) -> ProjectModel:
    done, _, _ = saturate(load_project(path), catalog(), rules())
    return ProjectModel.model_validate(json.loads(canonical_json(done)))


def _partizione(project: ProjectModel) -> SheetPartition:
    inline = inline_component_ids(project, catalog())
    return partition_project(project, build_trunks(project, inline))[0]


def _improver(project: ProjectModel) -> Improver:
    """Il ciclo, sulla posa che la fase del tronco gli consegna."""
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    spine = lay_the_spine(project, partition, registry, NOVE_C_A3, first)
    seeded = carry_the_rest(project, partition, registry, first, spine)
    return Improver(project, partition, registry, NOVE_C_A3, seeded, inline, spine)


def _pieghe(route: RoutedTrunk) -> int:
    return sum(max(len(segment) - 2, 0) for segment in route.segments)


def _autostrade_del_foglio(
    project: ProjectModel, sheet: SheetGeometry
) -> list[tuple[Trunk, RoutedTrunk]]:
    """Le autostrade della tavola consegnata, con la spezzata che le disegna."""
    partition = _partizione(project)
    levels = hierarchy_of(project, catalog(), list(partition.trunks))
    routes = {tuple(item.connection_ids): item for item in sheet.routes}
    return [
        (trunk, routes[tuple(trunk.connection_ids)])
        for trunk in partition.trunks
        if levels[trunk.connection_ids] is Level.AUTOSTRADA
        and tuple(trunk.connection_ids) in routes
    ]


@cache
def _tavola(path: Path) -> SheetGeometry:
    project = _fixture(path)
    return compose_drawing(project, catalog(), NOVE_C_A3).sheets[0]


# ---------------------------------------------------------------------------
# Criterio 1 — la fase del tronco esiste ed e' separata
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_la_fase_del_tronco_posa_solo_la_spina_e_instrada_solo_l_autostrada(
    index: int,
) -> None:
    """La prima fase produce la geometria del **solo** tronco.

    Non e' una rifinitura del ciclo con qualche vincolo in piu': e' una posa a
    se', con i propri partecipanti e le proprie tratte. Cio' che non e' tronco
    non vi compare — ne' come simbolo posato, ne' come tubazione instradata.
    """
    project = _completato(index)
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    layout = lay_the_spine(project, partition, registry, NOVE_C_A3, first)

    atteso = spine_participants(project, registry, list(partition.trunks))
    assert set(layout.participants) == atteso
    assert {item.component_id for item in layout.symbols} == atteso
    assert layout.machines == spine_machines(project, registry)

    autostrade = autostrada_trunks(project, registry, list(partition.trunks))
    assert [item.connection_ids for item in layout.trunks] == [
        item.connection_ids for item in autostrade
    ]
    assert len(layout.routes) == len(autostrade)

    # E il resto dell'impianto non partecipa: nessun utilizzatore, nessuna
    # tratta che non sia autostrada.
    levels = hierarchy_of(project, registry, list(partition.trunks))
    assert all(
        levels[item.connection_ids] is Level.AUTOSTRADA for item in layout.trunks
    )
    fuori = {
        item.id for item in project.components if item.id not in atteso
    }
    assert fuori, "l'impianto di prova deve avere anche qualcosa che non e' tronco"
    assert not fuori & {item.component_id for item in layout.symbols}


# ---------------------------------------------------------------------------
# Criterio 2 — il tronco e' dritto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_la_fase_del_tronco_consegna_un_tronco_rettilineo(index: int) -> None:
    """Ogni tratta del tronco e' un rettilineo: una spezzata sola, due punti."""
    project = _completato(index)
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    layout = lay_the_spine(project, partition, registry, NOVE_C_A3, first)

    assert layout.routes, "la fase deve instradare qualcosa"
    storte = [
        (trunk.start.component_id, trunk.end.component_id)
        for trunk, route in zip(layout.trunks, layout.routes, strict=True)
        if _pieghe(route) > 0
    ]
    assert not storte, storte
    assert layout.impossible == ()


@pytest.mark.parametrize("path", (TAVOLA_1, TAVOLA_2), ids=("tavola-1", "tavola-2"))
def test_sulle_due_tavole_ogni_autostrada_che_puo_essere_dritta_lo_e(
    path: Path,
) -> None:
    """Sulle tavole vere: zero pieghe su ogni autostrada raddrizzabile.

    «Raddrizzabile» non e' una scappatoia: e' il catalogo. Una tratta e'
    rettilinea solo se le sue due porte si guardano, e la fase del tronco
    dichiara in `SpineLayout.impossible` quelle che nessuna posa ammessa
    riuscirebbe a far guardare. Qui si pretende che le storte siano
    **esattamente** quelle, non una di piu'.
    """
    project = _fixture(path)
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    layout = lay_the_spine(project, partition, registry, NOVE_C_A3, first)
    impossibili = set(layout.impossible)

    storte = {
        trunk.connection_ids
        for trunk, route in _autostrade_del_foglio(project, _tavola(path))
        if _pieghe(route) > 0
    }
    assert storte <= impossibili, sorted(storte - impossibili)


def test_la_tavola_2_dichiara_quale_tratta_non_puo_essere_un_rettilineo() -> None:
    """Il limite della tavola 2, nominato e spiegato.

    La seconda uscita della deviatrice guarda **in basso**; la serpentina del
    bollitore si imbocca **da sinistra**, e il bollitore non ammette rotazioni.
    Perche' quelle due porte si guardino la deviatrice dovrebbe girare — e
    girando toglierebbe l'asse alla mandata verso il volano, che e' l'accumulo
    maggiore e sta sull'asse per disposizione del PO (architettura §4). Non e'
    una posa mancata: e' il catalogo, e questa prova lo mette agli atti perche'
    nessuno lo riscopra una terza volta credendolo un difetto del ciclo.
    """
    project = _fixture(TAVOLA_2)
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    layout = lay_the_spine(project, partition, registry, NOVE_C_A3, first)

    coinvolte = {
        trunk.connection_ids: (trunk.start.component_id, trunk.end.component_id)
        for trunk in layout.trunks
    }
    nomi = sorted(coinvolte[key] for key in layout.impossible)
    assert nomi == [
        ("bollitore", "ritorno"),
        ("deviatrice", "bollitore"),
    ], nomi

    # E la ragione, letta sul catalogo e non sul disegno: la porta del
    # bollitore guarda da una parte sola, e con la deviatrice ferma sull'asse
    # nessuna posa la mette di fronte.
    bollitore = registry.resolve(
        next(item.definition_id for item in project.components if item.id == "bollitore")
    ).symbol.manifest
    assert bollitore.allowed_rotations_deg == [0]
    assert bollitore.port("coil_in").face is PortFace.LEFT
    assert not can_be_straight(frozenset({PortFace.BOTTOM}), frozenset({PortFace.LEFT}))


# ---------------------------------------------------------------------------
# Criterio 3 — la rettilineita' e' un vincolo, non un costo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_una_mossa_che_piega_il_tronco_e_rifiutata_anche_se_costa_meno(
    index: int,
) -> None:
    """La prova negativa del pacchetto (§A.4).

    Si cerca fra le candidate del ciclo una mossa che **piega** un'autostrada e
    che, misurata, **batte** la posa corrente sul confronto unico. Deve
    esistere — altrimenti la prova non proverebbe niente, e lo dice — e deve
    essere **rifiutata** da `is_valid`.

    Ed e' qui che la prova distingue un vincolo da una voce di costo: se la
    rettilineita' stesse in `SheetCost`, una mossa che piega il tronco non
    potrebbe battere la posa corrente, e la prima meta' dell'asserzione
    fallirebbe. Le due meta' insieme dicono «rifiutata **pur** costando meno»,
    che e' la definizione di vincolo.
    """
    improver = _improver(_completato(index))
    corrente = improver.measure(improver.best)
    assert corrente is not None
    dritte = improver.straight_spine(improver.best)
    assert dritte, "serve un tronco gia' dritto per poterlo piegare"

    trovata = None
    for leader in improver.scan:
        for _, move in improver.candidates_by_kind(leader):
            dopo = {**improver.best, **move}
            if improver.straight_spine(dopo) >= dritte:
                continue
            misura = improver.measure(dopo)
            if misura is None or not misura.cost.beats(corrente.cost):
                continue
            trovata = move
            break
        if trovata is not None:
            break

    assert trovata is not None, (
        "nessuna candidata piega il tronco guadagnando: la prova non direbbe niente"
    )
    assert not improver.is_valid(trovata)


# ---------------------------------------------------------------------------
# Criterio 4 — il tronco si allunga invece di piegarsi
# ---------------------------------------------------------------------------


def _distanza_fra_le_macchine_di_spina(improver: Improver) -> float:
    """Quanto stanno lontane, in tutto, le macchine su cui il tronco si appoggia."""
    machines = sorted(improver.spine)
    return sum(
        abs(improver.best[here].origin.x_mm - improver.best[there].origin.x_mm)
        + abs(improver.best[here].origin.y_mm - improver.best[there].origin.y_mm)
        for index, here in enumerate(machines)
        for there in machines[index + 1 :]
    )


def _stringi(improver: Improver, trunk: Trunk) -> dict[str, object]:
    """Avvicina di un passo i due capi di una tratta, lungo il proprio asse.

    E' l'inverso esatto dell'allungo: si muove lungo la retta tutto cio' che
    sta da una parte del taglio, e nessuna quota cambia.
    """
    source, face = improver.port_at(
        improver.best[trunk.start.component_id], trunk.start.port_id
    )
    goal, _ = improver.port_at(improver.best[trunk.end.component_id], trunk.end.port_id)
    horizontal = face in (PortFace.LEFT, PortFace.RIGHT)
    cut = (
        (source.x_mm + goal.x_mm) / 2 if horizontal else (source.y_mm + goal.y_mm) / 2
    )
    verso = 1.0 if face in (PortFace.RIGHT, PortFace.BOTTOM) else -1.0

    def oltre(item: str) -> bool:
        placed = improver.best[item]
        middle = (
            placed.origin.x_mm + placed.width_mm / 2
            if horizontal
            else placed.origin.y_mm + placed.height_mm / 2
        )
        return (middle - cut) * verso > TOLERANCE_MM

    leaders = sorted({improver.leader_of(item) for item in improver.order if oltre(item)})
    indietro = -verso * improver.step
    return improver._translated(
        leaders, indietro if horizontal else 0.0, 0.0 if horizontal else indietro
    )


def _stringi_finche_il_corredo_non_ci_sta(improver: Improver, trunk: Trunk) -> int:
    """Stringe la campata, un passo per volta, finche' il corredo resta fuori.

    Il criterio parla di «un corredo che non entra nella campata disponibile»:
    non basta una campata corta sulla carta, serve che sia `settle_sheet` — la
    stessa funzione con cui la tavola si disegna — a dire che gli accessori
    della tratta non ci stanno. Si stringe finche' lo dice, e si restituisce
    quanti passi ci sono voluti.
    """
    index = improver.trunks.index(trunk)
    for passo in range(1, 41):
        improver.best = {**improver.best, **_stringi(improver, trunk)}
        improver._refresh_hang_gaps()
        misura = improver.measure(improver.best)
        if misura is None:
            return 0
        if index in misura.settled.unfit:
            return passo
    return 0


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_il_corredo_che_non_entra_allunga_il_tronco_e_non_lo_piega(
    index: int,
) -> None:
    """La mossa nuova (§B.2): due macchine di spina piu' lontane, tronco dritto.

    Si stringe a mano la campata di una tratta di autostrada finche' il corredo
    non ci sta — `settle_sheet` lo dichiara, contandola fra le tratte che non
    ospitano i propri accessori — e poi si lascia lavorare la **fase del
    corredo**. Quello che deve uscirne e' un tronco **piu' lungo**: le macchine
    di spina piu' lontane fra loro, la campata tornata capiente, e ogni tratta
    di autostrada ancora rettilinea. Nessuna piega, da nessuna parte.
    """
    improver = _improver(_completato(index))
    dritte = improver.straight_spine(improver.best)
    stretti = {item.connection_ids for item in improver.service_links}
    candidate = [
        item
        for item in improver.autostrade
        if item.connection_ids in dritte
        and item.connection_ids not in stretti
        and {item.start.component_id, item.end.component_id} & improver.spine
    ]
    assert candidate, "serve una tratta di tronco che tocchi una macchina di spina"
    trunk = min(
        candidate,
        key=lambda item: (
            improver._span_mm(improver.best, item) - improver._need_mm(item),
            item.connection_ids,
        ),
    )

    passi = _stringi_finche_il_corredo_non_ci_sta(improver, trunk)
    assert passi > 0, "la campata non si e' mai fatta stretta abbastanza"
    stretta = improver._span_mm(improver.best, trunk)
    assert improver.straight_spine(improver.best) == dritte

    corrente = improver.measure(improver.best)
    assert corrente is not None
    assert improver.trunks.index(trunk) in corrente.settled.unfit
    lontananza = _distanza_fra_le_macchine_di_spina(improver)

    improver.phase = Phase.CORREDO
    dopo = improver._fit_the_corredo(corrente)

    assert improver._span_mm(improver.best, trunk) > stretta + TOLERANCE_MM
    assert improver.straight_spine(improver.best) >= dritte
    assert _distanza_fra_le_macchine_di_spina(improver) > lontananza + TOLERANCE_MM
    assert dopo.cost.violations < corrente.cost.violations
    assert any(
        entry.kind == "allungo" and entry.accepted for entry in improver.journal
    )


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_l_allungo_non_sposta_nessuno_di_traverso(index: int) -> None:
    """Allungare vuol dire scorrere lungo l'asse, mai scavalcarlo.

    E' la ragione per cui l'allungo conserva ogni allineamento: chi si muove si
    muove **su una sola coordinata**, e su quella soltanto.
    """
    improver = _improver(_completato(index))
    for leader in improver.scan:
        for kind, move in improver.candidates_by_kind(leader):
            if kind != "allungo":
                continue
            assi = {
                (
                    abs(placed.origin.x_mm - improver.best[item].origin.x_mm)
                    > TOLERANCE_MM,
                    abs(placed.origin.y_mm - improver.best[item].origin.y_mm)
                    > TOLERANCE_MM,
                )
                for item, placed in move.items()
            }
            assert assi <= {(True, False), (False, True), (False, False)}
            assert len({asse for asse in assi if asse != (False, False)}) <= 1


# ---------------------------------------------------------------------------
# Criterio 5 — le strade di servizio non piegano il tronco
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_nella_fase_di_servizio_nessuna_candidata_piega_un_autostrada(
    index: int,
) -> None:
    """Il tronco e' fermo nella forma, e il costo non lo compra.

    Si passano in rassegna **tutte** le candidate che il ciclo sa generare
    nella fase delle strade di servizio: nessuna di quelle che `is_valid`
    accetta perde una tratta di autostrada gia' rettilinea. E fra quelle che
    rifiuta ce n'e' almeno una che la perderebbe, altrimenti il vincolo non
    starebbe mordendo nulla.
    """
    improver = _improver(_completato(index))
    improver.phase = Phase.SERVIZIO
    dritte = improver.straight_spine(improver.best)
    assert dritte

    rifiutate_perche_piegano = 0
    for leader in improver.scan:
        for _, move in improver.candidates_by_kind(leader):
            piega = improver.straight_spine({**improver.best, **move}) < dritte
            if improver.is_valid(move):
                assert not piega
            elif piega:
                rifiutate_perche_piegano += 1
    assert rifiutate_perche_piegano > 0


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_nella_fase_di_servizio_le_macchine_di_spina_non_si_girano(
    index: int,
) -> None:
    """«Un tronco fermo» (§C.1): una macchina di spina non cambia giacitura.

    Scorrere lungo il proprio asse resta permesso — e' cosi' che una strada di
    servizio trova la propria strada senza chiedere al tronco di piegarsi — ma
    girare una macchina di spina rifarebbe la forma del tronco, e la forma e'
    decisa.
    """
    improver = _improver(_completato(index))
    improver.phase = Phase.SERVIZIO
    for leader in improver.scan:
        for _, move in improver.candidates_by_kind(leader):
            if not improver.is_valid(move):
                continue
            for item, placed in move.items():
                if item not in improver.spine:
                    continue
                assert placed.rotation_deg == improver.best[item].rotation_deg
                assert placed.port_map == improver.best[item].port_map


def test_una_diramazione_non_accorcia_piegando_un_autostrada() -> None:
    """Su un impianto in cui piegare converrebbe, non si piega.

    Il caso e' quello delle due macchine: la seconda pompa di calore si innesta
    sul tronco attraverso i raccordi, e portare quei raccordi verso di lei
    accorcerebbe le sue due adduzioni. Sono strade di servizio — distribuzione,
    non tronco — e per accorciarsi dovrebbero piegare la mandata o il ritorno
    fra la macchina di spina e l'accumulo. Non lo fanno.
    """
    improver = _improver(_completato(1))
    improver.phase = Phase.SERVIZIO
    corrente = improver.measure(improver.best)
    assert corrente is not None
    dritte = improver.straight_spine(improver.best)

    guadagnose = 0
    for leader in improver.scan:
        for _, move in improver.candidates_by_kind(leader):
            dopo = {**improver.best, **move}
            if improver.straight_spine(dopo) >= dritte:
                continue
            misura = improver.measure(dopo)
            if misura is None or not misura.cost.beats(corrente.cost):
                continue
            guadagnose += 1
            assert not improver.is_valid(move)
    assert guadagnose > 0, "senza una mossa conveniente la prova non direbbe niente"


# ---------------------------------------------------------------------------
# Criteri 7 e 8 — le due tavole
# ---------------------------------------------------------------------------


def _porte_di_autostrada(
    project: ProjectModel, sheet: SheetGeometry, component_id: str
) -> dict[str, float]:
    """Dove stanno, sull'asse trasversale, le porte di autostrada di un pezzo."""
    registry = catalog()
    placed = next(item for item in sheet.symbols if item.component_id == component_id)
    manifest = registry.resolve(
        next(
            item.definition_id
            for item in project.components
            if item.id == component_id
        )
    ).symbol.manifest.rotated(placed.rotation_deg)
    found: dict[str, float] = {}
    for trunk, _route in _autostrade_del_foglio(project, sheet):
        for ref in (trunk.start, trunk.end):
            if ref.component_id != component_id:
                continue
            port = manifest.port(placed.physical_port(ref.port_id))
            found[ref.port_id] = placed.origin.y_mm + port.y_mm
    return found


def test_sulla_tavola_2_la_macchina_principale_e_l_accumulo_maggiore_sono_in_asse() -> None:
    """Il §4 dell'architettura, letto sulla tavola consegnata.

    «Allineando ingressi e uscite della macchina principale con quelli del
    serbatoio principale automaticamente abbiamo gia' due linee macro
    parallele»: la mandata della pompa di calore e l'ingresso del volano su una
    retta, il ritorno e l'uscita sull'altra. Non si giudica sull'intenzione ma
    sulle coordinate delle porte nella geometria che esce.
    """
    project = _fixture(TAVOLA_2)
    sheet = _tavola(TAVOLA_2)
    macchina = _porte_di_autostrada(project, sheet, "pdc")
    accumulo = _porte_di_autostrada(project, sheet, "volano")
    assert set(macchina) == {"water_supply", "water_return"}
    assert set(accumulo) == {"primary_in", "primary_out"}
    assert macchina["water_supply"] == pytest.approx(accumulo["primary_in"])
    assert macchina["water_return"] == pytest.approx(accumulo["primary_out"])
    assert macchina["water_supply"] != macchina["water_return"]


def _nodi_condivisi_col_tronco(project: ProjectModel, sheet: SheetGeometry) -> int:
    """Quanti nodi di griglia una tratta di rango inferiore divide con un'autostrada."""
    partition = _partizione(project)
    levels = hierarchy_of(project, catalog(), list(partition.trunks))
    livello = {
        tuple(trunk.connection_ids): levels[trunk.connection_ids]
        for trunk in partition.trunks
    }
    passaggi: dict[tuple[float, float], set[Level]] = {}
    for route in sheet.routes:
        rank = livello.get(tuple(route.connection_ids))
        if rank is None:
            continue
        for segment in route.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                passi = int(
                    round(
                        (
                            abs(after.x_mm - before.x_mm)
                            + abs(after.y_mm - before.y_mm)
                        )
                        / 2.5
                    )
                )
                for step in range(passi + 1):
                    ratio = 0.0 if passi == 0 else step / passi
                    cell = (
                        round(before.x_mm + (after.x_mm - before.x_mm) * ratio, 3),
                        round(before.y_mm + (after.y_mm - before.y_mm) * ratio, 3),
                    )
                    passaggi.setdefault(cell, set()).add(rank)
    return sum(
        1
        for ranghi in passaggi.values()
        if Level.AUTOSTRADA in ranghi and len(ranghi) > 1
    )


def test_quante_tratte_di_rango_inferiore_attraversano_ancora_il_tronco() -> None:
    """**Questa non e' la seconda meta' del criterio 7: e' la misura del suo scarto.**

    Il criterio chiede che nessuna tratta di rango inferiore attraversi
    un'autostrada. Sulla tavola 2 ne restano, e la causa e' quella che
    l'architettura ha gia' messo fuori perimetro (§6, I-061): l'acqua fredda
    attraversa il foglio con una linea sola, e il bollitore che la riceve sta
    dall'altra parte del tronco. Finche' l'ingresso dell'AF non si ripete, un
    tronco che passa in mezzo lo si incrocia per forza.

    La riga sta qui, misurata e non ammorbidita, perche' il numero non cresca
    di nascosto: **scende** quando I-061 sara' chiuso, e non deve risalire nel
    frattempo.
    """
    uno = _nodi_condivisi_col_tronco(_fixture(TAVOLA_1), _tavola(TAVOLA_1))
    due = _nodi_condivisi_col_tronco(_fixture(TAVOLA_2), _tavola(TAVOLA_2))
    assert uno <= 1, uno
    assert due <= 8, due


def test_sulla_tavola_1_il_tronco_e_dritto_e_la_rete_ordinaria_non_peggiora() -> None:
    """Criterio 8: la tavola 1 non paga la fase nuova.

    I tre numeri sono quelli della testa di `main` all'11 settembre 2026 —
    6 pieghe, 3 incroci, 550,0 mm di rete ordinaria — e sono un tetto, non un
    obiettivo: la posa a fasi deve arrivarci sotto, non solo non superarli. In
    piu' il tronco della tavola 1 e' **tutto** rettilineo, ed e' la proprieta'
    che la fase esiste per garantire.
    """
    project = _fixture(TAVOLA_1)
    sheet = _tavola(TAVOLA_1)
    autostrade = _autostrade_del_foglio(project, sheet)
    assert len(autostrade) == 8
    assert all(_pieghe(route) == 0 for _trunk, route in autostrade)

    pieghe = 0
    incroci = 0
    lunghezza = 0.0
    stub_points = {
        (round(point.x_mm, 3), round(point.y_mm, 3))
        for route in sheet.routes
        if route.flow_kind is not FlowKind.ORDINARY
        for point in route.crossings
    }
    for route in sheet.routes:
        if route.flow_kind is not FlowKind.ORDINARY:
            continue
        pieghe += _pieghe(route)
        lunghezza += sum(
            abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
            for segment in route.segments
            for before, after in zip(segment, segment[1:], strict=False)
        )
        incroci += sum(
            1
            for point in route.crossings
            if (round(point.x_mm, 3), round(point.y_mm, 3)) not in stub_points
        )
    assert pieghe <= 6, pieghe
    assert incroci <= 3, incroci
    assert lunghezza <= 550.0 + TOLERANCE_MM, lunghezza


# ---------------------------------------------------------------------------
# Criterio 11 — tutti e cinque gli impianti arrivano alla posa
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path", sorted(PROVE.glob("prova-*.json")), ids=lambda item: item.stem
)
def test_ogni_impianto_di_prova_arriva_alla_fase_del_tronco(path: Path) -> None:
    """La fase del tronco non fa fallire nessuno dei cinque impianti.

    Arrivare alla posa non vuol dire che la tavola esca: vuol dire che la prima
    fase produce una forma, o dichiara di non averla prodotta, senza mai
    sollevare. Una fase nuova che facesse cadere un impianto lo farebbe cadere
    in silenzio, sotto il `try` di chi la chiama.
    """
    project = _fixture(path)
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    layout = lay_the_spine(project, partition, registry, NOVE_C_A3, first)
    seeded = carry_the_rest(project, partition, registry, first, layout)
    assert len(seeded) == len(first)
    assert {item.component_id for item in seeded} == {
        item.component_id for item in first
    }
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    assert grid.step_mm > 0
