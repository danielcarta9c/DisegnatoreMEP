"""Le viste del grafo: la tavola unica, l'idraulica, l'elettrico e il comando.

**Il PO, il 29 ottobre 2026** (I-227): «sulle tavole di centrale o dove è già molto
denso meglio disegnare l'elettrico e comando su tavola separata. Su tavole piccole
come quella di sola distribuzione oppure come il caso dell'esempio (una sola
macchina canalizzata con singolo FC) si puo' fare su tavola unica».

**Lo stesso grafo, tre viste** — e la vista la sceglie il piano (`vista`), perche'
e' una decisione su come si compone la tavola, non sull'impianto:

- **`tutto`**, la tavola unica: il grafo intero. E' la vista di sempre, e senza
  elettrico nel grafo e' l'unica che esiste;
- **`idraulica`**: il grafo **senza il dominio del comando** — niente cavi e bus, e
  niente pezzi che stanno solo sul comando (il quadro, il sezionatore, il
  regolatore, la sonda esterna). La sonda a immersione **resta**, sul suo tubo: il
  pozzetto e' un fatto idraulico, e chi monta deve sapere dove va (*proposta*);
  perde il suo cavo;
- **`elettrico`**: **il solo dominio del comando** — i cavi, i bus, e i pezzi che
  toccano: il quadro, il regolatore, le sonde, e le macchine, i circolatori e le
  valvole che hanno un cavo. Le linee dell'acqua non ci sono. Un circolatore, che
  sull'idraulica sta in linea sul suo tubo, qui non ha il tubo e il piano lo posa
  come un pezzo (`ComponentRegistry.per_il_progetto`).

**Le sigle sono quelle del grafo intero.** La lettura dell'impianto numera i pezzi
nell'ordine in cui li incontra, e una vista che ne toglie qualcuno numererebbe gli
altri in un altro modo: la stessa pompa di calore sarebbe PDC-02 su una tavola e
PDC-01 sull'altra. La vista scrive percio' sul pezzo la sigla che il grafo intero
gli da', e su tutte e due le tavole la stessa macchina porta la stessa sigla.

**Le due tavole si rimandano**: il titolo dice quale delle due e', e una riga della
legenda dice dove sta l'altra (`rimando`).
"""

from __future__ import annotations

from typing import Literal

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ComponentInstance, ProjectModel
from disegnatore_mep.model.types import Domain

Vista = Literal["tutto", "idraulica", "elettrico"]
"""Le tre viste dello stesso grafo."""

VISTE: tuple[str, ...] = ("tutto", "idraulica", "elettrico")

TITOLO_DELLA_VISTA: dict[str, str] = {
    "idraulica": "idraulica",
    "elettrico": "elettrico e comando",
}
"""Come la vista si dice nel titolo della tavola. *Proposta della sessione.*"""

SUFFISSO_DEL_NUMERO = "-E"
"""Il numero della tavola dell'elettrico: quello dell'idraulica con «-E». *Proposta
della sessione*: la numerazione degli elaborati e' del PO."""

CAMPIONE_DEL_RIMANDO = "Vedi"
"""Il campione della riga di legenda che rimanda all'altra tavola."""


def _dominio_delle_reti(modello: ProjectModel) -> dict[str, Domain]:
    return {item.id: item.domain for item in modello.networks}


def ha_il_comando(modello: ProjectModel) -> bool:
    """Se il grafo porta almeno un cavo o un bus."""
    domini = _dominio_delle_reti(modello)
    return any(domini.get(item.network_id) is Domain.CONTROL for item in modello.connections)


def solo_comando(modello: ProjectModel, catalogo: ComponentRegistry) -> frozenset[str]:
    """I pezzi che stanno **solo** sul comando: tutte le loro porte sono cavi o bus.

    Si legge sulla voce come il registro la mostra, con le porte di comando delle
    macchine messe da parte: una pompa di calore ha l'acqua, e non e' fra questi."""
    return frozenset(
        item.id
        for item in modello.components
        if all(port.domain is Domain.CONTROL for port in catalogo.get(item.definition_id).ports)
    )


def numero_della_tavola(modello: ProjectModel, vista: str) -> str | None:
    """Il numero della tavola di quella vista, dai metadati del grafo."""
    numero = modello.metadata.sheet_number
    if numero is None or vista != "elettrico":
        return numero
    return numero + SUFFISSO_DEL_NUMERO


def rimando(modello: ProjectModel, vista: str) -> str | None:
    """La riga di legenda che dice dove sta l'altra tavola, o `None` per la tavola unica."""
    if vista == "tutto":
        return None
    altra = "elettrico" if vista == "idraulica" else "idraulica"
    numero = numero_della_tavola(modello, altra)
    dove = f"tavola {numero}" if numero else "la tavola"
    return f"{dove} «{TITOLO_DELLA_VISTA[altra]}», dallo stesso schema"


def _sigle_del_grafo_intero(
    modello: ProjectModel, catalogo: ComponentRegistry, naming: object
) -> dict[str, str]:
    """Le sigle che la lettura dell'impianto da' sul grafo intero, o nessuna se il
    grafo non si legge: allora valgono quelle che l'ingegnere ha scritto."""
    from pathlib import Path

    from disegnatore_mep.graph.naming import Naming, NamingError
    from disegnatore_mep.graph.plant import GraphError, read_plant

    if not isinstance(naming, Path):
        return {}
    try:
        return dict(read_plant(modello, catalogo, Naming.from_directory(naming)).sigle)
    except (GraphError, NamingError):
        return {}


def vista_del_grafo(
    modello: ProjectModel,
    vista: str,
    catalogo: ComponentRegistry,
    naming: object = None,
) -> tuple[ProjectModel, ComponentRegistry]:
    """Il grafo della vista, e il catalogo di quel grafo.

    Con `tutto` il grafo resta quello che e', e il catalogo e' quello del grafo: le
    porte di comando che collega, e nient'altro. Senza elettrico nel grafo e' il
    catalogo di sempre, voce per voce.

    `naming` e' la cartella dei nomi: serve a leggere le sigle del grafo intero. Senza,
    la vista porta le sole sigle che l'ingegnere ha scritto."""
    if vista not in VISTE:
        raise ValueError(f"la vista {vista!r} non esiste: le viste sono {', '.join(VISTE)}")
    if vista == "tutto":
        return modello, catalogo.per_il_progetto(modello)

    domini = _dominio_delle_reti(modello)

    def del_comando(rete: str) -> bool:
        return domini.get(rete) is Domain.CONTROL

    elettrica = vista == "elettrico"
    tubazioni = [item for item in modello.connections if del_comando(item.network_id) == elettrica]
    reti = [item for item in modello.networks if (item.domain is Domain.CONTROL) == elettrica]
    if elettrica:
        toccati = {
            ref.component_id
            for item in tubazioni
            for ref in (item.endpoint_a, item.endpoint_b)
        }
        pezzi = [item for item in modello.components if item.id in toccati]
    else:
        fuori = solo_comando(modello, catalogo)
        pezzi = [item for item in modello.components if item.id not in fuori]

    # Le sigle del grafo intero, scritte sui pezzi che la tavola nomina: le
    # apparecchiature della tabella. Gli altri pezzi una sigla sul disegno non la
    # portano, e scrivergliela la aggiungerebbe.
    from disegnatore_mep.graphics.tabella import FUNZIONI_DELLA_TABELLA

    sigle = _sigle_del_grafo_intero(modello, catalogo.per_il_progetto(modello), naming)

    def con_la_sigla(pezzo: ComponentInstance) -> ComponentInstance:
        if pezzo.tag is not None or pezzo.id not in sigle:
            return pezzo
        mestieri = set(catalogo.get(pezzo.definition_id).functions)
        if not mestieri & set(FUNZIONI_DELLA_TABELLA):
            return pezzo
        return pezzo.model_copy(update={"tag": sigle[pezzo.id]})

    meta = modello.metadata
    titolo = meta.sheet_title
    aggiunta = TITOLO_DELLA_VISTA[vista]
    metadati = meta.model_copy(
        update={
            "sheet_title": f"{titolo} — {aggiunta}" if titolo else aggiunta.capitalize(),
            "sheet_number": numero_della_tavola(modello, vista),
            # Il nome dei file: le due tavole escono accanto, e non si sovrascrivono.
            "project_id": f"{meta.project_id}-{vista}",
        }
    )
    rimaste = {item.id for item in reti}
    diametri = modello.diametri
    if diametri is not None:
        chieste = [rete for rete in diametri.reti if rete in rimaste]
        diametri = diametri.model_copy(update={"reti": chieste}) if chieste else None
    della_vista = modello.model_copy(
        update={
            "metadata": metadati,
            "networks": reti,
            "components": [con_la_sigla(item) for item in pezzi],
            "connections": tubazioni,
            "diametri": diametri,
        }
    )
    return della_vista, catalogo.per_il_progetto(della_vista)


__all__ = [
    "CAMPIONE_DEL_RIMANDO",
    "SUFFISSO_DEL_NUMERO",
    "TITOLO_DELLA_VISTA",
    "VISTE",
    "Vista",
    "ha_il_comando",
    "numero_della_tavola",
    "rimando",
    "solo_comando",
    "vista_del_grafo",
]
