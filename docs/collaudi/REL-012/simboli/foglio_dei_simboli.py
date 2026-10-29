"""Il foglio dei simboli di `REL-012` per il PO: i segni nuovi, da approvare sulla tavola.

Ogni simbolo e' disegnato **due volte**: grande, al doppio, con le porte marcate e
il loro nome — per giudicare la forma —, e accanto a misura vera, come esce sulla
tavola — per giudicare se si legge. Sotto: il nome che va in legenda, la sigla
della famiglia (dal catalogo e da `naming/families.json`), le rotazioni ammesse.
L'ultima riga porta tre simboli idronici gia' approvati, per il confronto di stile.

Il colore della porta e' il suo dominio, dal catalogo: blu l'acqua, verde l'aria,
viola il refrigerante, grigio la condensa, rosso il comando.

Uso, dalla radice del repository:

    PYTHONPATH=src python3 docs/collaudi/REL-012/simboli/foglio_dei_simboli.py

Scrive `foglio-dei-simboli.svg` e `.pdf` qui accanto; il PNG si ricava dal PDF con
`pdftoppm -png -r 150 -singlefile foglio-dei-simboli.pdf foglio-dei-simboli`.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming
from disegnatore_mep.graphics.pdf import larghezza_della_scritta, svg_in_pdf
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE

ROOT = Path(__file__).resolve().parents[4]
QUI = Path(__file__).resolve().parent

NUOVI_DEL_KIT = [
    "split-outdoor-unit",
    "ducted-indoor-unit",
    "zoning-plenum-5",
    "zone-controller",
    "electrical-panel",
    "air-diffuser",
    "return-grille",
    "condensate-trap",
    "condensate-outlet",
    "isolator-switch",
    "room-thermostat",
    "wired-remote",
]
NUOVI_DELLA_SESSIONE = ["plant-controller", "temperature-probe", "outdoor-temperature-probe"]
CONFRONTO = ["heat-pump-air-water", "pump-circulator", "thermometer"]

SCALA = 2.0
LARGHEZZA = 841.0
"""La larghezza di un A1: al doppio, plenum e centrale di zona chiedono spazio.
L'altezza e' quella che il contenuto chiede."""
MARGINE = 12.0
CORPO = 2.5
CORPO_PORTA = 1.6
SPAZIO = 8.0
COLORE_DEL_DOMINIO = {
    "hydronic": "#1f5fbf",
    "aeraulic": "#138a5e",
    "refrigerant": "#7b3fa0",
    "condensate": "#666666",
    "control": "#c0392b",
    "gas": "#b8860b",
}


def _x(testo: str) -> str:
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sigle(catalogo: ComponentRegistry, naming: Naming) -> dict[str, list[str]]:
    """Le sigle di famiglia delle voci che usano ciascun simbolo."""
    trovate: dict[str, list[str]] = {}
    for voce in catalogo.all():
        famiglia = naming.family_of(tuple(voce.functions), voce.id).prefix
        elenco = trovate.setdefault(voce.symbol_id, [])
        if famiglia not in elenco:
            elenco.append(famiglia)
    return trovate


def domini(catalogo: ComponentRegistry) -> dict[tuple[str, str], str]:
    """Il dominio di ogni porta, dalla prima voce che usa il simbolo."""
    trovati: dict[tuple[str, str], str] = {}
    for voce in catalogo.all():
        for porta in voce.ports:
            trovati.setdefault((voce.symbol_id, porta.id), porta.domain.value)
    return trovati


def cella(simbolo: Symbol, sigla: str, dominio: dict[tuple[str, str], str], titolo: str) -> tuple[str, float, float]:
    """Una cella: il simbolo al doppio con le porte, a misura vera, e le scritte.

    Restituisce l'SVG con l'origine nell'angolo in alto a sinistra, e la misura."""
    m = simbolo.manifest
    w, h = m.width_mm * SCALA, m.height_mm * SCALA
    tratto = A3_LANDSCAPE.line_mm(m.stroke_weight)
    sx = 14.0  # posto a sinistra per i nomi delle porte sulla faccia sinistra
    sy = 6.0  # e in alto per quelli sulla faccia alta
    parti = [
        f'<g transform="translate({sx:g} {sy:g}) scale({SCALA:g})" stroke="black" '
        f'stroke-width="{tratto / SCALA * 1.4:g}" fill="none">{simbolo.body}</g>'
    ]
    destra = 0.0
    for porta in m.ports:
        colore = COLORE_DEL_DOMINIO.get(dominio.get((m.id, porta.id), ""), "#000000")
        px, py = sx + porta.x_mm * SCALA, sy + porta.y_mm * SCALA
        parti.append(f'<circle cx="{px:g}" cy="{py:g}" r="0.9" fill="{colore}" stroke="none"/>')
        faccia = porta.face.value if hasattr(porta.face, "value") else str(porta.face)
        largo = larghezza_della_scritta(porta.id, CORPO_PORTA)
        tx, ty, ancora = {
            "left": (px - 1.6, py - 0.6, "end"),
            "right": (px + 1.6, py - 0.6, "start"),
            "top": (px + 0.9, py - 1.4, "start"),
            "bottom": (px + 0.9, py + 2.6, "start"),
        }[faccia]
        if faccia == "right":
            destra = max(destra, 1.6 + largo)
        parti.append(
            f'<text x="{tx:g}" y="{ty:g}" font-size="{CORPO_PORTA}" text-anchor="{ancora}" '
            f'fill="{colore}" stroke="none">{_x(porta.id)}</text>'
        )
    # A misura vera, accanto.
    vx = sx + w + destra + 6.0
    parti.append(
        f'<g transform="translate({vx:g} {sy:g})" stroke="black" stroke-width="{tratto:g}" '
        f'fill="none">{simbolo.body}</g>'
        f'<text x="{vx:g}" y="{sy + m.height_mm + 3.0:g}" font-size="1.8" fill="#555555" '
        f'stroke="none">1:1</text>'
    )
    larghezza_disegno = vx + m.width_mm
    basso = sy + max(h, m.height_mm + 3.0) + 5.5
    righe = [
        (f"{sigla}  ·  {m.name}", CORPO, "black", True),
        (f"{m.id}  ·  {m.width_mm:g} x {m.height_mm:g} mm  ·  rotazioni {m.allowed_rotations_deg}", 1.9, "#444444", False),
        (titolo, 1.9, "#444444", False),
    ]
    y = basso
    larghezza_testo = 0.0
    for testo, corpo, colore, grassetto in righe:
        peso = ' font-weight="bold"' if grassetto else ""
        parti.append(
            f'<text x="{sx:g}" y="{y:g}" font-size="{corpo}" fill="{colore}" stroke="none"{peso}>{_x(testo)}</text>'
        )
        larghezza_testo = max(larghezza_testo, sx + larghezza_della_scritta(testo, corpo, grassetto))
        y += corpo + 1.6
    return "".join(parti), max(larghezza_disegno, larghezza_testo), y


def foglio() -> str:
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)
    naming = Naming.from_directory(ROOT / "naming")
    le_sigle, i_domini = sigle(catalogo, naming), domini(catalogo)

    gruppi = [
        ("Dal kit aria-aria del PO (I-224) — proposta della sessione del 29/10, forma da approvare", NUOVI_DEL_KIT,
         "kit AA-01, da approvare"),
        ("Comando nell'idronico (I-226) — proposte della sessione, forma e sigla da approvare", NUOVI_DELLA_SESSIONE,
         "proposta REL-012 fase 3, da approvare"),
        ("Per confronto: simboli idronici gia' approvati", CONFRONTO, "gia' in libreria"),
    ]
    parti: list[str] = [
        f'<text x="{MARGINE:g}" y="{MARGINE + 2:g}" font-size="5" font-weight="bold" fill="black" stroke="none">'
        f"REL-012 — i simboli nuovi, per l'approvazione del PO</text>",
        f'<text x="{MARGINE:g}" y="{MARGINE + 8:g}" font-size="2.6" fill="#333333" stroke="none">'
        f"Ogni simbolo al doppio, con le porte marcate e nominate, e accanto a misura vera (1:1). "
        f"Colore della porta = dominio: blu acqua, verde aria, viola refrigerante, grigio condensa, rosso comando "
        f"(alimentazione, collegamento, bus).</text>",
    ]
    y = MARGINE + 16.0
    for titolo, ids, nota in gruppi:
        if not ids:
            continue
        parti.append(
            f'<text x="{MARGINE:g}" y="{y + 3:g}" font-size="3.2" font-weight="bold" fill="black" '
            f'stroke="none">{_x(titolo)}</text>'
            f'<line x1="{MARGINE:g}" y1="{y + 4.5:g}" x2="{LARGHEZZA - MARGINE:g}" y2="{y + 4.5:g}" '
            f'stroke="#999999" stroke-width="0.2"/>'
        )
        y += 8.0
        x, alto_riga = MARGINE, 0.0
        for simbolo_id in ids:
            simbolo = simboli.get(simbolo_id)
            sigla = " / ".join(le_sigle.get(simbolo_id, ["—"]))
            svg, largo, alto = cella(simbolo, sigla, i_domini, nota)
            if x + largo > LARGHEZZA - MARGINE:
                x, y, alto_riga = MARGINE, y + alto_riga + 4.0, 0.0
            parti.append(f'<g transform="translate({x:g} {y:g})">{svg}</g>')
            x += largo + SPAZIO
            alto_riga = max(alto_riga, alto)
        y += alto_riga + 6.0
    altezza = round(y + MARGINE)
    testa = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARGHEZZA:g}mm" height="{altezza:g}mm" '
        f'viewBox="0 0 {LARGHEZZA:g} {altezza:g}" font-family="Arial, Helvetica, sans-serif">'
        f'<rect x="0" y="0" width="{LARGHEZZA:g}" height="{altezza:g}" fill="white" stroke="none"/>'
    )
    return testa + "".join(parti) + "</svg>"


def main() -> None:
    svg = foglio()
    (QUI / "foglio-dei-simboli.svg").write_text(svg, encoding="utf-8")
    esito = svg_in_pdf(svg, titolo="REL-012 — i simboli nuovi")
    (QUI / "foglio-dei-simboli.pdf").write_bytes(esito.dati)
    if esito.sostituzioni:
        print("caratteri sostituiti:", esito.sostituzioni)


if __name__ == "__main__":
    main()
