"""Il banco delle tavole: le uscite di riferimento della skill, rifatte e confrontate (REL-024).

    python scripts/banco.py                    # rifa' le uscite e le confronta con le impronte
    python scripts/banco.py --registra         # riscrive le impronte (una modifica voluta)
    python scripts/banco.py --uscita <cartella>  # e lascia le tavole li', per guardarle

Fino alla 1.15.0 il banco era uno strumento di sessione (`docs/collaudi/REL-011/banco.py`):
girava solo quando la sessione se ne ricordava, e la regressione delle tavole — il controllo
che conta per il PO — non era una prova. Da qui lo e': `tests/test_il_banco.py` rifa' ogni
caso a ogni PR e lo confronta con `tests/banco/impronte.json`.

**Una tavola cambiata non e' un errore da far tacere**: se la modifica e' voluta, si
rigenerano le impronte con `--registra` e **la tavola nuova si mostra al PO nella PR**
(D-146). Le impronte sono sha256 delle uscite che si guardano — SVG, rilievi, distinta,
tracciati della pianta — piu' la riga di sintesi di `disegna`; il PDF e il DXF ne sono
traduzioni e non si impronta. Il disegno e' deterministico fra Python 3.11 e 3.13 e con
semi di hash diversi: misurato il 6 novembre 2026 sui 24 casi di REL-011.

I casi: i 24 del banco di REL-011, il T1 di REL-023, la villetta di REL-015 (idraulica ed
elettrico), l'aria-aria di REL-012 fase 2, il collaudo T3 di REL-012 con la sua pianta, la
distinta del T1.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
IMPRONTE = RADICE / "tests" / "banco" / "impronte.json"
C = "docs/collaudi"

# Le uscite che si improntano, per nome di file.
DA_IMPRONTARE = (".svg", "-rilievi.md", "distinta.json", "tabelle-del-foglio.json", ".tracciati.json")


@dataclass(frozen=True)
class Caso:
    nome: str
    grafo: str
    """Il grafo: completo, o di prima stesura se `completa`."""
    piani: tuple[str, ...] = ()
    completa: bool = False
    distinta: bool = False
    pianta: str | None = None
    note: str = field(default="", compare=False)


def _casi_di_rel011() -> list[Caso]:
    d18 = f"{C}/DRAW-018/prova-camera-pulita-2026-09-24"
    casi = [Caso(f"impianto-{n}", f"{d18}/grafo-completo-{n}.json", (f"{d18}/piano-completo-{n}.json",)) for n in range(1, 6)]
    casi += [
        Caso(f"impianto-6{x}", f"{C}/REL-003/impianto-6/grafo-completo-6.json", (f"{C}/REL-003/impianto-6/piano-6-{x}.json",))
        for x in ("a", "b")
    ]
    casi.append(Caso("impianto-7", f"{C}/REL-001/impianto-7/grafo-completo.json", (f"{C}/REL-001/impianto-7/piano.json",)))
    for lettera, nome in (("A", "A-com-era"), ("B", "B-proposta-po"), ("C", "C-volano-abbassato"), ("D", "D-volano-coricato")):
        casi.append(
            Caso(f"prova-po-{lettera}", f"{C}/REL-005/prova-po-1/grafo-proposta-po.json",
                 (f"{C}/REL-005/prova-po-1/piano-{nome}.json",), completa=True)
        )
    casi.append(Caso("simboli-rel009", f"{C}/REL-009/simboli-nuovi/grafo.json", (f"{C}/REL-009/simboli-nuovi/piano.json",), completa=True))
    reale = f"{C}/REL-009/caso-reale-2/grafo-prima-stesura.json"
    casi.append(Caso("caso-reale-2", reale, (f"{C}/REL-009/caso-reale-2/piano.json",), completa=True))
    casi += [
        Caso(f"prova-pulita-{x}", reale, (f"{C}/REL-009/prova-pulita-1.4/piano-{x}.json",), completa=True) for x in ("A", "B", "C")
    ]
    for n, nome in enumerate(
        ("prova-1-due-pdc-accumulo-combinato", "prova-2-pdc-deviatrice-acs", "prova-3-pdc-diretta-pavimento",
         "prova-4-ibrido-pdc-caldaia", "prova-5-cascata-tre-pdc"),
        start=1,
    ):
        casi.append(Caso(f"impianto-{n}-completato", f"examples/prova/{nome}.json", (f"{d18}/piano-completo-{n}.json",), completa=True))
    casi += [
        Caso(f"impianto-6{x}-completato", f"{C}/REL-003/capire-giro-2/grafo.json", (f"{C}/REL-003/impianto-6/piano-6-{x}.json",),
             completa=True)
        for x in ("a", "b")
    ]
    return casi


CASI: list[Caso] = [
    *_casi_di_rel011(),
    Caso("t1-rel023", f"{C}/REL-023/T1/grafo.json", (f"{C}/REL-023/T1/piano-idraulica.json",), completa=True, distinta=True),
    Caso("villetta-rel015", f"{C}/REL-015/pdc-regola/grafo.json",
         (f"{C}/REL-015/pdc-regola/piano-idraulica.json", f"{C}/REL-015/pdc-regola/piano-elettrico.json"), completa=True),
    Caso("aria-aria-rel012", f"{C}/REL-012/fase-2/grafo.json", (f"{C}/REL-012/fase-2/piano.json",), completa=True),
    Caso("collaudo-t3-rel012", f"{C}/REL-012/collaudo-t3/grafo-completo.json", (f"{C}/REL-012/collaudo-t3/piano.json",),
         pianta=f"{C}/REL-012/collaudo-t3/pianta.json"),
]


def _main_della_skill():  # type: ignore[no-untyped-def]
    sys.path.insert(0, str(RADICE / "src"))
    from disegnatore_mep.skill import cartelle_del_repository, main

    return main, cartelle_del_repository(RADICE)


def rifai(caso: Caso, cartella: Path) -> dict[str, str]:
    """Rifa' il caso nella cartella e ne restituisce le impronte: nome del file -> sha256,
    piu' le righe di sintesi di `disegna`."""
    main, cartelle = _main_della_skill()
    cartella.mkdir(parents=True, exist_ok=True)
    grafo = RADICE / caso.grafo

    def esegui(argv: list[str]) -> str:
        testo = io.StringIO()
        with contextlib.redirect_stdout(testo):
            codice = main(argv, cartelle)
        if codice == 1:
            raise RuntimeError(f"{caso.nome}: `{' '.join(argv[:2])}` non si e' potuto fare:\n{testo.getvalue()[-1500:]}")
        return testo.getvalue()

    if caso.completa:
        completo = cartella / "grafo-completo.json"
        esegui(["completa", str(grafo), "--out", str(completo)])
        grafo = completo
    impronte: dict[str, str] = {}
    if caso.completa:
        impronte["grafo-completo.json"] = _sha(grafo)
    for numero, piano in enumerate(caso.piani, start=1):
        uscita = esegui(["disegna", str(grafo), "--piano", str(RADICE / piano), "--out", str(cartella / "tavola")])
        sintesi = [riga for riga in uscita.splitlines() if riga.startswith("Formato")]
        impronte[f"sintesi-{numero}"] = sintesi[-1] if sintesi else "(nessuna riga di sintesi)"
    if caso.distinta:
        esegui(["distinta", str(grafo), "--out", str(cartella / "distinta")])
    if caso.pianta:
        # In sola lettura: dal REL-026 (B-4) la pianta scrive nel grafo le lunghezze misurate,
        # e il banco non tocca i file del repository.
        esegui(["pianta", str(RADICE / caso.pianta), "--out", str(cartella / "pianta"), "--senza-dxf",
                "--grafo", str(grafo), "--grafo-in-sola-lettura"])
    for file in sorted(cartella.rglob("*")):
        if file.is_file() and file.name.endswith(DA_IMPRONTARE):
            impronte[file.relative_to(cartella).as_posix()] = _sha(file)
    return impronte


def _sha(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def registrate() -> dict[str, dict[str, str]]:
    if not IMPRONTE.exists():
        return {}
    return json.loads(IMPRONTE.read_text(encoding="utf-8"))["casi"]  # type: ignore[no-any-return]


def differenze(attese: dict[str, str], trovate: dict[str, str]) -> list[str]:
    righe = []
    for chiave in sorted(set(attese) | set(trovate)):
        a, t = attese.get(chiave), trovate.get(chiave)
        if a == t:
            continue
        if a is None:
            righe.append(f"  + {chiave}: uscita nuova")
        elif t is None:
            righe.append(f"  - {chiave}: non esce piu'")
        elif chiave.startswith("sintesi"):
            righe.append(f"  ~ {chiave}:\n      era  {a}\n      ora  {t}")
        else:
            righe.append(f"  ~ {chiave}: cambiato")
    return righe


def principale(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registra", action="store_true", help="riscrive le impronte")
    parser.add_argument("--uscita", type=Path, help="lascia qui le tavole rifatte")
    parser.add_argument("--caso", action="append", help="solo questi casi")
    args = parser.parse_args(argv)
    casi = [c for c in CASI if not args.caso or c.nome in args.caso]
    attese = registrate()
    nuove: dict[str, dict[str, str]] = dict(attese)
    cambiati = 0
    with tempfile.TemporaryDirectory() as lavoro:
        base = args.uscita or Path(lavoro)
        if args.uscita and args.uscita.exists():
            shutil.rmtree(args.uscita)
        for caso in casi:
            trovate = rifai(caso, base / caso.nome)
            nuove[caso.nome] = trovate
            righe = differenze(attese.get(caso.nome, {}), trovate)
            if righe:
                cambiati += 1
                print(f"{caso.nome}: CAMBIATO\n" + "\n".join(righe))
            else:
                print(f"{caso.nome}: uguale")
    if args.registra:
        IMPRONTE.parent.mkdir(parents=True, exist_ok=True)
        IMPRONTE.write_text(
            json.dumps(
                {"nota": "Impronte del banco delle tavole: le riscrive `python scripts/banco.py --registra`, "
                         "e una tavola cambiata si mostra al PO nella PR (D-146).",
                 "casi": dict(sorted(nuove.items()))},
                ensure_ascii=False, indent=1,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"Impronte scritte: {IMPRONTE.relative_to(RADICE)} ({len(nuove)} casi)")
        return 0
    print(f"{len(casi) - cambiati} uguali, {cambiati} cambiati, su {len(casi)}")
    return 1 if cambiati else 0


if __name__ == "__main__":
    sys.exit(principale())
