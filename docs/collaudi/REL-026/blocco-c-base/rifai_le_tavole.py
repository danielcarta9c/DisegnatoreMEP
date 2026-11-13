"""Le tavole del collaudo della voce C-3 di REL-026 (la base architettonica), prima e dopo.

    .venv/bin/python docs/collaudi/REL-026/blocco-c-base/rifai_le_tavole.py

«Prima» e' la base del lavoro (`ff89e30`, i blocchi A e B uniti): le sue sorgenti si estraggono
con `git archive` in una cartella temporanea, e il disegno gira li', in un processo a parte.
«Dopo» e' il codice del ramo. Le tavole vanno nelle cartelle accanto a questo file:

- `t3/` — il collaudo T3 del banco (la pianta e il grafo di REL-012), prima e dopo;
- `sagome/` — il caso anonimo di B-2, `examples/pianta/casi/sagome-muri.json`, prima e dopo;
- `anonimo/` — il caso anonimo di C-3, `examples/pianta/casi/base-anonima.json`: la planimetria
  d'origine (inventata, con arredi e quote), la base standard sola, la sovrapposizione del
  controllo a vista e la tavola con l'impianto.

Formato, scala e avvisi di ognuna in `misure.txt`. Nessun dato di cliente: i casi sono anonimi.
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
sys.path.insert(0, str(RADICE / "src"))

from disegnatore_mep.graphics.cartiglio import Cartiglio  # noqa: E402
from disegnatore_mep.pianta.comando import disegna_la_pianta  # noqa: E402
from disegnatore_mep.pianta.sovrapposizione import controlla_a_vista  # noqa: E402
from disegnatore_mep.skill import anteprima  # noqa: E402

CARTIGLIO = RADICE / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
CATALOGO = RADICE / "examples" / "layout" / "catalog"
NOMI = RADICE / "naming"
T3_BANCO = RADICE / "docs" / "collaudi" / "REL-012" / "collaudo-t3"
CASI = RADICE / "examples" / "pianta" / "casi"

ESEGUI_LA_BASE = """
import sys
from pathlib import Path
from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.pianta.comando import disegna_la_pianta
sorgente, cartella, cartiglio, grafo, catalogo, nomi = sys.argv[1:7]
e = disegna_la_pianta(Path(sorgente), Path(cartella), Cartiglio.da_file(Path(cartiglio)), dxf=False, png=True,
                      grafo=Path(grafo) if grafo != "-" else None, catalogo=Path(catalogo), nomi=Path(nomi))
print(e.tavola.formato, e.tavola.scala, len(e.avvisi or []))
"""


def _pulisci(cartella: Path) -> Path:
    if cartella.exists():
        shutil.rmtree(cartella)
    cartella.mkdir(parents=True)
    return cartella


def _tieni(cartella: Path, anche: tuple[str, ...] = ()) -> None:
    """Restano i PNG, il PDF della tavola intera e i formati in `anche`; il resto si rifa' qui."""
    for file in cartella.rglob("*"):
        tenuto = file.name.endswith((".png", *anche)) or (file.suffix == ".pdf" and "-dettaglio-" not in file.name)
        if file.is_file() and not tenuto:
            file.unlink()


def prima(sorgente: Path, cartella: Path, base: Path, grafo: Path | None = None) -> str:
    _pulisci(cartella)
    uscita = subprocess.run(
        [sys.executable, "-c", ESEGUI_LA_BASE, str(sorgente), str(cartella), str(CARTIGLIO), str(grafo or "-"),
         str(CATALOGO), str(NOMI)],
        env={"PYTHONPATH": str(base / "src"), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True,
    )
    _tieni(cartella)
    return uscita.stdout.strip()


def dopo(sorgente: Path, cartella: Path, grafo: Path | None = None, dxf: bool = False) -> str:
    _pulisci(cartella)
    e = disegna_la_pianta(sorgente, cartella, Cartiglio.da_file(CARTIGLIO), dxf=dxf, png=True, grafo=grafo,
                          catalogo=CATALOGO, nomi=NOMI)
    _tieni(cartella, (".dxf",) if dxf else ())
    return f"{e.tavola.formato} {e.tavola.scala} {len(e.avvisi or [])}"


def anonimo(cartella: Path, lavoro: Path) -> list[str]:
    """Il caso di C-3: l'origine, la base sola, la sovrapposizione, la tavola con l'impianto."""
    _pulisci(cartella)
    righe: list[str] = []
    origine = CASI / "base-anonima" / "planimetria.pdf"
    anteprima(origine, cartella / "1-origine.png", 110)
    # La base standard sola: la stessa pianta senza pezzi, tracciati e zone esterne.
    dati = json.loads((CASI / "base-anonima.json").read_text(encoding="utf-8"))
    dati.update(pezzi=[], tracciati=[], zone_esterne=[], titolo="Base standard")
    dati["sfondo"]["file"] = str(origine)
    lavoro.mkdir(parents=True, exist_ok=True)
    sola = lavoro / "base-sola.json"
    sola.write_text(json.dumps(dati, ensure_ascii=False), encoding="utf-8")
    e = disegna_la_pianta(sola, lavoro / "base", Cartiglio.da_file(CARTIGLIO), dxf=False, png=True)
    shutil.copyfile(lavoro / "base" / "base-sola.png", cartella / "2-base-standard.png")
    righe.append(f"anonimo base standard: {e.tavola.formato} {e.tavola.scala}")
    vista = controlla_a_vista(CASI / "base-anonima.json", lavoro / "vista")
    for file in vista.file:
        if file.name.endswith("-sovrapposizione.png"):
            shutil.copyfile(file, cartella / "3-sovrapposizione.png")
        if file.name.endswith("-sovrapposizione.pdf"):
            shutil.copyfile(file, cartella / "3-sovrapposizione.pdf")
    righe += [f"anonimo sovrapposizione: {r}" for r in vista.righe if r.startswith(("Base:", "Porte:", "Superfici:"))]
    e = disegna_la_pianta(CASI / "base-anonima.json", lavoro / "impianto", Cartiglio.da_file(CARTIGLIO), dxf=True,
                          png=True)
    shutil.copyfile(lavoro / "impianto" / "base-anonima.png", cartella / "4-impianto.png")
    shutil.copyfile(lavoro / "impianto" / "base-anonima.pdf", cartella / "4-impianto.pdf")
    shutil.copyfile(lavoro / "impianto" / "base-anonima.dxf", cartella / "4-impianto.dxf")
    righe.append(f"anonimo impianto: {e.tavola.formato} {e.tavola.scala}, bloccanti {len(e.rilievi.bloccanti)}")
    return righe


def principale() -> int:
    with tempfile.TemporaryDirectory() as temporanea:
        base = Path(temporanea) / "base"
        base.mkdir()
        archivio = Path(temporanea) / "base.tar"
        with archivio.open("wb") as uscita:
            subprocess.run(["git", "-C", str(RADICE), "archive", BASE, "src", "rules", "naming"], stdout=uscita,
                           check=True)
        with tarfile.open(archivio) as tar:
            tar.extractall(base, filter="data")
        misure: list[str] = []
        pianta_t3, grafo_t3 = T3_BANCO / "pianta.json", T3_BANCO / "grafo-completo.json"
        misure.append(f"t3 prima: {prima(pianta_t3, QUI / 't3' / 'prima', base, grafo=grafo_t3)}")
        misure.append(f"t3 dopo: {dopo(pianta_t3, QUI / 't3' / 'dopo', grafo=grafo_t3)}")
        sagome = CASI / "sagome-muri.json"
        misure.append(f"sagome prima: {prima(sagome, QUI / 'sagome' / 'prima', base)}")
        misure.append(f"sagome dopo: {dopo(sagome, QUI / 'sagome' / 'dopo', dxf=True)}")
        misure += anonimo(QUI / "anonimo", Path(temporanea) / "anonimo")
    (QUI / "misure.txt").write_text("\n".join(misure) + "\n", encoding="utf-8")
    print("\n".join(misure))
    return 0


if __name__ == "__main__":
    raise SystemExit(principale())
