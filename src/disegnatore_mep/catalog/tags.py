"""La sigla di ogni pezzo, e l'ordine in cui l'impianto si legge.

Un pezzo senza sigla non si puo' ne' citare ne' contare — l'occhio terzo lo ha
trovato sulla tavola, dove due valvole su undici ne avevano una (D-097). La
sigla nasce qui, dal modello, e chiunque la mostri — l'albero dell'impianto, la
tavola, il computo — la chiede a questa funzione invece di inventarsene una.

**Da dove si comincia a contare** (D-098). Non dall'ordine in cui il file elenca
i pezzi, che e' un fatto del file e non dell'impianto: si parte dalle
**sorgenti** — dove il calore entra nell'acqua, e dove l'acqua entra
nell'edificio — e si segue il fluido. La prima valvola che si incontra uscendo
dal generatore e' la numero uno della sua famiglia. Le sorgenti si riconoscono
da cio' che dichiarano, mai da un elenco di nomi: un impianto con una caldaia al
posto della pompa di calore parte esattamente allo stesso modo.

Ne discende un costo, ed e' voluto: **inserire un pezzo vicino a una sorgente
sposta di uno i numeri della sua famiglia a valle.** E' normale per un documento
che si rigenera a ogni revisione. Cio' che resta fermo e' che lo stesso impianto
dia sempre le stesse sigle, comunque sia ordinato il file che lo descrive.

Due regole governano il resto:

- **Il modello vince.** Se l'ingegnere ha scritto la sigla di un pezzo, quella
  resta: la skill non ribattezza cio' che il progettista ha gia' chiamato, e
  quel numero resta prenotato per la sua famiglia.
- **Il resto si deriva** dalla famiglia del pezzo. Le famiglie sono scelte
  perche' un termotecnico italiano le legga senza leggenda, e non sono nomi di
  componenti travestiti: sono le sigle con cui quelle famiglie si scrivono da
  sempre su uno schema.
"""

import re

from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PortFlow

from .registry import ComponentRegistry

FAMILIES: tuple[tuple[str, str, str], ...] = (
    # (funzione di catalogo, sigla di famiglia, come si chiama in italiano)
    #
    # L'ordine conta: un pezzo con piu' funzioni prende la prima che combacia,
    # cosi' un volano — che separa e accumula — e' sempre un volano e non
    # dipende dall'ordine in cui il catalogo ha scritto le sue funzioni.
    ("heat_generation", "GT", "Generatore di calore"),
    ("thermal_storage", "VOL", "Accumulo inerziale"),
    ("dhw_storage", "BOL", "Accumulo di acqua calda sanitaria"),
    ("hydraulic_separation", "SEP", "Separatore idraulico"),
    ("circulation", "CIR", "Circolatore"),
    ("distribution", "COL", "Collettore"),
    ("emission", "TE", "Terminale di emissione"),
    ("diversion", "VD", "Valvola deviatrice"),
    ("dhw_mixing", "VM", "Valvola miscelatrice"),
    ("isolation_locked_open", "VIB", "Valvola di intercettazione bloccabile aperta"),
    ("isolation", "VI", "Valvola di intercettazione"),
    ("non_return", "VR", "Valvola di ritegno"),
    ("safety", "VS", "Valvola di sicurezza"),
    ("expansion", "VE", "Vaso di espansione"),
    ("filtration", "FIL", "Filtro"),
    ("sludge_separation", "DEF", "Defangatore"),
    ("air_release", "SA", "Separatore d'aria"),
    ("filling", "GR", "Gruppo di riempimento"),
    ("drain", "SC", "Attacco di scarico"),
    ("pressure_control", "RP", "Riduttore di pressione"),
    ("pressure_measurement", "MN", "Manometro"),
    ("temperature_measurement", "TM", "Termometro"),
    ("boundary", "AL", "Allacciamento"),
)

PREFIX_OF: dict[str, str] = {function: prefix for function, prefix, _ in FAMILIES}
FAMILY_NAME: dict[str, str] = {prefix: name for _, prefix, name in FAMILIES}

HEAT_SOURCE = "heat_generation"
"""Dove il calore entra nell'acqua: la prima sorgente da cui si conta."""

SUPPLY_BOUNDARY = "boundary"
"""Il confine dell'impianto. E' una sorgente solo se **alimenta**, cioe' se ha
un attacco da cui il fluido esce: un prelievo e' un confine anche lui, ma e'
dove l'acqua se ne va, non da dove arriva."""

WRITTEN_TAG = re.compile(r"^([A-Z]+)-(\d+)$")
"""Come e' fatta una sigla: famiglia, trattino, numero. Una sigla scritta a mano
che non abbia questa forma si rispetta lo stesso, ma non prenota nessun numero:
non si saprebbe quale."""


class TagError(ValueError):
    """Un pezzo di cui non si sa dire la famiglia."""


def family_of(functions: tuple[str, ...], definition_id: str) -> str:
    """La sigla di famiglia di un pezzo, dalle funzioni che dichiara."""
    for function, prefix, _ in FAMILIES:
        if function in functions:
            return prefix
    raise TagError(
        f"non so quale sigla di famiglia dare a un componente che fa "
        f"{', '.join(sorted(functions))}: aggiungerla all'elenco delle famiglie "
        f"invece di lasciare il pezzo senza nome ({definition_id})"
    )


def sources_of(project: ProjectModel, catalog: ComponentRegistry) -> list[str]:
    """Le sorgenti da cui si comincia a leggere l'impianto, in ordine (D-098).

    Prima i generatori, poi gli allacciamenti che alimentano. Nessun nome di
    componente: chi sia il generatore lo dice il catalogo.
    """
    generators: list[str] = []
    mains: list[str] = []
    for component in project.components:
        definition = catalog.get(component.definition_id)
        functions = set(definition.functions)
        if HEAT_SOURCE in functions:
            generators.append(component.id)
        elif SUPPLY_BOUNDARY in functions and any(
            port.flow is PortFlow.OUT for port in definition.ports
        ):
            mains.append(component.id)
    return generators + mains


def visit_order(project: ProjectModel, catalog: ComponentRegistry) -> list[str]:
    """L'ordine in cui i pezzi si incontrano partendo dalle sorgenti.

    Si segue il fluido: a ogni pezzo si guardano i suoi attacchi nell'ordine in
    cui il catalogo li dichiara, e per ciascuno prima la tubazione da cui
    l'acqua **esce** e poi quella da cui arriva. E' cio' che rende l'ordine
    indipendente da come il file elenca le tubazioni.

    Un circuito e' un anello: quando si torna su un pezzo gia' visto non si
    riparte, l'anello si e' chiuso. Cio' che nessuna sorgente raggiunge —
    un'isola nel modello — si legge alla fine, nell'ordine del modello, perche'
    resti visibile invece di sparire.
    """
    position = {item.id: index for index, item in enumerate(project.components)}
    ports = {
        item.id: [port.id for port in catalog.get(item.definition_id).ports]
        for item in project.components
    }
    leaving: dict[tuple[str, str], list[tuple[int, int, str]]] = {}
    for connection in project.connections:
        for near, far, outgoing in (
            (connection.endpoint_a, connection.endpoint_b, 0),
            (connection.endpoint_b, connection.endpoint_a, 1),
        ):
            leaving.setdefault((near.component_id, near.port_id), []).append(
                (outgoing, position.get(far.component_id, 0), far.component_id)
            )

    order: list[str] = []
    seen: set[str] = set()

    def walk(start: str) -> None:
        stack = [start]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            order.append(current)
            following: list[str] = []
            for port_id in ports.get(current, []):
                for _, _, peer in sorted(leaving.get((current, port_id), [])):
                    if peer not in seen:
                        following.append(peer)
            stack.extend(reversed(following))

    for source in sources_of(project, catalog):
        walk(source)
    for component in project.components:
        if component.id not in seen:
            walk(component.id)
    return order


def assign_tags(project: ProjectModel, catalog: ComponentRegistry) -> dict[str, str]:
    """La sigla di ogni pezzo, contata partendo dalle sorgenti (D-098).

    Le sigle scritte dall'ingegnere restano e prenotano il proprio numero; le
    altre si derivano dalla famiglia e riprendono a contare da li'.
    """
    written = {item.id: item.tag for item in project.components if item.tag is not None}
    used: dict[str, int] = {}
    for tag in written.values():
        shaped = WRITTEN_TAG.match(tag)
        if shaped is not None:
            prefix, number = shaped.group(1), int(shaped.group(2))
            used[prefix] = max(used.get(prefix, 0), number)

    tags: dict[str, str] = {}
    for component_id in visit_order(project, catalog):
        if component_id in written:
            tags[component_id] = written[component_id]
            continue
        definition = catalog.get(
            next(
                item.definition_id
                for item in project.components
                if item.id == component_id
            )
        )
        prefix = family_of(tuple(definition.functions), definition.id)
        used[prefix] = used.get(prefix, 0) + 1
        tags[component_id] = f"{prefix}-{used[prefix]:02d}"
    return tags


__all__ = [
    "FAMILIES",
    "FAMILY_NAME",
    "PREFIX_OF",
    "TagError",
    "assign_tags",
    "family_of",
    "sources_of",
    "visit_order",
]
