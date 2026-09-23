"""La misura di una tavola uscita da un piano: quella che la sessione riesegue (D-152).

Uso, dalla radice del repository:

    python docs/collaudi/DRAW-017/misura-tavole.py [--dettaglio] nome=grafo.json:piano.json [...]

Stampa una riga per tavola — formato, tratte, cedute, bloccanti, rilievi delle regole, avvisi,
spezzate piegate, pieghe, incroci — e, con ``--dettaglio``, i rilievi per codice e il testo dei
bloccanti. E' la tabella delle prove in camera pulita del 21, 22 e 23 settembre 2026: quello che
un agente riferisce non e' una misura finche' la sessione non l'ha rieseguito con questo.
"""

import sys
from collections import Counter
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.autostrade import pieghe_della_tratta
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.revisore import misura
from disegnatore_mep.validation.regole import rilievi_delle_regole

RADICE = Path(__file__).resolve().parents[3]


def main(argomenti: list[str]) -> None:
    simboli = SymbolRegistry.from_directory(RADICE / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(
        RADICE / "examples" / "layout" / "catalog", symbols=simboli
    )
    dettaglio = "--dettaglio" in argomenti
    print(
        f"{'tavola':24s} {'formato':7s} {'tratte':>6s} {'cedute':>6s} {'blocc':>5s} "
        f"{'regole':>6s} {'avvisi':>6s} {'piegate':>7s} {'pieghe':>6s} {'incroci':>7s}"
    )
    for voce in [item for item in argomenti if "=" in item]:
        nome, coppia = voce.split("=", 1)
        grafo, piano = coppia.split(":")
        modello = load_project(Path(grafo))
        scritto = carica_piano(Path(piano))
        esito = esegui_piano(modello, scritto, catalogo, simboli, RADICE / "naming")
        if esito.disegno is None:
            print(f"{nome:24s} NON ESCE — {(esito.errore or '')[:160]}")
            continue
        regole = rilievi_delle_regole(esito.disegno, esito.frame, catalogo, modello)
        tutti = [*esito.rilievi, *regole]
        punti = misura(esito, tutti)
        tratte = [route for foglio in esito.disegno.sheets for route in foglio.routes]
        piegate = sum(1 for route in tratte if pieghe_della_tratta(route) > 0)
        print(
            f"{nome:24s} {scritto.formato:7s} {len(tratte):6d} {punti.cedute:6d} "
            f"{punti.bloccanti:5d} {punti.violazioni:6d} {punti.avvisi:6d} {piegate:7d} "
            f"{punti.pieghe:6d} {punti.incroci:7d}"
        )
        if dettaglio:
            conta = Counter(item.code for item in tutti)
            print("     ", ", ".join(f"{codice} {n}" for codice, n in sorted(conta.items())))
            for item in tutti:
                if item.severity is IssueSeverity.BLOCKING:
                    print("      BLOCCANTE:", item.message[:200])


if __name__ == "__main__":
    main(sys.argv[1:])
