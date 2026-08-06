"""L'indirizzo dei nodi (D-105): le proprieta' dei criteri di accettazione.

Le prove asseriscono le regole della strada dove vivono — sulla linea, sul
nodo, sul civico — e mai su un totale: la principale tira dritto, la
secondaria muore sul nodo, i rami prendono la lettera, gli stacchi il civico.
E la proprieta' che governa tutto il grafo: stesso impianto, stessi indirizzi,
comunque sia scritto il file.
"""

import random
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import (
    LineFamilyEntry,
    LineNaming,
    Naming,
    NamingError,
    PlantLines,
    read_lines,
    read_plant,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PLANTS = sorted((ROOT / "examples" / "prova").glob("prova-*.json"))
CATALOG = ROOT / "examples" / "layout" / "catalog"
FOUNDATION_CATALOG = ROOT / "examples" / "foundation" / "catalog"
MIXED = ROOT / "examples" / "foundation" / "valid-mixed-project.json"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
RULES = ROOT / "rules" / "hydronic"

EVERY_PLANT = pytest.mark.parametrize(
    "plant", [str(item) for item in PLANTS], ids=[item.stem for item in PLANTS]
)


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def naming() -> Naming:
    return Naming.from_directory(NAMING)


def line_naming() -> LineNaming:
    return LineNaming.from_directory(NAMING)


def completed(plant: str) -> ProjectModel:
    registry = catalog()
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(registry)
    done, _, _ = saturate(load_project(Path(plant)), registry, rules)
    return done


def lines_of(project: ProjectModel, registry: ComponentRegistry) -> PlantLines:
    return read_lines(
        project, registry, read_plant(project, registry, naming()), line_naming()
    )


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


# --- stesso impianto, stessi indirizzi ------------------------------------------


@EVERY_PLANT
def test_same_plant_same_addresses_whatever_the_file_order(plant: str) -> None:
    registry = catalog()
    project = completed(plant)
    base = lines_of(project, registry)
    for seed in range(6):
        other = lines_of(shuffled(project, seed), registry)
        assert other.addresses == base.addresses, seed
        assert [
            (item.name, item.node_ids, item.branch_of) for item in other.lines
        ] == [(item.name, item.node_ids, item.branch_of) for item in base.lines], seed
        assert other.hanging == base.hanging, seed


# --- un solo indirizzo per pezzo, e nessun pezzo senza ---------------------------


@EVERY_PLANT
def test_every_piece_has_exactly_one_address(plant: str) -> None:
    registry = catalog()
    project = completed(plant)
    lines = lines_of(project, registry)
    addressed = set(lines.addresses)
    assert addressed == {item.id for item in project.components}
    values = list(lines.addresses.values())
    assert len(values) == len(set(values))


@EVERY_PLANT
def test_every_run_pipe_sits_on_exactly_one_line(plant: str) -> None:
    """Una linea con N nodi copre N-1 tubazioni: se i conti tornano rete per
    rete, nessuna tubazione e' rimasta fuori e nessuna sta su due linee."""
    registry = catalog()
    project = completed(plant)
    lines = lines_of(project, registry)
    for network_id, pipes in lines.run_pipes.items():
        spanned = sum(
            len(item.node_ids) - 1
            for item in lines.lines
            if item.network_id == network_id
        )
        assert spanned == len(pipes), network_id


# --- le regole della strada, come il PM le ha date -------------------------------


def test_the_first_supply_line_reads_as_the_pm_wrote_it() -> None:
    """«cp.01.n.01 e' l'uscita della pdc»: la prima mandata primaria parte
    dalla prima sorgente, e il suo capo e' il nodo numero uno."""
    registry = catalog()
    project = completed(str(PLANTS[0]))
    graph = read_plant(project, registry, naming())
    lines = lines_of(project, registry)
    first = lines.line("CP.01")
    head = first.node_ids[0]
    assert graph.node(head).sigla == "PDC-01"
    assert lines.addresses[head] == "CP.01.N.01"
    assert graph.node(first.node_ids[-1]).sigla == "ACC-01"


def test_where_two_lines_meet_the_secondary_dies_on_the_node() -> None:
    """La mandata del secondo generatore e' una linea numerata a se', e muore
    su un nodo della principale."""
    registry = catalog()
    project = completed(str(PLANTS[0]))
    graph = read_plant(project, registry, naming())
    lines = lines_of(project, registry)
    second = lines.line("CP.02")
    assert graph.node(second.node_ids[0]).sigla == "PDC-02"
    tail = second.node_ids[-1]
    assert lines.owner[tail] == "CP.01"


def test_on_the_common_return_the_branch_takes_the_letter() -> None:
    """«RP.01 arriva alla prima e RP.01a alla seconda» — testuale da D-105."""
    registry = catalog()
    project = completed(str(PLANTS[0]))
    graph = read_plant(project, registry, naming())
    lines = lines_of(project, registry)
    principal = lines.line("RP.01")
    branch = lines.line("RP.01a")
    assert graph.node(principal.node_ids[-1]).sigla == "PDC-01"
    assert graph.node(branch.node_ids[-1]).sigla == "PDC-02"
    assert branch.branch_of == "RP.01"


def test_what_hangs_from_a_stub_is_a_civic_number_of_the_node() -> None:
    """La catena appesa — bloccabile e vaso — porta i civici del proprio nodo,
    nell'ordine della catena."""
    registry = catalog()
    project = completed(str(PLANTS[0]))
    graph = read_plant(project, registry, naming())
    lines = lines_of(project, registry)
    vessel = next(
        item.component_id
        for item in graph.nodes
        if item.sigla.startswith("VE-")
    )
    node = next(item for item, chain in lines.hanging.items() if vessel in chain)
    chain = lines.hanging[node]
    root = lines.addresses[node]
    for index, hung in enumerate(chain, start=1):
        assert lines.addresses[hung] == f"{root}.{index}"
    assert lines.addresses[vessel] == f"{root}.2"


def test_the_ricircolo_is_a_lettered_branch_that_closes_its_ring() -> None:
    """Nel quinto impianto il ricircolo si stacca dalla mandata sanitaria e vi
    si richiude: e' `ACS.01a`, e le utenze restano sulla principale."""
    registry = catalog()
    project = completed(str(PLANTS[4]))
    graph = read_plant(project, registry, naming())
    lines = lines_of(project, registry)
    principal = lines.line("ACS.01")
    assert graph.node(principal.node_ids[-1]).sigla == "ACS-01"
    branch = lines.line("ACS.01a")
    assert branch.branch_of == "ACS.01"
    assert lines.owner[branch.node_ids[-1]] == "ACS.01"


@EVERY_PLANT
def test_the_line_families_come_from_the_table(plant: str) -> None:
    registry = catalog()
    lines = lines_of(completed(plant), registry)
    table = {item.prefix: item.name for item in line_naming().families}
    for line in lines.lines:
        assert line.family_prefix in table
        assert line.family_name == table[line.family_prefix]
        assert line.name.startswith(f"{line.family_prefix}.")


# --- cio' che non si sa dire non si tace -----------------------------------------


def test_a_line_the_table_cannot_name_stops_naming_the_culprit() -> None:
    table = LineNaming(
        families=(
            LineFamilyEntry(
                medium="heating_water",
                fed_by="generator",
                direction="supply",
                prefix="CP",
                name="mandata primaria",
            ),
        )
    )
    with pytest.raises(NamingError) as caught:
        table.family_for(
            medium="heating_water", fed_by="generator", direction="return"
        )
    assert "heating_water" in str(caught.value)
    assert "return" in str(caught.value)


# --- le linee sono idrauliche ----------------------------------------------------


def test_networks_that_carry_no_water_have_no_lines() -> None:
    registry = ComponentRegistry.from_directory(FOUNDATION_CATALOG)
    project = load_project(MIXED)
    lines = read_lines(
        project, registry, read_plant(project, registry, naming()), line_naming()
    )
    hydronic = {
        item.id for item in project.networks if item.domain is Domain.HYDRONIC
    }
    assert hydronic
    assert {item.network_id for item in lines.lines} <= hydronic
    assert set(lines.run_pipes) <= hydronic
