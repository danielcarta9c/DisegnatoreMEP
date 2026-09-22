# -*- coding: utf-8 -*-
"""Figura di spiegazione su B12. Non e' una tavola e non fa convenzione (D-165)."""

ROSSO, BLU, NERO, GRIGIO, AMBRA = "#c0392b", "#2471a3", "#111111", "#7b8a8b", "#b9770e"
W, H = 420.0, 297.0
out = []
A = out.append


def testo(x, y, s, size=3.3, col=NERO, peso="normal", anchor="start", corsivo="normal"):
    A(f'<text x="{x:g}" y="{y:g}" font-family="Helvetica,Arial,sans-serif" '
      f'font-size="{size:g}" fill="{col}" font-weight="{peso}" font-style="{corsivo}" '
      f'text-anchor="{anchor}">{s}</text>')


def blocco(x, y, righe, size=3.3, col=NERO, passo=5.0):
    for i, riga in enumerate(righe):
        testo(x, y + i * passo, riga, size, col)


def linea(pts, col, w=0.9, dash=None):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:g} {y:g}" for i, (x, y) in enumerate(pts))
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    A(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w:g}" '
      f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')


def scatola(x, y, w, h, etichetta, sotto=None):
    A(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="#ffffff" '
      f'stroke="{NERO}" stroke-width="0.4"/>')
    testo(x + w / 2, y + h / 2 + 1.1, etichetta, 3.1, NERO, "bold", "middle")
    if sotto:
        testo(x + w / 2, y + h + 4.2, sotto, 2.9, GRIGIO, anchor="middle")


def freccia(x, y, verso, col):
    d = {"giu": [(0, 0), (-1.2, -2.4), (1.2, -2.4)],
         "su": [(0, 0), (-1.2, 2.4), (1.2, 2.4)],
         "dx": [(0, 0), (-2.4, -1.2), (-2.4, 1.2)],
         "sx": [(0, 0), (2.4, -1.2), (2.4, 1.2)]}[verso]
    A('<polygon points="' + " ".join(f"{x + a:g},{y + b:g}" for a, b in d)
      + f'" fill="{col}"/>')


def nodo(x, y, col):
    A(f'<circle cx="{x:g}" cy="{y:g}" r="1.0" fill="{col}"/>')


def scavalco(x, y, col_colonna):
    """Due linee che si incrociano e NON si uniscono: la colonna passa intera."""
    A(f'<circle cx="{x:g}" cy="{y:g}" r="1.9" fill="#ffffff" stroke="none"/>')
    linea([(x, y - 2.1), (x, y + 2.1)], col_colonna, 1.5)


A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" '
  f'viewBox="0 0 {W:g} {H:g}"><rect width="{W:g}" height="{H:g}" fill="#ffffff"/>')

testo(18, 20, "B12 — il pettine, e dove l&#8217;impianto 5 non ci sta", 7.4, NERO, "bold")
testo(18, 27.5,
      "Figura di spiegazione. Non &#232; una tavola e non fa convenzione grafica (D-165). "
      "Rosso = mandata, blu = ritorno. Ogni utenza si prende da un lato solo (D-167).",
      3.2, GRIGIO)

for x0 in (18.0, 216.0):
    A(f'<rect x="{x0:g}" y="36" width="186" height="176" fill="none" '
      f'stroke="#d5d8dc" stroke-width="0.5"/>')

testo(26, 46, "A &#183; IL PETTINE — come l&#8217;hai disegnato tu", 4.5, NERO, "bold")
testo(26, 51.5, "due colonne, e bastano", 3.1, GRIGIO, corsivo="italic")
testo(224, 46, "B &#183; L&#8217;IMPIANTO 5 — come &#232; nel grafo", 4.5, NERO, "bold")
testo(224, 51.5, "le colonne diventano tre", 3.1, GRIGIO, corsivo="italic")


def volano(x):
    A(f'<rect x="{x:g}" y="58" width="26" height="30" rx="2" fill="#ffffff" '
      f'stroke="{NERO}" stroke-width="0.5"/>')
    testo(x + 13, 72, "VOLANO", 3.1, NERO, "bold", "middle")
    testo(x + 13, 77.5, "secondario", 2.8, GRIGIO, anchor="middle")


QUOTE = (98.0, 134.0, 170.0)        # il bordo alto di ciascuna utenza
FONDO_MANDATA = 174.0               # dove la colonna della mandata finisce
WU, HU = 34.0, 15.0

# ============================================================== PANNELLO A
volano(28)
XS, XR, XU = 90.0, 76.0, 144.0
linea([(54, 63), (XS, 63), (XS, 174)], ROSSO, 1.5)
freccia(XS, 128, "giu", ROSSO)
linea([(XR, 180), (XR, 76), (54, 76)], BLU, 1.5)
freccia(XR, 128, "su", BLU)

for i, y in enumerate(QUOTE):
    scatola(XU, y, WU, HU, f"{i + 1}&#170; utenza")
    linea([(XS, y + 4), (XU, y + 4)], ROSSO, 0.9)
    freccia(XU - 0.5, y + 4, "dx", ROSSO)
    nodo(XS, y + 4, ROSSO)
    linea([(XU, y + 10), (XR, y + 10)], BLU, 0.9)
    freccia(XR + 0.5, y + 10, "sx", BLU)
    nodo(XR, y + 10, BLU)
    if y + 10 < FONDO_MANDATA:
        scavalco(XS, y + 10, ROSSO)

testo(XU + WU / 2, 93, "la coppia corre affiancata fino all&#8217;utenza", 2.9, GRIGIO,
      anchor="middle")
testo(76, 196, "1 &#8594; 2 &#8594; 3 sulla mandata", 3.2, ROSSO, "bold")
testo(76, 202, "1 &#8594; 2 &#8594; 3 sul ritorno", 3.2, BLU, "bold")
testo(76, 208.5, "stesso ordine: due colonne bastano", 3.2, NERO, "bold")

# ============================================================== PANNELLO B
volano(226)
XS2, XR2, XE, XU2 = 288.0, 274.0, 262.0, 342.0
nomi = (("batteria UTA", "1&#170; sulla mandata"),
        ("ventilconvettori", "2&#170; sulla mandata"),
        ("pavimento radiante", "3&#170; sulla mandata"))

linea([(252, 63), (XS2, 63), (XS2, 174)], ROSSO, 1.5)
freccia(XS2, 128, "giu", ROSSO)
linea([(XR2, 144), (XR2, 76), (252, 76)], BLU, 1.5)
freccia(XR2, 110, "su", BLU)
linea([(XU2, 180), (XE, 180), (XE, 82), (XR2, 82)], BLU, 1.5)
freccia(XE, 130, "su", BLU)
nodo(XR2, 82, BLU)

for i, y in enumerate(QUOTE):
    scatola(XU2, y, WU, HU, nomi[i][0], nomi[i][1])
    linea([(XS2, y + 4), (XU2, y + 4)], ROSSO, 0.9)
    freccia(XU2 - 0.5, y + 4, "dx", ROSSO)
    nodo(XS2, y + 4, ROSSO)
    if i < 2:
        linea([(XU2, y + 10), (XR2, y + 10)], BLU, 0.9)
        freccia(XR2 + 0.5, y + 10, "sx", BLU)
        nodo(XR2, y + 10, BLU)
        if y + 10 < FONDO_MANDATA:
            scavalco(XS2, y + 10, ROSSO)

A(f'<rect x="{XE - 5.5:g}" y="78" width="11" height="106" fill="none" '
  f'stroke="{AMBRA}" stroke-width="0.6" stroke-dasharray="3 2" rx="3"/>')
testo(XE, 191, "la terza verticale", 3.1, AMBRA, "bold", "middle")
testo(XE, 196, "il ritorno del radiante", 2.9, AMBRA, anchor="middle")
testo(XE, 200.5, "risale da solo", 2.9, AMBRA, anchor="middle")
testo(XU2 - 4, 186, "e la sua coppia si apre subito", 2.9, AMBRA, anchor="end")

testo(300, 196, "1 &#8594; 2 &#8594; 3 sulla mandata", 3.2, ROSSO, "bold")
testo(300, 202, "3 &#8594; 1 &#8594; 2 sul ritorno", 3.2, BLU, "bold")
testo(300, 208.5, "ordine rovesciato: una colonna in pi&#249;", 3.2, AMBRA, "bold")

# ============================================================== la didascalia
A('<line x1="18" y1="220" x2="402" y2="220" stroke="#d5d8dc" stroke-width="0.5"/>')
testo(18, 228, "La differenza, in una riga.", 3.9, NERO, "bold")
blocco(18, 234.5, [
    "Nel pettine la mandata incontra le utenze nell&#8217;ordine 1-2-3 e il ritorno",
    "le raccoglie nello stesso ordine: due colonne bastano. Nell&#8217;impianto 5 la",
    "mandata serve il radiante per ultimo e il ritorno lo raccoglie per primo,",
    "attaccato al volano. Il suo ritorno deve risalire tutta la colonna, e per non",
    "passare addosso al nodo che raccoglie UTA e ventilconvettori si prende",
    "una terza verticale.",
])
testo(216, 228, "La domanda, ed &#232; tua: &#232; contenuto MEP.", 3.9, NERO, "bold")
blocco(216, 234.5, [
    "Primo sulla mandata = ultimo sul ritorno &#232; la firma di un ritorno invertito",
    "(Tichelmann), che pareggia le lunghezze dei circuiti: &#232; una scelta vera.",
    "Se &#232; voluta, la terza colonna &#232; giusta e B12 prende un&#8217;eccezione scritta.",
    "Se invece il radiante va alimentato per primo — com&#8217;&#232; nella tua tavola 5,",
    "dove sta in alto vicino al volano, con la sua miscelatrice — allora &#232; il grafo",
    "a sbagliare l&#8217;ordine: si corregge, e il pettine si chiude con due colonne.",
])

A("</svg>")
open("/tmp/claude-0/fig/b12.svg", "w", encoding="utf-8").write("\n".join(out))
print("scritto")
