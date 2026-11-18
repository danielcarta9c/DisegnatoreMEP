"""REL-027, criterio 5: il costo della minuteria e «Dove comprare» sulle voci della lista PR.MI.059.

Il grafo della commessa non è nel repository: le voci vengono dalla lista materiali che la skill ha
scritto (`voci.json`, con i codici che le regole della distinta danno a ciascuna). Si prezzano con il
listino rev. 06 e con lo stesso codice di `distinta --costo` (`prezza`, `ordine_della_minuteria`,
`costo_in_markdown`).

    python docs/collaudi/REL-027/pr-mi-059/misura.py
"""

import json
from pathlib import Path

from disegnatore_mep.distinta.costo import Costo, RigaDelCosto, costo_in_markdown
from disegnatore_mep.distinta.listino import leggi_il_listino
from disegnatore_mep.distinta.ordine import ordine_della_minuteria

QUI = Path(__file__).parent
ROOT = QUI.parents[3]
TITOLI = {"S": "Staffaggi e supporti", "I": "Circuito idraulico", "E": "Elettrico, comando e regolazione",
          "B": "Distribuzione aria", "C": "Circuito frigorifero", "D": "Scarico condensa"}


def costo_della_lista(voci: list[dict], listino_path: Path) -> Costo:
    listino = leggi_il_listino(listino_path)
    costo = Costo(progetto={"project_name": "PR.MI.059 (dalla lista materiali)"}, listino=listino)
    for v in voci:
        riga = RigaDelCosto(v["rif"], v["sezione"], v["testo"], v["quantita"], v["um"], [], None, None, "")
        if v["codici"] is None:
            riga.manca = "le regole non le danno un codice del listino"
        else:
            riga.codici = [(c, float(n)) for c, n in v["codici"]]
            mancanti = [c for c, _ in riga.codici if listino.get(c) is None]
            if mancanti:
                riga.manca = f"il listino non ha il codice {mancanti[0]}"
            else:
                riga.unitario = sum(n * listino.get(c).prezzo for c, n in riga.codici)  # type: ignore[union-attr]
                riga.totale = v["quantita"] * riga.unitario
                riga.conto = " + ".join(
                    f"{c} {listino.get(c).prezzo:.2f} ({listino.get(c).fornitore})" for c, _ in riga.codici  # type: ignore[union-attr]
                )
        costo.righe.append(riga)
    return costo


def main() -> None:
    dati = json.loads((QUI / "voci.json").read_text(encoding="utf-8"))
    costo = costo_della_lista(dati["voci"], ROOT / "skill" / "distinta" / "LISTINO-MINUTERIA.md")
    (QUI / "costo-minuteria.md").write_text(costo_in_markdown(costo, TITOLI), encoding="utf-8")
    ordine = ordine_della_minuteria(costo)
    print(f"voci {len(costo.righe)}, prezzate {len(costo.righe) - len(costo.da_prezzare)}, "
          f"da prezzare {len(costo.da_prezzare)}; totale {costo.totale:.2f} €")
    print(f"ordine: {ordine.totale:.2f} € + senza fornitore {ordine.totale_di_riferimento:.2f} €")
    print(f"un fornitore solo (articoli in comune: {len(ordine.articoli_in_comune)}):")
    for u in ordine.un_fornitore():
        print(f"  {u.fornitore:14} ha {u.ha:2} ({u.da_lui:8.2f} €), non ha {u.non_ha:2} ({u.altrove:7.2f} € altrove): "
              f"totale {u.totale:8.2f} €; sugli articoli in comune {u.in_comune:8.2f} €")
    for fornitore, righe in ordine.per_fornitore().items():
        print(f"  {fornitore}: {len(righe)} articoli, {sum(r.totale for r in righe):.2f} €")
    for c in ordine.combinazioni():
        print(f"  {' + '.join(c.fornitori):40} scoperti {c.scoperti:2}  {c.totale:9.2f} €  +{c.in_piu:7.2f} €")
    pdc = [v for v in dati["voci"] if v["rif"].startswith("P-")]
    solo_pdc = ordine_della_minuteria(costo_della_lista(pdc, ROOT / "skill" / "distinta" / "LISTINO-MINUTERIA.md"))
    print(f"solo la pompa di calore: {solo_pdc.totale:.2f} € in {len(solo_pdc.per_fornitore())} ordini")
    for fornitore, righe in solo_pdc.per_fornitore().items():
        print(f"  {fornitore}: {len(righe)} articoli, {sum(r.totale for r in righe):.2f} €")
    for c in solo_pdc.combinazioni():
        print(f"  {' + '.join(c.fornitori):40} scoperti {c.scoperti:2}  {c.totale:9.2f} €  +{c.in_piu:7.2f} €")

    confronto(costo)


def confronto(costo: Costo) -> None:
    """Abbattista e Idrosanitaria sugli articoli che hanno tutti e due, alle quantità della lista; e il
    circuito idraulico della pompa di calore (P-S, P-I) contro i totali delle due offerte."""
    ordine = ordine_della_minuteria(costo)
    a_meno = i_meno = 0
    tot_a = tot_i = 0.0
    for riga in ordine.righe:
        prezzi = {v.fornitore: v.prezzo for v in riga.offerte}
        if "Abbattista" in prezzi and "Idrosanitaria" in prezzi:
            tot_a += riga.quantita * prezzi["Abbattista"]
            tot_i += riga.quantita * prezzi["Idrosanitaria"]
            a_meno += prezzi["Abbattista"] < prezzi["Idrosanitaria"]
            i_meno += prezzi["Idrosanitaria"] < prezzi["Abbattista"]
    print(f"articoli in comune Abbattista-Idrosanitaria: {a_meno + i_meno}; meno caro Abbattista {a_meno}, "
          f"Idrosanitaria {i_meno}; alle quantità della lista Abbattista {tot_a:.2f} €, Idrosanitaria {tot_i:.2f} €")
    for riga in ordine.ordinabili:
        for v in riga.avvisi:
            print(f"avviso {riga.codice}: {v.fornitore} {v.prezzo:.2f} € ⚠ {v.scostamento}")
    idraulico = [r for r in costo.righe if r.rif.startswith(("P-S", "P-I"))]
    parte = Costo(progetto={}, listino=costo.listino, righe=idraulico)
    o = ordine_della_minuteria(parte)
    print(f"circuito idraulico della pompa di calore (P-S, P-I): {len(idraulico)} voci; ordine diviso "
          f"{o.totale:.2f} € + senza fornitore {o.totale_di_riferimento:.2f} €")
    for fornitore, righe in o.per_fornitore().items():
        print(f"  {fornitore}: {len(righe)} articoli, {sum(r.totale for r in righe):.2f} €")
    for c in o.combinazioni():
        print(f"  {' + '.join(c.fornitori):40} scoperti {c.scoperti:2}  {c.totale:9.2f} €  +{c.in_piu:7.2f} €")


if __name__ == "__main__":
    main()
