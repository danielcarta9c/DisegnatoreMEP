"""Le prove di DRAW-012: il motore disegna nell'ordine del disegnatore.

Il PO, il 16 settembre 2026, guardando la tavola 4:

    «E' inutile che continuiamo a ottimizzare un motore di disegno che se non
    ragiona bene in questo ordine e non ha regole per fare queste cose: stiamo
    ottimizzando la punta di una lancia storta.»

Il pacchetto cambia **l'ordine delle decisioni**, e qui si prova che l'ordine
nuovo e' quello, non che una taratura e' migliorata:

- **che cosa e' autostrada** (§B): dai generatori — **tutti** — agli accumuli e
  agli scambiatori, passando per i collettori e le tre vie; e sempre le linee
  che dagli accumuli vanno ai circolatori e da li' alla distribuzione, piu'
  l'uscita ACS;
- **l'autostrada intera** (§C): un oggetto, non una catena di frammenti, con
  l'invariante verificato su di lui — e' la prova che mancava, ed e' il motivo
  per cui il difetto della tavola 4 non si vedeva;
- **il costo** (§D): la lunghezza esce, il riempimento entra come **finestra**,
  e non si legge mai senza la copertura dell'ingombro.

Gli impianti veri si guardano dove il pacchetto li nomina — le fixture di
`examples/prova` — e i casi generali si costruiscono qui, con il catalogo di
prova, perche' una regola provata su una sola tavola e' una coincidenza.
"""

from collections.abc import Callable
from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import compose
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import Point
from disegnatore_mep.layout.hierarchy import (
    Level,
    hierarchy_of,
    spine_machines,
    user_machines,
)
from disegnatore_mep.layout.highways import Highway, highways, lies_in_line
from disegnatore_mep.layout.improve import FILL_WINDOW, SheetCost
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

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
PROVE = ROOT / "examples" / "prova"

TAVOLA_2 = PROVE / "prova-2-pdc-deviatrice-acs.json"
TAVOLA_4 = PROVE / "prova-4-ibrido-pdc-caldaia.json"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


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
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-ordine",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 17),
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
            SubsystemModel(
                id="tutto",
                name="tutto",
                component_ids=[item for item, _, _ in components],
                network_ids=[network_id for network_id, _ in networks],
            )
        ],
    )


def _runs(project: ProjectModel) -> list[Trunk]:
    return build_trunks(project, inline_component_ids(project, catalog()))


def _levels(project: ProjectModel) -> dict[tuple[str, ...], Level]:
    return hierarchy_of(project, catalog(), _runs(project))


def _key(project: ProjectModel, *connection_ids: str) -> tuple[str, ...]:
    """La tratta che porta quelle connessioni: una tratta ne puo' portare piu'
    d'una, perche' gli accessori in linea la spezzano nel modello e non nel
    disegno."""
    wanted = set(connection_ids)
    found = [
        item.connection_ids for item in _runs(project) if wanted <= set(item.connection_ids)
    ]
    assert len(found) == 1, f"{connection_ids}: {found}"
    return found[0]


# ---------------------------------------------------------------------------
# §B — che cosa e' autostrada, e chi lo decide
# ---------------------------------------------------------------------------


def due_generatori_e_un_collettore() -> ProjectModel:
    """Il caso generale di §B.1 e §B.3: due generatori che confluiscono su un
    collettore, con una tre vie sulla mandata del secondo, e un accumulo."""
    return _plant(
        [("primo", HEATING)],
        [
            ("generatore-a", "heat-pump-air-water", "PDC-01"),
            ("generatore-b", "gas-boiler", "CAL-01"),
            ("tre-vie", "diverting-valve-3way", "VD-01"),
            ("scambiatore", "plate-heat-exchanger", "SCA-01"),
            ("collettore", "tee-junction", None),
            ("ritorno", "tee-split", None),
            ("accumulo", "buffer-four-port", "VOL-01"),
        ],
        [
            _pipe("p1", "primo", ("generatore-a", "water_supply"), ("collettore", "a")),
            _pipe("p2", "primo", ("generatore-b", "water_supply"), ("tre-vie", "in")),
            _pipe("p3", "primo", ("tre-vie", "out_a"), ("collettore", "c")),
            _pipe("p4", "primo", ("tre-vie", "out_b"), ("scambiatore", "primary_in")),
            _pipe("p5", "primo", ("collettore", "b"), ("accumulo", "primary_in")),
            _pipe("p6", "primo", ("accumulo", "primary_out"), ("ritorno", "a")),
            _pipe("p7", "primo", ("ritorno", "b"), ("generatore-a", "water_return")),
            _pipe("p8", "primo", ("ritorno", "c"), ("generatore-b", "water_return")),
            _pipe("p9", "primo", ("scambiatore", "primary_out"), ("generatore-b", "water_return")),
        ][:8],
    )


def accumulo_circolatore_e_terminali() -> ProjectModel:
    """Il caso generale di §B.2: dall'accumulo, attraverso il circolatore, ai
    terminali — e l'uscita ACS accanto all'ingresso dell'acqua fredda."""
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("generatore", "heat-pump-air-water", "PDC-01"),
            ("accumulo", "buffer-combined", "ACC-01"),
            ("circolatore", "pump-circulator", "CIR-01"),
            ("terminali", "radiator", "RAD-01"),
            ("acquedotto", "cold-water-inlet", "AF-01"),
            ("utenze", "dhw-draw-off", "ACS-01"),
        ],
        [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("accumulo", "primary_in")),
            _pipe("p2", "primo", ("accumulo", "primary_out"), ("generatore", "water_return")),
            _pipe("s1", "secondo", ("accumulo", "secondary_out"), ("circolatore", "a")),
            _pipe("s2", "secondo", ("circolatore", "b"), ("terminali", "in")),
            _pipe("s3", "secondo", ("terminali", "out"), ("accumulo", "secondary_in")),
            _pipe("w1", "fredda", ("acquedotto", "a"), ("accumulo", "cold_in")),
            _pipe("w2", "calda", ("accumulo", "dhw_out"), ("utenze", "a")),
        ],
    )


def test_ogni_generatore_ha_la_propria_autostrada() -> None:
    """§B.3 — con piu' generatori le autostrade sono piu' d'una, e nessuno e'
    eletto. Il caso generale, e poi l'impianto 4, dove il difetto si vedeva."""
    project = due_generatori_e_un_collettore()
    assert spine_machines(project, catalog()) == frozenset(
        {"generatore-a", "generatore-b", "scambiatore", "accumulo"}
    )
    levels = _levels(project)
    for connection_id in ("p1", "p2", "p7", "p8"):
        assert levels[_key(project, connection_id)] is Level.AUTOSTRADA, connection_id

    impianto = load_project(TAVOLA_4)
    suoi = hierarchy_of(impianto, catalog(), _runs(impianto))
    # La mandata della pompa di calore e quella della caldaia: tutt'e due.
    # Prima di DRAW-012 lo era la sola caldaia, e l'analisi del 16 settembre lo
    # ha misurato (`2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md` §3.3).
    assert suoi[_key(impianto, "p1")] is Level.AUTOSTRADA
    assert suoi[_key(impianto, "p3")] is Level.AUTOSTRADA
    assert suoi[_key(impianto, "p8")] is Level.AUTOSTRADA
    assert suoi[_key(impianto, "p12")] is Level.AUTOSTRADA


def test_un_collettore_in_mezzo_non_interrompe_ne_declassa() -> None:
    """§B.1 — «un collettore o una tre vie in mezzo non interrompe l'autostrada
    e non la declassa». Il collettore e la tre vie stanno **dentro** la catena,
    e le tratte che li toccano restano di rango massimo."""
    project = due_generatori_e_un_collettore()
    levels = _levels(project)
    attraverso = ("p1", "p3", "p5", "p6", "p7", "p8")
    assert all(levels[_key(project, item)] is Level.AUTOSTRADA for item in attraverso)
    # E non sono frammenti sciolti: la catena li unisce da un generatore
    # all'accumulo passando per il collettore.
    catene = highways(project, catalog(), _runs(project))
    lunga = max(catene, key=lambda item: len(item.steps))
    assert len(lunga.steps) >= 2
    assert "collettore" in lunga.component_ids or "tre-vie" in lunga.component_ids


def test_dall_accumulo_al_circolatore_e_ai_terminali_e_autostrada() -> None:
    """§B.2 e §A.2 — «sempre» le linee che dagli accumuli vanno ai circolatori e
    da li' alla distribuzione, e l'uscita ACS. L'ingresso dell'acqua fredda no:
    resta uno stacco di servizio della fase del corredo."""
    project = accumulo_circolatore_e_terminali()
    assert user_machines(project, catalog()) == frozenset({"terminali", "utenze"})
    levels = _levels(project)
    # Il circolatore sta **dentro** la tratta: e' un accessorio in linea.
    mandata = _key(project, "s1", "s2")
    assert levels[mandata] is Level.AUTOSTRADA
    assert levels[_key(project, "s3")] is Level.AUTOSTRADA
    assert levels[_key(project, "w2")] is Level.AUTOSTRADA
    assert levels[_key(project, "w1")] is Level.DISTRIBUZIONE


def test_sulla_tavola_2_la_distribuzione_e_l_acs_sono_autostrada() -> None:
    """Criterio 1 del pacchetto, sulle tre tratte che il PM ha nominato una per
    una: oggi non lo erano, e cadevano in ultima fase insieme agli stacchi dei
    vasi di espansione."""
    project = load_project(TAVOLA_2)
    levels = hierarchy_of(project, catalog(), _runs(project))
    assert levels[_key(project, "s1", "s2")] is Level.AUTOSTRADA
    assert levels[_key(project, "s3")] is Level.AUTOSTRADA
    assert levels[_key(project, "w2")] is Level.AUTOSTRADA


# ---------------------------------------------------------------------------
# §C — l'autostrada e' un oggetto intero, non una catena di frammenti
# ---------------------------------------------------------------------------


Attacco = tuple[str, str]


def _laid(
    places: dict[Attacco, tuple[float, float]], faces: dict[Attacco, PortFace]
) -> Callable[[str, str], tuple[Point, PortFace] | None]:
    """Una lettura delle porte scritta a mano, per provare l'invariante senza
    passare da una posa vera: `lies_in_line` prende proprio questa firma."""

    def at(component_id: str, port_id: str) -> tuple[Point, PortFace] | None:
        if (component_id, port_id) not in faces:
            return None
        x_mm, y_mm = places[(component_id, port_id)]
        return (Point(x_mm=x_mm, y_mm=y_mm), faces[(component_id, port_id)])

    return at


def _catena_di_due() -> Highway:
    """Una catena di due tratte che si incontrano su un raccordo."""
    return Highway(
        keys=(("uno",), ("due",)),
        steps=(
            (
                PortRef(component_id="macchina", port_id="out"),
                PortRef(component_id="raccordo", port_id="a"),
            ),
            (
                PortRef(component_id="raccordo", port_id="b"),
                PortRef(component_id="accumulo", port_id="in"),
            ),
        ),
    )


def test_la_catena_intera_e_una_retta_e_ogni_frammento_non_basta() -> None:
    """Criterio 4 — **la prova che mancava**.

    I due frammenti sono dritti tutt'e due: dalla macchina al raccordo, e dal
    raccordo all'accumulo. L'invariante di sempre — «ogni tratta e' un
    rettilineo» — li approva entrambi, e su un frammento di cinque millimetri
    li approverebbe comunque. La catena intera pero' fa un gomito sul raccordo,
    ed e' quella la forma che il PO guarda.
    """
    faces = {
        ("macchina", "out"): PortFace.RIGHT,
        ("raccordo", "a"): PortFace.LEFT,
        ("raccordo", "b"): PortFace.RIGHT,
        ("accumulo", "in"): PortFace.LEFT,
    }
    dritta = {
        ("macchina", "out"): (0.0, 100.0),
        ("raccordo", "a"): (50.0, 100.0),
        ("raccordo", "b"): (55.0, 100.0),
        ("accumulo", "in"): (120.0, 100.0),
    }
    assert lies_in_line(_catena_di_due(), _laid(dritta, faces))

    # Ogni frammento resta dritto — la porta `b` del raccordo esce comunque a
    # destra e arriva a una porta che la guarda — ma la catena cambia quota:
    # e' un gomito, e nessun invariante di tratta se ne accorgeva.
    storta = dict(dritta)
    storta[("raccordo", "b")] = (55.0, 130.0)
    storta[("accumulo", "in")] = (120.0, 130.0)
    at = _laid(storta, faces)
    catena = _catena_di_due()
    for entry, exit_ in catena.steps:
        here = at(entry.component_id, entry.port_id)
        there = at(exit_.component_id, exit_.port_id)
        assert here is not None and there is not None
        # Il frammento e' dritto: facce opposte, stessa quota, verso giusto.
        assert there[1] is here[1].opposite
        assert here[0].y_mm == there[0].y_mm
    assert not lies_in_line(catena, at)


def test_l_autostrada_intera_esiste_e_attraversa_i_propri_crocevia() -> None:
    """Criterio 4 — l'oggetto c'e', e sull'impianto 4 unisce i pezzi che il PO
    nomina: dal generatore all'accumulo **attraverso** il collettore."""
    project = load_project(TAVOLA_4)
    catene = highways(project, catalog(), _runs(project))
    assert catene
    levels = hierarchy_of(project, catalog(), _runs(project))
    autostrade = {
        item.connection_ids
        for item in _runs(project)
        if levels[item.connection_ids] is Level.AUTOSTRADA
    }
    # Ogni autostrada sta in **una sola** catena: due catene che si
    # sovrappongono pretenderebbero due rette diverse per lo stesso tratto.
    presi = [key for item in catene for key in item.keys]
    assert sorted(presi) == sorted(autostrade)
    assert len(presi) == len(set(presi))
    # E almeno una catena attraversa davvero un crocevia.
    assert any(len(item.steps) > 1 for item in catene)


# ---------------------------------------------------------------------------
# §D — i millimetri escono dal costo, il riempimento entra come finestra
# ---------------------------------------------------------------------------


def _cost(**overrides: float) -> SheetCost:
    base: dict[str, float] = dict(
        violations=0,
        turnback_runs=0,
        turnback_mm=0.0,
        long_runs=0,
        bends=4,
        crossings=1,
        margin_gap=0.0,
        fill=0.55,
        coverage=0.80,
        imbalance=2.0,
        length_mm=500.0,
    )
    base.update(overrides)
    return SheetCost(**base)  # type: ignore[arg-type]


def test_la_lunghezza_non_entra_piu_nel_confronto() -> None:
    """Criterio 5 — due pose che differiscono **solo** per la lunghezza sono
    indifferenti. Il PO (D-139): «i mm non sono un vero parametro»."""
    corta = _cost(length_mm=100.0)
    lunga = _cost(length_mm=900.0)
    assert not corta.beats(lunga)
    assert not lunga.beats(corta)
    assert corta.key() == lunga.key()
    # E resta nella tupla: si riporta come misura, non come giudizio.
    assert "length_mm" in SheetCost._fields
    assert corta.length_mm == 100.0


def test_il_riempimento_non_entra_piu_nel_confronto() -> None:
    """**D-149** — due pose che differiscono solo per il riempimento sono
    indifferenti, esattamente come per la lunghezza con D-139.

    Fino al 19 settembre 2026 questa prova si chiamava
    `test_il_riempimento_e_una_finestra_non_una_scala` e pretendeva l'opposto:
    dentro la finestra si vinceva. **Non e' stata allentata — la disposizione
    che difendeva e' stata revocata dal PO**, che ha guardato le tavole: «ha
    dato solo risultati peggiori. Prima il disegno era meglio.»
    """
    basso, alto = FILL_WINDOW
    dentro = _cost(fill=(basso + alto) / 2)
    vuota = _cost(fill=basso - 0.15)
    stretta = _cost(fill=alto + 0.15)
    assert not dentro.beats(vuota)
    assert not vuota.beats(dentro)
    assert not dentro.beats(stretta)
    assert not stretta.beats(dentro)
    assert dentro.key() == vuota.key() == stretta.key()
    # E resta nella tupla: si riporta come misura, non come giudizio.
    assert "fill" in SheetCost._fields
    assert dentro.fill == (basso + alto) / 2


def test_la_copertura_esce_con_il_riempimento_che_sorvegliava() -> None:
    """**D-149** — la copertura dell'ingombro era la guardia del riempimento
    (D-141) e non ha senso da sola: sorvegliava un obiettivo che non c'e' piu'.

    Il trucco che D-141 nominava — spingere un pezzo in un angolo perche' il
    rettangolo dell'inchiostro cresca — **non ha piu' niente da comprare**:
    non c'e' nessuna voce che quel gonfiore faccia migliorare.
    """
    onesta = _cost(fill=0.30, coverage=0.80)
    trucco = _cost(fill=0.50, coverage=0.45)
    assert not trucco.beats(onesta)
    assert not onesta.beats(trucco)
    assert onesta.key() == trucco.key()
    # Resta come misura, e la voce che la calcolava e' ancora leggibile.
    assert "coverage" in SheetCost._fields
    assert trucco.coverage == 0.45


def test_il_margine_dal_bordo_resta_e_decide() -> None:
    """**D-143 non e' toccata da D-149**, ed e' la differenza fra le due.

    Il riempimento era un numero che il PO non aveva mai chiesto di inseguire;
    il margine gliel'ha chiesto lui guardando la tavola — «non si mettono gli
    oggetti cosi' vicini al bordo del foglio». Quindi esce l'uno e resta
    l'altro, e la chiave lo dimostra.
    """
    comoda = _cost(margin_gap=0.0, fill=0.05)
    al_bordo = _cost(margin_gap=12.0, fill=0.55)
    assert comoda.beats(al_bordo)
    assert not al_bordo.beats(comoda)


def test_l_ordine_delle_voci_e_quello_di_D_139_e_D_149() -> None:
    """Prima le curve, poi gli attraversamenti, poi il margine. E **ne' la
    lunghezza ne' il riempimento** entrano nella chiave."""
    assert SheetCost._fields[:6] == (
        "violations",
        "turnback_runs",
        "turnback_mm",
        "long_runs",
        "bends",
        "crossings",
    )
    # Una tavola con una curva in meno vince, per lunga e vuota che sia.
    assert _cost(bends=3, fill=0.05, coverage=0.2, length_mm=9999.0).beats(
        _cost(bends=4, fill=0.55, coverage=1.0, length_mm=1.0)
    )
    # A parita' di curve, un attraversamento in meno vince.
    assert _cost(crossings=0, fill=0.05, coverage=0.2).beats(
        _cost(crossings=1, fill=0.55, coverage=1.0)
    )
    # La chiave ha otto voci: le sei sopra, il margine, lo spareggio. Nove
    # erano prima di D-149, e la nona era il riempimento.
    assert len(_cost().key()) == 8


# ---------------------------------------------------------------------------
# §F — l'ultima spiaggia: si cede una curva, non si butta la struttura
# ---------------------------------------------------------------------------


def test_il_ciclo_senza_le_fasi_e_l_ultimissima_rete_e_la_cessione_viene_prima() -> None:
    """§F.1 — il ripiego che scarta le fasi non e' piu' il terzo, e' l'ultimo.

    Prima di `DRAW-012` `compose_sheet` ripiegava in quattro passi e il terzo
    era «il ciclo senza le fasi, cioe' la tavola che sarebbe uscita prima di
    DRAW-008»: l'impianto 4 usciva da li'. Adesso fra la posa seminata e quella
    rete c'e' la **cessione graduale**, e la rete che scarta le fasi e' la
    penultima via — dopo di lei resta solo la disposizione di partenza.
    """
    sorgente = Path(compose.__file__).read_text(encoding="utf-8")
    fasi = sorgente.index('("le fasi"')
    seminata = sorgente.index('"la posa seminata dal tronco"')
    cessione = sorgente.index('"la cessione graduale')
    senza = sorgente.index('"il ciclo senza le fasi')
    partenza = sorgente.index('"la disposizione di partenza"')
    assert fasi < seminata < cessione < senza < partenza
    # E la cessione e' limitata da un tetto dichiarato, come gli instradamenti
    # di prova: un ciclo di miglioramento per catena non e' gratis.
    assert isinstance(compose.MAX_SURRENDERS, int)
    assert compose.MAX_SURRENDERS > 0


def test_si_cede_prima_a_chi_ne_ha_meno_bisogno_e_solo_a_chi_si_sta_tenendo() -> None:
    """§F.3 — l'ordine della resa, e chi ne resta fuori.

    Fuori restano le catene che la posa **non tiene gia' dritte**: su di loro
    l'invariante non vincola niente — e' monotono — e cederle sarebbe un ciclo
    intero speso per non cambiare nulla.
    """
    def catena(name: str, passi: int) -> Highway:
        steps = tuple(
            (
                PortRef(component_id=f"{name}-{index}", port_id="a"),
                PortRef(component_id=f"{name}-{index + 1}", port_id="b"),
            )
            for index in range(passi)
        )
        return Highway(keys=tuple((f"{name}{index}",) for index in range(passi)), steps=steps)

    corta = catena("corta", 1)
    lunga = catena("lunga", 3)
    impossibile = catena("impossibile", 4)
    storta = catena("storta", 1)
    ordine = compose._order_of_surrender(
        (lunga, corta, impossibile, storta),
        frozenset({("impossibile0",)}),
        {},
        lambda item: item is not storta,
    )
    # Prima quella che nessuna posa raddrizza, poi la piu' corta, poi la lunga.
    assert [item.keys[0][0] for item in ordine] == ["impossibile0", "corta0", "lunga0"]
    assert storta not in ordine


def test_il_diario_dice_con_quale_via_la_tavola_e_uscita() -> None:
    """§F.3 e criterio 9 — un ripiego silenzioso e' come la tavola 4 e' arrivata
    in revisione senza che nessuna misura se ne accorgesse."""
    project = load_project(TAVOLA_2)
    journal = compose.ComposeJournal()
    frame, drawing = compose.compose_on_ordinary_frame(
        project, catalog(), journal=journal
    )
    assert len(journal.notes) == len(drawing.sheets)
    nota = journal.notes[0]
    assert nota.sheet_id == drawing.sheets[0].sheet_id
    assert nota.ripiego
    assert nota.highways > 0
    # Il pacchetto chiede che **nessun impianto** esca dal ripiego che scarta le
    # fasi: sulla tavola 2 non ci esce, e il diario e' il posto in cui si legge.
    assert "senza le fasi" not in nota.ripiego
