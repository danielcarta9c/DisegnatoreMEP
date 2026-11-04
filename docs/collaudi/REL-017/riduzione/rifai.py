"""Rifa' i ritagli della riduzione all'attacco (I-281, D-233), dalla radice del repository:

    PYTHONPATH=src python3 docs/collaudi/REL-017/riduzione/rifai.py

La villetta di riferimento (`docs/collaudi/REL-017/diametri/grafo.json`, Shenling 12 kW con
5 K, diametri chiesti sul primario; il piano dell'idraulica di `REL-015/pdc-regola`) in tre
varianti: il calcolo (MS 32×3, riduzione 1¼"×1"), la 15 kW del calcolo (MS 40×3,5, nessuna
riduzione) e la 15 kW con l'MS 32×3 del progettista (riduzione). Completa, disegna, la
tavola in PNG a 200 dpi, e il ritaglio attorno alla pompa di calore, dove stanno il giunto e
la riduzione. Il ritaglio si prende dalle coordinate della pompa di calore nell'SVG, cosi'
segue la macchina se il piano la sposta.
"""

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image  # noqa: E402

from disegnatore_mep.skill import cartelle_del_repository, main  # noqa: E402

VILLETTA = ROOT / "docs" / "collaudi" / "REL-017" / "diametri" / "grafo.json"
PIANO = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola" / "piano-idraulica.json"
DPI = 200
MARGINE_MM = (25.0, 30.0, 95.0, 45.0)
"""Quanto si prende attorno alla pompa di calore: a sinistra, sopra, a destra, sotto. A
destra fino al raccordo della sicurezza e al vaso, che dicono che cosa viene dopo."""


def _variante(potenza: float, sezione: str | None) -> dict[str, Any]:
    testo: dict[str, Any] = json.loads(VILLETTA.read_text(encoding="utf-8"))
    for pezzo in testo["components"]:
        if pezzo["id"] == "pdc":
            pezzo["properties"]["power_kw"] = potenza
    if sezione is not None:
        for tubo in testo["connections"]:
            if tubo["network_id"] == "primario":
                tubo["sezione"] = sezione
    return testo


VARIANTI = [
    ("villetta-12kw-ms32-calcolo", _variante(12, None)),
    ("villetta-15kw-ms40-calcolo", _variante(15, None)),
    ("villetta-15kw-ms32-del-progettista", _variante(15, "MS 32×3")),
]


def _esegui(argomenti: list[str]) -> str:
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        main(argomenti, cartelle_del_repository(ROOT))
    return uscita.getvalue()


def _riquadro_della_pdc(svg: str) -> tuple[float, float, float, float]:
    """Il riquadro del simbolo della pompa di calore nell'SVG, in millimetri di carta."""
    gruppo = re.search(r'<g[^>]*data-component-id="pdc"[^>]*>', svg)
    if gruppo is None:
        raise SystemExit("la pompa di calore non si trova nell'SVG")
    trasla = re.search(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)", gruppo.group(0))
    if trasla is None:
        raise SystemExit(f"la pompa di calore non ha una traslazione: {gruppo.group(0)}")
    x, y = float(trasla.group(1)), float(trasla.group(2))
    return x, y, x + 40.0, y + 30.0


def main_() -> None:
    for vecchio in QUI.glob("*.png"):
        vecchio.unlink()
    resoconto = ["# La riduzione all'attacco: le uscite di completa (I-281, D-233)\n"]
    with tempfile.TemporaryDirectory() as lavoro_:
        lavoro = Path(lavoro_)
        for nome, testo in VARIANTI:
            grafo, completo = lavoro / f"{nome}.json", lavoro / f"{nome}-completo.json"
            grafo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
            uscita = _esegui(["completa", str(grafo), "--out", str(completo)])
            righe = [r for r in uscita.splitlines() if r.startswith("Riduzioni") or "riduzione " in r]
            resoconto.append(f"\n## {nome}\n\n```\n" + ("\n".join(righe) or "(nessuna riduzione)") + "\n```\n")
            cartella = lavoro / nome
            disegna = _esegui(["disegna", str(completo), "--piano", str(PIANO), "--out", str(cartella), "--senza-dxf"])
            resoconto.append("\n" + next(r for r in disegna.splitlines() if r.startswith("Formato")) + "\n")
            (pdf,) = cartella.glob("*.pdf")
            (svg,) = cartella.glob("*.svg")
            intera = lavoro / f"{nome}.png"
            subprocess.run(["pdftoppm", "-png", "-r", str(DPI), "-singlefile", str(pdf), str(intera.with_suffix(""))], check=True)
            x0, y0, x1, y1 = _riquadro_della_pdc(svg.read_text(encoding="utf-8"))
            sinistra, sopra, destra, sotto = MARGINE_MM
            px = DPI / 25.4
            with Image.open(intera) as immagine:
                immagine.crop(
                    (
                        round((x0 - sinistra) * px),
                        round((y0 - sopra) * px),
                        round((x1 + destra) * px),
                        round((y1 + sotto) * px),
                    )
                ).save(QUI / f"{nome}.png")
    (QUI / "uscite.md").write_text("".join(resoconto), encoding="utf-8")
    print("\n".join(sorted(p.name for p in QUI.glob("*.png"))))


if __name__ == "__main__":
    main_()
