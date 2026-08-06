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


class RuleGap(StrictModel):
    """Una regola che si applica, e non ha niente da proporre.

    Non e' la stessa cosa di una regola che non si applica. Qui le condizioni
    sono vere — c'e' un pezzo che chiede quell'accessorio — ma il catalogo non
    ha nessuna voce che porti quella funzione su quel fluido. **Tacere sarebbe
    inventare al contrario**: l'ingegnere leggerebbe un elenco completo di
    integrazioni e crederebbe che non manchi niente.

    Non blocca. E' un punto aperto che entra nel dossier accanto alle proposte,
    con la stessa categoria della regola che lo ha generato: se la regola era
    necessaria, il punto aperto e' necessario.
    """

    rule_id: str = Field(pattern=ID_PATTERN)
    rule_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    category: IntegrationCategory
    name: str = Field(min_length=1)
    network_id: str = Field(pattern=ID_PATTERN)
    medium: str = Field(pattern=ID_PATTERN)
    anchor: PortRef
    """Il primo attacco rimasto scoperto. Ce ne possono essere altri sulla
    stessa rete: il punto aperto e' uno solo perche' il pezzo che manca in
    catalogo e' uno solo."""

    missing_function: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    source: str = Field(min_length=1)

    @property
    def key(self) -> tuple[str, str, str, str]:
        """Cosa rende due punti aperti lo stesso punto aperto."""
        return (self.rule_id, self.network_id, self.missing_function, self.medium)


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

    service_port: str | None = Field(default=None, pattern=ID_PATTERN)
    """L'attacco di servizio dell'ancoraggio su cui questo accessorio si appende.

    Vale solo per gli accessori che pendono da uno stacco (D-101). Se e'
    valorizzato, la macchina quell'attacco ce l'ha e l'accessorio ci si collega;
    se e' vuoto, la macchina non ce l'ha e lo stacco si apre sulla tubazione, con
    un raccordo. Chi applica non lo ridecide: lo ha gia' stabilito chi ha
    valutato la regola, guardando cosa la macchina dichiara.
    """

    rationale: str = Field(min_length=1)
    source: str = Field(min_length=1)


def proposed_component_id(definition_id: str, anchor: PortRef) -> str:
    """Identificativo derivato dai dati, mai da un contatore.

    Un contatore renderebbe il modello dipendente dall'ordine in cui le proposte
    sono state approvate: rieseguire produrrebbe identificativi diversi e il
    disegno non sarebbe piu' rigenerabile identico (§3.4 del piano).
    """
    return f"{definition_id}-{anchor.component_id}-{anchor.port_id}".replace("_", "-")


__all__ = ["RuleGap", "RuleProposal", "proposed_component_id"]
