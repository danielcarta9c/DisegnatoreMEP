"""I DXF delle sei tavole approvate, e le misure che se ne possono prendere senza AutoCAD.

Per ciascuna tavola approvata — i cinque impianti di `DRAW-018`, col cartiglio compilato
coi dati di prova di `REL-002` (I-132), e l'impianto 6 di `REL-003` (I-136) —:

1. il grafo con i **dati di prova** del cartiglio aggiunti ai metadati, come in
   `docs/collaudi/REL-002/collaudo.py`: il disegno non li legge;
2. `write_dxf`: il DXF, e il logo accanto;
3. **l'audit di ezdxf**, che dice se il file e' strutturato come AutoCAD lo vuole;
4. **la geometria riletta dal DXF** contro quella della tavola: ogni tratta di ogni
   rete, sul suo layer, e ogni simbolo, come inserimento del suo blocco, allo stesso
   punto entro un milionesimo di millimetro;
5. **la resa** della presentazione a foglio intero, 1:1, con il modulo `drawing` di
   ezdxf: il PDF nella cartella di lavoro, un'immagine a 100 dpi in `rese/`, da
   guardare accanto alla tavola approvata. I testi non sono quelli di AutoCAD — qui
   non c'e' Arial —, la geometria si'.

E' uno strumento di sessione: vuole ezdxf e PyMuPDF. Si lancia dalla radice:

    PYTHONPATH=src python3 docs/collaudi/REL-004/collaudo.py <cartella-di-lavoro>

I DXF escono in `docs/collaudi/REL-004/dxf/`, le immagini delle rese in
`docs/collaudi/REL-004/rese/`.
"""

import json
import sys
from pathlib import Path

import ezdxf
import pymupdf as mupdf
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
from ezdxf.math import BoundingBox2d

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.dxf import (
    inserimento_del_simbolo,
    layer_della_rete,
    nome_del_blocco,
    write_dxf,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import _interrupted, sheet_marks
from disegnatore_mep.layout.geometry import SheetGeometry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[3]
QUI = Path(__file__).resolve().parent
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
DATI = json.loads((ROOT / "docs" / "collaudi" / "REL-002" / "dati-di-prova.json").read_text("utf-8"))
MODELLO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
USCITA = QUI / "dxf"
RESE = QUI / "rese"
FORMATI = {"A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}


def tavole() -> list[tuple[str, Path, Path, dict[str, str]]]:
    elenco = [
        (
            f"tavola-{n}",
            APPROVATI / f"grafo-completo-{n}.json",
            APPROVATI / f"piano-completo-{n}.json",
            {**DATI["tutti"], **DATI["impianti"][n]},
        )
        for n in ("1", "2", "3", "4", "5")
    ]
    elenco.append(
        (
            "tavola-6",
            IMPIANTO_6 / "grafo-completo-6.json",
            IMPIANTO_6 / "piano-6-a.json",
            {**DATI["tutti"], "sheet_number": "T6"},
        )
    )
    return elenco


def misura(foglio: SheetGeometry, altezza: float, doc: "ezdxf.document.Drawing",
           simboli: SymbolRegistry) -> str:
    """La geometria riletta dal DXF contro quella della tavola, come le prove di
    `tests/graphics/test_dxf.py` fanno sull'impianto 6: qui sulle sei tavole."""
    reti = {layer_della_rete(r.medium, r.supply) for r in foglio.routes}
    scritte = sorted(
        (p.dxf.layer, tuple((round(x, 6), round(y, 6)) for x, y in p.get_points("xy")))
        for p in doc.modelspace().query("LWPOLYLINE")
        if p.dxf.layer in reti
    )
    marks = sheet_marks(foglio)
    attese = sorted(
        (
            layer_della_rete(route.medium, route.supply),
            tuple((round(q.x_mm, 6), round(altezza - q.y_mm, 6)) for q in piece),
        )
        for indice, route in enumerate(foglio.routes)
        for segment in route.segments
        for piece in _interrupted(segment, [m.at for m in marks.hops if m.route_index == indice])
    )
    inseriti = sorted(
        (i.dxf.name, round(i.dxf.insert.x, 6), round(i.dxf.insert.y, 6),
         round(i.dxf.rotation % 360, 6), i.dxf.xscale < 0)
        for i in doc.modelspace().query("INSERT")
        if i.dxf.layer == "M-DIAG-EQPM" and not i.dxf.name.endswith("_Lettera")
        and i.dxf.name.startswith("NoveC_") and i.dxf.name != "NoveC_FlowArrow"
    )
    posati = []
    for placed in foglio.symbols:
        manifest = simboli.get(placed.symbol_id).manifest
        dove = inserimento_del_simbolo(
            placed.origin, placed.rotation_deg, placed.specchiato,
            manifest.width_mm, manifest.height_mm, altezza,
        )
        posati.append((nome_del_blocco(placed.symbol_id), round(dove.x, 6), round(dove.y, 6),
                       round(dove.rotazione % 360, 6), dove.specchiato))
    tratte = "uguali" if scritte == attese else "DIVERSE"
    posa = "uguali" if inseriti == sorted(posati) else "DIVERSI"
    return (f"tratte {len(scritte)}/{len(attese)} {tratte}, "
            f"simboli {len(inseriti)}/{len(posati)} {posa}")


def rendi(dxf: Path, pdf: Path, png: Path) -> str:
    """La presentazione del DXF a foglio intero, 1:1. Un backend per uscita:
    riusarlo cambia la scala (misurato con ezdxf 1.4.4)."""
    doc = ezdxf.readfile(dxf)
    nome = next(item for item in doc.layouts.names() if item != "Model")
    carta = doc.paperspace(nome)
    larghezza, altezza = FORMATI[nome]
    contesto = RenderContext(doc)
    contesto.set_current_layout(carta)
    backend = pymupdf.PyMuPdfBackend()
    Frontend(contesto, backend).draw_layout(carta, finalize=True)
    pdf.write_bytes(
        backend.get_pdf_bytes(
            layout.Page(larghezza, altezza, layout.Units.mm, margins=layout.Margins.all(0)),
            settings=layout.Settings(scale=1),
            render_box=BoundingBox2d([(0, 0), (larghezza, altezza)]),
        )
    )
    mupdf.open(pdf)[0].get_pixmap(dpi=100).save(png)
    return nome


def main() -> None:
    lavoro = Path(sys.argv[1])
    lavoro.mkdir(parents=True, exist_ok=True)
    USCITA.mkdir(exist_ok=True)
    RESE.mkdir(exist_ok=True)
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)
    cartiglio = Cartiglio.da_file(MODELLO)
    print(f"{'tavola':10s} {'formato':7s} {'audit':14s} {'entita':>7s} {'blocchi':>7s} {'layer':>5s}  "
          "geometria")
    for nome, grafo, piano, dati in tavole():
        documento = json.loads(grafo.read_text(encoding="utf-8"))
        documento["metadata"].update(dati)
        modello = ProjectModel.model_validate(documento)
        esito = esegui_piano(modello, carica_piano(piano), catalogo, simboli, ROOT / "naming")
        if esito.disegno is None:
            raise SystemExit(f"{nome}: il piano non si esegue: {esito.errore}")
        (foglio,) = esito.disegno.sheets
        tavola = CartiglioDellaTavola(
            cartiglio=cartiglio, valori=valori_del_cartiglio(modello, foglio.sheet_id)
        )
        dxf = USCITA / f"{nome}.dxf"
        write_dxf(foglio, esito.frame, simboli, dxf, tavola)
        doc = ezdxf.readfile(dxf)
        auditor = doc.audit()
        audit = "nessun errore" if not auditor.has_errors else f"{len(auditor.errors)} errori"
        blocchi = sum(1 for item in doc.blocks if item.name.startswith("NoveC_"))
        formato = rendi(dxf, lavoro / f"{nome}-resa.pdf", RESE / f"{nome}.png")
        entita = len(doc.modelspace()) + len(doc.paperspace(formato))
        geometria = misura(foglio, esito.frame.standard.sheet_height_mm, doc, simboli)
        print(
            f"{nome:10s} {formato:7s} {audit:14s} {entita:7d} {blocchi:7d} "
            f"{len(doc.layers):5d}  {geometria}"
        )


if __name__ == "__main__":
    main()
