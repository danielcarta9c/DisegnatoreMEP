"""Il documento per il committente: e' generato, ed e' scritto nella sua lingua.

L'artefatto di G1 e' `docs/prodotto/GRAFO_IMPIANTO.md`. Le prove qui presidiano
le quattro cose che lo rendono affidabile:

1. il file pubblicato **e'** cio' che lo script rigenera oggi — mai un elaborato
   vecchio mostrato come attuale;
2. non contiene un solo identificativo di codice, nome di file, o parola del
   vocabolario tecnico interno, e nemmeno una parola d'inglese: chi lo legge
   giudica l'impianto, non il programma;
3. dice dove ogni anello si richiude, tante volte quante il grafo ne conta;
4. dice cio' che manca — un attacco senza tubazione, un pezzo che nessuna
   sorgente raggiunge — invece di tacerlo, e lo si prova su impianti che quei
   difetti ce li hanno davvero.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming, read_plant
from disegnatore_mep.io.project_json import load_project

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "examples" / "graph" / "build_plant_graph.py"
DOCUMENT = ROOT / "docs" / "prodotto" / "GRAFO_IMPIANTO.md"
NAMING = ROOT / "naming"
PLANT = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
HYDRONIC_CATALOG = ROOT / "examples" / "layout" / "catalog"
FOUNDATION_CATALOG = ROOT / "examples" / "foundation" / "catalog"
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
    project = load_project(PLANT)
    forbidden = {item.id for item in project.components}
    forbidden |= {item.definition_id for item in project.components}
    forbidden |= {item.id for item in project.networks}
    forbidden |= {item.id for item in project.subsystems}
    forbidden |= {item.id for item in project.connections}
    forbidden |= {item.id for item in catalog(HYDRONIC_CATALOG).all()}
    forbidden |= {project.metadata.project_id}
    leaked = sorted(item for item in forbidden if as_a_word(item, text()))
    assert not leaked, leaked


def test_the_document_names_no_file() -> None:
    document = text()
    for mark in (".json", ".py", ".md", ".svg", "examples/", "docs/", "src/"):
        assert mark not in document, mark


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
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    document = text()
    for reading in graph.readings:
        for step in reading.steps:
            if step.closes_the_ring:
                sigla = graph.node(step.arrives_at).sigla
                assert f"qui il giro si richiude su {sigla}" in document


def test_the_document_shows_the_crossings_with_their_arms() -> None:
    """Un attacco su cui convergono piu' tubazioni e' un incrocio, e i suoi rami
    si contano (D-097)."""
    graph = read_plant(load_project(PLANT), catalog(HYDRONIC_CATALOG), naming())
    document = text()
    assert graph.crossings
    for node, arm in graph.crossings:
        assert (
            f"sul braccio {arm.number} di **{node.sigla}**" in document
        ), (node.sigla, arm.number)


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
    assert "Nessuna sorgente arriva fin qui" in written


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


@pytest.mark.parametrize("plant,directory", [(TWO_ZONES, HYDRONIC_CATALOG), (MIXED, FOUNDATION_CATALOG)])
def test_the_document_of_any_plant_is_reproducible(plant: Path, directory: Path) -> None:
    module = generator()
    project = load_project(plant)
    assert module.build(project, catalog(directory), naming()) == module.build(
        project.model_copy(update={"connections": list(reversed(project.connections))}),
        catalog(directory),
        naming(),
    )
