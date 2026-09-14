"""La traslazione di blocco: le prove di DRAW-009 §B.

Il PO, il 12 settembre 2026, correggendo la lettura che DRAW-008 aveva adottato:

    il tronco e' un **corpo rigido, non un corpo immobile**. Trasla tutto
    intero, si allunga lungo il proprio asse, e porta con se' cio' che gli sta
    appeso. Se il corredo dell'ACS non sta sotto, si alzano PDC e puffer.

Fino a DRAW-008 il ciclo non aveva quella mossa, e non e' una sfumatura: nessuna
delle mosse esistenti fa la stessa cosa. `_shift_moves` sposta un gruppo per una
relazione gia' esistente sul foglio; `_column_moves` sposta una colonna;
`_stretch_moves` taglia il foglio a meta' di una tratta e pretende che una parte
resti ferma — allontana, non trasla. Nessuna prende un insieme di pezzi
**allineati** e lo sposta tutto intero insieme a tutto cio' che deve seguirlo.

Quattro cose si provano qui, e sono i criteri 5, 6 e 7 del pacchetto:

- la mossa **esiste**, e vince dove nessuna mossa esistente vince;
- il blocco **non si deforma**: dopo la traslazione ogni distanza interna al
  blocco e' quella di prima;
- se un pezzo **non puo' seguire**, la mossa non si fa — e non si fa a meta';
- una traslazione che **piega il tronco** e' rifiutata da `is_valid` anche
  quando batte la chiave di costo.
"""

from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol, Point
from disegnatore_mep.layout.improve import BLOCK_STEPS, Improver, Move
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import SpineLayout, carry_the_rest, lay_the_spine
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
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
TOLERANCE_MM = 1e-6


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


def tronco_con_corredo_sotto() -> ProjectModel:
    """Il banco: un tronco con il proprio corredo appeso **sotto**, e un utente
    che sta sotto anche lui.

    E' la forma dell'impianto 2 ridotta all'osso, e ne conserva l'unica cosa che
    conta per questa mossa: fra il tronco e il bollitore c'e' una fascia
    occupata da cio' che dal tronco **pende** — qui il vaso di espansione. La
    tratta che porta al bollitore deve attraversare quella fascia, e il vaso e'
    dove la attraverserebbe. Nessuna mossa che sposti un pezzo per volta apre
    quel passaggio: spostare il vaso lascia il raccordo che lo regge, spostare
    il raccordo piega il tronco. Il passaggio si apre **alzando il tronco tutto
    intero, vaso compreso**, ed e' la traslazione di blocco.

    Niente acqua fredda e niente sanitario: il banco prova una mossa della posa,
    e due reti in piu' proverebbero soltanto che il banco e' grande.
    """
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="blocco",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 13),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id="primo", name="primo", domain="hydronic", medium=HEATING),
        ],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water", tag="PDC-01"),
            ComponentInstance(id="deviatrice", definition_id="diverting-valve-3way", tag="VD-01"),
            ComponentInstance(id="serbatoio", definition_id="buffer-four-port", tag="VOL-01"),
            ComponentInstance(id="bollitore", definition_id="dhw-cylinder", tag="BOL-01"),
            ComponentInstance(id="ritorno", definition_id="tee-junction", tag=None),
            ComponentInstance(id="stacco-vaso", definition_id="tee-branch", tag=None),
            ComponentInstance(id="vaso", definition_id="expansion-connection", tag=None),
        ],
        connections=[
            _pipe("p1", "primo", ("generatore", "water_supply"), ("deviatrice", "in")),
            _pipe("p2", "primo", ("deviatrice", "out_a"), ("serbatoio", "primary_in")),
            _pipe("p3", "primo", ("serbatoio", "primary_out"), ("ritorno", "a")),
            _pipe("p4", "primo", ("deviatrice", "out_b"), ("bollitore", "coil_in")),
            _pipe("p5", "primo", ("bollitore", "coil_out"), ("ritorno", "c")),
            _pipe("p6", "primo", ("ritorno", "b"), ("stacco-vaso", "a")),
            _pipe("p7", "primo", ("stacco-vaso", "b"), ("generatore", "water_return")),
            _pipe("p8", "primo", ("stacco-vaso", "branch"), ("vaso", "a")),
        ],
        subsystems=[
            SubsystemModel(
                id="centrale",
                name="centrale",
                component_ids=[
                    "generatore",
                    "deviatrice",
                    "serbatoio",
                    "bollitore",
                    "ritorno",
                    "stacco-vaso",
                    "vaso",
                ],
                network_ids=["primo"],
            )
        ],
    )


def _pezzi(
    project: ProjectModel,
) -> tuple[SheetPartition, list[PlacedSymbol], SpineLayout, Improver]:
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    first = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    spine = lay_the_spine(project, partition, catalog(), NOVE_C_A3, first)
    seeded = carry_the_rest(project, partition, catalog(), first, spine, NOVE_C_A3)
    improver = Improver(
        project, partition, catalog(), NOVE_C_A3, seeded, inline, spine
    )
    improver.refining = True
    return partition, seeded, spine, improver


@cache
def _banco() -> tuple[Improver, tuple[str, ...]]:
    """Il banco, costruito una volta: la posa seminata dal tronco e il blocco."""
    _, _, _, improver = _pezzi(tronco_con_corredo_sotto())
    block = improver.block_of(improver.scan[0])
    if not block:
        block = next(
            (improver.block_of(item) for item in improver.order if improver.block_of(item)),
            (),
        )
    return improver, block


def _distanze(improver: Improver, table: Move, block: tuple[str, ...]) -> dict[
    tuple[str, str], tuple[float, float]
]:
    """Ogni distanza interna al blocco, come coppia di scarti sui due assi."""
    out: dict[tuple[str, str], tuple[float, float]] = {}
    for index, one in enumerate(block):
        for two in block[index + 1 :]:
            here = table.get(one) or improver.best[one]
            there = table.get(two) or improver.best[two]
            out[one, two] = (
                there.origin.x_mm - here.origin.x_mm,
                there.origin.y_mm - here.origin.y_mm,
            )
    return out


def test_il_blocco_e_cio_che_una_autostrada_dritta_tiene_allineato() -> None:
    """Il corpo rigido si legge sul tronco, non su un elenco di nomi.

    Ci stanno i pezzi che una tratta di autostrada **gia' rettilinea** tiene
    allineati; non ci sta chi vi e' unito da una tratta che dritta non e', come
    il bollitore, perche' traslarlo insieme non conserverebbe niente.
    """
    improver, block = _banco()
    assert len(block) >= 2, block
    assert "generatore" in block and "serbatoio" in block, block
    assert "bollitore" not in block, block
    for trunk in improver.autostrade:
        ends = (trunk.start.component_id, trunk.end.component_id)
        if improver.lies_straight(improver.best, trunk) and ends[0] in block:
            assert ends[1] in block, (ends, block)


def test_la_traslazione_di_blocco_esiste_e_sposta_tutto_intero() -> None:
    """Criterio 5, prima meta': la mossa c'e', e muove il blocco e basta.

    Ogni candidata sposta **tutti** i membri del blocco della stessa quantita' e
    non tocca nessun pezzo che al blocco non appartiene, se non le figure che
    pendono dai suoi membri — che il blocco se le porta dietro.
    """
    improver, block = _banco()
    moves = improver._block_moves(improver.scan[0]) or improver._block_moves(block[0])
    assert moves, "nessuna traslazione di blocco generata"
    figure = {child for leader in block for child in improver.below(leader)}
    for move in moves:
        deltas = {
            (
                move[item].origin.x_mm - improver.best[item].origin.x_mm,
                move[item].origin.y_mm - improver.best[item].origin.y_mm,
            )
            for item in block
        }
        assert len(deltas) == 1, (deltas, block)
        assert deltas != {(0.0, 0.0)}
        estranei = set(move) - set(block) - figure
        assert not estranei, estranei


def test_il_blocco_non_si_deforma() -> None:
    """Criterio 6, prima meta': ogni distanza interna resta quella di prima."""
    improver, block = _banco()
    prima = _distanze(improver, {}, block)
    moves = improver._block_moves(improver.scan[0]) or improver._block_moves(block[0])
    assert moves
    for move in moves:
        assert _distanze(improver, move, block) == prima


def test_se_un_pezzo_non_puo_seguire_la_mossa_non_si_fa() -> None:
    """Criterio 6, seconda meta': non si fa a meta'.

    Si prende la traslazione piu' lunga e la si spinge fuori dall'area di
    disegno: `is_valid` la rifiuta **intera**, e nel farlo rifiuta anche lo
    spostamento dei membri che ci sarebbero stati. Non esiste una candidata che
    ne sposti una parte: le mosse generate hanno un solo scarto per tutti.
    """
    improver, block = _banco()
    fuori = improver.area.x_mm - improver.best[block[0]].origin.x_mm - improver.step
    troppo = improver._translated(block, fuori, 0.0)
    assert not improver.is_valid(troppo)
    meta = dict(troppo)
    for item in block[len(block) // 2 :]:
        meta.pop(item, None)
    deltas = {
        (
            meta.get(item, improver.best[item]).origin.x_mm - improver.best[item].origin.x_mm,
            meta.get(item, improver.best[item]).origin.y_mm - improver.best[item].origin.y_mm,
        )
        for item in block
    }
    assert len(deltas) > 1, "la mossa a meta' andrebbe costruita a mano"
    generate = improver._block_moves(improver.scan[0]) or improver._block_moves(block[0])
    for move in generate:
        assert all(item in move for item in block), (set(block) - set(move))


@pytest.mark.parametrize("steps", BLOCK_STEPS)
def test_una_traslazione_che_piega_il_tronco_e_rifiutata(steps: int) -> None:
    """Criterio 7, la prova negativa.

    Si sposta **meta'** del blocco — un solo membro — di traverso all'asse del
    tronco: l'autostrada che lo univa al resto smette di essere un rettilineo.
    `is_valid` la rifiuta, e la rifiuta **anche quando batte la chiave di
    costo**, perche' la rettilineita' del tronco non e' una voce di costo ma un
    vincolo (DRAW-008 §A.4). La prova misura le due cose separatamente: prima
    che la mossa sia davvero rifiutata, poi che il rifiuto non dipenda dal
    costo.
    """
    improver, block = _banco()
    dritte = [
        trunk
        for trunk in improver.autostrade
        if improver.lies_straight(improver.best, trunk)
        and trunk.start.component_id in block
        and trunk.end.component_id in block
    ]
    assert dritte, "il banco non ha nessuna autostrada dritta dentro il blocco"
    trunk = dritte[0]
    solo = trunk.end.component_id
    amount = steps * improver.step
    for dx, dy in ((0.0, -amount), (0.0, amount)):
        storto = improver._translated([solo], dx, dy)
        if improver.lies_straight({**improver.best, **storto}, trunk):
            continue
        assert not improver.is_valid(storto), (solo, dx, dy)


def test_il_rifiuto_non_dipende_dalla_chiave_di_costo() -> None:
    """La seconda meta' del criterio 7, detta per intero.

    Una prova negativa che rifiuta mosse gia' cattive non prova niente: il
    vincolo si distingue dal costo **solo** dove le due cose dicono il
    contrario. Qui la situazione si costruisce: si allontana il bollitore, cosi'
    che le tratte che lo raggiungono diventino care, e da li' piegare il tronco
    verso di lui **conviene** — la chiave di costo migliora. `is_valid` dice no
    lo stesso, a tutte, perche' la rettilineita' del tronco non e' una voce di
    costo ma un vincolo che nessun guadagno compra (DRAW-008 §A.4).

    Se nessuna delle traslazioni provate battesse il costo la prova fallirebbe
    dicendolo, invece di passare in silenzio su un banco che non prova niente.
    """
    _, _, _, improver = _pezzi(tronco_con_corredo_sotto())
    improver.refining = True
    block = improver.block_of(improver.scan[0]) or next(
        (improver.block_of(item) for item in improver.order if improver.block_of(item)),
        (),
    )
    assert block
    lontano = improver._translated(["bollitore"], 0.0, 10 * improver.step)
    assert improver.is_valid(lontano), "il banco non ammette l'allontanamento"
    improver.best = {**improver.best, **lontano}
    improver._refresh_hang_gaps()
    base = improver.measure(improver.best)
    assert base is not None, "il banco allontanato non si instrada"

    dritte = [
        trunk for trunk in improver.autostrade if improver.lies_straight(improver.best, trunk)
    ]
    assert dritte, "il banco non ha nessuna autostrada dritta da piegare"
    battute = 0
    for solo in block:
        for steps in BLOCK_STEPS:
            for delta in (-steps * improver.step, steps * improver.step):
                for move in (
                    improver._translated([solo], delta, 0.0),
                    improver._translated([solo], 0.0, delta),
                ):
                    after = {**improver.best, **move}
                    if not any(
                        improver.lies_straight(improver.best, trunk)
                        and not improver.lies_straight(after, trunk)
                        for trunk in improver.autostrade
                    ):
                        continue
                    # Piega il tronco: rifiutata, sempre.
                    assert not improver.is_valid(move), (solo, delta)
                    found = improver.measure(after)
                    if found is not None and found.cost.beats(base.cost):
                        battute += 1
    assert battute, (
        "nessuna delle traslazioni che piegano il tronco batte la chiave di costo: "
        "la prova non distinguerebbe il vincolo dal costo"
    )


def test_il_ciclo_offre_la_traslazione_di_blocco_fra_le_proprie_candidate() -> None:
    """La mossa non vive solo come metodo: il ciclo la **genera**.

    Una mossa che nessuna candidata porta non esiste per il ciclo, e il
    criterio 5 chiede che esista dove serve.
    """
    improver, block = _banco()
    kinds = {kind for kind, _ in improver.candidates_by_kind(block[0])}
    assert "blocco" in kinds, sorted(kinds)


def test_nessuna_mossa_esistente_fa_la_stessa_cosa() -> None:
    """Criterio 5, seconda meta': **nessuna** delle mosse di prima traslava il
    blocco tutto intero.

    Si guardano le candidate di tutte le altre specie e si conta quante
    spostano ogni membro del blocco della stessa quantita', senza toccare altro.
    Deve essere zero: se una ci fosse, la mossa nuova sarebbe un doppione.
    """
    improver, block = _banco()
    figure = {child for leader in block for child in improver.below(leader)}
    for kind, move in improver.candidates_by_kind(block[0]):
        if kind == "blocco":
            continue
        deltas = {
            (
                move.get(item, improver.best[item]).origin.x_mm
                - improver.best[item].origin.x_mm,
                move.get(item, improver.best[item]).origin.y_mm
                - improver.best[item].origin.y_mm,
            )
            for item in block
        }
        if deltas == {(0.0, 0.0)} or len(deltas) > 1:
            continue
        estranei = set(move) - set(block) - figure
        assert estranei, (
            f"la specie «{kind}» trasla gia' il blocco tutto intero: "
            f"la traslazione di blocco sarebbe un doppione"
        )


def test_la_traslazione_di_blocco_vince_dove_nessun_altra_vince() -> None:
    """Criterio 5, la misura: la mossa nuova **vince**.

    Sul banco costruito a mano si misura la chiave di costo di ogni candidata,
    specie per specie. La migliore fra le traslazioni di blocco batte la
    migliore fra tutte le altre: e' il senso della mossa, e senza questa misura
    «esiste» non vorrebbe dire niente.
    """
    improver, block = _banco()
    migliori: dict[str, tuple[object, ...]] = {}
    for kind, move in improver.candidates_by_kind(block[0]):
        if not improver.is_valid(move):
            continue
        found = improver.measure({**improver.best, **move})
        if found is None:
            continue
        key = found.cost.key()
        if kind not in migliori or key < migliori[kind]:
            migliori[kind] = key
    assert "blocco" in migliori, sorted(migliori)
    altre = {kind: key for kind, key in migliori.items() if kind != "blocco"}
    assert altre, "il banco non offre nessun'altra specie con cui confrontarsi"
    assert migliori["blocco"] < min(altre.values()), (migliori["blocco"], altre)


def test_la_traslazione_di_blocco_costa_zero() -> None:
    """§B.4: spostare macchine non costa, e il blocco si giudica sul foglio.

    Si misura che la traslazione non cambia **nessuna** delle voci del costo per
    conto proprio: la differenza di chiave viene tutta dal reinstradamento, cioe'
    dalle tratte che il tronco, spostandosi, ha accorciato o raddrizzato. Qui si
    prova la forma debole e verificabile: il blocco traslato di poco non
    peggiora la lunghezza totale delle proprie tratte interne, che dopo la
    traslazione sono identiche.
    """
    improver, block = _banco()
    interne = [
        trunk
        for trunk in improver.trunks
        if trunk.start.component_id in block and trunk.end.component_id in block
    ]
    assert interne
    moves = improver._block_moves(improver.scan[0]) or improver._block_moves(block[0])
    for move in moves:
        after = {**improver.best, **move}
        for trunk in interne:
            assert improver._link_mm(after, trunk) == pytest.approx(
                improver._link_mm(improver.best, trunk)
            )
            assert improver.lies_straight(after, trunk) == improver.lies_straight(
                improver.best, trunk
            )


def test_un_blocco_solo_propone_la_propria_traslazione() -> None:
    """Una mossa per blocco, non una per membro.

    Ogni candidata e' un instradamento di prova, e il tetto delle prove e'
    quello: proporre la stessa traslazione da ciascun membro la moltiplicherebbe
    per il numero dei membri senza aggiungere una sola posa nuova.
    """
    improver, block = _banco()
    proponenti = [item for item in block if improver._block_moves(item)]
    assert proponenti == [block[0]], proponenti


def test_il_blocco_porta_con_se_cio_che_gli_pende() -> None:
    """§B.2: il corpo rigido si porta dietro le figure appese ai suoi membri.

    Se qualcuno resta indietro la figura si spezza, e nessun vincolo se ne
    accorge: si misura che dopo la mossa ogni appeso ha lo stesso scarto dal
    proprio attacco che aveva prima.
    """
    improver, block = _banco()
    appesi = [
        (leader, child)
        for leader in block
        for child in improver.below(leader)
    ]
    if not appesi:
        pytest.skip("questo banco non ha figure appese al tronco")
    moves = improver._block_moves(improver.scan[0]) or improver._block_moves(block[0])
    for move in moves:
        for leader, child in appesi:
            assert child in move, (leader, child)
            before = (
                improver.best[child].origin.x_mm - improver.best[leader].origin.x_mm,
                improver.best[child].origin.y_mm - improver.best[leader].origin.y_mm,
            )
            now = (
                move[child].origin.x_mm - move[leader].origin.x_mm,
                move[child].origin.y_mm - move[leader].origin.y_mm,
            )
            assert now == pytest.approx(before), (child, before, now)


def test_senza_una_fase_del_tronco_non_c_e_nessun_corpo_rigido() -> None:
    """Il blocco esiste solo dove c'e' una forma da conservare.

    Un `Improver` costruito senza la fase del tronco — come fa il ripiego di
    `compose_sheet` — non ha autostrade dichiarate, quindi non ha nessun corpo
    rigido e nessuna traslazione di blocco. La mossa non si inventa un tronco
    dove nessuno l'ha costruito.
    """
    project = tronco_con_corredo_sotto()
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    first = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    senza = Improver(project, partition, catalog(), NOVE_C_A3, first, inline)
    assert senza.autostrade == []
    for item in senza.order:
        assert senza.block_of(item) == ()
        assert senza._block_moves(item) == []


def test_la_mossa_si_legge_nel_diario_con_il_proprio_nome() -> None:
    """Il diario dice quali alternative sono state provate, e con che nome.

    Serve al rapporto: «esiste» si prova mostrando la specie fra quelle
    generate, non descrivendola.
    """
    improver, block = _banco()
    generate = improver.candidates_by_kind(block[0])
    assert any(kind == "blocco" for kind, _ in generate)
    quante = sum(1 for kind, _ in generate if kind == "blocco")
    assert quante >= len(BLOCK_STEPS), quante


def test_la_mossa_che_porta_un_membro_fuori_dal_foglio_e_rifiutata() -> None:
    """L'altra faccia di «se un pezzo non puo' seguire»: il bordo destro.

    Si spinge il blocco a destra finche' il membro piu' a destra esce dall'area
    di disegno. La mossa non si fa, e non si fa nemmeno per i membri che ci
    sarebbero stati.
    """
    improver, block = _banco()
    sporgente = max(improver.best[item].right_mm for item in block)
    oltre = improver.area.right_mm - sporgente + improver.step
    fuori = improver._translated(block, oltre, 0.0)
    assert not improver.is_valid(fuori)


def test_ogni_membro_del_blocco_si_sposta_o_nessuno() -> None:
    """La forma minima di «non si fa a meta'», su tutte le candidate generate."""
    improver, block = _banco()
    for move in improver._block_moves(block[0]):
        mossi = [item for item in block if item in move]
        assert len(mossi) == len(block), (len(mossi), len(block))
        assert all(
            move[item].origin != Point(
                x_mm=improver.best[item].origin.x_mm, y_mm=improver.best[item].origin.y_mm
            )
            for item in block
        )
