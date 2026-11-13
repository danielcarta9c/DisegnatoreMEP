"""Le tavole del collaudo del blocco B di REL-026, prima e dopo.

    .venv/bin/python docs/collaudi/REL-026/blocco-b/rifai_le_tavole.py

«Prima» e' la base del pacchetto (`d9c8f2e`, la 2.0.0 con il pacchetto scritto): le sue
sorgenti si estraggono con `git archive` in una cartella temporanea, e il disegno gira
li', in un processo a parte. «Dopo» e' il codice del ramo. Le tavole vanno nelle
cartelle accanto a questo file, una per caso:

- `t3/` — il collaudo T3 (la pianta e il grafo del banco): prima, dopo (forature spente
  di base, B-3), dopo con `"forature": true`;
- `sagome/` — il caso anonimo `examples/pianta/casi/sagome-muri.json` (B-2): senza le
  sagome (i rettangoli asse-spessore) e con, ciascuno col suo dettaglio A; con il DXF;
- `discordanze/` — il T3 con 49 discordanze (B-5): prima con distinta e grafo (A1), dopo
  con distinta e grafo, dopo senza confronto;
- `lunghezze/` — la prova di accettazione di B-4 sul T3 anonimo: la pianta al primo giro,
  la pianta dopo aver spostato TA-01, la tavola dello schema rifatta dal grafo aggiornato.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
BASE = "d9c8f2e"
sys.path.insert(0, str(RADICE / "src"))

from disegnatore_mep.graphics.cartiglio import Cartiglio  # noqa: E402
from disegnatore_mep.pianta.comando import disegna_la_pianta  # noqa: E402
from disegnatore_mep.skill import cartelle_del_repository  # noqa: E402
from disegnatore_mep.skill import main as skill  # noqa: E402

CARTIGLIO = RADICE / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
CATALOGO = RADICE / "examples" / "layout" / "catalog"
NOMI = RADICE / "naming"
T3_BANCO = RADICE / "docs" / "collaudi" / "REL-012" / "collaudo-t3"
CASI = RADICE / "examples" / "pianta" / "casi"

ESEGUI_LA_BASE = """
import sys
from pathlib import Path
from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.pianta.comando import disegna_la_pianta, riassunto
sorgente, cartella, cartiglio, distinta, grafo, catalogo, nomi = sys.argv[1:8]
e = disegna_la_pianta(Path(sorgente), Path(cartella), Cartiglio.da_file(Path(cartiglio)), dxf=False, png=True,
                      distinta=Path(distinta) if distinta != "-" else None,
                      grafo=Path(grafo) if grafo != "-" else None, catalogo=Path(catalogo), nomi=Path(nomi))
print(e.tavola.formato, e.tavola.scala, len(e.avvisi or []), len(e.confronto.avvisi) if e.confronto else 0)
"""


def _pulisci(cartella: Path) -> Path:
    if cartella.exists():
        shutil.rmtree(cartella)
    cartella.mkdir(parents=True)
    return cartella


def _tieni_le_tavole(cartella: Path, anche: tuple[str, ...] = (), pdf: bool = False) -> None:
    """Restano i PNG e i tracciati (e i formati in `anche`); con `pdf` anche il PDF della
    tavola intera. SVG, DXF e gli altri PDF si rifanno con questo script, e pesano (un PDF
    porta i caratteri: 220 KB); il logo del cartiglio no. Lo schema, che di suo non scrive
    l'anteprima, la riceve qui."""
    from disegnatore_mep.skill import anteprima

    for documento in cartella.rglob("*.pdf"):
        if not documento.with_suffix(".png").exists():
            anteprima(documento, documento.with_suffix(".png"), 110)
    for file in cartella.rglob("*"):
        tenuto = file.name.endswith((".png", ".tracciati.json", *anche)) or (
            pdf and file.suffix == ".pdf" and "-dettaglio-" not in file.name
        )
        if file.is_file() and not tenuto:
            file.unlink()


def prima(sorgente: Path, cartella: Path, base: Path, distinta: Path | None = None, grafo: Path | None = None) -> str:
    """Il disegno con le sorgenti della base, in un processo a parte."""
    _pulisci(cartella)
    uscita = subprocess.run(
        [sys.executable, "-c", ESEGUI_LA_BASE, str(sorgente), str(cartella), str(CARTIGLIO),
         str(distinta or "-"), str(grafo or "-"), str(CATALOGO), str(NOMI)],
        env={"PYTHONPATH": str(base / "src"), "PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=True,
    )
    _tieni_le_tavole(cartella)
    return uscita.stdout.strip()


def dopo(sorgente: Path, cartella: Path, dxf: bool = False, distinta: Path | None = None,
         grafo: Path | None = None, pdf: bool = True) -> str:
    _pulisci(cartella)
    e = disegna_la_pianta(sorgente, cartella, Cartiglio.da_file(CARTIGLIO), dxf=dxf, png=True, distinta=distinta,
                          grafo=grafo, catalogo=CATALOGO, nomi=NOMI)
    _tieni_le_tavole(cartella, (".dxf",) if dxf else (), pdf=pdf)
    return f"{e.tavola.formato} {e.tavola.scala} {len(e.avvisi or [])} {len(e.confronto.avvisi) if e.confronto else 0}"


def _variante(sorgente: Path, destinazione: Path, cambia) -> Path:  # type: ignore[no-untyped-def]
    dati = json.loads(sorgente.read_text(encoding="utf-8"))
    cambia(dati)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_text(json.dumps(dati, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return destinazione


def discordante(dati: dict) -> None:  # type: ignore[type-arg]
    """Lo stesso caso di `tests/pianta/test_rilievi_bd_rm_260.py` (B-5)."""
    nuove = {p["sigla"]: p["sigla"].replace("TA-", "BOC-") for p in dati["pezzi"] if p["sigla"].startswith("TA-")}
    for pezzo in dati["pezzi"]:
        pezzo["sigla"] = nuove.get(pezzo["sigla"], pezzo["sigla"])
    for tracciato in dati["tracciati"]:
        tracciato["tratta"] = f"T{int(tracciato['tratta'][1:]) + 40:02d}"
        if tracciato.get("lunghezza_m") is not None:
            tracciato["lunghezza_m"] += 1
        for capo in ("da", "a"):
            valore = tracciato[capo]
            if isinstance(valore, dict):
                valore["pezzo"] = nuove.get(valore["pezzo"], valore["pezzo"])
            else:
                tracciato[capo] = nuove.get(valore, valore)


def lunghezze(cartella: Path) -> list[str]:
    """La prova di accettazione di B-4 (come `test_1_…`/`test_2_…`/`test_3_…`)."""
    righe: list[str] = []
    lavoro = _pulisci(cartella / "ingressi")
    grafo = json.loads((CASI / "collaudo-t3.grafo-completo.json").read_text(encoding="utf-8"))
    misurate = ("ramo-matrimoniale", "ramo-singola", "ramo-soggiorno-varco", "ramo-soggiorno-parete",
                "bus-matrimoniale", "bus-singola", "bus-soggiorno", "cavo-comando-filo", "alim-quadro-sezionatore")
    for tubazione in grafo["connections"]:
        if tubazione["id"] in misurate:
            tubazione.pop("lunghezza_m")
    percorso_del_grafo = lavoro / "grafo-completo.json"
    percorso_del_grafo.write_text(json.dumps(grafo, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
                                  encoding="utf-8")
    shutil.copyfile(percorso_del_grafo, lavoro / "grafo-completo.prima.json")
    pianta = _variante(CASI / "collaudo-t3.json", lavoro / "pianta.json",
                       lambda d: [t.pop("lunghezza_m", None) for t in d["tracciati"]])
    cartelle = cartelle_del_repository(RADICE)

    def mep(*argv: str) -> str:
        testo = io.StringIO()
        with contextlib.redirect_stdout(testo):
            skill(list(argv), cartelle)
        return testo.getvalue()

    def grafo_e_avvisi(console: str) -> list[str]:
        return [r for r in console.splitlines() if r.startswith(("Grafo ", "  - T", "Lunghezze del", "Avviso: Senza"))]

    righe.append("== giro 1: pianta --grafo")
    righe += grafo_e_avvisi(mep("pianta", str(pianta), "--out", str(cartella / "giro-1"), "--senza-dxf",
                                "--grafo", str(percorso_del_grafo)))
    shutil.copyfile(percorso_del_grafo, lavoro / "grafo-completo.dopo-il-giro-1.json")
    righe.append("== giro 1 rilanciato uguale")
    righe += grafo_e_avvisi(mep("pianta", str(pianta), "--out", str(lavoro / "giro-1b"), "--senza-dxf",
                                "--grafo", str(percorso_del_grafo)))
    _variante(pianta, pianta, lambda d: next(p for p in d["pezzi"] if p["sigla"] == "TA-01").update(x=1.55))
    righe.append("== giro 2: TA-01 spostata di un metro verso ovest")
    righe += grafo_e_avvisi(mep("pianta", str(pianta), "--out", str(cartella / "giro-2"), "--senza-dxf",
                                "--grafo", str(percorso_del_grafo)))
    shutil.copyfile(percorso_del_grafo, lavoro / "grafo-completo.dopo-il-giro-2.json")
    mep("distinta", str(percorso_del_grafo), "--out", str(cartella / "distinta"))
    mep("disegna", str(percorso_del_grafo), "--piano", str(T3_BANCO / "piano.json"), "--out", str(cartella / "schema"))
    mep("disegna", str(lavoro / "grafo-completo.prima.json"), "--piano", str(T3_BANCO / "piano.json"),
        "--out", str(cartella / "schema-prima"))
    shutil.rmtree(lavoro / "giro-1b")
    for sotto in ("giro-1", "giro-2", "schema", "schema-prima"):
        _tieni_le_tavole(cartella / sotto, pdf=sotto in ("giro-2", "schema"))
    for file in (cartella / "distinta").glob("*"):
        if not file.name.endswith(("distinta.json", "distinta-calcoli.md")):
            file.unlink()
    return righe


def principale() -> int:
    with tempfile.TemporaryDirectory() as temporanea:
        base = Path(temporanea) / "base"
        base.mkdir()
        archivio = Path(temporanea) / "base.tar"
        with archivio.open("wb") as uscita:
            subprocess.run(["git", "-C", str(RADICE), "archive", BASE, "src", "rules", "naming"], stdout=uscita, check=True)
        with tarfile.open(archivio) as tar:
            tar.extractall(base, filter="data")
        ingressi = _pulisci(Path(temporanea) / "ingressi")
        misure: list[str] = []

        # B-3: il collaudo T3 del banco, prima e dopo; e con le forature accese.
        pianta_t3, grafo_t3 = T3_BANCO / "pianta.json", T3_BANCO / "grafo-completo.json"
        misure.append(f"t3 prima: {prima(pianta_t3, QUI / 't3' / 'prima', base, grafo=grafo_t3)}")
        misure.append(f"t3 dopo: {dopo(pianta_t3, QUI / 't3' / 'dopo', grafo=grafo_t3)}")
        accese = _variante(pianta_t3, ingressi / "t3" / "pianta.json", lambda d: d.update(forature=True))
        misure.append(f"t3 dopo, forature accese: {dopo(accese, QUI / 't3' / 'dopo-forature-accese', grafo=grafo_t3, pdf=False)}")
        uguali = [
            png.name for png in sorted((QUI / "t3" / "prima").glob("*.png"))
            if png.read_bytes() == (QUI / "t3" / "dopo-forature-accese" / png.name).read_bytes()
        ]
        misure.append(f"t3 prima = dopo con le forature accese, PNG identici byte per byte: {', '.join(uguali)}")

        # B-2: le sagome, senza e con.
        sagome = CASI / "sagome-muri.json"
        senza = _variante(sagome, ingressi / "sagome" / "senza-sagome.json", lambda d: d.pop("sagome_muri"))
        misure.append(f"sagome senza: {dopo(senza, QUI / 'sagome' / 'senza-sagome', pdf=False)}")
        con = _variante(sagome, ingressi / "sagome" / "con-sagome.json", lambda d: None)
        misure.append(f"sagome con: {dopo(con, QUI / 'sagome' / 'con-sagome', dxf=True)}")

        # B-5: il T3 con 49 discordanze.
        disc = _variante(CASI / "collaudo-t3.json", ingressi / "discordanze" / "discordanze.json", discordante)
        distinta, grafo = CASI / "collaudo-t3.distinta.json", CASI / "collaudo-t3.grafo-completo.json"
        misure.append(f"discordanze prima, distinta e grafo: "
                      f"{prima(disc, QUI / 'discordanze' / 'prima', base, distinta=distinta, grafo=grafo)}")
        misure.append(f"discordanze dopo, distinta e grafo: "
                      f"{dopo(disc, QUI / 'discordanze' / 'dopo', distinta=distinta, grafo=grafo)}")
        misure.append(f"discordanze dopo, senza confronto: {dopo(disc, QUI / 'discordanze' / 'dopo-senza-confronto', pdf=False)}")

        # B-4: le lunghezze nel grafo.
        misure += lunghezze(QUI / "lunghezze")
    (QUI / "misure.txt").write_text(
        "# formato, scala, avvisi sulla tavola, avvisi del confronto (rifai_le_tavole.py)\n" + "\n".join(misure) + "\n",
        encoding="utf-8",
    )
    print("\n".join(misure))
    return 0


if __name__ == "__main__":
    sys.exit(principale())
