"""Il giro dei DXF con l'ODA File Converter: DXF -> DWG (AutoCAD 2018) -> DXF.

AutoCAD qui non c'e'. L'ODA File Converter (Open Design Alliance, gratuito) legge e
scrive DWG con le librerie che usano molti programmi CAD: se un DXF gli arriva storto,
lo rifiuta o lo corregge, e il confronto fra andata e ritorno lo mostra. Per ciascun
DXF di `docs/collaudi/REL-004/dxf/`:

1. **il DWG** che ne fa ODA, e la sua versione (`AC1032` = AutoCAD 2018);
2. **il DXF di ritorno**, confrontato con quello di andata su tutto quello che il
   disegnatore vede: layer (colore esatto, tipo di linea, spessore, stampa,
   descrizione), entita' per tipo e layer nei due spazi, colori, blocchi, inserimenti,
   immagini, intestazione, presentazione attiva, impostazione di stampa, finestre, stili
   di testo. **Non** il colore d'indice di ripiego (codice 62): ODA lo ricalcola col suo
   criterio, che non e' documentato, e AutoCAD non lo usa;
3. **la resa** di andata e di ritorno, a 100 dpi, confrontata pixel per pixel.

E' uno strumento di sessione: vuole ezdxf, PyMuPDF, `xvfb-run` e l'ODA File Converter
estratto dalla sua AppImage (`--appimage-extract`, cosi' non serve FUSE). Dalla radice:

    PYTHONPATH=src python3 docs/collaudi/REL-004/giro_oda.py <AppRun di ODA> <cartella-di-lavoro>
"""

import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import ezdxf
import pymupdf
from ezdxf.addons.drawing import Frontend, RenderContext, layout
from ezdxf.addons.drawing import pymupdf as uscita_pymupdf
from ezdxf.math import BoundingBox2d

QUI = Path(__file__).resolve().parent
DXF = QUI / "dxf"
FORMATI = {"A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}


def converti(oda: Path, da: Path, a: Path, formato: str, filtro: str, lavoro: Path) -> int:
    runtime = lavoro / "runtime"
    runtime.mkdir(mode=0o700, exist_ok=True)
    ambiente = {**os.environ, "XDG_RUNTIME_DIR": str(runtime)}
    esito = subprocess.run(
        ["xvfb-run", "-a", str(oda), str(da), str(a), "ACAD2018", formato, "0", "1", filtro],
        env=ambiente, capture_output=True, timeout=600, check=False,
    )
    return esito.returncode


def firma(doc: ezdxf.document.Drawing) -> dict[str, object]:
    nome = next(n for n in doc.layouts.names() if n != "Model")
    carta = doc.paperspace(nome)
    stampa = carta.dxf_layout.dxf
    return {
        "layer": {
            item.dxf.name: (
                item.rgb and tuple(item.rgb), item.dxf.linetype.upper(),
                item.dxf.get("lineweight"), item.dxf.get("plot", 1), item.description,
            )
            for item in doc.layers
        },
        "modello": Counter((e.dxftype(), e.dxf.layer) for e in doc.modelspace()),
        "carta": Counter((e.dxftype(), e.dxf.layer) for e in carta),
        "colori": sorted(
            (e.dxftype(), tuple(e.rgb))
            for spazio in (doc.modelspace(), carta) for e in spazio if e.rgb is not None
        ),
        "blocchi": {
            b.name: Counter((e.dxftype(), e.dxf.layer, e.dxf.get("color")) for e in b)
            for b in doc.blocks if b.name.startswith("NoveC_")
        },
        "inserimenti": sorted(
            (i.dxf.name, i.dxf.layer, round(i.dxf.insert.x, 4), round(i.dxf.insert.y, 4),
             round(i.dxf.rotation % 360, 4), round(i.dxf.xscale, 4))
            for i in doc.modelspace().query("INSERT")
        ),
        "immagini": sorted(d.dxf.filename for d in doc.objects.query("IMAGEDEF")),
        "intestazione": {
            v: doc.header.get(v)
            for v in ("$INSUNITS", "$MEASUREMENT", "$LTSCALE", "$PSLTSCALE", "$CELTSCALE",
                      "$LWDISPLAY", "$TILEMODE", "$TEXTSTYLE")
        },
        "presentazione attiva": doc.layouts.active_layout().name,
        "stampa": (
            stampa.plot_configuration_file, stampa.paper_size, stampa.plot_layout_flags,
            stampa.plot_type, stampa.scale_numerator, stampa.scale_denominator,
            round(stampa.paper_width, 2), round(stampa.paper_height, 2),
            stampa.left_margin, stampa.bottom_margin, stampa.get("current_style_sheet"),
        ),
        "finestre": sorted(
            (v.dxf.layer, v.dxf.status, v.dxf.flags, round(v.dxf.width, 2),
             round(v.dxf.height, 2), round(v.dxf.view_height, 2))
            for v in carta.query("VIEWPORT")
        ),
        "stili": {
            s.dxf.name.upper(): s.dxf.font for s in doc.styles
            if s.dxf.name.upper().startswith("NOVEC")
        },
    }


def pixel(dxf: Path) -> tuple[int, int, bytes]:
    """La presentazione a foglio intero, 1:1, in pixel a 100 dpi."""
    doc = ezdxf.readfile(dxf)
    nome = next(n for n in doc.layouts.names() if n != "Model")
    carta = doc.paperspace(nome)
    larghezza, altezza = FORMATI[nome]
    contesto = RenderContext(doc)
    contesto.set_current_layout(carta)
    uscita = uscita_pymupdf.PyMuPdfBackend()
    Frontend(contesto, uscita).draw_layout(carta, finalize=True)
    pdf = uscita.get_pdf_bytes(
        layout.Page(larghezza, altezza, layout.Units.mm, margins=layout.Margins.all(0)),
        settings=layout.Settings(scale=1),
        render_box=BoundingBox2d([(0, 0), (larghezza, altezza)]),
    )
    immagine = pymupdf.open(stream=pdf, filetype="pdf")[0].get_pixmap(dpi=100)
    return immagine.width, immagine.height, immagine.samples


def main() -> None:
    oda, lavoro = Path(sys.argv[1]), Path(sys.argv[2])
    andata, dwg, ritorno = lavoro / "andata", lavoro / "dwg", lavoro / "ritorno"
    for cartella in (andata, dwg, ritorno):
        shutil.rmtree(cartella, ignore_errors=True)
        cartella.mkdir(parents=True)
    for file in DXF.iterdir():
        shutil.copy(file, andata)
    print("DXF -> DWG, uscita", converti(oda, andata, dwg, "DWG", "*.DXF", lavoro))
    for logo in DXF.glob("*.jpg"):
        shutil.copy(logo, dwg)
    print("DWG -> DXF, uscita", converti(oda, dwg, ritorno, "DXF", "*.DWG", lavoro))
    for logo in DXF.glob("*.jpg"):
        shutil.copy(logo, ritorno)
    for dxf in sorted(andata.glob("*.dxf")):
        versione = (dwg / f"{dxf.stem}.dwg").read_bytes()[:6].decode("ascii")
        prima, dopo = firma(ezdxf.readfile(dxf)), firma(ezdxf.readfile(ritorno / dxf.name))
        diversi = [chiave for chiave in prima if prima[chiave] != dopo[chiave]]
        a, b = pixel(dxf), pixel(ritorno / dxf.name)
        cambiati = sum(1 for i in range(0, len(a[2]), 3) if a[2][i:i + 3] != b[2][i:i + 3])
        print(
            f"{dxf.stem:10s} DWG {versione}  ritorno "
            f"{'identico' if not diversi else 'diverso in ' + ', '.join(diversi)}  "
            f"resa {a[0]}x{a[1]}, pixel diversi {cambiati}"
        )


if __name__ == "__main__":
    main()
