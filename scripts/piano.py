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


def orienta_raccordi(posati, modello, partizione, catalogo):
    """Gira ogni raccordo verso i vicini che ha davvero.

    **Per un raccordo a T la posa decide quale attacco fisico serve quale porta
    del modello** (`PlacedSymbol.port_map`): il T si disegna come un punto e i
    suoi tre attacchi sono uguali, quindi «la porta di prosecuzione» puo' stare
    sull'attacco perpendicolare perche' il percorso principale giri dentro il
    raccordo invece che in un gomito a parte (D-004, I-027).

    Quella mappa e' **una proprieta' della posa**, non del grafo. Chi sposta i
    pezzi senza rifarla lascia i T girati verso dove stavano prima: il ritorno
    che arriva da destra pretende di entrare dall'attacco di sinistra, e non si
    instrada nessuna linea.

    Qui la si ricava dal fatto piu' semplice che esista: **ogni porta guarda il
    proprio vicino.** Per ciascuna porta del modello si sa dove sta il pezzo
    dall'altro capo; fra gli attacchi liberi del simbolo si prende quello la cui
    faccia punta di piu' da quella parte. Nessun peso, nessuna ricerca: un
    prodotto scalare e un'assegnazione avida in ordine di preferenza.
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

    fuori = []
    for item in posati:
        porte = vicini.get(item.component_id, {})
        definizione = catalogo.resolve(definizioni[item.component_id]).definition
        if not definizione.is_a_fitting or len(porte) < 2:
            fuori.append(item)
            continue
        manifesto = catalogo.resolve(
            definizioni[item.component_id]
        ).symbol.manifest.rotated(item.rotation_deg)
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
                punteggio = faccia[0] * verso[0] + faccia[1] * verso[1]
                preferenze.append((-punteggio, porta, attacco.id))
        preferenze.sort()

        mappa: dict[str, str] = {}
        presi: set[str] = set()
        for _, porta, attacco in preferenze:
            if porta in mappa or attacco in presi:
                continue
            mappa[porta] = attacco
            presi.add(attacco)
        # Le porte del modello che nessun tronco usa tengono il proprio
        # attacco omonimo, se e' rimasto libero.
        for attacco in manifesto.ports:
            if attacco.id not in presi and attacco.id not in mappa:
                mappa.setdefault(attacco.id, attacco.id)
        fuori.append(item.model_copy(update={"port_map": mappa}))
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
    seminata = orienta_raccordi(seminata, modello, partizione, catalogo)

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
