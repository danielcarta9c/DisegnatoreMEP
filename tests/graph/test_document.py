"""Il documento per il committente: e' generato, ed e' scritto nella sua lingua.

L'artefatto di G1 e' `docs/prodotto/GRAFO_IMPIANTO.md`, ed e' **l'unico**: il
grafo dopo le integrazioni e i punti aperti delle regole si leggono qui, non in
un secondo documento che direbbe le stesse cose con parole diverse. Le prove qui
presidiano le cinque cose che lo rendono affidabile:

1. il file pubblicato **e'** cio' che lo script rigenera oggi — mai un elaborato
   vecchio mostrato come attuale;
2. non contiene un solo identificativo di codice, nome di file, nome di regola, o
   parola del vocabolario tecnico interno, e nemmeno una parola d'inglese: chi lo
   legge giudica l'impianto, non il programma;
3. dice dove ogni anello si richiude, tante volte quante il grafo ne conta;
4. dice cio' che manca — un attacco senza tubazione, un pezzo che nessuna
   sorgente raggiunge — invece di tacerlo, e lo si prova su impianti che quei
   difetti ce li hanno davvero;
5. quando una regola si applica e il catalogo non ha il pezzo, il documento lo
   dice **sul nodo in cui il pezzo manca** (D-096).
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import LineNaming, Naming, read_lines, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "examples" / "graph" / "build_plant_graph.py"
DOCUMENT = ROOT / "docs" / "prodotto" / "GRAFO_IMPIANTO.md"
NAMING = ROOT / "naming"
PLANT = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
HYDRONIC_CATALOG = ROOT / "examples" / "layout" / "catalog"
FOUNDATION_CATALOG = ROOT / "examples" / "foundation" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
TWO_ZONES = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
MIXED = ROOT / "examples" / "foundation" / "valid-mixed-project.json"

ENGLISH = (
    "the",
    "and",
    "with",
    "water",
    "valve",
    "pump",
    "supply",
    "return",
    "port",
    "node",
    "edge",
    "pipe",
    "plant",
    "source",
    "medium",
    "storage",
    "buffer",
    "cylinder",
    "boundary",
    "safety",
    "isolation",
    "drain",
    "filling",
    "flow",
    "walk",
    "ring",
    "reading",
    "component",
    "connection",
)
"""Parole che, se comparissero, direbbero che un'etichetta interna e' passata."""


def generator() -> ModuleType:
    """Lo script pubblicato, caricato dal suo file: e' quello che si collauda."""
    spec = importlib.util.spec_from_file_location("build_plant_graph", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog(directory: Path) -> ComponentRegistry:
    return ComponentRegistry.from_directory(directory)


def line_naming() -> LineNaming:
    return LineNaming.from_directory(NAMING)


def naming() -> Naming:
    return Naming.from_directory(NAMING)


def text() -> str:
    return DOCUMENT.read_text("utf-8")


def as_a_word(needle: str, haystack: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(needle)}(?![\w-])", haystack) is not None


# --- 1. il documento pubblicato e' la rigenerazione corrente ------------------


def test_the_published_document_is_the_current_regeneration(tmp_path: Path) -> None:
    target = tmp_path / "grafo.md"
    finished = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert finished.returncode == 0, finished.stderr
    assert target.read_text("utf-8") == text()


def test_the_document_is_written_by_a_committed_script() -> None:
    assert SCRIPT.is_file()
    assert DOCUMENT.is_file()


def test_two_regenerations_are_identical() -> None:
    project = load_project(PLANT)
    module = generator()
    once = module.build(project, catalog(HYDRONIC_CATALOG), naming())
    twice = module.build(project, catalog(HYDRONIC_CATALOG), naming())
    assert once == twice


# --- 2. il documento parla al committente -------------------------------------


def test_the_document_names_no_identifier_of_the_programme() -> None:
    """Anche i nomi delle regole: da quando i punti aperti si leggono qui, una
    regola potrebbe far passare il proprio identificativo davanti a chi legge."""
    project = load_project(PLANT)
    forbidden = {item.id for item in project.components}
    forbidden |= {item.definition_id for item in project.components}
    forbidden |= {item.id for item in project.networks}
    forbidden |= {item.id for item in project.subsystems}
    forbidden |= {item.id for item in project.connections}
    forbidden |= {item.id for item in catalog(HYDRONIC_CATALOG).all()}
    forbidden |= {project.metadata.project_id}
    forbidden |= {rule.id for rule in RuleRegistry.from_directory(RULES).all()}
    leaked = sorted(item for item in forbidden if as_a_word(item, text()))
    assert not leaked, leaked


def test_the_document_names_no_file() -> None:
    document = text()
    for mark in (".json", ".py", ".md", ".svg", "examples/", "docs/", "src/"):
        assert mark not in document, mark
    for path in sorted(RULES.glob("*.json")):
        assert path.name not in document, path.name


def test_the_document_speaks_no_internal_vocabulary() -> None:
    """Nessun mestiere di catalogo, nessun fluido in forma tecnica, nessuna
    proprieta': il committente legge «acqua fredda sanitaria»."""
    document = text()
    tokens: set[str] = set()
    for definition in catalog(HYDRONIC_CATALOG).all():
        tokens |= set(definition.functions)
        tokens |= {port.medium for port in definition.ports}
        tokens |= {str(trait) for trait in definition.traits}
    leaked = sorted(item for item in tokens if as_a_word(item, document))
    assert not leaked, leaked


def test_the_document_speaks_italian_only() -> None:
    document = text().lower()
    leaked = sorted(item for item in ENGLISH if as_a_word(item, document))
    assert not leaked, leaked


def test_the_document_shows_every_piece_with_its_sigla() -> None:
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    document = text()
    missing = sorted(
        node.sigla for node in graph.nodes if not as_a_word(node.sigla, document)
    )
    assert not missing, missing


def test_the_document_says_on_which_fluid_each_piece_runs() -> None:
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    table = naming()
    document = text()
    media = {medium for node in graph.nodes for medium in node.media}
    assert media
    for medium in media:
        assert table.name_of_medium(medium) in document


def test_the_document_says_which_water_each_tank_holds() -> None:
    """E' cio' che rende visibile a occhio uno scarico sul circuito sbagliato.

    Un bollitore che tiene acqua calda sanitaria e ha lo scarico sull'acqua di
    riscaldamento si vede leggendo due righe, senza sapere niente di
    impiantistica: e' il difetto per cui G3 e' stato respinto."""
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    table = naming()
    document = text()
    tanks = [node for node in graph.nodes if node.stored_medium is not None]
    assert tanks, "nessun serbatoio: prova inutile"
    for node in tanks:
        assert node.stored_medium is not None
        # La riga della tabella dei nodi comincia con l'indirizzo (D-105): la
        # sigla si cerca dentro la riga, non in testa.
        row = next(
            line for line in document.splitlines() if f"| **{node.sigla}** |" in line
        )
        assert "tiene in serbo" in row, row
        assert table.name_of_medium(node.stored_medium) in row, row


# --- 3. l'anello si legge come anello -----------------------------------------


def test_the_document_says_where_every_ring_closes() -> None:
    """Si contano le chiusure **sul grafo** e si pretende che il documento ne
    parli tante volte quante sono: cosi' la prova non si accontenta di trovare
    la frase una volta."""
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    closures = sum(
        1 for reading in graph.readings for step in reading.steps if step.closes_the_ring
    )
    assert closures
    assert text().count("qui il giro si richiude su") == closures


def test_the_document_names_the_piece_the_ring_closes_on() -> None:
    """Con l'indirizzo dei nodi (D-105) un anello si chiude dove una linea
    finisce su un nodo gia' numerato della propria acqua: e' quel pezzo che il
    documento deve nominare. Il **numero** degli anelli resta controllato dalla
    prova precedente contro la passeggiata, che e' una lettura indipendente."""
    project = load_project(PLANT)
    registry = catalog(HYDRONIC_CATALOG)
    graph = read_plant(project, registry, naming())
    lines = read_lines(project, registry, graph, line_naming())
    document = text()
    closed = 0
    for line in lines.lines:
        tail = line.node_ids[-1]
        if lines.owner.get(tail) == line.name:
            continue
        if any(
            graph.pipe(item).leaves.component_id == tail
            for item in lines.run_pipes.get(line.network_id, ())
        ):
            closed += 1
            sigla = graph.node(tail).sigla
            assert f"qui il giro si richiude su {sigla}" in document
    assert closed, "nessun anello sulle linee: prova inutile"


def test_the_document_says_out_loud_that_there_are_no_crossings() -> None:
    """Un attacco porta una tubazione sola (D-100), quindi su un impianto ben
    modellato di incroci non ce ne sono — e il documento lo **dice**, invece di
    tacere una sezione vuota. Dove due tubazioni si incontrano c'e' un pezzo che
    le unisce, e quello si legge fra i nodi come tutti gli altri."""
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    assert graph.crossings == ()
    assert "ogni attacco porta una sola tubazione" in text()


# --- 4. cio' che manca si legge, su impianti che ce l'hanno --------------------


def test_the_document_names_the_attachments_that_carry_no_pipe() -> None:
    module = generator()
    project = load_project(TWO_ZONES)
    registry = catalog(HYDRONIC_CATALOG)
    written = module.build(project, registry, naming())
    graph = read_plant(project, registry, naming())
    assert graph.free_arms
    for node, arm in graph.free_arms:
        assert f"braccio {arm.number}" in written
        assert node.sigla in written
    assert "Attacchi su cui non arriva nessuna tubazione" in written


def test_the_document_names_the_pieces_no_source_reaches() -> None:
    module = generator()
    project = load_project(MIXED)
    registry = catalog(FOUNDATION_CATALOG)
    written = module.build(project, registry, naming())
    graph = read_plant(project, registry, naming())
    assert graph.unreached
    for component_id in graph.unreached:
        assert graph.node(component_id).sigla in written
    assert "Pezzi che nessuna sorgente raggiunge." in written


def test_when_nothing_is_missing_the_document_says_so_out_loud() -> None:
    """Il silenzio non vale nemmeno quando va tutto bene: se il documento non
    dicesse niente, non si saprebbe se il controllo e' stato fatto."""
    document = text()
    assert "**Attacchi liberi:** nessuno" in document
    assert "**Pezzi che nessuna sorgente raggiunge:** nessuno" in document
    assert "**Tubazioni non lette:** nessuna" in document


def test_the_document_reads_a_plant_it_was_not_written_for() -> None:
    """Quattro domini, cinque reti, nemmeno un identificativo in comune con la
    centrale: se il documento sapesse leggere solo l'impianto di accettazione,
    qui si fermerebbe."""
    module = generator()
    written = module.build(load_project(MIXED), catalog(FOUNDATION_CATALOG), naming())
    graph = read_plant(load_project(MIXED), catalog(FOUNDATION_CATALOG), naming())
    for node in graph.nodes:
        assert as_a_word(node.sigla, written), node.sigla
    for word in ENGLISH:
        if word in ("supply", "return"):
            continue
        assert not as_a_word(word, written.lower()), word


# --- 5. i punti aperti si leggono sul nodo a cui manca il pezzo ---------------


def test_a_missing_piece_is_named_at_the_node_where_it_is_missing() -> None:
    """Il difetto che ha fatto respingere G3, dal lato del documento.

    Si toglie dal catalogo lo scarico sanitario: il bollitore non puo' piu'
    svuotare la propria riserva, e il grafo deve dirlo **sul bollitore** — non
    tacere, e non dirlo in fondo dove nessuno collega la cosa al pezzo."""
    module = generator()
    registry = ComponentRegistry.from_directory(
        HYDRONIC_CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    without = ComponentRegistry(
        [item for item in registry.all() if item.id != "drain-connection-dhw"],
        symbols=SymbolRegistry.from_directory(SYMBOLS),
    )
    project, _, gaps = saturate(
        load_project(ESSENTIAL), without, RuleRegistry.from_directory(RULES)
    )
    assert gaps

    written = str(module.build(project, without, naming(), gaps))
    tank = read_plant(project, without, naming()).node(gaps[0].anchor.component_id).sigla
    said = [line for line in written.splitlines() if "manca" in line and tank in line]
    assert said, written
    assert "attacco di scarico" in said[0].lower()
    assert "acqua calda sanitaria" in said[0]
    assert "Punti aperti" in written


def test_the_published_document_has_no_open_point_because_the_plant_has_none() -> None:
    """L'altro verso: la sezione c'e' sempre, e dice il vero."""
    registry = ComponentRegistry.from_directory(
        HYDRONIC_CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    _, _, gaps = saturate(
        load_project(ESSENTIAL), registry, RuleRegistry.from_directory(RULES)
    )
    assert gaps == []
    assert "**Punti aperti:** nessuno" in text()


@pytest.mark.parametrize("plant,directory", [(TWO_ZONES, HYDRONIC_CATALOG), (MIXED, FOUNDATION_CATALOG)])
def test_the_document_of_any_plant_is_reproducible(plant: Path, directory: Path) -> None:
    module = generator()
    project = load_project(plant)
    assert module.build(project, catalog(directory), naming()) == module.build(
        project.model_copy(update={"connections": list(reversed(project.connections))}),
        catalog(directory),
        naming(),
    )
