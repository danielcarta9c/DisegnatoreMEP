"""Esegue un **piano di composizione** scritto a mano, invece di cercarlo.

È la prova dell'approccio nuovo (PO, 19 settembre 2026): il disegno non lo
trova un solutore che minimizza una somma pesata, lo **compone** chi sa come si
fa un disegno — e il motore deterministico esegue quel piano e lo controlla.

Qui chi compone è l'agente, a mano, in sessione. Il piano è un file JSON che
dice **soltanto dove stanno i pezzi grossi**:

    {
      "passo_mm": 2.5,
      "pezzi": {
        "pdc-master": {"x": 35, "y": 120},
        "pdc-slave":  {"x": 35, "y": 75}
      }
    }

Tutto il resto lo fa il motore che già esiste, e sono le parti che la ricerca
del 4 agosto §3 dichiara sane: gli accessori appesi seguono il proprio pezzo,
l'instradamento è ortogonale e in griglia, le linee si interrompono sotto i
simboli, i validatori misurano, il rendering è quello.

**Che cosa NON gira**: `lay_the_spine` e `improve_sheet`, cioè la fase del
tronco e il ciclo di miglioramento — le due che cercano invece di comporre. Se
la tavola esce bene senza di loro, l'approccio è dimostrato.

    scripts/piano.py <progetto-completo.json> <piano.json> <cartella-uscita>
"""

from __future__ import annotations

import json
import pathlib
import sys

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.addresses import with_addresses
from disegnatore_mep.layout.compose import (
    centre_vertically,
    inline_component_ids,
)
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import DrawingGeometry, Point, SheetGeometry
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import settle_sheet
from disegnatore_mep.layout.labels import place_labels
from disegnatore_mep.layout.legend import build_legend
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import SpineLayout, carry_the_rest
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.validation.preflight import preflight_drawing

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _frame(nome: str) -> SheetFrame:
    larghezze = {"A4": 297.0, "A3": 420.0, "A2": 594.0, "A1": 841.0}
    voluta = larghezze[nome]
    for item in ORDINARY_FRAMES:
        if abs(item.standard.sheet_width_mm - voluta) < 1e-6:
            return item
    raise SystemExit(f"formato {nome} sconosciuto")


_VERSO: dict[PortFace, tuple[float, float]] = {
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
    PortFace.BOTTOM: (0.0, 1.0),
}


def orienta(posati, modello, partizione, catalogo, fissate):
    """Ogni pezzo si **gira verso i vicini che ha davvero**.

    Il piano dice **dove** sta un pezzo. Da che parte guarda non glielo deve
    dire: si deduce, e deve dedursi, perche' e' una conseguenza della posa e non
    una scelta di chi compone.

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
    prodotto scalare e un'assegnazione avida.

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

    def centro(item) -> tuple[float, float]:
        return (
            item.origin.x_mm + item.width_mm / 2,
            item.origin.y_mm + item.height_mm / 2,
        )

    def accoppia(manifesto, item, porte):
        """Il punteggio della rotazione, e la mappa che ne esce."""
        mio_centro = centro(item)
        preferenze = []
        for porta, altro in sorted(porte.items()):
            if altro not in dove:
                continue
            suo = centro(dove[altro])
            verso = (suo[0] - mio_centro[0], suo[1] - mio_centro[1])
            norma = max(abs(verso[0]) + abs(verso[1]), 1e-9)
            verso = (verso[0] / norma, verso[1] / norma)
            for attacco in manifesto.ports:
                faccia = _VERSO[attacco.face]
                preferenze.append(
                    (-(faccia[0] * verso[0] + faccia[1] * verso[1]), porta, attacco.id)
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
        for attacco in manifesto.ports:
            if attacco.id not in presi and attacco.id not in mappa:
                mappa.setdefault(attacco.id, attacco.id)
        return punteggio, mappa

    fuori = []
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
        # **La mappa delle porte si rifà soltanto per i raccordi.** Un T si
        # disegna come un punto e ha tre attacchi **uguali**: quale porta del
        # modello stia su quale attacco e' una scelta della posa (D-004,
        # I-027). Su una macchina no: `primary_out` e `cold_in` di un accumulo
        # sono due bocchettoni **fisici diversi del serbatoio**, e scambiarli
        # non e' un ritocco grafico, e' un altro impianto.
        #
        # **Misurato il 20 settembre.** Rimappando anche le macchine, l'acqua
        # fredda dell'impianto 1 finiva sulla porta a quota 211 — che e'
        # `primary_out` — invece che su `cold_in` a 228,5: il ritorno e
        # l'ingresso sanitario arrivavano allo stesso punto, e il PO l'ha visto
        # guardando la tavola. Era un errore di **contenuto** prodotto da una
        # deduzione grafica.
        raccordo = risolto.definition.is_a_fitting
        rotazioni = (
            sorted(base.allowed_rotations_deg)
            if (raccordo or len(porte) < 2) and item.component_id not in fissate
            else [item.rotation_deg]
        )
        scelta = None
        for gradi in rotazioni:
            manifesto = base.rotated(gradi)
            provvisorio = item.model_copy(
                update={
                    "rotation_deg": gradi,
                    "width_mm": manifesto.width_mm,
                    "height_mm": manifesto.height_mm,
                }
            )
            punteggio, mappa = accoppia(manifesto, provvisorio, porte)
            if scelta is None or punteggio > scelta[0] + 1e-9:
                scelta = (punteggio, provvisorio, mappa)
        assert scelta is not None
        fuori.append(
            scelta[1].model_copy(update={"port_map": scelta[2]})
            if raccordo
            else scelta[1]
        )
    return fuori


def main() -> int:
    progetto = pathlib.Path(sys.argv[1])
    piano = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    uscita = pathlib.Path(sys.argv[3])
    uscita.mkdir(parents=True, exist_ok=True)

    simboli = SymbolRegistry.from_directory(ROOT / "assets/symbols")
    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples/layout/catalog", symbols=simboli
    )
    naming = Naming.from_directory(ROOT / "naming")
    modello = load_project(progetto)
    frame = _frame(piano.get("formato", "A3"))
    area = frame.drawing_rect_mm
    grid = GridSpace(origin=area, standard=frame.standard)

    inline = inline_component_ids(modello, catalogo)
    partizione = partition_project(modello, build_trunks(modello, inline))[0]

    # 1. La posa di partenza serve solo come **inventario**: da lei si prendono
    #    i simboli, le rotazioni e la mappa delle porte di ogni pezzo. Le
    #    coordinate che calcola le sovrascrive il piano.
    partenza = place_sheet(modello, partizione, catalogo, frame, inline)
    per_id = {item.component_id: item for item in partenza}

    ignoti = sorted(set(piano["pezzi"]) - set(per_id))
    if ignoti:
        raise SystemExit(f"il piano nomina pezzi che non esistono: {', '.join(ignoti)}")

    def in_griglia(valore: float, base: float) -> float:
        passo = frame.standard.grid_mm
        return base + round((valore - base) / passo) * passo

    posati = []
    for component_id, dove in piano["pezzi"].items():
        item = per_id[component_id]
        aggiornamenti: dict[str, object] = {
            "origin": Point(
                x_mm=in_griglia(float(dove["x"]), area.x_mm),
                y_mm=in_griglia(float(dove["y"]), area.y_mm),
            )
        }
        if "rotazione" in dove:
            aggiornamenti["rotation_deg"] = int(dove["rotazione"])
        posati.append(item.model_copy(update=aggiornamenti))

    # 2. Chi non è nel piano **segue il proprio pezzo**: è la stessa meccanica
    #    con cui la fase del tronco trascinava il resto dell'impianto, e qui
    #    la si usa tale e quale — solo che i partecipanti li ho scelti io.
    finta_fase = SpineLayout(
        machines=frozenset(piano["pezzi"]),
        participants=tuple(piano["pezzi"]),
        trunks=(),
        symbols=tuple(posati),
        routes=(),
        runs=(),
        routed=True,
    )
    seminata = carry_the_rest(modello, partizione, catalogo, partenza, finta_fase, frame)
    fissate = frozenset(
        component_id
        for component_id, dove in piano["pezzi"].items()
        if "rotazione" in dove
    )
    prima_di_girare = {item.component_id: item.rotation_deg for item in seminata}
    seminata = orienta(seminata, modello, partizione, catalogo, fissate)
    girati = [
        f"{item.component_id} {prima_di_girare[item.component_id]}->{item.rotation_deg}"
        for item in seminata
        if prima_di_girare[item.component_id] != item.rotation_deg
    ]
    if girati:
        print("girati dalla deduzione: " + ", ".join(girati) + "\n")

    # 3. Da qui in avanti è il motore di sempre: instradamento, accessori in
    #    linea, legenda, centratura, testi. **Nessuna ricerca.**
    try:
        sistemata = settle_sheet(
            modello, list(partizione.trunks), seminata, catalogo, grid
        )
    except LayoutError as errore:
        print(f"il piano non si instrada: {errore}\n")
        # **La diagnostica utile e' dove sono finiti i pezzi**, non il
        # messaggio: chi compone deve poter vedere che cosa ha lasciato in
        # mezzo, e correggere il piano invece di indovinare.
        print("posa applicata (i pezzi del piano sono marcati con *):")
        for item in sorted(seminata, key=lambda i: (i.origin.x_mm, i.origin.y_mm)):
            segno = "*" if item.component_id in piano["pezzi"] else " "
            print(
                f"  {segno} {item.component_id:46} "
                f"{item.width_mm:5.1f}x{item.height_mm:5.1f} "
                f"@({item.origin.x_mm:6.1f},{item.origin.y_mm:6.1f})"
            )
        return 1

    voci, chiavi = build_legend(
        modello, sistemata.symbols, partizione.network_ids, catalogo, frame
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
    disegno = with_addresses(disegno, modello, catalogo, frame, ROOT / "naming")

    rilievi = preflight_drawing(disegno, frame, catalogo)
    bloccanti = [item for item in rilievi if item.severity.value == "blocking"]
    for item in rilievi:
        print(f"  [{item.severity.value:8}] {item.code}: {item.message[:150]}")

    nome = progetto.name.replace("-completo.json", "")
    (uscita / f"{nome}-t1.svg").write_text(
        render_sheet(disegno.sheets[0], frame, simboli), encoding="utf-8"
    )
    (uscita / f"{nome}-geometria.json").write_text(
        disegno.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    print(f"\ntavola scritta: {uscita / (nome + '-t1.svg')}")
    print(f"rilievi: {len(rilievi)} di cui {len(bloccanti)} bloccanti")
    _ = naming
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
