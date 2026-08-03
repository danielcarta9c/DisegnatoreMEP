import pytest

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.domains.builtin import BasicDomainPack
from disegnatore_mep.domains.registry import DomainRegistry, default_domain_registry
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain, IssueSeverity, PortFlow


def port(domain: Domain, medium: str, flow: PortFlow) -> PortDefinition:
    return PortDefinition(
        id="p",
        domain=domain,
        medium=medium,
        flow=flow,
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


def test_domain_mismatch_takes_precedence_over_medium() -> None:
    # validate_pair returns on the first matching branch in the fixed order
    # domain -> medium -> flow. This pair violates both domain and medium;
    # pinning that only PORT_DOMAIN_MISMATCH surfaces is deliberate, not
    # incidental, because later consumers (the topology validator) depend
    # on this precedence to report a single, unambiguous issue per pair.
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.AERAULIC, "supply_air", PortFlow.OUT),
        port(Domain.AERAULIC, "supply_air", PortFlow.IN),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_DOMAIN_MISMATCH"]
    assert issues[0].severity == IssueSeverity.BLOCKING


def test_medium_mismatch_takes_precedence_over_flow() -> None:
    # Same deliberate-ordering guarantee as above, one branch down: a pair
    # with matching domain but wrong medium AND a repeated non-bidirectional
    # flow must report only PORT_MEDIUM_MISMATCH, not PORT_FLOW_MISMATCH.
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    issues = registry.get(Domain.HYDRONIC).validate_pair(
        port(Domain.HYDRONIC, "chilled_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "chilled_water", PortFlow.OUT),
        network,
    )
    assert [issue.code for issue in issues] == ["PORT_MEDIUM_MISMATCH"]
    assert issues[0].severity == IssueSeverity.BLOCKING


def test_all_mismatch_branches_are_blocking() -> None:
    registry = default_domain_registry()
    network = NetworkModel(
        id="heating",
        name="Riscaldamento",
        domain=Domain.HYDRONIC,
        medium="heating_water",
    )
    pack = registry.get(Domain.HYDRONIC)
    domain_mismatch = pack.validate_pair(
        port(Domain.AERAULIC, "heating_water", PortFlow.OUT),
        port(Domain.AERAULIC, "heating_water", PortFlow.IN),
        network,
    )
    medium_mismatch = pack.validate_pair(
        port(Domain.HYDRONIC, "chilled_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "chilled_water", PortFlow.IN),
        network,
    )
    flow_mismatch = pack.validate_pair(
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        port(Domain.HYDRONIC, "heating_water", PortFlow.OUT),
        network,
    )
    for issues in (domain_mismatch, medium_mismatch, flow_mismatch):
        assert issues != []
        assert all(issue.severity == IssueSeverity.BLOCKING for issue in issues)
