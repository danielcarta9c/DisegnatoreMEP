"""L'autostrada sulla tavola: la catena si ritrova sulle tratte instradate.

Il difetto che queste prove difendono e' quello che ha generato **D-151**: fino
a ieri la geometria non sapeva **quali tratte sono autostrada**, e
`RUN_WITH_TOO_MANY_BENDS` contava una piega della dorsale come una piega di uno
stacchetto. Il PO, il 20 settembre: «abbiamo ottimizzato le curve e gli
attraversamenti sugli attacchetti e abbiamo fatto sta curva senza senso».

La terza prova e' la piu' importante, ed e' la forma esatta del difetto che
`DRAW-012` §C ha gia' descritto sul modello: **ogni tratta e' dritta e la catena
fa un gomito sul raccordo che le unisce.** I numeri erano verdi e la tavola era
storta.
"""

# categoria: difende una regola del piano

from datetime import date
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.autostrade import (
    autostrade_del_progetto,
    e_autostrada,
    pieghe_dell_autostrada,
    pieghe_della_tratta,
    porte_in_tavola,
    tratte_dell_autostrada,
)
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
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
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.validation.preflight import bends_per_run

ROOT = Path(__file__).resolve().parents[2]
PRIMO = "primo"


def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def _tubo(
    identifier: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=identifier,
        network_id=PRIMO,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _impianto(
    components: list[tuple[str, str]], connections: list[ConnectionModel]
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-autostrade",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 20),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(
                id=PRIMO, name=PRIMO, domain="hydronic", medium="heating_water"
            )
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=connections,
        subsystems=[
            SubsystemModel(
                id="tutto",
                name="tutto",
                component_ids=[item for item, _ in components],
                network_ids=[PRIMO],
            )
        ],
    )


def cascata() -> ProjectModel:
    """Due generatori in parallelo su un volano, e nient'altro.

    Le autostrade sono le catene che uniscono i generatori al volano
    attraverso i due raccordi: e' il caso su cui **D-138** dice «dai generatori
    agli accumuli», al plurale.
    """
    return _impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
            ("unione", "tee-junction"),
            ("volano", "buffer-four-port"),
            ("ripartizione", "tee-split"),
            ("presa", "tee-branch"),
            ("manometro", "pressure-gauge"),
        ],
        [
            _tubo("p1", ("nord", "water_supply"), ("unione", "a")),
            _tubo("p2", ("sud", "water_supply"), ("unione", "c")),
            _tubo("p3", ("unione", "b"), ("volano", "primary_in")),
            _tubo("p4", ("volano", "primary_out"), ("ripartizione", "a")),
            _tubo("p5", ("ripartizione", "b"), ("nord", "water_return")),
            _tubo("p6", ("ripartizione", "c"), ("sud", "water_return")),
            _tubo("st1", ("ripartizione", "b"), ("presa", "a")),
            _tubo("st2", ("presa", "branch"), ("manometro", "a")),
        ],
    )


def posa(
    project: ProjectModel,
    catalog: ComponentRegistry,
    origini: dict[str, tuple[float, float]],
    rotazioni: dict[str, int] | None = None,
) -> list[PlacedSymbol]:
    """I pezzi dove il piano li mette, con l'ingombro che il simbolo dichiara."""
    gradi = rotazioni or {}
    definizioni = {item.id: item.definition_id for item in project.components}
    posati: list[PlacedSymbol] = []
    for component_id, (x_mm, y_mm) in origini.items():
        risolto = catalog.resolve(definizioni[component_id])
        manifesto = risolto.symbol.manifest.rotated(gradi.get(component_id, 0))
        posati.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=manifesto.id,
                rotation_deg=gradi.get(component_id, 0),
                origin=Point(x_mm=x_mm, y_mm=y_mm),
                width_mm=manifesto.width_mm,
                height_mm=manifesto.height_mm,
            )
        )
    return posati


def tratta(
    connection_ids: list[str], *punti: tuple[float, float]
) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=PRIMO,
        medium="heating_water",
        connection_ids=connection_ids,
        segments=[[Point(x_mm=x, y_mm=y) for x, y in punti]],
    )


# Una posa in cui **ogni porta che conta sta dove serve**: nord e sud a
# sinistra, i due raccordi in mezzo, il volano a destra. Le coordinate sono
# quelle che le prove qui sotto usano, e si leggono dal manifesto dei simboli:
# la pompa e' 40x30 con le due porte sulla faccia destra a +5 e +20, il T e'
# 5x5 con le porte a meta' faccia, il volano e' 25x45 con `primary_in` a +5 e
# `primary_out` a +20 sulla faccia sinistra.
ORIGINI = {
    "nord": (0.0, 0.0),
    "sud": (0.0, 60.0),
    "unione": (60.0, 2.5),
    "volano": (100.0, 0.0),
    "ripartizione": (60.0, 17.5),
    "presa": (40.0, 17.5),
    "manometro": (40.0, 40.0),
}


def foglio(
    project: ProjectModel, catalog: ComponentRegistry, routes: list[RoutedTrunk]
) -> SheetGeometry:
    return SheetGeometry(
        sheet_id="t1",
        title="Prova",
        symbols=posa(project, catalog, ORIGINI),
        routes=routes,
    )


def test_la_catena_si_ritrova_sulle_tratte_instradate() -> None:
    """Una tratta instradata sa a quale autostrada appartiene, e uno stacco no.

    L'aggancio e' `connection_ids`, la stessa chiave che il modello usa: nessun
    nome, nessuna coordinata.
    """
    project, registry = cascata(), catalogo()
    autostrade = autostrade_del_progetto(project, registry)
    assert autostrade, "la cascata ha almeno un'autostrada"

    struttura = tratta(["p1"], (40.0, 5.0), (60.0, 5.0))
    stacco = tratta(["st2"], (42.5, 17.5), (42.5, 40.0))

    trovata = e_autostrada(struttura, autostrade)
    assert trovata is not None
    assert "p1" in trovata.connection_ids
    assert "nord" in trovata.pezzi and "volano" in trovata.pezzi
    assert trovata.nome.count("->") == len(trovata.pezzi) - 1

    assert e_autostrada(stacco, autostrade) is None


def test_una_catena_dritta_non_e_un_rilievo() -> None:
    """Nord, il raccordo e il volano sulla stessa quota: zero pieghe, nessun avviso.

    Le due tratte della catena si susseguono **attraverso** il raccordo, e la
    retta non cambia: e' la forma che `DRAW-012` §C chiede all'autostrada fra
    le macchine di spina.
    """
    project, registry = cascata(), catalogo()
    autostrade = autostrade_del_progetto(project, registry)
    routes = [
        tratta(["p1"], (40.0, 5.0), (60.0, 5.0)),
        tratta(["p3"], (65.0, 5.0), (100.0, 5.0)),
    ]
    sheet = foglio(project, registry, routes)
    porte = porte_in_tavola(sheet, project, registry)

    catena = e_autostrada(routes[0], autostrade)
    assert catena is not None
    assert [item is not None for item in tratte_dell_autostrada(catena, routes)] == [
        True,
        True,
    ]
    assert catena.curve_ammesse == 0
    assert pieghe_dell_autostrada(catena, routes, porte) == 0
    assert bends_per_run(DrawingGeometry(project_id="prova", sheets=[sheet]), autostrade) == []


def test_una_catena_piegata_dentro_una_tratta_e_un_rilievo() -> None:
    """La seconda tratta fa una elle: la catena non e' piu' una retta.

    La piega sta **dentro** la tratta, e la conta anche il preflight: qui si
    verifica che le due misure dicano lo stesso numero.
    """
    project, registry = cascata(), catalogo()
    autostrade = autostrade_del_progetto(project, registry)
    routes = [
        tratta(["p1"], (40.0, 5.0), (60.0, 5.0)),
        tratta(["p3"], (65.0, 5.0), (65.0, 30.0), (100.0, 30.0)),
    ]
    sheet = foglio(project, registry, routes)
    porte = porte_in_tavola(sheet, project, registry)

    catena = e_autostrada(routes[1], autostrade)
    assert catena is not None
    assert pieghe_della_tratta(routes[1]) == 1
    # Una piega dentro la tratta, e una sul crocevia: uscendo dal raccordo la
    # catena scende invece di proseguire in orizzontale.
    assert pieghe_dell_autostrada(catena, routes, porte) == 2

    rilievi = bends_per_run(
        DrawingGeometry(project_id="prova", sheets=[sheet]), autostrade
    )
    assert [item.code for item in rilievi] == ["RUN_WITH_TOO_MANY_BENDS"]
    assert "autostrada" in rilievi[0].message
    assert "le pieghe ammesse sono 0" in rilievi[0].message


def test_la_piega_sul_crocevia_la_vede_solo_la_catena() -> None:
    """**Ogni tratta e' dritta e la catena fa un gomito**: e' il difetto di D-151.

    Le due tratte hanno zero pieghe ciascuna, quindi nessuna misura per tratta
    ha niente da dire — ne' il conto di sempre, ne' quello nuovo. La catena,
    invece, cambia giacitura sul raccordo: entra in orizzontale a quota 5 ed
    esce in verticale su x=65. E' esattamente «i numeri erano verdi e la tavola
    era storta».
    """
    project, registry = cascata(), catalogo()
    autostrade = autostrade_del_progetto(project, registry)
    routes = [
        tratta(["p1"], (40.0, 5.0), (60.0, 5.0)),
        tratta(["p3"], (65.0, 5.0), (65.0, 30.0)),
    ]
    volano_piu_in_basso = dict(ORIGINI, volano=(65.0, 25.0))
    sheet = SheetGeometry(
        sheet_id="t1",
        title="Prova",
        symbols=posa(project, registry, volano_piu_in_basso),
        routes=routes,
    )
    porte = porte_in_tavola(sheet, project, registry)

    assert [pieghe_della_tratta(item) for item in routes] == [0, 0]
    assert (
        bends_per_run(DrawingGeometry(project_id="prova", sheets=[sheet]), autostrade)
        == []
    )

    catena = e_autostrada(routes[0], autostrade)
    assert catena is not None
    assert pieghe_dell_autostrada(catena, routes, porte) == 1
    assert catena.curve_ammesse == 0


def test_una_catena_che_il_foglio_non_porta_intera_non_si_misura() -> None:
    """Meglio nessun numero che un numero su una catena mutilata."""
    project, registry = cascata(), catalogo()
    autostrade = autostrade_del_progetto(project, registry)
    routes = [tratta(["p1"], (40.0, 5.0), (60.0, 5.0))]
    sheet = foglio(project, registry, routes)
    porte = porte_in_tavola(sheet, project, registry)

    catena = e_autostrada(routes[0], autostrade)
    assert catena is not None
    assert len(catena.catene) > 1
    assert pieghe_dell_autostrada(catena, routes, porte) is None


def test_senza_le_autostrade_il_preflight_conta_come_prima() -> None:
    """La retrocompatibilita' e' un vincolo, non una cortesia.

    Trentasei file di prove misurano `bends_per_run` senza sapere niente di
    catene: chiamata senza autostrade, la misura resta quella di sempre — tre
    pieghe per unire due porte (`BENDS_PER_RUN_MAX`, D-078).
    """
    project, registry = cascata(), catalogo()
    routes = [
        tratta(["p1"], (40.0, 5.0), (60.0, 5.0)),
        tratta(["p3"], (65.0, 5.0), (65.0, 30.0), (100.0, 30.0)),
    ]
    sheet = foglio(project, registry, routes)
    assert bends_per_run(DrawingGeometry(project_id="prova", sheets=[sheet])) == []
