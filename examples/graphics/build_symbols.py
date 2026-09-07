"""Genera la libreria dei simboli pubblicati.

Trentuno simboli su quattro domini (idronico, aeraulico, refrigerante, gas),
con porte sul perimetro, faccia coerente con il lato e **ogni coordinata su un
nodo della griglia** da 2,5 mm: senza quest'ultima proprieta' l'instradamento
ortogonale non raggiunge nessun attacco (D-054).

## Le fonti

Nessuna forma e' inventata (D-067, D-081). Dove la UNI 9511 copre il segno —
valvolame (Tab. 3), apparecchi indicatori (Tab. 10), vasi di espansione — il
corpo riproduce la riga della tavola e il manifesto la dichiara nel campo
`source` («UNI 9511 Tab. 3, tramite SRC-016»; le tavole sono fonti secondarie,
mai la norma direttamente). Le macchine e gli accessori che la norma non copre
— pompa di calore, accumuli, circolatore, collettore, separatori — seguono la
pratica di settore consolidata negli schemi dei produttori («pratica di
settore, cfr. SRC-008»). Il registro delle fonti e'
docs/research/SOURCE_REGISTER.md.

## La gerarchia dimensionale

In una tavola tecnica la taglia di un simbolo comunica il peso del componente
nell'impianto: una valvola si disegna piccola, un accumulo grande. D-050
registrava le taglie uniformi della prima libreria come convenzione di prova;
questa e' la gerarchia che le sostituisce (D-055).

    accessorio in linea     5 x 5       2 x 2 passi
    accessorio terminale    5 x 10      2 x 4
    apparecchio            10 x 10      4 x 4
    terminale              20 x 15      8 x 6
    collettore             40 x 5      16 x 2
    vaso                   10 x 15      4 x 6
    compensatore         12,5 x 25      5 x 10
    macchina               40 x 30     16 x 12
    accumulo               25 x 45     10 x 18

Le proporzioni sono misurate su una tavola di riferimento fornita dal PM: una
macchina sta a una valvola come **6 a 1** in misura lineare, trentasei a uno in
area. La gerarchia precedente le teneva a 3 a 1, e il risultato non si leggeva
come uno schema: sembravano tutti componenti dello stesso peso.

Ogni lato e' un multiplo del passo. Il lato su cui una porta e' **centrata** e'
un numero **pari** di passi, cosi' il centro cade su un nodo. E' il vincolo che
decide le taglie: 7,5 x 7,5 sarebbe stata una misura ragionevole per un
apparecchio, ma tre passi sono dispari e la porta centrata sarebbe caduta fra
due nodi.

## I corpi

Ogni corpo SVG e' un frammento senza radice `<svg>`, disegnato in coordinate
locali in millimetri con l'origine nell'angolo in alto a sinistra del riquadro.
Lo spessore e il colore del tratto sono decisi dal foglio che ospita il simbolo:
un corpo non dichiara mai il proprio `stroke`. Un `fill` compare solo dove
rappresenta una parte davvero piena (la girante di un circolatore, il fondello
di raccolta di un defangatore, il punto di giunzione di una derivazione).

I corpi sono **disegnati in funzione del riquadro**, non scritti come
coordinate fisse: cambiare una taglia della gerarchia non puo' cosi' lasciare
un disegno fuori dal proprio box.

## I segni corretti da DRAW-005

La matrice PM del 5 settembre 2026 (`docs/pm/2026-09-05-audit-simboli-e-contenuto-tavola1.md`)
fissa per i simboli critici della tavola 1: il filtro a Y nella forma classica,
con ramo inclinato e gambo che non sale mai sopra l'asse; la freccia del
confine di rete come **glifo di verso** dichiarato, che il renderer punta nel
verso locale dell'acqua; le lettere di manometro e termometro come **glifi
leggibili**, contro-ruotati dal registro; l'interasse di quindici millimetri
fra mandata e ritorno della pompa di calore; e tre riserve con tre corpi —
puffer, bollitore, accumulo combinato — in cui chi attraversa la riserva senza
mescolarsi lo fa in un serpentino continuo e chi entra nel volume tocca il
mantello.

Rieseguire questo script deve produrre file bit per bit identici.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import SymbolManifest

REPO_ROOT = Path(__file__).resolve().parents[2]
SYMBOLS_DIR = REPO_ROOT / "assets" / "symbols"

VERSION = "1.0.0"

# Orientamenti in cui un simbolo puo' essere disegnato in un impianto reale.
# E' un vincolo tecnico, non geometrico (D-049).
ALLOWED_ROTATIONS_DEG = [0, 90, 180, 270]
AIR_VENT_ROTATIONS_DEG = [0]
"""Uno sfiato d'aria automatico scarica verso l'alto."""
EXPANSION_VESSEL_ROTATIONS_DEG = [0, 180]
"""Un vaso di espansione a membrana si disegna in piedi."""
UPRIGHT_ROTATIONS_DEG = [0]
"""Accumuli e macchine si disegnano nel proprio verso: coricarli non aiuta a leggere."""
STRAINER_ROTATIONS_DEG = [0, 270]
"""Un filtro a Y ha il gambo in basso, in ogni rotazione ammessa (DRAW-005, I-031).

Il ramo inclinato scende dall'asse verso il basso a sinistra: a 0 gradi punta
in basso, a 270 — la rotazione che lo posa su una tubazione verticale — in
basso a destra. A 90 e a 180 il gambo salirebbe sopra l'asse, e un cestello
che pesca in alto non raccoglie niente: quelle due non si ammettono."""

CLEARANCE_MM = A3_LANDSCAPE.min_clearance_mm
GRID_MM = A3_LANDSCAPE.grid_mm

# La gerarchia dimensionale (D-055). Ogni misura e' un multiplo del passo.
INLINE_ACCESSORY = (5.0, 5.0)
TERMINAL_ACCESSORY = (5.0, 10.0)
BRANCHED_ACCESSORY = (5.0, 10.0)
"""Accessorio che sta **sulla** tubazione ma pende da una derivazione.

Un vaso di espansione, una valvola di sicurezza, uno scarico: il fluido non ci
passa attraverso, ci arriva da uno stacco. Sul modello restano componenti in
linea a due porte — la derivazione fa parte del corpo del simbolo, come la
convenzione dei compositi permette (CONV-GRAFICA-002) — perche' un vero ramo
richiederebbe un raccordo a T come componente a se', e a quel punto ogni
accessorio pesa tre pezzi invece di uno. Il riquadro e' alto il doppio del
proprio passo di attacco, cosi' la derivazione ha dove stare.
"""
DEVICE = (10.0, 10.0)
TERMINAL = (20.0, 15.0)
MANIFOLD = (40.0, 5.0)
VESSEL = (10.0, 15.0)
SEPARATOR = (12.5, 25.0)
MACHINE = (40.0, 30.0)
STORAGE = (25.0, 45.0)

# Le fonti dichiarate nel campo `source` di ogni manifesto (D-067, D-081).
# La UNI 9511 si cita sempre tramite la fonte secondaria verificata, mai da sola.
SOURCE_UNI_TAB1 = "UNI 9511 Tab. 1, tramite SRC-016"
"""Tubazioni e loro giunzioni: tavola 1. E' li' che derivazione e incrocio si
distinguono, la prima col cerchio pieno e il secondo con la croce nuda."""
SOURCE_UNI_TAB3 = "UNI 9511 Tab. 3, tramite SRC-016"
"""Valvolame: tavola 3 della norma, pubblicata da Oppo (SRC-016)."""
SOURCE_UNI_TAB10 = "UNI 9511 Tab. 10, tramite SRC-016"
"""Apparecchi indicatori: lettera in un cerchio, tavola 10 (SRC-016)."""
SOURCE_UNI_VESSELS = "UNI 9511, tramite SRC-015"
"""Vasi di espansione: segni della norma riprodotti nel materiale di SRC-015."""
SOURCE_UNI_EXCHANGERS = "UNI 9511, tramite SRC-015"
"""Scambiatori: segni della norma riprodotti nel materiale di SRC-015."""
SOURCE_PRACTICE_HYDRONIC = "pratica di settore, cfr. SRC-008"
"""Macchine e accessori idronici fuori norma: schemi dei produttori (Caleffi)."""
SOURCE_PRACTICE_PENDING = (
    "pratica di settore — fonte puntuale da acquisire col dominio (DEFERRED §5)"
)
"""Domini fuori MVP (aeraulico, gas, refrigerante): la forma e' di pratica
comune ma nessuna fonte acquisita la documenta ancora. La stringa lo dice,
il rinvio e' registrato: vietato inventare vale anche per le citazioni
(D-083), e un puntatore a un documento non verificato sarebbe inventato."""


def n(value: float) -> str:
    """Numero stabile nel testo SVG: nessuna coda in virgola mobile."""
    return f"{round(value, 4):g}"


def face_center(face: str, width_mm: float, height_mm: float) -> tuple[float, float]:
    return {
        "left": (0.0, height_mm / 2),
        "right": (width_mm, height_mm / 2),
        "top": (width_mm / 2, 0.0),
        "bottom": (width_mm / 2, height_mm),
    }[face]


def port(port_id: str, face: str, width_mm: float, height_mm: float) -> dict[str, Any]:
    x_mm, y_mm = face_center(face, width_mm, height_mm)
    return {"id": port_id, "face": face, "x_mm": x_mm, "y_mm": y_mm}


def port_at(port_id: str, face: str, along_mm: float, width_mm: float, height_mm: float) -> dict[str, Any]:
    """Porta su una faccia, a una posizione scelta invece che al centro."""
    coordinate = {
        "left": (0.0, along_mm),
        "right": (width_mm, along_mm),
        "top": (along_mm, 0.0),
        "bottom": (along_mm, height_mm),
    }[face]
    return {"id": port_id, "face": face, "x_mm": coordinate[0], "y_mm": coordinate[1]}


def keep_out(ports: list[dict[str, Any]], clearance_mm: float = CLEARANCE_MM) -> dict[str, float]:
    """Area di rispetto sui lati che portano una porta, derivata dalle porte."""
    faces = {item["face"] for item in ports}
    return {
        f"{side}_mm": clearance_mm if side in faces else 0.0
        for side in ("left", "right", "top", "bottom")
    }


FITTING_CLEARANCE_MM = 0.5
"""L'area di rispetto di un raccordo (D-119): mezzo millimetro.

Un raccordo e' un punto della tubazione, non un apparecchio, e non c'e' niente
da cui tenersi distanti. Il riquadro resta 5 x 5, perche' i tre attacchi devono
cadere su nodi della griglia (D-054): cio' che si toglie e' il rispetto, non il
segno. Portato qui dal manifesto committato: il segno era stato corretto a mano,
e il generatore lo rigenerava com'era prima."""

SOURCE_UNI_TAB1_FITTING = (
    "UNI 9511 Tab. 1, tramite SRC-016 — area di rispetto azzerata (D-119b): un "
    "raccordo e' un punto della tubazione, non un apparecchio, e non c'e' niente da "
    "cui tenersi distanti. Il segno disegnato e' un punto di due decimi di "
    "millimetro: chi guarda vede le linee dividersi e sa che li' c'e' un T"
)
"""La fonte dei raccordi, con la decisione che ne ha ridotto il rispetto."""

SOURCE_UNI_CHECK_VALVE = (
    "UNI 9511 Tab. 3 «valvola di non ritorno», tramite SRC-016, e la parola del PM "
    "che l'ha respinta due volte: «una sorta di z di fianco con freccia sopra». Il "
    "segno e' una **z** — barra alta, diagonale, barra bassa — con la freccia del "
    "senso del flusso sopra. La versione precedente provava a farla con due "
    "barrette VERTICALI unite da una diagonale: sulla carta non legge come una z, "
    "legge come una N storta, ed e' quella che il PM ha visto e respinto. Il segno "
    "e' stato guardato rasterizzato prima di scriverlo, non descritto a memoria: e' "
    "la stessa lezione di I-004, applicata anche al proprio disegno e non solo alle "
    "fonti altrui"
)
"""La fonte del ritegno, con la decisione che ne ha rifatto il segno (D-122)."""


# ---------------------------------------------------------------------------
# Corpi, disegnati in funzione del riquadro.
# ---------------------------------------------------------------------------


def stubs_horizontal(w: float, h: float, inset: float) -> str:
    """I due monconi d'attacco, da bordo a bordo verso il corpo centrale."""
    y = h / 2
    return (
        f'<line x1="0" y1="{n(y)}" x2="{n(inset)}" y2="{n(y)}"/>'
        f'<line x1="{n(w - inset)}" y1="{n(y)}" x2="{n(w)}" y2="{n(y)}"/>'
    )


def valve_isolation_body(w: float, h: float) -> str:
    """Segno generale del valvolame (UNI 9511 Tab. 3): due triangoli chiusi
    che si toccano al vertice, senza riempimento."""
    inset = w / 6
    left, right = inset, w - inset
    cx, cy = w / 2, h / 2
    top, bottom = h * 0.1, h * 0.9
    return (
        stubs_horizontal(w, h, inset)
        + f'<path d="M{n(left)} {n(top)} L{n(left)} {n(bottom)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(right)} {n(top)} L{n(right)} {n(bottom)} L{n(cx)} {n(cy)} Z"/>'
    )


def valve_check_body(w: float, h: float) -> str:
    """Valvola di non ritorno (UNI 9511 Tab. 3, D-122): una **z** — barra alta,
    diagonale, barra bassa — con la freccia del senso del flusso sopra.

    E' il segno che il PM ha approvato dopo averlo visto rasterizzato; il
    generatore lo riproduce dal manifesto committato, che era stato corretto a
    mano (DRAW-005)."""
    inset = w / 5
    left, right = inset, w - inset
    top, bottom = h * 0.24, h * 0.76
    arrow_y = h * 0.06
    tail, head = w * 0.28, w * 0.72
    barb = w * 0.12
    return (
        stubs_horizontal(w, h, inset)
        + f'<line x1="{n(left)}" y1="{n(top)}" x2="{n(right)}" y2="{n(top)}"/>'
        f'<line x1="{n(right)}" y1="{n(top)}" x2="{n(left)}" y2="{n(bottom)}"/>'
        f'<line x1="{n(left)}" y1="{n(bottom)}" x2="{n(right)}" y2="{n(bottom)}"/>'
        f'<line x1="{n(tail)}" y1="{n(arrow_y)}" x2="{n(head)}" y2="{n(arrow_y)}"/>'
        f'<line x1="{n(head)}" y1="{n(arrow_y)}" '
        f'x2="{n(head - barb)}" y2="{n(arrow_y - barb / 2)}"/>'
        f'<line x1="{n(head)}" y1="{n(arrow_y)}" '
        f'x2="{n(head - barb)}" y2="{n(arrow_y + barb / 2)}"/>'
    )


def strainer_body(w: float, h: float) -> str:
    """Filtro a Y, nella forma classica (DRAW-005, I-031): la linea passa
    dritta fra le due porte, dal centro scende il **ramo inclinato** a
    quarantacinque gradi verso il basso a sinistra — il lato da cui l'acqua
    arriva — e in fondo al ramo sta il **gambo**, il tappo del cestello,
    perpendicolare al ramo. La Y si legge cosi', e il segno precedente — un
    triangolo a V sotto la linea — non era mai stato approvato dal PO."""
    y = h / 2
    cx = w / 2
    reach = min(w, h) * 0.32
    tip_x, tip_y = cx - reach, y + reach
    cap = min(w, h) * 0.1 / 2**0.5
    return (
        f'<line x1="0" y1="{n(y)}" x2="{n(w)}" y2="{n(y)}"/>'
        f'<line x1="{n(cx)}" y1="{n(y)}" x2="{n(tip_x)}" y2="{n(tip_y)}"/>'
        f'<line x1="{n(tip_x - cap)}" y1="{n(tip_y - cap)}" '
        f'x2="{n(tip_x + cap)}" y2="{n(tip_y + cap)}"/>'
    )


def pump_body(w: float, h: float) -> str:
    """Circolatore della pratica italiana: cerchio con il triangolo pieno
    inscritto, il vertice nel verso del flusso (dalla porta a alla b)."""
    inset = w / 5
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.3
    half = r * 0.866
    return (
        stubs_horizontal(w, h, inset)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<path d="M{n(cx - r / 2)} {n(cy - half)} '
        f'L{n(cx - r / 2)} {n(cy + half)} L{n(cx + r)} {n(cy)} Z" fill="black"/>'
    )


def fan_body(w: float, h: float) -> str:
    """Stessa macchina rotante, ma con l'elica a tre pale: aria, non liquido."""
    inset = w / 5
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.3
    return (
        stubs_horizontal(w, h, inset)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - r * 0.75)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx - r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
    )


def gas_meter_body(w: float, h: float) -> str:
    """Quadrante di misura: cerchio, indice e perno pieno."""
    inset = w / 5
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.29
    return (
        stubs_horizontal(w, h, inset)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + r * 0.7)}" y2="{n(cy - r * 0.55)}"/>'
        f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 0.15)}" fill="black"/>'
    )


def duct_damper_body(w: float, h: float) -> str:
    """Tronchetto di canale con la lama vista semi-aperta."""
    inset = w / 6
    box_x, box_y = inset, h * 0.1
    box_w, box_h = w - 2 * inset, h * 0.8
    return (
        stubs_horizontal(w, h, inset)
        + f'<rect x="{n(box_x)}" y="{n(box_y)}" width="{n(box_w)}" height="{n(box_h)}"/>'
        f'<line x1="{n(box_x + box_w * 0.15)}" y1="{n(box_y + box_h * 0.15)}" '
        f'x2="{n(box_x + box_w * 0.85)}" y2="{n(box_y + box_h * 0.85)}"/>'
    )


def air_diffuser_body(w: float, h: float) -> str:
    """Collarino con le diagonali incrociate: bocchetta vista in pianta."""
    stub = w * 0.2
    x, y = stub, h * 0.12
    bw, bh = w - stub - w * 0.08, h * 0.76
    return (
        f'<line x1="0" y1="{n(h / 2)}" x2="{n(stub)}" y2="{n(h / 2)}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x + bw)}" y2="{n(y + bh)}"/>'
        f'<line x1="{n(x)}" y1="{n(y + bh)}" x2="{n(x + bw)}" y2="{n(y)}"/>'
    )


def air_vent_body(w: float, h: float) -> str:
    """Bulbo su stelo con il tappo di sfiato sopra. La porta e' in basso."""
    cx = w / 2
    return (
        f'<line x1="{n(cx)}" y1="{n(h)}" x2="{n(cx)}" y2="{n(h * 0.62)}"/>'
        f'<circle cx="{n(cx)}" cy="{n(h * 0.42)}" r="{n(w * 0.34)}"/>'
        f'<line x1="{n(cx - w * 0.3)}" y1="{n(h * 0.14)}" '
        f'x2="{n(cx + w * 0.3)}" y2="{n(h * 0.14)}"/>'
    )


def expansion_vessel_body(w: float, h: float) -> str:
    """Vaso chiuso a membrana (UNI 9511): capsula con il diaframma
    orizzontale a meta'. La porta e' in alto."""
    cx = w / 2
    x, y = w * 0.15, h * 0.18
    bw, bh = w * 0.7, h * 0.75
    return (
        f'<line x1="{n(cx)}" y1="0" x2="{n(cx)}" y2="{n(y)}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}" '
        f'rx="{n(bw * 0.25)}"/>'
        f'<line x1="{n(x)}" y1="{n(y + bh / 2)}" '
        f'x2="{n(x + bw)}" y2="{n(y + bh / 2)}"/>'
    )


def refrigerant_branch_body(w: float, h: float) -> str:
    """Derivazione a T con il punto di giunzione pieno."""
    cx, cy = w / 2, h / 2
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(h)}"/>'
        f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(min(w, h) * 0.075)}" fill="black"/>'
    )



# --- famiglie richieste dagli impianti di prova del committente --------------
# Ognuna e' **dato**: un corpo, una scheda, e nessuna riga di programma. Se per
# aggiungere una famiglia servisse toccare il motore, il motore sarebbe
# sbagliato (ADR 0005).


def gas_boiler_body(w: float, h: float, ports: list[dict[str, Any]]) -> str:
    """Caldaia murale: involucro, camera di combustione e la fiamma."""
    x, y = w * 0.06, h * 0.1
    bw, bh = w * 0.88, h * 0.8
    fx, fy = w * 0.5, h * 0.66
    r = h * 0.13
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}" rx="{n(h * 0.05)}"/>'
        f'<rect x="{n(x + bw * 0.18)}" y="{n(y + bh * 0.12)}" '
        f'width="{n(bw * 0.64)}" height="{n(bh * 0.3)}"/>'
        f'<path d="M{n(fx)} {n(fy - r)} Q{n(fx + r * 0.8)} {n(fy)} {n(fx)} {n(fy + r)} '
        f'Q{n(fx - r * 0.8)} {n(fy)} {n(fx)} {n(fy - r)} Z"/>'
        + stubs_to_ports(ports, w, h, w * 0.06)
    )


def plate_exchanger_body(w: float, h: float, ports: list[dict[str, Any]]) -> str:
    """Scambiatore a piastre: il riquadro con le piastre a zig-zag in mezzo."""
    x, y = w * 0.16, h * 0.1
    bw, bh = w * 0.68, h * 0.8
    steps = 6
    plates = "".join(
        f'<line x1="{n(x + bw * (index + 0.5) / steps)}" y1="{n(y + bh * 0.12)}" '
        f'x2="{n(x + bw * (index + 0.5) / steps)}" y2="{n(y + bh * 0.88)}"/>'
        for index in range(steps)
    )
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        + plates
        + stubs_to_ports(ports, w, h, x)
    )


def coil_body(w: float, h: float) -> str:
    """Batteria alettata idronica: il riquadro con la serpentina che lo attraversa."""
    x, y = w * 0.12, h * 0.18
    bw, bh = w * 0.76, h * 0.64
    turns = 4
    step = bw / turns
    path = f"M{n(x)} {n(y + bh / 2)} "
    for index in range(turns):
        top = y + bh * (0.2 if index % 2 == 0 else 0.8)
        path += f"L{n(x + step * (index + 0.5))} {n(top)} "
    path += f"L{n(x + bw)} {n(y + bh / 2)}"
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<path d="{path}"/>'
        + stubs_horizontal(w, h, x)
    )


def stubs_to_ports(ports: list[dict[str, Any]], w: float, h: float, inset: float) -> str:
    """Un moncone da ogni porta verso l'interno del riquadro.

    Disegnato **dalle porte**, non da quote ripetute a mano: e' l'unico modo
    perche' il corpo raggiunga davvero gli attacchi che il manifesto dichiara,
    qualunque sia la taglia del riquadro.
    """
    segments = []
    for item in ports:
        x, y = item["x_mm"], item["y_mm"]
        target = {
            "left": (inset, y),
            "right": (w - inset, y),
            "top": (x, inset),
            "bottom": (x, h - inset),
        }[item["face"]]
        segments.append(
            f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(target[0])}" y2="{n(target[1])}"/>'
        )
    return "".join(segments)


def heat_pump_body(w: float, h: float, ports: list[dict[str, Any]]) -> str:
    """Macchina esterna: involucro, ventilatore e batteria alettata."""
    x, y = w * 0.06, h * 0.1
    bw, bh = w * 0.88, h * 0.8
    cx, cy = x + bw * 0.34, y + bh / 2
    r = bh * 0.3
    fins = "".join(
        f'<line x1="{n(x + bw * (0.62 + i * 0.09))}" y1="{n(y + bh * 0.15)}" '
        f'x2="{n(x + bw * (0.62 + i * 0.09))}" y2="{n(y + bh * 0.85)}"/>'
        for i in range(4)
    )
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - r * 0.75)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx - r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
        + fins
        + stubs_to_ports(ports, w, h, w * 0.06)
    )


def _shell_of(w: float, h: float) -> tuple[float, float, float, float]:
    """Il mantello di una riserva: x, y, larghezza e altezza nel riquadro."""
    return w * 0.14, h * 0.06, w * 0.72, h * 0.88


def stubs_into_the_shell(ports: list[dict[str, Any]], w: float, h: float) -> str:
    """Un moncone da ogni porta **fino al mantello**: l'attacco entra nel volume.

    Disegnato dalle porte, come `stubs_to_ports`, ma il capo interno sta sul
    mantello e non a una quota fissa: e' cosi' che si legge che quell'attacco
    comunica col volume (DRAW-005, I-036).
    """
    x, y, bw, bh = _shell_of(w, h)
    segments = []
    for item in ports:
        px, py = item["x_mm"], item["y_mm"]
        target = {
            "left": (x, py),
            "right": (x + bw, py),
            "top": (px, y),
            "bottom": (px, y + bh),
        }[item["face"]]
        segments.append(
            f'<line x1="{n(px)}" y1="{n(py)}" x2="{n(target[0])}" y2="{n(target[1])}"/>'
        )
    return "".join(segments)


def coil_between(
    entry: dict[str, Any], exit: dict[str, Any], w: float, h: float, rows: int
) -> str:
    """Il serpentino: **un tracciato solo** dall'attacco d'ingresso a quello
    d'uscita, che entra nel mantello, vi gira avanti e indietro, e ne esce.

    E' il segno che dice che quel fluido attraversa la riserva scambiando
    calore senza mescolarsi (DRAW-005, I-036): l'acqua fredda che diventa
    sanitaria nell'accumulo combinato, l'acqua tecnica che scalda il
    bollitore. Un serpentino tracciato a pezzi non si legge come tale.
    """
    x, y, bw, bh = _shell_of(w, h)
    left, right = x + bw * 0.2, x + bw * 0.8
    top_row, bottom_row = y + bh * 0.2, y + bh * 0.84
    entry_y, exit_y = entry["y_mm"], exit["y_mm"]
    points: list[tuple[float, float]] = [(entry["x_mm"], entry_y)]
    if entry["face"] == "left":
        points.append((left, entry_y))
        start_y = entry_y
    else:
        points.append((entry["x_mm"], top_row))
        start_y = top_row
    if exit["face"] == "top":
        end_y = top_row
    elif exit["face"] == "left":
        end_y = exit_y
    else:
        end_y = bottom_row
    span = (end_y - start_y) / rows
    here_x = left
    row_y = start_y
    for index in range(rows):
        other = right if here_x == left else left
        points.append((other, row_y))
        here_x = other
        if index < rows - 1:
            row_y += span
            points.append((here_x, row_y))
    if exit["face"] == "top":
        points.append((exit["x_mm"], row_y))
        points.append((exit["x_mm"], y))
    elif exit["face"] == "left":
        points.append((left, end_y))
        points.append((exit["x_mm"], end_y))
    else:
        points.append((exit["x_mm"], row_y))
        points.append((exit["x_mm"], y + bh))
    points.append((exit["x_mm"], exit["y_mm"]))
    tidy: list[tuple[float, float]] = []
    for point in points:
        if not tidy or (n(tidy[-1][0]), n(tidy[-1][1])) != (n(point[0]), n(point[1])):
            tidy.append(point)
    d = "M" + " L".join(f"{n(px)} {n(py)}" for px, py in tidy)
    return (
        f'<path class="coil" data-from="{entry["id"]}" data-to="{exit["id"]}" d="{d}"/>'
    )


def reserve_body(
    w: float,
    h: float,
    ports: list[dict[str, Any]],
    coil: tuple[str, str] | None = None,
    rows: int = 5,
) -> str:
    """Una riserva: il mantello, gli attacchi che entrano nel volume e, se un
    fluido la attraversa senza mescolarsi, il suo serpentino.

    Tre riserve, tre corpi (DRAW-005, I-036): il **puffer** ha il solo volume
    di acqua tecnica e nessun serpentino; il **bollitore** tiene in serbo acqua
    sanitaria, e il serpentino tecnico che lo scalda va dal proprio ingresso al
    proprio ritorno; l'**accumulo combinato** tiene in serbo acqua tecnica, e il
    serpentino sanitario va dall'ingresso dell'acqua fredda all'uscita
    dell'acqua calda. Quale coppia di attacchi sia il serpentino lo dice il
    catalogo — i fluidi diversi da quello tenuto in serbo — e qui si scrive per
    nome soltanto perche' questo generatore non legge il catalogo.
    """
    x, y, bw, bh = _shell_of(w, h)
    shell = (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}" '
        f'rx="{n(bw * 0.18)}"/>'
    )
    by_id = {item["id"]: item for item in ports}
    through = set(coil or ())
    stubs = stubs_into_the_shell([item for item in ports if item["id"] not in through], w, h)
    if coil is None:
        return shell + stubs
    return shell + coil_between(by_id[coil[0]], by_id[coil[1]], w, h, rows) + stubs


def diverting_valve_body(w: float, h: float) -> str:
    """Valvola a tre vie (UNI 9511 Tab. 3): tre triangoli chiusi che
    convergono al centro — sinistra, destra e terza via in basso."""
    cx, cy = w / 2, h / 2
    d = min(w, h) * 0.28
    s = d * 0.8
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(cx - d)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx + d)}" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy + d)}" x2="{n(cx)}" y2="{n(h)}"/>'
        f'<path d="M{n(cx - d)} {n(cy - s)} L{n(cx - d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(cx + d)} {n(cy - s)} L{n(cx + d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(cx - s)} {n(cy + d)} L{n(cx + s)} {n(cy + d)} L{n(cx)} {n(cy)} Z"/>'
    )


def manifold_body(w: float, h: float, outlets: tuple[float, ...]) -> str:
    """Collettore: un corpo orizzontale con gli stacchi verso il basso."""
    y = h / 2
    drops = "".join(
        f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x)}" y2="{n(h)}"/>' for x in outlets
    )
    return (
        f'<rect x="0" y="{n(h * 0.2)}" width="{n(w)}" height="{n(h * 0.6)}" '
        f'rx="{n(h * 0.3)}"/>' + drops
    )


def radiator_body(w: float, h: float) -> str:
    """Radiatore: gli elementi in vista frontale."""
    x, y = w * 0.1, h * 0.15
    bw, bh = w * 0.8, h * 0.7
    elements = "".join(
        f'<line x1="{n(x + bw * frac)}" y1="{n(y)}" x2="{n(x + bw * frac)}" y2="{n(y + bh)}"/>'
        for frac in (0.2, 0.4, 0.6, 0.8)
    )
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        + elements
        + f'<line x1="0" y1="{n(h / 2)}" x2="{n(x)}" y2="{n(h / 2)}"/>'
        f'<line x1="{n(x + bw)}" y1="{n(h / 2)}" x2="{n(w)}" y2="{n(h / 2)}"/>'
    )


def underfloor_body(w: float, h: float) -> str:
    """Pannello radiante: la serpentina dentro il proprio riquadro."""
    x, y = w * 0.1, h * 0.15
    bw, bh = w * 0.8, h * 0.7
    path = [f"M{n(x + bw * 0.08)} {n(y + bh * 0.9)}"]
    for i in range(4):
        top = y + bh * 0.1
        bottom = y + bh * 0.9
        left = x + bw * (0.08 + i * 0.28)
        path.append(f"L{n(left)} {n(top)} L{n(left + bw * 0.14)} {n(top)} "
                    f"L{n(left + bw * 0.14)} {n(bottom)}")
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<path d="{" ".join(path)}"/>'
        f'<line x1="0" y1="{n(h / 2)}" x2="{n(x)}" y2="{n(h / 2)}"/>'
        f'<line x1="{n(x + bw)}" y1="{n(h / 2)}" x2="{n(w)}" y2="{n(h / 2)}"/>'
    )


def fan_coil_body(w: float, h: float) -> str:
    """Ventilconvettore: batteria alettata piu' ventilatore."""
    x, y = w * 0.1, h * 0.15
    bw, bh = w * 0.8, h * 0.7
    fins = "".join(
        f'<line x1="{n(x + bw * frac)}" y1="{n(y)}" x2="{n(x + bw * frac)}" y2="{n(y + bh)}"/>'
        for frac in (0.15, 0.3, 0.45)
    )
    cx, cy = x + bw * 0.75, y + bh / 2
    r = bh * 0.3
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        + fins
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cy - r * 0.75)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx - r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + r * 0.65)}" y2="{n(cy + r * 0.38)}"/>'
        + f'<line x1="0" y1="{n(h / 2)}" x2="{n(x)}" y2="{n(h / 2)}"/>'
        f'<line x1="{n(x + bw)}" y1="{n(h / 2)}" x2="{n(w)}" y2="{n(h / 2)}"/>'
    )


# --- accessori con derivazione disegnata nel corpo ------------------------
# La linea passa a meta' altezza; lo stacco esce sopra o sotto e porta
# l'accessorio. Tutto in funzione del riquadro, come gli altri corpi.


def _through_line(w: float, h: float) -> str:
    y = h / 2
    return f'<line x1="0" y1="{n(y)}" x2="{n(w)}" y2="{n(y)}"/>'


def tee_junction_body(w: float, h: float) -> str:
    """Raccordo a T: la linea passante, il ramo che sale, e il pallino.

    UNI 9511 Tab. 1 distingue con questo segno una **derivazione** — due
    tubazioni che si uniscono davvero — da un incrocio senza connessione, che e'
    una croce nuda. Il pallino ha diametro pari a quattro volte lo spessore del
    tratto, ed e' quello che rende il raccordo leggibile come raccordo invece che
    come due linee che si toccano.
    """
    radius = 2 * A3_LANDSCAPE.line_medium_mm
    return (
        _through_line(w, h)
        + f'<line x1="{n(w / 2)}" y1="0" x2="{n(w / 2)}" y2="{n(h / 2)}"/>'
        + f'<circle cx="{n(w / 2)}" cy="{n(h / 2)}" r="{n(radius)}" '
        f'fill="currentColor"/>'
    )


def _branch_down(w: float, h: float, to: float) -> str:
    return f'<line x1="{n(w / 2)}" y1="{n(h / 2)}" x2="{n(w / 2)}" y2="{n(to)}"/>'


def _branch_up(w: float, h: float, to: float) -> str:
    return f'<line x1="{n(w / 2)}" y1="{n(h / 2)}" x2="{n(w / 2)}" y2="{n(to)}"/>'


# --- accessori che pendono da uno stacco -----------------------------------
#
# Hanno **un attacco solo** (D-101). Prima ne avevano due e portavano dentro il
# corpo del simbolo sia la linea passante sia la derivazione: era la scorciatoia
# di D-071, e faceva sembrare che l'acqua passasse dentro uno scarico. Adesso il
# simbolo disegna l'accessorio e basta; il tratto che lo collega e' una tubazione
# del modello, e sta dove il grafo dice.


def _stem(w: float, h: float, face: str, to: float) -> str:
    """Il tratto corto dall'attacco al corpo dell'accessorio."""
    start = 0.0 if face == "top" else h
    return f'<line x1="{n(w / 2)}" y1="{n(start)}" x2="{n(w / 2)}" y2="{n(to)}"/>'


def expansion_connection_body(w: float, h: float) -> str:
    """Vaso a membrana appeso al proprio attacco: capsula con il diaframma
    orizzontale a meta' (UNI 9511, vaso chiuso a membrana)."""
    top = h * 0.3
    x, bw, bh = w * 0.1, w * 0.8, h * 0.6
    return (
        _stem(w, h, "top", top)
        + f'<rect x="{n(x)}" y="{n(top)}" width="{n(bw)}" height="{n(bh)}" '
        f'rx="{n(bh * 0.2)}"/>'
        f'<line x1="{n(x)}" y1="{n(top + bh / 2)}" '
        f'x2="{n(x + bw)}" y2="{n(top + bh / 2)}"/>'
    )


def safety_valve_body(w: float, h: float) -> str:
    """Valvola di sicurezza (UNI 9511 Tab. 3): corpo a triangolo con la molla
    a zig-zag sopra, appesa al proprio attacco."""
    apex_y = h * 0.62
    base_y = h * 0.42
    half = w * 0.32
    zig_left, zig_right = w * 0.22, w * 0.78
    steps = (h * 0.34, h * 0.26, h * 0.18, h * 0.1)
    spring = f"M{n(w / 2)} {n(base_y)} " + " ".join(
        f"L{n(zig_left if index % 2 == 0 else zig_right)} {n(y)}"
        for index, y in enumerate(steps)
    )
    return (
        _stem(w, h, "bottom", apex_y)
        + f'<path d="M{n(w / 2 - half)} {n(base_y)} L{n(w / 2 + half)} {n(base_y)} '
        f'L{n(w / 2)} {n(apex_y)} Z"/>'
        f'<path d="{spring}"/>'
    )


def air_separator_body(w: float, h: float) -> str:
    """Corpo sulla linea e sfiato automatico in cima."""
    y = h / 2
    top = h * 0.24
    return (
        _through_line(w, h)
        + f'<rect x="{n(w * 0.2)}" y="{n(y - h * 0.09)}" '
        f'width="{n(w * 0.6)}" height="{n(h * 0.18)}"/>'
        + _branch_up(w, h, top)
        + f'<circle cx="{n(w / 2)}" cy="{n(top - h * 0.06)}" r="{n(h * 0.06)}"/>'
    )


def dirt_separator_body(w: float, h: float) -> str:
    """Corpo sulla linea e vaso di raccolta sotto, con il rubinetto."""
    y = h / 2
    bottom = h * 0.76
    return (
        _through_line(w, h)
        + f'<rect x="{n(w * 0.2)}" y="{n(y - h * 0.09)}" '
        f'width="{n(w * 0.6)}" height="{n(h * 0.18)}"/>'
        + _branch_down(w, h, bottom)
        + f'<path d="M{n(w * 0.25)} {n(bottom - h * 0.1)} L{n(w * 0.75)} '
        f'{n(bottom - h * 0.1)} L{n(w / 2)} {n(bottom)} Z" fill="black"/>'
    )


def filling_unit_body(w: float, h: float) -> str:
    """Gruppo di riempimento appeso al proprio attacco: valvola a farfalla e
    riduttore a triangolo in serie, uno sopra l'altro lungo lo stacco."""
    cx = w / 2
    half = w * 0.24
    v_top, v_mid, v_bottom = h * 0.24, h * 0.4, h * 0.56
    r_base, r_apex = h * 0.68, h * 0.92
    return (
        _stem(w, h, "top", v_top)
        + f'<path d="M{n(cx - half)} {n(v_top)} L{n(cx + half)} {n(v_top)} '
        f'L{n(cx)} {n(v_mid)} Z"/>'
        f'<path d="M{n(cx - half)} {n(v_bottom)} L{n(cx + half)} {n(v_bottom)} '
        f'L{n(cx)} {n(v_mid)} Z"/>'
        f'<line x1="{n(cx)}" y1="{n(v_bottom)}" x2="{n(cx)}" y2="{n(r_base)}"/>'
        f'<path d="M{n(cx - half)} {n(r_base)} L{n(cx + half)} {n(r_base)} '
        f'L{n(cx)} {n(r_apex)} Z"/>'
    )


def drain_connection_body(w: float, h: float) -> str:
    """Attacco di scarico appeso al proprio attacco: la valvola e il tratto
    finale all'estremita' aperta."""
    cx = w / 2
    base_top, mid, base_bottom = h * 0.3, h * 0.48, h * 0.66
    end = h * 0.88
    half = w * 0.24
    return (
        _stem(w, h, "top", base_top)
        + f'<path d="M{n(cx - half)} {n(base_top)} L{n(cx + half)} {n(base_top)} '
        f'L{n(cx)} {n(mid)} Z"/>'
        f'<path d="M{n(cx - half)} {n(base_bottom)} L{n(cx + half)} {n(base_bottom)} '
        f'L{n(cx)} {n(mid)} Z"/>'
        f'<line x1="{n(cx)}" y1="{n(base_bottom)}" x2="{n(cx)}" y2="{n(end)}"/>'
        f'<line x1="{n(cx - half)}" y1="{n(end)}" x2="{n(cx + half)}" y2="{n(end)}"/>'
    )


DIAL_GLYPH_ID = "lettera"
"""Il glifo leggibile di uno strumento indicatore: la lettera nel quadrante."""


def dial_centre(w: float, h: float) -> tuple[float, float]:
    """Il centro del quadrante, attorno a cui la lettera resta dritta."""
    return w / 2, h * 0.3


def _dial(w: float, h: float, mark_of: Any) -> str:
    """Strumento indicatore appeso al proprio attacco: il quadrante e la lettera.

    La lettera sta in un gruppo dichiarato leggibile (DRAW-005, I-033): chi
    ruota il simbolo la contro-ruota attorno al centro del quadrante, cosi'
    che `P` e `T` si leggano nel verso della tavola anche a strumento girato.
    """
    r = w * 0.4
    cx, cy = dial_centre(w, h)
    return (
        _stem(w, h, "bottom", cy + r)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        + f'<g data-glyph="{DIAL_GLYPH_ID}">{mark_of(cx, cy, r)}</g>'
    )


def thermometer_body(w: float, h: float) -> str:
    """Termometro (UNI 9511 Tab. 10): cerchio con la lettera T, tracciata a
    tratti — due segmenti — per non dipendere da alcun font."""

    def mark(cx: float, cy: float, r: float) -> str:
        bar_y = cy - r * 0.45
        half = r * 0.45
        return (
            f'<line x1="{n(cx - half)}" y1="{n(bar_y)}" '
            f'x2="{n(cx + half)}" y2="{n(bar_y)}"/>'
            f'<line x1="{n(cx)}" y1="{n(bar_y)}" '
            f'x2="{n(cx)}" y2="{n(cy + r * 0.5)}"/>'
        )

    return _dial(w, h, mark)


def pressure_gauge_body(w: float, h: float) -> str:
    """Manometro (UNI 9511 Tab. 10): cerchio con la lettera P a tratti —
    asta verticale e pancia a semicerchio, nessun font."""

    def mark(cx: float, cy: float, r: float) -> str:
        x0 = cx - r * 0.25
        top_y, mid_y, bottom_y = cy - r * 0.5, cy, cy + r * 0.55
        return (
            f'<line x1="{n(x0)}" y1="{n(top_y)}" x2="{n(x0)}" y2="{n(bottom_y)}"/>'
            f'<path d="M{n(x0)} {n(top_y)} Q{n(x0 + r * 0.85)} '
            f'{n((top_y + mid_y) / 2)} {n(x0)} {n(mid_y)}"/>'
        )

    return _dial(w, h, mark)


def mixing_valve_body(w: float, h: float) -> str:
    """Valvola a tre vie di UNI 9511 Tab. 3 — tre triangoli chiusi al centro,
    ingresso freddo dal basso — con lo stelo a T della testa termostatica."""
    cx, cy = w / 2, h / 2
    d = w * 0.33
    s = d * 0.8
    stem_top = h * 0.3
    cap = w * 0.16
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(cx - d)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx + d)}" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<path d="M{n(cx - d)} {n(cy - s)} L{n(cx - d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(cx + d)} {n(cy - s)} L{n(cx + d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(cx - s)} {n(cy + d)} L{n(cx + s)} {n(cy + d)} L{n(cx)} {n(cy)} Z"/>'
        f'<line x1="{n(cx)}" y1="{n(cy + d)}" x2="{n(cx)}" y2="{n(h * 0.85)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(stem_top)}"/>'
        f'<line x1="{n(cx - cap)}" y1="{n(stem_top)}" x2="{n(cx + cap)}" y2="{n(stem_top)}"/>'
    )


def pressure_reducer_body(w: float, h: float) -> str:
    """Riduttore di pressione, forma comune italiana: farfalla con la
    calotta piatta della molla sullo stelo."""
    cx, cy = w / 2, h / 2
    d = w * 0.33
    s = d * 0.8
    cap_w = w * 0.44
    cap_top, cap_bottom = h * 0.22, h * 0.34
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(cx - d)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx + d)}" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<path d="M{n(cx - d)} {n(cy - s)} L{n(cx - d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<path d="M{n(cx + d)} {n(cy - s)} L{n(cx + d)} {n(cy + s)} L{n(cx)} {n(cy)} Z"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(cap_bottom)}"/>'
        f'<rect x="{n(cx - cap_w / 2)}" y="{n(cap_top)}" '
        f'width="{n(cap_w)}" height="{n(cap_bottom - cap_top)}"/>'
    )


def network_boundary_body(w: float, h: float) -> str:
    """Confine di rete: da dove il fluido arriva, o dove se ne va.

    Il corpo e' la sola linea fino alla porta. La freccia non sta nel corpo:
    e' un glifo di verso dichiarato nel manifesto (`boundary_flow_glyph`), e
    chi disegna la punta nel verso locale dell'acqua letto dal catalogo
    (DRAW-005, I-032) — verso la porta sull'acquedotto, da cui l'acqua esce
    verso l'impianto; verso l'interno sulle utenze, in cui l'acqua entra."""
    cy = h / 2
    return f'<line x1="0" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'


def boundary_flow_glyph(w: float, h: float) -> dict[str, Any]:
    """La freccia del confine, centrata sul tratto che porta alla porta: a
    verso uscente ridisegna esattamente il triangolo che il corpo aveva."""
    return {
        "port": "a",
        "x_mm": w * 0.725,
        "y_mm": h / 2,
        "length_mm": w * 0.55,
        "half_width_mm": h * 0.2,
    }



@dataclass(frozen=True)
class SymbolSpec:
    id: str
    name: str
    width_mm: float
    height_mm: float
    inline: bool
    ports: list[dict[str, Any]]
    body: str
    source: str
    allowed_rotations_deg: list[int] = field(
        default_factory=lambda: list(ALLOWED_ROTATIONS_DEG)
    )
    flow_glyphs: list[dict[str, Any]] = field(default_factory=list)
    """Le frecce di verso legate a una porta, che il renderer traccia nel verso
    locale dell'acqua (DRAW-005, I-032)."""
    upright_glyphs: list[dict[str, Any]] = field(default_factory=list)
    """I glifi interni dichiarati leggibili, che restano dritti rispetto al
    foglio quando il corpo ruota (DRAW-005, I-033)."""
    version: str = VERSION
    """La versione del manifesto: sale quando il segno cambia forma o porte."""
    clearance_mm: float = CLEARANCE_MM
    """L'area di rispetto sulle facce con porta. Un raccordo e' un punto della
    tubazione, non un apparecchio, e ne tiene una minima (D-119)."""


def inline_symbol(
    symbol_id: str,
    name: str,
    size: tuple[float, float],
    body_of: Any,
    source: str,
    allowed_rotations_deg: list[int] | None = None,
    version: str = VERSION,
) -> SymbolSpec:
    """Componente in linea: due porte opposte, a sinistra e a destra."""
    w, h = size
    return SymbolSpec(
        id=symbol_id,
        name=name,
        width_mm=w,
        height_mm=h,
        inline=True,
        ports=[port("a", "left", w, h), port("b", "right", w, h)],
        body=body_of(w, h),
        source=source,
        allowed_rotations_deg=list(allowed_rotations_deg or ALLOWED_ROTATIONS_DEG),
        version=version,
    )


def single_port_symbol(
    symbol_id: str,
    name: str,
    size: tuple[float, float],
    face: str,
    body_of: Any,
    source: str,
    allowed_rotations_deg: list[int] | None = None,
    flow_glyphs: list[dict[str, Any]] | None = None,
    upright_glyphs: list[dict[str, Any]] | None = None,
    version: str = VERSION,
) -> SymbolSpec:
    w, h = size
    return SymbolSpec(
        id=symbol_id,
        name=name,
        width_mm=w,
        height_mm=h,
        inline=False,
        ports=[port("a", face, w, h)],
        body=body_of(w, h),
        source=source,
        allowed_rotations_deg=list(allowed_rotations_deg or ALLOWED_ROTATIONS_DEG),
        flow_glyphs=list(flow_glyphs or []),
        upright_glyphs=list(upright_glyphs or []),
        version=version,
    )


def dial_glyph(size: tuple[float, float]) -> list[dict[str, Any]]:
    """La lettera di uno strumento indicatore, dichiarata leggibile."""
    cx, cy = dial_centre(*size)
    return [{"id": DIAL_GLYPH_ID, "x_mm": cx, "y_mm": cy}]


def two_port_terminal(symbol_id: str, name: str, body_of: Any, source: str) -> SymbolSpec:
    """Terminale d'impianto: ingresso a sinistra, uscita a destra.

    Non e' un componente in linea: la tubazione ci finisce dentro, non ci passa
    attraverso, quindi non dichiara alcuna interruzione di linea.
    """
    w, h = TERMINAL
    return SymbolSpec(
        id=symbol_id,
        name=name,
        width_mm=w,
        height_mm=h,
        inline=False,
        ports=[port("in", "left", w, h), port("out", "right", w, h)],
        body=body_of(w, h),
        source=source,
    )


HEAT_PUMP_W, HEAT_PUMP_H = MACHINE
STORAGE_W, STORAGE_H = STORAGE
MANIFOLD_W, MANIFOLD_H = MANIFOLD
MANIFOLD_OUTLETS = (12.5, 27.5)

HEAT_PUMP_PORTS = [
    # Quindici millimetri fra mandata e ritorno (DRAW-005, I-039): e' l'interasse
    # del simbolo della pompa di calore della tavola 1, e non una costante per
    # tutte le macchine. Cinque millimetri erano l'altezza di una valvola: due
    # valvole sui due rami si toccavano, e la posa pagava gradini. Con quindici
    # gli accessori dei due rami hanno lo spazio funzionale che il catalogo
    # chiede, e le porte stanno alle stesse quote di quelle primarie
    # dell'accumulo, che e' cio' che permette una mandata diritta.
    port_at("water_supply", "right", 5.0, HEAT_PUMP_W, HEAT_PUMP_H),
    port_at("water_return", "right", 20.0, HEAT_PUMP_W, HEAT_PUMP_H),
]
CYLINDER_PORTS = [
    port_at("coil_in", "left", 7.5, STORAGE_W, STORAGE_H),
    port_at("coil_out", "left", 17.5, STORAGE_W, STORAGE_H),
    port_at("dhw_out", "top", 7.5, STORAGE_W, STORAGE_H),
    # L'ingresso freddo sta in basso **a lato**, non sul fondo: un attacco sulla
    # faccia inferiore di un accumulo appoggiato a terra e' irraggiungibile,
    # perche' la tubazione dovrebbe passare sotto la linea di terra.
    port_at("cold_in", "left", 37.5, STORAGE_W, STORAGE_H),
    # La sede della sonda: attacco di servizio dichiarato in legenda dal
    # costruttore (SRC-018), a meta' altezza sul fianco libero.
    port_at("probe", "right", 20.0, STORAGE_W, STORAGE_H),
]
BUFFER_PORTS = [
    port_at("primary_in", "left", 5.0, STORAGE_W, STORAGE_H),
    port_at("primary_out", "left", 20.0, STORAGE_W, STORAGE_H),
    port_at("secondary_out", "right", 5.0, STORAGE_W, STORAGE_H),
    port_at("secondary_in", "right", 20.0, STORAGE_W, STORAGE_H),
    # Gli attacchi di servizio, dove il costruttore li mette davvero: lo sfiato
    # in cima, lo scarico in fondo, la sonda sul fianco (SRC-017, SRC-018).
    port_at("vent", "top", 12.5, STORAGE_W, STORAGE_H),
    port_at("drain", "bottom", 12.5, STORAGE_W, STORAGE_H),
    port_at("probe", "left", 32.5, STORAGE_W, STORAGE_H),
]

GAS_BOILER_PORTS = [
    port_at("water_supply", "right", 10.0, *MACHINE),
    port_at("water_return", "right", 20.0, *MACHINE),
]
EXCHANGER_PORTS = [
    port_at("primary_in", "left", 5.0, *SEPARATOR),
    port_at("primary_out", "left", 20.0, *SEPARATOR),
    port_at("secondary_out", "right", 5.0, *SEPARATOR),
    port_at("secondary_in", "right", 20.0, *SEPARATOR),
]
BUFFER_TWO_PORTS = [
    port_at("a", "left", 5.0, STORAGE_W, STORAGE_H),
    port_at("b", "right", 5.0, STORAGE_W, STORAGE_H),
    port_at("vent", "top", 12.5, STORAGE_W, STORAGE_H),
    port_at("drain", "bottom", 12.5, STORAGE_W, STORAGE_H),
    port_at("probe", "left", 32.5, STORAGE_W, STORAGE_H),
]
BUFFER_COMBINED_PORTS = [
    port_at("primary_in", "left", 5.0, STORAGE_W, STORAGE_H),
    port_at("primary_out", "left", 20.0, STORAGE_W, STORAGE_H),
    port_at("secondary_out", "right", 5.0, STORAGE_W, STORAGE_H),
    port_at("secondary_in", "right", 20.0, STORAGE_W, STORAGE_H),
    port_at("dhw_out", "top", 7.5, STORAGE_W, STORAGE_H),
    port_at("cold_in", "left", 37.5, STORAGE_W, STORAGE_H),
    port_at("vent", "top", 17.5, STORAGE_W, STORAGE_H),
    port_at("drain", "bottom", 12.5, STORAGE_W, STORAGE_H),
    port_at("probe", "right", 32.5, STORAGE_W, STORAGE_H),
]
DHW_HEAT_PUMP_PORTS = [
    port_at("cold_in", "left", 37.5, STORAGE_W, STORAGE_H),
    port_at("dhw_out", "top", 12.5, STORAGE_W, STORAGE_H),
    port_at("probe", "right", 20.0, STORAGE_W, STORAGE_H),
]

SYMBOLS: list[SymbolSpec] = [
    # --- accessori proposti dalle regole (P1) -------------------------------
    # Tutti in linea: la derivazione, dove serve, sta nel corpo del simbolo.
    # Gli accessori che pendono da uno stacco hanno un attacco solo (D-101): il
    # tratto che li collega e' una tubazione del modello, non un tratto disegnato
    # dentro il simbolo.
    single_port_symbol(
        "expansion-connection", "Vaso di espansione", BRANCHED_ACCESSORY, "top",
        expansion_connection_body, SOURCE_UNI_VESSELS, EXPANSION_VESSEL_ROTATIONS_DEG,
    ),
    single_port_symbol(
        "valve-safety", "Valvola di sicurezza", BRANCHED_ACCESSORY, "bottom",
        safety_valve_body, SOURCE_UNI_TAB3,
    ),
    inline_symbol("air-separator", "Separatore d'aria", BRANCHED_ACCESSORY, air_separator_body, SOURCE_PRACTICE_HYDRONIC),
    inline_symbol("dirt-separator", "Defangatore", BRANCHED_ACCESSORY, dirt_separator_body, SOURCE_PRACTICE_HYDRONIC),
    single_port_symbol(
        "filling-unit", "Gruppo di riempimento", BRANCHED_ACCESSORY, "top",
        filling_unit_body, SOURCE_PRACTICE_HYDRONIC,
    ),
    single_port_symbol(
        "drain-connection", "Attacco di scarico", BRANCHED_ACCESSORY, "top",
        drain_connection_body, SOURCE_PRACTICE_HYDRONIC,
    ),
    single_port_symbol(
        "thermometer", "Termometro", BRANCHED_ACCESSORY, "bottom",
        thermometer_body, SOURCE_UNI_TAB10, upright_glyphs=dial_glyph(BRANCHED_ACCESSORY),
        version="2.0.0",
    ),
    single_port_symbol(
        "pressure-gauge", "Manometro", BRANCHED_ACCESSORY, "bottom",
        pressure_gauge_body, SOURCE_UNI_TAB10, upright_glyphs=dial_glyph(BRANCHED_ACCESSORY),
        version="2.0.0",
    ),
    inline_symbol("mixing-valve-thermostatic", "Valvola miscelatrice termostatica", BRANCHED_ACCESSORY, mixing_valve_body, SOURCE_UNI_TAB3),
    inline_symbol("pressure-reducer", "Riduttore di pressione", BRANCHED_ACCESSORY, pressure_reducer_body, SOURCE_PRACTICE_HYDRONIC),
    single_port_symbol(
        "network-boundary", "Confine di rete", INLINE_ACCESSORY, "right", network_boundary_body,
        SOURCE_PRACTICE_HYDRONIC, flow_glyphs=[boundary_flow_glyph(*INLINE_ACCESSORY)],
        version="2.0.0",
    ),
    # --- le famiglie dei cinque impianti di prova del committente -----------
    SymbolSpec(
        id="gas-boiler",
        name="Caldaia a condensazione",
        width_mm=MACHINE[0],
        height_mm=MACHINE[1],
        inline=False,
        ports=GAS_BOILER_PORTS,
        body=gas_boiler_body(MACHINE[0], MACHINE[1], GAS_BOILER_PORTS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    SymbolSpec(
        id="plate-heat-exchanger",
        name="Scambiatore a piastre",
        width_mm=SEPARATOR[0],
        height_mm=SEPARATOR[1],
        inline=False,
        ports=EXCHANGER_PORTS,
        body=plate_exchanger_body(SEPARATOR[0], SEPARATOR[1], EXCHANGER_PORTS),
        source=SOURCE_UNI_EXCHANGERS,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    SymbolSpec(
        id="ahu-coil",
        name="Batteria di trattamento aria",
        width_mm=TERMINAL[0],
        height_mm=TERMINAL[1],
        inline=False,
        ports=[port("in", "left", *TERMINAL), port("out", "right", *TERMINAL)],
        body=coil_body(*TERMINAL),
        source=SOURCE_PRACTICE_HYDRONIC,
    ),
    SymbolSpec(
        id="buffer-two-port",
        name="Volano termico a due attacchi",
        width_mm=STORAGE[0],
        height_mm=STORAGE[1],
        inline=False,
        ports=BUFFER_TWO_PORTS,
        body=reserve_body(STORAGE_W, STORAGE_H, BUFFER_TWO_PORTS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="1.1.0",
    ),
    SymbolSpec(
        id="buffer-combined",
        name="Accumulo combinato",
        width_mm=STORAGE[0],
        height_mm=STORAGE[1],
        inline=False,
        ports=BUFFER_COMBINED_PORTS,
        # Il serpentino sanitario, continuo da `cold_in` a `dhw_out`; i quattro
        # attacchi tecnici entrano nel volume del mantello (I-036, I-037).
        body=reserve_body(
            STORAGE_W, STORAGE_H, BUFFER_COMBINED_PORTS, coil=("cold_in", "dhw_out"), rows=6
        ),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="2.0.0",
    ),
    SymbolSpec(
        id="dhw-heat-pump",
        name="Boiler in pompa di calore",
        width_mm=STORAGE[0],
        height_mm=STORAGE[1],
        inline=False,
        ports=DHW_HEAT_PUMP_PORTS,
        body=reserve_body(STORAGE_W, STORAGE_H, DHW_HEAT_PUMP_PORTS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="1.1.0",
    ),
    SymbolSpec(
        id="mixing-valve-3way",
        name="Valvola miscelatrice a tre vie",
        width_mm=DEVICE[0],
        height_mm=DEVICE[1],
        inline=False,
        ports=[
            port("hot_in", "left", *DEVICE),
            port("cold_in", "bottom", *DEVICE),
            port("out", "right", *DEVICE),
        ],
        body=diverting_valve_body(*DEVICE),
        source=SOURCE_UNI_TAB3,
    ),
    # --- idronico -----------------------------------------------------------
    # Il T di UNI 9511 serve a due cose che sul disegno hanno lo stesso segno e
    # nel modello sono pezzi diversi: la **confluenza**, dove due tubazioni
    # diventano una (D-100), e la **derivazione**, da cui pende un accessorio
    # (D-101). Il segno e' uno, e i due lo condividono.
    SymbolSpec(
        id="tee-junction",
        name="Raccordo a T",
        width_mm=INLINE_ACCESSORY[0],
        height_mm=INLINE_ACCESSORY[1],
        # Non interrompe la linea come fa una valvola: e' il punto in cui due
        # linee diventano una, e i tre attacchi lo dicono da soli.
        inline=False,
        ports=[
            port("a", "left", *INLINE_ACCESSORY),
            port("c", "top", *INLINE_ACCESSORY),
            port("b", "right", *INLINE_ACCESSORY),
        ],
        body=tee_junction_body(*INLINE_ACCESSORY),
        source=SOURCE_UNI_TAB1_FITTING,
        version="2.0.0",
        clearance_mm=FITTING_CLEARANCE_MM,
    ),
    SymbolSpec(
        id="tee-branch",
        name="Derivazione a T",
        width_mm=INLINE_ACCESSORY[0],
        height_mm=INLINE_ACCESSORY[1],
        inline=False,
        ports=[
            port("a", "left", *INLINE_ACCESSORY),
            port("branch", "top", *INLINE_ACCESSORY),
            port("b", "right", *INLINE_ACCESSORY),
        ],
        body=tee_junction_body(*INLINE_ACCESSORY),
        source=SOURCE_UNI_TAB1_FITTING,
        version="2.0.0",
        clearance_mm=FITTING_CLEARANCE_MM,
    ),
    inline_symbol("valve-isolation", "Valvola di intercettazione", INLINE_ACCESSORY, valve_isolation_body, SOURCE_UNI_TAB3),
    inline_symbol(
        "valve-check", "Valvola di ritegno", INLINE_ACCESSORY, valve_check_body,
        SOURCE_UNI_CHECK_VALVE, version="3.0.0",
    ),
    inline_symbol(
        "strainer", "Filtro a Y", INLINE_ACCESSORY, strainer_body, SOURCE_PRACTICE_HYDRONIC,
        STRAINER_ROTATIONS_DEG, version="2.0.0",
    ),
    inline_symbol("pump-circulator", "Pompa di circolazione", DEVICE, pump_body, SOURCE_PRACTICE_HYDRONIC),
    single_port_symbol(
        "air-vent", "Valvola di sfiato aria", TERMINAL_ACCESSORY, "bottom",
        air_vent_body, SOURCE_PRACTICE_HYDRONIC, AIR_VENT_ROTATIONS_DEG,
    ),
    SymbolSpec(
        id="heat-pump-air-water",
        name="Pompa di calore aria-acqua",
        width_mm=HEAT_PUMP_W,
        height_mm=HEAT_PUMP_H,
        inline=False,
        ports=HEAT_PUMP_PORTS,
        body=heat_pump_body(HEAT_PUMP_W, HEAT_PUMP_H, HEAT_PUMP_PORTS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="2.0.0",
    ),
    SymbolSpec(
        id="dhw-cylinder",
        name="Bollitore ACS",
        width_mm=STORAGE_W,
        height_mm=STORAGE_H,
        inline=False,
        ports=CYLINDER_PORTS,
        # Il serpentino tecnico, continuo da `coil_in` a `coil_out`; acqua fredda
        # e acqua calda sanitaria entrano nel volume che il bollitore tiene in serbo.
        body=reserve_body(
            STORAGE_W, STORAGE_H, CYLINDER_PORTS, coil=("coil_in", "coil_out"), rows=4
        ),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="2.0.0",
    ),
    SymbolSpec(
        id="buffer-four-port",
        name="Volano termico a quattro attacchi",
        width_mm=STORAGE_W,
        height_mm=STORAGE_H,
        inline=False,
        ports=BUFFER_PORTS,
        body=reserve_body(STORAGE_W, STORAGE_H, BUFFER_PORTS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
        version="1.1.0",
    ),
    SymbolSpec(
        id="diverting-valve-3way",
        name="Valvola deviatrice a tre vie",
        width_mm=DEVICE[0],
        height_mm=DEVICE[1],
        inline=False,
        ports=[
            port("in", "left", *DEVICE),
            port("out_a", "right", *DEVICE),
            port("out_b", "bottom", *DEVICE),
        ],
        body=diverting_valve_body(*DEVICE),
        source=SOURCE_UNI_TAB3,
    ),
    SymbolSpec(
        id="zone-manifold",
        name="Collettore di zona",
        width_mm=MANIFOLD_W,
        height_mm=MANIFOLD_H,
        inline=False,
        ports=[
            port("in", "left", MANIFOLD_W, MANIFOLD_H),
            *(
                port_at(f"out_{index + 1}", "bottom", x, MANIFOLD_W, MANIFOLD_H)
                for index, x in enumerate(MANIFOLD_OUTLETS)
            ),
        ],
        body=manifold_body(MANIFOLD_W, MANIFOLD_H, MANIFOLD_OUTLETS),
        source=SOURCE_PRACTICE_HYDRONIC,
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    two_port_terminal("radiator", "Radiatore", radiator_body, SOURCE_PRACTICE_HYDRONIC),
    two_port_terminal("underfloor-panel", "Pannello radiante", underfloor_body, SOURCE_PRACTICE_HYDRONIC),
    two_port_terminal("fan-coil", "Ventilconvettore", fan_coil_body, SOURCE_PRACTICE_HYDRONIC),
    # --- aeraulico ----------------------------------------------------------
    inline_symbol("duct-damper", "Serranda", INLINE_ACCESSORY, duct_damper_body, SOURCE_PRACTICE_PENDING),
    single_port_symbol("air-diffuser", "Diffusore d'aria", DEVICE, "left", air_diffuser_body, SOURCE_PRACTICE_PENDING),
    inline_symbol("fan-inline", "Ventilatore in linea", DEVICE, fan_body, SOURCE_PRACTICE_PENDING),
    # --- refrigerante -------------------------------------------------------
    SymbolSpec(
        id="refrigerant-branch",
        name="Derivazione refrigerante",
        width_mm=DEVICE[0],
        height_mm=DEVICE[1],
        inline=False,
        ports=[
            port("a", "left", *DEVICE),
            port("b", "right", *DEVICE),
            port("c", "bottom", *DEVICE),
        ],
        body=refrigerant_branch_body(*DEVICE),
        source=SOURCE_PRACTICE_PENDING,
    ),
    # --- gas ----------------------------------------------------------------
    # La pratica del gas usa il segno generale del valvolame con una sigla di
    # fluido, non una forma diversa: stesso corpo della intercettazione.
    inline_symbol("gas-valve", "Valvola gas", INLINE_ACCESSORY, valve_isolation_body, SOURCE_UNI_TAB3),
    inline_symbol("gas-meter", "Contatore gas", DEVICE, gas_meter_body, SOURCE_PRACTICE_PENDING),
]


def manifest_payload(spec: SymbolSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": spec.id,
        "version": spec.version,
        "name": spec.name,
        "width_mm": spec.width_mm,
        "height_mm": spec.height_mm,
        "allowed_rotations_deg": spec.allowed_rotations_deg,
    }
    if spec.inline:
        # L'interruzione vale l'intera larghezza: le porte sono a sinistra e a
        # destra, quindi l'asse che le unisce e' orizzontale.
        payload["inline_gap_mm"] = spec.width_mm
    payload["ports"] = spec.ports
    payload["keep_out"] = keep_out(spec.ports, spec.clearance_mm)
    if spec.flow_glyphs:
        payload["flow_glyphs"] = spec.flow_glyphs
    if spec.upright_glyphs:
        payload["upright_glyphs"] = spec.upright_glyphs
    payload["source"] = spec.source
    return payload


def write_symbol(directory: Path, spec: SymbolSpec) -> None:
    payload = manifest_payload(spec)
    SymbolManifest.model_validate(payload)  # fail fast, before anything is written
    (directory / f"{spec.id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (directory / f"{spec.id}.svg").write_text(spec.body + "\n", encoding="utf-8")


def main() -> None:
    SYMBOLS_DIR.mkdir(parents=True, exist_ok=True)
    for spec in SYMBOLS:
        write_symbol(SYMBOLS_DIR, spec)


if __name__ == "__main__":
    main()
