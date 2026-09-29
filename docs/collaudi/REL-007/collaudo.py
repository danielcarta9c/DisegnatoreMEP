"""Le sei tavole approvate con i diametri, la variante retrofit, e le misure di REL-007.

Per ciascuna tavola approvata — i cinque impianti di `DRAW-018` e l'impianto 6 di
`REL-003` — e per la **variante retrofit** dell'impianto 1 (diametri sul solo
primario, distribuzione esistente, I-145):

1. il grafo con i dati di prova del cartiglio (`docs/collaudi/REL-002/`), della
   tabella (`docs/collaudi/REL-006/`) e dei diametri (`dati-di-prova.json`, qui
   accanto): la richiesta dei diametri, le reti esistenti, i salti termici, le
   portate di progetto;
2. `esegui_piano` sul **suo** piano: la tavola in SVG e in DXF, e il PDF con
   `scripts/to-pdf.sh`;
3. le misure:
   - **le etichette**: quante, e quali;
   - **un'etichetta per tratto**: ogni tratto che porta il DN ne ha una, e una sola;
     nessuna etichetta nomina un tratto che non lo porta;
   - **non toccano niente**: il riquadro di ogni etichetta contro simboli, sigle,
     altre etichette, tabella e le altre linee, con la distanza della cosa piu'
     vicina; e dalla propria linea sta allo stacco dichiarato;
   - **il disegno non si muove**: simboli, tratte e sigle uguali a quelli della
     stessa tavola senza la richiesta dei diametri;
   - **il DXF porta le stesse etichette**, sul loro layer: testo, punto e rotazione
     riletti dal file;
   - **deterministico**: due esecuzioni danno lo stesso SVG e lo stesso DXF;
   - i rilievi del preflight e delle regole;
4. il **foglio dei calcoli** di ogni tavola, in `foglio-dei-calcoli.md`.

E' uno strumento di sessione: vuole ezdxf e il browser. Si lancia dalla radice:

    PYTHONPATH=src python3 docs/collaudi/REL-007/collaudo.py <cartella-di-lavoro>
"""

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import ezdxf

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.foglio import foglio_in_markdown, righe_del_calcolo
from disegnatore_mep.diametri.tratti import tratti_da_etichettare, tratti_del_diametro
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.cartiglio import Cartiglio, CartiglioDellaTavola, valori_del_cartiglio
from disegnatore_mep.graphics.dxf import LAYER_DIAMETRI, write_dxf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.layout.diametri import STACCO_DALLA_LINEA_MM, riquadro_del_diametro
from disegnatore_mep.layout.geometry import SheetGeometry, zona_della_tabella
from disegnatore_mep.layout.labels import text_width_mm
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.validation.regole import rilievi_delle_regole

ROOT = Path(__file__).resolve().parents[3]
QUI = Path(__file__).resolve().parent
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
CARTIGLIO = json.loads((ROOT / "docs" / "collaudi" / "REL-002" / "dati-di-prova.json").read_text("utf-8"))
TABELLA = json.loads((ROOT / "docs" / "collaudi" / "REL-006" / "dati-di-prova.json").read_text("utf-8"))
DIAMETRI = json.loads((QUI / "dati-di-prova.json").read_text("utf-8"))
MODELLO_DEL_CARTIGLIO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
USCITA = QUI / "tavole"

Box = tuple[float, float, float, float]


def tavole() -> list[tuple[str, str, Path, Path, dict]]:  # type: ignore[type-arg]
    elenco = [
        (
            f"tavola-{n}", n, APPROVATI / f"grafo-completo-{n}.json",
            APPROVATI / f"piano-completo-{n}.json", DIAMETRI["impianti"][n],
        )
        for n in ("1", "2", "3", "4", "5")
    ]
    elenco.append(
        ("tavola-6", "6", IMPIANTO_6 / "grafo-completo-6.json", IMPIANTO_6 / "piano-6-a.json",
         DIAMETRI["impianti"]["6"])
    )
    for nome, variante in DIAMETRI["varianti"].items():
        n = variante["impianto"]
        elenco.append(
            (f"tavola-{nome}", n, APPROVATI / f"grafo-completo-{n}.json",
             APPROVATI / f"piano-completo-{n}.json", variante)
        )
    return elenco


def con_i_dati(
    grafo: Path, impianto: str, diametri: dict | None, con_la_richiesta: bool = True  # type: ignore[type-arg]
) -> ProjectModel:
    documento = json.loads(grafo.read_text(encoding="utf-8"))
    cartiglio = (
        {**CARTIGLIO["tutti"], "sheet_number": "T6"}
        if impianto == "6"
        else {**CARTIGLIO["tutti"], **CARTIGLIO["impianti"][impianto]}
    )
    documento["metadata"].update(cartiglio)
    pezzi = {item["id"]: item for item in documento["components"]}
    for identificativo, proprieta in TABELLA["impianti"][impianto].items():
        pezzi[identificativo]["properties"].update(proprieta)
    if diametri is not None:
        mancanti = sorted(set(diametri["pezzi"]) - set(pezzi))
        if mancanti:
            raise SystemExit(f"impianto {impianto}: i dati di prova nominano pezzi che non ci sono: {mancanti}")
        for identificativo, proprieta in diametri["pezzi"].items():
            pezzi[identificativo]["properties"].update(proprieta)
        reti = [item["id"] for item in documento["networks"]]
        esistenti = set(diametri.get("esistenti", []))
        for rete in documento["networks"]:
            if rete["id"] in esistenti:
                rete["esistente"] = True
        chieste = reti if diametri["reti"] == "tutte" else diametri["reti"]
        if con_la_richiesta:
            documento["diametri"] = {"reti": [rete for rete in chieste if rete not in esistenti]}
    return ProjectModel.model_validate(documento)


def esegui(nome: str, modello: ProjectModel, piano: Path, simboli: SymbolRegistry,
           catalogo: ComponentRegistry, cartiglio: Cartiglio, cartella: Path):  # type: ignore[no-untyped-def]
    esito = esegui_piano(modello, carica_piano(piano), catalogo, simboli, ROOT / "naming")
    if esito.disegno is None:
        raise SystemExit(f"{nome}: il piano non si esegue: {esito.errore}")
    (foglio,) = esito.disegno.sheets
    tavola = CartiglioDellaTavola(cartiglio=cartiglio, valori=valori_del_cartiglio(modello, foglio.sheet_id))
    cartella.mkdir(parents=True, exist_ok=True)
    svg = cartella / f"{nome}.svg"
    svg.write_text(render_sheet(foglio, esito.frame, simboli, tavola), encoding="utf-8")
    dxf = cartella / f"{nome}.dxf"
    write_dxf(foglio, esito.frame, simboli, dxf, tavola)
    return esito, foglio, svg, dxf


def _sovrapposti(a: Box, b: Box) -> bool:
    return a[0] < b[2] - 1e-6 and b[0] < a[2] - 1e-6 and a[1] < b[3] - 1e-6 and b[1] < a[3] - 1e-6


def _distanza(a: Box, b: Box) -> float:
    dx = max(b[0] - a[2], a[0] - b[2], 0.0)
    dy = max(b[1] - a[3], a[1] - b[3], 0.0)
    return math.hypot(dx, dy)


def ostacoli(foglio: SheetGeometry, corpo: float) -> list[tuple[str, frozenset[str], Box]]:
    """Tutto cio' che un'etichetta del DN non deve toccare, ciascuno con le
    connessioni della tratta a cui appartiene (vuote per chi non e' una linea)."""
    elenco: list[tuple[str, frozenset[str], Box]] = [
        (f"simbolo {s.component_id}", frozenset(), (s.origin.x_mm, s.origin.y_mm, s.right_mm, s.bottom_mm))
        for s in foglio.symbols
    ]
    for route in foglio.routes:
        for segment in route.segments:
            for a, b in zip(segment, segment[1:], strict=False):
                elenco.append(
                    (f"linea {route.connection_ids[0] if route.connection_ids else '?'}",
                     frozenset(route.connection_ids),
                     (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm)))
                )
    for label in foglio.labels:
        larghezza = text_width_mm(label.text, corpo)
        elenco.append(
            (f"sigla {label.text}", frozenset(),
             (label.anchor.x_mm, label.anchor.y_mm - corpo, label.anchor.x_mm + larghezza, label.anchor.y_mm))
        )
    if foglio.tabella is not None:
        elenco.append(("tabella", frozenset(), zona_della_tabella(foglio.tabella.riquadro, 0.0)))
    return elenco


def diametri_nel_dxf(dxf: Path, foglio: SheetGeometry, altezza: float) -> str:
    doc = ezdxf.readfile(dxf)
    testi = sorted(
        (e.dxf.text, round(e.dxf.insert.x, 6), round(e.dxf.insert.y, 6), round(e.dxf.rotation, 6))
        for e in doc.modelspace()
        if e.dxf.layer == LAYER_DIAMETRI and e.dxftype() == "TEXT"
    )
    attesi = sorted(
        (e.testo, round(e.ancora.x_mm, 6), round(altezza - e.ancora.y_mm, 6), 90.0 if e.verticale else 0.0)
        for e in foglio.diametri
    )
    altro = sorted(
        {e.dxftype() for e in doc.modelspace() if e.dxf.layer == LAYER_DIAMETRI} - {"TEXT"}
    )
    esito = f"{len(testi)}/{len(attesi)} {'uguali' if testi == attesi else 'DIVERSI'}"
    return esito + (f", altre entita' {altro}" if altro else "")


def impronta(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    lavoro = Path(sys.argv[1])
    USCITA.mkdir(exist_ok=True)
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)
    cartiglio = Cartiglio.da_file(MODELLO_DEL_CARTIGLIO)
    naming = Naming.from_directory(ROOT / "naming")
    fogli_dei_calcoli: list[str] = []
    for nome, impianto, grafo, piano, dati in tavole():
        modello = con_i_dati(grafo, impianto, dati)
        esito, foglio, svg, dxf = esegui(nome, modello, piano, simboli, catalogo, cartiglio, USCITA)
        _, _, svg2, dxf2 = esegui(nome, modello, piano, simboli, catalogo, cartiglio, lavoro / "seconda")
        # **Gli stessi dati, senza la richiesta dei diametri**: cosi' l'unica
        # differenza e' il DN. Le portate di progetto delle utenze e le potenze
        # delle zone si scrivono accanto ai pezzi comunque (D-052), e non sono di
        # REL-007.
        senza = con_i_dati(grafo, impianto, dati, con_la_richiesta=False)
        _, foglio_senza, _, _ = esegui(nome, senza, piano, simboli, catalogo, cartiglio, lavoro / "senza")
        frame = esito.frame
        pdf = USCITA / f"{nome}.pdf"
        subprocess.run(["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(pdf)], check=True)
        formato = {420.0: "A3", 594.0: "A2", 841.0: "A1"}[frame.standard.sheet_width_mm]
        print(f"\n== {nome} — {grafo.name}, formato {formato}")
        corpo = frame.standard.text_small_mm

        # Le etichette, e un'etichetta per tratto.
        tratti = tratti_da_etichettare(modello, catalogo)
        per_tratto = {t.connection_ids: 0 for t in tratti}
        estranee = 0
        for etichetta in foglio.diametri:
            chiave = frozenset(etichetta.connection_ids)
            if chiave in per_tratto:
                per_tratto[chiave] += 1
            else:
                estranee += 1
        senza_etichetta = sum(1 for quante in per_tratto.values() if quante == 0)
        doppie = sum(1 for quante in per_tratto.values() if quante > 1)
        scritte = sorted({e.testo for e in foglio.diametri}, key=lambda t: int(t.split()[-1]))
        verticali = sum(1 for e in foglio.diametri if e.verticale)
        print(
            f"   etichette {len(foglio.diametri)} ({verticali} verticali) {scritte} · tratti col DN "
            f"{len(tratti)}: senza etichetta {senza_etichetta}, con piu' di una {doppie}, "
            f"etichette su un tratto che non lo porta {estranee}"
        )
        tutti = tratti_del_diametro(modello, catalogo)
        print(
            f"   tratti d'acqua {len(tutti)}: col DN {len(tratti)}, senza DN "
            f"{len(tutti) - len(tratti)} {sorted({t.perche_senza_dn for t in tutti if not t.porta_il_dn and t.perche_senza_dn})}"
        )

        # Non toccano niente.
        cose = ostacoli(foglio, corpo)
        altre_etichette = [(riquadro_del_diametro(e, corpo), e) for e in foglio.diametri]
        toccate = []
        piu_vicina = (math.inf, "")
        stacchi = []
        for box, etichetta in altre_etichette:
            proprie = frozenset(etichetta.connection_ids)
            for nome_cosa, connessioni, riquadro in cose:
                if connessioni and connessioni <= proprie:
                    continue
                if _sovrapposti(box, riquadro):
                    toccate.append(f"{etichetta.testo} su {nome_cosa}")
                d = _distanza(box, riquadro)
                if d < piu_vicina[0]:
                    piu_vicina = (d, f"{etichetta.testo} da {nome_cosa}")
            for altro_box, altra in altre_etichette:
                if altra is not etichetta and _sovrapposti(box, altro_box):
                    toccate.append(f"{etichetta.testo} su {altra.testo}")
            proprie_linee = [
                riquadro for _, connessioni, riquadro in cose if connessioni and connessioni <= proprie
            ]
            stacchi.append(min(_distanza(box, riquadro) for riquadro in proprie_linee))
        print(
            f"   toccano qualcosa: {len(toccate)} {toccate if toccate else ''}— la cosa piu' vicina: "
            f"{piu_vicina[1]} a {piu_vicina[0]:.2f} mm · dalla propria linea: "
            f"{min(stacchi):.2f}–{max(stacchi):.2f} mm (stacco dichiarato {STACCO_DALLA_LINEA_MM:g})"
        )

        # Il disegno non si muove.
        uguali = {
            "simboli": [s.model_dump() for s in foglio.symbols] == [s.model_dump() for s in foglio_senza.symbols],
            "tratte": [r.model_dump() for r in foglio.routes] == [r.model_dump() for r in foglio_senza.routes],
            "sigle": [x.model_dump() for x in foglio.labels] == [x.model_dump() for x in foglio_senza.labels],
            "tabella": foglio.tabella == foglio_senza.tabella,
            "legenda": foglio.legend == foglio_senza.legend and foglio.network_keys == foglio_senza.network_keys,
        }
        print(
            "   rispetto alla tavola senza diametri: "
            + ", ".join(f"{k} {'uguali' if v else 'DIVERSI'}" for k, v in uguali.items())
            + f" · riga della legenda: {'si' if foglio.note_della_legenda else 'no'}"
            + (f" ({' / '.join(foglio.note_della_legenda[0].righe)})" if foglio.note_della_legenda else "")
        )
        print(f"   DXF: etichette sul layer {LAYER_DIAMETRI} {diametri_nel_dxf(dxf, foglio, frame.standard.sheet_height_mm)}")
        print(
            f"   deterministico: SVG {'uguale' if svg.read_bytes() == svg2.read_bytes() else 'DIVERSO'} ({impronta(svg)}), "
            f"DXF {'uguale' if dxf.read_bytes() == dxf2.read_bytes() else 'DIVERSO'} ({impronta(dxf)})"
        )
        rilievi = [f"{item.code} ({item.severity.value})" for item in esito.rilievi]
        regole = [item.code for item in rilievi_delle_regole(esito.disegno, frame, catalogo, modello)]
        print(f"   preflight: {rilievi or 'nessun rilievo'} · regole: {regole or 'nessuna violazione'}")
        svg.unlink()

        sigle = read_plant(modello, catalogo, naming).sigle
        righe = righe_del_calcolo(modello, catalogo, sigle)
        titolo = modello.metadata.project_name
        fogli_dei_calcoli.append(f"## {nome} — {titolo}\n\n{foglio_in_markdown(righe)}")

    (QUI / "foglio-dei-calcoli.md").write_text(
        "# Il foglio dei calcoli delle tavole di REL-007\n\n"
        "Scritto da `collaudo.py` con `diametri.foglio`: una riga per tratto d'acqua. **I dati "
        "sono di prova, e inventati** (`dati-di-prova.json`, e la tabella di `REL-006`). Le basi "
        "del calcolo sono **D-193**: DN come diametro interno netto, velocità massima per "
        "diametro (tab. 9 del Quaderno Caleffi n. 5), acqua a 4,18 kJ/(kg·K) e 1000 kg/m³.\n\n"
        + "\n".join(fogli_dei_calcoli),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
