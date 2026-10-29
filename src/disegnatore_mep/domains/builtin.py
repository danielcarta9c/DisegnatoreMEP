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
        # **Una tubazione si scrive nel verso del fluido**: dall'attacco da cui esce a
        # quello in cui entra. La lettura dell'impianto lo pretende (`graph.plant`), e
        # se non lo trova si ferma; la tabella delle apparecchiature allora ripiega
        # sulle sole sigle dell'ingegnere, e tutte le altre spariscono in silenzio. E'
        # il «sigle tutte o niente» del kit aria-aria (REL-012, §6.1): due tubazioni
        # dell'alimentazione erano scritte dall'ingresso della macchina verso il
        # quadro, e nessuno lo diceva. Un attacco senza verso (`bidirectional`) va
        # bene da tutt'e due le parti.
        if port_a.flow == PortFlow.IN or port_b.flow == PortFlow.OUT:
            return [
                ValidationIssue(
                    code="CONNECTION_WRITTEN_BACKWARDS",
                    severity=IssueSeverity.BLOCKING,
                    message=(
                        f"la tubazione e' scritta al contrario: va da {port_a.id} "
                        f"({port_a.flow.value}) a {port_b.id} ({port_b.flow.value}); si scrive "
                        f"dall'attacco da cui il fluido esce (endpoint_a) a quello in cui entra "
                        f"(endpoint_b), o la lettura dell'impianto si ferma e le sigle della "
                        f"famiglia non si assegnano"
                    ),
                    entity_ids=entities,
                )
            ]
        return []
