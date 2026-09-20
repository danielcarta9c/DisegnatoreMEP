"""Le regole del piano, ciascuna col caso che cade e quello pulito.

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
from disegnatore_mep.graphics.symbol import PortFace
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
    ORDINE_DELLE_REGOLE,
    autostrade_storte,
    macchine_in_parallelo_senza_collettore,
    organi_che_spezzano_il_tratto,
    organi_di_servizio_lontani,
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
# A4 — un organo di servizio sta addosso al pezzo che serve
# ===========================================================================


def girato_verso(
    catalog: ComponentRegistry, definition_id: str, port_id: str, faccia: PortFace
) -> int:
    """La rotazione con cui quell'attacco guarda da quella parte.

    Serve a posare un organo **come il motore lo poserebbe** — rivolto verso il
    pezzo da cui pende — invece di scrivere a mano una rotazione che il giorno
    dopo, cambiato il simbolo, guarda da un'altra parte.
    """
    manifesto = catalog.resolve(definition_id).symbol.manifest
    for gradi in manifesto.allowed_rotations_deg:
        if manifesto.rotated(gradi).port(port_id).face is faccia:
            return gradi
    raise AssertionError(f"{definition_id} non sa guardare {faccia}")


def uno_sfiato_su_uno_stacco(con_la_valvola: bool) -> ProjectModel:
    """Una pompa, un T sulla mandata, e uno sfiato appeso allo stacco del T.

    Lo sfiato ha **un attacco solo** e pende da `branch`, che il catalogo
    dichiara fuori dal percorso del fluido (`stub`): e' la stessa lettura con
    cui il motore riconosce un accessorio appeso. Con la valvola, lo stesso
    stacco porta **un accessorio in linea**, e il minimo cresce di conseguenza.
    """
    pezzi = [
        ("nord", "heat-pump-air-water"),
        ("stacco", "tee-branch"),
        ("volano", "buffer-four-port"),
        ("sfiato", "air-vent"),
    ]
    tubi = [
        tubo("p1", ("nord", "water_supply"), ("stacco", "a")),
        tubo("p2", ("stacco", "b"), ("volano", "primary_in")),
    ]
    if con_la_valvola:
        pezzi.append(("valvola", "valve-isolation"))
        tubi.append(tubo("s1", ("stacco", "branch"), ("valvola", "a")))
        tubi.append(tubo("s2", ("valvola", "b"), ("sfiato", "a")))
    else:
        tubi.append(tubo("s1", ("stacco", "branch"), ("sfiato", "a")))
    return impianto(pezzi, tubi)


def _stacco_dello_sfiato(
    catalog: ComponentRegistry,
    lungo_mm: float,
    con_la_valvola: bool,
    nord_a: tuple[float, float] = (100.0, 100.0),
) -> tuple[ProjectModel, list[PlacedSymbol], list[RoutedTrunk]]:
    """La tavola con lo sfiato a `lungo_mm` dal proprio T, valvola o no.

    Le coordinate del tubo non si scrivono: si leggono dalle porte dei pezzi
    posati, e con la valvola la spezzata si interrompe sotto di lei come la
    interrompe il motore (D-027).
    """
    project = uno_sfiato_su_uno_stacco(con_la_valvola)
    origini = {
        "nord": nord_a,
        "stacco": (200.0, 102.5),
        "volano": (260.0, 100.0),
        # Lo sfiato pende **sopra** il T: il suo attacco guarda in giu\' e sta
        # `lungo_mm` piu\' in alto di quello del T.
        "sfiato": (200.0, 92.5 - lungo_mm),
    }
    gradi: dict[str, int] = {}
    if con_la_valvola:
        # La valvola sta **sullo** stacco, girata come il motore la girerebbe:
        # i suoi due attacchi in fila lungo la derivazione, non di traverso.
        gradi["valvola"] = girato_verso(
            catalog, "valve-isolation", "a", PortFace.BOTTOM
        )
        origini["valvola"] = (200.0, 87.5)
    symbols = posa(project, catalog, origini, rotazioni=gradi)
    porte = porte_di(project, catalog, symbols)
    capo, coda = dove(porte, "sfiato", "a"), dove(porte, "stacco", "branch")
    if not con_la_valvola:
        return project, symbols, [tratta(["s1"], [capo, coda])]
    fermate = sorted(
        (dove(porte, "valvola", "a"), dove(porte, "valvola", "b")),
        key=lambda punto: punto.y_mm,
    )
    return (
        project,
        symbols,
        [tratta(["s1", "s2"], [capo, fermate[0]], [fermate[1], coda])],
    )


def test_a4_uno_stacco_al_proprio_minimo_non_da_rilievi() -> None:
    """Lo sfiato addosso al proprio T: dieci millimetri, ed e\' il minimo.

    Il minimo non e\' scritto qui: e\' quello che il motore calcola per questo
    stacco (`place.stub_minimum_mm` e cio\' che gli sta intorno). Dieci
    millimetri sono `place.ROW_GAP_MM`, la distanza minima fra due simboli
    qualunque sul foglio (D-062), che su uno stacco vuoto e\' la voce che vince.
    """
    registry = catalogo()
    project, symbols, routes = _stacco_dello_sfiato(registry, 10.0, False)
    assert (
        organi_di_servizio_lontani(tavola(symbols, routes), FRAME, registry, project)
        == []
    )


def test_a4_uno_stacco_piu_lungo_del_minimo_e_un_rilievo() -> None:
    """Lo stesso sfiato a venti millimetri: dieci di tubo che nessuno ha chiesto.

    E\' il messaggio che **D-153** prescrive, con i nomi veri e i numeri veri:
    quanto e\' lungo lo stacco, quanto vale il suo minimo, e quanto tubo c\'e\'
    di troppo.
    """
    registry = catalogo()
    project, symbols, routes = _stacco_dello_sfiato(registry, 20.0, False)
    rilievi = organi_di_servizio_lontani(
        tavola(symbols, routes), FRAME, registry, project
    )

    assert [item.code for item in rilievi] == ["SERVICE_STUB_LONGER_THAN_ITS_MINIMUM"]
    assert rilievi[0].severity is IssueSeverity.WARNING
    detto = rilievi[0].message
    assert "sfiato" in detto and "stacco" in detto
    assert "lungo 20.0 mm" in detto
    assert "minimo su griglia e\' 10.0" in detto
    assert "10.0 mm di tubo in piu\'" in detto
    assert "A4" not in detto.split("(")[0], "il testo dice il fatto, non la sigla"


def test_a4_uno_stacco_lungo_per_i_suoi_accessori_non_e_una_violazione() -> None:
    """**L\'eccezione di D-145.** Stessa lunghezza, due verdetti diversi.

    Venti millimetri di stacco sono una violazione su una derivazione vuota e
    **non lo sono** se su quella derivazione c\'e\' una valvola: il minimo non e\'
    piu\' quello dello stacco vuoto, e\' quello che l\'accessorio pretende
    (**I-044**, e l\'interruzione che `inline.py` gli lascera\'). E\' il «vincolo
    dichiarato» che **D-145** punto 1 nomina — «per esempio far posto a un altro
    accessorio in linea sulla stessa tratta» — e non e\' un caso a parte nel
    codice: sta **dentro il minimo**.

    Le due meta\' di questa prova vanno lette insieme: senza la prima, la
    seconda dimostrerebbe soltanto che il controllo tace.
    """
    registry = catalogo()

    vuoto, senza, rotte_senza = _stacco_dello_sfiato(registry, 20.0, False)
    assert [
        item.code
        for item in organi_di_servizio_lontani(
            tavola(senza, rotte_senza), FRAME, registry, vuoto
        )
    ] == ["SERVICE_STUB_LONGER_THAN_ITS_MINIMUM"], "venti su una derivazione vuota"

    project, symbols, routes = _stacco_dello_sfiato(registry, 20.0, True)
    assert (
        organi_di_servizio_lontani(tavola(symbols, routes), FRAME, registry, project)
        == []
    ), "venti su una derivazione che porta una valvola"


def test_a4_uno_stacco_lungo_perche_il_posto_e_preso_non_e_una_violazione() -> None:
    """**L\'altra eccezione di D-145**, e anche questa e\' del motore.

    Lo stesso sfiato a venti millimetri, con la pompa di calore posata sotto di
    lui: un passo piu\' vicino al proprio T il suo riquadro toccherebbe la
    macchina, e allora lo stacco e\' lungo **per necessita\'**, non per una
    costante. E\' la lettura che
    `tests/layout/test_stacchi_minimi_e_interasse.py::_taken_one_step_closer`
    fa gia\' sulla posa, e che qui arriva sulla tavola finita.

    Le due meta\' vanno lette insieme: la stessa geometria, col posto libero,
    e\' la violazione di `test_a4_uno_stacco_piu_lungo_del_minimo_e_un_rilievo`.
    """
    registry = catalogo()
    project, symbols, routes = _stacco_dello_sfiato(
        registry, 20.0, False, nord_a=(160.0, 70.0)
    )
    assert (
        organi_di_servizio_lontani(tavola(symbols, routes), FRAME, registry, project)
        == []
    )


def un_bollitore_e_il_suo_prelievo() -> ProjectModel:
    """Un bollitore, e il prelievo ACS che se ne va verso le utenze.

    Il prelievo e\' un **confine di rete** (`flow.BOUNDARY_FUNCTION`) e non pende
    da nessuno stacco: il suo attacco sta sul percorso del fluido, e per la posa
    del motore «e\' l\'ultimo passo della lettura e sta in fondo, come ogni
    utilizzatore». E\' il pezzo per cui A4 esiste.
    """
    return impianto(
        [
            ("nord", "heat-pump-air-water"),
            ("bollitore", "dhw-cylinder"),
            ("presa", "dhw-draw-off"),
        ],
        [
            tubo("p1", ("nord", "water_supply"), ("bollitore", "coil_in")),
            tubo("p2", ("bollitore", "coil_out"), ("nord", "water_return")),
            tubo("acs", ("bollitore", "dhw_out"), ("presa", "a")),
        ],
    )


def _prelievo_a(
    catalog: ComponentRegistry, lungo_mm: float
) -> tuple[ProjectModel, list[PlacedSymbol], list[RoutedTrunk]]:
    """La tavola col prelievo ACS a `lungo_mm` dall\'uscita del bollitore."""
    project = un_bollitore_e_il_suo_prelievo()
    solo = posa(project, catalog, {"bollitore": (200.0, 150.0)})
    uscita = porte_di(project, catalog, solo)[("bollitore", "dhw_out")][0]
    gradi = girato_verso(catalog, "dhw-draw-off", "a", PortFace.BOTTOM)
    attacco = catalog.resolve("dhw-draw-off").symbol.manifest.rotated(gradi).port("a")
    symbols = posa(
        project,
        catalog,
        {
            "nord": (100.0, 150.0),
            "bollitore": (200.0, 150.0),
            "presa": (
                uscita.x_mm - attacco.x_mm,
                uscita.y_mm - lungo_mm - attacco.y_mm,
            ),
        },
        rotazioni={"presa": gradi},
    )
    porte = porte_di(project, catalog, symbols)
    return (
        project,
        symbols,
        [tratta(["acs"], [dove(porte, "presa", "a"), uscita])],
    )


def test_a4_un_confine_di_rete_lontano_dal_pezzo_che_serve_e_un_rilievo() -> None:
    """Il prelievo ACS a mezzo metro dal bollitore: il difetto che A4 esiste per dire.

    E\' quello che le cinque tavole di `DRAW-015` portavano e che **nessun
    rilievo misurava**: **D-145** era un vincolo della posa, e da **D-151** la
    posa non decide piu\' — il piano scrive le coordinate. Un confine di rete
    «non ha una posizione propria e va accanto all\'utente che serve» (I-061), e
    qui l\'utente sta cinquecento millimetri piu\' in la\'.
    """
    registry = catalogo()
    project, symbols, routes = _prelievo_a(registry, 500.0)
    rilievi = organi_di_servizio_lontani(
        tavola(symbols, routes), FRAME, registry, project
    )

    assert [item.code for item in rilievi] == ["SERVICE_STUB_LONGER_THAN_ITS_MINIMUM"]
    assert rilievi[0].severity is IssueSeverity.WARNING
    detto = rilievi[0].message
    assert "presa" in detto and "bollitore" in detto
    assert "lungo 500.0 mm" in detto and "minimo su griglia e\' 10.0" in detto
    assert rilievi[0].entity_ids == ["t1", "presa", "bollitore"]


def test_a4_un_confine_di_rete_addosso_al_proprio_bollitore_non_da_rilievi() -> None:
    """Lo stesso prelievo al proprio minimo: A4 tace, e non e\' una soglia.

    E\' la meta\' che difende il controllo da se stesso: un rilievo che si accende
    comunque non dice niente. Dieci millimetri sono il minimo del motore per
    questo stacco, non un numero scelto qui.
    """
    registry = catalogo()
    project, symbols, routes = _prelievo_a(registry, 10.0)
    assert (
        organi_di_servizio_lontani(tavola(symbols, routes), FRAME, registry, project)
        == []
    )


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


CODICI = {
    "A1": "PIECE_OUTSIDE_ITS_BAND",
    "A4": "SERVICE_STUB_LONGER_THAN_ITS_MINIMUM",
    "B1": "HIGHWAY_IS_NOT_STRAIGHT",
    "B3": "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
    "B4": "INLINE_ORGAN_BREAKS_THE_RUN",
}
"""Il rilievo di ciascuna regola misurata, nell'ordine di `ORDINE_DELLE_REGOLE`."""


def test_il_raccoglitore_porta_tutte_le_regole_e_solo_avvisi() -> None:
    """`rilievi_delle_regole` e' l'unione dei controlli, e non blocca.

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
    assert set(item.code for item in rilievi) <= set(CODICI.values())


def test_il_raccoglitore_ha_un_rilievo_per_ogni_regola_dichiarata() -> None:
    """Ogni sigla di `ORDINE_DELLE_REGOLE` ha il proprio codice, e viceversa.

    E' la prova che difende l'aggancio: una regola aggiunta a `regole.py` e
    lasciata fuori dal raccoglitore — o un codice che nessuna sigla nomina —
    non si vede da nessuna parte finche' qualcuno non guarda una tavola.
    """
    assert set(ORDINE_DELLE_REGOLE) == set(CODICI)
    assert tuple(CODICI) == ORDINE_DELLE_REGOLE, "l'ordine e' quello delle sigle"


def test_a4_il_raccoglitore_porta_anche_lo_stacco_troppo_lungo() -> None:
    """Il prelievo lontano esce da `rilievi_delle_regole`, non solo dal controllo.

    E' il difetto che **D-145** vietava e che **D-151** ha reso invisibile: se
    A4 non passa di qui, il revisore e la CLI non la vedono.
    """
    registry = catalogo()
    project, symbols, routes = _prelievo_a(registry, 500.0)
    rilievi = rilievi_delle_regole(tavola(symbols, routes), FRAME, registry, project)

    assert CODICI["A4"] in {item.code for item in rilievi}
    assert all(item.severity is IssueSeverity.WARNING for item in rilievi)
