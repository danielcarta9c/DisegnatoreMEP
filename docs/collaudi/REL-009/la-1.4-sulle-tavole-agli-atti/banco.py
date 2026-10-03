"""Banco di prova: le tavole agli atti disegnate con una versione del codice.

    python3 banco.py <radice-del-codice> <cartella-di-uscita> [<radice-dei-dati>]

Per ogni tavola: `completa` se il grafo e' di prima stesura, poi `disegna` col piano; in un
processo nuovo per tavola, cronometrato. Scrive `esiti.json`.
"""

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

CODICE = Path(sys.argv[1]).resolve()
USCITA = Path(sys.argv[2]).resolve()
DATI = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else CODICE
USCITA.mkdir(parents=True, exist_ok=True)

C = "docs/collaudi"
TAVOLE: list[tuple[str, str, str, bool]] = [
    *[
        (f"impianto-{n}", f"{C}/DRAW-018/prova-camera-pulita-2026-09-24/grafo-completo-{n}.json",
         f"{C}/DRAW-018/prova-camera-pulita-2026-09-24/piano-completo-{n}.json", False)
        for n in range(1, 6)
    ],
    ("impianto-6a", f"{C}/REL-003/impianto-6/grafo-completo-6.json", f"{C}/REL-003/impianto-6/piano-6-a.json", False),
    ("impianto-6b", f"{C}/REL-003/impianto-6/grafo-completo-6.json", f"{C}/REL-003/impianto-6/piano-6-b.json", False),
    ("impianto-7", f"{C}/REL-001/impianto-7/grafo-completo.json", f"{C}/REL-001/impianto-7/piano.json", False),
    *[
        (f"prova-po-{lettera}", f"{C}/REL-005/prova-po-1/grafo-proposta-po.json",
         f"{C}/REL-005/prova-po-1/piano-{nome}.json", True)
        for lettera, nome in (("A", "A-com-era"), ("B", "B-proposta-po"), ("C", "C-volano-abbassato"), ("D", "D-volano-coricato"))
    ],
    ("simboli-rel009", f"{C}/REL-009/simboli-nuovi/grafo.json", f"{C}/REL-009/simboli-nuovi/piano.json", True),
    ("caso-reale-2", f"{C}/REL-009/caso-reale-2/grafo-prima-stesura.json", f"{C}/REL-009/caso-reale-2/piano.json", True),
]

PROGRAMMA = """
import contextlib, io, sys, time
from pathlib import Path
from disegnatore_mep.skill import main, cartelle_del_repository
c = cartelle_del_repository(Path('.'))
grafo, piano, uscita, completa = sys.argv[1], sys.argv[2], Path(sys.argv[3]), sys.argv[4] == '1'
uscita.mkdir(parents=True, exist_ok=True)
t0 = time.perf_counter()
if completa:
    with contextlib.redirect_stdout(io.StringIO()):
        main(['completa', grafo, '--out', str(uscita / 'gc.json')], c)
    grafo = str(uscita / 'gc.json')
t1 = time.perf_counter()
testo = io.StringIO()
with contextlib.redirect_stdout(testo):
    rc = main(['disegna', grafo, '--piano', piano, '--out', str(uscita / 'tavola')], c)
t2 = time.perf_counter()
(uscita / 'disegna.txt').write_text(testo.getvalue(), encoding='utf-8')
print(f'TEMPI {t1 - t0:.2f} {t2 - t1:.2f} {rc}')
"""

esiti = []
for nome, grafo, piano, completa in TAVOLE:
    if not (DATI / grafo).exists() or not (DATI / piano).exists():
        esiti.append({"tavola": nome, "esito": "manca il grafo o il piano"})
        continue
    cartella = USCITA / nome
    inizio = time.perf_counter()
    fatto = subprocess.run(
        [sys.executable, "-c", PROGRAMMA, str(DATI / grafo), str(DATI / piano), str(cartella), "1" if completa else "0"],
        cwd=CODICE, env={"PYTHONPATH": str(CODICE / "src"), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, timeout=1800,
    )
    totale = time.perf_counter() - inizio
    tempi = next((riga.split() for riga in fatto.stdout.splitlines() if riga.startswith("TEMPI")), None)
    testo = (cartella / "disegna.txt").read_text(encoding="utf-8") if (cartella / "disegna.txt").exists() else fatto.stderr[-2000:]
    sintesi = next((riga for riga in testo.splitlines() if riga.startswith("Formato")), None)
    errore = next((riga for riga in testo.splitlines() if "non si instrada" in riga or riga.startswith("Errore")), None)
    svg = sorted((cartella / "tavola").glob("*.svg")) if (cartella / "tavola").exists() else []
    esiti.append({
        "tavola": nome,
        "processo_s": round(totale, 1),
        "completa_s": float(tempi[1]) if tempi else None,
        "disegna_s": float(tempi[2]) if tempi else None,
        "rc": int(tempi[3]) if tempi else fatto.returncode,
        "sintesi": sintesi,
        "errore": errore,
        "svg": hashlib.sha256(svg[0].read_bytes()).hexdigest()[:16] if svg else None,
    })
    print(nome, esiti[-1]["disegna_s"], sintesi or errore, flush=True)

(USCITA / "esiti.json").write_text(json.dumps(esiti, ensure_ascii=False, indent=1), encoding="utf-8")
