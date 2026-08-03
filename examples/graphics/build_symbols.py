"""Genera la prima libreria trasversale di simboli grafici.

Dodici simboli, quattro per dominio (idronico, aeraulico, refrigerante, gas),
tutti in linea o meno secondo la tabella del Task 6, con porte sul perimetro
e faccia coerente con il lato. Vedi
`.superpowers/sdd/2026-08-03-graphic-system-symbol-library-plan/task-6-brief.md`.

Ogni corpo SVG e' un frammento senza radice `<svg>`, disegnato in coordinate
locali in millimetri con l'origine nell'angolo in alto a sinistra del
riquadro. Lo spessore e il colore del tratto sono decisi dal foglio che
ospita il simbolo (vedi `graphics/svg.py`): un corpo non dichiara mai il
proprio `stroke`. Un `fill` compare solo dove rappresenta davvero una parte
piena del simbolo (il disco di una valvola di ritegno, il rotore di una
pompa, il punto di giunzione di una derivazione, il perno di un contatore).

Rieseguire questo script deve produrre file bit per bit identici: nessuna
data, nessun ordine di dizionario e nessuna rappresentazione in virgola
mobile puo' variare da un'esecuzione all'altra.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import SymbolManifest

REPO_ROOT = Path(__file__).resolve().parents[2]
SYMBOLS_DIR = REPO_ROOT / "assets" / "symbols"

VERSION = "1.0.0"
ALLOWED_ROTATIONS_DEG = [0, 90, 180, 270]
INLINE_MM = 6.0
CLEARANCE_MM = A3_LANDSCAPE.min_clearance_mm

# Riferimento unico per tutti e dodici: la libreria HVAC&R nominata dal
# documento di design (docs/specs/2026-08-01-disegnatore-mep-design.md, §17)
# per il linguaggio simbolico specifico di dominio, distinto dalle regole
# generali di disegno di ISO 14617-1/-2 che quel documento cita a parte.
SOURCE = (
    "ANSI/ASHRAE Standard 134 - Graphic Symbols for Heating, Ventilating, "
    "Air-Conditioning, and Refrigerating Systems"
)


def face_center(face: str, width_mm: float, height_mm: float) -> tuple[float, float]:
    """Coordinata centrata sulla faccia indicata, secondo la regola del Task 6:
    verticale -> meta' altezza, orizzontale -> meta' larghezza.
    """
    return {
        "left": (0.0, height_mm / 2),
        "right": (width_mm, height_mm / 2),
        "top": (width_mm / 2, 0.0),
        "bottom": (width_mm / 2, height_mm),
    }[face]


def port(port_id: str, face: str, width_mm: float, height_mm: float) -> dict[str, Any]:
    x_mm, y_mm = face_center(face, width_mm, height_mm)
    return {"id": port_id, "face": face, "x_mm": x_mm, "y_mm": y_mm}


def keep_out(*sides: str) -> dict[str, float]:
    """keep_out pari a min_clearance_mm sui lati elencati, 0 sugli altri."""
    return {
        f"{side}_mm": CLEARANCE_MM if side in sides else 0.0
        for side in ("left", "right", "top", "bottom")
    }


@dataclass(frozen=True)
class SymbolSpec:
    id: str
    name: str
    width_mm: float
    height_mm: float
    inline: bool
    ports: list[dict[str, Any]]
    keep_out: dict[str, float]
    body: str


def inline_symbol(symbol_id: str, name: str, body: str) -> SymbolSpec:
    """Componente in linea 6x6 mm: due porte opposte, sinistra e destra."""
    width_mm = height_mm = INLINE_MM
    return SymbolSpec(
        id=symbol_id,
        name=name,
        width_mm=width_mm,
        height_mm=height_mm,
        inline=True,
        ports=[
            port("a", "left", width_mm, height_mm),
            port("b", "right", width_mm, height_mm),
        ],
        keep_out=keep_out("left", "right"),
        body=body,
    )


def single_port_symbol(
    symbol_id: str,
    name: str,
    width_mm: float,
    height_mm: float,
    face: str,
    body: str,
) -> SymbolSpec:
    """Componente non in linea con una sola porta, centrata su una faccia."""
    return SymbolSpec(
        id=symbol_id,
        name=name,
        width_mm=width_mm,
        height_mm=height_mm,
        inline=False,
        ports=[port("a", face, width_mm, height_mm)],
        keep_out=keep_out(face),
        body=body,
    )


# ---------------------------------------------------------------------------
# Corpi SVG. Ogni costante e' il frammento locale in millimetri di un solo
# simbolo: nessuna funzione qui sceglie una forma in base al tipo di impianto,
# ogni corpo e' semplicemente un dato di disegno.
# ---------------------------------------------------------------------------

# valve-isolation: valvola a farfalla generica, riquadro 6x6 mm. Corpo dato
# testualmente dal brief del Task 6 - due monconi di attacco e una singola
# path che, senza riempimento, traccia i due lati verticali e le due
# diagonali del riquadro interno: la classica "clessidra" delle valvole.
VALVE_ISOLATION_BODY = (
    '<line x1="0" y1="3" x2="1" y2="3"/>'
    '<line x1="5" y1="3" x2="6" y2="3"/>'
    '<path d="M1 1 L5 5 L5 1 L1 5 Z"/>'
)

# valve-check: stessa famiglia della valvola di intercettazione, ma
# direzionale - un disco pieno a forma di triangolo che appoggia su una
# battuta perpendicolare, la convenzione grafica standard per il ritegno.
VALVE_CHECK_BODY = (
    '<line x1="0" y1="3" x2="1" y2="3"/>'
    '<line x1="5" y1="3" x2="6" y2="3"/>'
    '<path d="M1 1.3 L1 4.7 L4.6 3 Z" fill="black"/>'
    '<line x1="4.6" y1="1.3" x2="4.6" y2="4.7"/>'
)

# strainer: la linea principale passa dritta da a verso b - il filtro non
# interrompe il flusso - con il cestello del filtro a Y appeso sotto,
# base sulla linea e apice in basso. Un cerchio con una sola diagonale
# e' stato scartato: a questa scala si legge come il segnale di divieto,
# non come un filtro.
STRAINER_BODY = (
    '<line x1="0" y1="3" x2="6" y2="3"/>'
    '<path d="M2 3 L4 3 L3 5.5 Z"/>'
)

# pump-circulator: macchina rotante generica (cerchio) con la freccia piena
# del girante che indica il verso di spinta del flusso, da a verso b.
PUMP_CIRCULATOR_BODY = (
    '<line x1="0" y1="3" x2="1.2" y2="3"/>'
    '<line x1="4.8" y1="3" x2="6" y2="3"/>'
    '<circle cx="3" cy="3" r="1.8"/>'
    '<path d="M2.1 1.8 L2.1 4.2 L4.1 3 Z" fill="black"/>'
)

# expansion-vessel: riquadro 6x10 mm, unica porta in alto. Un serbatoio con
# la linea orizzontale della membrana che separa la parte a gas da quella
# collegata all'impianto.
EXPANSION_VESSEL_BODY = (
    '<line x1="3" y1="0" x2="3" y2="2"/>'
    '<rect x="1" y="2" width="4" height="7"/>'
    '<line x1="1" y1="5.5" x2="5" y2="5.5"/>'
)

# air-vent: riquadro 8x8 mm, unica porta in basso. Un piccolo bulbo su uno
# stelo, con una battuta orizzontale sopra a rappresentare il tappo di
# sfiato - lo sfiato d'aria automatico da tubazione.
AIR_VENT_BODY = (
    '<line x1="4" y1="8" x2="4" y2="5"/>'
    '<circle cx="4" cy="3.2" r="1.8"/>'
    '<line x1="3.2" y1="1.4" x2="4.8" y2="1.4"/>'
)

# duct-damper: un tronchetto di canale d'aria (rettangolo) con la lama della
# serranda vista semi-aperta in diagonale.
DUCT_DAMPER_BODY = (
    '<line x1="0" y1="3" x2="1" y2="3"/>'
    '<line x1="5" y1="3" x2="6" y2="3"/>'
    '<rect x="1" y="1" width="4" height="4"/>'
    '<line x1="1.6" y1="1.6" x2="4.4" y2="4.4"/>'
)

# air-diffuser: riquadro 8x8 mm, unica porta a sinistra. Il collarino
# rettangolare del diffusore con le due diagonali incrociate: la lettura a
# pianta di una bocchetta a effetto radiale, distribuita in piu' direzioni.
AIR_DIFFUSER_BODY = (
    '<line x1="0" y1="4" x2="2" y2="4"/>'
    '<rect x="2" y="1" width="5" height="6"/>'
    '<line x1="2" y1="1" x2="7" y2="7"/>'
    '<line x1="2" y1="7" x2="7" y2="1"/>'
)

# fan-inline: stessa macchina rotante della pompa (cerchio), ma con tre pale
# a stella dal centro al posto della freccia piena - l'elica in vista
# frontale, aria e non liquido.
FAN_INLINE_BODY = (
    '<line x1="0" y1="3" x2="1.2" y2="3"/>'
    '<line x1="4.8" y1="3" x2="6" y2="3"/>'
    '<circle cx="3" cy="3" r="1.8"/>'
    '<line x1="3" y1="3" x2="3" y2="1.7"/>'
    '<line x1="3" y1="3" x2="1.87" y2="3.65"/>'
    '<line x1="3" y1="3" x2="4.13" y2="3.65"/>'
)

# refrigerant-branch: riquadro 8x8 mm, tre porte (a sinistra, b destra, c in
# basso). Una semplice derivazione a T con il punto di giunzione pieno.
REFRIGERANT_BRANCH_BODY = (
    '<line x1="0" y1="4" x2="8" y2="4"/>'
    '<line x1="4" y1="4" x2="4" y2="8"/>'
    '<circle cx="4" cy="4" r="0.6" fill="black"/>'
)

# gas-valve: la stessa clessidra della valvola di intercettazione, ma
# racchiusa in un corpo circolare - la convenzione della valvola a
# maschio/sfera usata per le intercettazioni gas.
GAS_VALVE_BODY = (
    '<line x1="0" y1="3" x2="1" y2="3"/>'
    '<line x1="5" y1="3" x2="6" y2="3"/>'
    '<circle cx="3" cy="3" r="2"/>'
    '<path d="M1.7 1.9 L4.3 4.1 L4.3 1.9 L1.7 4.1 Z"/>'
)

# gas-meter: corpo circolare con un indice e il relativo perno pieno al
# centro - il quadrante di misura del contatore.
GAS_METER_BODY = (
    '<line x1="0" y1="3" x2="1.3" y2="3"/>'
    '<line x1="4.7" y1="3" x2="6" y2="3"/>'
    '<circle cx="3" cy="3" r="1.7"/>'
    '<line x1="3" y1="3" x2="4.2" y2="2.1"/>'
    '<circle cx="3" cy="3" r="0.25" fill="black"/>'
)


SYMBOLS: list[SymbolSpec] = [
    # idronico
    inline_symbol("valve-isolation", "Valvola di intercettazione", VALVE_ISOLATION_BODY),
    inline_symbol("valve-check", "Valvola di ritegno", VALVE_CHECK_BODY),
    inline_symbol("strainer", "Filtro a Y", STRAINER_BODY),
    inline_symbol("pump-circulator", "Pompa di circolazione", PUMP_CIRCULATOR_BODY),
    single_port_symbol(
        "expansion-vessel", "Vaso di espansione", 6.0, 10.0, "top", EXPANSION_VESSEL_BODY
    ),
    single_port_symbol("air-vent", "Valvola di sfiato aria", 8.0, 8.0, "bottom", AIR_VENT_BODY),
    # aeraulico
    inline_symbol("duct-damper", "Serranda", DUCT_DAMPER_BODY),
    single_port_symbol("air-diffuser", "Diffusore d'aria", 8.0, 8.0, "left", AIR_DIFFUSER_BODY),
    inline_symbol("fan-inline", "Ventilatore in linea", FAN_INLINE_BODY),
    # refrigerante
    SymbolSpec(
        id="refrigerant-branch",
        name="Derivazione refrigerante",
        width_mm=8.0,
        height_mm=8.0,
        inline=False,
        ports=[
            port("a", "left", 8.0, 8.0),
            port("b", "right", 8.0, 8.0),
            port("c", "bottom", 8.0, 8.0),
        ],
        keep_out=keep_out("left", "right", "bottom"),
        body=REFRIGERANT_BRANCH_BODY,
    ),
    # gas
    inline_symbol("gas-valve", "Valvola gas", GAS_VALVE_BODY),
    inline_symbol("gas-meter", "Contatore gas", GAS_METER_BODY),
]


def manifest_payload(spec: SymbolSpec) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": spec.id,
        "version": VERSION,
        "name": spec.name,
        "width_mm": spec.width_mm,
        "height_mm": spec.height_mm,
        "allowed_rotations_deg": ALLOWED_ROTATIONS_DEG,
    }
    if spec.inline:
        payload["inline_gap_mm"] = spec.width_mm
    payload["ports"] = spec.ports
    payload["keep_out"] = spec.keep_out
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
