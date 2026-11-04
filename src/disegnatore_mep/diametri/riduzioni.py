"""La riduzione all'attacco della macchina, posata come un pezzo vero (REL-017, I-281).

Il PO, sul tubo scelto dalla velocita' (D-233): «manca un simobolo della riduzione in
tavola. se facciamo riduzione fuori dalla PDC serve il simbolo no ?». Dove il tubo che
arriva a una macchina ha il pollice piu' piccolo del suo attacco
(`costruttori.riduzioni_all_attacco`) — la Shenling da 12 kW ha l'attacco da 1¼" e la
velocita' sceglie il multistrato 32×3, da 1" —, `completa` posa una **riduzione** sulla
mandata e sul ritorno.

**Dove**: subito dopo il giunto antivibrante, prima di tutto il resto. Il giunto resta
grande quanto l'attacco e attaccato alla macchina (D-218, D-222); il corredo che le
regole ancorano alla macchina — la sicurezza, l'antigelo, il filtro — sta sul tubo,
oltre la riduzione (`rules.apply`, `assembly.runs`). Senza giunto la riduzione sta
sull'attacco.

**Non e' una regola**: non la decide un accessorio che manca, la decide il tubo, che
esiste solo dove il progettista chiede i diametri o li scrive. Non la scrive nemmeno il
progettista: la posa `completa`, e rilanciare `completa` sul grafo completo non ne
aggiunge un'altra.
"""

from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import AGAINST_THE_MACHINE_FUNCTIONS, PIPE_REDUCTION
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    EvidenceRef,
    PortRef,
    ProjectModel,
)

from .costruttori import RiduzioneAllAttacco, riduzioni_all_attacco

VOCE_DELLA_RIDUZIONE = "pipe-reducer"
"""La voce di catalogo della riduzione concentrica: l'attacco `a` e' il lato largo."""

ATTACCO = "attacco"
"""Il pollice dell'attacco della macchina, sul pezzo della riduzione: «1¼"»."""

TUBO = "tubo"
"""Il pollice del tubo che ci arriva, sul pezzo della riduzione: «1"»."""

RIFERIMENTO = "riduzione-all-attacco@1.0.0"
"""Da dove viene il pezzo, nella sua evidenza: la posa di `completa`, non una regola
del registro."""

PERCHE = (
    "Il tubo scelto dalla velocita' ha il pollice piu' piccolo dell'attacco della macchina "
    "(D-233): fra l'attacco e il tubo ci vuole una riduzione. Sta subito dopo il giunto "
    "antivibrante, che resta grande quanto l'attacco; il resto del corredo sta sul tubo, oltre "
    "di lei. Il PO: «se facciamo riduzione fuori dalla PDC serve il simbolo» (I-281)."
)

_SENZA_LA_SCRITTA: dict[str, None] = {"sezione": None, "lunghezza_m": None, "scritta": None}
"""Sezione e lunghezza sono del tratto intero: restano sulla prima meta' della tubazione
spezzata, come quando la spezza una regola (`rules.apply`)."""


@dataclass(frozen=True)
class RiduzionePosata:
    """Una riduzione all'attacco, e il pezzo che la porta nel grafo."""

    riduzione: RiduzioneAllAttacco
    pezzo: str
    """L'id del pezzo nel grafo."""
    aggiunta: bool
    """`completa` l'ha posata adesso; falso se c'era gia' (un rilancio)."""


def id_della_riduzione(macchina: str, porta: str) -> str:
    """Derivato dai dati — la macchina e il suo attacco —, come il giunto: lo stesso
    attacco da' sempre lo stesso pezzo, ed e' quello che rende il rilancio innocuo."""
    return f"{VOCE_DELLA_RIDUZIONE}-{macchina}-{porta}".replace("_", "-")


def _funzioni(project: ProjectModel, catalog: ComponentRegistry, component_id: str) -> set[str]:
    pezzo = next((item for item in project.components if item.id == component_id), None)
    if pezzo is None or not catalog.contains(pezzo.definition_id):
        return set()
    return set(catalog.get(pezzo.definition_id).functions)


def _dove_posarla(
    project: ProjectModel, catalog: ComponentRegistry, attacco: PortRef
) -> tuple[ConnectionModel, PortRef] | None:
    """La tubazione da spezzare e il suo capo dalla parte della macchina: quella che
    tocca l'attacco, oppure, se sull'attacco c'e' il giunto antivibrante, quella oltre
    il giunto. `None` se oltre il giunto c'e' gia' una riduzione, o se la fila non si
    legge (un giunto con piu' di una tubazione per lato)."""
    vicino = attacco
    visti: set[str] = {attacco.component_id}
    while True:
        tubazioni = [item for item in project.connections if vicino in (item.endpoint_a, item.endpoint_b)]
        if len(tubazioni) != 1:
            return None
        tubazione = tubazioni[0]
        lontano = tubazione.endpoint_b if tubazione.endpoint_a == vicino else tubazione.endpoint_a
        funzioni = _funzioni(project, catalog, lontano.component_id)
        if PIPE_REDUCTION in funzioni:
            return None
        if lontano.component_id in visti or not funzioni & AGAINST_THE_MACHINE_FUNCTIONS:
            return tubazione, vicino
        visti.add(lontano.component_id)
        oltre = [
            ref
            for item in project.connections
            if item.id != tubazione.id
            for ref, altro in ((item.endpoint_a, item.endpoint_b), (item.endpoint_b, item.endpoint_a))
            if ref.component_id == lontano.component_id and altro.component_id != lontano.component_id
        ]
        if len(oltre) != 1:
            return None
        vicino = oltre[0]


def _id_libero(project: ProjectModel, voluto: str) -> str:
    usati = {item.id for item in project.connections}
    candidato, indice = voluto, 1
    while candidato in usati:
        indice += 1
        candidato = f"{voluto}{indice}"
    return candidato


def posa_le_riduzioni(
    project: ProjectModel, catalog: ComponentRegistry
) -> tuple[ProjectModel, list[RiduzionePosata]]:
    """Il grafo con una riduzione su ogni attacco d'acqua piu' grande del tubo che ci
    arriva, e l'elenco delle riduzioni — posate adesso o gia' presenti.

    Si posa solo dove la voce `pipe-reducer` e' nel catalogo. La tubazione si spezza nel
    verso in cui era scritta: l'attacco largo `a` guarda la macchina, quello stretto `b`
    il tubo. Il pezzo porta `attacco` e `tubo`, i due pollici, che la distinta scrive
    («Riduzione 1¼" M × 1" F»); entra nel sottosistema della macchina, come il giunto."""
    if not catalog.contains(VOCE_DELLA_RIDUZIONE):
        return project, []
    posate: list[RiduzionePosata] = []
    current = project
    for riduzione in riduzioni_all_attacco(project, catalog):
        pezzo_id = id_della_riduzione(riduzione.macchina, riduzione.porta)
        if any(item.id == pezzo_id for item in current.components):
            posate.append(RiduzionePosata(riduzione, pezzo_id, aggiunta=False))
            continue
        attacco = PortRef(component_id=riduzione.macchina, port_id=riduzione.porta)
        dove = _dove_posarla(current, catalog, attacco)
        if dove is None:
            continue
        tubazione, vicino = dove
        verso_la_macchina = tubazione.endpoint_a == vicino
        primo = PortRef(component_id=pezzo_id, port_id="a" if verso_la_macchina else "b")
        secondo = PortRef(component_id=pezzo_id, port_id="b" if verso_la_macchina else "a")
        prima = tubazione.model_copy(update={"id": _id_libero(current, f"{tubazione.id}-a"), "endpoint_b": primo})
        dopo = tubazione.model_copy(
            update={
                "id": _id_libero(current, f"{tubazione.id}-b"),
                "endpoint_a": secondo,
                **_SENZA_LA_SCRITTA,
            }
        )
        pezzo = ComponentInstance(
            id=pezzo_id,
            definition_id=VOCE_DELLA_RIDUZIONE,
            properties={ATTACCO: riduzione.attacco, TUBO: riduzione.tubo.pollici},
            evidence=[EvidenceRef(kind="rule", reference=RIFERIMENTO, note=PERCHE)],
        )
        tubazioni: list[ConnectionModel] = []
        for item in current.connections:
            tubazioni.extend((prima, dopo) if item.id == tubazione.id else (item,))
        current = current.model_copy(
            update={
                "components": [*current.components, pezzo],
                "connections": tubazioni,
                "subsystems": [
                    item.model_copy(update={"component_ids": [*item.component_ids, pezzo_id]})
                    if riduzione.macchina in item.component_ids
                    else item
                    for item in current.subsystems
                ],
            }
        )
        posate.append(RiduzionePosata(riduzione, pezzo_id, aggiunta=True))
    return current, posate


def pollici_dietro_le_riduzioni(project: ProjectModel, catalog: ComponentRegistry) -> dict[str, str]:
    """Il pollice dei pezzi fra la macchina e la sua riduzione — il giunto antivibrante —:
    quello dell'attacco, non quello del tubo (D-218, D-233). Il giunto si compra grande
    quanto l'attacco della macchina: e' per questo che la riduzione gli sta dopo."""
    pollici: dict[str, str] = {}
    for pezzo in project.components:
        attacco = pezzo.properties.get(ATTACCO)
        if pezzo.definition_id != VOCE_DELLA_RIDUZIONE or not isinstance(attacco, str):
            continue
        cursore = PortRef(component_id=pezzo.id, port_id="a")
        visti = {pezzo.id}
        while True:
            tubazioni = [item for item in project.connections if cursore in (item.endpoint_a, item.endpoint_b)]
            if len(tubazioni) != 1:
                break
            lontano = tubazioni[0].endpoint_b if tubazioni[0].endpoint_a == cursore else tubazioni[0].endpoint_a
            if lontano.component_id in visti or not (
                _funzioni(project, catalog, lontano.component_id) & AGAINST_THE_MACHINE_FUNCTIONS
            ):
                break
            visti.add(lontano.component_id)
            pollici[lontano.component_id] = attacco
            oltre = [
                ref
                for item in project.connections
                if item.id != tubazioni[0].id
                for ref in (item.endpoint_a, item.endpoint_b)
                if ref.component_id == lontano.component_id
            ]
            if len(oltre) != 1:
                break
            cursore = oltre[0]
    return pollici


__all__ = [
    "ATTACCO",
    "TUBO",
    "VOCE_DELLA_RIDUZIONE",
    "RiduzionePosata",
    "id_della_riduzione",
    "pollici_dietro_le_riduzioni",
    "posa_le_riduzioni",
]
