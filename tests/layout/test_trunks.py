import pytest

from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

METADATA = {
    "project_id": "trunks",
    "client": "Nove C",
    "project_name": "Tratte",
    "commission_code": "DEV-001",
    "revision": "00",
    "issue_date": "2026-08-04",
}


def link(cid: str, a: str, ap: str, b: str, bp: str, network: str = "heating") -> dict[str, object]:
    return {
        "id": cid,
        "network_id": network,
        "endpoint_a": {"component_id": a, "port_id": ap},
        "endpoint_b": {"component_id": b, "port_id": bp},
    }


def project(
    connections: list[dict[str, object]],
    components: list[str],
    networks: list[dict[str, object]] | None = None,
) -> ProjectModel:
    return ProjectModel.model_validate(
        {
            "metadata": METADATA,
            "networks": networks
            or [
                {
                    "id": "heating",
                    "name": "Riscaldamento",
                    "domain": "hydronic",
                    "medium": "heating_water",
                }
            ],
            "components": [{"id": item, "definition_id": "x"} for item in components],
            "connections": connections,
        }
    )


def test_three_accessories_collapse_into_one_run() -> None:
    model = project(
        [
            link("s1", "pump", "out", "valve", "a"),
            link("s2", "valve", "b", "strainer", "a"),
            link("s3", "strainer", "b", "check", "a"),
            link("s4", "check", "b", "boiler", "in"),
        ],
        ["pump", "valve", "strainer", "check", "boiler"],
    )
    trunks = build_trunks(model, frozenset({"valve", "strainer", "check"}))
    assert len(trunks) == 1
    trunk = trunks[0]
    assert trunk.start.component_id == "pump"
    assert trunk.end.component_id == "boiler"
    assert trunk.connection_ids == ("s1", "s2", "s3", "s4")
    assert trunk.inline_component_ids == ("valve", "strainer", "check")
    assert trunk.network_id == "heating"


def test_a_run_without_accessories_is_still_a_run() -> None:
    model = project([link("s1", "pump", "out", "boiler", "in")], ["pump", "boiler"])
    trunks = build_trunks(model, frozenset())
    assert len(trunks) == 1
    assert trunks[0].connection_ids == ("s1",)
    assert trunks[0].inline_component_ids == ()


def test_every_connection_lands_in_exactly_one_run() -> None:
    model = project(
        [
            link("a1", "pump", "out", "valve", "a"),
            link("a2", "valve", "b", "boiler", "in"),
            link("b1", "boiler", "out", "vessel", "a"),
        ],
        ["pump", "valve", "boiler", "vessel"],
    )
    trunks = build_trunks(model, frozenset({"valve"}))
    seen = [cid for trunk in trunks for cid in trunk.connection_ids]
    assert sorted(seen) == ["a1", "a2", "b1"]
    assert len(seen) == len(set(seen))


def test_the_result_is_deterministic() -> None:
    model = project(
        [
            link("a1", "pump", "out", "valve", "a"),
            link("a2", "valve", "b", "boiler", "in"),
            link("b1", "boiler", "out", "vessel", "a"),
        ],
        ["pump", "valve", "boiler", "vessel"],
    )
    runs = {
        tuple(trunk.connection_ids for trunk in build_trunks(model, frozenset({"valve"})))
        for _ in range(5)
    }
    assert len(runs) == 1


def test_an_accessory_with_one_connection_is_refused() -> None:
    model = project([link("s1", "pump", "out", "valve", "a")], ["pump", "valve"])
    with pytest.raises(LayoutError, match="needs two"):
        build_trunks(model, frozenset({"valve"}))


def test_an_accessory_bridging_two_networks_is_refused() -> None:
    model = project(
        [
            link("s1", "pump", "out", "valve", "a"),
            link("s2", "valve", "b", "chiller", "in", network="chilled"),
        ],
        ["pump", "valve", "chiller"],
        networks=[
            {"id": "heating", "name": "R", "domain": "hydronic", "medium": "heating_water"},
            {"id": "chilled", "name": "F", "domain": "hydronic", "medium": "chilled_water"},
        ],
    )
    with pytest.raises(LayoutError, match="joins two networks"):
        build_trunks(model, frozenset({"valve"}))


def test_a_ring_of_accessories_alone_is_refused() -> None:
    """Una tratta di soli accessori non tocca nessun componente: sparirebbe."""
    model = project(
        [
            link("s1", "valve", "b", "strainer", "a"),
            link("s2", "strainer", "b", "valve", "a"),
        ],
        ["valve", "strainer"],
    )
    with pytest.raises(LayoutError, match="belong to no run"):
        build_trunks(model, frozenset({"valve", "strainer"}))


def test_the_run_reports_the_ports_it_starts_and_ends_on() -> None:
    model = project(
        [
            link("s1", "pump", "out", "valve", "a"),
            link("s2", "valve", "b", "boiler", "return"),
        ],
        ["pump", "valve", "boiler"],
    )
    trunk = build_trunks(model, frozenset({"valve"}))[0]
    assert (trunk.start.component_id, trunk.start.port_id) == ("pump", "out")
    assert (trunk.end.component_id, trunk.end.port_id) == ("boiler", "return")
