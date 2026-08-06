import pytest

from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

METADATA = {
    "project_id": "partition",
    "client": "Nove C",
    "project_name": "Partizione",
    "commission_code": "DEV-001",
    "revision": "00",
    "issue_date": "2026-08-04",
}

NETWORKS = [
    {"id": "heating", "name": "Riscaldamento", "domain": "hydronic", "medium": "heating_water"}
]


def link(cid: str, a: str, ap: str, b: str, bp: str) -> dict[str, object]:
    return {
        "id": cid,
        "network_id": "heating",
        "endpoint_a": {"component_id": a, "port_id": ap},
        "endpoint_b": {"component_id": b, "port_id": bp},
    }


def model(**overrides: object) -> ProjectModel:
    payload: dict[str, object] = {
        "metadata": METADATA,
        "networks": NETWORKS,
        "components": [
            {"id": item, "definition_id": "x"}
            for item in ("pump", "valve", "boiler", "terminal")
        ],
        "connections": [
            link("s1", "pump", "out", "valve", "a"),
            link("s2", "valve", "b", "boiler", "in"),
            link("s3", "boiler", "out", "terminal", "in"),
        ],
    }
    payload.update(overrides)
    return ProjectModel.model_validate(payload)


def two_sheets() -> ProjectModel:
    return model(
        subsystems=[
            {"id": "plant", "name": "Centrale",
             "component_ids": ["pump", "valve", "boiler"], "network_ids": ["heating"]},
            {"id": "zones", "name": "Zone", "component_ids": ["terminal"]},
        ],
        sheets=[
            {"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"],
             "band_assignments": [{"subsystem_id": "plant", "band": "generation", "order": 0}]},
            {"id": "t2", "title": "Zone", "subsystem_ids": ["zones"],
             "band_assignments": [{"subsystem_id": "zones", "band": "terminal", "order": 0}]},
        ],
    )


def test_a_project_without_sheets_becomes_one_partition() -> None:
    project = model()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    assert len(parts) == 1
    assert set(parts[0].component_ids) == {"pump", "valve", "boiler", "terminal"}
    assert parts[0].links == ()


def test_declared_sheets_become_partitions_in_declared_order() -> None:
    project = two_sheets()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    assert [part.sheet_id for part in parts] == ["t1", "t2"]
    assert set(parts[0].component_ids) == {"pump", "valve", "boiler"}
    assert set(parts[1].component_ids) == {"terminal"}


def test_no_component_is_lost() -> None:
    project = two_sheets()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    placed = {cid for part in parts for cid in part.component_ids}
    assert placed == {item.id for item in project.components}


def test_a_connection_across_sheets_becomes_a_pair_of_links() -> None:
    project = two_sheets()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    links = [link for part in parts for link in part.links]
    assert len(links) == 2
    assert links[0].pair_id == links[1].pair_id
    assert {link.sheet_id for link in links} == {"t1", "t2"}
    assert {link.peer_sheet_id for link in links} == {"t1", "t2"}


def test_every_link_has_exactly_one_twin() -> None:
    """La prova di accoppiamento richiesta dalla specifica §12.2."""
    project = two_sheets()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    pairs: dict[str, int] = {}
    for part in parts:
        for item in part.links:
            pairs[item.pair_id] = pairs.get(item.pair_id, 0) + 1
    assert pairs and set(pairs.values()) == {2}


def test_a_link_names_its_fluid_and_where_it_goes() -> None:
    project = two_sheets()
    parts = partition_project(project, build_trunks(project, frozenset({"valve"})))
    item = parts[0].links[0]
    assert item.network_id == "heating"
    assert item.medium == "heating_water"
    assert item.connection_id == "s3"
    assert item.port.component_id in {"boiler", "terminal"}


def test_a_run_with_accessories_stays_whole_on_one_sheet() -> None:
    project = two_sheets()
    trunks = build_trunks(project, frozenset({"valve"}))
    parts = partition_project(project, trunks)
    with_valve = [
        part for part in parts if any(item.inline_component_ids for item in part.trunks)
    ]
    assert len(with_valve) == 1
    assert "valve" in with_valve[0].component_ids


def test_a_boundary_that_cuts_a_run_with_accessories_is_refused() -> None:
    """Un accessorio sta su una tratta: se il confine la taglia, resterebbe
    senza alcuna linea su cui posarsi e sparirebbe dal disegno."""
    project = model(
        subsystems=[
            {"id": "plant", "name": "Centrale", "component_ids": ["pump", "valve"]},
            {"id": "zones", "name": "Zone", "component_ids": ["boiler", "terminal"]},
        ],
        sheets=[
            {"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"],
             "band_assignments": [{"subsystem_id": "plant", "band": "generation", "order": 0}]},
            {"id": "t2", "title": "Zone", "subsystem_ids": ["zones"],
             "band_assignments": [{"subsystem_id": "zones", "band": "terminal", "order": 0}]},
        ],
    )
    with pytest.raises(LayoutError, match="must not carry any"):
        partition_project(project, build_trunks(project, frozenset({"valve"})))


def test_an_empty_sheet_is_refused() -> None:
    project = model(
        subsystems=[
            {"id": "plant", "name": "Centrale",
             "component_ids": ["pump", "valve", "boiler", "terminal"]}
        ],
        sheets=[
            {"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"],
             "band_assignments": [{"subsystem_id": "plant", "band": "generation", "order": 0}]},
            {"id": "t2", "title": "Vuota", "subsystem_ids": []},
        ],
    )
    with pytest.raises(LayoutError, match="carries no component"):
        partition_project(project, build_trunks(project, frozenset({"valve"})))


def test_a_component_in_no_subsystem_is_refused_when_sheets_are_declared() -> None:
    project = model(
        subsystems=[
            {"id": "plant", "name": "Centrale", "component_ids": ["pump", "valve", "boiler"]}
        ],
        sheets=[
            {"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"],
             "band_assignments": [{"subsystem_id": "plant", "band": "generation", "order": 0}]},
        ],
    )
    with pytest.raises(LayoutError, match=r"belong to no sheet.*\['terminal'\]"):
        partition_project(project, build_trunks(project, frozenset({"valve"})))


def test_a_component_on_two_sheets_is_refused() -> None:
    project = model(
        subsystems=[
            {"id": "plant", "name": "Centrale",
             "component_ids": ["pump", "valve", "boiler", "terminal"]},
            {"id": "zones", "name": "Zone", "component_ids": ["boiler"]},
        ],
        sheets=[
            {"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"],
             "band_assignments": [{"subsystem_id": "plant", "band": "generation", "order": 0}]},
            {"id": "t2", "title": "Zone", "subsystem_ids": ["zones"],
             "band_assignments": [{"subsystem_id": "zones", "band": "terminal", "order": 0}]},
        ],
    )
    with pytest.raises(LayoutError, match="boiler.*more than one sheet"):
        partition_project(project, build_trunks(project, frozenset({"valve"})))


def test_the_partition_is_deterministic() -> None:
    project = two_sheets()
    trunks = build_trunks(project, frozenset({"valve"}))
    runs = {
        tuple(
            (part.sheet_id, part.component_ids, tuple(item.id for item in part.links))
            for part in partition_project(project, trunks)
        )
        for _ in range(5)
    }
    assert len(runs) == 1
