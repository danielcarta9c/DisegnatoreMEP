"""Assi fra le porte, dorsali rettilinee e T che assorbe una curva (DRAW-004).

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

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.composition import Standing
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    drawing_fingerprint,
)
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


def _prepared(project: ProjectModel) -> tuple[SheetPartition, frozenset[str]]:
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return partition, inline


def _posa(project: ProjectModel) -> list[PlacedSymbol]:
    partition, inline = _prepared(project)
    return place_sheet(project, partition, catalog(), NOVE_C_A3, inline)


def _improver(project: ProjectModel, placed: list[PlacedSymbol]) -> Improver:
    partition, inline = _prepared(project)
    return Improver(project, partition, catalog(), NOVE_C_A3, placed, inline)


def _refiner(project: ProjectModel, placed: list[PlacedSymbol]) -> Improver:
    """Il ciclo nella fase di rifinitura, dove vivono i candidati di DRAW-004:
    assi coordinati, dorsali, la T che gira, le quote delle macchine."""
    improver = _improver(project, placed)
    improver.refining = True
    return improver


def _moved(
    placed: list[PlacedSymbol], component_id: str, dx_mm: float = 0.0, dy_mm: float = 0.0
) -> list[PlacedSymbol]:
    return [
        item.model_copy(
            update={"origin": Point(x_mm=item.origin.x_mm + dx_mm, y_mm=item.origin.y_mm + dy_mm)}
        )
        if item.component_id == component_id
        else item
        for item in placed
    ]


def _bends_of(improver: Improver, layout: Move) -> dict[tuple[str, ...], int]:
    """Le pieghe di ogni tratta, sulla tavola instradata di quella posa."""
    found = improver.measure(layout)
    assert found is not None
    return {
        trunk.connection_ids: sum(max(len(segment) - 2, 0) for segment in route.segments)
        for trunk, route in zip(improver.trunks, found.settled.routes, strict=True)
    }


def _port(improver: Improver, layout: Move, component_id: str, port_id: str) -> tuple[Point, PortFace]:
    return improver.port_at(layout[component_id], port_id)


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


def _sopra_il_raccordo(project: ProjectModel) -> list[PlacedSymbol]:
    """La posa iniziale, con il terminale portato sopra il raccordo e girato
    perche' il suo ingresso guardi in basso — la strada dal raccordo e' una
    verticale, se il raccordo la offre — e l'accumulo a destra del raccordo,
    con l'ingresso sull'asse della sua uscita diritta."""
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    tee = where["raccordo"]
    tank_port = catalog().resolve("buffer-two-port").symbol.manifest.port("a")
    placed = [
        item.model_copy(
            update={
                "origin": Point(
                    x_mm=tee.right_mm + 8 * STEP_MM,
                    y_mm=tee.origin.y_mm + tee.height_mm / 2 - tank_port.y_mm,
                )
            }
        )
        if item.component_id == "serbatoio"
        else item
        for item in placed
    ]
    radiator = catalog().resolve("radiator").symbol.manifest
    turned = next(
        degrees
        for degrees in sorted(radiator.allowed_rotations_deg)
        if radiator.rotated(degrees).port("in").face is PortFace.BOTTOM
    )
    shape = radiator.rotated(turned)
    port = shape.port("in")
    top = tee.origin.y_mm - 8 * STEP_MM
    return [
        item.model_copy(
            update={
                "rotation_deg": turned,
                "width_mm": shape.width_mm,
                "height_mm": shape.height_mm,
                "origin": Point(
                    x_mm=tee.origin.x_mm + tee.width_mm / 2 - port.x_mm,
                    y_mm=top - shape.height_mm,
                ),
            }
        )
        if item.component_id == "terminale"
        else item
        for item in placed
    ]


# ---------------------------------------------------------------------------
# 1-3. Candidati di allineamento delle porte
# ---------------------------------------------------------------------------


def test_un_allineamento_gratuito_toglie_una_curva_e_batte_la_posa_iniziale() -> None:
    """Prova 1: due macchine con porte collegabili direttamente ma disallineate."""
    project = macchina_e_serbatoio()
    placed = _posa(project)
    improver = _refiner(project, placed)
    before = improver.measure(improver.best)
    assert before is not None
    supply, _ = _port(improver, improver.best, "macchina", "water_supply")
    inlet, _ = _port(improver, improver.best, "serbatoio", "a")
    assert supply.y_mm != inlet.y_mm, "la posa iniziale lascia il dogleg"
    bends = _bends_of(improver, improver.best)
    assert bends[("c1",)] >= 2

    winners: list[Move] = []
    for leader in ("macchina", "serbatoio"):
        for move in improver.candidates(leader):
            if not improver.is_valid(move):
                continue
            trial = {**improver.best, **move}
            after, _ = _port(improver, trial, "macchina", "water_supply")
            into, _ = _port(improver, trial, "serbatoio", "a")
            if after.y_mm != into.y_mm:
                continue
            found = improver.measure(trial)
            if found is None:
                continue
            if found.cost.beats(before.cost) and _bends_of(improver, trial)[("c1",)] < bends[("c1",)]:
                winners.append(move)
    assert winners, "nessun candidato allinea le due porte togliendo la curva"
    # Il candidato sposta soltanto simboli: nessuna tratta e' toccata a mano.
    assert all(isinstance(item, PlacedSymbol) for move in winners for item in move.values())

    # Il ciclo e' greedy sul costo della tavola intera: alla fine batte la
    # posa iniziale e ha tolto curve, anche se la strada che ha preso puo'
    # non essere quella del primo candidato che allineava.
    final = {item.component_id: item for item in improver.run()}
    settled = improver.measure(final)
    assert settled is not None
    assert settled.cost.beats(before.cost)
    assert sum(_bends_of(improver, final).values()) < sum(bends.values())


def test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore() -> None:
    """Prova 2: l'asse e' un candidato, non un obbligo.

    Lo stesso impianto, con un secondo accumulo posato esattamente dove il
    primo dovrebbe salire per allinearsi: la mossa che allinea da sola viola
    la distanza minima, e si tiene solo cio' che batte davvero la tavola.
    """
    project = _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("serbatoio", "buffer-two-port"),
            ("riserva", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "serbatoio", "a"),
            ("c2", "serbatoio", "b", "terminale", "in"),
            ("c3", "terminale", "out", "macchina", "water_return"),
            ("c4", "riserva", "b", "terminale", "in"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("accumulo", ["serbatoio", "riserva"]),
            ("utenza", ["terminale"]),
        ],
    )
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    machine, tank = where["macchina"], where["serbatoio"]
    supply_y = machine.origin.y_mm + catalog().resolve("heat-pump-air-water").symbol.manifest.port("water_supply").y_mm
    inlet_y = catalog().resolve("buffer-two-port").symbol.manifest.port("a").y_mm
    aligned_top = supply_y - inlet_y
    # La riserva sta sopra il serbatoio, a un passo da dove il serbatoio
    # allineato finirebbe: salire vuol dire toccarla.
    blocked = [
        item.model_copy(
            update={"origin": Point(x_mm=tank.origin.x_mm, y_mm=aligned_top - STEP_MM)}
        )
        if item.component_id == "riserva"
        else item
        for item in placed
    ]
    improver = _improver(project, blocked)
    before = improver.measure(improver.best)
    assert before is not None
    alone = {
        "serbatoio": tank.model_copy(
            update={"origin": Point(x_mm=tank.origin.x_mm, y_mm=aligned_top)}
        )
    }
    assert not improver.is_valid(alone), "allinearsi da soli viola la distanza minima"

    final = {item.component_id: item for item in improver.run()}
    after = improver.measure(final)
    assert after is not None
    assert not before.cost.beats(after.cost), "il ciclo non peggiora mai la tavola"
    assert after.cost.violations == 0
    # Ogni mossa accettata ha battuto strettamente la precedente: l'asse non
    # e' mai stato imposto.
    accepted = [entry for entry in improver.journal if entry.accepted]
    keys = [before.cost.key()]
    for entry in accepted:
        assert entry.cost is not None
        keys.append(entry.cost)
    assert all(later < earlier for earlier, later in zip(keys, keys[1:], strict=False))


def test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale() -> None:
    """Prova 3: la quota iniziale e' un suggerimento di posa, non un vincolo."""
    project = macchina_e_serbatoio()
    placed = _posa(project)
    improver = _refiner(project, placed)
    assert improver.standings["serbatoio"] is Standing.GROUND
    assert improver.standings["macchina"] is Standing.GROUND
    vertical = [
        move
        for leader in ("serbatoio", "macchina")
        for move in improver.candidates(leader)
        if any(
            improver.standings[item] is Standing.GROUND
            and placed_item.origin.y_mm != improver.best[item].origin.y_mm
            for item, placed_item in move.items()
        )
    ]
    assert vertical, "nessun candidato muove in verticale una macchina a terra"
    assert any(improver.is_valid(move) for move in vertical)
    # Restano i vincoli: griglia, area e ordine di processo.
    for move in vertical:
        if improver.is_valid(move):
            for item in move.values():
                assert (item.origin.y_mm - improver.area.y_mm) % STEP_MM == 0
                assert item.bottom_mm <= improver.levels.ground_mm + 1e-9


# ---------------------------------------------------------------------------
# 4. Dorsale prima, stacchi dopo
# ---------------------------------------------------------------------------


def test_una_dorsale_con_uno_stacco_resta_rettilinea_e_la_t_sta_sull_asse() -> None:
    project = dorsale_con_uno_stacco()
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    # Il raccordo viene portato apposta fuori asse, sopra la riga della porta.
    bent = _moved(placed, "raccordo", dy_mm=-3 * STEP_MM)
    improver = _refiner(project, bent)
    before = improver.measure(improver.best)
    assert before is not None
    bends = _bends_of(improver, improver.best)
    assert bends[("c1",)] + bends[("c2",)] >= 2, "la posa piegata ha il dogleg"

    def on_the_axis(layout: Move) -> bool:
        supply, _ = _port(improver, layout, "macchina", "water_supply")
        entry, _ = _port(improver, layout, "raccordo", "a")
        exit_, _ = _port(improver, layout, "raccordo", "b")
        inlet, _ = _port(improver, layout, "serbatoio", "a")
        return supply.y_mm == entry.y_mm == exit_.y_mm == inlet.y_mm

    spine = [
        {**improver.best, **move}
        for leader in ("raccordo", "macchina", "serbatoio")
        for move in improver.candidates(leader)
        if improver.is_valid(move) and on_the_axis({**improver.best, **move})
    ]
    assert spine, "nessun candidato rimette raccordo e accumulo sull'asse della macchina"
    assert any(
        _bends_of(improver, layout)[("c1",)] == 0 and _bends_of(improver, layout)[("c2",)] == 0
        for layout in spine
    )

    # Alla fine decide il costo della tavola intera: il raccordo sta
    # sull'asse della macchina e la sequenza non paga il dogleg; se il
    # percorso verso l'accumulo gira, gira **nel raccordo** — la T che
    # assorbe la curva — e non in un gomito a parte.
    final = {item.component_id: item for item in improver.run()}
    supply, _ = _port(improver, final, "macchina", "water_supply")
    entry, _ = _port(improver, final, "raccordo", "a")
    assert supply.y_mm == entry.y_mm, "il raccordo sta sull'asse della macchina"
    settled = _bends_of(improver, final)
    assert settled[("c1",)] == 0
    assert settled[("c2",)] == 0 or (settled[("c2",)] == 1 and final["raccordo"].port_map)
    assert settled[("c1",)] + settled[("c2",)] < bends[("c1",)] + bends[("c2",)]
    assert where["terminale"].component_id in final


# ---------------------------------------------------------------------------
# 5-6. La T che assorbe una curva
# ---------------------------------------------------------------------------


def _faces(improver: Improver, layout: Move) -> dict[str, PortFace]:
    return {
        port_id: _port(improver, layout, "raccordo", port_id)[1] for port_id in ("a", "b", "c")
    }


def test_una_t_con_due_imbocchi_ortogonali_assorbe_un_gomito() -> None:
    """Prova 5: la T resta, il gomito separato sparisce; grafo e connessioni
    restano identici."""
    project = tee_che_deve_girare()
    placed = _sopra_il_raccordo(project)
    improver = _refiner(project, placed)
    before = improver.measure(improver.best)
    assert before is not None
    bends = _bends_of(improver, improver.best)
    assert bends[("c2",)] + bends[("c3",)] >= 1, "la posa iniziale paga un gomito"

    orthogonal = [
        move
        for move in improver.candidates("raccordo")
        if "raccordo" in move
        and improver.is_valid(move)
        and move["raccordo"].port_map
        and _faces(improver, {**improver.best, **move})["b"] is PortFace.TOP
        and _faces(improver, {**improver.best, **move})["c"] is PortFace.RIGHT
    ]
    assert orthogonal, "nessun candidato usa due attacchi ortogonali per la prosecuzione"
    better = [
        move
        for move in orthogonal
        if (found := improver.measure({**improver.best, **move})) is not None
        and found.cost.beats(before.cost)
    ]
    assert better, "la T ortogonale non batte la T piu' gomito"
    layout = {**improver.best, **better[0]}
    settled = _bends_of(improver, layout)
    assert settled[("c2",)] + settled[("c3",)] < bends[("c2",)] + bends[("c3",)]

    final = {item.component_id: item for item in improver.run()}
    after = improver.measure(final)
    assert after is not None
    assert after.cost.beats(before.cost)
    assert final["raccordo"].port_map, "la posa finale usa la coppia ortogonale"
    # Il grafo non e' cambiato: stesse connessioni, stessi identificativi,
    # stesse porte del modello alle stesse tratte.
    assert [item.connection_ids for item in improver.trunks] == [
        item.connection_ids for item in _prepared(project)[0].trunks
    ]
    assert project == tee_che_deve_girare()
    assert set(final["raccordo"].port_map) <= {"a", "b", "c"}
    assert sorted(final["raccordo"].port_map.values()) == sorted(final["raccordo"].port_map)


def test_se_la_t_ortogonale_peggiora_resta_la_configurazione_corrente() -> None:
    """Prova 6: tutto gia' in asse, la T diritta e' la migliore e resta."""
    project = dorsale_con_uno_stacco()
    placed = _posa(project)
    improver = _improver(project, placed)
    # Prima si toglie il dogleg con il ciclo: la posa che ne esce e' quella
    # che nessuna permutazione della T deve battere.
    final = {item.component_id: item for item in improver.run()}
    settled = improver.measure(final)
    assert settled is not None
    assert _bends_of(improver, final)[("c1",)] == 0
    assert _bends_of(improver, final)[("c2",)] == 0
    # Le permutazioni della T sono candidati della rifinitura; quelle che
    # voltano un attacco al proprio pari si scartano prima di misurarle, le
    # altre si misurano e nessuna batte la posa diritta.
    assert improver.refining
    permuted = [
        move
        for move in improver.candidates("raccordo")
        if "raccordo" in move and move["raccordo"].port_map and improver.is_valid(move)
    ]
    for move in permuted:
        found = improver.measure({**final, **move})
        assert found is None or not found.cost.beats(settled.cost)
    tried = [entry for entry in improver.journal if entry.kind == "tee"]
    assert tried or not permuted
    assert not final["raccordo"].port_map


def _keeps_every_port_in_place(project: ProjectModel, component_id: str) -> None:
    """Nessuna permutazione per un pezzo che non e' un raccordo: ne' fra le
    ammesse, ne' in nessun candidato di nessun pezzo, ne' nella posa finale."""
    placed = _posa(project)
    improver = _improver(project, placed)
    assert improver.permutations[component_id] == [{}]
    for leader in improver.order:
        for move in improver.candidates(leader):
            for item, pose in move.items():
                assert pose.port_map == {}, (leader, item)
    final = {item.component_id: item for item in improver.run()}
    assert final[component_id].port_map == {}
    assert all(item.port_map == {} for item in final.values())
    drawn = compose_drawing(project, catalog(), NOVE_C_A3).sheets[0]
    assert all(item.port_map == {} for item in drawn.symbols)


def test_una_valvola_miscelatrice_a_tre_vie_non_permuta_le_porte() -> None:
    """Tre porte dello stesso fluido, ma ognuna con un ruolo: calda, fredda,
    uscita. Il catalogo la dichiara `circuit_mixing`, non raccordo, e il
    disegnatore non le scambia mai."""
    project = _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("miscelatrice", "mixing-valve-3way"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "miscelatrice", "hot_in"),
            ("c2", "miscelatrice", "out", "terminale", "in"),
            ("c3", "terminale", "out", "miscelatrice", "cold_in"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("distribuzione", ["miscelatrice"]),
            ("utenza", ["terminale"]),
        ],
    )
    _keeps_every_port_in_place(project, "miscelatrice")


def test_un_collettore_di_zona_non_permuta_le_porte() -> None:
    """Un ingresso e due uscite dello stesso fluido: il catalogo lo dichiara
    `distribution`, e le sue porte restano dove sono."""
    project = _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("collettore", "zone-manifold"),
            ("zona-uno", "radiator"),
            ("zona-due", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "collettore", "in"),
            ("c2", "collettore", "out_1", "zona-uno", "in"),
            ("c3", "collettore", "out_2", "zona-due", "in"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("distribuzione", ["collettore"]),
            ("utenza", ["zona-uno", "zona-due"]),
        ],
    )
    _keeps_every_port_in_place(project, "collettore")


def test_solo_un_raccordo_dichiarato_dal_catalogo_ammette_permutazioni() -> None:
    """Il criterio e' la funzione di catalogo, non il numero di porte."""
    project = tee_che_deve_girare()
    improver = _improver(project, _posa(project))
    assert len(improver.permutations["raccordo"]) > 1
    assert improver.permutations["macchina"] == [{}]
    assert improver.permutations["serbatoio"] == [{}]


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


def test_i_testi_non_cambiano_nessun_candidato_simbolo_o_tubo() -> None:
    """Prova 8: aggiungere, cambiare o togliere testi non tocca la posa."""
    plain = tee_che_deve_girare()
    tagged = tee_che_deve_girare(
        tags={"macchina": "PDC-LUNGHISSIMA-0001", "serbatoio": "ACC-01", "terminale": "RAD-01"}
    )
    first, second = _improver(plain, _posa(plain)), _improver(tagged, _posa(tagged))
    assert {k: (v.origin, v.rotation_deg) for k, v in first.best.items()} == {
        k: (v.origin, v.rotation_deg) for k, v in second.best.items()
    }
    for leader in first.order:
        mine = [
            sorted((k, v.origin.x_mm, v.origin.y_mm, v.rotation_deg, tuple(sorted(v.port_map.items()))) for k, v in move.items())
            for move in first.candidates(leader)
        ]
        theirs = [
            sorted((k, v.origin.x_mm, v.origin.y_mm, v.rotation_deg, tuple(sorted(v.port_map.items()))) for k, v in move.items())
            for move in second.candidates(leader)
        ]
        assert mine == theirs, leader
    assert _shape(compose_drawing(plain, catalog(), NOVE_C_A3)) == _shape(
        compose_drawing(tagged, catalog(), NOVE_C_A3)
    )
