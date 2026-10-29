"""Tavola M.03 — pianta dei posizionamenti e dei tracciati, sulla planimetria catastale ingrandita a 1:50.
Stessi numeri di M.02 (dim.json). Scrive SVG e PDF nella cartella della tavola, col cartiglio Nove C.
Uso: python3 pianta.py <cartella tavola>
"""
import json
import sys
from pathlib import Path

from PIL import Image

L = Path(__file__).parent
sys.path.insert(0, str(L / "skill" / "scripts"))
from disegnatore_mep.graphics.cartiglio import (  # noqa: E402
    Cartiglio, CartiglioDellaTavola, disegna_cartiglio, valori_del_cartiglio)
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.pdf import scrivi_pdf  # noqa: E402
from disegnatore_mep.model.project import ProjectModel  # noqa: E402

PT = 0.3528
dim = json.loads((L / "dim.json").read_text(encoding="utf-8"))
T = {t["id"]: t for t in dim["tratte"]}

PX_M = 59.06                      # px per metro sul catastale a 300 dpi, scala 1:200
ORIG_PX = (80, 100)               # origine dell'edificio sul ritaglio
CROP = (55, 75, 765, 750)         # ritaglio del catastale da stampare
K = 20.0 / PX_M                   # mm di carta per pixel a 1:50 (1 m = 20 mm)
X0, Y0 = 16.0, 19.0               # dove cade l'angolo del ritaglio sul foglio

ARIA, FRIGO, COND, POT, LINK, BUS = "#148f77", "#6c3483", "#616a6b", "#b03a2e", "#a04000", "#1f618d"


def P(x, y):
    """metri dell'edificio -> mm del foglio"""
    return (X0 + (ORIG_PX[0] - CROP[0] + x * PX_M) * K, Y0 + (ORIG_PX[1] - CROP[1] + y * PX_M) * K)


class S:
    def __init__(self):
        self.p = []

    def add(self, t):
        self.p.append(t)

    def linea(self, pts, col, w=0.45, dash=None, metri=True):
        q = [P(*a) if metri else a for a in pts]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in q)}" fill="none" stroke="{col}" '
                 f'stroke-width="{w}"{d}/>')

    def rett(self, x0, y0, x1, y1, col="black", w=0.3, fill="none", dash=None, metri=True, op=None):
        if metri:
            (x0, y0), (x1, y1) = P(x0, y0), P(x1, y1)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{op}"' if op else ""
        self.add(f'<rect x="{min(x0, x1):.2f}" y="{min(y0, y1):.2f}" width="{abs(x1 - x0):.2f}" '
                 f'height="{abs(y1 - y0):.2f}" fill="{fill}" stroke="{col}" stroke-width="{w}"{d}{o}/>')

    def testo(self, t, x, y, corpo=7, col="black", grass=False, anchor="start", metri=False, bianco=False):
        if metri:
            x, y = P(x, y)
        t = (t.replace("≥ ", "min. ").replace("≥", "min. ").replace("&", "&amp;"))
        g = ' font-weight="bold"' if grass else ""
        if bianco:
            from disegnatore_mep.graphics.cartiglio import larghezza_mm
            w = larghezza_mm(t, corpo, grass)
            xx = x - (w / 2 if anchor == "middle" else (w if anchor == "end" else 0))
            self.add(f'<rect x="{xx - 0.6:.2f}" y="{y - corpo * PT * 0.78:.2f}" width="{w + 1.2:.2f}" '
                     f'height="{corpo * PT * 1.05:.2f}" fill="white" stroke="none" fill-opacity="0.85"/>')
        self.add(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{corpo * PT:.3f}"{g} fill="{col}" '
                 f'font-family="Arial, Helvetica, sans-serif" text-anchor="{anchor}">{t}</text>')

    def cerchio(self, x, y, r, col, fill="white", w=0.3, metri=True):
        if metri:
            x, y = P(x, y)
        self.add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{col}" stroke-width="{w}"/>')


def m(x):
    return f"{x:g}".replace(".", ",")


def componi(cartella: Path):
    # sfondo: catastale schiarito, in grigi
    im = Image.open(L / "pt_crop.png").convert("L").crop(CROP)
    im = im.point(lambda v: int(255 - (255 - v) * 0.42))
    jpg = cartella / "AA-01_M.03_catastale.jpg"
    im.save(jpg, quality=88)
    w_mm, h_mm = (CROP[2] - CROP[0]) * K, (CROP[3] - CROP[1]) * K

    s = S()
    s.add(f'<image href="{jpg.name}" x="{X0}" y="{Y0}" width="{w_mm:.2f}" height="{h_mm:.2f}" preserveAspectRatio="none"/>')

    # destinazioni di progetto
    for nome, x, y in [("Z1 · Camera 13 m²", 2.2, 1.6), ("Z2 · Camera 15 m² (ex cucina)", 7.0, 1.2),
                       ("Z3 · Camera 16 m²", 2.2, 8.3), ("Z4 · Soggiorno-cucina 24 m²", 8.2, 8.6),
                       ("disimpegno ovest", 4.75, 5.35), ("disimpegno est (ingresso)", 8.40, 5.28),
                       ("bagno", 1.6, 5.25)]:
        s.testo(nome, x, y, 7.5 if nome.startswith("Z") else 6.5, "#1c2e4a", nome.startswith("Z"), "middle",
                metri=True, bianco=True)

    # blocco UI / plenum / ripresa nel controsoffitto del disimpegno est
    b = dim["blocco"]
    s.rett(*b["plenum"], col="black", w=0.35, fill="#d6eae6")
    s.rett(*b["ui"], col="black", w=0.35, fill="#e6e9ef")
    s.rett(*b["ripresa"], col="black", w=0.35, fill="#f3f4f7")
    x0, y0, x1, y1 = b["ripresa"]
    s.rett(x0 - 0.02, y0 - 0.0, x1 + 0.02, y1, col=ARIA, w=0.3, dash="1.2 0.8")
    s.testo("PLZ-01", (b["plenum"][0] + b["plenum"][2]) / 2, 4.73, 5.5, grass=True, anchor="middle", metri=True)
    s.testo("+ CZ-01", (b["plenum"][0] + b["plenum"][2]) / 2, 4.98, 5, anchor="middle", metri=True)
    s.testo("UI-01", (b["ui"][0] + b["ui"][2]) / 2, 4.88, 6, grass=True, anchor="middle", metri=True)
    s.testo("RA-01 ripresa 1000×250", 7.62, 4.78, 5.5, ARIA, anchor="start", metri=True, bianco=True)

    # rami aria e bocchette
    getto = {"B1": (0, -1), "B2": (0, -1), "B3": (0, 1), "B4": (0, 1), "B5": (0, 1)}
    for bid, v in dim["percorsi_aria"].items():
        pts = v["punti"]
        s.linea(pts, ARIA, 0.9)
        xe, ye = pts[-1]
        dx, dy = getto[bid]
        # bocchetta 400 mm (8 mm a 1:50) sul filo del muro, freccia del getto
        bx, by = P(xe, ye)
        s.rett(bx - 4, by - 0.9, bx + 4, by + 0.9, col=ARIA, w=0.4, fill="white", metri=False)
        s.linea([(bx, by + dy * 1.0), (bx, by + dy * 6.0)], ARIA, 0.35, metri=False)
        s.add(f'<path d="M{bx - 1.1:.2f} {by + dy * 4.6:.2f} L{bx:.2f} {by + dy * 6.4:.2f} L{bx + 1.1:.2f} '
              f'{by + dy * 4.6:.2f}" fill="none" stroke="{ARIA}" stroke-width="0.35"/>')
        t = T[f"A-{bid}"]
        lato = {"B1": -1, "B2": 1, "B3": -1, "B4": 1, "B5": 1}[bid]
        s.testo(f"{bid} · Ø200 · L {m(t['l_quot_m'])} m", bx, by + dy * (13.0 if bid == "B4" else 9.0) + (1.8 if dy > 0 else 0), 6,
                ARIA, True, "middle", metri=False, bianco=True)
    # attraversamenti della tramezza
    for y in (4.55, 4.83, 4.18):
        s.cerchio(dim["tramezza_x"], y, 0.9, "black", w=0.25)

    # condensa
    s.linea(dim["percorso_cond"], COND, 0.6, "1.6 0.8")
    xs, ys = P(*dim["percorso_cond"][-1])
    s.cerchio(xs, ys, 1.0, COND, metri=False)
    s.testo(f"condensa PVC Ø32 · L {m(T['C-1']['l_quot_m'])} m, sifone e scarico Ø40", xs - 2, ys + 4.2, 5.5, COND,
            metri=False, bianco=True)

    # frigo + collegamento UI-UE
    s.linea(dim["percorso_frigo"], FRIGO, 0.7)
    ux, uy = dim["ue_pos"]
    a, bb = P(ux - 0.05, uy - 0.48), P(ux + 0.36, uy + 0.48)
    s.rett(a[0], a[1], bb[0], bb[1], col="black", w=0.4, fill="#e6e9ef", metri=False)
    s.testo("UE-01", bb[0] + 1.5, P(0, uy)[1] - 1.0, 6.5, grass=True, metri=False, bianco=True)
    s.testo("posizione da confermare", bb[0] + 1.5, P(0, uy)[1] + 1.8, 5.5, metri=False, bianco=True)
    s.testo(f"linee frigo 1/4\"-1/2\" + 4G1,5 · L {m(T['R-L']['l_quot_m'])} m", P(9.35, 3.4)[0] + 1.2,
            P(9.35, 3.4)[1], 5.5, FRIGO, metri=False, bianco=True)

    # elettrico
    qx, qy = dim["qe"]
    s.linea([(qx, qy), (8.95, 4.62), (9.3, 4.62), (9.3, 2.85), (ux, 2.85)], POT, 0.45, "2.4 0.6 0.6 0.6")
    s.linea([(qx, qy), (6.2, qy)], POT, 0.45, "2.4 0.6 0.6 0.6")
    a = P(qx - 0.12, qy - 0.06)
    s.rett(a[0], a[1], a[0] + 4.8, a[1] + 2.4, col="black", w=0.3, fill="#2d2d2d", metri=False)
    s.testo("QE-01 (presunto)", a[0] + 2.4, a[1] + 5.4, 5.5, anchor="middle", metri=False, bianco=True)
    s.cerchio(9.3, 3.55, 0.8, POT, w=0.3)
    s.testo("SZ-01", P(9.3, 3.55)[0] + 1.5, P(9.3, 3.55)[1] + 0.8, 5, POT, metri=False, bianco=True)

    # bus e termostati, Madoka
    cx, cy = dim["centrale"]
    for tid, (zid, (tx, ty)) in dim["termostati"].items():
        via = (tx, cy) if zid in ("Z3", "Z4") else (tx, 4.02)
        s.linea([(cx, cy), (cx, via[1]), via, (tx, ty)] if zid in ("Z1", "Z2") else [(cx, cy), via, (tx, ty)],
                BUS, 0.4, "1 0.8")
        x, y = P(tx, ty)
        s.rett(x - 1.6, y - 1.6, x + 1.6, y + 1.6, col=BUS, w=0.35, fill="white", metri=False)
        s.testo("T", x, y + 1.0, 6, BUS, True, "middle", metri=False)
        s.testo(tid, x + 2.4, y + 1.0, 5.5, BUS, metri=False, bianco=True)
    mx, my = dim["madoka"]
    s.linea([(7.05, 4.45), (mx, 4.45), (mx, my)], BUS, 0.4, "1 0.8")
    x, y = P(mx, my)
    s.rett(x - 1.6, y - 1.6, x + 1.6, y + 1.6, col=BUS, w=0.35, fill="white", metri=False)
    s.testo("CF-01", x + 2.4, y + 1.0, 5.5, BUS, metri=False, bianco=True)

    # orientamento e scala grafica
    s.testo("NO", X0 + w_mm / 2, Y0 + 3.0, 7, "#1c2e4a", True, "middle")
    s.testo("SE", X0 + w_mm / 2, Y0 + h_mm - 1.0, 7, "#1c2e4a", True, "middle")
    s.testo("SO", X0 + 1.0, Y0 + h_mm / 2, 7, "#1c2e4a", True)
    s.testo("NE", X0 + w_mm - 1.0, Y0 + h_mm / 2 - 20, 7, "#1c2e4a", True, "end")
    xb, yb = X0 + 4, Y0 + h_mm - 6
    for i in range(5):
        s.rett(xb + i * 20, yb, xb + (i + 1) * 20, yb + 1.2, col="black", w=0.2,
               fill="black" if i % 2 == 0 else "white", metri=False)
    for i in range(6):
        s.testo(f"{i} m" if i in (0, 5) else str(i), xb + i * 20, yb - 0.8, 5.5, anchor="middle")

    # colonna di destra: legenda e note
    xl, yl = 268.0, 22.0
    s.testo("PIANTA DEI POSIZIONAMENTI E DEI TRACCIATI", xl, yl, 8, "#1c2e4a", True)
    yl += 4.0
    s.testo("su planimetria catastale 1:200 ingrandita a 1:50 — misure indicative (±10-15%)", xl, yl, 6, "#555555")
    yl += 7
    leg = [(ARIA, None, 0.9, "rami di mandata Ø200 flessibili coibentati, bocchette B1-B5 e getto"),
           (FRIGO, None, 0.7, "linee frigorifere 1/4\"-1/2\" e cavo di collegamento UI-UE"),
           (COND, "1.6 0.8", 0.6, "scarico condensa con sifone allo scarico del bagno"),
           (POT, "2.4 0.6 0.6 0.6", 0.45, "alimentazioni dal quadro: UE con sezionatore SZ-01, centrale Airzone"),
           (BUS, "1 0.8", 0.4, "bus Airzone ai termostati TZ e linea P1-P2 al comando Madoka CF-01")]
    for col, dash, w, testo in leg:
        s.linea([(xl, yl - 1.0), (xl + 10, yl - 1.0)], col, w, dash, metri=False)
        s.testo(testo, xl + 13, yl, 6.5)
        yl += 5.2
    s.rett(xl, yl - 2.6, xl + 10, yl - 0.4, col=ARIA, w=0.3, dash="1.2 0.8", metri=False)
    s.testo("griglia di ripresa 1000×250 nel controsoffitto (Committente)", xl + 13, yl, 6.5)
    yl += 5.2
    s.cerchio(xl + 5, yl - 1.4, 0.9, "black", metri=False)
    s.testo("foratura della tramezza fra i disimpegni", xl + 13, yl, 6.5)
    yl += 9
    s.testo("QUOTE E POSIZIONI", xl, yl, 8, "#1c2e4a", True)
    yl += 5.5
    note = [
        "UI-01 e plenum PLZ-01 nel controsoffitto del disimpegno est, uscite del plenum verso ovest; ripresa RA-01 "
        "verso l'ingresso. Altezza libera min. 35 cm sotto il solaio; botole di ispezione 600×600 sotto UI e plenum.",
        "Bocchette a parete sotto il soffitto, sopra le porte delle camere (B1, B3) o sul muro verso il disimpegno "
        "(B2, B4); B5 nella veletta lungo il muro del soggiorno. Velette: altezza utile min. 30 cm.",
        "Termostati TZ a 1,50 m dal pavimento, accanto alla porta, lontani da bocchette e sole; Madoka CF-01 "
        "all'ingresso.",
        "UE-01 a parete sotto il portico (fronte NE), a distanza dalla PdC idronica del riscaldamento; quadro QE-01 presunto "
        "all'ingresso: entrambi da confermare in sopralluogo.",
        "Condensa dalla UI verso il bagno attraverso la tramezza, in pendenza min. 1%, poi in traccia fino al sifone.",
        "Tracciati indicativi: il percorso definitivo si fissa in sopralluogo con l'impresa del controsoffitto. "
        "Diametri, portate e lunghezze da quotare: tavola M.02, tabella delle tratte.",
    ]
    from disegnatore_mep.graphics.cartiglio import larghezza_mm

    def a_capo(t, w, corpo=6.5):
        out, r = [], ""
        for p in t.split():
            prova = (r + " " + p).strip()
            if larghezza_mm(prova.replace("≥", "min."), corpo, False) <= w or not r:
                r = prova
            else:
                out.append(r)
                r = p
        return out + [r]

    for i, n in enumerate(note, start=1):
        s.testo(f"{i}.", xl, yl, 6.5)
        for k, r in enumerate(a_capo(n, 134)):
            s.testo(r, xl + 4, yl + k * 3.0, 6.5)
        yl += len(a_capo(n, 134)) * 3.0 + 1.6

    # cartiglio
    proj = ProjectModel.model_validate_json((L / "grafo-completo.json").read_text(encoding="utf-8"))
    val = valori_del_cartiglio(proj, "t1")
    val.update({"titolo_tavola": "Pianta dei posizionamenti e dei tracciati", "numero_tavola": "M.03",
                "scala": "1:50"})
    cart = Cartiglio.da_file(L / "skill" / "dati" / "cartiglio" / "Cartiglio_NoveC_A3.json")
    frame = NOVE_C_A3
    tav = CartiglioDellaTavola(cartiglio=cart, valori=val)
    cartsvg = disegna_cartiglio(tav, frame).svg
    logo = L / "skill" / "dati" / "cartiglio" / "Cartiglio_NoveC_A3-logo.jpg"
    (cartella / logo.name).write_bytes(logo.read_bytes())

    W, H = frame.standard.sheet_width_mm, frame.standard.sheet_height_mm
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}" '
           f'font-family="Arial, Helvetica, sans-serif">' + "".join(s.p) + cartsvg + "</svg>")
    out = cartella / "caso-prova-aria-aria-M03.svg"
    out.write_text(svg, encoding="utf-8")
    esito = scrivi_pdf(out, titolo="AA-01 — M.03 Pianta dei posizionamenti e dei tracciati")
    if esito.sostituzioni:
        print("caratteri sostituiti:", {x.carattere for x in esito.sostituzioni})
    print(out.with_suffix(".pdf"), f"fine colonna destra y {yl:.1f}")


if __name__ == "__main__":
    componi(Path(sys.argv[1]) if len(sys.argv) > 1 else L / "tavola")
