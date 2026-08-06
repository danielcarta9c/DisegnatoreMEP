"""L'albero dell'impianto: l'artefatto su cui le regole si collaudano (D-096).

Le regole degli accessori non si verificano su un disegno. Si verificano su
questo: un grafo scritto, con una sigla per pezzo, in cui un accessorio finito
sul circuito sbagliato si vede leggendo. Le prove qui presidiano le quattro cose
che lo rendono affidabile:

1. il file pubblicato **e'** cio' che lo script rigenera oggi;
2. le sigle sono stabili — lo stesso impianto da' sempre le stesse — e non
   dipendono da come il file elenca le tubazioni (D-098);
3. il documento e' leggibile da un non tecnico: nessun identificativo, nessun
   nome di file, nessuna parola del vocabolario tecnico interno;
4. quando una regola si applica e il catalogo non ha il pezzo, l'albero lo dice
   **nel punto in cui il pezzo manca**.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.tags import assign_tags, sources_of, visit_order
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "examples" / "rules" / "build_plant_tree.py"
DOCUMENT = ROOT / "docs" / "prodotto" / "ALBERO_IMPIANTO.md"
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
COMPLETE = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def generator() -> ModuleType:
    """Lo script pubblicato, caricato dal suo file: e' quello che si collauda."""
    spec = importlib.util.spec_from_file_location("build_plant_tree", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def complete() -> ProjectModel:
    return load_project(COMPLETE)


# --- 1. il documento pubblicato e' la rigenerazione corrente -------------------


def test_the_published_tree_is_the_current_regeneration(tmp_path: Path) -> None:
    """Mai un artefatto vecchio mostrato come attuale, nemmeno per la lettura."""
    target = tmp_path / "albero.md"
    finished = subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert finished.returncode == 0, finished.stderr
    assert target.read_text("utf-8") == DOCUMENT.read_text("utf-8")


def test_the_tree_is_written_by_the_script_and_not_by_hand() -> None:
    assert SCRIPT.is_file()
    assert DOCUMENT.is_file()


# --- 2. una sigla sola per pezzo, stabile -------------------------------------


def test_every_piece_has_a_sigla_and_no_two_share_one() -> None:
    """Un pezzo senza sigla non si puo' ne' citare ne' contare (D-097)."""
    project = complete()
    tags = assign_tags(project, catalog())
    assert len(tags) == len(project.components)
    assert len(set(tags.values())) == len(tags)
    for component in project.components:
        assert tags[component.id].strip()


def test_a_piece_keeps_the_sigla_the_engineer_wrote() -> None:
    project = complete()
    tags = assign_tags(project, catalog())
    written = {item.id: item.tag for item in project.components if item.tag is not None}
    assert written
    for component_id, tag in written.items():
        assert tags[component_id] == tag


def test_two_runs_give_the_same_sigle() -> None:
    project = complete()
    assert assign_tags(project, catalog()) == assign_tags(project, catalog())


def test_the_sigle_do_not_depend_on_how_the_file_lists_the_pipes() -> None:
    """D-098: stesso impianto, stesse sigle, comunque sia ordinato il file.

    Si rovescia l'elenco delle tubazioni — stesso impianto, stessa topologia — e
    si pretende che ogni pezzo si chiami come prima. Senza la partenza dalle
    sorgenti, la numerazione seguirebbe l'ordine del file e cambierebbe qui."""
    project = complete()
    shuffled = project.model_copy(
        update={"connections": list(reversed(project.connections))}
    )
    assert assign_tags(shuffled, catalog()) == assign_tags(project, catalog())


def test_the_reading_starts_from_the_sources_and_they_are_declared() -> None:
    """Le sorgenti si riconoscono da cio' che dichiarano, mai da un elenco di nomi."""
    project = complete()
    registry = catalog()
    starts = sources_of(project, registry)
    assert starts
    for component_id in starts:
        definition = registry.get(
            next(
                item.definition_id
                for item in project.components
                if item.id == component_id
            )
        )
        assert {"heat_generation", "boundary"} & set(definition.functions)
    assert visit_order(project, registry)[0] == starts[0]


def test_the_reading_touches_every_piece_exactly_once() -> None:
    """Un circuito e' un anello: si torna sui propri passi e non si ricomincia,
    e nessun pezzo resta fuori dalla lettura."""
    project = complete()
    order = visit_order(project, catalog())
    assert len(order) == len(set(order)) == len(project.components)


# --- 3. il documento parla al committente -------------------------------------


def test_the_tree_names_no_identifier_and_no_file() -> None:
    text = DOCUMENT.read_text("utf-8")
    project = complete()
    registry = catalog()
    forbidden = {item.id for item in project.components}
    forbidden |= {item.definition_id for item in project.components}
    forbidden |= {item.id for item in project.networks}
    forbidden |= {item.id for item in registry.all()}
    forbidden |= {rule.id for rule in RuleRegistry.from_directory(RULES).all()}
    forbidden |= {path.name for path in sorted(RULES.glob("*.json"))}
    leaked = sorted(item for item in forbidden if item in text)
    assert not leaked, leaked


def test_the_tree_speaks_no_technical_vocabulary() -> None:
    """Nessuna funzione di catalogo, nessun fluido in forma tecnica: il
    committente legge «acqua fredda sanitaria», non l'etichetta interna."""
    text = DOCUMENT.read_text("utf-8")
    tokens = {
        function for item in catalog().all() for function in item.functions
    }
    tokens |= {port.medium for item in catalog().all() for port in item.ports}
    leaked = sorted(item for item in tokens if item in text)
    assert not leaked, leaked


def test_the_tree_shows_every_piece_of_the_plant() -> None:
    """Ogni pezzo compare, con la sua sigla: e' la condizione perche' il
    committente possa dire «questo qui e' nel posto sbagliato»."""
    text = DOCUMENT.read_text("utf-8")
    tags = assign_tags(complete(), catalog())
    missing = sorted(tag for tag in tags.values() if tag not in text)
    assert not missing, missing


def test_the_tree_says_on_which_fluid_every_circuit_runs() -> None:
    text = DOCUMENT.read_text("utf-8")
    for words in ("acqua di riscaldamento", "acqua fredda sanitaria", "acqua calda sanitaria"):
        assert words in text


def test_the_tree_shows_where_each_circuit_closes_back_on_itself() -> None:
    """Un circuito idronico e' un anello, non un albero.

    Prima o poi una fila arriva su un pezzo gia' letto: quello e' il punto in cui
    il giro si richiude, e il documento lo deve dire — fermarsi li' farebbe
    credere che manchi un pezzo. La prova conta i punti di chiusura sul grafo e
    pretende che il documento ne parli tante volte quante sono."""
    module = generator()
    plant = module.Plant(complete(), catalog())
    closures = 0
    for network in plant.project.networks:
        met: set[str] = set()
        for start, _, _, end, _, pipe in plant.runs():
            if pipe.network_id != network.id:
                continue
            if start in met and end in met:
                closures += 1
            met.update({start, end})
    assert closures, "nessun anello: su un impianto idronico sarebbe sospetto"
    assert DOCUMENT.read_text("utf-8").count("il giro si richiude su") == closures


# --- 4. cio' che manca si vede dove manca -------------------------------------


def test_a_missing_piece_is_named_at_the_node_where_it_is_missing() -> None:
    """Il difetto che ha fatto respingere P2, dal lato del documento.

    Si toglie dal catalogo lo scarico sanitario: il bollitore non puo' piu'
    svuotare la propria riserva, e l'albero deve dirlo sul bollitore — non
    tacere, e non dirlo in fondo dove nessuno collega la cosa al pezzo."""
    module = generator()
    registry = catalog()
    without = ComponentRegistry(
        [item for item in registry.all() if item.id != "drain-connection-dhw"],
        symbols=SymbolRegistry.from_directory(SYMBOLS),
    )
    rules = RuleRegistry.from_directory(RULES)
    project, _, gaps = saturate(load_project(ESSENTIAL), without, rules)
    assert gaps

    text = str(module.build(project, without, gaps))
    tank = assign_tags(project, without)[gaps[0].anchor.component_id]
    said = [line for line in text.splitlines() if "manca" in line and tank in line]
    assert said, text
    assert "attacco di scarico" in said[0].lower()
    assert "acqua calda sanitaria" in said[0]
    assert "Punti aperti" in text


def test_the_published_tree_has_no_open_point_because_the_plant_has_none() -> None:
    """L'altro verso: la sezione c'e' sempre, e dice il vero."""
    _, _, gaps = saturate(load_project(ESSENTIAL), catalog(), RuleRegistry.from_directory(RULES))
    assert gaps == []
    assert "Nessuno: per ogni accessorio" in DOCUMENT.read_text("utf-8")


def test_the_generator_refuses_a_fluid_it_cannot_name(tmp_path: Path) -> None:
    """Meglio un documento che non esce di uno che mette davanti al committente
    un'etichetta interna."""
    module = generator()
    with pytest.raises(module.TreeError, match="non so come chiamare"):
        module.fluid("liquido-che-non-esiste")


def test_the_tree_is_built_on_a_model_the_rules_have_nothing_left_to_say_about() -> None:
    assert evaluate(complete(), catalog(), RuleRegistry.from_directory(RULES)).proposals == []
