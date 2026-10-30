"""Scrive il grafo della M.02 (REL-012, fase 2) dal grafo completo dell'esempio AA-01.

    python3 docs/collaudi/REL-012/fase-2/fai-il-grafo.py

Il grafo di partenza e' `examples/distinta/AA-01/grafo-completo.json` (REL-013): il
canalizzato del kit, con lunghezze, sezioni, portate e protezioni come dati del
progettista. Due cose cambiano, e sono quelle che un agente scriverebbe oggi
seguendo `skill/capire/ISTRUZIONI.md`:

- **i tre campi del tratto in testa alla tubazione** — `sezione`, `lunghezza_m`,
  `scritta` —, non fra le `properties`: il motore li legge li' e li scrive sulla
  tavola; la distinta li legge in tutti e due i posti. Un raccordo diretto (plenum
  sulla macchina, ripresa sulla bocca, cablaggio di fabbrica) ha lunghezza `0`, che il
  campo in testa non ammette (`gt=0`): resta fra le `properties`, dove la distinta
  lo legge, e con lei la sua `sezione` — la ripresa 1000×250 sta sulla bocca della
  macchina, la misura e' gia' nell'etichetta della ripresa come sulla M.02 del kit, e
  scritta di nuovo lungo il raccordo starebbe stretta accanto alla freccia. Una
  `scritta` vera («di fabbrica») va in testa anche su un raccordo diretto;
- **l'etichetta delle bocchette senza la sigla**: la sigla (`B1`) e' gia' il `tag`, e
  sulla tavola si scriverebbe due volte, «B1» e «B1 · Camera 13 m²». L'etichetta
  porta il solo locale, come quella dei termostati;
- **il sifone senza sigla**, come sul grafo del kit: «SIF-01», a sinistra del sifone,
  prendeva il posto del richiamo della scritta della condensa, e la tavola usciva con
  un rilievo bloccante (`RUN_LABEL_OMITTED`, c-1). Allungare lo stacco dello scarico
  per fargli posto apre l'avviso di A4 (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM`). Nella
  tabella delle tratte il sifone si legge «sifone» invece di «SIF-01».

Nient'altro: pezzi, reti, capi e dati restano quelli dell'esempio.
"""

import json
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
PARTENZA = RADICE / "examples" / "distinta" / "AA-01" / "grafo-completo.json"
QUI = Path(__file__).resolve().parent

CAMPI_DEL_TRATTO = ("sezione", "lunghezza_m", "scritta")


def main() -> None:
    grafo = json.loads(PARTENZA.read_text(encoding="utf-8"))
    for pezzo in grafo["components"]:
        if pezzo["id"] == "sifone":
            pezzo["tag"] = None
        tag = pezzo.get("tag")
        etichetta = pezzo["properties"].get("etichetta")
        if tag and isinstance(etichetta, str) and etichetta.startswith(f"{tag} · "):
            pezzo["properties"]["etichetta"] = etichetta[len(tag) + 3 :]
    for tubazione in grafo["connections"]:
        dati = tubazione["properties"]
        testa = {}
        diretto = dati.get("lunghezza_m") == 0
        for campo in CAMPI_DEL_TRATTO:
            valore = dati.get(campo)
            if valore is None or (diretto and campo != "scritta"):
                continue
            testa[campo] = dati.pop(campo)
        ordinata = {chiave: tubazione[chiave] for chiave in ("id", "network_id", "endpoint_a", "endpoint_b")}
        tubazione.clear()
        tubazione.update(ordinata | testa | {"properties": dati})
    (QUI / "grafo.json").write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
