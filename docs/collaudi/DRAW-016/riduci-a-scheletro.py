#!/usr/bin/env python3
"""Riduce un impianto al proprio **scheletro**: solo macchine e collettori.

**A che serve.** Il PO, il 21 settembre 2026, aprendo `DRAW-016`:

    «Proviamo innanzi tutto nella prossima sessione a disegnare le tavole
    SENZA LE VALVOLE IN MEZZO in modo da vedere se gli agenti riescono a
    disegnare queste autostrade come farebbe un disegnatore umano.»

Lo scheletro e' quell'ingresso: il grafo senza corredo, su cui si vede se chi
compone sa tirare le autostrade. Lo script sta qui — e non in `scratchpad` —
perche' **una prova che non si riesegue non e' una prova**.

**Che cosa toglie, e che cosa no.**

1. **Si potano le foglie.** Un organo di servizio e' un vicolo cieco: valvola,
   manometro, sfiato, vaso, confine di rete. Si toglie chi ha grado <= 1, e si
   ripete finche' ce n'e': un T che reggeva solo una valvola scende a grado 2 e
   sparisce anche lui.
2. **I raccordi che uniscono davvero restano.** Chi resta a grado >= 3 e'
   struttura, non corredo: e' il collettore. **Toglierli non e' un'opzione** —
   tre pompe in parallelo senza i loro due T scaricherebbero **tre tubazioni su
   una porta sola**, e il grafo non lo permette (misurato il 20 settembre 2026,
   `DRAW-015` RAPPORTO §13.3).
3. **Le macchine restano unite dove lo erano**, passando *attraverso* i pezzi
   tolti: ogni coppia di porte che prima si raggiungeva diventa un collegamento
   diretto, e si porta dietro la propria rete.

**Che cosa NON e'.** Non e' un impianto vero e non deve diventarlo: manca tutto
cio' che la norma e le regole del motore pretendono. Serve a **guardare le
autostrade**, e il giudizio su quelle e' grafico, non numerico (**D-164**).

Uso:

    python docs/collaudi/DRAW-016/riduci-a-scheletro.py \\
        <progetto-completo.json> <scheletro.json> [<piano.json> <piano-ridotto.json>]

Il piano e' facoltativo: se lo si passa, ne esce la copia con i soli pezzi
sopravvissuti, che serve a instradare lo scheletro col piano scritto a mano e
misurare il punto di partenza.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.hierarchy import spine_machines, user_machines

RADICE = Path(__file__).resolve().parents[3]
Porta = tuple[str, str]


def _pezzi_da_tenere(dati: dict[str, Any], completo: Path) -> set[str]:
    """Le macchine di spina e d'utenza, piu' i raccordi che uniscono davvero."""
    progetto = load_project(completo)
    catalogo = ComponentRegistry.from_directory(
        RADICE / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(RADICE / "assets" / "symbols"),
    )
    tenuti = set(spine_machines(progetto, catalogo)) | set(user_machines(progetto, catalogo))

    vicini: dict[str, set[str]] = collections.defaultdict(set)
    for collegamento in dati["connections"]:
        a = collegamento["endpoint_a"]["component_id"]
        b = collegamento["endpoint_b"]["component_id"]
        vicini[a].add(b)
        vicini[b].add(a)

    vivi = {pezzo["id"] for pezzo in dati["components"]}
    potato = True
    while potato:
        potato = False
        for pezzo in list(vivi):
            if pezzo in tenuti:
                continue
            if len([v for v in vicini[pezzo] if v in vivi]) <= 1:
                vivi.discard(pezzo)
                potato = True
    for pezzo in vivi:
        if len([v for v in vicini[pezzo] if v in vivi]) >= 3:
            tenuti.add(pezzo)
    return tenuti


def _collegamenti_diretti(
    dati: dict[str, Any], tenuti: set[str]
) -> list[tuple[Porta, Porta, str]]:
    """Ogni coppia di porte che si raggiungeva passando per i pezzi tolti."""
    vicini: dict[Porta, list[Porta]] = collections.defaultdict(list)
    rete_di: dict[tuple[Porta, Porta], str] = {}
    for collegamento in dati["connections"]:
        a = (collegamento["endpoint_a"]["component_id"], collegamento["endpoint_a"]["port_id"])
        b = (collegamento["endpoint_b"]["component_id"], collegamento["endpoint_b"]["port_id"])
        vicini[a].append(b)
        vicini[b].append(a)
        rete_di[(a, b)] = collegamento["network_id"]
        rete_di[(b, a)] = collegamento["network_id"]

    def altre_porte_dello_stesso_pezzo(porta: Porta) -> list[Porta]:
        """Dentro un pezzo tolto si passa da una porta all'altra."""
        return [q for q in vicini if q[0] == porta[0] and q != porta]

    diretti: list[tuple[Porta, Porta, str]] = []
    visti: set[tuple[Porta, Porta]] = set()
    for porta in list(vicini):
        if porta[0] not in tenuti:
            continue
        for primo in vicini[porta]:
            coda, passati = [primo], {porta}
            arrivo: Porta | None = None
            rete = rete_di.get((porta, primo), "")
            while coda:
                qui = coda.pop()
                if qui in passati:
                    continue
                passati.add(qui)
                if qui[0] in tenuti:
                    arrivo = qui
                    break
                coda.extend(vicini[qui])
                coda.extend(altre_porte_dello_stesso_pezzo(qui))
            if arrivo is None or porta == arrivo:
                continue
            chiave = (min(porta, arrivo), max(porta, arrivo))
            if chiave in visti:
                continue
            visti.add(chiave)
            diretti.append((porta, arrivo, rete))
    return diretti


def main(argomenti: list[str]) -> int:
    if len(argomenti) not in (2, 4):
        print(__doc__)
        return 2
    completo, fuori = Path(argomenti[0]), Path(argomenti[1])
    dati = json.loads(completo.read_text(encoding="utf-8"))

    tenuti = _pezzi_da_tenere(dati, completo)
    diretti = _collegamenti_diretti(dati, tenuti)

    scheletro = dict(dati)
    scheletro["components"] = [p for p in dati["components"] if p["id"] in tenuti]
    scheletro["connections"] = [
        {
            "id": f"m{indice}",
            "endpoint_a": {"component_id": a[0], "port_id": a[1]},
            "endpoint_b": {"component_id": b[0], "port_id": b[1]},
            "network_id": rete,
            "evidence": [],
            "properties": {},
        }
        for indice, (a, b, rete) in enumerate(diretti, start=1)
    ]
    fuori.write_text(json.dumps(scheletro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if len(argomenti) == 4:
        piano = json.loads(Path(argomenti[2]).read_text(encoding="utf-8"))
        piano["pezzi"] = {k: v for k, v in piano["pezzi"].items() if k in tenuti}
        Path(argomenti[3]).write_text(
            json.dumps(piano, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    print(
        f"{completo.name}: {len(dati['components'])} pezzi -> "
        f"**{len(scheletro['components'])}**, "
        f"{len(dati['connections'])} tubazioni -> **{len(scheletro['connections'])}**"
    )
    print("  " + ", ".join(sorted(tenuti)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
