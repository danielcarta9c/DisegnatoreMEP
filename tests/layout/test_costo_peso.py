"""La posa governata dal costo delle tubazioni (DRAW-002, I-021, D-078, D-080).

Il PO: «bisogna spostare le macchine perche' spostare le macchine costa zero;
invece incroci, curve e lunghezze costano». Il PM ne ha fatto una specifica:
un solo confronto lessicografico della tavola intera, nessuna distensione che
compri riempimento pagando in tubo, candidati ricavati dalla topologia.

Queste prove sono **generali**: gli impianti sono costruiti qui dentro, con il
catalogo di prova, e nessuna coordinata o identificativo dell'impianto 1 entra
nel motore ne' nelle attese. Sono scritte prima del codice applicativo, come il
pacchetto chiede.
"""
# categoria: difendeva il solutore — SheetCost e improve_sheet: l'ordine lessicografico delle voci e il ciclo di miglioramento (DRAW-002, D-078, D-080)

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import improve
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    drawing_fingerprint,
)
from disegnatore_mep.layout.improve import Improver, SheetCost, improve_sheet
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
FIXTURE = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"

STEP_MM = NOVE_C_A3.standard.grid_mm


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _plant(
    components: list[tuple[str, str]],
    connections: list[tuple[str, str, str, str, str]],
    subsystems: list[tuple[str, list[str]]],
) -> ProjectModel:
    """Un impianto minimo: (id, definizione), (id, da, porta, a, porta), gruppi."""
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-costo-peso",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date="2026-09-03",
        ),
        subsystems=[
            SubsystemModel(id=name, name=name, component_ids=members, network_ids=["rete"])
            for name, members in subsystems
        ],
        networks=[
            NetworkModel(id="rete", name="Rete", domain="hydronic", medium="heating_water")
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=[
            ConnectionModel(
                id=item,
                network_id="rete",
                endpoint_a=PortRef(component_id=source, port_id=source_port),
                endpoint_b=PortRef(component_id=target, port_id=target_port),
            )
            for item, source, source_port, target, target_port in connections
        ],
    )


def _prepared(project: ProjectModel) -> tuple[SheetPartition, frozenset[str]]:
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return partition, inline


def _improver(project: ProjectModel, placed: list[PlacedSymbol]) -> Improver:
    partition, inline = _prepared(project)
    return Improver(project, partition, catalog(), NOVE_C_A3, placed, inline)


def _shifted(item: PlacedSymbol, dx_mm: float, dy_mm: float = 0.0) -> PlacedSymbol:
    return item.model_copy(
        update={"origin": Point(x_mm=item.origin.x_mm + dx_mm, y_mm=item.origin.y_mm + dy_mm)}
    )


# ---------------------------------------------------------------------------
# Gli impianti di prova, costruiti qui: nessun identificativo dell'impianto 1
# ---------------------------------------------------------------------------


def generatore_accumulo_terminale() -> ProjectModel:
    """Una macchina, un accumulo e un terminale in fila, con una valvola."""
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("valvola", "valve-isolation"),
            ("serbatoio", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "valvola", "a"),
            ("c2", "valvola", "b", "serbatoio", "a"),
            ("c3", "serbatoio", "b", "terminale", "in"),
            ("c4", "terminale", "out", "macchina", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina", "valvola"]),
            ("accumulo", ["serbatoio"]),
            ("utenza", ["terminale"]),
        ],
    )


def due_macchine_in_parallelo() -> ProjectModel:
    """Due macchine uguali sugli stessi raccordi: una pila, per costruzione."""
    return _plant(
        components=[
            ("prima", "heat-pump-air-water"),
            ("seconda", "heat-pump-air-water"),
            ("confluenza", "tee-junction"),
            ("serbatoio", "buffer-two-port"),
            ("ripartizione", "tee-split"),
        ],
        connections=[
            ("c1", "prima", "water_supply", "confluenza", "a"),
            ("c2", "seconda", "water_supply", "confluenza", "c"),
            ("c3", "confluenza", "b", "serbatoio", "a"),
            ("c4", "serbatoio", "b", "ripartizione", "a"),
            ("c5", "ripartizione", "b", "prima", "water_return"),
            ("c6", "ripartizione", "c", "seconda", "water_return"),
        ],
        subsystems=[
            ("generazione", ["prima", "seconda", "confluenza", "ripartizione"]),
            ("accumulo", ["serbatoio"]),
        ],
    )


def macchina_e_terminale() -> ProjectModel:
    """Una macchina e un terminale che si parlano direttamente."""
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "terminale", "in"),
            ("c2", "terminale", "out", "macchina", "water_return"),
        ],
        subsystems=[("generazione", ["macchina"]), ("utenza", ["terminale"])],
    )


def _posa(project: ProjectModel) -> list[PlacedSymbol]:
    partition, inline = _prepared(project)
    return place_sheet(project, partition, catalog(), NOVE_C_A3, inline)


# ---------------------------------------------------------------------------
# 1. Un solo confronto esplicito, lessicografico
# ---------------------------------------------------------------------------


def _cost(**overrides: float) -> SheetCost:
    base = dict(
        violations=0,
        turnback_runs=0,
        turnback_mm=0.0,
        long_runs=0,
        bends=4,
        crossings=1,
        # D-143: il margine di rispetto entra nella chiave fra gli
        # attraversamenti e il riempimento (DRAW-013 §B).
        margin_gap=0.0,
        fill=0.55,
        coverage=0.80,
        imbalance=2.0,
        length_mm=200.0,
    )
    base.update(overrides)
    return SheetCost(**base)  # type: ignore[arg-type]


def test_l_ordine_del_costo_e_quello_del_pacchetto() -> None:
    """Le voci di costo, nell'ordine dichiarato, e nessuna che pesi le altre.

    **Riscritta il 17 settembre 2026 da `DRAW-012` §D.** Fino a `DRAW-011` le
    voci in fila erano sette e la settima era `length_mm`; il PO l'ha tolta
    (**D-139**): «i mm non sono un vero costo da misurare, lo e' piu' avere un
    buon riempimento, ne' troppo poco ne' troppo». Restano i costi veri — le
    curve e, in secondo luogo, gli attraversamenti — e al posto della lunghezza
    entra il **riempimento dentro la propria finestra**. La lunghezza resta
    nella tupla, e si riporta: come misura, non come giudizio.
    """
    assert SheetCost._fields[:6] == (
        "violations",
        "turnback_runs",
        "turnback_mm",
        "long_runs",
        "bends",
        "crossings",
    )
    # Ogni voce comanda su tutte quelle che la seguono: una geometria peggiore
    # di uno su una voce non si compra con nessun guadagno su quelle dopo.
    worse_later = dict(
        turnback_runs=0,
        turnback_mm=0.0,
        long_runs=0,
        bends=0,
        crossings=0,
        fill=0.55,
        coverage=1.0,
        imbalance=1.0,
    )
    for index, field in enumerate(SheetCost._fields[:6]):
        better = _cost()
        # La stessa tavola, migliore su tutto cio' che viene dopo `field`...
        rival_values = {
            name: value
            for name, value in worse_later.items()
            if SheetCost._fields.index(name) > index
        }
        rival = _cost(**rival_values)
        # ...ma peggiore di uno su `field`.
        rival = rival._replace(**{field: getattr(better, field) + 1})
        assert better.beats(rival), field
        assert not rival.beats(better), field


def test_nessun_riempimento_compra_pieghe_incroci_o_backtracking() -> None:
    """Il riempimento e' una **finestra**, non una ragione per pagare (D-139).

    **Riscritta il 17 settembre 2026 da `DRAW-012` §D**: la lunghezza esce
    dall'elenco di cio' che il riempimento non puo' comprare, perche' non e'
    piu' un costo. Tutto il resto resta com'era, ed e' il punto: una tavola con
    una piega in piu' non si giustifica con un foglio meglio riempito.
    """
    compact = _cost(fill=0.20, coverage=0.4, imbalance=5.0)
    for field in ("crossings", "bends", "long_runs", "turnback_mm", "turnback_runs"):
        spread = _cost(fill=0.55, coverage=1.0, imbalance=1.0)
        spread = spread._replace(**{field: getattr(compact, field) + 1})
        assert compact.beats(spread), field
    # A geometria uguale sulle sei voci decide il riempimento, e decide **dentro
    # la finestra**: si perde a stare sotto come a stare sopra.
    assert _cost(fill=0.55).beats(_cost(fill=0.30))
    assert _cost(fill=0.55).beats(_cost(fill=0.85))
    assert _cost(imbalance=1.5).beats(_cost(imbalance=2.0))
    assert not _cost().beats(_cost())
    # E la distensione come obiettivo autonomo non esiste piu' (§2): una
    # finestra non e' un traguardo, ed e' la ragione per cui D-139 puo'
    # modificare D-134 senza contraddirla.
    for name in ("FILL_TARGET_RATIO", "SPREAD_STEPS", "MAX_SPREAD_TRIALS", "_spread_out"):
        assert not hasattr(improve, name), name


def test_il_limite_di_ricerca_e_dichiarato() -> None:
    """Il ciclo e' limitato, e il limite e' un numero che si legge (§3)."""
    assert isinstance(improve.MAX_TRIAL_ROUTINGS, int)
    assert improve.MAX_TRIAL_ROUTINGS > 0


# ---------------------------------------------------------------------------
# 2. Una posa compatta batte una posa equidistante
# ---------------------------------------------------------------------------


def test_allontanare_le_macchine_non_costa_piu_tubo() -> None:
    """Stesse macchine, stessa topologia, solo piu' tubo: **e' indifferente**.

    **Riscritta il 17 settembre 2026 da `DRAW-012` §D.** Fino a `DRAW-011` la
    prova si chiamava «una posa compatta batte una posa equidistante» e chiedeva
    esattamente cio' che il PO ha tolto: che chi allunga il tubo perda. Il PO
    (**D-139**): «continuo a pensare che i mm non siano un vero parametro. Anche
    perche' un disegno ben fatto e' anche comodo e ho spazio per mettere i tag».

    Cio' che resta vero — ed e' il punto — e' che allontanare le macchine non
    deve **peggiorare** niente d'altro: le due pose differiscono per il solo
    tubo, e sulle voci vere — pieghe e attraversamenti — sono pari. Chi vince
    lo decide il riempimento, che e' un'altra prova.
    """
    project = generatore_accumulo_terminale()
    compact = _posa(project)
    spread = [
        _shifted(item, {"serbatoio": 40.0, "terminale": 80.0}.get(item.component_id, 0.0))
        for item in compact
    ]
    improver = _improver(project, compact)
    compact_cost = improver.measure(compact)
    spread_cost = improver.measure(spread)
    assert compact_cost is not None and spread_cost is not None
    # La posa larga e' piu' lunga — la misura c'e' ancora e si legge...
    assert compact_cost.cost.length_mm < spread_cost.cost.length_mm
    # ...ma non decide: sulle voci di costo le due pose non differiscono per
    # la lunghezza, e il confronto non la guarda.
    assert compact_cost.cost.key()[:6] == spread_cost.cost.key()[:6]
    solo_la_lunghezza = compact_cost.cost._replace(
        length_mm=spread_cost.cost.length_mm
    )
    assert not solo_la_lunghezza.beats(compact_cost.cost)
    assert not compact_cost.cost.beats(solo_la_lunghezza)


def test_il_miglioratore_non_peggiora_mai_il_costo_della_posa_di_partenza() -> None:
    """Monotono: ogni mossa accettata batte la precedente sul confronto unico."""
    for project in (generatore_accumulo_terminale(), due_macchine_in_parallelo()):
        first = _posa(project)
        improver = _improver(project, first)
        before = improver.measure(first)
        after = improver.measure(
            improve_sheet(
                project, improver.partition, catalog(), NOVE_C_A3, first, improver.inline_ids
            )
        )
        assert before is not None and after is not None
        assert not before.cost.beats(after.cost)


# ---------------------------------------------------------------------------
# 3. I candidati vengono dalla topologia
# ---------------------------------------------------------------------------


def test_una_pila_collegata_puo_traslare_come_gruppo() -> None:
    """Due macchine impilate si spostano insieme, senza sfilarne una (§3)."""
    project = due_macchine_in_parallelo()
    # La posa iniziale appoggia la pila al margine sinistro: la si sposta di
    # quattro centimetri perche' abbia spazio da tutte e due le parti.
    placed = [_shifted(item, 40.0) for item in _posa(project)]
    where = {item.component_id: item for item in placed}
    assert where["prima"].origin.x_mm == where["seconda"].origin.x_mm, "la posa le impila"
    improver = _improver(project, placed)
    together = [
        move
        for move in improver.candidates("prima")
        if "prima" in move
        and "seconda" in move
        and move["prima"].origin.x_mm != where["prima"].origin.x_mm
        and move["prima"].origin.x_mm - where["prima"].origin.x_mm
        == move["seconda"].origin.x_mm - where["seconda"].origin.x_mm
        and move["prima"].origin.y_mm == where["prima"].origin.y_mm
        and move["seconda"].origin.y_mm == where["seconda"].origin.y_mm
    ]
    assert together, "nessun candidato trasla la pila come gruppo"
    assert any(improver.is_valid(move) for move in together)
    # E nessun candidato sfila una sola delle due in orizzontale.
    for move in improver.candidates("prima"):
        if "prima" in move and move["prima"].origin.x_mm != where["prima"].origin.x_mm:
            assert "seconda" in move
            assert (
                move["seconda"].origin.x_mm - where["seconda"].origin.x_mm
                == move["prima"].origin.x_mm - where["prima"].origin.x_mm
            )


def test_i_candidati_raggiungono_l_allineamento_fra_porte_oltre_quattro_passi() -> None:
    """La quota giusta si prende in una mossa sola, anche a venti millimetri (§3).

    Le vecchie traslazioni erano di uno, due e quattro passi: un terminale a
    otto passi dalla riga della porta che lo alimenta non ci arrivava mai in una
    mossa, e in piu' mosse solo se ognuna migliorava da sola.
    """
    project = macchina_e_terminale()
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    machine, terminal = where["macchina"], where["terminale"]
    manifest = catalog().resolve("heat-pump-air-water").symbol.manifest
    feed_y = machine.origin.y_mm + manifest.port("water_supply").y_mm
    radiator = catalog().resolve("radiator").symbol.manifest.rotated(terminal.rotation_deg)
    port_y = radiator.port("in").y_mm
    # Il terminale viene portato apposta otto passi sopra la riga della porta.
    far = [
        item.model_copy(
            update={"origin": Point(x_mm=item.origin.x_mm, y_mm=feed_y - port_y - 8 * STEP_MM)}
        )
        if item.component_id == "terminale"
        else item
        for item in placed
    ]
    improver = _improver(project, far)
    aligned = [
        move
        for move in improver.candidates("terminale")
        if "terminale" in move
        and move["terminale"].rotation_deg == terminal.rotation_deg
        and move["terminale"].origin.y_mm + port_y == feed_y
    ]
    assert aligned, "nessun candidato porta la porta del terminale sulla riga della macchina"
    assert any(improver.is_valid(move) for move in aligned)


def test_i_candidati_si_avvicinano_alla_distanza_minima_che_lascia_posto_agli_accessori() -> None:
    """Chi e' lontano viene avvicinato quanto gli accessori in linea permettono (§3)."""
    project = generatore_accumulo_terminale()
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    far = [
        _shifted(item, 60.0) if item.component_id == "serbatoio" else item for item in placed
    ]
    improver = _improver(project, far)
    machine = where["macchina"]
    closer = [
        move["serbatoio"].origin.x_mm
        for move in improver.candidates("serbatoio")
        if "serbatoio" in move and improver.is_valid(move)
    ]
    assert closer
    # Almeno un candidato torna piu' vicino della posa di partenza, e nessuno
    # si posa addosso alla macchina: fra le due porte resta il rettilineo che
    # la valvola pretende.
    assert min(closer) < where["serbatoio"].origin.x_mm + 60.0
    assert min(closer) > machine.right_mm


# ---------------------------------------------------------------------------
# 4. Determinismo, e indipendenza dagli identificativi
# ---------------------------------------------------------------------------


def _renamed(project: ProjectModel) -> ProjectModel:
    """Lo stesso impianto con ogni identificativo cambiato, e l'ordine alfabetico
    rovesciato: se il motore decidesse qualcosa in base al nome, si vedrebbe."""
    names = (
        [item.id for item in project.components]
        + [item.id for item in project.connections]
        + [item.id for item in project.subsystems]
        + [item.id for item in project.networks]
    )
    ordered = sorted(names)
    mapping = {name: f"z{len(ordered) - index:03d}-{name}" for index, name in enumerate(ordered)}

    def rename(document: object) -> object:
        if isinstance(document, dict):
            out: dict[str, object] = {}
            for key, value in document.items():
                if key in _ID_KEYS and isinstance(value, str):
                    out[key] = mapping.get(value, value)
                elif key in _ID_LIST_KEYS and isinstance(value, list):
                    out[key] = [mapping.get(item, item) for item in value]
                else:
                    out[key] = rename(value)
            return out
        if isinstance(document, list):
            return [rename(item) for item in document]
        return document

    return ProjectModel.model_validate(rename(project.model_dump(mode="json")))


_ID_KEYS = frozenset({"id", "component_id", "network_id", "subsystem_id"})
_ID_LIST_KEYS = frozenset({"component_ids", "network_ids", "subsystem_ids"})


def _shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    """La geometria senza i nomi: cosa c'e' e dove, non come si chiama."""
    sheet = drawing.sheets[0]
    symbols = sorted(
        (item.symbol_id, item.rotation_deg, item.origin.x_mm, item.origin.y_mm)
        for item in sheet.symbols
    )
    routes = sorted(
        (
            route.medium,
            tuple(tuple((point.x_mm, point.y_mm) for point in segment) for segment in route.segments),
        )
        for route in sheet.routes
    )
    return (tuple(symbols), tuple(routes))


def test_due_ingressi_equivalenti_con_identificativi_diversi_danno_la_stessa_geometria() -> None:
    """Il nome di un pezzo non decide dove sta (D-093)."""
    project = load_project(FIXTURE)
    twin = _renamed(project)
    assert {item.id for item in twin.components}.isdisjoint(
        {item.id for item in project.components}
    )
    assert _shape(compose_drawing(project, catalog(), NOVE_C_A3)) == _shape(
        compose_drawing(twin, catalog(), NOVE_C_A3)
    )


def test_due_generazioni_consecutive_danno_lo_stesso_fingerprint() -> None:
    project = generatore_accumulo_terminale()
    once = drawing_fingerprint(compose_drawing(project, catalog(), NOVE_C_A3))
    twice = drawing_fingerprint(compose_drawing(project, catalog(), NOVE_C_A3))
    assert once == twice


@pytest.mark.parametrize("project", [due_macchine_in_parallelo()], ids=["pila"])
def test_la_posa_migliorata_e_sempre_la_stessa(project: ProjectModel) -> None:
    first = _posa(project)
    improver = _improver(project, first)
    once = improve_sheet(project, improver.partition, catalog(), NOVE_C_A3, list(first), improver.inline_ids)
    twice = improve_sheet(project, improver.partition, catalog(), NOVE_C_A3, list(first), improver.inline_ids)
    assert [item.model_dump() for item in once] == [item.model_dump() for item in twice]
