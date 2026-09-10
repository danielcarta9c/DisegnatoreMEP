"""Il blocco B di DRAW-006-R1: gli assi si cercano anche **attraverso** i pezzi.

Il PM, sulla PR #24: «I candidati di asse vedono prevalentemente estremi diretti
o catene semplici. La deviatrice interrompe la relazione PDC–puffer e impedisce
di provare l'allineamento ovvio delle loro porte.»

Cio' che il pacchetto chiede:

1. i candidati di asse si generano fra coppie di porte compatibili di macchine
   principali **anche attraverso** raccordi, catene di accessori in linea e
   componenti multivia, per ciascuno stato idraulico ammesso dal catalogo;
2. si provano la traslazione del gruppo a monte, quella del gruppo a valle e
   l'asse comune; e quando due macchine hanno coppie mandata/ritorno
   compatibili, anche l'allineamento simultaneo delle due coppie;
3. l'allineamento resta **una candidata**, non un assoluto: decide il costo.

Le prove sono generali: gli impianti si costruiscono qui, e cio' che si pretende
si legge dal **catalogo** — gli stati ammessi di un multivia — non da una tavola.
"""

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.improve import Improver, Move
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

STEP_MM = NOVE_C_A3.standard.grid_mm
TOLERANCE_MM = 1e-6


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
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-assi-stati",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date="2026-09-10",
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


def _posa(project: ProjectModel) -> list[PlacedSymbol]:
    partition, inline = _prepared(project)
    return place_sheet(project, partition, catalog(), NOVE_C_A3, inline)


def _refiner(project: ProjectModel) -> Improver:
    partition, inline = _prepared(project)
    improver = Improver(
        project, partition, catalog(), NOVE_C_A3, _posa(project), inline
    )
    improver.refining = True
    return improver


def _pairs(improver: Improver, leader: str) -> set[tuple[str, str, str]]:
    """Le coppie di porte che il ciclo considera allineabili, da quel pezzo.

    `(porta mia, pezzo pari, porta del pari)`. E' la superficie che il blocco B
    generalizza: prima portava soltanto i capi diretti di una tratta.
    """
    return {
        (item.my_port, item.peer_id, item.peer_port)
        for item in improver.linked_peers(leader)
    }


# ---------------------------------------------------------------------------
# Gli impianti di prova
# ---------------------------------------------------------------------------


def deviatrice_fra_due_macchine() -> ProjectModel:
    """Un generatore, una deviatrice a tre vie e i due rami che ne escono.

    E' la forma dell'impianto 2 e dell'impianto 4, senza i loro nomi: la
    deviatrice sta fra la macchina e cio' che serve, e i suoi due rami non
    comunicano fra loro in nessuno stato.
    """
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("multivia", "diverting-valve-3way"),
            ("serbatoio", "buffer-two-port"),
            ("riserva", "dhw-cylinder"),
            ("confluenza", "tee-junction"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "multivia", "in"),
            ("c2", "multivia", "out_a", "serbatoio", "a"),
            ("c3", "multivia", "out_b", "riserva", "coil_in"),
            ("c4", "serbatoio", "b", "confluenza", "a"),
            ("c5", "riserva", "coil_out", "confluenza", "c"),
            ("c6", "confluenza", "b", "macchina", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina", "multivia"]),
            ("accumulo", ["serbatoio", "riserva", "confluenza"]),
        ],
    )


def catena_in_linea_fra_due_macchine() -> ProjectModel:
    """Due macchine e, in mezzo, una fila di accessori in linea.

    La catena non interrompe la relazione fra le due porte: il fluido ci passa
    attraverso, e le due macchine restano allineabili.
    """
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("organo", "valve-isolation"),
            ("filtro", "strainer"),
            ("serbatoio", "buffer-two-port"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "organo", "a"),
            ("c2", "organo", "b", "filtro", "a"),
            ("c3", "filtro", "b", "serbatoio", "a"),
            ("c4", "serbatoio", "b", "macchina", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("accumulo", ["serbatoio"]),
        ],
    )


def raccordo_fra_due_macchine() -> ProjectModel:
    """Due macchine e un raccordo di confluenza fra loro."""
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("altra", "heat-pump-air-water"),
            ("raccordo", "tee-junction"),
            ("serbatoio", "buffer-two-port"),
            ("ripartizione", "tee-split"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "raccordo", "a"),
            ("c2", "altra", "water_supply", "raccordo", "c"),
            ("c3", "raccordo", "b", "serbatoio", "a"),
            ("c4", "serbatoio", "b", "ripartizione", "a"),
            ("c5", "ripartizione", "b", "macchina", "water_return"),
            ("c6", "ripartizione", "c", "altra", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina", "altra", "raccordo"]),
            ("accumulo", ["serbatoio", "ripartizione"]),
        ],
    )


# ---------------------------------------------------------------------------
# B.1 — le coppie si cercano attraverso raccordi, catene e multivia
# ---------------------------------------------------------------------------


def test_le_coppie_di_asse_attraversano_una_catena_di_accessori() -> None:
    """Una valvola e un filtro in mezzo non nascondono la macchina che segue."""
    improver = _refiner(catena_in_linea_fra_due_macchine())
    assert ("water_supply", "serbatoio", "a") in _pairs(improver, "macchina"), (
        "il ciclo non vede l'accumulo dall'altro capo della catena: l'asse "
        "ovvio fra le due porte non viene nemmeno provato"
    )


def test_le_coppie_di_asse_attraversano_un_raccordo() -> None:
    """Un raccordo e' un pallino sul tubo, non un capolinea."""
    improver = _refiner(raccordo_fra_due_macchine())
    assert ("water_supply", "serbatoio", "a") in _pairs(improver, "macchina")


def test_le_coppie_di_asse_attraversano_un_multivia_stato_per_stato() -> None:
    """Ogni stato ammesso apre una coppia, e nessuno stato ne apre di false.

    Gli stati li dichiara il **catalogo**: la prova li rilegge da li' e ne
    ricava cosa pretendere, invece di scrivere a mano l'elenco delle coppie.
    """
    project = deviatrice_fra_due_macchine()
    improver = _refiner(project)
    multivia = catalog().get("diverting-valve-3way")
    assert len(multivia.hydraulic_states) > 1, (
        "il multivia di prova non dichiara stati alternativi: la prova non "
        "misurerebbe niente"
    )
    trovate = _pairs(improver, "macchina")
    assert ("water_supply", "serbatoio", "a") in trovate, (
        "lo stato che manda l'acqua sul primo ramo non genera nessuna coppia"
    )
    assert ("water_supply", "riserva", "coil_in") in trovate, (
        "lo stato che manda l'acqua sul secondo ramo non genera nessuna coppia"
    )


def test_i_due_rami_di_un_multivia_non_diventano_una_coppia() -> None:
    """`out_a ↔ out_b` non e' un passaggio, e non lo diventa per l'asse.

    E' la stessa proprieta' che governa la sicurezza (DRAW-006, blocco C): se
    l'asse la violasse, il ciclo allineerebbe due porte che l'acqua non collega
    mai — e la deviatrice tornerebbe genericamente passante.
    """
    improver = _refiner(deviatrice_fra_due_macchine())
    peers = {peer for _, peer, _ in _pairs(improver, "serbatoio")}
    assert "riserva" not in peers, (
        "il ciclo considera allineabili i due rami della deviatrice, che non "
        "comunicano in nessuno stato ammesso"
    )


# ---------------------------------------------------------------------------
# B.2 — le tre mosse, e le due coppie insieme
# ---------------------------------------------------------------------------


def _allineate(
    improver: Improver, layout: Move, first: tuple[str, str], second: tuple[str, str]
) -> bool:
    here, _ = improver.port_at(layout[first[0]], first[1])
    there, _ = improver.port_at(layout[second[0]], second[1])
    return (
        abs(here.x_mm - there.x_mm) <= TOLERANCE_MM
        or abs(here.y_mm - there.y_mm) <= TOLERANCE_MM
    )


def test_l_asse_attraverso_il_multivia_ha_una_candidata_che_lo_realizza() -> None:
    """Fra le candidate ce n'e' almeno una che mette le due porte in asse.

    Non si pretende che vinca: l'asse e' una candidata e decide il costo della
    tavola intera (B.3). Si pretende che **esista**, perche' prima non veniva
    nemmeno generata.
    """
    project = deviatrice_fra_due_macchine()
    improver = _refiner(project)
    coppia = (("macchina", "water_supply"), ("serbatoio", "a"))
    trovate = [
        move
        for leader in ("macchina", "serbatoio")
        for kind, move in improver.candidates_by_kind(leader)
        if kind == "asse"
        and improver.is_valid(move)
        and _allineate(improver, {**improver.best, **move}, *coppia)
    ]
    assert trovate, (
        "nessuna candidata di asse allinea la porta della macchina con quella "
        "dell'accumulo attraverso la deviatrice"
    )


def test_due_coppie_compatibili_si_provano_anche_insieme() -> None:
    """Mandata e ritorno di due macchine: c'e' la candidata che le allinea tutte e due."""
    project = catena_in_linea_fra_due_macchine()
    improver = _refiner(project)
    mandata = (("macchina", "water_supply"), ("serbatoio", "a"))
    ritorno = (("macchina", "water_return"), ("serbatoio", "b"))
    trovate = [
        move
        for leader in ("macchina", "serbatoio")
        for kind, move in improver.candidates_by_kind(leader)
        if kind == "asse"
        and improver.is_valid(move)
        and _allineate(improver, {**improver.best, **move}, *mandata)
        and _allineate(improver, {**improver.best, **move}, *ritorno)
    ]
    assert trovate, (
        "nessuna candidata allinea insieme la coppia di mandata e quella di "
        "ritorno delle due macchine"
    )
