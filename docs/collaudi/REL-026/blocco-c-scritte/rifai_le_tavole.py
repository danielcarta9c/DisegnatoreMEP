"""Le tavole del collaudo del blocco C di REL-026 (C-1 e C-2, le scritte), prima e dopo.

    .venv/bin/python docs/collaudi/REL-026/blocco-c-scritte/rifai_le_tavole.py

«Prima» e' la base del blocco (`ff89e30`, il ramo della sessione coi blocchi A e B): le sue
sorgenti si estraggono con `git archive` in una cartella temporanea, e il disegno gira li',
in un processo a parte. «Dopo» e' il codice del ramo. Una cartella per caso, accanto a
questo file, con `prima/` e `dopo/`: SVG, PDF e PNG di ogni tavola (anche dei riquadri di
dettaglio), e i tracciati.

- `t3/` — il collaudo T3 del banco (`docs/collaudi/REL-012/collaudo-t3`, col grafo in sola
  lettura, come il banco): prima con tre dettagli automatici, A, B e C;
- `t3-esempio/` — il T3 di `examples/pianta/casi/collaudo-t3.json`, con distinta e grafo
  (i casi delle prove): prima con un dettaglio automatico;
- `sagome/` — `examples/pianta/casi/sagome-muri.json`: il dettaglio A lo chiede la pianta, e
  resta;
- `appartamento/` — l'appartamento aria-aria della skill: prima con due dettagli automatici;
- `fitta/` — il caso anonimo di questo blocco, `examples/pianta/casi/centrale-fitta.json`: la
  centrale in un locale tecnico piccolo, e mandata e ritorno dei ventilconvettori.

Le misure di ogni tavola vanno in `misure.txt`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
BASE = "ff89e30"
CARTIGLIO = RADICE / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
CATALOGO = RADICE / "examples" / "layout" / "catalog"
NOMI = RADICE / "naming"
T3_BANCO = RADICE / "docs" / "collaudi" / "REL-012" / "collaudo-t3"
ESEMPI = RADICE / "examples" / "pianta"
CASI = ESEMPI / "casi"

DISEGNA = """
import json, sys
from pathlib import Path
from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.pianta.comando import disegna_la_pianta
sorgente, cartella, cartiglio, distinta, grafo, catalogo, nomi = sys.argv[1:8]
e = disegna_la_pianta(Path(sorgente), Path(cartella), Cartiglio.da_file(Path(cartiglio)), dxf=False, png=True,
                      distinta=Path(distinta) if distinta != "-" else None,
                      grafo=Path(grafo) if grafo != "-" else None, catalogo=Path(catalogo), nomi=Path(nomi))
r = e.rilievi
print(json.dumps({
    "formato": e.tavola.formato, "scala": e.tavola.scala,
    "dettagli": [f"{d.formato}" for d in e.dettagli or []],
    "scritte_nel_dettaglio": r.scritte_nel_dettaglio,
    "scritte_in_legenda": len(r.scritte_in_legenda),
    "scritte_fuori_pianta": getattr(r, "scritte_fuori_pianta", []),
    "richiamo_fuori_piu_lungo_mm": round(getattr(r, "richiamo_fuori_piu_lungo_mm", 0.0), 1),
    "richiami_che_si_incrociano": len(getattr(r, "richiami_che_si_incrociano", [])),
    "richiami_fuori_sopra": getattr(r, "richiami_fuori_sopra", []),
    "scritte_senza_posto": [c for c, s in e.tavola.scritte if not s.libera],
    "bloccanti": r.bloccanti,
}, ensure_ascii=False))
"""


def _pulisci(cartella: Path) -> Path:
    if cartella.exists():
        shutil.rmtree(cartella)
    cartella.mkdir(parents=True)
    return cartella


def disegna(sorgente: Path, cartella: Path, sorgenti: Path, distinta: Path | None = None,
            grafo: Path | None = None) -> dict[str, object]:
    """Il disegno con le sorgenti date (la base o il ramo), in un processo a parte. Il grafo
    si legge soltanto: `disegna_la_pianta` lo scrive solo se glielo si chiede."""
    _pulisci(cartella)
    uscita = subprocess.run(
        [sys.executable, "-c", DISEGNA, str(sorgente), str(cartella), str(CARTIGLIO), str(distinta or "-"),
         str(grafo or "-"), str(CATALOGO), str(NOMI)],
        env={"PYTHONPATH": str(sorgenti / "src"), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True,
        check=True,
    )
    for file in cartella.rglob("*"):
        if file.is_file() and not file.name.endswith((".svg", ".pdf", ".png", ".tracciati.json")):
            file.unlink()
    return json.loads(uscita.stdout.strip().splitlines()[-1])  # type: ignore[no-any-return]


def principale() -> int:
    casi: list[tuple[str, Path, Path | None, Path | None]] = [
        ("t3", T3_BANCO / "pianta.json", None, T3_BANCO / "grafo-completo.json"),
        ("t3-esempio", CASI / "collaudo-t3.json", CASI / "collaudo-t3.distinta.json",
         CASI / "collaudo-t3.grafo-completo.json"),
        ("sagome", CASI / "sagome-muri.json", None, None),
        ("appartamento", ESEMPI / "appartamento-aria-aria.json", None, None),
        ("fitta", CASI / "centrale-fitta.json", None, None),
    ]
    misure: list[str] = []
    with tempfile.TemporaryDirectory() as temporanea:
        base = Path(temporanea) / "base"
        base.mkdir()
        archivio = Path(temporanea) / "base.tar"
        with archivio.open("wb") as uscita:
            subprocess.run(["git", "-C", str(RADICE), "archive", BASE, "src", "rules", "naming"], stdout=uscita,
                           check=True)
        with tarfile.open(archivio) as tar:
            tar.extractall(base, filter="data")
        for nome, sorgente, distinta, grafo in casi:
            for quando, sorgenti in (("prima", base), ("dopo", RADICE)):
                esito = disegna(sorgente, QUI / nome / quando, sorgenti, distinta, grafo)
                misure.append(f"{nome} {quando}: {json.dumps(esito, ensure_ascii=False)}")
                print(misure[-1])
    (QUI / "misure.txt").write_text(
        "# per caso, prima e dopo: formato e scala, i riquadri di dettaglio (il loro formato), le scritte\n"
        "# rimandate al dettaglio, quante in legenda, quelle fuori dalla pianta col richiamo, i richiami che\n"
        "# si incrociano, quelli sopra scritte o pezzi, le scritte senza posto, i bloccanti (rifai_le_tavole.py)\n"
        + "\n".join(misure) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(principale())
