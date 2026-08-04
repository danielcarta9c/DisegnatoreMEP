"""Una proposta: cosa, dove, perche', e da quale regola.

Non e' una modifica. Il motore le produce, l'ingegnere le approva, e solo dopo
qualcuno le applica (§9.2). Il campo che conta per il dossier e' `rationale`:
una proposta senza motivazione non e' rappresentabile, perche' non ci sarebbe
niente da approvare.
"""

from pydantic import Field

from disegnatore_mep.model.base import ID_PATTERN, StrictModel
from disegnatore_mep.model.project import PortRef
from disegnatore_mep.model.types import IntegrationCategory


class RuleProposal(StrictModel):
    """Un accessorio proposto su un attacco di un componente esistente."""

    rule_id: str = Field(pattern=ID_PATTERN)
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    category: IntegrationCategory
    component_id: str = Field(pattern=ID_PATTERN)
    definition_id: str = Field(pattern=ID_PATTERN)
    name: str = Field(min_length=1)
    network_id: str = Field(pattern=ID_PATTERN)
    anchor: PortRef
    """L'attacco su cui si posa. La connessione si ritrova al momento di
    applicare, non si registra qui: se un'altra proposta e' gia' stata applicata
    sullo stesso attacco, la connessione di allora non esiste piu'."""

    inlet_port: str = Field(pattern=ID_PATTERN)
    outlet_port: str = Field(pattern=ID_PATTERN)
    rationale: str = Field(min_length=1)
    source: str = Field(min_length=1)


def proposed_component_id(definition_id: str, anchor: PortRef) -> str:
    """Identificativo derivato dai dati, mai da un contatore.

    Un contatore renderebbe il modello dipendente dall'ordine in cui le proposte
    sono state approvate: rieseguire produrrebbe identificativi diversi e il
    disegno non sarebbe piu' rigenerabile identico (§3.4 del piano).
    """
    return f"{definition_id}-{anchor.component_id}-{anchor.port_id}".replace("_", "-")


__all__ = ["RuleProposal", "proposed_component_id"]
