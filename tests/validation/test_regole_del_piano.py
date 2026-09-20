"""Le quattro regole di D-154, ciascuna col caso che cade e quello pulito.

Ogni geometria e' costruita a mano, minima e leggibile, e **nessuna passa dalla
catena di impaginazione**: una regola che si dimostra solo sul caso di
accettazione smette di dimostrare qualcosa il giorno in cui quel caso cambia,
ed e' esattamente il giorno in cui serve. E' la stessa scelta, e per la stessa
ragione, di `tests/validation/test_preflight.py`.

Le coordinate dei tubi non si scrivono a mano: si leggono dalle **porte dei
pezzi posati**, con `porte_in_tavola`. Cosi' una prova non si rompe il giorno in
cui un simbolo cambia di mezzo millimetro, e soprattutto non puo' dimostrare una
regola su una geometria che il motore non potrebbe mai produrre.
"""

# categoria: difende una regola del piano

from datetime import date
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.autostrade import PorteInTavola, porte_in_tavola
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
from disegnatore_mep.model.types import IssueSeverity, PlantRegime
from disegnatore_mep.validation.regole import (
    DISTRIBUZIONE,
    GENERAZIONE,
    autostrade_storte,
    macchine_in_parallelo_senza_collettore,
    organi_che_spezzano_il_tratto,
    pezzi_fuori_fascia,
    rilievi_delle_regole,
)

ROOT = Path(__file__).resolve().parents[2]
FRAME = NOVE_C_A3
RETE = "primo"


def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


# --- gli attrezzi per costruire un impianto e una tavola a mano ----------------


def tubo(identifier: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
    return ConnectionModel(
        id=identifier,
        network_id=RETE,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def impianto(
    components: list[tuple[str, str]], connections: list[ConnectionModel]
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-regole",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 20),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id=RETE, name=RETE, domain="hydronic", medium="heating_water")
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
                network_ids=[RETE],
            )
        ],
    )


def posa(
    project: ProjectModel,
    catalog: ComponentRegistry,
    origini: dict[str, tuple[float, float]],
    rotazioni: dict[str, int] | None = None,
) -> list[PlacedSymbol]:
    gradi = rotazioni or {}
    definizioni = {item.id: item.definition_id for item in project.components}
    posati: list[PlacedSymbol] = []
    for component_id, (x_mm, y_mm) in origini.items():
        manifesto = catalog.resolve(definizioni[component_id]).symbol.manifest.rotated(
            gradi.get(component_id, 0)
        )
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


def dove(porte: PorteInTavola, component_id: str, port_id: str) -> Point:
    return porte[(component_id, port_id)][0]


def tratta(connection_ids: list[str], *pezzi: list[Point]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=RETE,
        medium="heating_water",
        connection_ids=connection_ids,
        segments=list(pezzi),
    )


def tavola(symbols: list[PlacedSymbol], routes: list[RoutedTrunk]) -> DrawingGeometry:
    return DrawingGeometry(
        project_id="prova",
        sheets=[
            SheetGeometry(
                sheet_id="t1", title="Prova", symbols=symbols, routes=routes
            )
        ],
    )


def porte_di(
    project: ProjectModel, catalog: ComponentRegistry, symbols: list[PlacedSymbol]
) -> PorteInTavola:
    return porte_in_tavola(
        SheetGeometry(sheet_id="t1", title="Prova", symbols=symbols), project, catalog
    )


# ===========================================================================
# A1 — tre macro fasce verticali
# ===========================================================================


def centrale_con_un_terminale() -> ProjectModel:
    """Un generatore, un volano, un radiatore: una fascia per ciascuno."""
    return impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("volano", "buffer-four-port"),
            ("corpo", "radiator"),
        ],
        [
            tubo("p1", ("nord", "water_supply"), ("volano", "primary_in")),
            tubo("p2", ("volano", "primary_out"), ("nord", "water_return")),
            tubo("s1", ("volano", "secondary_out"), ("corpo", "in")),
            tubo("s2", ("corpo", "out"), ("volano", "secondary_in")),
        ],
    )


def test_a1_le_tre_fasce_separate_non_danno_rilievi() -> None:
    """Generazione, accumuli, distribuzione: in quest'ordine e senza toccarsi."""
    project, registry = centrale_con_un_terminale(), catalogo()
    symbols = posa(
        project,
        registry,
        {"nord": (0.0, 0.0), "volano": (100.0, 0.0), "corpo": (200.0, 0.0)},
    )
    assert pezzi_fuori_fascia(tavola(symbols, []), registry, project) == []


def test_a1_un_terminale_dentro_la_fascia_dei_generatori_e_un_rilievo() -> None:
    """Il radiatore finisce sopra la pompa di calore: due fasce si accavallano.

    Il rilievo nomina il pezzo, la sua fascia e la fascia in cui e' finito, con
    le ascisse vere: senza quelle, chi legge non sa dove mettere il dito.
    """
    project, registry = centrale_con_un_terminale(), catalogo()
    symbols = posa(
        project,
        registry,
        {"nord": (0.0, 0.0), "volano": (100.0, 0.0), "corpo": (20.0, 60.0)},
    )
    rilievi = pezzi_fuori_fascia(tavola(symbols, []), registry, project)

    assert [item.code for item in rilievi] == ["PIECE_OUTSIDE_ITS_BAND"] * 2
    assert all(item.severity is IssueSeverity.WARNING for item in rilievi)
    detto = " | ".join(item.message for item in rilievi)
    assert "corpo" in detto and "nord" in detto
    assert GENERAZIONE in detto and DISTRIBUZIONE in detto
    assert "volano" not in detto, "il volano sta al suo posto e non va nominato"
    assert "x=20.0" in detto and "x=40.0" in detto


# ===========================================================================
# B1 — prima le autostrade, e il piu' dritte possibile
# ===========================================================================


def cascata_su_un_volano() -> ProjectModel:
    """Due generatori in parallelo, un volano, e un radiatore sul secondario."""
    return impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
            ("unione", "tee-junction"),
            ("volano", "buffer-four-port"),
            ("ripartizione", "tee-split"),
        ],
        [
            tubo("p1", ("nord", "water_supply"), ("unione", "a")),
            tubo("p2", ("sud", "water_supply"), ("unione", "c")),
            tubo("p3", ("unione", "b"), ("volano", "primary_in")),
            tubo("p4", ("volano", "primary_out"), ("ripartizione", "a")),
            tubo("p5", ("ripartizione", "b"), ("nord", "water_return")),
            tubo("p6", ("ripartizione", "c"), ("sud", "water_return")),
        ],
    )


def _mandata_della_cascata(
    catalog: ComponentRegistry, volano_x_mm: float, volano_y_mm: float
) -> tuple[ProjectModel, list[PlacedSymbol], PorteInTavola]:
    project = cascata_su_un_volano()
    symbols = posa(
        project,
        catalog,
        {
            "nord": (0.0, 0.0),
            "sud": (0.0, 60.0),
            "unione": (60.0, 2.5),
            "volano": (volano_x_mm, volano_y_mm),
            "ripartizione": (60.0, 40.0),
        },
    )
    return project, symbols, porte_di(project, catalog, symbols)


def test_b1_un_autostrada_dritta_non_da_rilievi() -> None:
    """Pompa, raccordo e volano sulla stessa quota: la catena e' una retta."""
    registry = catalogo()
    project, symbols, porte = _mandata_della_cascata(registry, 100.0, 0.0)
    routes = [
        tratta(["p1"], [dove(porte, "nord", "water_supply"), dove(porte, "unione", "a")]),
        tratta(
            ["p3"], [dove(porte, "unione", "b"), dove(porte, "volano", "primary_in")]
        ),
    ]
    assert autostrade_storte(tavola(symbols, routes), registry, project) == []


def test_b1_un_autostrada_che_piega_e_un_rilievo_e_dice_quante_volte() -> None:
    """La catena esce dal raccordo e scende: e' una piega, e ne aveva zero.

    E' il messaggio che **D-153** prescrive — «la tratta `s3` piega quattro
    volte, e su un'autostrada le pieghe ammesse sono zero» — con i nomi veri e i
    numeri veri di questa tavola.
    """
    registry = catalogo()
    project, symbols, porte = _mandata_della_cascata(registry, 65.0, 25.0)
    routes = [
        tratta(["p1"], [dove(porte, "nord", "water_supply"), dove(porte, "unione", "a")]),
        tratta(
            ["p3"], [dove(porte, "unione", "b"), dove(porte, "volano", "primary_in")]
        ),
    ]
    rilievi = autostrade_storte(tavola(symbols, routes), registry, project)

    assert [item.code for item in rilievi] == ["HIGHWAY_IS_NOT_STRAIGHT"]
    assert rilievi[0].severity is IssueSeverity.WARNING
    detto = rilievi[0].message
    assert "p1" in detto and "p3" in detto
    assert "piegano 1 volta" in detto
    assert "le pieghe ammesse sono 0" in detto
    assert "nord" in detto and "volano" in detto
    assert "B1" not in detto.split("(")[0], "il testo dice il fatto, non la sigla"


# ===========================================================================
# B3 — piu' generatori o piu' terminali ⇒ collettore verticale
# ===========================================================================


def tre_generatori_su_due_raccordi() -> ProjectModel:
    """Tre pompe di calore che confluiscono su una catena di due T.

    E' la forma della cascata: ogni macchina il proprio stacco corto, e i
    raccordi incolonnati.
    """
    return impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("centro", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
            ("alto", "tee-junction"),
            ("basso", "tee-junction"),
            ("volano", "buffer-four-port"),
        ],
        [
            tubo("g1", ("nord", "water_supply"), ("alto", "a")),
            tubo("g2", ("alto", "b"), ("basso", "b")),
            tubo("g3", ("centro", "water_supply"), ("basso", "a")),
            tubo("g4", ("sud", "water_supply"), ("basso", "c")),
            tubo("g5", ("alto", "c"), ("volano", "primary_in")),
        ],
    )


def _cascata_con_i_raccordi(
    catalog: ComponentRegistry, basso_x_mm: float
) -> tuple[ProjectModel, list[PlacedSymbol], PorteInTavola]:
    project = tre_generatori_su_due_raccordi()
    symbols = posa(
        project,
        catalog,
        {
            "nord": (0.0, 0.0),
            "centro": (0.0, 60.0),
            "sud": (0.0, 120.0),
            "alto": (100.0, 2.5),
            "basso": (basso_x_mm, 62.5),
            "volano": (200.0, 0.0),
        },
    )
    return project, symbols, porte_di(project, catalog, symbols)


def test_b3_un_collettore_verticale_e_allineato_non_da_rilievi() -> None:
    """I due T sulla stessa ascissa, e la tratta fra loro in verticale."""
    registry = catalogo()
    project, symbols, porte = _cascata_con_i_raccordi(registry, 100.0)
    routes = [
        tratta(["g2"], [dove(porte, "alto", "b"), dove(porte, "basso", "b")]),
    ]
    assert (
        macchine_in_parallelo_senza_collettore(
            tavola(symbols, routes), FRAME, registry, project
        )
        == []
    )


def test_b3_due_raccordi_sfalsati_sono_un_rilievo() -> None:
    """Il secondo T se ne va di quaranta millimetri: non e' piu' un collettore.

    Il rilievo dice **quali** T, **a quali ascisse** e **quante** macchine in
    parallelo ci si attaccano.
    """
    registry = catalogo()
    project, symbols, porte = _cascata_con_i_raccordi(registry, 140.0)
    partenza, arrivo = dove(porte, "alto", "b"), dove(porte, "basso", "b")
    routes = [
        tratta(
            ["g2"],
            [
                partenza,
                Point(x_mm=partenza.x_mm, y_mm=arrivo.y_mm),
                arrivo,
            ],
        ),
    ]
    rilievi = macchine_in_parallelo_senza_collettore(
        tavola(symbols, routes), FRAME, registry, project
    )

    assert [item.code for item in rilievi] == [
        "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR"
    ]
    assert rilievi[0].severity is IssueSeverity.WARNING
    detto = rilievi[0].message
    assert "alto" in detto and "basso" in detto
    assert "3 generatori in parallelo" in detto
    assert "nord" in detto and "centro" in detto and "sud" in detto
    assert "x=102.5" in detto and "x=142.5" in detto
    assert "40.0 mm" in detto


# ===========================================================================
# B4 — un organo in linea non spezza il tratto
# ===========================================================================


def un_circolatore_in_linea() -> ProjectModel:
    """Il circolatore sta **sopra** la tratta e la interrompe (D-027)."""
    return impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("pompa", "pump-circulator"),
            ("volano", "buffer-four-port"),
        ],
        [
            tubo("b1", ("nord", "water_supply"), ("pompa", "a")),
            tubo("b2", ("pompa", "b"), ("volano", "primary_in")),
            tubo("b3", ("volano", "primary_out"), ("nord", "water_return")),
        ],
    )


def test_b4_un_organo_sulla_retta_non_da_rilievi() -> None:
    """Ingresso e uscita allineati: la linea passa, e il pezzo non la piega."""
    registry = catalogo()
    project = un_circolatore_in_linea()
    symbols = posa(
        project,
        registry,
        {"nord": (0.0, 0.0), "pompa": (60.0, 0.0), "volano": (100.0, 0.0)},
    )
    porte = porte_di(project, registry, symbols)
    routes = [
        tratta(
            ["b1", "b2"],
            [dove(porte, "nord", "water_supply"), dove(porte, "pompa", "a")],
            [dove(porte, "pompa", "b"), dove(porte, "volano", "primary_in")],
        )
    ]
    assert organi_che_spezzano_il_tratto(tavola(symbols, routes), registry, project) == []


def test_b4_un_organo_sulla_piega_e_un_rilievo() -> None:
    """Il circolatore girato di novanta gradi, con la linea che gli svolta addosso.

    E' il difetto trovato sull'impianto 5 composto: la tratta arriva orizzontale
    sulla porta di sopra e riparte verticale da quella di sotto. L'organo sta
    sulla piega, e la piega e' **sua**.
    """
    registry = catalogo()
    project = un_circolatore_in_linea()
    symbols = posa(
        project,
        registry,
        {"nord": (0.0, 0.0), "pompa": (60.0, 0.0), "volano": (100.0, 60.0)},
        rotazioni={"pompa": 90},
    )
    porte = porte_di(project, registry, symbols)
    sopra, sotto = dove(porte, "pompa", "a"), dove(porte, "pompa", "b")
    partenza = dove(porte, "nord", "water_supply")
    arrivo = dove(porte, "volano", "primary_in")
    routes = [
        tratta(
            ["b1", "b2"],
            # La tratta arriva **orizzontale** sulla porta di sopra, e riparte
            # **verticale** da quella di sotto: l'organo sta sulla piega.
            [partenza, Point(x_mm=partenza.x_mm, y_mm=sopra.y_mm), sopra],
            [sotto, Point(x_mm=sotto.x_mm, y_mm=arrivo.y_mm), arrivo],
        )
    ]
    rilievi = organi_che_spezzano_il_tratto(tavola(symbols, routes), registry, project)

    assert [item.code for item in rilievi] == ["INLINE_ORGAN_BREAKS_THE_RUN"]
    assert rilievi[0].severity is IssueSeverity.WARNING
    detto = rilievi[0].message
    assert "pompa" in detto
    assert " a " in detto and " b " in detto
    assert "orizzontale" in detto and "verticale" in detto
    assert f"x={sopra.x_mm:.1f}" in detto


# ===========================================================================
# Il raccoglitore
# ===========================================================================


def test_il_raccoglitore_porta_tutte_e_quattro_le_regole_e_solo_avvisi() -> None:
    """`rilievi_delle_regole` e' l'unione dei quattro controlli, e non blocca.

    La severita' e' una scelta dichiarata (vedi il modulo): una violazione di
    regola e' un difetto **del piano**, non un motivo per rifiutare la tavola.
    Il cancello di consegna resta quello del preflight (D-063).
    """
    registry = catalogo()
    project, symbols, porte = _mandata_della_cascata(registry, 65.0, 25.0)
    routes = [
        tratta(["p1"], [dove(porte, "nord", "water_supply"), dove(porte, "unione", "a")]),
        tratta(
            ["p3"], [dove(porte, "unione", "b"), dove(porte, "volano", "primary_in")]
        ),
    ]
    rilievi = rilievi_delle_regole(tavola(symbols, routes), FRAME, registry, project)

    assert rilievi, "questa tavola una regola la viola"
    assert all(item.severity is IssueSeverity.WARNING for item in rilievi)
    assert set(item.code for item in rilievi) <= {
        "PIECE_OUTSIDE_ITS_BAND",
        "HIGHWAY_IS_NOT_STRAIGHT",
        "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
        "INLINE_ORGAN_BREAKS_THE_RUN",
    }
