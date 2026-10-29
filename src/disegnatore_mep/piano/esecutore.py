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
6. legenda, centratura, **la tabella delle apparecchiature** — e il disegno
   che le fa spazio (REL-006) —, sigle, indirizzi;
7. il **preflight**, che misura.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.scritte import CAMPIONE_DELLA_LEGENDA as CAMPIONE_DELLA_SCRITTA
from disegnatore_mep.diametri.scritte import TESTO_DELLA_LEGENDA as TESTO_DELLA_SCRITTA
from disegnatore_mep.diametri.scritte import tratti_da_scrivere
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.graphics.tabella import sigle_sul_disegno, tabella_della_tavola
from disegnatore_mep.graphics.tabelle import posa_le_tabelle
from disegnatore_mep.layout.addresses import with_addresses
from disegnatore_mep.layout.compose import (
    centre_vertically,
    inline_component_ids,
    sgombra_la_tabella,
)
from disegnatore_mep.layout.diametri import (
    CAMPIONE_DELLA_LEGENDA,
    TESTO_DELLA_LEGENDA,
    note_della_legenda,
    posa_i_diametri,
    riquadro_del_diametro,
)
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    SHEET_MARGIN_MIN_MM,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
    TabellaNelleZone,
    zona_della_tabella,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import settle_sheet
from disegnatore_mep.layout.labels import place_labels, place_tags_that_yield
from disegnatore_mep.layout.legend import build_legend
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import SpineLayout, carry_the_rest
from disegnatore_mep.layout.trunks import build_trunks, porte_di_comando_in_linea
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.piano.formato import ErroreDelPiano, PianoDiComposizione
from disegnatore_mep.piano.vista import (
    CAMPIONE_DEL_RIMANDO,
    rimando,
    sigle_del_grafo_intero,
    vista_del_grafo,
)
from disegnatore_mep.validation.issues import ValidationIssue
from disegnatore_mep.validation.preflight import preflight_drawing

_LARGHEZZE_MM: dict[str, float] = {"A3": 420.0, "A2": 594.0, "A1": 841.0}
"""La larghezza di ciascun formato ordinario, che e' come lo si riconosce."""

_VERSO: dict[PortFace, tuple[float, float]] = {
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
    PortFace.BOTTOM: (0.0, 1.0),
}
"""Da che parte guarda ciascuna faccia, con y verso il basso come in SVG."""


_FOGLIO_DELL_INVENTARIO = SheetFrame(
    standard=ORDINARY_FRAMES[-1].standard.model_copy(
        update={"sheet_width_mm": 4000.0, "sheet_height_mm": 3000.0}
    )
)
"""Il foglio su cui si rifa' la posa d'inventario quando quella sul formato del piano non
entra: grande abbastanza per qualunque centrale, e mai disegnato."""


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

    # **Un cavo non gira un pezzo che ha il suo tubo** (REL-012, fase 3). La sonda
    # pende dal suo tubo e manda il segnale al regolatore: guarda il tubo, e il cavo
    # parte da dove la sonda lo porta. Sulla tavola dell'elettrico il tubo non c'e',
    # e allora la sonda guarda il suo cavo.
    vicini: dict[str, dict[str, str]] = {}
    via_cavo: dict[str, dict[str, str]] = {}
    for trunk in partizione.trunks:
        for mio, suo in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
            if mio.component_id == suo.component_id:
                continue
            voce = definizioni.get(mio.component_id)
            if voce is not None and mio.port_id in catalogo.porte_di_comando(voce):
                via_cavo.setdefault(mio.component_id, {})[mio.port_id] = suo.component_id
                continue
            vicini.setdefault(mio.component_id, {})[mio.port_id] = suo.component_id
    for component_id, porte_del_cavo in via_cavo.items():
        vicini.setdefault(component_id, porte_del_cavo)

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
            # Una porta di comando e' il suo attacco e nessun altro (REL-012): il
            # cavo non si sposta su un bocchettone dell'acqua.
            candidati = (
                [manifesto.port(porta)]
                if porta in manifesto.control_port_ids
                else manifesto.ports
            )
            for bocchettone in candidati:
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

    modello: ProjectModel
    """Il grafo che la tavola disegna: quello della vista del piano (REL-012). Per la
    tavola unica e' il grafo dato."""

    catalogo: ComponentRegistry
    """Il catalogo di quel grafo, con le porte di comando che collega (REL-012):
    quello con cui chi viene dopo — le regole del piano, il cartiglio — deve leggere
    la tavola."""

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


def con_le_porte_scollegate(
    foglio: SheetGeometry,
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    reti: Sequence[str],
) -> SheetGeometry:
    """Il foglio con, su ogni pezzo, le porte che **nessuna linea della tavola**
    collega fra quelle che il corpo del simbolo disegna col loro moncone
    (collaudo T1 di REL-012, §3).

    Sul canalizzato del collaudo la centrale di zona disegnava il moncone del
    quarto bus, che nessun termostato usava: si leggeva come un attacco libero. Il
    renderer toglie il moncone di queste porte. Una porta conta collegata se una
    tubazione **di una rete di questa tavola** ci arriva: sulla tavola idraulica di
    un grafo con l'elettrico, il cavo sta sull'altra, e il suo moncone non c'e'.

    Solo i simboli con i gruppi `data-port` — le macchine dell'aria-aria e del
    comando — hanno qualcosa da togliere; gli altri restano com'erano, e la loro
    geometria non cambia di un byte."""
    sulla_tavola = set(reti)
    collegate = {
        (ref.component_id, ref.port_id)
        for item in modello.connections
        if item.network_id in sulla_tavola
        for ref in (item.endpoint_a, item.endpoint_b)
    }
    voce = {item.id: item.definition_id for item in modello.components}
    posati: list[PlacedSymbol] = []
    for placed in foglio.symbols:
        definizione = voce.get(placed.component_id)
        if definizione is None:
            posati.append(placed)
            continue
        col_moncone = catalogo.resolve(definizione).symbol.porte_col_moncone
        if not col_moncone:
            posati.append(placed)
            continue
        attaccate = {
            placed.physical_port(porta)
            for componente, porta in collegate
            if componente == placed.component_id
        }
        libere = sorted(col_moncone - attaccate)
        posati.append(placed.model_copy(update={"porte_scollegate": libere}) if libere else placed)
    return foglio.model_copy(update={"symbols": posati})


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
    tabelle: Sequence[TabellaNelleZone] = (),
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

    `tabelle` sono le tabelle che un altro modulo — la distinta, la tabella delle
    tratte (REL-013) — vuole sulla tavola, nelle zone che il piano lascia
    (`zone_tabelle`): il motore le posa e le disegna (`graphics.tabelle`). Una
    tabella che non entra nella sua zona e' un `LayoutError` che lo dice.
    """
    # **La vista** (REL-012, fase 3, I-227): la tavola unica, l'idraulica o
    # l'elettrico e il comando dallo stesso grafo. Da qui in avanti il grafo e' quello
    # della vista, e il catalogo quello di quel grafo — con le porte di comando che
    # collega, e soltanto quelle: senza elettrico, il catalogo di sempre.
    # Il rimando all'altra tavola si legge sul grafo intero: il numero di ciascuna
    # vista viene dal suo.
    altra_tavola = rimando(modello, piano.vista)
    # Le sigle del grafo intero, per i pezzi fuori dall'acqua (collaudo T1).
    sigle_intere = sigle_del_grafo_intero(modello, catalogo.per_il_progetto(modello), naming)
    modello, catalogo = vista_del_grafo(modello, piano.vista, catalogo, naming)
    frame = _frame(piano.formato)
    # **Le zone delle tabelle** (REL-012): lo stesso foglio, con l'area del disegno
    # piu' stretta. Da qui in avanti tutto — posa, instradamento, centratura, preflight
    # — vede l'area che resta.
    if piano.zone_tabelle is not None:
        try:
            frame = frame.con_le_zone(piano.zone_tabelle.destra_mm, piano.zone_tabelle.basso_mm)
        except ValueError as errore:
            raise ErroreDelPiano(f"le zone delle tabelle non entrano nell'{piano.formato}: {errore}") from errore
    area = frame.drawing_rect_mm
    grid = GridSpace(origin=area, standard=frame.standard)

    inline = inline_component_ids(modello, catalogo)
    partizione = partition_project(
        modello, build_trunks(modello, inline, porte_di_comando_in_linea(modello, catalogo))
    )[0]

    # 1. La posa di partenza serve solo come **inventario**: da lei si prendono
    #    i simboli, le rotazioni e la mappa delle porte di ogni pezzo. Le
    #    coordinate che calcola le sovrascrive il piano.
    try:
        partenza = place_sheet(modello, partizione, catalogo, frame, inline)
    except LayoutError:
        # **L'inventario non e' la tavola** (REL-009, I-205). Se la posa
        # automatica non entra nel formato del piano lo si rifa' su un foglio
        # grande: da lei servono simboli, rotazioni e porte, non le coordinate.
        # Il 3 ottobre 2026 il caso reale, col collettore largo 40, si fermava
        # qui su A1 — «the 1 functional bands need 1317.5mm» — con un piano che
        # posava ogni pezzo dentro l'A1.
        partenza = place_sheet(modello, partizione, catalogo, _FOGLIO_DELL_INVENTARIO, inline)
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
            modello=modello,
            catalogo=catalogo,
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
    foglio = con_le_porte_scollegate(foglio, modello, catalogo, partizione.network_ids)
    foglio = centre_vertically(foglio, area, frame.standard.grid_mm)

    # **La tabella delle apparecchiature, in alto a sinistra** (REL-006, I-141).
    # Si compone qui perche' elenca i pezzi di questa tavola, e il disegno le fa
    # spazio **prima** dei testi: si sposta tutto insieme, e solo se centrato ci
    # entrerebbe. Le apparecchiature della tabella portano la loro sigla anche
    # sul disegno — quella che l'ingegnere ha scritto, o quella della famiglia
    # (D-097) — e i loro dati stanno nella tabella, non accanto al pezzo.
    ostacoli: tuple[tuple[float, float, float, float], ...] = ()
    in_tabella: frozenset[str] = frozenset()
    tabella = tabella_della_tavola(modello, catalogo, naming, foglio, frame)
    if tabella is not None:
        foglio = sgombra_la_tabella(
            foglio, area, tabella.riquadro, frame.standard.grid_mm, SHEET_MARGIN_MIN_MM
        )
        codici = {riga.component_id: riga.codice for riga in tabella.righe if riga.codice}
        foglio = foglio.model_copy(
            update={
                "tabella": tabella,
                "symbols": [
                    item.model_copy(update={"tag": codici[item.component_id]})
                    if item.tag is None and item.component_id in codici
                    else item
                    for item in foglio.symbols
                ],
            }
        )
        ostacoli = (zona_della_tabella(tabella.riquadro),)
        in_tabella = frozenset(riga.component_id for riga in tabella.righe)

    # **I pezzi fuori dall'acqua portano la loro sigla** (collaudo T1 di REL-012):
    # bocchette, riprese, termostati, quadro, sezionatore, sifone, scarico. Sono
    # quelli che la pianta e la distinta citano, e senza una sigla sullo schema non
    # c'era modo di collegare l'una all'altro. L'idronico resta com'e': una valvola
    # la sigla sul disegno non la porta (`tabella.fuori_dall_acqua`). Si posano per
    # ultime, dopo le scritte dei tratti, e cedono (`place_tags_that_yield`).
    # Chi ha gia' una sigla — scritta dal progettista, o il codice della tabella —
    # la porta gia': qui solo gli altri.
    fuori = sigle_sul_disegno(
        modello,
        catalogo,
        sigle_intere,
        (item.component_id for item in foglio.symbols if item.tag is None),
    )

    # Le tubazioni con la scritta del progettista: un testo di pezzo non sta lungo
    # di loro, o si leggerebbe come la loro scritta (collaudo T1 di REL-012).
    scritte, calcolati = tratti_da_scrivere(modello, catalogo)
    linee_scritte = frozenset(item for scritta in scritte for item in scritta.connection_ids)
    foglio = foglio.model_copy(
        update={
            "labels": place_labels(
                modello,
                foglio.symbols,
                frame.standard,
                routes=foglio.routes,
                area=area,
                ostacoli=ostacoli,
                senza_valori=in_tabella,
                linee_scritte=linee_scritte,
            )
        }
    )

    # **Il DN dei tratti, in linea con la tubazione** (REL-007, D-193). Solo se
    # il progettista l'ha chiesto, e sulle reti che ha detto; dopo le sigle,
    # perche' e' l'ultimo testo che si scrive e non sposta niente. La legenda
    # spiega la scritta con una riga sua (I-155), se almeno un tratto la porta.
    #
    # **E la scritta che il progettista ha dato al tratto** (REL-012): «Ø200 · L 6
    # m», «3G2,5 · L 20 m». La posa e' la stessa; un DN calcolato sullo stesso
    # tratto le cede il posto, e la legenda la spiega con una riga sua, «Ø · L»,
    # sotto quella del DN, che resta «Øi».
    # **Le due tavole si rimandano** (REL-012, fase 3): sull'idraulica una riga della
    # legenda dice dove sta l'elettrico e il comando, e viceversa. Sotto le righe delle
    # scritte, se ci sono.
    spiegate: list[tuple[str, str]] = []
    if scritte or calcolati:
        diametri, _ = posa_i_diametri(
            (*scritte, *calcolati), foglio, frame.standard, area, ostacoli
        )
        foglio = foglio.model_copy(update={"diametri": diametri})
        nominate = {frozenset(item.connection_ids) for item in diametri}
        spiegate = [
            voce
            for voce, quali in (
                ((CAMPIONE_DELLA_LEGENDA, TESTO_DELLA_LEGENDA), calcolati),
                ((CAMPIONE_DELLA_SCRITTA, TESTO_DELLA_SCRITTA), scritte),
            )
            if any(frozenset(item.connection_ids) in nominate for item in quali)
        ]
    if fuori:
        foglio = foglio.model_copy(
            update={
                "symbols": [
                    item.model_copy(update={"tag": fuori[item.component_id]})
                    if item.tag is None and item.component_id in fuori
                    else item
                    for item in foglio.symbols
                ],
                "labels": [
                    *foglio.labels,
                    *place_tags_that_yield(
                        foglio.symbols,
                        fuori,
                        frame.standard,
                        routes=foglio.routes,
                        already=foglio.labels,
                        occupied=[
                            (
                                riquadro_del_diametro(item, frame.standard.text_small_mm),
                                () if item.richiamo is None else item.richiamo.segmenti,
                            )
                            for item in foglio.diametri
                        ],
                        area=area,
                        ostacoli=ostacoli,
                        linee_scritte=linee_scritte,
                    ),
                ],
            }
        )
    if altra_tavola is not None:
        spiegate.append((CAMPIONE_DEL_RIMANDO, altra_tavola))
    if scritte or calcolati or altra_tavola is not None:
        note = note_della_legenda(foglio, frame, spiegate)
        if note:
            foglio = foglio.model_copy(update={"note_della_legenda": note})
    # **Le tabelle nelle zone** (REL-012): fuori dall'area del disegno, quindi non
    # spostano niente; si posano per ultime.
    foglio = posa_le_tabelle(foglio, frame, tabelle)
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
        modello=modello,
        catalogo=catalogo,
    )
