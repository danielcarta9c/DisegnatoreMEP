"""L'esecutore del piano: il motore esegue quello che il pianificatore ha composto.

E' `scripts/piano.py` portato in `src/`, e non e' una riscrittura: la logica e
le note misurate che stavano nei suoi commenti sono la memoria del progetto e
stanno qui. Il pezzo che ha prodotto le due tavole della prova
(`docs/collaudi/PROVA-PIANO/`) e' questo.

**Che cosa NON gira, ed e' il punto** (D-151): ne' `lay_the_spine` — la fase
del tronco — ne' `improve_sheet` — il ciclo di miglioramento. Sono le due che
**cercano** invece di comporre. Tutto il resto e' il motore di sempre, e sono
le parti che la ricerca del 4 agosto §3 dichiara sane: gli accessori appesi
seguono il proprio pezzo, l'instradamento e' ortogonale e in griglia, le linee
si interrompono sotto i simboli, la legenda, le sigle, gli indirizzi, i
validatori.

Il giro, in ordine:

1. la **posa di partenza** come inventario — simboli, rotazioni, mappa delle
   porte — e le coordinate le sovrascrive il piano;
2. **la semina**: chi non e' nel piano segue il proprio pezzo (`carry_the_rest`);
3. **la deduzione della rotazione** (`orienta`), che e' l'unica decisione che
   l'esecutore prende, e la prende solo dove non c'e' scelta;
4. **la traslazione nell'area**: il disegno si porta al centro dell'area del
   formato **prima** di instradarlo, perche' del piano contano le posizioni
   relative e non quelle sul foglio;
5. **l'instradamento** e gli accessori in linea (`settle_sheet`);
6. legenda, centratura, sigle, indirizzi;
7. il **preflight**, che misura.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.layout.addresses import with_addresses
from disegnatore_mep.layout.compose import centre_vertically, inline_component_ids
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import settle_sheet
from disegnatore_mep.layout.labels import place_labels
from disegnatore_mep.layout.legend import build_legend
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import SpineLayout, carry_the_rest
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.piano.formato import ErroreDelPiano, PianoDiComposizione
from disegnatore_mep.validation.issues import ValidationIssue
from disegnatore_mep.validation.preflight import preflight_drawing

_LARGHEZZE_MM: dict[str, float] = {"A4": 297.0, "A3": 420.0, "A2": 594.0, "A1": 841.0}
"""La larghezza di ciascun formato ordinario, che e' come lo si riconosce."""

_VERSO: dict[PortFace, tuple[float, float]] = {
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
    PortFace.BOTTOM: (0.0, 1.0),
}
"""Da che parte guarda ciascuna faccia, con y verso il basso come in SVG."""


def _frame(nome: str) -> SheetFrame:
    """La squadratura del formato che il piano ha chiesto."""
    voluta = _LARGHEZZE_MM[nome]
    for item in ORDINARY_FRAMES:
        if abs(item.standard.sheet_width_mm - voluta) < 1e-6:
            return item
    raise ErroreDelPiano(f"formato {nome} sconosciuto")


def orienta(
    posati: list[PlacedSymbol],
    modello: ProjectModel,
    partizione: SheetPartition,
    catalogo: ComponentRegistry,
    fissate: frozenset[str],
) -> list[PlacedSymbol]:
    """Ogni pezzo si **gira verso i vicini che ha davvero**.

    E' il controllo che `docs/regole-del-piano.md` **C2** nomina per nome. Il
    piano dice **dove** sta un pezzo. Da che parte guarda non glielo deve dire:
    si deduce, e deve dedursi, perche' e' una conseguenza della posa e non una
    scelta di chi compone.

    Sono due cose insieme, e vanno decise insieme:

    * la **rotazione** del simbolo — quale faccia porta ciascun attacco;
    * la **mappa delle porte** (`PlacedSymbol.port_map`) — quale attacco fisico
      serve quale porta del modello. Per un raccordo a T, che si disegna come un
      punto e ha tre attacchi uguali, la posa puo' mandare la prosecuzione
      sull'attacco perpendicolare perche' il percorso principale giri dentro il
      raccordo invece che in un gomito a parte (D-004, I-027).

    **Misurato il 20 settembre, ed e' la ragione per cui questa funzione fa
    anche la rotazione.** Nel primo piano dell'impianto 1 il tee del manometro
    era rimasto a `rot=0`, cioe' con lo stacco rivolto **in su**, mentre il
    piano aveva messo il manometro **sotto**. La linea usciva in alto, girava a
    destra, scendeva per sessanta millimetri, tornava indietro e risaliva: il
    rettangolo che il PO ha cerchiato chiedendo «perche' non sei andato
    dritto?». Gli altri due tee dello stesso gruppo erano a `rot=180` per caso,
    perche' cosi' li aveva lasciati la posa di partenza.

    Il criterio e' uno solo e non ha pesi: **ogni porta guarda il proprio
    vicino.** Fra le rotazioni che il simbolo dichiara ammesse si prende quella
    che allinea meglio gli attacchi con i pezzi dall'altro capo; a rotazione
    scelta, ogni porta prende l'attacco che punta di piu' da quella parte. Un
    prodotto scalare e un'assegnazione avida. **Nessuna ricerca.**

    **La rotazione si deduce solo dove non c'e' scelta** (C2): per un
    **raccordo** — che e' un punto sulla tubazione — e per un pezzo con **un
    attacco solo**. Una macchina con due o piu' attacchi in uso **ha** una
    scelta, e quella scelta e' del pianificatore.

    ⚠ **Il buco noto** (`ARCHITETTURA-DEL-PIANO.md` §4): un pezzo con **due**
    attacchi che **non e' una macchina** — il gruppo di riempimento — non
    rientra in nessuno dei due casi. Qui conta come una macchina, cioe' la sua
    rotazione **non si deduce** e va scritta a mano nel piano. E' cosi' che
    `impianto-1.json` scrive `"rotazione": 180` sul proprio gruppo di
    riempimento, e lo dice nelle note.

    **La mappa delle porte si rifa' soltanto per i raccordi** (C3, D-004,
    I-027). Un T si disegna come un punto e ha tre attacchi **uguali**: quale
    porta del modello stia su quale attacco e' una scelta della posa. Su una
    macchina no: `primary_out` e `cold_in` di un accumulo sono due bocchettoni
    **fisici diversi del serbatoio**, e scambiarli non e' un ritocco grafico,
    e' un altro impianto.

    **Misurato il 20 settembre.** Rimappando anche le macchine, l'acqua fredda
    dell'impianto 1 finiva sulla porta a quota 211 — che e' `primary_out` —
    invece che su `cold_in` a 228,5: il ritorno e l'ingresso sanitario
    arrivavano allo stesso punto, e il PO l'ha visto guardando la tavola. Era un
    errore di **contenuto** prodotto da una deduzione grafica.

    `fissate` sono i pezzi per cui il piano ha scritto la rotazione a mano: li'
    la scelta e' del compositore e non si tocca.
    """
    definizioni = {item.id: item.definition_id for item in modello.components}
    dove = {item.component_id: item for item in posati}

    vicini: dict[str, dict[str, str]] = {}
    for trunk in partizione.trunks:
        for mio, suo in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
            if mio.component_id != suo.component_id:
                vicini.setdefault(mio.component_id, {})[mio.port_id] = suo.component_id

    def centro(item: PlacedSymbol) -> tuple[float, float]:
        return (
            item.origin.x_mm + item.width_mm / 2,
            item.origin.y_mm + item.height_mm / 2,
        )

    def accoppia(
        manifesto: SymbolManifest, item: PlacedSymbol, porte: dict[str, str]
    ) -> tuple[float, dict[str, str]]:
        """Il punteggio della rotazione, e la mappa che ne esce."""
        mio_centro = centro(item)
        preferenze: list[tuple[float, str, str]] = []
        for porta, altro in sorted(porte.items()):
            if altro not in dove:
                continue
            suo = centro(dove[altro])
            verso = (suo[0] - mio_centro[0], suo[1] - mio_centro[1])
            norma = max(abs(verso[0]) + abs(verso[1]), 1e-9)
            verso = (verso[0] / norma, verso[1] / norma)
            # `bocchettone` e non `attacco` perche' qui si tiene in mano
            # l'attacco **fisico** del simbolo, e tre righe piu' giu' `attacco`
            # e' il suo identificativo: due cose diverse, due nomi diversi.
            for bocchettone in manifesto.ports:
                faccia = _VERSO[bocchettone.face]
                preferenze.append(
                    (
                        -(faccia[0] * verso[0] + faccia[1] * verso[1]),
                        porta,
                        bocchettone.id,
                    )
                )
        preferenze.sort()
        mappa: dict[str, str] = {}
        presi: set[str] = set()
        punteggio = 0.0
        for meno_punteggio, porta, attacco in preferenze:
            if porta in mappa or attacco in presi:
                continue
            mappa[porta] = attacco
            presi.add(attacco)
            punteggio -= meno_punteggio
        for bocchettone in manifesto.ports:
            if bocchettone.id not in presi and bocchettone.id not in mappa:
                mappa.setdefault(bocchettone.id, bocchettone.id)
        return punteggio, mappa

    fuori: list[PlacedSymbol] = []
    for item in posati:
        porte = vicini.get(item.component_id, {})
        if not porte:
            fuori.append(item)
            continue
        risolto = catalogo.resolve(definizioni[item.component_id])
        base = risolto.symbol.manifest
        # **Si gira chi non ha scelta.** Un pezzo attaccato da una parte sola —
        # uno sfiato, uno scarico, un vaso, un manometro — non decide come sta
        # sul foglio: il suo unico attacco deve guardare chi lo regge, e
        # basta. Lo stesso vale per un raccordo, che e' un punto sulla
        # tubazione: il suo verso e' una conseguenza di dove passa la linea.
        #
        # Una macchina con due o piu' attacchi in uso **ha** una scelta, e
        # quella scelta e' di chi compone: se l'accumulo guarda a destra o a
        # sinistra cambia tutto il disegno. Misurato il 20 settembre: girando
        # anche le macchine, l'accumulo ruotava e la mandata dell'ACS usciva da
        # un'altra faccia, con la miscelatrice che si ritrovava sulla piega
        # della propria tratta.
        raccordo = risolto.definition.is_a_fitting
        #
        # **Le giaciture provate sono otto, non quattro** (**D-169**): le
        # rotazioni ammesse, per diritto o specchiate. Vale solo per chi non ha
        # scelta — un raccordo, un pezzo con un attacco solo — perche' per chi
        # ce l'ha la giacitura la decide **il piano**, specchio compreso.
        deduce = (raccordo or len(porte) < 2) and item.component_id not in fissate
        giaciture = (
            [(g, s) for g in sorted(base.allowed_rotations_deg) for s in (False, True)]
            if deduce
            else [(item.rotation_deg, item.specchiato)]
        )
        scelta: tuple[float, PlacedSymbol, dict[str, str]] | None = None
        for gradi, specchiato in giaciture:
            manifesto = base.rotated(gradi, specchiato)
            provvisorio = item.model_copy(
                update={
                    "rotation_deg": gradi,
                    "specchiato": specchiato,
                    "width_mm": manifesto.width_mm,
                    "height_mm": manifesto.height_mm,
                }
            )
            punteggio, mappa = accoppia(manifesto, provvisorio, porte)
            if scelta is None or punteggio > scelta[0] + 1e-9:
                scelta = (punteggio, provvisorio, mappa)
        assert scelta is not None
        # **La mappa delle porte si rifa' solo per i raccordi** (C3): sulla
        # macchina si tiene quella che la posa aveva, e si cambia soltanto come
        # sta girata.
        fuori.append(
            scelta[1].model_copy(update={"port_map": scelta[2]})
            if raccordo
            else scelta[1]
        )
    return fuori


@dataclass(frozen=True)
class EsitoDelPiano:
    """Che cosa e' uscito dall'esecuzione di un piano — anche quando non esce.

    **La diagnostica utile e' la posa, non il messaggio.** Chi compone deve
    poter vedere che cosa ha lasciato in mezzo e correggere il piano invece di
    indovinare: per questo `posa` c'e' **sempre**, anche quando il piano non si
    instrada e `disegno` e' `None`.
    """

    disegno: DrawingGeometry | None
    """La tavola. `None` se il piano non si instrada."""

    frame: SheetFrame
    """La squadratura del formato che il piano ha chiesto."""

    rilievi: list[ValidationIssue]
    """Le misure del preflight. Vuote se il piano non si instrada."""

    posa: tuple[PlacedSymbol, ...]
    """La posa applicata, **sempre**: e' la diagnostica utile.

    Sono i pezzi come il piano li ha messi, portata a termine dalla semina e
    dalla deduzione della rotazione — **prima** dell'instradamento e della
    centratura. E' apposta: le coordinate stanno cosi' nello stesso sistema in
    cui e' scritto il piano, e chi corregge il piano legge qui senza dover
    togliere una traslazione — nemmeno il millimetro con cui la griglia del
    motore, che parte dall'angolo dell'area, si discosta da quella del piano.
    La tavola finita sta in `disegno`.
    """

    partizione: SheetPartition
    """La partizione usata. Serve a chi deve sapere quali tratte sono autostrada."""

    errore: str | None
    """Il messaggio dell'instradamento che non si chiude. `None` se si e' chiuso."""

    girati: tuple[str, ...]
    """I pezzi girati dalla deduzione, nella forma `id 0->180`."""

    @property
    def bloccanti(self) -> list[ValidationIssue]:
        """I soli rilievi che fermano una consegna (D-063)."""
        return [
            item for item in self.rilievi if item.severity == IssueSeverity.BLOCKING
        ]

    @property
    def cedute(self) -> tuple[RoutedTrunk, ...]:
        """Le tratte che hanno preso la spezzata di ripiego (D-150).

        Da questa via sono **sempre vuote per costruzione**: `settle_sheet` gira
        qui senza `last_resort`, quindi una tratta che non si instrada solleva
        invece di cedere, e l'esito e' un piano che non si instrada. Restano
        contate perche' il contratto di D-150 e' che una tavola ceduta si dica,
        e perche' il giorno che questa via accendesse il ripiego il conto e' gia'
        al suo posto.
        """
        if self.disegno is None:
            return ()
        return tuple(
            tratta
            for foglio in self.disegno.sheets
            for tratta in foglio.routes
            if tratta.unresolved
        )


def _detto_nel_piano(
    messaggio: str, partizione: SheetPartition, posa: tuple[PlacedSymbol, ...]
) -> str:
    """L'errore dell'instradamento, con i due capi della tratta **nel sistema
    del piano**.

    L'instradatore dice le celle della propria griglia — «no route from (117,
    25) to (122, 26)» — contate dall'angolo dell'area e dopo la traslazione che
    porta il disegno al centro: chi compone non ha modo di riportarle sul
    piano, e due agenti in camera pulita l'hanno scritto il 23 settembre 2026.
    Qui si aggiunge quello che il piano sa leggere: quali pezzi la tratta
    unisce, e dove il piano li ha messi.
    """
    trovata = re.search(r"\brun (\S+) on network", messaggio)
    if trovata is None:
        return messaggio
    tratta = next(
        (
            trunk
            for trunk in partizione.trunks
            if trovata.group(1) in trunk.connection_ids
        ),
        None,
    )
    if tratta is None:
        return messaggio
    dove = {item.component_id: item.origin for item in posa}
    capi = [
        f"{ref.component_id}.{ref.port_id}"
        + (
            f" (il pezzo sta a {dove[ref.component_id].x_mm:g}, "
            f"{dove[ref.component_id].y_mm:g} nel piano)"
            if ref.component_id in dove
            else ""
        )
        for ref in (tratta.start, tratta.end)
    ]
    return (
        f"{messaggio} — la tratta va da {capi[0]} a {capi[1]}; le coppie fra "
        "parentesi del messaggio sono celle della griglia del foglio, non "
        "millimetri del piano"
    )


def esegui_piano(
    modello: ProjectModel,
    piano: PianoDiComposizione,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
    naming: Path,
    verifica: bool = False,
) -> EsitoDelPiano:
    """Esegue un piano di composizione, e misura quello che ne esce.

    **Non gira nessuna ricerca**: ne' `lay_the_spine` ne' `improve_sheet`. Se la
    tavola esce bene senza di loro, l'approccio e' dimostrato — ed e' quello che
    la prova del 19/20 settembre ha misurato: ~30 secondi a giro contro i 10-40
    minuti del solutore.

    `simboli` non serve all'esecuzione — il catalogo porta gia' i simboli
    risolti — e sta nella firma perche' chi esegue un piano poi lo **disegna**:
    il renderer vuole la libreria, e il revisore che si costruisce su questo
    esito la riceve di qui senza doverla ricaricare.

    Solleva `ErroreDelPiano` se il piano nomina pezzi che non esistono nel
    modello, elencandoli: e' un difetto del piano, non della tavola, e va detto
    prima di posare qualunque cosa.
    """
    frame = _frame(piano.formato)
    area = frame.drawing_rect_mm
    grid = GridSpace(origin=area, standard=frame.standard)

    inline = inline_component_ids(modello, catalogo)
    partizione = partition_project(modello, build_trunks(modello, inline))[0]

    # 1. La posa di partenza serve solo come **inventario**: da lei si prendono
    #    i simboli, le rotazioni e la mappa delle porte di ogni pezzo. Le
    #    coordinate che calcola le sovrascrive il piano.
    partenza = place_sheet(modello, partizione, catalogo, frame, inline)
    per_id = {item.component_id: item for item in partenza}

    ignoti = sorted(set(piano.pezzi) - set(per_id))
    # **Chi e' nel modello ma non si posa col piano va detto per nome**: sono
    # gli organi in linea, che il motore mette da solo sulla loro tratta. Fino
    # al 23 settembre 2026 finivano fra i pezzi «che non esistono nel modello»,
    # e chi componeva leggeva un messaggio falso su un pezzo che il grafo
    # porta.
    in_linea = sorted(set(ignoti) & inline)
    inesistenti = [item for item in ignoti if item not in inline]
    if inesistenti:
        raise ErroreDelPiano(
            "il piano nomina pezzi che non esistono nel modello: "
            f"{', '.join(inesistenti)}"
        )
    if in_linea:
        raise ErroreDelPiano(
            "il piano posa organi in linea, che il motore mette da solo sulla loro "
            f"tratta: {', '.join(in_linea)} — toglili dal piano (il loro simbolo "
            "dichiara `inline_gap_mm`)"
        )

    def in_griglia(valore: float, base: float) -> float:
        passo = frame.standard.grid_mm
        return base + round((valore - base) / passo) * passo

    posati: list[PlacedSymbol] = []
    for component_id, dove in piano.pezzi.items():
        item = per_id[component_id]
        aggiornamenti: dict[str, object] = {
            "origin": Point(
                x_mm=in_griglia(dove.x, area.x_mm),
                y_mm=in_griglia(dove.y, area.y_mm),
            )
        }
        if dove.rotazione is not None:
            aggiornamenti["rotation_deg"] = dove.rotazione
        if dove.specchio:
            aggiornamenti["specchiato"] = True
        posati.append(item.model_copy(update=aggiornamenti))

    # 2. Chi non e' nel piano **segue il proprio pezzo**: e' la stessa meccanica
    #    con cui la fase del tronco trascinava il resto dell'impianto, e qui
    #    la si usa tale e quale — solo che i partecipanti li ha scelti il piano.
    finta_fase = SpineLayout(
        machines=frozenset(piano.pezzi),
        participants=tuple(piano.pezzi),
        trunks=(),
        symbols=tuple(posati),
        routes=(),
        runs=(),
        routed=True,
    )
    seminata = carry_the_rest(modello, partizione, catalogo, partenza, finta_fase, frame)
    fissate = frozenset(
        component_id
        for component_id, dove in piano.pezzi.items()
        if dove.rotazione is not None
    )
    prima_di_girare = {
        item.component_id: (item.rotation_deg, item.specchiato) for item in seminata
    }
    seminata = orienta(seminata, modello, partizione, catalogo, fissate)
    # **La giacitura e' rotazione piu' specchio** (D-169), e il rapporto le dice
    # tutt'e due. Finche' diceva la sola rotazione, un pezzo che la deduzione
    # specchiava senza girarlo non compariva affatto, e il 22 settembre 2026 un
    # agente ne ha dedotto — leggendo questo elenco — che la deduzione provasse
    # quattro giaciture invece di otto.
    girati = tuple(
        f"{item.component_id} {prima_di_girare[item.component_id][0]}->{item.rotation_deg}"
        + (" specchiato" if item.specchiato else "")
        for item in seminata
        if prima_di_girare[item.component_id] != (item.rotation_deg, item.specchiato)
    )
    # **La posa si dice nel sistema del piano.** La griglia del motore parte
    # dall'angolo dell'area da disegno, che su un A3 sta a 16 mm dal bordo: un
    # piano scritto sui multipli del passo si siede un millimetro piu' in basso.
    # Il disegno e' giusto — le posizioni relative non cambiano — ma fino al 23
    # settembre 2026 la posa lo riportava cosi', e due agenti in camera pulita
    # hanno letto «y spostate di +1 mm» senza poterne sapere il perche'.
    scarto_x = area.x_mm - round(area.x_mm / frame.standard.grid_mm) * frame.standard.grid_mm
    scarto_y = area.y_mm - round(area.y_mm / frame.standard.grid_mm) * frame.standard.grid_mm
    posa = tuple(
        item.model_copy(
            update={
                "origin": Point(
                    x_mm=item.origin.x_mm - scarto_x, y_mm=item.origin.y_mm - scarto_y
                )
            }
        )
        for item in seminata
    )

    # 3. **Il motore trasla prima di instradare.** Il piano dice dove stanno i
    #    pezzi gli uni rispetto agli altri; dove stia il disegno sul foglio non
    #    lo sa, e non glielo si chiede. Si porta al centro dell'area con la
    #    stessa centratura che lo rimette a posto a tavola finita, e lo spostamento
    #    e' un multiplo del passo, quindi nessuna porta esce dalla griglia.
    #    **Misurato il 22 settembre 2026**, sulla tavola che il PO ha poi
    #    approvato: lo stesso piano spostato di (-20, -105) non si instradava —
    #    «every orthogonal path is blocked» — perche' le tratte dei pezzi a
    #    coordinate negative stavano fuori dalla griglia. Adesso da' la stessa
    #    tavola, e le nove tavole agli atti non si spostano di un punto.
    seminata = list(
        centre_vertically(
            SheetGeometry(
                sheet_id=partizione.sheet_id,
                title=partizione.title,
                symbols=seminata,
            ),
            area,
            frame.standard.grid_mm,
        ).symbols
    )

    # 4. Da qui in avanti e' il motore di sempre: instradamento, accessori in
    #    linea, legenda, centratura, testi. **Nessuna ricerca.**
    try:
        sistemata = settle_sheet(
            modello, list(partizione.trunks), seminata, catalogo, grid
        )
    except LayoutError as errore:
        return EsitoDelPiano(
            disegno=None,
            frame=frame,
            rilievi=[],
            posa=posa,
            partizione=partizione,
            errore=_detto_nel_piano(str(errore), partizione, posa),
            girati=girati,
        )

    voci, chiavi = build_legend(
        modello,
        sistemata.symbols,
        partizione.network_ids,
        catalogo,
        frame,
        routes=sistemata.routes,
    )
    foglio = SheetGeometry(
        sheet_id=partizione.sheet_id,
        title=partizione.title,
        symbols=sistemata.symbols,
        routes=sistemata.routes,
        legend=voci,
        network_keys=chiavi,
    )
    foglio = centre_vertically(foglio, area, frame.standard.grid_mm)
    foglio = foglio.model_copy(
        update={
            "labels": place_labels(
                modello,
                foglio.symbols,
                frame.standard,
                routes=foglio.routes,
                area=area,
            )
        }
    )
    disegno = DrawingGeometry(project_id=modello.metadata.project_id, sheets=[foglio])
    # **Gli indirizzi dei nodi si chiedono, non si subiscono** (D-110). Fino al
    # 20 settembre il piano li metteva sempre, e la conseguenza si vedeva a
    # colpo d'occhio: la tavola che il PO guarda per giudicare il **disegno**
    # arrivava coperta di sigle di verifica, e giudicare il disegno e' il suo
    # controllo (D-146). `--verifica` resta, ed e' preziosa per chi cerca un
    # pezzo sul grafo; ma la tavola ordinaria e' quella di consegna.
    if verifica:
        disegno = with_addresses(disegno, modello, catalogo, frame, naming)

    return EsitoDelPiano(
        disegno=disegno,
        frame=frame,
        # **Il modello si passa al preflight** (DRAW-015): senza, la piega di
        # un'autostrada si conta col metro di uno stacchetto, ed e' il difetto
        # che ha generato D-151. Con il modello, `bends_per_run` sa quali
        # tratte sono autostrada e quante pieghe la loro catena ammette.
        rilievi=preflight_drawing(disegno, frame, catalogo, modello),
        posa=posa,
        partizione=partizione,
        errore=None,
        girati=girati,
    )
