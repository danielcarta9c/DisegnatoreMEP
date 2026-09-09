"""La catena della macchina: che cos'e', e quanto rettilineo pretende.

E' il contratto di DRAW-005-R1 (I-044): dalla porta di un pezzo che si
manutiene, i pezzi in linea fino al primo organo di chiusura compreso — il
filtro a Y e la sua valvola sul ritorno della pompa di calore — si posano a
**distanze fisse** dalla porta, sul **primo rettilineo** che ne parte, prima
della prima curva. Due macchine uguali con la stessa catena hanno la stessa
geometria locale, anche se una catena ruota.

Vive in un modulo suo perche' la leggono in due, e devono leggerla uguale:
l'instradatore, che deve lasciare dalla porta il rettilineo che la catena
occupera', e la posa degli accessori, che ve la siede. Il criterio e' del
catalogo, mai del nome del pezzo: la proprieta' `maintainable` da una parte,
le funzioni che chiudono dall'altra.
"""

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import CLOSING_FUNCTIONS, ComponentTrait
from disegnatore_mep.model.project import PortRef, ProjectModel

from .trunks import Trunk

MIN_SPACING_MM = 2.5
"""Distanza minima fra due accessori sulla stessa tratta: un passo di griglia."""

SNUG_CLEARANCE_MM = 2.5
"""Stacco di chi isola contro l'apparecchio che si manutiene (D-120).

Un passo, e non zero, perche' **davanti a un attacco c'e' una cella sola ed e'
la sua unica uscita** (D-113): quella corsia non e' gioco. Un passo oltre e' il
minimo raggiungibile, e porta il fianco della valvola a cinque millimetri dal
punto d'attacco invece dei dodici e mezzo che lasciava lo stacco ordinario.

E' la regola che il PM ha dato «da senior al disegnatore»: «le valvole di
intercettazione che vengono montate per manutenere le macchine devono essere
disegnate molto piu' vicine agli attacchi, una regola di vicinanza fissa e
piuttosto piccola, esempio 2 mm» (I-018).
"""

CHAIN_PORT_GAP_MM = SNUG_CLEARANCE_MM + MIN_SPACING_MM
"""Da dove comincia la catena della macchina, misurato dalla porta (I-044).

La soglia dell'attacco — la cella riservata davanti a ogni porta (D-113) — piu'
un passo: e' il fianco a cinque millimetri dal punto d'attacco che D-120 ha
sempre dato alla valvola che isola, ora esteso a tutta la catena. Fisso, e non
una frazione della tratta: due macchine uguali hanno la stessa distanza."""


def is_machine_end(project: ProjectModel, catalog: ComponentRegistry, ref: PortRef) -> bool:
    """Il capo e' **la macchina stessa**: un pezzo che si manutiene, non un
    raccordo attraverso cui la si raggiunge. Solo qui la catena e' un contratto
    duro (I-044): oltre un raccordo passante l'organo si stringe al raccordo
    come da I-035, scorrendo al primo posto libero."""
    definition_id = next(
        (item.definition_id for item in project.components if item.id == ref.component_id),
        None,
    )
    if definition_id is None:
        return False
    definition = catalog.get(definition_id)
    return definition.has_trait(ComponentTrait.MAINTAINABLE) and not definition.is_a_fitting


def machine_chains(
    project: ProjectModel, catalog: ComponentRegistry, trunk: Trunk
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Le catene ai due capi della tratta: dalla porta della macchina, i pezzi
    in linea fino al primo organo di chiusura compreso. Vuota dove il capo non
    e' una macchina, o dove non c'e' un organo che chiuda.

    Un organo solo puo' chiudere un tratto con un pezzo manutenibile a ciascun
    capo (I-034): appartiene alla catena che porta anche i pezzi propri della
    macchina — il filtro — e, a pari titolo, al capo di arrivo.
    """
    definitions = {item.id: item.definition_id for item in project.components}
    members = list(trunk.inline_component_ids)
    closes = [
        bool(CLOSING_FUNCTIONS & set(catalog.get(definitions[item]).functions)) for item in members
    ]

    def along(order: list[int]) -> list[int]:
        found: list[int] = []
        for index in order:
            found.append(index)
            if closes[index]:
                return found
        return []

    head = along(list(range(len(members)))) if is_machine_end(project, catalog, trunk.start) else []
    tail = (
        along(list(range(len(members) - 1, -1, -1)))
        if is_machine_end(project, catalog, trunk.end)
        else []
    )
    if set(head) & set(tail):
        if len(head) > 1 and len(tail) == 1:
            tail = []
        else:
            head = []
    return tuple(members[index] for index in head), tuple(members[index] for index in tail)


def chain_room_mm(
    project: ProjectModel, catalog: ComponentRegistry, chain: tuple[str, ...], horizontal: bool
) -> float:
    """Quanto rettilineo la catena occupa dalla porta, passo di coda compreso.

    Lo stacco dalla porta, poi ogni pezzo con il suo passo: e' la stessa somma
    che la posa fa quando la siede, letta prima che la tratta esista, cosi'
    che l'instradatore lasci quel rettilineo libero dalla porta. L'ingombro di
    un pezzo lungo il tubo dipende dalla giacitura: il riquadro girato di un
    quarto scambia larghezza e altezza.
    """
    if not chain:
        return 0.0
    definitions = {item.id: item.definition_id for item in project.components}
    reach = CHAIN_PORT_GAP_MM
    for component_id in chain:
        manifest = catalog.resolve(definitions[component_id]).symbol.manifest
        wanted = (0, 180) if horizontal else (90, 270)
        rotation = next((item for item in wanted if item in manifest.allowed_rotations_deg), None)
        turned = manifest if rotation is None else manifest.rotated(rotation)
        extent = turned.width_mm if horizontal else turned.height_mm
        reach += extent + MIN_SPACING_MM
    return reach


__all__ = [
    "CHAIN_PORT_GAP_MM",
    "MIN_SPACING_MM",
    "SNUG_CLEARANCE_MM",
    "chain_room_mm",
    "is_machine_end",
    "machine_chains",
]
