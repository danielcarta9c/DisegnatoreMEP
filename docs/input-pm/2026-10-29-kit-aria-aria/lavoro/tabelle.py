"""Scrive sulla tavola (SVG -> PDF, e DXF) la tabella delle tratte, le note e il computo.

Le zone sono quelle che il telaio A2T lascia libere: a destra del disegno e sotto.
Uso: python3 tabelle.py <cartella tavola>
"""
import json
import sys
from pathlib import Path

L = Path(__file__).parent
sys.path.insert(0, str(L / "skill" / "scripts"))
from disegnatore_mep.graphics.cartiglio import larghezza_mm  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A2T  # noqa: E402
from disegnatore_mep.graphics.pdf import scrivi_pdf  # noqa: E402

PT = 0.3528
CORPO = 7.0            # pt del corpo delle tabelle
CORPO_TIT = 8.0
H_RIGA = 3.4
TRATTO = 0.18
TRATTO_F = 0.35
GRIGIO = "#e6e9ef"
BLU = "#1c2e4a"

dim = json.loads((L / "dim.json").read_text(encoding="utf-8"))


def pulisci(t):
    return (str(t).replace("≥ ", "min. ").replace("≥", "min. ").replace("≤ ", "max. ")
            .replace("→", "-").replace(" ", " "))


def num(x, dec=1):
    if x is None or x == "":
        return ""
    if isinstance(x, (int, float)):
        s = f"{x:.{dec}f}".rstrip("0").rstrip(".") if isinstance(x, float) else str(x)
        return s.replace(".", ",")
    return str(x)


def a_capo(testo, larghezza, corpo=CORPO, grassetto=False):
    parole, righe, riga = pulisci(testo).split(), [], ""
    for p in parole:
        prova = (riga + " " + p).strip()
        if larghezza_mm(prova, corpo, grassetto) <= larghezza or not riga:
            riga = prova
        else:
            righe.append(riga)
            riga = p
    if riga:
        righe.append(riga)
    return righe or [""]


class Disegno:
    def __init__(self):
        self.svg, self.linee, self.testi, self.campi = [], [], [], []

    def linea(self, x1, y1, x2, y2, w=TRATTO, col="black"):
        self.svg.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{col}" stroke-width="{w}"/>')
        self.linee.append((x1, y1, x2, y2, w))

    def campo(self, x, y, w, h, col=GRIGIO):
        self.svg.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{col}" stroke="none"/>')
        self.campi.append((x, y, w, h))

    def testo(self, t, x, y, corpo=CORPO, grassetto=False, anchor="start", col="black"):
        t = pulisci(t)
        esc = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        peso = ' font-weight="bold"' if grassetto else ""
        self.svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{corpo * PT:.4f}"{peso} fill="{col}" '
                        f'font-family="Arial, Helvetica, sans-serif" text-anchor="{anchor}">{esc}</text>')
        self.testi.append((t, x, y, corpo * PT, grassetto, anchor))


def tabella(d, x0, y0, colonne, righe, titolo=None, gruppi=None):
    """colonne: [(intestazione, larghezza, allineamento)], righe: [[celle]] o ("gruppo", testo).
    Ritorna la y di fine."""
    y = y0
    larg = sum(c[1] for c in colonne)
    if titolo:
        d.testo(titolo, x0, y + 3.2, CORPO_TIT, True, col=BLU)
        y += 5.0
    # intestazione
    righe_int = [a_capo(c[0], c[1] - 2.4, CORPO, True) for c in colonne]
    h_int = max(len(r) for r in righe_int) * 2.8 + 1.6
    d.campo(x0, y, larg, h_int)
    d.linea(x0, y, x0 + larg, y, TRATTO_F)
    x = x0
    for (intest, w, al), rr in zip(colonne, righe_int):
        for k, r in enumerate(rr):
            yy = y + 1.0 + 2.47 + k * 2.8
            if al == "r":
                d.testo(r, x + w - 1.2, yy, CORPO, True, "end")
            else:
                d.testo(r, x + 1.2, yy, CORPO, True)
        x += w
    y += h_int
    d.linea(x0, y, x0 + larg, y, TRATTO)
    spezzoni = [[y0 + (5.0 if titolo else 0), y]]
    for riga in righe:
        if isinstance(riga, tuple) and riga[0] == "gruppo":
            spezzoni[-1][1] = y
            d.campo(x0, y, larg, H_RIGA, "#f3f4f7")
            d.testo(riga[1], x0 + 1.2, y + 2.55, CORPO, True, col=BLU)
            y += H_RIGA
            d.linea(x0, y, x0 + larg, y, TRATTO)
            spezzoni.append([y, y])
            continue
        celle = [a_capo(v, c[1] - 2.4) if c[2] != "r" else [pulisci(v)] for v, c in zip(riga, colonne)]
        n = max(len(c) for c in celle)
        h = H_RIGA + (n - 1) * 2.8
        x = x0
        for (intest, w, al), cc in zip(colonne, celle):
            for k, r in enumerate(cc):
                yy = y + 2.55 + k * 2.8
                if al == "r":
                    d.testo(r, x + w - 1.2, yy, CORPO, False, "end")
                else:
                    d.testo(r, x + 1.2, yy, CORPO)
            x += w
        y += h
        d.linea(x0, y, x0 + larg, y, TRATTO)
        spezzoni[-1][1] = y
    # verticali: i bordi per tutta l'altezza, gli interni solo fuori dalle righe di gruppo
    yi = y0 + (5.0 if titolo else 0)
    d.linea(x0, yi, x0, y, TRATTO)
    d.linea(x0 + larg, yi, x0 + larg, y, TRATTO)
    x = x0
    for c in colonne[:-1]:
        x += c[1]
        for a, b in spezzoni:
            if b > a:
                d.linea(x, a, x, b, TRATTO)
    d.linea(x0, y, x0 + larg, y, TRATTO_F)
    return y


def note(d, x0, y0, larghezza, titolo, elenco, prefisso=""):
    y = y0
    d.testo(titolo, x0, y + 3.2, CORPO_TIT, True, col=BLU)
    y += 5.5
    rientro = 6.0 if prefisso else 4.5
    for i, n in enumerate(elenco, start=1):
        righe = a_capo(n, larghezza - rientro - 0.5)
        d.testo(f"{prefisso}{i}" if prefisso else f"{i}.", x0, y + 2.6)
        for k, r in enumerate(righe):
            d.testo(r, x0 + rientro, y + 2.6 + k * 3.0)
        y += len(righe) * 3.0 + 0.9
    return y


# ------------------------------------------------------------------ contenuti
NOMI = {"PLZ-01": "PLZ-01", "UE-01": "UE-01", "UI-01": "UI-01", "QE-01": "quadro", "CF-01": "CF-01",
        "RA-01": "ripresa"}
ORDINE = dim["ordine"]
T = {t["id"]: t for t in dim["tratte"]}
amb = {b["id"]: b["ambiente"] for b in dim["bocchette"]}


def da_a(t):
    da, a = t["da"], t["a"]
    if t["rete"] == "bus-airzone":
        return f"CZ-01 - {a}"
    if da == "PLZ-01":
        return f"PLZ-01 - {a} {amb.get(a, '')}".strip()
    if t["rete"] == "bus-airzone":
        return f"CZ-01 - {a}"
    if t["id"] == "E-4":
        return "UI-01 - CZ-01"
    if t["id"] == "E-3":
        return "quadro - CZ-01"
    if t["id"] == "E-1":
        return "quadro - SZ - UE-01"
    if t["id"] == "A-RIP":
        return "ripresa - UI-01"
    return f"{NOMI.get(da, da)} - {NOMI.get(a, a)}"


righe_tratte = []
for tid in ORDINE:
    t = T[tid]
    righe_tratte.append([t["num"], da_a(t), t["dn"] or "-", t["materiale"],
                         num(t["portata_m3h"], 0) if t["portata_m3h"] else "",
                         num(t["v_ms"], 1) if t["v_ms"] else "",
                         num(t["l_stima_m"], 1) if t["l_stima_m"] is not None else "",
                         num(t["l_quot_m"], 1) if t["l_quot_m"] is not None else ""])
COL_TRATTE = [("Tratto", 11, "l"), ("Da - a", 52, "l"), ("Ø / sezione", 21, "l"),
              ("Materiale", 36, "l"), ("Q m³/h", 10, "r"), ("v m/s", 9, "r"),
              ("L stim. m", 11.5, "r"), ("L quot. m", 12.5, "r")]

COL_COMPUTO = [("Rif.", 9, "l"), ("Voce", 141, "l"), ("UM", 13, "l"), ("Q.tà", 11, "r"),
               ("Fornitura", 20, "l"), ("Note", 63, "l")]


def righe_computo():
    out, cat, n = [], None, {}
    for v in dim["bom"]:
        if v["cat"] != cat:
            cat = v["cat"]
            out.append(("gruppo", cat))
        lettera = cat[0]
        n[lettera] = n.get(lettera, 0) + 1
        q = v["q"]
        qs = num(float(q), 2) if isinstance(q, float) else str(q)
        out.append([f"{lettera}.{n[lettera]}", v["voce"], v["um"], qs, v["fornitura"], v["note"]])
    return out


def misura_righe(righe, colonne):
    h = 0
    for r in righe:
        if isinstance(r, tuple):
            h += H_RIGA
            continue
        n = max(len(a_capo(v, c[1] - 2.4)) if c[2] != "r" else 1 for v, c in zip(r, colonne))
        h += H_RIGA + (n - 1) * 2.8
    return h


def componi(cartella: Path):
    svgp = next(cartella.glob("*-t1.svg"))
    frame = NOVE_C_A2T
    area = frame.drawing_rect_mm
    legenda = frame.legend_rect_mm
    xd = area.right_mm + 4.0
    wd = legenda.x_mm - 3.0 - xd
    d = Disegno()

    y = tabella(d, xd, area.y_mm + 2.0, COL_TRATTE, righe_tratte,
                "TABELLA DELLE TRATTE — diametri e lunghezze per la quotazione")
    y = note(d, xd, y + 3.0, wd, "NOTE TECNICHE", dim["note"])
    y = note(d, xd, y + 2.0, wd, "G. ATTIVITÀ DA QUOTARE A CORPO (manodopera e mezzi)", dim["attivita"], "G.")
    fine_destra = y

    # computo in basso, su due colonne
    righe = righe_computo()
    x0, y0 = area.x_mm + 2.0, area.bottom_mm + 1.5
    larg = sum(c[1] for c in COL_COMPUTO)
    gap = (legenda.x_mm - 3.0 - x0 - 2 * larg)
    # punto di taglio: equilibra le altezze, senza spezzare un gruppo dal suo titolo
    tot = misura_righe(righe, COL_COMPUTO)
    acc, taglio = 0, len(righe)
    for i, r in enumerate(righe):
        acc += misura_righe([r], COL_COMPUTO)
        if acc >= tot / 2 - 2:
            taglio = i + 1
            break
    if isinstance(righe[taglio - 1], tuple):
        taglio -= 1
    sx, dx = righe[:taglio], righe[taglio:]
    d.testo("COMPUTO DELLE QUANTITÀ E DEI PEZZI SPECIALI — quantità indicative per il prezzo a corpo, da verificare in sopralluogo "
            "(varianti e voci aggiunte: file Excel)",
            x0, y0 + 3.2, CORPO_TIT, True, col=BLU)
    y1 = tabella(d, x0, y0 + 5.0, COL_COMPUTO, sx)
    y2 = tabella(d, x0 + larg + gap, y0 + 5.0, COL_COMPUTO, dx)
    limite = frame.title_block_rect_mm.y_mm - 1.0
    print(f"zona destra: x {xd:.1f} larga {wd:.1f}, fine {fine_destra:.1f} (limite {area.bottom_mm:.1f})")
    print(f"computo: larghezza {2 * larg + gap:.1f}, fine {max(y1, y2):.1f} (limite {limite:.1f}), gap {gap:.1f}")
    if fine_destra > area.bottom_mm or max(y1, y2) > limite or gap < 3:
        print("ATTENZIONE: le tabelle escono dalla zona")

    testo = svgp.read_text(encoding="utf-8")
    testo = testo.replace("</svg>", '<g class="tabelle-bd-mi-059">' + "".join(d.svg) + "</g></svg>")
    svgp.write_text(testo, encoding="utf-8")
    esito = scrivi_pdf(svgp, titolo="AA-01 — M.02 Schema funzionale canalizzato")
    if esito.sostituzioni:
        print("caratteri sostituiti:", {s.carattere for s in esito.sostituzioni})
    dxf(cartella, d)


def dxf(cartella: Path, d: Disegno):
    import ezdxf
    p = next(cartella.glob("*-t1.dxf"))
    doc = ezdxf.readfile(p)
    msp = doc.modelspace()
    H = 420.0
    stile = None
    for e in msp.query("TEXT"):
        stile = e.dxf.style
        break
    if "M-ANNO-SCHD" not in doc.layers:
        doc.layers.add("M-ANNO-SCHD", color=7)
    for x1, y1, x2, y2, w in d.linee:
        msp.add_line((x1, H - y1), (x2, H - y2), dxfattribs={"layer": "M-ANNO-SCHD", "lineweight": 18 if w < 0.3 else 35})
    from ezdxf.enums import TextEntityAlignment
    for t, x, y, h, g, anchor in d.testi:
        att = {"layer": "M-ANNO-SCHD", "height": h * 0.716}
        if stile:
            att["style"] = stile
        e = msp.add_text(t, dxfattribs=att)
        al = {"start": TextEntityAlignment.LEFT, "end": TextEntityAlignment.RIGHT,
              "middle": TextEntityAlignment.CENTER}[anchor]
        e.set_placement((x, H - y), align=al)
    doc.saveas(p)


if __name__ == "__main__":
    componi(Path(sys.argv[1]) if len(sys.argv) > 1 else L / "tavola")
