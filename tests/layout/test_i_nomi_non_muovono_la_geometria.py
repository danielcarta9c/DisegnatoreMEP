"""Assi fra le porte, dorsali rettilinee e T che assorbe una curva (DRAW-004).

> **Dal 2 ottobre 2026 (I-180) il solutore non c'e' piu'**, e con lui le prove che lo
> difendevano. Restano qui la prova che ridenominare i pezzi non cambia la geometria. Il resto di questa intestazione e' la storia del
> file, e si legge come tale.


Il PO (I-026, I-027, I-029): «allineare l'uscita di A con l'asse utile verso
l'ingresso di B e' un modo di ragionare, non una regola assoluta». Il
disegnatore prova a spostare gratuitamente le macchine per togliere curve,
costruisce una dorsale diritta e poi aggiunge gli stacchi; sceglie pero'
l'alternativa con il costo globale minore, misurato sulla tavola completa dopo
il reinstradamento. Una T puo' usare due attacchi ortogonali come prosecuzione
e assorbire il gomito nel punto di diramazione: e' una proprieta' della posa,
non del grafo.

Queste prove sono **generali**: gli impianti sono costruiti qui dentro con il
catalogo di prova, e nessuna coordinata o identificativo dell'impianto 1 entra
nel motore ne' nelle attese. Scritte prima del codice applicativo, come il
pacchetto chiede.
"""
# categoria: difende il motore — ridenominare i pezzi non cambia la geometria, e due generazioni coincidono

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    drawing_fingerprint,
)
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



@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _plant(
    components: list[tuple[str, str]],
    connections: list[tuple[str, str, str, str, str]],
    subsystems: list[tuple[str, list[str]]],
    tags: dict[str, str] | None = None,
) -> ProjectModel:
    """Un impianto minimo: (id, definizione), (id, da, porta, a, porta), gruppi."""
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-assi",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date="2026-09-04",
        ),
        subsystems=[
            SubsystemModel(id=name, name=name, component_ids=members, network_ids=["rete"])
            for name, members in subsystems
        ],
        networks=[
            NetworkModel(id="rete", name="Rete", domain="hydronic", medium="heating_water")
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition, tag=(tags or {}).get(item))
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
















# ---------------------------------------------------------------------------
# Gli impianti di prova, costruiti qui
# ---------------------------------------------------------------------------


def macchina_e_serbatoio() -> ProjectModel:
    """Una macchina e un accumulo, collegabili con una linea diritta.

    Le due porte non stanno alla stessa quota quando i due pezzi poggiano allo
    stesso piano: la macchina e' alta trenta e l'accumulo quarantacinque. E'
    il dogleg che spostare gratuitamente una delle due toglie.
    """
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("serbatoio", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "serbatoio", "a"),
            ("c2", "serbatoio", "b", "terminale", "in"),
            ("c3", "terminale", "out", "macchina", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("accumulo", ["serbatoio"]),
            ("utenza", ["terminale"]),
        ],
    )


def dorsale_con_uno_stacco() -> ProjectModel:
    """Una sequenza principale macchina → raccordo → accumulo, con un ramo
    che dal raccordo sale a un terminale."""
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("raccordo", "tee-split"),
            ("serbatoio", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "raccordo", "a"),
            ("c2", "raccordo", "b", "serbatoio", "a"),
            ("c3", "raccordo", "c", "terminale", "in"),
        ],
        subsystems=[
            ("generazione", ["macchina", "raccordo"]),
            ("accumulo", ["serbatoio"]),
            ("utenza", ["terminale"]),
        ],
    )


def tee_che_deve_girare(tags: dict[str, str] | None = None) -> ProjectModel:
    """Un raccordo il cui percorso principale gira: dalla macchina sale al
    terminale, mentre lo stacco prosegue diritto verso l'accumulo.

    Il modello dice quali porte si collegano — `b` al terminale, `c`
    all'accumulo — e il simbolo disegna un punto: quale attacco fisico serve
    ciascuna porta e' una scelta della posa.
    """
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("raccordo", "tee-split"),
            ("terminale", "radiator"),
            ("serbatoio", "buffer-two-port"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "raccordo", "a"),
            ("c2", "raccordo", "b", "terminale", "in"),
            ("c3", "raccordo", "c", "serbatoio", "a"),
        ],
        subsystems=[
            ("generazione", ["macchina", "raccordo"]),
            ("utenza", ["terminale"]),
            ("accumulo", ["serbatoio"]),
        ],
        tags=tags,
    )




# ---------------------------------------------------------------------------
# 1-3. Candidati di allineamento delle porte
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# 4. Dorsale prima, stacchi dopo
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# 5-6. La T che assorbe una curva
# ---------------------------------------------------------------------------
















# ---------------------------------------------------------------------------
# 7-8. Determinismo, identificativi, testi
# ---------------------------------------------------------------------------

_ID_KEYS = frozenset({"id", "component_id", "network_id", "subsystem_id"})
_ID_LIST_KEYS = frozenset({"component_ids", "network_ids", "subsystem_ids"})


def _renamed(project: ProjectModel) -> ProjectModel:
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


def _shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    sheet = drawing.sheets[0]
    symbols = sorted(
        (
            item.symbol_id,
            item.rotation_deg,
            item.origin.x_mm,
            item.origin.y_mm,
            tuple(sorted(item.port_map.values())),
        )
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


def test_ridenominare_gli_id_non_cambia_la_geometria_e_due_generazioni_coincidono() -> None:
    """Prova 7."""
    for project in (tee_che_deve_girare(), dorsale_con_uno_stacco(), macchina_e_serbatoio()):
        once = compose_drawing(project, catalog(), NOVE_C_A3)
        twice = compose_drawing(project, catalog(), NOVE_C_A3)
        assert drawing_fingerprint(once) == drawing_fingerprint(twice)
        renamed = compose_drawing(_renamed(project), catalog(), NOVE_C_A3)
        assert _shape(once) == _shape(renamed)


