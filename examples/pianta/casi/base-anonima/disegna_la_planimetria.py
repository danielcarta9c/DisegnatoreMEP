"""La planimetria d'origine del caso anonimo di REL-026 C-3: un trilocale inventato, disegnato
come lo disegna un architetto — muri campiti di nero, arredi, quote, il retino del balcone, i
nomi dei locali in maiuscolo con i mq, un cartiglio — su un A3 a 1:50.

    python examples/pianta/casi/base-anonima/disegna_la_planimetria.py

Scrive `planimetria.pdf` qui accanto, con il PDF del motore: stessi dati, stessi byte. Serve al
controllo a vista (`mep.py base base-anonima.json`): la base trascritta in `base-anonima.json`
si sovrappone a questa planimetria, e la tavola dell'impianto la ridisegna nella grafica
standard. **Nessun dato vero**: il committente, lo studio e l'indirizzo non esistono.
"""

from __future__ import annotations

import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI.parents[3] / "src"))

from disegnatore_mep.graphics.pdf import svg_in_pdf  # noqa: E402

FOGLIO_MM = (420.0, 297.0)
SCALA = 50
ORIGINE_MM = (60.0, 70.0)
"""Dove cade sul foglio il punto (0, 0) della pianta: lo spigolo esterno in alto a sinistra."""
K = 1000.0 / SCALA
"""Millimetri di carta per metro."""

PERIMETRO = 0.30
TRAMEZZA = 0.10

# Le stanze nette (x0, y0, x1, y1) in metri, e il nome come lo scrive l'architetto.
STANZE = {
    "SOGGIORNO-CUCINA": (0.30, 0.30, 5.70, 4.50),
    "CAMERA": (5.80, 0.30, 10.30, 4.50),
    "CAMERETTA": (0.30, 4.60, 3.60, 7.30),
    "INGRESSO": (3.70, 4.60, 7.70, 7.30),
    "BAGNO": (7.80, 4.60, 10.30, 7.30),
}

# I vani nei muri: (dove, da, a) — sul lato nord/sud una x, sul lato ovest/est o su una tramezza una y.
FINESTRE = [
    ("nord", 1.20, 2.80), ("nord", 7.30, 8.70), ("ovest", 1.80, 3.00), ("ovest", 5.50, 6.50), ("est", 5.70, 6.30),
]
PORTE = [
    # (muro, centro, larghezza, cerniera, verso): muro «sud» il perimetro, «y4.55» la tramezza giorno/notte…
    ("sud", 5.70, 0.90, -1, -1),
    ("y4.55", 7.00, 0.80, +1, -1),
    ("x3.65", 5.30, 0.80, -1, -1),
    ("x7.75", 5.30, 0.70, -1, +1),
]
VARCHI = [("y4.55", 4.60, 1.20)]


def p(x: float, y: float) -> tuple[float, float]:
    return (round(ORIGINE_MM[0] + x * K, 3), round(ORIGINE_MM[1] + y * K, 3))


def poligono(punti: list[tuple[float, float]], riempi: str = "none", tratto: str = "#000000",
             spessore: float = 0.25, extra: str = "") -> str:
    testo = " ".join(f"{a:g},{b:g}" for a, b in (p(*q) for q in punti))
    return (f'<polygon points="{testo}" fill="{riempi}" stroke="{tratto}" stroke-width="{spessore:g}"{extra}/>')


def linea(a: tuple[float, float], b: tuple[float, float], spessore: float = 0.18, colore: str = "#000000",
          tratteggio: str = "") -> str:
    (x1, y1), (x2, y2) = p(*a), p(*b)
    extra = f' stroke-dasharray="{tratteggio}"' if tratteggio else ""
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{colore}" stroke-width="{spessore:g}"{extra}/>'


def rettangolo(x0: float, y0: float, x1: float, y1: float, **kw: object) -> str:
    return poligono([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)  # type: ignore[arg-type]


def scritta(x: float, y: float, testo: str, corpo_mm: float = 3.2, grassetto: bool = False,
            ancora: str = "middle", carta: bool = False) -> str:
    cx, cy = (x, y) if carta else p(x, y)
    peso = ' font-weight="bold"' if grassetto else ""
    return f'<text x="{cx:g}" y="{cy:g}" font-size="{corpo_mm:g}"{peso} text-anchor="{ancora}">{testo}</text>'


def muri() -> list[str]:
    """I muri campiti di nero, come li disegna l'architetto: il perimetro e le tramezze, coi vani."""
    out: list[str] = []
    w, h = 10.60, 7.60
    # Il perimetro, lato per lato, spezzato dai vani.
    vani: dict[str, list[tuple[float, float]]] = {"nord": [], "sud": [], "ovest": [], "est": []}
    for lato, a, b in FINESTRE:
        vani[lato].append((a, b))
    for muro, c, larghezza, _, _ in PORTE:
        if muro in vani:
            vani[muro].append((c - larghezza / 2, c + larghezza / 2))
    for lato, lungo in (("nord", w), ("sud", w), ("ovest", h), ("est", h)):
        pieni, s = [], 0.0
        for a, b in sorted(vani[lato]):
            pieni.append((s, a))
            s = b
        pieni.append((s, lungo))
        for a, b in pieni:
            if lato == "nord":
                out.append(rettangolo(a, 0, b, PERIMETRO, riempi="#1a1a1a"))
            elif lato == "sud":
                out.append(rettangolo(a, h - PERIMETRO, b, h, riempi="#1a1a1a"))
            elif lato == "ovest":
                out.append(rettangolo(0, a, PERIMETRO, b, riempi="#1a1a1a"))
            else:
                out.append(rettangolo(w - PERIMETRO, a, w, b, riempi="#1a1a1a"))
    # Le tramezze: x=5.75 (0,30–4,50), y=4.55 (0,30–10,30), x=3.65 e x=7.75 (4,60–7,30).
    tramezze = {
        "x5.75": (5.75, 0.30, 4.50), "y4.55": (4.55, 0.30, 10.30), "x3.65": (3.65, 4.60, 7.30),
        "x7.75": (7.75, 4.60, 7.30),
    }
    for nome, (asse, da, a) in tramezze.items():
        tagli = [(c - lg / 2, c + lg / 2) for m, c, lg, _, _ in PORTE if m == nome]
        tagli += [(c - lg / 2, c + lg / 2) for m, c, lg in VARCHI if m == nome]
        s = da
        for t0, t1 in [*sorted(tagli), (a, a)]:
            if t0 > s:
                if nome.startswith("x"):
                    out.append(rettangolo(asse - TRAMEZZA / 2, s, asse + TRAMEZZA / 2, t0, riempi="#1a1a1a"))
                else:
                    out.append(rettangolo(s, asse - TRAMEZZA / 2, t0, asse + TRAMEZZA / 2, riempi="#1a1a1a"))
            s = t1
    return out


def serramenti() -> list[str]:
    """Le finestre a tre linee nello spessore del muro, le porte con l'anta e l'arco."""
    out: list[str] = []
    for lato, a, b in FINESTRE:
        for d in (0.0, PERIMETRO / 2, PERIMETRO):
            if lato == "nord":
                out.append(linea((a, d), (b, d)))
            elif lato == "ovest":
                out.append(linea((d, a), (d, b)))
            else:
                out.append(linea((10.60 - d, a), (10.60 - d, b)))
        if lato == "nord":
            out += [linea((a, 0), (a, PERIMETRO)), linea((b, 0), (b, PERIMETRO))]
    for muro, c, larghezza, cerniera, verso in PORTE:
        r = larghezza * K
        if muro in ("sud", "y4.55"):
            y = 7.30 if muro == "sud" else 4.55 + verso * TRAMEZZA / 2
            xc = c + cerniera * larghezza / 2
            punta = (xc, y + verso * larghezza)
            out.append(linea((xc, y), punta, 0.25))
            (x1, y1), (x2, y2) = p(*punta), p(c - cerniera * larghezza / 2, y)
            orario = 1 if (cerniera * verso) < 0 else 0
            out.append(f'<path d="M{x1:g} {y1:g} A{r:g} {r:g} 0 0 {orario} {x2:g} {y2:g}" fill="none" '
                       f'stroke="#000000" stroke-width="0.18"/>')
        else:
            x = float(muro[1:]) + verso * TRAMEZZA / 2
            yc = c + cerniera * larghezza / 2
            punta = (x + verso * larghezza, yc)
            out.append(linea((x, yc), punta, 0.25))
            (x1, y1), (x2, y2) = p(*punta), p(x, c - cerniera * larghezza / 2)
            orario = 0 if (cerniera * verso) < 0 else 1
            out.append(f'<path d="M{x1:g} {y1:g} A{r:g} {r:g} 0 0 {orario} {x2:g} {y2:g}" fill="none" '
                       f'stroke="#000000" stroke-width="0.18"/>')
    return out


def arredi() -> list[str]:
    """Quello che la base non trascrive: letti, divano, tavolo, cucina, sanitari, armadi."""
    g = "#555555"
    out = [
        # soggiorno-cucina: il piano della cucina coi fuochi e il lavello, il divano, il tavolo e le sedie
        rettangolo(0.30, 0.30, 0.90, 3.10, tratto=g), rettangolo(0.40, 0.60, 0.80, 1.10, tratto=g),
        rettangolo(0.40, 1.50, 0.80, 2.10, tratto=g),
        rettangolo(3.20, 2.80, 5.40, 3.70, tratto=g), rettangolo(3.20, 2.80, 5.40, 3.05, tratto=g),
        rettangolo(1.80, 1.30, 3.40, 2.20, tratto=g),
        *(rettangolo(x, y, x + 0.42, y + 0.40, tratto=g) for x in (1.95, 2.75) for y in (0.85, 2.25)),
        # camera: il letto matrimoniale coi comodini, l'armadio a muro con la croce
        rettangolo(7.15, 0.30, 8.85, 2.40, tratto=g), rettangolo(7.25, 0.40, 7.95, 0.80, tratto=g),
        rettangolo(8.05, 0.40, 8.75, 0.80, tratto=g),
        rettangolo(6.65, 0.30, 7.10, 0.75, tratto=g), rettangolo(8.90, 0.30, 9.35, 0.75, tratto=g),
        rettangolo(9.70, 0.80, 10.30, 3.60, tratto=g),
        linea((9.70, 0.80), (10.30, 3.60), 0.13, g), linea((10.30, 0.80), (9.70, 3.60), 0.13, g),
        # cameretta: il letto singolo e la scrivania
        rettangolo(0.30, 5.40, 1.20, 7.30, tratto=g), rettangolo(2.40, 6.70, 3.60, 7.30, tratto=g),
        # bagno: la doccia, il WC, il lavabo
        rettangolo(9.40, 6.40, 10.30, 7.30, tratto=g), linea((9.40, 6.40), (10.30, 7.30), 0.13, g),
        rettangolo(7.85, 5.95, 8.35, 6.55, tratto=g), rettangolo(8.70, 6.85, 9.30, 7.30, tratto=g),
        # ingresso: la scarpiera
        rettangolo(6.95, 6.80, 7.70, 7.30, tratto=g),
    ]
    return out


def balcone() -> list[str]:
    """Il balcone sul fronte nord: il parapetto e il retino del pavimento."""
    out = [poligono([(1.0, 0.0), (1.0, -1.40), (9.0, -1.40), (9.0, 0.0)], spessore=0.35)]
    # Il retino: le rette x + y = c a 45 gradi, ritagliate sul balcone (x 1–9, y -1,4–0).
    c = 1.0 - 1.40 + 0.30
    while c < 9.0:
        xa, xb = max(1.0, c), min(9.0, c + 1.40)
        out.append(linea((xa, c - xa), (xb, c - xb), 0.1, "#888888"))
        c = round(c + 0.30, 6)
    out.append(scritta(5.0, -0.55, "BALCONE", 3.0, True))
    out.append(scritta(5.0, -0.15, "mq 11,2", 2.4))
    return out


def quote() -> list[str]:
    """Le quote dell'architetto, fuori dalla pianta: lunghezza totale e parziali in alto, altezza a sinistra."""
    out: list[str] = []
    y = -2.10
    for a, b in ((0.0, 5.75), (5.75, 10.60)):
        out.append(linea((a, y), (b, y), 0.13))
        out += [linea((v, y - 0.12), (v, y + 0.12), 0.13) for v in (a, b)]
        out.append(scritta((a + b) / 2, y - 0.12, f"{b - a:.2f}".replace(".", ","), 2.6))
    y = -2.70
    out.append(linea((0.0, y), (10.60, y), 0.13))
    out += [linea((v, y - 0.12), (v, y + 0.12), 0.13) for v in (0.0, 10.60)]
    out.append(scritta(5.30, y - 0.12, "10,60", 2.6))
    x = -0.90
    out.append(linea((x, 0.0), (x, 7.60), 0.13))
    out += [linea((x - 0.12, v), (x + 0.12, v), 0.13) for v in (0.0, 4.55, 7.60)]
    out.append(scritta(x - 0.25, 2.30, "4,55", 2.6, ancora="end"))
    out.append(scritta(x - 0.25, 6.10, "3,05", 2.6, ancora="end"))
    return out


def nomi() -> list[str]:
    out: list[str] = []
    for nome, (x0, y0, x1, y1) in STANZE.items():
        mq = (x1 - x0) * (y1 - y0)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if nome == "SOGGIORNO-CUCINA":
            cx, cy = 2.60, 3.35
        if nome == "CAMERA":
            cx, cy = 8.00, 3.30
        out.append(scritta(cx, cy, nome, 3.0, True))
        out.append(scritta(cx, cy + 0.42, f"mq {mq:.1f}".replace(".", ","), 2.4))
    return out


def cartiglio() -> list[str]:
    x0, y0, x1, y1 = 300.0, 250.0, 410.0, 287.0
    out = [
        f'<rect x="{x0:g}" y="{y0:g}" width="{x1 - x0:g}" height="{y1 - y0:g}" fill="none" stroke="#000000" '
        'stroke-width="0.35"/>',
        f'<line x1="{x0:g}" y1="{y0 + 12:g}" x2="{x1:g}" y2="{y0 + 12:g}" stroke="#000000" stroke-width="0.18"/>',
        scritta(x0 + 3, y0 + 8, "STUDIO DI ARCHITETTURA ESEMPIO", 3.4, True, "start", True),
        scritta(x0 + 3, y0 + 19, "Trilocale di prova - pianta piano tipo", 2.8, False, "start", True),
        scritta(x0 + 3, y0 + 26, "Tavola A.01 - Stato di progetto", 2.8, False, "start", True),
        scritta(x0 + 3, y0 + 33, "Scala 1:50 - formato A3", 2.8, True, "start", True),
    ]
    return out


def svg() -> str:
    w, h = FOGLIO_MM
    parti = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}" '
        'font-family="Helvetica">',
        f'<rect x="0" y="0" width="{w:g}" height="{h:g}" fill="#ffffff" stroke="none"/>',
        f'<rect x="10" y="10" width="{w - 20:g}" height="{h - 20:g}" fill="none" stroke="#000000" stroke-width="0.5"/>',
        *balcone(), *arredi(), *muri(), *serramenti(), *quote(), *nomi(), *cartiglio(),
        "</svg>",
    ]
    return "\n".join(parti) + "\n"


def main() -> int:
    destinazione = QUI / "planimetria.pdf"
    destinazione.write_bytes(svg_in_pdf(svg(), QUI, "Planimetria di prova (inventata)").dati)
    print(f"Scritta: {destinazione}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
