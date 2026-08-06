"""Il grafo dell'impianto: le proprieta' che lo rendono citabile e riproducibile.

Le prove non contano i pezzi di una tavola di prova: asseriscono **proprieta'**
che devono valere su qualunque impianto, e le verificano dove la regola vive —
per nodo, per attacco, per tubazione (D-088, D-092). Ogni proprieta' e' provata
su piu' impianti, fra cui uno che non e' stato scritto per questo pezzo e che
non condivide con gli altri ne' un identificativo, ne' un fluido, ne' un
dominio.

Le cinque proprieta' di accettazione di G1:

1. ogni nodo ha una sigla, e nessuna sigla e' ripetuta;
2. stesso impianto, stesse sigle — comunque sia ordinato il file che lo
   descrive, e qualunque sia il seme delle tabelle di hash;
3. un anello si legge come anello: la lettura dice dove si chiude e prosegue;
4. sorgenti e famiglie si riconoscono da cio' che i pezzi **dichiarano**, mai da
   un elenco di nomi, e la tabella delle sigle e' un **dato**;
5. cio' che manca — un attacco senza tubazione, un pezzo che nessuna sorgente
   raggiunge — e' un dato del grafo, non un silenzio.
"""

import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import GraphError, Naming, NamingError, PlantGraph, read_plant
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
NAMING = ROOT / "naming"
HYDRONIC_CATALOG = ROOT / "examples" / "layout" / "catalog"
FOUNDATION_CATALOG = ROOT / "examples" / "foundation" / "catalog"

PLANTS: dict[str, tuple[Path, Path]] = {
    # L'impianto di accettazione: centrale a pompa di calore completata dalle
    # regole degli accessori.
    "centrale completa": (
        ROOT / "examples" / "rules" / "centrale-pdc-completa.json",
        HYDRONIC_CATALOG,
    ),
    # Lo stesso impianto prima delle integrazioni: meno pezzi, stessa forma.
    "centrale essenziale": (
        ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json",
        HYDRONIC_CATALOG,
    ),
    # Un impianto scritto per un altro pezzo del progetto, con due attacchi
    # ancora da collegare.
    "pompa di calore con due zone": (
        ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json",
        HYDRONIC_CATALOG,
    ),
    "centrale su quattro fasce": (
        ROOT / "examples" / "layout" / "centrale-pdc-quattro-fasce.json",
        HYDRONIC_CATALOG,
    ),
    # L'impianto per cui questo pezzo non e' stato scritto: quattro domini,
    # cinque reti, sette fluidi diversi da quelli della centrale, e nemmeno un
    # identificativo in comune.
    "impianto misto": (
        ROOT / "examples" / "foundation" / "valid-mixed-project.json",
        FOUNDATION_CATALOG,
    ),
}


def naming() -> Naming:
    return Naming.from_directory(NAMING)


def graph_of(name: str) -> PlantGraph:
    plant, catalog = PLANTS[name]
    return read_plant(
        load_project(plant), ComponentRegistry.from_directory(catalog), naming()
    )


def project_of(name: str) -> ProjectModel:
    return load_project(PLANTS[name][0])


def catalog_of(name: str) -> ComponentRegistry:
    return ComponentRegistry.from_directory(PLANTS[name][1])


EVERY_PLANT = pytest.mark.parametrize("plant", sorted(PLANTS))


# --- 1. ogni nodo ha una sigla, e nessuna e' ripetuta -------------------------


@EVERY_PLANT
def test_every_piece_has_a_sigla(plant: str) -> None:
    """Un pezzo senza sigla non si puo' ne' citare ne' contare (D-097)."""
    graph = graph_of(plant)
    project = project_of(plant)
    assert len(graph.nodes) == len(project.components)
    for node in graph.nodes:
        assert node.sigla.strip(), node.component_id
    assert {node.component_id for node in graph.nodes} == {
        item.id for item in project.components
    }


@EVERY_PLANT
def test_no_two_pieces_share_a_sigla(plant: str) -> None:
    graph = graph_of(plant)
    sigle = [node.sigla for node in graph.nodes]
    assert len(set(sigle)) == len(sigle)


@EVERY_PLANT
def test_the_sigla_the_engineer_wrote_is_kept(plant: str) -> None:
    """La skill non ribattezza cio' che il progettista ha gia' chiamato."""
    graph = graph_of(plant)
    written = {
        item.id: item.tag for item in project_of(plant).components if item.tag is not None
    }
    assert written, "l'impianto non porta nessuna sigla scritta a mano: prova inutile"
    for component_id, tag in written.items():
        assert graph.node(component_id).sigla == tag


@EVERY_PLANT
def test_a_derived_sigla_never_steals_a_number_the_engineer_used(plant: str) -> None:
    """Le sigle scritte a mano prenotano il proprio numero nella loro famiglia."""
    graph = graph_of(plant)
    written = {
        item.tag for item in project_of(plant).components if item.tag is not None
    }
    derived = {
        node.sigla for node in graph.nodes if not node.written_by_the_engineer
    }
    assert not (written & derived)


# --- 2. stesso impianto, stesse sigle -----------------------------------------


def shuffled(project: ProjectModel, seed: int) -> ProjectModel:
    """Lo stesso impianto, scritto in un altro ordine. Stessa topologia."""
    rng = random.Random(seed)
    connections = list(project.connections)
    components = list(project.components)
    networks = list(project.networks)
    rng.shuffle(connections)
    rng.shuffle(components)
    rng.shuffle(networks)
    return project.model_copy(
        update={
            "connections": connections,
            "components": components,
            "networks": networks,
        }
    )


@EVERY_PLANT
def test_the_sigle_do_not_depend_on_how_the_file_lists_the_pipes(plant: str) -> None:
    """E' il criterio di accettazione piu' duro, e chiude alla radice il rilievo
    R2 del collaudo delle regole: l'ordine delle tubazioni nel file e' un fatto
    del file, non dell'impianto, e non deve poter cambiare un nome."""
    project, catalog = project_of(plant), catalog_of(plant)
    expected = read_plant(project, catalog, naming()).sigle
    reversed_pipes = project.model_copy(
        update={"connections": list(reversed(project.connections))}
    )
    assert read_plant(reversed_pipes, catalog, naming()).sigle == expected
    for seed in range(25):
        moved = project.model_copy(
            update={"connections": random.Random(seed).sample(
                list(project.connections), len(project.connections)
            )}
        )
        assert read_plant(moved, catalog, naming()).sigle == expected, seed


@EVERY_PLANT
def test_the_whole_reading_survives_any_reordering(plant: str) -> None:
    """Non solo le sigle: la passeggiata stessa, passo per passo. Se cambiasse
    l'ordine dei passi, cambierebbero anche i numeri della revisione dopo."""
    project, catalog = project_of(plant), catalog_of(plant)
    reference = read_plant(project, catalog, naming())
    expected = [
        (step.departs_from, step.arrives_at, step.closes_the_ring, step.rejoins)
        for reading in reference.readings
        for step in reading.steps
    ]
    for seed in range(25):
        graph = read_plant(shuffled(project, seed), catalog, naming())
        assert [
            (step.departs_from, step.arrives_at, step.closes_the_ring, step.rejoins)
            for reading in graph.readings
            for step in reading.steps
        ] == expected, seed


def sigle_from_a_fresh_interpreter(plant: str, hash_seed: str) -> str:
    """Le sigle calcolate in un interprete nuovo, col seme delle tabelle dato.

    Un dizionario percorso nel suo ordine di inserimento e' riproducibile; un
    insieme no, e il suo ordine cambia col seme. Provarlo dentro lo stesso
    processo non proverebbe niente: il seme si fissa all'avvio.
    """
    path, catalog = PLANTS[plant]
    program = (
        "import json;"
        "from pathlib import Path;"
        "from disegnatore_mep.catalog.registry import ComponentRegistry;"
        "from disegnatore_mep.graph import Naming, read_plant;"
        "from disegnatore_mep.io.project_json import load_project;"
        f"graph = read_plant(load_project(Path({str(path)!r})),"
        f" ComponentRegistry.from_directory(Path({str(catalog)!r})),"
        f" Naming.from_directory(Path({str(NAMING)!r})));"
        "print(json.dumps([[n.component_id, n.sigla] for n in graph.nodes]))"
    )
    finished = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
        env={"PATH": "/usr/bin:/bin", "PYTHONHASHSEED": hash_seed},
    )
    assert finished.returncode == 0, finished.stderr
    return finished.stdout


@EVERY_PLANT
def test_the_sigle_do_not_depend_on_the_hash_seed(plant: str) -> None:
    seeds = ["0", "1", "7", "12345"]
    answers = {seed: sigle_from_a_fresh_interpreter(plant, seed) for seed in seeds}
    assert len(set(answers.values())) == 1, answers


# --- 3. un anello si legge come anello ----------------------------------------


@EVERY_PLANT
def test_every_pipe_is_read_exactly_once(plant: str) -> None:
    """La lettura copre tutto l'impianto e non ripassa: e' la condizione perche'
    «ogni tubazione compare una volta» sia un'affermazione vera e non un augurio."""
    graph = graph_of(plant)
    walked = [
        step.connection_id for reading in graph.readings for step in reading.steps
    ]
    assert sorted(walked) == sorted(pipe.connection_id for pipe in graph.pipes)
    assert len(set(walked)) == len(walked)
    assert graph.unread_pipes == ()


def test_a_ring_reads_as_a_ring() -> None:
    """Un circuito idronico si chiude su se' stesso: la lettura lo dice.

    Si verifica dove la proprieta' vive — sul passo — e non contando le righe di
    un documento: per ogni chiusura, il pezzo d'arrivo deve essere gia' comparso
    prima nella stessa lettura, e la lettura non deve fermarsi li'.
    """
    for plant in ("centrale completa", "centrale essenziale", "pompa di calore con due zone"):
        graph = graph_of(plant)
        closures = [
            (reading, step)
            for reading in graph.readings
            for step in reading.steps
            if step.closes_the_ring
        ]
        assert closures, f"{plant}: nessun anello su un impianto idronico e' sospetto"
        for reading, step in closures:
            met_before = [reading.start]
            for item in reading.steps:
                if item is step:
                    break
                met_before.append(item.arrives_at)
            assert step.arrives_at in met_before, (plant, step.connection_id)


def test_the_reading_does_not_stop_where_the_ring_closes() -> None:
    """Fermarsi alla prima chiusura farebbe sparire meta' impianto."""
    graph = graph_of("centrale completa")
    for reading in graph.readings:
        closures = [
            index
            for index, step in enumerate(reading.steps)
            if step.closes_the_ring
        ]
        if closures and closures[0] < len(reading.steps) - 1:
            return
    pytest.fail("nessuna lettura prosegue dopo essersi richiusa")


def test_arriving_from_another_circuit_is_not_called_a_ring() -> None:
    """L'acqua fredda che arriva al bollitore non chiude nessun anello: ci si
    innesta. Chiamarla chiusura direbbe al committente che il circuito e' un
    anello quando invece finisce li'."""
    graph = graph_of("centrale completa")
    joins = [
        step
        for reading in graph.readings
        for step in reading.steps
        if step.rejoins
    ]
    assert joins, "l'impianto di accettazione ha un innesto fra circuiti"
    for step in joins:
        assert not step.closes_the_ring


# --- 4. sorgenti, famiglie e sigle vengono da cio' che i pezzi dichiarano ------


@EVERY_PLANT
def test_the_reading_starts_where_a_declared_property_says_so(plant: str) -> None:
    """Nessun elenco di nomi: la sorgente e' tale perche' la sua famiglia lo
    dichiara, e la famiglia viene dal mestiere che il catalogo scrive."""
    graph, catalog, project = graph_of(plant), catalog_of(plant), project_of(plant)
    table = naming()
    definitions = {item.id: item.definition_id for item in project.components}
    starts = [item for item in graph.readings if item.kind == "source"]
    assert starts, plant
    for reading in starts:
        definition = catalog.get(definitions[reading.start])
        family = table.family_of(tuple(definition.functions), definition.id)
        assert family.starts_the_reading, definition.id
        assert family.function in definition.functions


def test_a_generator_is_recognised_whatever_it_is_called() -> None:
    """La prova che la sorgente non e' un nome: due impianti che non hanno in
    comune ne' un identificativo, ne' una voce di catalogo, ne' un nome in
    italiano — una pompa di calore e una caldaia a gas — cominciano dal proprio
    generatore allo stesso modo."""
    for plant in ("centrale completa", "impianto misto"):
        graph, project = graph_of(plant), project_of(plant)
        catalog = catalog_of(plant)
        first = graph.readings[0]
        definition = catalog.get(
            next(item.definition_id for item in project.components if item.id == first.start)
        )
        assert "heat_generation" in definition.functions
    assert not (
        {item.definition_id for item in project_of("centrale completa").components}
        & {item.definition_id for item in project_of("impianto misto").components}
    )


def test_the_prefix_table_is_data_and_not_code(tmp_path: Path) -> None:
    """Cambiare la tabella cambia le sigle senza toccare una riga di programma.

    E' la differenza fra un dato e una costante scritta nel codice: se la sigla
    di una famiglia si potesse cambiare solo modificando il programma, la
    tabella sarebbe codice travestito.
    """
    families = json.loads((NAMING / "families.json").read_text("utf-8"))
    for entry in families["families"]:
        if entry["function"] == "isolation":
            entry["prefix"] = "RUB"
    (tmp_path / "families.json").write_text(json.dumps(families), encoding="utf-8")
    (tmp_path / "media.json").write_text(
        (NAMING / "media.json").read_text("utf-8"), encoding="utf-8"
    )
    graph = read_plant(
        project_of("centrale completa"),
        catalog_of("centrale completa"),
        Naming.from_directory(tmp_path),
    )
    assert any(node.sigla.startswith("RUB-") for node in graph.nodes)
    assert not any(
        node.sigla.startswith("VI-") and not node.written_by_the_engineer
        for node in graph.nodes
    )


def test_a_family_that_is_not_in_the_table_stops_the_reading(tmp_path: Path) -> None:
    """Un pezzo senza famiglia non prende una sigla inventata: fa fallire, e
    dice quale mestiere non sa nominare."""
    families = json.loads((NAMING / "families.json").read_text("utf-8"))
    families["families"] = [
        item for item in families["families"] if item["function"] != "isolation"
    ]
    (tmp_path / "families.json").write_text(json.dumps(families), encoding="utf-8")
    (tmp_path / "media.json").write_text(
        (NAMING / "media.json").read_text("utf-8"), encoding="utf-8"
    )
    with pytest.raises(NamingError) as raised:
        read_plant(
            project_of("centrale completa"),
            catalog_of("centrale completa"),
            Naming.from_directory(tmp_path),
        )
    assert "isolation" in str(raised.value)


def test_a_fluid_without_a_name_stops_the_reading() -> None:
    with pytest.raises(NamingError) as raised:
        naming().name_of_medium("qualcosa_che_non_esiste")
    assert "qualcosa_che_non_esiste" in str(raised.value)


def test_the_table_names_every_trade_the_catalogues_declare() -> None:
    """Se un mestiere del catalogo non avesse famiglia, ci sarebbe un pezzo che
    non si puo' siglare — e lo si scoprirebbe solo su quell'impianto."""
    table = naming()
    known = {entry.function for entry in table.families}
    for directory in (HYDRONIC_CATALOG, FOUNDATION_CATALOG):
        for definition in ComponentRegistry.from_directory(directory).all():
            assert set(definition.functions) & known, definition.id


def test_the_table_names_every_fluid_the_catalogues_declare() -> None:
    table = naming()
    for directory in (HYDRONIC_CATALOG, FOUNDATION_CATALOG):
        for definition in ComponentRegistry.from_directory(directory).all():
            for port in definition.ports:
                assert table.name_of_medium(port.medium)


# --- 5. i silenzi diventano dati ----------------------------------------------


def test_an_attachment_without_a_pipe_is_a_fact_of_the_graph() -> None:
    """Su un impianto in cui il sanitario non e' ancora collegato, i due attacchi
    liberi del bollitore si vedono: non spariscono."""
    graph = graph_of("pompa di calore con due zone")
    free = {(node.sigla, arm.number) for node, arm in graph.free_arms}
    assert free, "questo impianto ha attacchi ancora da collegare"
    for _, arm in graph.free_arms:
        assert arm.carries_nothing
        assert arm.pipes == ()


def test_a_piece_no_source_reaches_is_a_fact_of_the_graph() -> None:
    """Un ventilatore su un canale che nessuna presa d'aria alimenta resta
    visibile, siglato, e dichiarato per quello che e'."""
    graph = graph_of("impianto misto")
    assert graph.unreached, "questo impianto ha un'isola"
    for component_id in graph.unreached:
        assert graph.node(component_id).sigla
    islands = [item for item in graph.readings if item.kind == "unreached"]
    assert islands
    assert {item.start for item in islands} <= set(graph.unreached)


@EVERY_PLANT
def test_an_attachment_keeps_all_its_pipes_and_never_one(plant: str) -> None:
    """La radice del difetto che rendeva diverso lo stesso impianto scritto in
    un altro ordine: tenere **una** tubazione per attacco. Qui l'attacco le
    tiene tutte, e la somma torna."""
    graph = graph_of(plant)
    counted = sum(len(arm.pipes) for node in graph.nodes for arm in node.arms)
    assert counted == 2 * len(graph.pipes)
    for node, arm in graph.crossings:
        assert len(arm.pipes) > 1
        assert len(set(arm.pipes)) == len(arm.pipes), (node.sigla, arm.number)


def test_a_pipe_written_the_wrong_way_round_is_refused() -> None:
    """Il verso viene dal modello, e il modello non deve poter mentire: se il
    primo estremo di una tubazione fosse un ingresso, la lettura seguirebbe il
    fluido al contrario senza che nessuno se ne accorga."""
    project = project_of("centrale essenziale")
    flipped = project.connections[0].model_copy(
        update={
            "endpoint_a": project.connections[0].endpoint_b,
            "endpoint_b": project.connections[0].endpoint_a,
        }
    )
    broken = project.model_copy(
        update={"connections": [flipped, *project.connections[1:]]}
    )
    with pytest.raises(GraphError) as raised:
        read_plant(broken, catalog_of("centrale essenziale"), naming())
    assert "al contrario" in str(raised.value)
