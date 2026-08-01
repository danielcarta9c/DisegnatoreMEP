from collections.abc import Sequence

from disegnatore_mep.model.types import Domain

from .base import DomainPack
from .builtin import BasicDomainPack


class DomainRegistry:
    def __init__(self, packs: Sequence[DomainPack]) -> None:
        self._packs: dict[Domain, DomainPack] = {}
        for pack in packs:
            if pack.domain in self._packs:
                raise ValueError(f"duplicate domain pack: {pack.domain.value}")
            self._packs[pack.domain] = pack

    def get(self, domain: Domain) -> DomainPack:
        try:
            return self._packs[domain]
        except KeyError as exc:
            raise ValueError(f"missing domain pack: {domain.value}") from exc

    def all(self) -> tuple[DomainPack, ...]:
        return tuple(self._packs[key] for key in sorted(self._packs, key=str))


def default_domain_registry() -> DomainRegistry:
    return DomainRegistry([BasicDomainPack(domain) for domain in Domain])
