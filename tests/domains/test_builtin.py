import pytest

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.domains.builtin import BasicDomainPack
from disegnatore_mep.domains.registry import DomainRegistry, default_domain_registry
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain, PortFlow


def port(domain: Domain, medium: str, flow: PortFlow) -> PortDefinition:
    return PortDefinition(
        id="p",
        domain=domain,
        medium=medium,
        flow=flow,
        x_mm=0,
        y_mm=0,
        angle_deg=0,
    )


def test_all_domains_have_a_pack() -> None:
    registry = default_domain_registry()
    assert {pack.domain for pack in registry.all()} == set(Domain)


def test_pack_rejects_cross_medium_connection() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "chilled_water", PortFlow.IN),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_MEDIUM_MISMATCH"]


def test_pack_accepts_output_to_input() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "heating_water", PortFlow.IN),
        network,
    )
    assert issues == []


def test_pack_rejects_port_domain_mismatch() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.AERAULIC, "heating_water", PortFlow.IN),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_DOMAIN_MISMATCH"]


def test_pack_rejects_two_output_ports() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_FLOW_MISMATCH"]


def test_pack_accepts_two_bidirectional_ports() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.BIDIRECTIONAL),
        port(Domain.HYDRONIC, "heating_water", PortFlow.BIDIRECTIONAL),
        network,
    )
    assert issues == []


def test_registry_rejects_duplicate_domain_pack() -> None:
    with pytest.raises(ValueError, match="duplicate domain pack"):
        DomainRegistry([BasicDomainPack(Domain.HYDRONIC), BasicDomainPack(Domain.HYDRONIC)])


def test_registry_raises_for_missing_domain_pack() -> None:
    registry = DomainRegistry([])
    with pytest.raises(ValueError, match="missing domain pack"):
        registry.get(Domain.HYDRONIC)
