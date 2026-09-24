"""Il foglio dei simboli nuovi di `REL-003`, per l'occhio del PO (I-124, D-184).

Uso, dalla radice del repository:

    python docs/collaudi/REL-003/foglio-simboli.py <cartella di uscita>

Scrive due SVG in A3 orizzontale, da convertire in PDF con `scripts/to-pdf.sh`:

- `foglio-1-scala-reale.svg` — per ogni famiglia il simbolo di oggi accanto a quello nuovo,
  **a misura di stampa**: un millimetro del foglio e' un millimetro della tavola;
- `foglio-2-ingrandito.svg` — i simboli nuovi **ingranditi due volte**, con il nome di ogni
  attacco, per guardarne il disegno.

I simboli si leggono dalla libreria pubblicata (`assets/symbols`), cioe' da quello che il
generatore ha scritto: il foglio non disegna niente di suo, e un simbolo che manca lo dice.
Tratto e colore sono quelli con cui una tavola disegna un simbolo: nero, spessore dal
manifesto, nessun riempimento se il corpo non lo dichiara.
"""

import sys
from pathlib import Path

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE

RADICE = Path(__file__).resolve().parents[3]
STANDARD = A3_LANDSCAPE

FAMIGLIE: list[tuple[str, str | None, str]] = [
    # (famiglia, simbolo di oggi, simbolo nuovo)
    ("Pompa di calore aria-acqua", "heat-pump-air-water", "heat-pump-air-water-large"),
    ("Caldaia a condensazione", "gas-boiler", "gas-boiler-modular"),
    ("Solare termico — collettore", None, "solar-collector"),
    ("Bollitore ACS", "dhw-cylinder", "dhw-cylinder-twin-coil"),
    ("Ventilconvettore", "fan-coil", "fan-coil-ducted"),
]

NOMI_DEGLI_ATTACCHI: dict[str, str] = {
    "water_supply": "mandata",
    "water_return": "ritorno",
    "in": "ingresso",
    "out": "uscita",
    "coil_in": "serpentino integrazione — ingresso",
    "coil_out": "serpentino integrazione — uscita",
    "solar_coil_in": "serpentino solare — ingresso",
    "solar_coil_out": "serpentino solare — uscita",
    "dhw_out": "acqua calda",
    "cold_in": "acqua fredda",
    "probe": "sonda",
    "recirculation_in": "ricircolo",
}

PALLINO_MM = 0.6
TESTO_MM = STANDARD.text_small_mm


def _testo(x: float, y: float, testo: str, dimensione: float = TESTO_MM, ancora: str = "start") -> str:
    testo = testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        f'<text x="{x:g}" y="{y:g}" font-size="{dimensione:g}" text-anchor="{ancora}" '
        f'font-family="sans-serif" stroke="none" fill="black">{testo}</text>'
    )


def _simbolo(simbolo: Symbol, x: float, y: float, scala: float = 1.0, attacchi: bool = False) -> str:
    """Il corpo come lo disegna una tavola, con i pallini degli attacchi."""
    manifesto = simbolo.manifest
    spessore = STANDARD.line_mm(manifesto.stroke_weight) / scala
    pallini = "".join(
        f'<circle cx="{porta.x_mm:g}" cy="{porta.y_mm:g}" r="{PALLINO_MM / scala:g}" '
        f'fill="black" stroke="none"/>'
        for porta in manifesto.ports
    )
    parti = [
        f'<g transform="translate({x:g} {y:g}) scale({scala:g})" stroke="black" '
        f'stroke-width="{spessore:g}" fill="none">{simbolo.body}{pallini}</g>'
    ]
    if attacchi:
        for porta in manifesto.ports:
            nome = NOMI_DEGLI_ATTACCHI.get(porta.id, porta.id)
            px, py = x + porta.x_mm * scala, y + porta.y_mm * scala
            if porta.face.value == "left":
                parti.append(_testo(px - 2.0, py + TESTO_MM / 3, nome, ancora="end"))
            elif porta.face.value == "right":
                parti.append(_testo(px + 2.0, py + TESTO_MM / 3, nome))
            elif porta.face.value == "top":
                parti.append(_testo(px, py - 2.0, nome, ancora="middle"))
            else:
                parti.append(_testo(px, py + 2.0 + TESTO_MM, nome, ancora="middle"))
    return "".join(parti)


def _presenti(libreria: SymbolRegistry) -> set[str]:
    return {simbolo.manifest.id for simbolo in libreria.all()}


def _mancante(x: float, y: float, identificativo: str) -> str:
    return _testo(x, y + TESTO_MM, f"{identificativo}: non c'è nella libreria")


def _apri(titolo: str) -> list[str]:
    s = STANDARD
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{s.sheet_width_mm:g}mm" '
        f'height="{s.sheet_height_mm:g}mm" viewBox="0 0 {s.sheet_width_mm:g} {s.sheet_height_mm:g}">',
        f'<rect x="0" y="0" width="{s.sheet_width_mm:g}" height="{s.sheet_height_mm:g}" '
        f'fill="white" stroke="none"/>',
        f'<rect x="{s.margin_left_mm:g}" y="{s.margin_top_mm:g}" width="{s.usable_width_mm:g}" '
        f'height="{s.usable_height_mm:g}" fill="none" stroke="black" '
        f'stroke-width="{s.line_thin_mm:g}"/>',
        _testo(s.margin_left_mm + 5, s.margin_top_mm + 9, titolo, STANDARD.text_normal_mm),
    ]


def foglio_a_scala_reale(libreria: SymbolRegistry) -> str:
    s = STANDARD
    parti = _apri(
        "REL-003 — i simboli nuovi accanto a quelli di oggi · scala reale: 1 mm del foglio = "
        "1 mm della tavola · proposta del 24 settembre 2026, da approvare"
    )
    x_famiglia = s.margin_left_mm + 5
    x_oggi = s.margin_left_mm + 70
    x_nuovo = s.margin_left_mm + 150
    y = s.margin_top_mm + 22
    parti.append(_testo(x_oggi, y - 6, "oggi", s.text_normal_mm))
    parti.append(_testo(x_nuovo, y - 6, "nuovo", s.text_normal_mm))
    for famiglia, oggi, nuovo in FAMIGLIE:
        altezza = 0.0
        parti.append(_testo(x_famiglia, y + TESTO_MM, famiglia, s.text_normal_mm))
        for colonna, identificativo in ((x_oggi, oggi), (x_nuovo, nuovo)):
            if identificativo is None:
                parti.append(_testo(colonna, y + TESTO_MM, "— (non c'è)"))
                continue
            if identificativo not in _presenti(libreria):
                parti.append(_mancante(colonna, y, identificativo))
                continue
            simbolo = libreria.get(identificativo)
            parti.append(_simbolo(simbolo, colonna, y))
            parti.append(
                _testo(
                    colonna,
                    y + simbolo.manifest.height_mm + TESTO_MM + 1.5,
                    f"{simbolo.manifest.name} — {simbolo.manifest.width_mm:g} × "
                    f"{simbolo.manifest.height_mm:g} mm",
                )
            )
            altezza = max(altezza, simbolo.manifest.height_mm)
        y += max(altezza, 10.0) + 14.0
    parti.append("</svg>")
    return "".join(parti)


def foglio_ingrandito(libreria: SymbolRegistry) -> str:
    s = STANDARD
    scala = 2.0
    parti = _apri("REL-003 — i simboli nuovi ingranditi due volte, con il nome di ogni attacco")
    # Due colonne: a sinistra le macchine larghe, a destra bollitore e ventilconvettore.
    colonne: list[list[str]] = [
        ["heat-pump-air-water-large", "gas-boiler-modular", "solar-collector"],
        ["dhw-cylinder-twin-coil", "fan-coil-ducted"],
    ]
    x_colonne = (s.margin_left_mm + 60.0, s.margin_left_mm + 285.0)
    for x, identificativi in zip(x_colonne, colonne, strict=True):
        y = s.margin_top_mm + 22
        for identificativo in identificativi:
            if identificativo not in _presenti(libreria):
                parti.append(_mancante(x, y, identificativo))
                y += 20
                continue
            simbolo = libreria.get(identificativo)
            parti.append(_simbolo(simbolo, x, y, scala=scala, attacchi=True))
            parti.append(
                _testo(x, y + simbolo.manifest.height_mm * scala + TESTO_MM + 2.5, simbolo.manifest.name)
            )
            y += simbolo.manifest.height_mm * scala + 16.0
    parti.append("</svg>")
    return "".join(parti)


def main(argomenti: list[str]) -> None:
    if len(argomenti) != 1:
        raise SystemExit("uso: foglio-simboli.py <cartella di uscita>")
    uscita = Path(argomenti[0])
    uscita.mkdir(parents=True, exist_ok=True)
    libreria = SymbolRegistry.from_directory(RADICE / "assets" / "symbols")
    (uscita / "foglio-1-scala-reale.svg").write_text(foglio_a_scala_reale(libreria), encoding="utf-8")
    (uscita / "foglio-2-ingrandito.svg").write_text(foglio_ingrandito(libreria), encoding="utf-8")
    print(uscita / "foglio-1-scala-reale.svg")
    print(uscita / "foglio-2-ingrandito.svg")


if __name__ == "__main__":
    main(sys.argv[1:])
