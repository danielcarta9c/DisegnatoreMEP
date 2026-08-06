"""Il report delle integrazioni: il materiale del dossier di approvazione.

La skill lo presentera' (§5.3), il nucleo lo produce. Raggruppato per categoria
perche' e' cosi' che si legge: prima cosa serve per forza, poi cosa e'
consigliato, poi cosa dipende dal caso.
"""

from pydantic import Field

from disegnatore_mep.catalog.tags import family_in_words, fluid_in_words
from disegnatore_mep.model.base import StrictModel
from disegnatore_mep.model.types import IntegrationCategory

from .proposal import RuleGap, RuleProposal

CATEGORY_LABELS: dict[IntegrationCategory, str] = {
    IntegrationCategory.NECESSARY: "Necessarie",
    IntegrationCategory.RECOMMENDED: "Raccomandate",
    IntegrationCategory.CONDITIONAL: "Condizionate",
}

CATEGORY_ADJECTIVES: dict[IntegrationCategory, str] = {
    IntegrationCategory.NECESSARY: "necessario",
    IntegrationCategory.RECOMMENDED: "raccomandato",
    IntegrationCategory.CONDITIONAL: "condizionato",
}
"""La categoria di un punto aperto e' quella della regola che lo ha generato:
un accessorio necessario che manca in catalogo e' un punto aperto necessario."""


class IntegrationEntry(StrictModel):
    category: IntegrationCategory
    name: str
    where: str
    """Dove, in parole: «sul ritorno di hp». La posizione sulla tavola non c'entra."""

    rationale: str
    source: str
    rule: str


class OpenPoint(StrictModel):
    """Un accessorio che ci vorrebbe e che non si puo' proporre.

    Non e' un'integrazione mancata per scelta: e' una lacuna del catalogo, e va
    letta come una domanda al progettista invece che come un silenzio."""

    category: IntegrationCategory
    name: str
    where: str
    what_is_missing: str
    """In parole: quale mestiere nessun pezzo di catalogo sa fare su quel fluido."""

    rationale: str
    source: str
    rule: str


class IntegrationReport(StrictModel):
    entries: list[IntegrationEntry] = Field(default_factory=list)
    open_points: list[OpenPoint] = Field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Niente da proporre **e** niente da segnalare.

        I punti aperti contano: un dossier che dicesse «il modello e' gia'
        completo» mentre un accessorio necessario non e' proponibile
        mentirebbe."""
        return not self.entries and not self.open_points

    def of(self, category: IntegrationCategory) -> list[IntegrationEntry]:
        return [item for item in self.entries if item.category == category]


def build_report(
    proposals: list[RuleProposal], gaps: list[RuleGap] | None = None
) -> IntegrationReport:
    order = list(IntegrationCategory)
    ranked = sorted(proposals, key=lambda item: order.index(item.category))
    pending = sorted(gaps or [], key=lambda item: order.index(item.category))
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
        ],
        open_points=[
            OpenPoint(
                category=item.category,
                name=item.name,
                where=f"su {item.anchor.component_id}.{item.anchor.port_id}, "
                f"rete {item.network_id}",
                what_is_missing=(
                    f"in catalogo non c'e' nessun pezzo che faccia da "
                    f"{family_in_words(item.missing_function).lower()} su "
                    f"{fluid_in_words(item.medium)}, quindi questo accessorio "
                    f"{CATEGORY_ADJECTIVES[item.category]} non viene proposto: "
                    f"va deciso dal progettista"
                ),
                rationale=item.rationale,
                source=item.source,
                rule=f"{item.rule_id}@{item.rule_version}",
            )
            for item in pending
        ],
    )


__all__ = [
    "CATEGORY_ADJECTIVES",
    "CATEGORY_LABELS",
    "IntegrationEntry",
    "IntegrationReport",
    "OpenPoint",
    "build_report",
]
