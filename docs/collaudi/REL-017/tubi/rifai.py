"""Rifa' le tavole del tubo da comprare (I-279, I-281), dalla radice del repository:

    PYTHONPATH=src python3 docs/collaudi/REL-017/tubi/rifai.py

La villetta di riferimento (`docs/collaudi/REL-017/diametri/grafo.json`, Shenling 12 kW con
5 K, deviatrice, volano a 4 attacchi; il piano dell'idraulica di `REL-015/pdc-regola`) e
l'impianto 7 di `REL-001`, ciascuno in qualche variante: completa, disegna, la tavola in
PDF e in PNG (`pdftoppm -r 110`), i rilievi, e il foglio dei calcoli della villetta. Le
uscite di `completa` e `disegna` stanno in `uscite.md`: gli avvisi dei tubi, le riduzioni
agli attacchi, la verifica della prevalenza.
"""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.diametri.foglio import (  # noqa: E402
    foglio_in_markdown,
    prevalenza_in_markdown,
    righe_del_calcolo,
)
from disegnatore_mep.diametri.perdite import verifiche_della_prevalenza  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.piano.vista import sigle_del_grafo_intero  # noqa: E402
from disegnatore_mep.skill import cartelle_del_repository, main  # noqa: E402

VILLETTA = ROOT / "docs" / "collaudi" / "REL-017" / "diametri"
PIANO_VILLETTA = ROOT / "docs" / "collaudi" / "REL-017" / "riduzione" / "piano-idraulica.json"
"""Il piano della villetta di `REL-015/pdc-regola` con la pompa di calore 10 mm a sinistra: il posto della riduzione (D-233)."""
IMPIANTO_7 = ROOT / "docs" / "collaudi" / "REL-001" / "impianto-7"

Ritocco = Callable[[dict[str, Any]], None]


def _pdc(**proprieta: Any) -> Ritocco:
    def ritocca(grafo: dict[str, Any]) -> None:
        for pezzo in grafo["components"]:
            if pezzo["id"] == "pdc":
                pezzo["properties"].update(proprieta)

    return ritocca


def _materiale(materiale: str) -> Ritocco:
    def ritocca(grafo: dict[str, Any]) -> None:
        grafo["materiale_tubazioni"] = materiale

    return ritocca


def _esecutivo(grafo: dict[str, Any]) -> None:
    grafo["metadata"]["livello"] = "esecutivo"


def _sezione_su_tutto(sezione: str) -> Ritocco:
    """Il caso della commessa: la sezione su ogni tubazione del primario, anche sui pezzi
    corti e sugli stacchi."""

    def ritocca(grafo: dict[str, Any]) -> None:
        for tubo in grafo["connections"]:
            if tubo["network_id"] == "primario":
                tubo["sezione"] = sezione

    return ritocca


VARIANTI: list[tuple[str, Path, Path, list[Ritocco], list[Ritocco]]] = [
    # nome, grafo di prima stesura, piano, ritocchi prima di completare, ritocchi dopo
    ("villetta-calcolo", VILLETTA / "grafo.json", PIANO_VILLETTA, [], []),
    ("villetta-con-lunghezze", VILLETTA / "grafo-con-lunghezze.json", PIANO_VILLETTA, [], []),
    # La sezione del progettista sta gia' nel grafo che `completa` legge — e' lei che decide
    # la riduzione all'attacco (D-233) —, e poi su ogni pezzo corto del grafo completo.
    ("villetta-sezione-ms32-su-tutto", VILLETTA / "grafo.json", PIANO_VILLETTA, [_sezione_su_tutto("MS 32×3")],
     [_sezione_su_tutto("MS 32×3")]),
    ("villetta-15kw-ms32-del-progettista", VILLETTA / "grafo.json", PIANO_VILLETTA,
     [_pdc(power_kw=15), _sezione_su_tutto("MS 32×3")], [_sezione_su_tutto("MS 32×3")]),
    ("villetta-15kw-calcolo", VILLETTA / "grafo.json", PIANO_VILLETTA, [_pdc(power_kw=15)], []),
    ("villetta-acciaio", VILLETTA / "grafo.json", PIANO_VILLETTA, [_materiale("acciaio")], []),
    ("villetta-rame-esecutivo", VILLETTA / "grafo.json", PIANO_VILLETTA, [_materiale("rame"), _esecutivo], []),
    ("villetta-esecutivo", VILLETTA / "grafo.json", PIANO_VILLETTA, [_esecutivo], []),
    ("impianto-7-multistrato", IMPIANTO_7 / "grafo-completo.json", IMPIANTO_7 / "piano.json", [], []),
    ("impianto-7-acciaio", IMPIANTO_7 / "grafo-completo.json", IMPIANTO_7 / "piano.json", [_materiale("acciaio")], []),
]


def _esegui(argomenti: list[str]) -> str:
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        main(argomenti, cartelle_del_repository(ROOT))
    return uscita.getvalue()


def main_() -> None:
    cartelle = cartelle_del_repository(ROOT)
    simboli = SymbolRegistry.from_directory(cartelle.simboli)
    catalogo = ComponentRegistry.from_directory(cartelle.catalogo, symbols=simboli)
    for vecchio in QUI.glob("*.png"):
        vecchio.unlink()
    resoconto: list[str] = ["# Le uscite di completa e disegna (I-279, I-281)\n"]
    fogli: list[str] = ["# Il foglio dei calcoli delle varianti della villetta (I-279)\n"]
    with tempfile.TemporaryDirectory() as lavoro_:
        lavoro = Path(lavoro_)
        for nome, grafo, piano, prima, dopo in VARIANTI:
            testo = json.loads(grafo.read_text(encoding="utf-8"))
            for ritocco in prima:
                ritocco(testo)
            bozza = lavoro / f"{nome}-grafo.json"
            bozza.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
            completo = lavoro / f"{nome}-completo.json"
            completa = "" if "impianto-7" in nome else _esegui(["completa", str(bozza), "--out", str(completo)])
            if "impianto-7" in nome:
                shutil.copy(bozza, completo)
            if dopo:
                testo = json.loads(completo.read_text(encoding="utf-8"))
                for ritocco in dopo:
                    ritocco(testo)
                completo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
            cartella = lavoro / nome
            disegna = _esegui(["disegna", str(completo), "--piano", str(piano), "--out", str(cartella), "--senza-dxf"])
            (pdf,) = cartella.glob("*.pdf")
            subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", str(pdf), str(QUI / nome)], check=True)
            resoconto.append(f"\n## {nome}\n")
            for titolo, testo_uscita in (("completa", completa), ("disegna", disegna)):
                righe = [
                    riga
                    for riga in testo_uscita.splitlines()
                    if not riga.lstrip().startswith(("perche'", "fonte:"))
                    and (
                        riga.startswith(("Avvisi", "Riduzioni", "  - GT-", "  - PDC", "Formato"))
                        or any(chiave in riga for chiave in ("riduzione ", "DIAMETER", "RUN_LABEL"))
                    )
                ]
                if righe:
                    resoconto.append(f"\n`{titolo}`:\n\n```\n" + "\n".join(righe) + "\n```\n")
            if nome.startswith("villetta"):
                modello = load_project(completo)
                del_progetto = catalogo.per_il_progetto(modello)
                sigle = sigle_del_grafo_intero(modello, del_progetto, cartelle.naming)
                righe_ = [r for r in righe_del_calcolo(modello, del_progetto, sigle) if r.portata_m3h is not None]
                verifiche = verifiche_della_prevalenza(modello, del_progetto)
                fogli.append(f"\n## {nome}\n\n{foglio_in_markdown(righe_)}{prevalenza_in_markdown(verifiche, sigle)}")
    (QUI / "uscite.md").write_text("".join(resoconto), encoding="utf-8")
    (QUI / "foglio-dei-calcoli.md").write_text("".join(fogli), encoding="utf-8")
    print("\n".join(sorted(p.name for p in QUI.glob("*.png"))))


if __name__ == "__main__":
    main_()
