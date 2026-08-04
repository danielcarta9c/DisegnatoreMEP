"""Il report delle integrazioni: il materiale del dossier di approvazione.

La skill lo presentera' (§5.3), il nucleo lo produce. Raggruppato per categoria
perche' e' cosi' che si legge: prima cosa serve per forza, poi cosa e'
consigliato, poi cosa dipende dal caso.
"""

from pydantic import Field

from disegnatore_mep.model.base import StrictModel
from disegnatore_mep.model.types import IntegrationCategory

from .proposal import RuleProposal

CATEGORY_LABELS: dict[IntegrationCategory, str] = {
    IntegrationCategory.NECESSARY: "Necessarie",
    IntegrationCategory.RECOMMENDED: "Raccomandate",
    IntegrationCategory.CONDITIONAL: "Condizionate",
}


class IntegrationEntry(StrictModel):
    category: IntegrationCategory
    name: str
    where: str
    """Dove, in parole: «sul ritorno di hp». La posizione sulla tavola non c'entra."""

    rationale: str
    source: str
    rule: str


class IntegrationReport(StrictModel):
    entries: list[IntegrationEntry] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.entries

    def of(self, category: IntegrationCategory) -> list[IntegrationEntry]:
        return [item for item in self.entries if item.category == category]


def build_report(proposals: list[RuleProposal]) -> IntegrationReport:
    order = list(IntegrationCategory)
    ranked = sorted(proposals, key=lambda item: order.index(item.category))
    return IntegrationReport(
        entries=[
            IntegrationEntry(
                category=item.category,
                name=item.name,
                where=f"su {item.anchor.component_id}.{item.anchor.port_id}, "
                f"rete {item.network_id}",
                rationale=item.rationale,
                source=item.source,
                rule=f"{item.rule_id}@{item.rule_version}",
            )
            for item in ranked
        ]
    )


__all__ = ["CATEGORY_LABELS", "IntegrationEntry", "IntegrationReport", "build_report"]
