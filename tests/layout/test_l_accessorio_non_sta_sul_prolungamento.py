"""Un accessorio non si posa sul prolungamento del tubo da cui la sua tratta si stacca (I-217).

Sulla tavola della prova pulita C, ingrandita: il giunto antivibrante sul ritorno
dell'ultima pompa di ogni cascata stava sulla **verticale del collettore**, mentre
quello delle altre pompe sta sul loro stacco orizzontale. La tratta dell'ultima
pompa esce dall'ultimo raccordo del collettore **dalla parte opposta** a quella da
cui il collettore arriva, scende lungo la stessa verticale e solo dopo piega verso
la macchina; gli accessori si posavano sul primo rettilineo libero, cioe' sul
collettore. A chi legge la tavola a freddo il giunto sembra del collettore comune.

Nessun controllo lo misurava. La regola: se la tratta esce da un raccordo **in
prolungamento** di un altro suo attacco, e poi piega, gli accessori che non sono
la catena di una macchina saltano quel primo rettilineo, quando il resto della
tratta li contiene. Lo stesso dal capo di arrivo.
"""

# categoria: difende il disegno — I-217, la tavola d'esempio del revisore

from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol, Point, RoutedTrunk
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import place_inline_accessories
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime

ROOT = Path(__file__).resolve().parents[2]


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def _ramo(dalla_porta: str) -> ProjectModel:
    """Un raccordo che divide, e dalla porta data un giunto fino a un T con lo sfiato.

    Sul raccordo `a` e `b` stanno su facce opposte, `c` di fianco: dalla `b` si esce
    in prolungamento della `a`, dalla `c` si esce di lato.
    """

    def tubo(ident: str, a: str, b: str) -> ConnectionModel:
        (pa, porta_a), (pb, porta_b) = a.split("."), b.split(".")
        return ConnectionModel(
            id=ident,
            network_id="rit",
            endpoint_a=PortRef(component_id=pa, port_id=porta_a),
            endpoint_b=PortRef(component_id=pb, port_id=porta_b),
        )

    altra = "c" if dalla_porta == "b" else "b"
    pezzi = [
        ("divide", "tee-split"),
        ("giunto", "flexible-joint"),
        ("tee-sfiato", "tee-branch"),
        ("sfiato", "air-vent"),
        ("valvola", "valve-isolation"),
        ("pdc", "heat-pump-air-water"),
        ("altro", "fan-coil"),
        ("sorgente", "fan-coil"),
    ]
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="ramo", client="prova", project_name="prova",
            commission_code="PROVA", revision="00", issue_date=date(2026, 10, 23),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[NetworkModel(id="rit", name="rit", domain="hydronic", medium="heating_water")],
        components=[ComponentInstance(id=ident, definition_id=voce) for ident, voce in pezzi],
        connections=[
            tubo("arriva", "sorgente.out", "divide.a"),
            tubo("t1", f"divide.{dalla_porta}", "giunto.a"),
            tubo("t2", "giunto.b", "tee-sfiato.a"),
            tubo("t3", "tee-sfiato.branch", "sfiato.a"),
            tubo("t4", "tee-sfiato.b", "valvola.a"),
            tubo("t5", "valvola.b", "pdc.water_return"),
            tubo("lato", f"divide.{altra}", "altro.in"),
        ],
    )


AREA = NOVE_C_A3.drawing_rect_mm
X0, Y0 = AREA.x_mm + 150, AREA.y_mm + 50
"""L'asse del collettore e la quota del raccordo che divide."""

GIU_E_A_SINISTRA = [
    Point(x_mm=X0, y_mm=Y0 + 2.5), Point(x_mm=X0, y_mm=Y0 + 40), Point(x_mm=X0 - 60, y_mm=Y0 + 40)
]
"""Dall'attacco di sotto: giu' lungo l'asse del collettore, poi a sinistra verso la macchina."""

A_SINISTRA = [Point(x_mm=X0 - 2.5, y_mm=Y0), Point(x_mm=X0 - 60, y_mm=Y0)]
"""Dall'attacco di fianco: dritti a sinistra, come le pompe sopra l'ultima."""


def _posa(dalla_porta: str, punti: list[Point]) -> PlacedSymbol:
    project = _ramo(dalla_porta)
    registry = catalogo()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    tratta = next(item for item in trunks if "giunto" in item.inline_component_ids)
    if tratta.start.component_id != "divide":
        punti = list(reversed(punti))
    instradata = RoutedTrunk(
        network_id="rit",
        medium="heating_water",
        connection_ids=list(tratta.connection_ids),
        segments=[punti],
    )
    griglia = GridSpace(origin=AREA, standard=NOVE_C_A3.standard)
    posati, _ = place_inline_accessories(project, tratta, instradata, registry, griglia, trunks=trunks)
    return next(item for item in posati if item.component_id == "giunto")


def test_il_giunto_non_sta_sul_prolungamento_del_collettore() -> None:
    giunto = _posa("b", GIU_E_A_SINISTRA)
    assert giunto.rotation_deg % 180 == 0, (
        f"il giunto sta sulla verticale che prolunga il collettore (ruotato di {giunto.rotation_deg}°): "
        f"va sullo stacco orizzontale verso la macchina"
    )


def test_e_sta_alla_stessa_distanza_dal_collettore_dei_fratelli() -> None:
    """Una colonna di giunti uguali si legge se sono in fila: l'ultima pompa non fa eccezione."""
    ultimo = _posa("b", GIU_E_A_SINISTRA)
    fratello = _posa("c", A_SINISTRA)
    assert ultimo.origin.x_mm == fratello.origin.x_mm, (ultimo.origin.x_mm, fratello.origin.x_mm)


def test_dall_uscita_di_lato_il_primo_rettilineo_resta_buono() -> None:
    """Dall'attacco di fianco la tratta non prolunga niente: se scende, il giunto scende con lei."""
    giunto = _posa("c", [Point(x_mm=X0 - 2.5, y_mm=Y0), Point(x_mm=X0 - 2.5, y_mm=Y0 + 40),
                         Point(x_mm=X0 - 60, y_mm=Y0 + 40)])
    assert giunto.rotation_deg % 180 == 90, giunto.rotation_deg


def _rete(pezzi: list[tuple[str, str]], tubi: list[tuple[str, str]]) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="rete", client="prova", project_name="prova",
            commission_code="PROVA", revision="00", issue_date=date(2026, 10, 23),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[NetworkModel(id="rit", name="rit", domain="hydronic", medium="heating_water")],
        components=[ComponentInstance(id=ident, definition_id=voce) for ident, voce in pezzi],
        connections=[
            ConnectionModel(
                id=f"t{numero}",
                network_id="rit",
                endpoint_a=PortRef(component_id=a.split(".")[0], port_id=a.split(".")[1]),
                endpoint_b=PortRef(component_id=b.split(".")[0], port_id=b.split(".")[1]),
            )
            for numero, (a, b) in enumerate(tubi)
        ],
    )


def _posa_la_tratta_di(project: ProjectModel, pezzo: str, punti: list[Point]) -> dict[str, int]:
    """Le rotazioni degli accessori della tratta che porta `pezzo`, instradata per `punti`
    a partire dal raccordo `divide`."""
    registry = catalogo()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    tratta = next(item for item in trunks if pezzo in item.inline_component_ids)
    if tratta.start.component_id != "divide":
        punti = list(reversed(punti))
    instradata = RoutedTrunk(
        network_id="rit", medium="heating_water",
        connection_ids=list(tratta.connection_ids), segments=[punti],
    )
    griglia = GridSpace(origin=AREA, standard=NOVE_C_A3.standard)
    posati, _ = place_inline_accessories(project, tratta, instradata, registry, griglia, trunks=trunks)
    return {item.component_id: item.rotation_deg % 180 for item in posati}


def test_chi_arriva_nell_attacco_comune_tiene_il_suo_ultimo_rettilineo() -> None:
    """La tratta esce in prolungamento da un raccordo e arriva nell'ingresso di un altro, che
    divide: li' e' lei il tubo comune, e il suo ultimo rettilineo resta buono. La prima stesura
    della regola toglieva anche quello, e il giunto tornava sulla verticale."""
    project = _rete(
        [("divide", "tee-split"), ("colonna", "tee-split"), ("giunto", "flexible-joint"),
         ("sorgente", "fan-coil"), ("altro", "fan-coil"), ("primo", "fan-coil"), ("giu", "fan-coil")],
        [("sorgente.out", "divide.a"), ("divide.b", "giunto.a"), ("giunto.b", "colonna.a"),
         ("colonna.b", "primo.in"), ("colonna.c", "giu.in"), ("divide.c", "altro.in")],
    )
    punti = [Point(x_mm=X0, y_mm=Y0 + 2.5), Point(x_mm=X0, y_mm=Y0 + 40), Point(x_mm=X0 + 80, y_mm=Y0 + 40)]
    assert _posa_la_tratta_di(project, "giunto", punti) == {"giunto": 0}


def test_la_pompa_che_prosegue_dritta_resta_sull_autostrada() -> None:
    """Due pompe di zona dallo stesso raccordo; la prima prosegue dritta e poi scende. La sua
    fila resta sul primo orizzontale, come la sorella: le pompe in parallelo le governa I-204,
    del PO, prima di questa regola. Sulla tavola del caso la pompa della zona lontana era
    finita in verticale."""
    pezzi = [("divide", "tee-split"), ("sorgente", "fan-coil"), ("zona-1", "fan-coil"), ("zona-2", "fan-coil")]
    tubi = [("sorgente.out", "divide.a")]
    for n, porta in ((1, "b"), (2, "c")):
        pezzi += [(f"v{n}a", "valve-isolation"), (f"pompa-{n}", "pump-circulator"), (f"v{n}b", "valve-isolation")]
        tubi += [(f"divide.{porta}", f"v{n}a.a"), (f"v{n}a.b", f"pompa-{n}.a"),
                 (f"pompa-{n}.b", f"v{n}b.a"), (f"v{n}b.b", f"zona-{n}.in")]
    punti = [Point(x_mm=X0 + 2.5, y_mm=Y0), Point(x_mm=X0 + 80, y_mm=Y0), Point(x_mm=X0 + 80, y_mm=Y0 + 80)]
    rotazioni = _posa_la_tratta_di(_rete(pezzi, tubi), "pompa-1", punti)
    # la valvola dopo la pompa isola il terminale, e sta sul suo attacco (D-120)
    assert {pezzo: rotazioni[pezzo] for pezzo in ("v1a", "pompa-1")} == {"v1a": 0, "pompa-1": 0}, rotazioni
