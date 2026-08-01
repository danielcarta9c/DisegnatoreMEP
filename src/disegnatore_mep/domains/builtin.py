from dataclasses import dataclass

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain, IssueSeverity, PortFlow
from disegnatore_mep.validation.issues import ValidationIssue


@dataclass(frozen=True)
class BasicDomainPack:
    domain: Domain

    def validate_pair(
        self,
        port_a: PortDefinition,
        port_b: PortDefinition,
        network: NetworkModel,
    ) -> list[ValidationIssue]:
        entities = [network.id, port_a.id, port_b.id]
        if network.domain != self.domain or port_a.domain != self.domain or port_b.domain != self.domain:
            return [
                ValidationIssue(
                    code="PORT_DOMAIN_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"ports and network must belong to {self.domain.value}",
                    entity_ids=entities,
                )
            ]
        if port_a.medium != network.medium or port_b.medium != network.medium:
            return [
                ValidationIssue(
                    code="PORT_MEDIUM_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"ports must use network medium {network.medium}",
                    entity_ids=entities,
                )
            ]
        invalid_pair = port_a.flow == port_b.flow and port_a.flow != PortFlow.BIDIRECTIONAL
        if invalid_pair:
            return [
                ValidationIssue(
                    code="PORT_FLOW_MISMATCH",
                    severity=IssueSeverity.BLOCKING,
                    message=f"cannot connect two {port_a.flow.value} ports",
                    entity_ids=entities,
                )
            ]
        return []
