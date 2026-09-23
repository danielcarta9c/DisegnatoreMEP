"""Il pavimento di B1, e il suo metro: una tavola che il PO ha approvato.

**D-171** ha tolto a B1 il numero massimo di curve e ci ha messo un
**pavimento**: il rilievo `HIGHWAY_IS_NOT_STRAIGHT` accusa solo le pieghe **in
piu'** di quelle che le facce dei simboli impongono. Contava pero' i soli
**crocevia**, le pieghe fra due porte dello stesso pezzo, e sulla tavola 5 del
22 settembre 2026 — che il PO il 23 ha dichiarato buona (**I-108**) — accendeva
**sette rilievi falsi**. Erano tutti pieghe **fra due pezzi**: il gomito in
fondo a un collettore verticale, la L fra la terza via di una tre vie e la
serpentina del bollitore, la testa della colonna di un pettine.

Queste prove tengono insieme le due meta' del criterio che il pacchetto ha
scritto: **la tavola approvata non porta piu' rilievi di B1**, e **le pieghe che
una posa diversa toglierebbe restano accusate** — il gradino fra due porte che
si guardano, il giro largo, la U che ribaltare un pezzo raddrizza, la linea che
gira intorno a un organo in linea.
"""

# categoria: difende una regola del piano — B1, il pavimento delle facce

from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.autostrade import (
    PorteInTavola,
    autostrade_del_progetto,
    curve_imposte,
    gradini_delle_coppie,
    porte_in_tavola,
)
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.highways import (
    curve_imposte_fra_due_pezzi,
    pavimento_della_catena,
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
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.validation.regole import autostrade_storte

ROOT = Path(__file__).resolve().parents[2]
PROVE = ROOT / "docs" / "collaudi" / "DRAW-016"
RETE = "primo"

L, R, T, B = PortFace.LEFT, PortFace.RIGHT, PortFace.TOP, PortFace.BOTTOM


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(ROOT / "assets" / "symbols")


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=simboli()
    )


# ===========================================================================
# Il metro: la tavola approvata, e quella che il giorno dopo si e' raddrizzata
# ===========================================================================


def _rilievi_di_b1(scheletro: Path, piano: Path) -> list[str]:
    """Le catene che B1 accusa, eseguendo il piano come fa `disegnatore-mep piano`."""
    modello = load_project(scheletro)
    esito = esegui_piano(
        modello, carica_piano(piano), catalogo(), simboli(), ROOT / "naming"
    )
    assert esito.disegno is not None, esito.errore
    return [
        item.message
        for item in autostrade_storte(esito.disegno, catalogo(), modello)
        if item.code == "HIGHWAY_IS_NOT_STRAIGHT"
    ]


def test_la_tavola_approvata_dal_po_non_porta_rilievi_di_b1() -> None:
    """**Il criterio di chiusura, ed e' una tavola** (I-108).

    Il PO, il 23 settembre 2026, guardando l'impianto 5 ricomposto dal
    pianificatore: «la tavola va bene». Con il pavimento dei soli crocevia ne
    uscivano sette rilievi, e la sessione li aveva verificati uno per uno sul
    disegno: nessuna di quelle pieghe era una scelta di chi compone. **Un
    pavimento che accusa una tavola approvata e' sbagliato.**
    """
    prova = PROVE / "prova-camera-pulita-2026-09-22"
    assert _rilievi_di_b1(prova / "scheletro-5.json", prova / "piano-5.json") == []


def test_la_catena_che_attraversa_il_collettore_resta_accusata() -> None:
    """**Senza ammorbidire il rilievo sulle pieghe che una posa diversa toglie.**

    Il piano del 21 settembre porta la mandata dal volano alla pompa capofila
    **attraverso tutto il collettore verticale**: entra dall'alto con un gomito,
    scende, ed esce in fondo con un altro. I raccordi li passa dritti, e un
    pezzo che la catena passa dritto si gira sulla catena — quindi quei due
    gomiti non sono imposti. **Lo dimostra la tavola del giorno dopo**: con la
    capofila sulla linea principale e il collettore appeso sotto, la stessa
    catena e' una retta.
    """
    prova = PROVE / "prova-camera-pulita-2026-09-21"
    accusati = _rilievi_di_b1(prova / "scheletro-5.json", prova / "piano-5.json")
    attraverso = [
        messaggio
        for messaggio in accusati
        if "volano -> deviatrice -> cascata-mandata-b -> cascata-mandata-a -> pdc-1"
        in messaggio
    ]
    assert len(attraverso) == 1, accusati
    assert "piegano 2 volte" in attraverso[0]
    assert "ne impongono 0" in attraverso[0]


# ===========================================================================
# Le due meta' del pavimento, sulle facce
# ===========================================================================


@pytest.mark.parametrize("partenza", [L, R, T, B])
@pytest.mark.parametrize("arrivo", [L, R, T, B])
def test_fra_due_pezzi_conta_solo_l_asse(partenza: PortFace, arrivo: PortFace) -> None:
    """**Una L fra due pezzi e' imposta; una U no.**

    Spostare un pezzo non gira nessuna faccia, e ribaltarlo — lo specchio di
    D-169, il mezzo giro — la gira nella sua opposta, **sullo stesso asse**. Due
    porte su assi perpendicolari fanno una L che nessuna posa toglie; due porte
    sullo stesso asse o si guardano, o fanno una U che ribaltare uno dei due
    pezzi raddrizza.
    """
    orizzontali = {L, R}
    stesso_asse = (partenza in orizzontali) == (arrivo in orizzontali)
    assert curve_imposte_fra_due_pezzi(partenza, arrivo) == (0 if stesso_asse else 1)


def _facce(
    passi: list[tuple[tuple[str, str, PortFace], tuple[str, str, PortFace]]],
) -> tuple[tuple[tuple[PortRef, PortRef], ...], dict[tuple[str, str], PortFace]]:
    """Una catena scritta a mano: per ogni tratta, porta d'ingresso e d'uscita
    con la faccia su cui guardano."""
    steps: list[tuple[PortRef, PortRef]] = []
    facce: dict[tuple[str, str], PortFace] = {}
    for (pezzo_a, porta_a, faccia_a), (pezzo_b, porta_b, faccia_b) in passi:
        steps.append(
            (
                PortRef(component_id=pezzo_a, port_id=porta_a),
                PortRef(component_id=pezzo_b, port_id=porta_b),
            )
        )
        facce[(pezzo_a, porta_a)] = faccia_a
        facce[(pezzo_b, porta_b)] = faccia_b
    return tuple(steps), facce


def _pavimento(
    passi: list[tuple[tuple[str, str, PortFace], tuple[str, str, PortFace]]],
) -> int | None:
    steps, facce = _facce(passi)
    return pavimento_della_catena(
        steps, lambda ref: facce.get((ref.component_id, ref.port_id))
    )


def test_il_gomito_in_fondo_al_collettore_e_imposto() -> None:
    """L'ultima pompa ha l'attacco sul fianco, il collettore scende verticale: la
    tratta fra i due e' una L, ed e' `m6` e `m9` della tavola approvata."""
    assert _pavimento([(("pdc-3", "water_supply", R), ("collettore", "a", B))]) == 1


def test_la_linea_che_gira_intorno_a_un_passaggio_dritto_non_e_imposta() -> None:
    """**La linea passa, non si piega intorno a lui** (B4).

    Un raccordo di traverso sulla linea: entra dall'alto ed esce dal basso,
    mentre la pompa e il volano si guardano in orizzontale. Contate tratta per
    tratta sarebbero due L; ma un pezzo che la catena passa dritto si gira sulla
    catena, e allora la catena e' una retta. Il pavimento e' **zero**.
    """
    assert (
        _pavimento(
            [
                (("pompa", "water_supply", R), ("raccordo", "a", T)),
                (("raccordo", "b", B), ("volano", "primary_in", L)),
            ]
        )
        == 0
    )


def test_l_anello_che_torna_sul_proprio_pezzo_resta_com_e_posato() -> None:
    """L'anello del ricircolo della tavola approvata: dal bollitore sale
    all'innesto, lo passa dritto, gira alla presa e **torna sull'innesto**.

    L'innesto e' toccato due volte, quindi non si gira per una sola: resta
    fisso, e il pavimento e' **tre** — la curva della presa e le due L. E' la
    catena `m28 + m29 + m30`, che piega tre volte.
    """
    assert (
        _pavimento(
            [
                (("bollitore", "dhw_out", T), ("innesto", "a", B)),
                (("innesto", "b", T), ("presa", "a", L)),
                (("presa", "c", B), ("innesto", "c", R)),
            ]
        )
        == 3
    )


def test_una_porta_che_la_posa_non_colloca_non_da_un_pavimento() -> None:
    """Un pavimento a meta' non e' un pavimento."""
    steps, _ = _facce([(("pompa", "water_supply", R), ("volano", "primary_in", L))])
    assert pavimento_della_catena(steps, lambda ref: None) is None


# ===========================================================================
# Il gomito, sulla tavola
# ===========================================================================


def _tubo(identifier: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
    return ConnectionModel(
        id=identifier,
        network_id=RETE,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _impianto(
    components: list[tuple[str, str]], connections: list[ConnectionModel]
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-pavimento",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 23),
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


def _posa(
    project: ProjectModel,
    origini: dict[str, tuple[float, float]],
    giaciture: dict[str, tuple[int, bool]] | None = None,
) -> list[PlacedSymbol]:
    scelte = giaciture or {}
    definizioni = {item.id: item.definition_id for item in project.components}
    posati: list[PlacedSymbol] = []
    for component_id, (x_mm, y_mm) in origini.items():
        gradi, specchio = scelte.get(component_id, (0, False))
        manifesto = catalogo().resolve(definizioni[component_id]).symbol.manifest
        girato = manifesto.rotated(gradi, specchio)
        posati.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=manifesto.id,
                rotation_deg=gradi,
                specchiato=specchio,
                origin=Point(x_mm=x_mm, y_mm=y_mm),
                width_mm=girato.width_mm,
                height_mm=girato.height_mm,
            )
        )
    return posati


def _porte(project: ProjectModel, symbols: list[PlacedSymbol]) -> PorteInTavola:
    return porte_in_tavola(
        SheetGeometry(sheet_id="t1", title="Prova", symbols=symbols), project, catalogo()
    )


def _tratta(connection_ids: list[str], *punti: Point) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=RETE,
        medium="heating_water",
        connection_ids=connection_ids,
        segments=[list(punti)],
    )


def _tavola(symbols: list[PlacedSymbol], routes: list[RoutedTrunk]) -> DrawingGeometry:
    return DrawingGeometry(
        project_id="prova",
        sheets=[SheetGeometry(sheet_id="t1", title="Prova", symbols=symbols, routes=routes)],
    )


def _due_pompe_su_un_volano() -> ProjectModel:
    """La capofila sulla linea principale, la seconda appesa sotto al raccordo."""
    return _impianto(
        [
            ("capofila", "heat-pump-air-water"),
            ("seconda", "heat-pump-air-water"),
            ("unione", "tee-junction"),
            ("volano", "buffer-four-port"),
        ],
        [
            _tubo("p1", ("capofila", "water_supply"), ("unione", "a")),
            _tubo("p2", ("seconda", "water_supply"), ("unione", "c")),
            _tubo("p3", ("unione", "b"), ("volano", "primary_in")),
        ],
    )


# Il raccordo specchiato e girato di mezzo giro: `a` a sinistra, `b` a destra,
# `c` **in basso**, verso la seconda pompa. Le coordinate si leggono dal
# manifesto: pompa 40x30 con la mandata a destra a +5, raccordo 5x5, volano
# 25x45 con `primary_in` a sinistra a +5.
_ORIGINI = {
    "capofila": (0.0, 0.0),
    "seconda": (0.0, 45.0),
    "unione": (60.0, 2.5),
    "volano": (100.0, 0.0),
}
_UNIONE_IN_BASSO = {"unione": (180, True)}


def _il_collettore(project: ProjectModel, giro_largo: bool) -> DrawingGeometry:
    symbols = _posa(project, _ORIGINI, _UNIONE_IN_BASSO)
    porte = _porte(project, symbols)

    def dove(pezzo: str, porta: str) -> Point:
        return porte[(pezzo, porta)][0]

    mandata, ramo = dove("seconda", "water_supply"), dove("unione", "c")
    if giro_largo:
        # Dalla seconda pompa si va oltre il raccordo e si torna indietro:
        # tre pieghe dove la L ne chiede una.
        giro = [
            mandata,
            Point(x_mm=80.0, y_mm=mandata.y_mm),
            Point(x_mm=80.0, y_mm=30.0),
            Point(x_mm=ramo.x_mm, y_mm=30.0),
            ramo,
        ]
    else:
        giro = [mandata, Point(x_mm=ramo.x_mm, y_mm=mandata.y_mm), ramo]
    routes = [
        _tratta(["p1"], dove("capofila", "water_supply"), dove("unione", "a")),
        _tratta(["p2"], *giro),
        _tratta(["p3"], dove("unione", "b"), dove("volano", "primary_in")),
    ]
    return _tavola(symbols, routes)


def test_sulla_tavola_il_gomito_in_fondo_al_collettore_non_e_un_rilievo() -> None:
    """La seconda pompa entra nel raccordo da sotto con una L: e' la forma.

    Prima del 23 settembre 2026 questa tavola dava un rilievo — «piega 1 volta,
    e i simboli ne impongono 0» — ed era il caso di `m6` e `m9` sulla tavola che
    il PO ha approvato.
    """
    project = _due_pompe_su_un_volano()
    disegno = _il_collettore(project, giro_largo=False)
    assert autostrade_storte(disegno, catalogo(), project) == []


def test_sulla_tavola_il_giro_largo_resta_un_rilievo() -> None:
    """La stessa L, fatta andando oltre il raccordo e tornando: due pieghe in piu'."""
    project = _due_pompe_su_un_volano()
    disegno = _il_collettore(project, giro_largo=True)
    rilievi = autostrade_storte(disegno, catalogo(), project)
    assert [item.code for item in rilievi] == ["HIGHWAY_IS_NOT_STRAIGHT"]
    assert "piega 3 volte" in rilievi[0].message
    assert "ne impone 1" in rilievi[0].message
    assert "2 di troppo" in rilievi[0].message


# ===========================================================================
# Il gradino della coppia: interasse 15 contro 10
# ===========================================================================


def _volano_e_radiatori() -> ProjectModel:
    return _impianto(
        [
            ("volano", "buffer-four-port"),
            ("radiatori", "radiator"),
        ],
        [
            _tubo("s1", ("volano", "secondary_out"), ("radiatori", "in")),
            _tubo("s2", ("radiatori", "out"), ("volano", "secondary_in")),
        ],
    )


def _la_coppia(radiatori_y_mm: float) -> tuple[ProjectModel, DrawingGeometry]:
    """Il volano ha la coppia a **15**, il radiatore a **10** (D-167): le due
    linee sono rette insieme solo se le porte stanno alla stessa distanza, e non
    ci stanno. Ogni linea che non trova la propria quota fa un gradino a meta'
    strada."""
    project = _volano_e_radiatori()
    symbols = _posa(project, {"volano": (0.0, 0.0), "radiatori": (60.0, radiatori_y_mm)})
    porte = _porte(project, symbols)

    def linea(connessione: str, da: tuple[str, str], a: tuple[str, str]) -> RoutedTrunk:
        qui, la = porte[da][0], porte[a][0]
        if qui.y_mm == la.y_mm:
            return _tratta([connessione], qui, la)
        return _tratta(
            [connessione],
            qui,
            Point(x_mm=40.0, y_mm=qui.y_mm),
            Point(x_mm=40.0, y_mm=la.y_mm),
            la,
        )

    routes = [
        linea("s1", ("volano", "secondary_out"), ("radiatori", "in")),
        linea("s2", ("radiatori", "out"), ("volano", "secondary_in")),
    ]
    return project, _tavola(symbols, routes)


def test_il_gradino_che_la_coppia_deve_fare_non_e_un_rilievo() -> None:
    """La mandata dritta e il ritorno che scende di 5 mm: il gradino e' della
    coppia, e nessuna posa lo toglie. E' il ritorno dei radiatori
    dell'impianto 1 composto a mano."""
    project, disegno = _la_coppia(radiatori_y_mm=2.5)
    assert autostrade_storte(disegno, catalogo(), project) == []

    autostrade = autostrade_del_progetto(project, catalogo())
    sheet = disegno.sheets[0]
    porte = porte_in_tavola(sheet, project, catalogo())
    assert all(curve_imposte(item, porte) == 0 for item in autostrade)
    assert sorted(gradini_delle_coppie(autostrade, sheet.routes, porte).values()) == [2]


def test_se_la_coppia_fa_due_gradini_uno_e_di_troppo() -> None:
    """Il radiatore a una quota che non allinea nessuna delle due: due gradini,
    e la coppia ne chiede uno. **Un rilievo solo**, e non due."""
    project, disegno = _la_coppia(radiatori_y_mm=5.0)
    rilievi = autostrade_storte(disegno, catalogo(), project)
    assert [item.code for item in rilievi] == ["HIGHWAY_IS_NOT_STRAIGHT"]
    assert "2 di troppo" in rilievi[0].message


def test_con_lo_stesso_interasse_nessun_gradino_e_imposto() -> None:
    """Due macchine con la coppia a 15 su quote diverse: tutt'e due le linee
    fanno un gradino, e **tutt'e due sono di chi ha posato** — basta metterle
    allo stesso y."""
    project = _impianto(
        [("pompa", "heat-pump-air-water"), ("volano", "buffer-four-port")],
        [
            _tubo("p1", ("pompa", "water_supply"), ("volano", "primary_in")),
            _tubo("p2", ("volano", "primary_out"), ("pompa", "water_return")),
        ],
    )
    symbols = _posa(project, {"pompa": (0.0, 0.0), "volano": (80.0, 10.0)})
    porte = _porte(project, symbols)

    def gradino(connessione: str, da: tuple[str, str], a: tuple[str, str]) -> RoutedTrunk:
        qui, la = porte[da][0], porte[a][0]
        return _tratta(
            [connessione],
            qui,
            Point(x_mm=60.0, y_mm=qui.y_mm),
            Point(x_mm=60.0, y_mm=la.y_mm),
            la,
        )

    routes = [
        gradino("p1", ("pompa", "water_supply"), ("volano", "primary_in")),
        gradino("p2", ("volano", "primary_out"), ("pompa", "water_return")),
    ]
    rilievi = autostrade_storte(_tavola(symbols, routes), catalogo(), project)
    assert len(rilievi) == 2
    assert all("2 di troppo" in item.message for item in rilievi)
