"""Le prove di DRAW-007, blocco B: il costo pesa la gerarchia.

Il difetto che chiudono, nelle parole del PO:

    «Le tubazioni che vanno alle macchine principali sono l'autostrada, e su
    quelle i costi dovrebbero essere ancora maggiori.»

Fino a DRAW-006-R1 `SheetCost` contava pieghe, incroci e millimetri **allo
stesso peso ovunque**. Con quel conto il ciclo di miglioramento respingeva un
allineamento che costava tre pieghe di contorno, e lo faceva *correttamente*:
stava minimizzando cio' che gli era stato chiesto. Il criterio sbagliato era il
costo, non il ciclo.

La prova che conta e' **negativa**: la stessa piega, messa una volta sul tronco
e una volta su uno stacco, deve produrre due costi diversi, e il piu' basso
dev'essere quello con la piega sullo stacco. Rendendo i pesi uguali la
differenza sparisce — ed e' il modo in cui questa prova dimostra di misurare i
pesi e non qualcos'altro.
"""

from datetime import date
from pathlib import Path
from unittest.mock import patch

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import Point
from disegnatore_mep.layout.hierarchy import Level, weight_of
from disegnatore_mep.layout.improve import Improver, SheetCost
from disegnatore_mep.layout.inline import SettledSheet
from disegnatore_mep.layout.partition import partition_project
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
from disegnatore_mep.model.types import PlantRegime

ROOT = Path(__file__).resolve().parents[2]
HEATING = "heating_water"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def _pipe(
    identifier: str, network: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=identifier,
        network_id=network,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def macchina_accumulo_e_uno_stacco() -> ProjectModel:
    """La forma minima che porta tutt'e due i livelli che servono qui: un
    tronco fra due macchine di spina, e uno stacco cieco che non porta a
    nessuna macchina."""
    components = [
        ("nord", "heat-pump-air-water"),
        ("volano", "buffer-four-port"),
        ("presa", "tee-branch"),
        ("manometro", "pressure-gauge"),
    ]
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-costo",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 11),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id="primo", name="primo", domain="hydronic", medium=HEATING)
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=[
            _pipe("p1", "primo", ("nord", "water_supply"), ("volano", "primary_in")),
            _pipe("p2", "primo", ("volano", "primary_out"), ("presa", "a")),
            _pipe("p3", "primo", ("presa", "b"), ("nord", "water_return")),
            _pipe("st", "primo", ("presa", "branch"), ("manometro", "a")),
        ],
        subsystems=[
            SubsystemModel(
                id="tutto",
                name="tutto",
                component_ids=[item for item, _ in components],
                network_ids=["primo"],
            )
        ],
    )


def _improver(project: ProjectModel) -> Improver:
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = partition_project(project, build_trunks(project, inline))[0]
    placed = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    return Improver(project, partition, registry, NOVE_C_A3, placed, inline)


def _con_una_piega_in_piu(settled: SettledSheet, index: int) -> SettledSheet:
    """La stessa tavola con **una piega in piu'** su una tratta sola.

    Il punto aggiunto sta sulla stessa retta dei due che lo circondano: non
    allunga il tubo di un millimetro e non puo' far tornare indietro nessuna
    tratta. Per il conto del ciclo — pieghe di una spezzata, cioe' punti meno
    due — e' pero' una piega, ed e' esattamente cio' che questa prova vuole
    isolare: il **peso**, separato da ogni altro effetto geometrico.
    """
    routes = list(settled.routes)
    route = routes[index]
    segments = [list(segment) for segment in route.segments]
    first = next(item for item in segments if len(item) >= 2)
    before, after = first[0], first[1]
    first.insert(
        1,
        Point(
            x_mm=(before.x_mm + after.x_mm) / 2,
            y_mm=(before.y_mm + after.y_mm) / 2,
        ),
    )
    routes[index] = route.model_copy(update={"segments": segments})
    return settled._replace(routes=routes)


def _due_costi() -> tuple[SheetCost, SheetCost]:
    """Il costo della stessa piega messa sul tronco, e messo sullo stacco."""
    project = macchina_accumulo_e_uno_stacco()
    improver = _improver(project)
    measured = improver.measure(improver.best)
    assert measured is not None, "la posa iniziale non si instrada"
    sul_tronco = next(
        index
        for index, trunk in enumerate(improver.trunks)
        if improver.hierarchy[trunk.connection_ids] is Level.AUTOSTRADA
    )
    sullo_stacco = next(
        index
        for index, trunk in enumerate(improver.trunks)
        if improver.hierarchy[trunk.connection_ids] is Level.SERVIZIO
    )
    return (
        improver.cost_of(improver.best, _con_una_piega_in_piu(measured.settled, sul_tronco)),
        improver.cost_of(
            improver.best, _con_una_piega_in_piu(measured.settled, sullo_stacco)
        ),
    )


# ---------------------------------------------------------------------------
# B.1 — la scala dei pesi, e il numero che la fissa
# ---------------------------------------------------------------------------


def test_i_pesi_sono_ordinati_come_i_livelli() -> None:
    assert (
        weight_of(Level.AUTOSTRADA)
        > weight_of(Level.DISTRIBUZIONE)
        > weight_of(Level.SERVIZIO)
    )


def test_una_piega_sul_tronco_costa_piu_di_dieci_pieghe_di_servizio() -> None:
    """Il numero e' del PO: «si accettano volentieri dieci pieghe in piu' sulle
    strade secondarie per tenere pulite le due macro-linee». La prova pretende
    che la scala dica quella frase, non un'altra."""
    assert weight_of(Level.AUTOSTRADA) > 10 * weight_of(Level.SERVIZIO)


# ---------------------------------------------------------------------------
# B, criterio 3 — la prova negativa
# ---------------------------------------------------------------------------


def test_la_stessa_piega_costa_meno_su_uno_stacco_che_sul_tronco() -> None:
    """Criterio 3, il verso positivo: fra due tavole che differiscono per la
    sola posizione di una piega, il ciclo tiene quella con la piega fuori dal
    tronco."""
    sul_tronco, sullo_stacco = _due_costi()
    assert sullo_stacco.beats(sul_tronco), (sullo_stacco, sul_tronco)
    assert not sul_tronco.beats(sullo_stacco)


def test_con_i_pesi_uguali_la_differenza_sparisce() -> None:
    """Criterio 3, la mutazione negativa: resi uguali i pesi, le due tavole
    diventano indistinguibili e il ciclo non ha piu' ragione di preferire l'una
    all'altra. E' il comportamento di DRAW-006-R1, ed e' il difetto."""
    piatti = {level: 1 for level in Level}
    with patch.dict("disegnatore_mep.layout.hierarchy._WEIGHT", piatti, clear=True):
        sul_tronco, sullo_stacco = _due_costi()
    assert sul_tronco.key() == sullo_stacco.key(), (sul_tronco, sullo_stacco)
