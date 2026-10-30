"""Il foglio delle porte di comando di `REL-012` fase 3, per il PO: dove stanno, su quale faccia.

Uso, dalla radice del repository:

    PYTHONPATH=src python3 docs/collaudi/REL-012/fase-3/foglio_delle_porte.py

Ogni simbolo che ha porte elettriche e di comando (`control_ports` del manifesto) e' disegnato
come nel foglio dei simboli di `REL-012/simboli/` — al doppio con tutte le porte marcate e
nominate, e accanto a misura vera —: le porte dell'acqua in blu, quelle di comando in rosso. Il
corpo dei simboli **non e' cambiato**: le porte di comando sono nuove, e sono **facoltative**
(senza un cavo nel grafo non esistono per il disegno). **Proposta della sessione**, da
approvare sulla tavola.

Riusa la cella del foglio dei simboli; scrive `foglio-delle-porte.svg` e `.pdf` qui accanto.
"""

import importlib.util
import json
from pathlib import Path

from disegnatore_mep.graphics.pdf import svg_in_pdf
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry

QUI = Path(__file__).resolve().parent
ROOT = QUI.parents[3]

_spec = importlib.util.spec_from_file_location(
    "foglio_dei_simboli", ROOT / "docs/collaudi/REL-012/simboli/foglio_dei_simboli.py"
)
assert _spec is not None and _spec.loader is not None
fds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fds)

LARGHEZZA = 420.0


def domini_interi() -> dict[tuple[str, str], str]:
    """Il dominio di ogni porta dalle voci intere del catalogo, porte di comando comprese
    (il registro le tiene da parte, il file le porta)."""
    trovati: dict[tuple[str, str], str] = {}
    for percorso in sorted((ROOT / "examples/layout/catalog").glob("*.json")):
        voce = json.loads(percorso.read_text("utf-8"))
        for porta in voce["ports"]:
            trovati.setdefault((voce["symbol_id"], porta["id"]), porta["domain"])
    return trovati


def con_tutte_le_porte(simbolo: Symbol) -> Symbol:
    """Il simbolo con le porte di comando fra le altre, solo per marcarle sul foglio."""
    m = simbolo.manifest
    return Symbol(
        manifest=m.model_construct(**{**dict(m), "ports": [*m.ports, *m.control_ports]}),
        body=simbolo.body,
    )


def foglio() -> str:
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    i_domini = domini_interi()
    con_comando = [item for item in simboli.all() if item.manifest.control_ports]
    parti: list[str] = [
        f'<text x="{fds.MARGINE:g}" y="{fds.MARGINE + 2:g}" font-size="5" font-weight="bold" fill="black" '
        f'stroke="none">REL-012 fase 3 — le porte elettriche e di comando, proposta</text>',
        f'<text x="{fds.MARGINE:g}" y="{fds.MARGINE + 8:g}" font-size="2.6" fill="#333333" stroke="none">'
        "Blu: le porte dell'acqua, come sono. Rosso: le porte di comando nuove — power alimentazione, bus "
        "bus di comando, comando attuatore della valvola, signal segnale della sonda. Facoltative: senza un "
        "cavo nel grafo non esistono per il disegno.</text>",
    ]
    y = fds.MARGINE + 16.0
    x, alto_riga = fds.MARGINE, 0.0
    for simbolo in con_comando:
        svg, largo, alto = fds.cella(
            con_tutte_le_porte(simbolo),
            ", ".join(sorted(simbolo.manifest.control_port_ids)),
            i_domini,
            f"versione {simbolo.manifest.version}",
        )
        if x + largo > LARGHEZZA - fds.MARGINE:
            x, y, alto_riga = fds.MARGINE, y + alto_riga + 4.0, 0.0
        parti.append(f'<g transform="translate({x:g} {y:g})">{svg}</g>')
        x += largo + fds.SPAZIO
        alto_riga = max(alto_riga, alto)
    altezza = round(y + alto_riga + 2 * fds.MARGINE)
    testa = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGHEZZA:g}mm" height="{altezza:g}mm" '
        f'viewBox="0 0 {LARGHEZZA:g} {altezza:g}" font-family="Arial, Helvetica, sans-serif">'
        f'<rect x="0" y="0" width="{LARGHEZZA:g}" height="{altezza:g}" fill="white" stroke="none"/>'
    )
    return testa + "".join(parti) + "</svg>"


def main() -> None:
    svg = foglio()
    (QUI / "foglio-delle-porte.svg").write_text(svg, encoding="utf-8")
    esito = svg_in_pdf(svg, titolo="REL-012 fase 3 — le porte di comando")
    (QUI / "foglio-delle-porte.pdf").write_bytes(esito.dati)


if __name__ == "__main__":
    main()
