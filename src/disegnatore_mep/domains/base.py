from typing import Protocol

from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import NetworkModel
from disegnatore_mep.model.types import Domain
from disegnatore_mep.validation.issues import ValidationIssue


class DomainPack(Protocol):
    """Contract for a per-domain vocabulary and compatibility validator.

    `domain` is declared read-only so that immutable implementations
    (frozen dataclasses) satisfy the protocol; a class exposing a plain
    mutable attribute satisfies it too.
    """

    @property
    def domain(self) -> Domain: ...

    def validate_pair(
        self,
        port_a: PortDefinition,
        port_b: PortDefinition,
        network: NetworkModel,
    ) -> list[ValidationIssue]:
        raise NotImplementedError
