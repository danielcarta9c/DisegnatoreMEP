"""Le sei tavole approvate con la tabella delle apparecchiature, e le misure di REL-006.

Per ciascuna tavola approvata — i cinque impianti di `DRAW-018` e l'impianto 6 di
`REL-003` —:

1. il grafo con i **dati di prova** del cartiglio (`docs/collaudi/REL-002/`) e con quelli
   della tabella (`dati-di-prova.json`, qui accanto), aggiunti alle proprieta' dei pezzi:
   il disegno non li legge;
2. `esegui_piano` sul **suo** piano: la tavola, in SVG e in DXF;
3. il PDF, con `scripts/to-pdf.sh` (il browser dell'ambiente);
4. le misure:
   - **la tabella**: le righe, come la tavola le scrive;
   - **il disegno non passa sulla tabella**: ogni simbolo, tratto di tubazione, sigla,
     richiamo e rimando contro il riquadro della tabella, e la distanza del piu' vicino;
   - **il disegno non si e' spostato**: simboli e tratte contro la geometria di `main`
     (`--prima <cartella>`, scritta da `geometria_di_main.py` su un albero di `main`);
   - **il DXF porta la tabella**, sul suo layer, uguale a quella dell'SVG: ogni linea e
     ogni testo riletti dal file;
   - **deterministico**: due esecuzioni danno lo stesso SVG e lo stesso DXF, byte per byte;
   - i rilievi del preflight e delle regole.

Esce anche la tavola 1 **senza dati di prova della tabella** (`tavola-1-senza-dati`): le
celle vuote, col trattino.

E' uno strumento di sessione: vuole ezdxf e il browser. Si lancia dalla radice:

    PYTHONPATH=src python3 docs/collaudi/REL-006/collaudo.py <cartella-di-lavoro> [--prima <cartella>]
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import ezdxf

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.dxf import ALTEZZA_MAIUSCOLE_EM, LAYER_TABELLA, write_dxf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.tabella import celle, tratti_della_tabella
from disegnatore_mep.layout.geometry import SheetGeometry
from disegnatore_mep.layout.labels import text_width_mm
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.validation.regole import rilievi_delle_regole

ROOT = Path(__file__).resolve().parents[3]
QUI = Path(__file__).resolve().parent
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
CARTIGLIO = json.loads(
    (ROOT / "docs" / "collaudi" / "REL-002" / "dati-di-prova.json").read_text("utf-8")
)
TABELLA = json.loads((QUI / "dati-di-prova.json").read_text("utf-8"))
MODELLO_DEL_CARTIGLIO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
USCITA = QUI / "tavole"

Box = tuple[float, float, float, float]


def tavole() -> list[tuple[str, str, Path, Path]]:
    elenco = [
        (f"tavola-{n}", n, APPROVATI / f"grafo-completo-{n}.json", APPROVATI / f"piano-completo-{n}.json")
        for n in ("1", "2", "3", "4", "5")
    ]
    elenco.append(("tavola-6", "6", IMPIANTO_6 / "grafo-completo-6.json", IMPIANTO_6 / "piano-6-a.json"))
    elenco.append(
        ("tavola-1-senza-dati", "1", APPROVATI / "grafo-completo-1.json", APPROVATI / "piano-completo-1.json")
    )
    return elenco


def con_i_dati(grafo: Path, impianto: str, con_la_tabella: bool) -> ProjectModel:
    documento = json.loads(grafo.read_text(encoding="utf-8"))
    cartiglio = (
        {**CARTIGLIO["tutti"], "sheet_number": "T6"}
        if impianto == "6"
        else {**CARTIGLIO["tutti"], **CARTIGLIO["impianti"][impianto]}
    )
    documento["metadata"].update(cartiglio)
    if con_la_tabella:
        dati = TABELLA["impianti"][impianto]
        pezzi = {item["id"]: item for item in documento["components"]}
        mancanti = sorted(set(dati) - set(pezzi))
        if mancanti:
            raise SystemExit(f"impianto {impianto}: i dati di prova nominano pezzi che non ci sono: {mancanti}")
        for identificativo, proprieta in dati.items():
            pezzi[identificativo]["properties"].update(proprieta)
    return ProjectModel.model_validate(documento)


def _dentro(box: Box, zona: Box) -> bool:
    return box[0] < zona[2] - 1e-6 and zona[0] < box[2] - 1e-6 and box[1] < zona[3] - 1e-6 and zona[1] < box[3] - 1e-6


def _distanza(box: Box, zona: Box) -> float:
    dx = max(zona[0] - box[2], box[0] - zona[2], 0.0)
    dy = max(zona[1] - box[3], box[1] - zona[3], 0.0)
    return (dx * dx + dy * dy) ** 0.5


def ingombri(foglio: SheetGeometry, corpo: float) -> list[tuple[str, Box]]:
    """Tutto quello che il disegno mette sul foglio, ciascuno col suo riquadro."""
    elenco: list[tuple[str, Box]] = [
        (f"simbolo {s.component_id}", (s.origin.x_mm, s.origin.y_mm, s.right_mm, s.bottom_mm))
        for s in foglio.symbols
    ]
    for route in foglio.routes:
        for segment in route.segments:
            for a, b in zip(segment, segment[1:], strict=False):
                elenco.append(
                    (
                        f"tratta {', '.join(route.connection_ids)}",
                        (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm)),
                    )
                )
    for label in foglio.labels:
        larghezza = text_width_mm(label.text, corpo)
        elenco.append(
            (f"sigla {label.text}", (label.anchor.x_mm, label.anchor.y_mm - corpo, label.anchor.x_mm + larghezza, label.anchor.y_mm))
        )
        if label.leader_from is not None:
            a, b = label.leader_from, label.anchor
            elenco.append(
                (f"richiamo di {label.text}", (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm)))
            )
    for ref in foglio.cross_references:
        elenco.append(
            (f"rimando {ref.text}", (ref.anchor.x_mm, ref.anchor.y_mm - corpo, ref.anchor.x_mm + text_width_mm(ref.text, corpo), ref.anchor.y_mm))
        )
    return elenco


def tabella_nel_dxf(dxf: Path, foglio: SheetGeometry, standard: object, altezza: float) -> str:
    """Le linee e i testi della tabella riletti dal DXF, contro quelli dell'SVG."""
    doc = ezdxf.readfile(dxf)
    entita = [item for item in doc.modelspace() if item.dxf.layer == LAYER_TABELLA]
    linee = sorted(
        (round(e.dxf.start.x, 6), round(e.dxf.start.y, 6), round(e.dxf.end.x, 6), round(e.dxf.end.y, 6))
        for e in entita
        if e.dxftype() == "LINE"
    )
    testi = sorted(
        (e.dxf.text, round(e.dxf.insert.x, 6), round(e.dxf.insert.y, 6), round(e.dxf.height, 4), e.dxf.style)
        for e in entita
        if e.dxftype() == "TEXT"
    )
    assert foglio.tabella is not None
    tratti = tratti_della_tabella(foglio.tabella, standard)  # type: ignore[arg-type]
    attese_linee = sorted(
        (round(x1, 6), round(altezza - y1, 6), round(x2, 6), round(altezza - y2, 6)) for x1, y1, x2, y2 in tratti.linee
    )
    attesi_testi = sorted(
        (
            t.testo,
            round(t.x_mm, 6),
            round(altezza - t.y_mm, 6),
            round(round(tratti.corpo_mm * ALTEZZA_MAIUSCOLE_EM, 4), 4),
            "NOVEC_ARIAL_GRASSETTO" if t.grassetto else "NOVEC_ARIAL",
        )
        for t in tratti.testi
    )
    altro = sorted({item.dxftype() for item in entita} - {"LINE", "TEXT"})
    esito = (
        f"linee {len(linee)}/{len(attese_linee)} {'uguali' if linee == attese_linee else 'DIVERSE'}, "
        f"testi {len(testi)}/{len(attesi_testi)} {'uguali' if testi == attesi_testi else 'DIVERSI'}"
    )
    return esito + (f", altre entita' {altro}" if altro else "")


def esegui(nome: str, impianto: str, grafo: Path, piano: Path, simboli: SymbolRegistry,
           catalogo: ComponentRegistry, cartiglio: Cartiglio, cartella: Path) -> tuple[ProjectModel, object, SheetGeometry, Path, Path]:
    modello = con_i_dati(grafo, impianto, not nome.endswith("senza-dati"))
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
    return modello, esito, foglio, svg, dxf


def impronta(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def main() -> None:
    lavoro = Path(sys.argv[1])
    prima = Path(sys.argv[sys.argv.index("--prima") + 1]) if "--prima" in sys.argv else None
    USCITA.mkdir(exist_ok=True)
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)
    cartiglio = Cartiglio.da_file(MODELLO_DEL_CARTIGLIO)
    for nome, impianto, grafo, piano in tavole():
        modello, esito, foglio, svg, dxf = esegui(nome, impianto, grafo, piano, simboli, catalogo, cartiglio, USCITA)
        _, _, _, svg2, dxf2 = esegui(nome, impianto, grafo, piano, simboli, catalogo, cartiglio, lavoro / "seconda")
        frame = esito.frame  # type: ignore[attr-defined]
        pdf = USCITA / f"{nome}.pdf"
        subprocess.run(["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(pdf)], check=True)
        print(f"\n== {nome} — {grafo.name}, formato {'A3' if frame.standard.sheet_width_mm == 420 else 'A2'}")
        tabella = foglio.tabella
        if tabella is None:
            print("   NESSUNA TABELLA")
            continue
        print(f"   tabella {tabella.larghezza_mm:g} x {tabella.altezza_mm:g} mm in ({tabella.x_mm:g}, {tabella.y_mm:g}), colonne {tabella.colonne_mm}")
        for riga in tabella.righe:
            print("   | " + " | ".join(celle(riga)))
        corpo = frame.standard.text_small_mm
        cose = ingombri(foglio, corpo)
        dentro = [nome_ for nome_, box in cose if _dentro(box, tabella.riquadro)]
        vicino = min(cose, key=lambda item: _distanza(item[1], tabella.riquadro))
        print(f"   nella tabella: {len(dentro)} {dentro if dentro else ''}— il piu' vicino: {vicino[0]} a {_distanza(vicino[1], tabella.riquadro):.1f} mm")
        if prima is not None and not nome.endswith("senza-dati"):
            vecchia = json.loads((prima / f"{nome}.json").read_text("utf-8"))["sheets"][0]
            simboli_prima = sorted((s["component_id"], s["origin"]["x_mm"], s["origin"]["y_mm"], s["rotation_deg"], s.get("specchiato", False)) for s in vecchia["symbols"])
            simboli_ora = sorted((s.component_id, s.origin.x_mm, s.origin.y_mm, s.rotation_deg, s.specchiato) for s in foglio.symbols)
            tratte_prima = sorted(json.dumps(r["segments"]) for r in vecchia["routes"])
            tratte_ora = sorted(json.dumps([[p.model_dump() for p in seg] for seg in r.segments]) for r in foglio.routes)
            sigle_prima = sorted((lbl["text"], lbl["anchor"]["x_mm"], lbl["anchor"]["y_mm"]) for lbl in vecchia["labels"])
            sigle_ora = sorted((lbl.text, lbl.anchor.x_mm, lbl.anchor.y_mm) for lbl in foglio.labels)
            nuove = sorted({t for t, _, _ in sigle_ora} - {t for t, _, _ in sigle_prima})
            spostate = sorted(t for t, x, y in sigle_prima if (t, x, y) not in set(sigle_ora))
            print(
                f"   rispetto a main: simboli {'fermi' if simboli_prima == simboli_ora else 'SPOSTATI'} ({len(simboli_ora)}), "
                f"tratte {'uguali' if tratte_prima == tratte_ora else 'DIVERSE'} ({len(tratte_ora)}), "
                f"sigle nuove {nuove}, sigle di main spostate o tolte {spostate}"
            )
        print(f"   DXF: {tabella_nel_dxf(dxf, foglio, frame.standard, frame.standard.sheet_height_mm)}")
        print(
            f"   deterministico: SVG {'uguale' if svg.read_bytes() == svg2.read_bytes() else 'DIVERSO'} ({impronta(svg)}), "
            f"DXF {'uguale' if dxf.read_bytes() == dxf2.read_bytes() else 'DIVERSO'} ({impronta(dxf)})"
        )
        rilievi = [f"{item.code} ({item.severity.value})" for item in esito.rilievi]  # type: ignore[attr-defined]
        regole = [item.code for item in rilievi_delle_regole(esito.disegno, frame, catalogo, modello)]  # type: ignore[attr-defined]
        print(f"   preflight: {rilievi or 'nessun rilievo'} · regole: {regole or 'nessuna violazione'}")
        svg.unlink()


if __name__ == "__main__":
    main()
