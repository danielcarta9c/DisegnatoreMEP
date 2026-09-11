"""La gerarchia della tavola: autostrada, distribuzione, servizio (DRAW-007, §A).

Il PO, il 10 settembre 2026:

    «Le tubazioni che vanno alle macchine principali sono l'autostrada, e su
    quelle i costi dovrebbero essere ancora maggiori. Oggi nel nostro router
    non abbiamo distinzione tra autostrada principale e strade secondarie:
    tutto e' principale ma non e' cosi'.»

Non e' una preferenza estetica: e' il modo in cui un progettista costruisce una
tavola. Allineate le porte della macchina principale con quelle dell'accumulo
principale nascono **due rette parallele** — mandata e ritorno — e tutto il
resto si appende a quelle. Chi disegna accetta volentieri dieci pieghe in piu'
sulle strade secondarie per tenere pulite le due macro-linee; un costo che le
pesa uguali fa il contrario, e lo fa **correttamente** secondo il criterio che
ha. Il criterio sbagliato e' il costo, non il ciclo che lo minimizza.

**La primitiva.** La prima stesura del pacchetto contava «quanta parte
dell'impianto dipende da questa tratta». Il prototipo l'ha smentita sulle due
tavole vere: su un circuito chiuso il cammino a valle rientra su se' stesso,
quindi ogni tratta dell'anello raggiunge ogni utilizzatore e ventuno tratte su
ventidue prendono lo stesso peso. Non e' una toppa mancante, e' la primitiva
sbagliata. Quella scelta dal PO e' il **tronco fra le macchine principali**, ed
e' quella che questo modulo calcola.

Il conto vive **qui e in nessun altro posto**: lo leggono il costo di posa e
l'obiettivo di allineamento, e con `DRAW-008` lo leggera' anche lo spessore del
tratto. Tre calcoli separati direbbero prima o poi tre cose diverse sulla stessa
tubazione.
"""

from enum import IntEnum

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.layout.flow import (
    GENERATOR_FUNCTIONS,
    STORE_FUNCTIONS,
    TrunkKey,
)
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.order import structural_order
from disegnatore_mep.model.project import ProjectModel

DISTRIBUTION_FUNCTIONS = frozenset({"distribution"})
"""Chi ripartisce il fluido fra piu' circuiti: il collettore.

Sta sulla spina insieme a chi genera e a chi accumula perche' e' il terzo capo
delle «due macro-linee»: il tronco non finisce sull'accumulo, arriva fin dove il
fluido si divide.
"""


class Level(IntEnum):
    """Il livello di una tratta. **Ordinato**, e non per comodita'.

    Il costo deve poterlo pesare come una grandezza — moltiplicare, confrontare,
    sommare — invece di aprire un elenco di casi. Un elenco di casi e' la strada
    piu' corta perche' il quarto livello, il giorno che serve, venga dimenticato
    in una funzione su tre.
    """

    SERVIZIO = 0
    """Non porta a nessuna macchina: stacchi ciechi e accessori appesi."""

    DISTRIBUZIONE = 1
    """Porta a una macchina che sulla spina non sta: un utilizzatore, un
    generatore oltre il principale, un confine di rete."""

    AUTOSTRADA = 2
    """Sta fra due macchine di spina. Su un circuito chiuso ci stanno **sia la
    mandata sia il ritorno**, che e' precisamente cio' che il PO chiama «le due
    macro-linee parallele»."""


_WEIGHT: dict["Level", int] = {}
"""Riempito sotto, dopo che `Level` esiste. Sta qui, e in nessun altro posto."""


def weight_of(level: Level) -> int:
    """Quanto pesa una piega, un incrocio o un millimetro su quel livello.

    La scala e' 1 / 4 / 16, e il numero che la fissa e' il PO:

        «Si accettano volentieri dieci pieghe in piu' sulle strade secondarie
        per tenere pulite le due macro-linee.»

    Sedici e' il primo gradino della scala che supera quel dieci: una piega
    sull'autostrada costa piu' di dieci pieghe di servizio, e il ciclo
    preferisce sempre spostarla fuori dal tronco. Non e' una costante arbitraria
    e non e' tarata su una fixture: e' la frase del PO tradotta in un numero, e
    se il PO la cambia questa e' l'unica riga da toccare.
    """
    return _WEIGHT[level]


def _is_a_machine(definition: ComponentDefinition) -> bool:
    """Un apparecchio, non un raccordo e non qualcosa che pende da uno stacco.

    E' la distinzione che il catalogo dichiara gia': un raccordo lo si
    attraversa e basta, un accessorio appeso e' un capolinea che non porta da
    nessuna parte. Cio' che resta e' una macchina, e sono le macchine che la
    gerarchia unisce.
    """
    return not definition.is_a_fitting and not definition.attaches_on_a_branch


_WEIGHT.update(
    {
        Level.SERVIZIO: 1,
        Level.DISTRIBUZIONE: 4,
        Level.AUTOSTRADA: 16,
    }
)


def spine_machines(project: ProjectModel, catalog: ComponentRegistry) -> frozenset[str]:
    """Le macchine su cui il tronco si appoggia.

    Ogni macchina che accumula o separa idraulicamente, ogni collettore, e
    **una sola** macchina di generazione. Una sola perche' e' l'unica che puo'
    stare sull'asse: le altre in cascata ci si innestano, ed e' cio' che il PO
    chiama «i generatori oltre il primo allineato».

    A parita' di mestiere decide lo **spareggio strutturale** — come sono
    attaccate al resto dell'impianto — e soltanto fra macchine che nessun dato
    dell'impianto distingue decide l'identificativo. Mai un nome scelto a mano.
    """
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    machines = [key for key, value in definitions.items() if _is_a_machine(value)]
    spine = {
        key
        for key in machines
        if frozenset(definitions[key].functions) & (STORE_FUNCTIONS | DISTRIBUTION_FUNCTIONS)
    }
    order = structural_order(project)
    generators = sorted(
        (
            key
            for key in machines
            if frozenset(definitions[key].functions) & GENERATOR_FUNCTIONS
        ),
        key=lambda key: order[key],
    )
    if generators:
        spine.add(generators[0])
    return frozenset(spine)


def hierarchy_of(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, Level]:
    """Il livello di ciascuna tratta.

    Si guarda che cosa c'e' **di qua e di la'** della tratta, camminando
    attraverso i raccordi e fermandosi sulla prima macchina. Se da tutt'e due i
    lati si arriva a una macchina di spina la tratta e' del tronco; se da
    tutt'e due si arriva a una macchina, e' distribuzione; se da un lato non si
    arriva a nessuna macchina, quel lato e' un capolinea ed e' servizio.

    La simmetria della definizione e' il motivo per cui mandata e ritorno di un
    circuito chiuso finiscono **tutt'e due** in cima: nessuna delle due e' «la
    strada», sono le due corsie della stessa strada.
    """
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    machines = {key for key, value in definitions.items() if _is_a_machine(value)}
    spine = spine_machines(project, catalog)

    edges: dict[str, list[tuple[str, TrunkKey]]] = {}
    for trunk in trunks:
        first, second = trunk.start.component_id, trunk.end.component_id
        edges.setdefault(first, []).append((second, trunk.connection_ids))
        edges.setdefault(second, []).append((first, trunk.connection_ids))

    def machines_beyond(start: str, without: TrunkKey) -> frozenset[str]:
        """Le macchine raggiunte da `start` senza attraversarne una, e senza
        rientrare per la tratta da cui si sta guardando.

        **Si attraversano soltanto i raccordi.** Un accessorio appeso e' un
        capolinea anche quando ha due porte: il gruppo di riempimento, da
        DRAW-006-R1, e' un ponte fra la rete fredda e il circuito, e chi lo
        attraversasse leggerebbe come tronco fra due macchine di spina uno
        stacco che di spina non ha niente — collegando per giunta due reti che
        sulla tavola non si toccano.
        """
        if start in machines:
            return frozenset({start})
        if not definitions[start].is_a_fitting:
            # Il capolinea vale anche quando ci si parte, non solo quando ci si
            # arriva: guardando dal ponte del riempimento verso il proprio
            # stacco, dall'altra sua porta non si esce.
            return frozenset()
        seen = {start}
        found: set[str] = set()
        frontier = [start]
        while frontier:
            onward: list[str] = []
            for node in frontier:
                for other, key in edges.get(node, ()):
                    if key == without or other in seen:
                        continue
                    seen.add(other)
                    if other in machines:
                        found.add(other)
                        continue
                    if not definitions[other].is_a_fitting:
                        continue
                    onward.append(other)
            frontier = onward
        return frozenset(found)

    levels: dict[TrunkKey, Level] = {}
    for trunk in trunks:
        here = machines_beyond(trunk.start.component_id, trunk.connection_ids)
        there = machines_beyond(trunk.end.component_id, trunk.connection_ids)
        if here & spine and there & spine:
            levels[trunk.connection_ids] = Level.AUTOSTRADA
        elif here and there:
            levels[trunk.connection_ids] = Level.DISTRIBUZIONE
        else:
            levels[trunk.connection_ids] = Level.SERVIZIO
    return levels
