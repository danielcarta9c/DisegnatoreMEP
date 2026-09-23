"""L'autostrada intera: non una catena di frammenti, ma un oggetto (DRAW-012 §C).

**Il difetto che questo modulo chiude.** Fino a `DRAW-011` un'autostrada non
esisteva come oggetto: esistevano le sue **tratte**, e ogni raccordo o multivia
incontrato ne apriva una nuova. Sull'impianto 4 erano dieci tronconi lunghi
cinque o dieci millimetri, e l'invariante «ogni tratta del tronco e' un
rettilineo» veniva verificato su **ciascun troncone**, dove e' vero per
costruzione: un frammento di 5 mm e' dritto sempre. **Nessun invariante diceva
che la catena intera fosse una retta**, ed e' il motivo per cui il difetto non
si vedeva: i numeri erano verdi e la tavola era storta.

**Che cos'e' una catena.** Una successione massimale di tratte di livello
autostrada che si susseguono passando **attraverso** i crocevia — i raccordi e i
multivia, che non sono capolinea ma punti della tubazione — e che comincia e
finisce su una macchina, o dove la retta non prosegue.

**Dove la retta prosegue lo dice il simbolo, non la geometria.** Arrivati su un
crocevia da una porta, la catena continua sulla porta che il manifesto dichiara
sulla **faccia opposta**: e' la sola che possa stare sulla stessa retta, e la
relazione sopravvive a qualunque rotazione perche' ruotare il simbolo ruota
tutt'e due le facce. Su un raccordo a T — `a` a sinistra, `b` a destra, `c` in
cima — la catena passa fra `a` e `b` e il braccio `c` se ne stacca: e'
esattamente «uno dei due rami resta sull'asse e l'altro se ne stacca»
(`2026-09-11-architettura-della-posa-a-fasi.md` §4). Con due generatori che
confluiscono su un collettore le catene sono **due**, ciascuna fino al punto in
cui confluiscono, che e' cio' che **D-138** dispone.

Poiche' «di fronte» e' una relazione simmetrica e **una porta porta una sola
tubazione** (D-100), l'accoppiamento sui crocevia e' un abbinamento perfetto: le
catene sono le componenti connesse di quell'abbinamento e non dipendono
dall'ordine in cui si costruiscono. Non c'e' nessuno spareggio da fare, e quindi
nessun nome puo' entrarci.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.order import structural_order
from disegnatore_mep.model.project import PortRef, ProjectModel

from .geometry import Point
from .hierarchy import (
    Level,
    axis_rank,
    hierarchy_of,
    is_a_machine,
    machines_beyond_of,
    ports_through,
)
from .trunks import Trunk

TrunkKey = tuple[str, ...]

_TOLERANCE_MM = 1e-6

_HORIZONTAL_FACES = frozenset({PortFace.LEFT, PortFace.RIGHT})

_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}

PortAt = Callable[[str, str], tuple[Point, PortFace] | None]
"""Dove sta una porta sulla tavola, e su che faccia guarda.

La firma e' quella che hanno gia' `improve.Improver.port_at` e
`spine._Spine.port_at`: chi chiama passa la propria, perche' l'invariante si
deve poter verificare **sulla stessa geometria** che il ciclo sta valutando.
`None` per un pezzo che questa posa non colloca.
"""


@dataclass(frozen=True)
class Highway:
    """Un'autostrada intera, dall'inizio alla fine.

    `steps` la percorre: ogni passo e' una tratta, con la porta da cui vi si
    entra e quella da cui se ne esce, **nell'ordine della catena** e non in
    quello in cui il file ha scritto le connessioni. Fra un passo e il
    successivo c'e' un crocevia, e la catena vi passa attraverso.
    """

    keys: tuple[TrunkKey, ...]
    steps: tuple[tuple[PortRef, PortRef], ...]

    @property
    def head(self) -> PortRef:
        """Il capo da cui la catena comincia."""
        return self.steps[0][0]

    @property
    def tail(self) -> PortRef:
        """Il capo su cui finisce."""
        return self.steps[-1][1]

    @property
    def component_ids(self) -> tuple[str, ...]:
        """I pezzi che la catena tocca, nell'ordine in cui li incontra."""
        found: list[str] = []
        for entry, exit_ in self.steps:
            for ref in (entry, exit_):
                if ref.component_id not in found:
                    found.append(ref.component_id)
        return tuple(found)

    @property
    def is_a_single_run(self) -> bool:
        """Vero se la catena e' una tratta sola: allora l'invariante nuovo non
        aggiunge niente a quello di sempre, ed e' giusto che sia cosi'."""
        return len(self.steps) == 1


def highways(
    project: ProjectModel, catalog: ComponentRegistry, trunks: Iterable[Trunk]
) -> tuple[Highway, ...]:
    """Le autostrade intere dell'impianto, ciascuna con le proprie tratte.

    Ogni tratta di livello autostrada sta in **una sola** catena: le catene non
    si sovrappongono, altrimenti pretendere che due catene incidenti siano
    tutt'e due rette imporrebbe al disegno una condizione che nessuna posa puo'
    soddisfare — due rette diverse per lo stesso tratto.
    """
    runs = list(trunks)
    levels = hierarchy_of(project, catalog, runs)
    autostrade = [
        item for item in runs if levels[item.connection_ids] is Level.AUTOSTRADA
    ]
    definitions: dict[str, ComponentDefinition] = {
        item.id: catalog.get(item.definition_id) for item in project.components
    }
    sizes = {
        item.id: (
            catalog.resolve(item.definition_id).symbol.manifest.width_mm
            * catalog.resolve(item.definition_id).symbol.manifest.height_mm
        )
        for item in project.components
    }
    order = structural_order(project)
    machines = {key for key, value in definitions.items() if is_a_machine(value)}

    at_port: dict[tuple[str, str], Trunk] = {}
    for trunk in autostrade:
        for ref in (trunk.start, trunk.end):
            at_port[(ref.component_id, ref.port_id)] = trunk
    beyond = machines_beyond_of(project, catalog, runs)

    def rank_of(here: str, port_id: str) -> tuple[int, float, int]:
        """Quanto pesa il ramo che parte da questa porta: dove porta, e quanto
        e' grande cio' a cui porta.

        Stessa camminata e stesso conto della fase del tronco — la prima sta in
        `hierarchy.machines_beyond_of`, il secondo in `hierarchy.axis_rank` —
        perche' la catena deve proseguire dove il tronco tiene l'asse: due
        criteri diversi misurerebbero una forma che il motore non sta
        costruendo.
        """
        trunk = at_port[(here, port_id)]
        far = trunk.end if trunk.start.component_id == here else trunk.start
        found = beyond((far.component_id, far.port_id), trunk.connection_ids)
        if not found:
            return (2, 0.0, 0)
        return min(
            (
                *axis_rank(frozenset(definitions[item].functions), sizes[item]),
                order.get(item, 0),
            )
            for item in found
        )

    def onward(ref: PortRef, taken: set[TrunkKey]) -> PortRef | None:
        """La porta da cui la catena prosegue. `None` se finisce qui.

        Finisce su una **macchina**, che e' un capolinea e non un punto della
        tubazione; e finisce dove nessuna delle porte comunicanti porta una
        tratta di autostrada ancora libera.
        """
        definition = definitions[ref.component_id]
        if is_a_machine(definition):
            return None
        free = [
            port_id
            for port_id in sorted(ports_through(definition, ref.port_id))
            if (ref.component_id, port_id) in at_port
            and at_port[(ref.component_id, port_id)].connection_ids not in taken
        ]
        if not free:
            return None
        chosen = min(free, key=lambda port_id: (rank_of(ref.component_id, port_id), port_id))
        return PortRef(component_id=ref.component_id, port_id=chosen)

    def step_from(trunk: Trunk, entry: PortRef) -> tuple[PortRef, PortRef]:
        return (entry, trunk.end if entry == trunk.start else trunk.start)

    # **Le catene cominciano dalle macchine**, e nell'ordine strutturale: e' lo
    # stesso capo da cui la fase del tronco comincia a camminare, cosi' che
    # l'asse che quella costruisce sia l'asse su cui questa misura. Le tratte
    # che nessuna macchina tocca formano poi le proprie catene, nell'ordine in
    # cui la partizione le elenca.
    def seed_key(pair: tuple[Trunk, PortRef | None]) -> tuple[int, int, str]:
        trunk, anchor = pair
        if anchor is None:
            return (1, 0, trunk.connection_ids[0])
        return (0, order.get(anchor.component_id, 0), anchor.port_id)

    seeds: list[tuple[Trunk, PortRef | None]] = []
    for trunk in autostrade:
        anchors = [
            ref
            for ref in (trunk.start, trunk.end)
            if ref.component_id in machines
        ]
        seeds.append((trunk, anchors[0] if anchors else None))
    seeds.sort(key=seed_key)

    taken: set[TrunkKey] = set()
    found: list[Highway] = []
    for trunk, anchor in seeds:
        if trunk.connection_ids in taken:
            continue
        taken.add(trunk.connection_ids)
        entry = anchor if anchor is not None else trunk.start
        chain: list[tuple[PortRef, PortRef]] = [step_from(trunk, entry)]
        keys: list[TrunkKey] = [trunk.connection_ids]

        # Avanti, poi indietro: la catena cresce dai due capi finche' il
        # crocevia offre un proseguimento che nessun'altra catena ha preso.
        for forward in (True, False):
            cursor = chain[-1][1] if forward else chain[0][0]
            while True:
                across = onward(cursor, taken)
                if across is None:
                    break
                following = at_port[(across.component_id, across.port_id)]
                taken.add(following.connection_ids)
                piece = step_from(following, across)
                if forward:
                    chain.append(piece)
                    keys.append(following.connection_ids)
                else:
                    chain.insert(0, (piece[1], piece[0]))
                    keys.insert(0, following.connection_ids)
                cursor = piece[1]
        found.append(Highway(keys=tuple(keys), steps=tuple(chain)))
    return tuple(found)


def turns_of(highway: Highway, port_at: PortAt) -> int | None:
    """Quante curve fa la catena con questa posa, o `None` se non si misura.

    Ogni tratta deve restare un rettilineo: le due porte si guardano in faccia e
    la tratta va nel verso della porta da cui parte. Fra una tratta e la
    successiva la retta puo' **cambiare**, e ogni cambio — di direzione o di
    quota — e' una curva. Zero curve e' la retta di `DRAW-012` §C; una curva e'
    la forma che **D-144** chiede alla distribuzione.

    `None` quando la posa non colloca un pezzo, o quando una tratta non e' un
    rettilineo: non c'e' un numero di curve da dare, e chi chiama lo tratta come
    una catena che non sta nella propria forma.
    """
    heading: tuple[float, float] | None = None
    axis: float | None = None
    turns = 0
    for entry, exit_ in highway.steps:
        here = port_at(entry.component_id, entry.port_id)
        there = port_at(exit_.component_id, exit_.port_id)
        if here is None or there is None:
            return None
        (source, face), (goal, other) = here, there
        if other is not face.opposite:
            return None
        direction = _DIRECTION[face]
        if face in _HORIZONTAL_FACES:
            if abs(source.y_mm - goal.y_mm) > _TOLERANCE_MM:
                return None
            if (goal.x_mm - source.x_mm) * direction[0] <= _TOLERANCE_MM:
                return None
            quota = source.y_mm
        else:
            if abs(source.x_mm - goal.x_mm) > _TOLERANCE_MM:
                return None
            if (goal.y_mm - source.y_mm) * direction[1] <= _TOLERANCE_MM:
                return None
            quota = source.x_mm
        if heading is not None and (
            heading != direction or abs((axis or 0.0) - quota) > _TOLERANCE_MM
        ):
            turns += 1
        heading, axis = direction, quota
    if heading is None:
        return None
    return turns


def curve_imposte_dal_crocevia(arrivo: PortFace, partenza: PortFace) -> int:
    """Quante pieghe **la forma dei due attacchi impone** su un crocevia.

    La catena arriva su un pezzo dalla porta `arrivo` e lo lascia dalla porta
    `partenza`, e le due porte stanno **sullo stesso pezzo**. Chi vi arriva
    viaggia nel verso **contrario** alla faccia su cui arriva; chi ne esce
    viaggia nel verso della faccia da cui esce. Da qui i tre soli casi:

    - **facce opposte** — si entra e si esce nello stesso verso: **zero**, la
      catena passa dritta;
    - **facce perpendicolari** — il verso gira di un quarto: **una**, e non
      c'e' posa che la tolga;
    - **stessa faccia** — si deve tornare indietro: **due**.

    **E' invariante per giacitura, ed e' per questo che e' un pavimento e non
    una taratura.** Ruotare o specchiare un pezzo gira **tutte** le sue porte
    insieme: l'angolo fra due facce **dello stesso pezzo** non cambia. Quello
    che questo conto dice non lo si puo' quindi togliere ne' girando il pezzo
    ne' spostandolo — e' esattamente cio' che **B7** intende con «non e' la posa
    a sbagliare: e' la forma dei due simboli».

    **Fra due pezzi diversi conta l'altra meta' del pavimento**,
    `curve_imposte_fra_due_pezzi`: li' l'angolo dipende da come i due pezzi
    sono girati l'uno rispetto all'altro, e se ne conta solo la parte che
    nessuna posa cambia.
    """
    if partenza is arrivo.opposite:
        return 0
    if partenza is arrivo:
        return 2
    return 1


def curve_imposte_fra_due_pezzi(partenza: PortFace, arrivo: PortFace) -> int:
    """Quante pieghe impongono **due porte di due pezzi diversi** fra cui la
    catena corre: `partenza` e' la porta da cui esce, `arrivo` quella in cui
    entra — anche attraverso pezzi che la catena passa dritta, che qui non
    contano (`pavimento_della_catena`).

    **Una sola cosa di due pezzi diversi nessuna posa la cambia: l'asse.**
    Spostarli non gira nessuna faccia. Ribaltarli — lo specchio di **D-169**, o
    il mezzo giro dove la libreria lo ammette — gira una faccia nella sua
    opposta, e la lascia **sul proprio asse**: orizzontale resta orizzontale,
    verticale resta verticale. Da qui i due soli casi:

    - **assi perpendicolari** — **una**. E' la L fra due pezzi, e nessuno
      spostamento e nessun ribaltamento la toglie. Sono i casi misurati sulla
      tavola 5 del 22 settembre 2026, che il PO ha approvato (**I-108**) e che
      il pavimento di D-171 accusava sette volte: il **gomito in fondo a un
      collettore verticale**, dove l'ultima macchina ha l'attacco sul fianco; la
      **L fra la terza via di una tre vie e la serpentina** del bollitore; la
      testa della colonna di un pettine;
    - **stesso asse** — **zero**. Se le due porte si guardano, allineate la
      catena passa dritta; se guardano dalla stessa parte, la U che ne viene la
      toglie **ribaltare uno dei due pezzi**, e un ribaltamento e' una scelta di
      chi compone.

    **Perche' l'asse e non la faccia, detto dalla parte di chi compone.** Il
    quarto di giro di un pezzo non e' una mossa di posa: pompe, caldaie,
    accumuli e scambiatori stanno in piedi — la libreria li ammette solo a zero
    gradi —, il terminale si prende di lato (**B12**, **D-167**), e un organo in
    linea ha la via dritta sulla linea (**B4**). Quello che resta a chi compone e' il **ribaltamento**, e un
    ribaltamento l'asse non lo cambia. Il caso in cui un quarto di giro e'
    davvero una scelta — il pezzo che la catena attraversa dritto — lo toglie
    `pavimento_della_catena`, che quel pezzo lo gira sulla catena.
    """
    if arrivo in (partenza, partenza.opposite):
        return 0
    return 1


PortFaceOf = Callable[[PortRef], PortFace | None]
"""Su che faccia guarda una porta, o `None` se la posa non colloca il pezzo."""


def pavimento_della_catena(
    steps: tuple[tuple[PortRef, PortRef], ...], face_of: PortFaceOf
) -> int | None:
    """Quante pieghe **le facce dei simboli** impongono a una catena intera.

    E' il pavimento di **B1**. Due addendi, e il secondo e' quello che il 22
    settembre 2026 mancava:

    1. **i crocevia** — su ogni pezzo che la catena attraversa, le pieghe fra
       le due porte da cui entra ed esce (`curve_imposte_dal_crocevia`);
    2. **i tratti fra due capi fissi** — le pieghe fra le porte di due pezzi
       diversi (`curve_imposte_fra_due_pezzi`).

    **Chi e' un capo fisso.** I due capi della catena, e ogni crocevia **dove la
    catena gira**. Un pezzo che la catena **passa dritta** — due facce opposte —
    non lo e': la sua giacitura segue la catena, perche' e' esattamente cio'
    che la catena e' («la linea passa, non si piega intorno a lui», **B4**; e
    il raccordo lo si attraversa sull'asse, `highways`). Se una posa lo lascia
    di traverso, la linea gli gira intorno con due gomiti che un quarto di giro
    toglie, e quei gomiti non sono imposti: il pavimento misura il tratto **da
    un capo fisso all'altro**, scavalcando i passaggi dritti.

    Un pezzo che la catena tocca **due volte** — un anello che torna sul pezzo
    da cui era passata — resta fisso anche dove lo passa dritto: la sua
    giacitura la guardano tutt'e due le volte, e non si puo' girarla per una
    sola.

    **Un crocevia dove la catena gira resta com'e' posato.** Girarlo di un
    quarto sposta la L da una tratta all'altra, e la toglie da tutt'e due solo
    se il pezzo sta di traverso rispetto a tutt'e due i vicini. Cercato sulle
    nove tavole del 23 settembre 2026, il caso compare una volta sola: la presa
    dell'anello del ricircolo della tavola approvata, dove le due tratte tornano
    sullo stesso pezzo e il quarto di giro non si puo' fare. Altrove la
    rotazione di un raccordo la deduce il motore, verso i vicini che ha (C2).

    `None` quando la posa non colloca una delle porte: un pavimento a meta' non
    e' un pavimento.
    """
    ports: list[PortRef] = [steps[0][0]]
    for (_, entrata), (uscita, _) in zip(steps, steps[1:], strict=False):
        ports.extend((entrata, uscita))
    ports.append(steps[-1][1])
    faces = [face_of(ref) for ref in ports]
    known = [face for face in faces if face is not None]
    if len(known) != len(faces):
        return None
    pieces = [ref.component_id for ref in ports]

    imposte = 0
    fixed = [True] * len(ports)
    # Le porte di un crocevia sono in coppia: arrivo in posizione dispari,
    # partenza nella successiva.
    for index in range(1, len(ports) - 1, 2):
        arrivo, partenza = known[index], known[index + 1]
        imposte += curve_imposte_dal_crocevia(arrivo, partenza)
        dritto = partenza is arrivo.opposite
        toccato_due_volte = pieces.count(pieces[index]) > 2
        if dritto and not toccato_due_volte:
            fixed[index] = fixed[index + 1] = False

    start = 0
    while start < len(ports) - 1:
        end = start + 1
        while not fixed[end]:
            end += 2
        imposte += curve_imposte_fra_due_pezzi(known[start], known[end])
        start = end + 1
    return imposte


def turns_forced(highway: Highway, port_at: PortAt) -> int | None:
    """Quante curve **i simboli che la catena tocca impongono** a questa catena.

    E' il pavimento di **B1** dopo **D-171**: il PO ha detto che la regola e'
    «piu' dritte possibili, **meno curve possibili**, meno sormonti possibili»,
    e che **un numero massimo non c'e'** — «dicevo una curva nel caso del
    generatore singolo e due accumuli, ma era per far capire il concetto». Un
    massimo fisso si insegue (**D-164**); un pavimento no, perche' non si
    guadagna niente a starci sopra e non si puo' scendere sotto.

    Il conto e' `pavimento_della_catena`, sulle facce che questa posa da'. Tre
    casi, misurati sulle tavole:

    - una catena che attraversa un **collettore verticale** ne ha **due**, una
      per capo: si entra di fianco, si sale, si esce di fianco. E' la
      contraddizione fra **B1** e **B3**, chiusa da D-171;
    - una che attraversa una **valvola a tre vie sulla terza via** ne ha
      **una**: la terza via e' perpendicolare alla via dritta e gira insieme a
      lei;
    - una che **finisce** in un collettore verticale, o che corre fra due porte
      su assi perpendicolari, ne ha **una**: e' la L fra due pezzi, e la tavola
      5 approvata dal PO il 23 settembre 2026 (**I-108**) ne porta sette.

    **Il gradino di una coppia** — mandata e ritorno fra due pezzi con
    interassi diversi — qui non si vede, perche' guarda due catene insieme: lo
    conta la tavola, `autostrade.gradini_delle_coppie`.

    `None` quando la posa non colloca un pezzo della catena: non c'e' un
    pavimento da dare, e chi chiama non deve leggerne uno.
    """

    def face_of(ref: PortRef) -> PortFace | None:
        found = port_at(ref.component_id, ref.port_id)
        return None if found is None else found[1]

    return pavimento_della_catena(highway.steps, face_of)


def lies_in_line(highway: Highway, port_at: PortAt) -> bool:
    """Vero se la catena sta **nella propria forma**, con questa posa.

    La forma e' quella che **le facce dei pezzi che tocca consentono**: le
    due porte di ogni tratta si guardano in faccia, la tratta va nel verso della
    porta da cui parte, e la catena non piega **piu' di quanto i simboli le
    impongano** — `turns_forced`. E' la condizione che fallisce quando ogni
    frammento e' dritto e la catena fa un gomito **in piu'** sul raccordo che li
    unisce.

    **Il confronto non e' con un numero** (**D-171**): non c'e' un massimo di
    curve, ce n'e' un minimo imposto dai simboli, e la posa che ci sta sopra ha
    piegato per scelta propria. Prima di D-171 il paragone era
    `Highway.turns_allowed` — zero fra le macchine di spina, uno verso i
    terminali — e accusava le catene che passano per un collettore verticale,
    che di pieghe ne hanno due per forza.

    Una posa che non colloca uno dei pezzi non e' una catena storta: e' una
    catena che non si puo' ancora misurare, e la risposta e' `False` senza
    giudizio — chi chiama usa l'invariante in modo monotono, «cio' che e' dritto
    non si storce», e su una catena non misurabile non c'e' niente da
    conservare.
    """
    turns = turns_of(highway, port_at)
    imposte = turns_forced(highway, port_at)
    return turns is not None and imposte is not None and turns <= imposte


def crooked_highways(
    laid: Iterable[Highway], port_at: PortAt
) -> tuple[Highway, ...]:
    """Le catene che con questa posa non sono una retta."""
    return tuple(item for item in laid if not lies_in_line(item, port_at))


__all__ = [
    "Highway",
    "PortAt",
    "PortFaceOf",
    "crooked_highways",
    "curve_imposte_dal_crocevia",
    "curve_imposte_fra_due_pezzi",
    "highways",
    "lies_in_line",
    "pavimento_della_catena",
    "turns_forced",
    "turns_of",
]
