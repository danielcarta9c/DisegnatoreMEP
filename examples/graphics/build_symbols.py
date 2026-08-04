"""Genera la libreria dei simboli pubblicati.

Venti simboli su quattro domini (idronico, aeraulico, refrigerante, gas), con
porte sul perimetro, faccia coerente con il lato e **ogni coordinata su un
nodo della griglia** da 2,5 mm: senza quest'ultima proprieta' l'instradamento
ortogonale non raggiunge nessun attacco (D-054).

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
rappresenta una parte davvero piena (il disco di un ritegno, la freccia di una
pompa, il punto di giunzione di una derivazione).

I corpi sono **disegnati in funzione del riquadro**, non scritti come
coordinate fisse: cambiare una taglia della gerarchia non puo' cosi' lasciare
un disegno fuori dal proprio box.

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

SOURCE = "CONV-GRAFICA-001"
"""Convenzione grafica interna del progetto, non una norma esterna (D-047)."""


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


def keep_out(ports: list[dict[str, Any]]) -> dict[str, float]:
    """Area di rispetto sui lati che portano una porta, derivata dalle porte."""
    faces = {item["face"] for item in ports}
    return {
        f"{side}_mm": CLEARANCE_MM if side in faces else 0.0
        for side in ("left", "right", "top", "bottom")
    }


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
    """La clessidra delle valvole: due triangoli opposti al vertice."""
    inset = w / 6
    left, right = inset, w - inset
    top, bottom = h * 0.1, h * 0.9
    return (
        stubs_horizontal(w, h, inset)
        + f'<path d="M{n(left)} {n(top)} L{n(right)} {n(bottom)} '
        f'L{n(right)} {n(top)} L{n(left)} {n(bottom)} Z"/>'
    )


def valve_check_body(w: float, h: float) -> str:
    """Ritegno: disco pieno a triangolo che appoggia su una battuta."""
    inset = w / 6
    left, right = inset, w - inset
    top, bottom = h * 0.2, h * 0.8
    return (
        stubs_horizontal(w, h, inset)
        + f'<path d="M{n(left)} {n(top)} L{n(left)} {n(bottom)} '
        f'L{n(right - 0.2)} {n(h / 2)} Z" fill="black"/>'
        f'<line x1="{n(right - 0.2)}" y1="{n(top)}" '
        f'x2="{n(right - 0.2)}" y2="{n(bottom)}"/>'
    )


def strainer_body(w: float, h: float) -> str:
    """Filtro a Y: la linea passa dritta, il cestello scende sotto."""
    y = h / 2
    return (
        f'<line x1="0" y1="{n(y)}" x2="{n(w)}" y2="{n(y)}"/>'
        f'<path d="M{n(w * 0.3)} {n(y)} L{n(w * 0.7)} {n(y)} '
        f'L{n(w / 2)} {n(h * 0.95)} Z"/>'
    )


def pump_body(w: float, h: float) -> str:
    """Macchina rotante con la freccia piena del girante."""
    inset = w / 5
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.3
    return (
        stubs_horizontal(w, h, inset)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<path d="M{n(cx - r * 0.5)} {n(cy - r * 0.7)} '
        f'L{n(cx - r * 0.5)} {n(cy + r * 0.7)} L{n(cx + r * 0.7)} {n(cy)} Z" fill="black"/>'
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


def gas_valve_body(w: float, h: float) -> str:
    """La clessidra dentro un corpo circolare: valvola a sfera per il gas."""
    inset = w / 6
    cx, cy = w / 2, h / 2
    r = min(w, h) * 0.42
    d = r * 0.72
    return (
        stubs_horizontal(w, h, inset)
        + f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}"/>'
        f'<path d="M{n(cx - d)} {n(cy - d * 0.75)} L{n(cx + d)} {n(cy + d * 0.75)} '
        f'L{n(cx + d)} {n(cy - d * 0.75)} L{n(cx - d)} {n(cy + d * 0.75)} Z"/>'
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
    """Serbatoio con la membrana orizzontale. La porta e' in alto."""
    cx = w / 2
    x, y = w * 0.15, h * 0.18
    bw, bh = w * 0.7, h * 0.75
    return (
        f'<line x1="{n(cx)}" y1="0" x2="{n(cx)}" y2="{n(y)}"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<line x1="{n(x)}" y1="{n(y + bh * 0.45)}" '
        f'x2="{n(x + bw)}" y2="{n(y + bh * 0.45)}"/>'
    )


def refrigerant_branch_body(w: float, h: float) -> str:
    """Derivazione a T con il punto di giunzione pieno."""
    cx, cy = w / 2, h / 2
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx)}" y2="{n(h)}"/>'
        f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(min(w, h) * 0.075)}" fill="black"/>'
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


def cylinder_body(w: float, h: float, coil: bool, ports: list[dict[str, Any]]) -> str:
    """Serbatoio verticale a fondi bombati. Con serpentino se scaldato da uno."""
    x, y = w * 0.14, h * 0.06
    bw, bh = w * 0.72, h * 0.88
    shell = (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}" '
        f'rx="{n(bw * 0.18)}"/>'
    )
    stubs = stubs_to_ports(ports, w, h, min(w, h) * 0.1)
    if not coil:
        return shell + stubs
    turns = "".join(
        f'<path d="M{n(x + bw * 0.2)} {n(y + bh * (0.28 + i * 0.14))} '
        f'Q{n(x + bw * 0.5)} {n(y + bh * (0.35 + i * 0.14))} '
        f'{n(x + bw * 0.8)} {n(y + bh * (0.28 + i * 0.14))}"/>'
        for i in range(4)
    )
    return shell + turns + stubs


def buffer_body(w: float, h: float, ports: list[dict[str, Any]]) -> str:
    """Volano a quattro attacchi: serbatoio con gli stacchi sulle proprie porte."""
    x, y = w * 0.14, h * 0.06
    bw, bh = w * 0.72, h * 0.88
    return (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(bw)}" height="{n(bh)}" '
        f'rx="{n(bw * 0.18)}"/>' + stubs_to_ports(ports, w, h, x)
    )


def diverting_valve_body(w: float, h: float) -> str:
    """Deviatrice a tre vie: la clessidra con la terza via verso il basso."""
    cx, cy = w / 2, h / 2
    d = min(w, h) * 0.28
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(cx - d)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx + d)}" y1="{n(cy)}" x2="{n(w)}" y2="{n(cy)}"/>'
        f'<line x1="{n(cx)}" y1="{n(cy + d)}" x2="{n(cx)}" y2="{n(h)}"/>'
        f'<path d="M{n(cx - d)} {n(cy - d * 0.8)} L{n(cx + d)} {n(cy + d * 0.8)} '
        f'L{n(cx + d)} {n(cy - d * 0.8)} L{n(cx - d)} {n(cy + d * 0.8)} Z"/>'
        f'<path d="M{n(cx - d * 0.8)} {n(cy + d)} L{n(cx + d * 0.8)} {n(cy + d)} '
        f'L{n(cx)} {n(cy)} Z"/>'
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


def _branch_down(w: float, h: float, to: float) -> str:
    return f'<line x1="{n(w / 2)}" y1="{n(h / 2)}" x2="{n(w / 2)}" y2="{n(to)}"/>'


def _branch_up(w: float, h: float, to: float) -> str:
    return f'<line x1="{n(w / 2)}" y1="{n(h / 2)}" x2="{n(w / 2)}" y2="{n(to)}"/>'


def expansion_connection_body(w: float, h: float) -> str:
    """Stacco verso il basso e vaso a membrana appeso."""
    top = h * 0.62
    x, bw, bh = w * 0.15, w * 0.7, h * 0.32
    return (
        _through_line(w, h)
        + _branch_down(w, h, top)
        + f'<rect x="{n(x)}" y="{n(top)}" width="{n(bw)}" height="{n(bh)}"/>'
        f'<line x1="{n(x)}" y1="{n(top + bh * 0.45)}" '
        f'x2="{n(x + bw)}" y2="{n(top + bh * 0.45)}"/>'
    )


def safety_valve_body(w: float, h: float) -> str:
    """Stacco verso l'alto, valvola a molla con lo scarico libero."""
    top = h * 0.3
    return (
        _through_line(w, h)
        + _branch_up(w, h, top)
        + f'<path d="M{n(w * 0.2)} {n(top)} L{n(w * 0.8)} {n(top)} '
        f'L{n(w / 2)} {n(top + h * 0.16)} Z"/>'
        f'<line x1="{n(w * 0.5)}" y1="{n(top)}" x2="{n(w * 0.9)}" y2="{n(h * 0.08)}"/>'
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
    """Stacco verso il basso con riduttore e ritegno: il gruppo di riempimento."""
    top = h * 0.62
    return (
        _through_line(w, h)
        + _branch_down(w, h, h * 0.95)
        + f'<rect x="{n(w * 0.15)}" y="{n(top)}" '
        f'width="{n(w * 0.7)}" height="{n(h * 0.2)}"/>'
        f'<line x1="{n(w * 0.15)}" y1="{n(top + h * 0.2)}" '
        f'x2="{n(w * 0.85)}" y2="{n(top)}"/>'
    )


def drain_connection_body(w: float, h: float) -> str:
    """Stacco verso il basso con rubinetto a maschio."""
    top = h * 0.68
    return (
        _through_line(w, h)
        + _branch_down(w, h, top)
        + f'<path d="M{n(w * 0.22)} {n(top)} L{n(w * 0.78)} {n(top + h * 0.22)} '
        f'L{n(w * 0.78)} {n(top)} L{n(w * 0.22)} {n(top + h * 0.22)} Z"/>'
    )


def _dial(w: float, h: float, mark: str) -> str:
    top = h * 0.28
    r = h * 0.14
    return (
        _through_line(w, h)
        + _branch_up(w, h, top + r)
        + f'<circle cx="{n(w / 2)}" cy="{n(top)}" r="{n(r)}"/>' + mark
    )


def thermometer_body(w: float, h: float) -> str:
    """Quadrante con la colonna: la temperatura si legge, non si regola."""
    top = h * 0.28
    return _dial(
        w, h,
        f'<line x1="{n(w / 2)}" y1="{n(top - h * 0.09)}" '
        f'x2="{n(w / 2)}" y2="{n(top + h * 0.05)}"/>',
    )


def pressure_gauge_body(w: float, h: float) -> str:
    """Quadrante con la lancetta obliqua: si distingue dal termometro a colpo d'occhio."""
    top = h * 0.28
    return _dial(
        w, h,
        f'<line x1="{n(w / 2)}" y1="{n(top)}" '
        f'x2="{n(w * 0.72)}" y2="{n(top - h * 0.09)}"/>',
    )


def mixing_valve_body(w: float, h: float) -> str:
    """Clessidra sulla linea, con l'ingresso freddo dal basso."""
    inset = w / 6
    left, right = inset, w - inset
    y = h / 2
    top, bottom = y - h * 0.16, y + h * 0.16
    return (
        stubs_horizontal(w, h, inset)
        + f'<path d="M{n(left)} {n(top)} L{n(right)} {n(bottom)} '
        f'L{n(right)} {n(top)} L{n(left)} {n(bottom)} Z"/>'
        + _branch_down(w, h, h * 0.92)
        + f'<path d="M{n(w * 0.32)} {n(h * 0.8)} L{n(w * 0.68)} {n(h * 0.8)} '
        f'L{n(w / 2)} {n(h * 0.92)} Z"/>'
    )


def pressure_reducer_body(w: float, h: float) -> str:
    """Corpo sulla linea con la molla di taratura sopra."""
    y = h / 2
    return (
        _through_line(w, h)
        + f'<rect x="{n(w * 0.2)}" y="{n(y - h * 0.1)}" '
        f'width="{n(w * 0.6)}" height="{n(h * 0.2)}"/>'
        + _branch_up(w, h, h * 0.3)
        + f'<line x1="{n(w * 0.25)}" y1="{n(h * 0.3)}" '
        f'x2="{n(w * 0.75)}" y2="{n(h * 0.3)}"/>'
    )


def network_boundary_body(w: float, h: float) -> str:
    """Confine di rete: da dove il fluido arriva, o dove se ne va."""
    cy = h / 2
    return (
        f'<line x1="0" y1="{n(cy)}" x2="{n(w * 0.45)}" y2="{n(cy)}"/>'
        f'<path d="M{n(w * 0.45)} {n(cy - h * 0.2)} L{n(w)} {n(cy)} '
        f'L{n(w * 0.45)} {n(cy + h * 0.2)} Z"/>'
    )



@dataclass(frozen=True)
class SymbolSpec:
    id: str
    name: str
    width_mm: float
    height_mm: float
    inline: bool
    ports: list[dict[str, Any]]
    body: str
    allowed_rotations_deg: list[int] = field(
        default_factory=lambda: list(ALLOWED_ROTATIONS_DEG)
    )


def inline_symbol(
    symbol_id: str,
    name: str,
    size: tuple[float, float],
    body_of: Any,
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
    )


def single_port_symbol(
    symbol_id: str,
    name: str,
    size: tuple[float, float],
    face: str,
    body_of: Any,
    allowed_rotations_deg: list[int] | None = None,
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
        allowed_rotations_deg=list(allowed_rotations_deg or ALLOWED_ROTATIONS_DEG),
    )


def two_port_terminal(symbol_id: str, name: str, body_of: Any) -> SymbolSpec:
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
    )


HEAT_PUMP_W, HEAT_PUMP_H = MACHINE
STORAGE_W, STORAGE_H = STORAGE
MANIFOLD_W, MANIFOLD_H = MANIFOLD
MANIFOLD_OUTLETS = (12.5, 27.5)

HEAT_PUMP_PORTS = [
    port_at("water_supply", "right", 5.0, HEAT_PUMP_W, HEAT_PUMP_H),
    port_at("water_return", "right", 10.0, HEAT_PUMP_W, HEAT_PUMP_H),
]
CYLINDER_PORTS = [
    port_at("coil_in", "left", 7.5, STORAGE_W, STORAGE_H),
    port_at("coil_out", "left", 17.5, STORAGE_W, STORAGE_H),
    port_at("dhw_out", "top", 7.5, STORAGE_W, STORAGE_H),
    # L'ingresso freddo sta in basso **a lato**, non sul fondo: un attacco sulla
    # faccia inferiore di un accumulo appoggiato a terra e' irraggiungibile,
    # perche' la tubazione dovrebbe passare sotto la linea di terra.
    port_at("cold_in", "left", 37.5, STORAGE_W, STORAGE_H),
]
BUFFER_PORTS = [
    port_at("primary_in", "left", 5.0, STORAGE_W, STORAGE_H),
    port_at("primary_out", "left", 20.0, STORAGE_W, STORAGE_H),
    port_at("secondary_out", "right", 5.0, STORAGE_W, STORAGE_H),
    port_at("secondary_in", "right", 20.0, STORAGE_W, STORAGE_H),
]

SYMBOLS: list[SymbolSpec] = [
    # --- accessori proposti dalle regole (P1) -------------------------------
    # Tutti in linea: la derivazione, dove serve, sta nel corpo del simbolo.
    inline_symbol("expansion-connection", "Vaso di espansione", BRANCHED_ACCESSORY, expansion_connection_body),
    inline_symbol("valve-safety", "Valvola di sicurezza", BRANCHED_ACCESSORY, safety_valve_body),
    inline_symbol("air-separator", "Separatore d'aria", BRANCHED_ACCESSORY, air_separator_body),
    inline_symbol("dirt-separator", "Defangatore", BRANCHED_ACCESSORY, dirt_separator_body),
    inline_symbol("filling-unit", "Gruppo di riempimento", BRANCHED_ACCESSORY, filling_unit_body),
    inline_symbol("drain-connection", "Attacco di scarico", BRANCHED_ACCESSORY, drain_connection_body),
    inline_symbol("thermometer", "Termometro", BRANCHED_ACCESSORY, thermometer_body),
    inline_symbol("pressure-gauge", "Manometro", BRANCHED_ACCESSORY, pressure_gauge_body),
    inline_symbol("mixing-valve-thermostatic", "Valvola miscelatrice termostatica", BRANCHED_ACCESSORY, mixing_valve_body),
    inline_symbol("pressure-reducer", "Riduttore di pressione", BRANCHED_ACCESSORY, pressure_reducer_body),
    single_port_symbol(
        "network-boundary", "Confine di rete", INLINE_ACCESSORY, "right", network_boundary_body,
    ),
    # --- idronico -----------------------------------------------------------
    inline_symbol("valve-isolation", "Valvola di intercettazione", INLINE_ACCESSORY, valve_isolation_body),
    inline_symbol("valve-check", "Valvola di ritegno", INLINE_ACCESSORY, valve_check_body),
    inline_symbol("strainer", "Filtro a Y", INLINE_ACCESSORY, strainer_body),
    inline_symbol("pump-circulator", "Pompa di circolazione", DEVICE, pump_body),
    single_port_symbol(
        "expansion-vessel", "Vaso di espansione ad attacco singolo", VESSEL, "top",
        expansion_vessel_body, EXPANSION_VESSEL_ROTATIONS_DEG,
    ),
    single_port_symbol(
        "air-vent", "Valvola di sfiato aria", TERMINAL_ACCESSORY, "bottom",
        air_vent_body, AIR_VENT_ROTATIONS_DEG,
    ),
    SymbolSpec(
        id="heat-pump-air-water",
        name="Pompa di calore aria-acqua",
        width_mm=HEAT_PUMP_W,
        height_mm=HEAT_PUMP_H,
        inline=False,
        ports=HEAT_PUMP_PORTS,
        body=heat_pump_body(HEAT_PUMP_W, HEAT_PUMP_H, HEAT_PUMP_PORTS),
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    SymbolSpec(
        id="dhw-cylinder",
        name="Bollitore ACS",
        width_mm=STORAGE_W,
        height_mm=STORAGE_H,
        inline=False,
        ports=CYLINDER_PORTS,
        body=cylinder_body(STORAGE_W, STORAGE_H, True, CYLINDER_PORTS),
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    SymbolSpec(
        id="buffer-four-port",
        name="Volano termico a quattro attacchi",
        width_mm=STORAGE_W,
        height_mm=STORAGE_H,
        inline=False,
        ports=BUFFER_PORTS,
        body=buffer_body(STORAGE_W, STORAGE_H, BUFFER_PORTS),
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
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
        allowed_rotations_deg=list(UPRIGHT_ROTATIONS_DEG),
    ),
    two_port_terminal("radiator", "Radiatore", radiator_body),
    two_port_terminal("underfloor-panel", "Pannello radiante", underfloor_body),
    two_port_terminal("fan-coil", "Ventilconvettore", fan_coil_body),
    # --- aeraulico ----------------------------------------------------------
    inline_symbol("duct-damper", "Serranda", INLINE_ACCESSORY, duct_damper_body),
    single_port_symbol("air-diffuser", "Diffusore d'aria", DEVICE, "left", air_diffuser_body),
    inline_symbol("fan-inline", "Ventilatore in linea", DEVICE, fan_body),
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
    ),
    # --- gas ----------------------------------------------------------------
    inline_symbol("gas-valve", "Valvola gas", INLINE_ACCESSORY, gas_valve_body),
    inline_symbol("gas-meter", "Contatore gas", DEVICE, gas_meter_body),
]


def manifest_payload(spec: SymbolSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": spec.id,
        "version": VERSION,
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
    payload["keep_out"] = keep_out(spec.ports)
    payload["source"] = SOURCE
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
