"""Dove comprare la minuteria: l'ordine per fornitore (REL-027, I-303).

Il PO compra la minuteria fra piu' fornitori (Abbattista, Tecnomat, Idrosanitaria) e vuole che la
skill gli dica, sul prezzo totale, **che cosa comprare da chi** — «compra queste 6 cose da
Abbattista e queste 15 da Idrosanitaria». Qui si fa il conto, sugli **articoli** del listino (i
codici), non sulle voci della distinta: una voce puo' usare piu' articoli, e un articolo puo'
servire a piu' voci; l'ordine si fa per articolo.

- **La quantita' di un articolo** e' la somma, sulle voci prezzate della distinta, di quantita'
  della voce × unita' dell'articolo per unita' della voce. Le voci DA PREZZARE o con la quantita'
  DA DEFINIRE non entrano.
- **Il fornitore di un articolo** e' quello da cui si ordina che lo vende al prezzo piu' basso (a
  pari prezzo, il primo in ordine alfabetico). Un articolo che nessun fornitore da cui si ordina
  ha, ma che ha un riferimento (online, le fatture di un installatore), va fra quelli **senza
  fornitore**, col prezzo di riferimento.
- **Le combinazioni** dicono quanto costa ordinare da meno fornitori: per ogni gruppo di fornitori,
  quanti articoli non hanno, quanto costano gli articoli che hanno, e quanto in piu' del minimo
  sugli **stessi** articoli — il confronto e' sempre a parita' di articoli.
- **Un fornitore solo** (I-306): se il progettista compra tutta la minuteria da uno, quale costa
  meno sul totale. Il totale di ciascuno e' sullo **stesso paniere**: gli articoli che ha, ai suoi
  prezzi, piu' quelli che non ha, dal piu' economico degli altri (andrebbero comprati altrove). E
  accanto, il conto sui soli articoli che **tutti** hanno: dove il listino di un fornitore e'
  incompleto, e' quello che dice chi costa meno a parita' di articoli.

Il conto non tiene il trasporto, l'ordine minimo e le condizioni di pagamento, e i prezzi hanno la
data del loro documento: lo dice il file che lo scrive.
"""

from dataclasses import dataclass, field
from itertools import combinations
from typing import TYPE_CHECKING, Any

from .listino import Listino, VoceDelListino

if TYPE_CHECKING:
    from .costo import Costo

MASSIMO_PER_TUTTE_LE_COMBINAZIONI = 5
"""Fino a cinque fornitori si mostrano tutte le combinazioni (31); oltre, solo i singoli e tutti."""


@dataclass
class RigaDellOrdine:
    codice: str
    quantita: float
    um: str
    descrizione: str
    voci: list[str] = field(default_factory=list)
    """I riferimenti delle voci della distinta che usano l'articolo."""
    offerte: tuple[VoceDelListino, ...] = ()
    """I prezzi dei fornitori da cui si ordina, il piu' basso per primo."""
    riferimento: VoceDelListino | None = None
    """Il prezzo di riferimento, quando nessun fornitore da cui si ordina ha l'articolo."""

    @property
    def scelta(self) -> VoceDelListino | None:
        return self.offerte[0] if self.offerte else None

    @property
    def totale(self) -> float:
        voce = self.scelta or self.riferimento
        return self.quantita * voce.prezzo if voce else 0.0

    def prezzo_da(self, fornitori: frozenset[str]) -> float | None:
        """Il prezzo piu' basso dell'articolo fra `fornitori`, o None se nessuno di loro lo ha."""
        return next((v.prezzo for v in self.offerte if v.fornitore in fornitori), None)


@dataclass(frozen=True)
class Combinazione:
    fornitori: tuple[str, ...]
    scoperti: int
    """Gli articoli che nessuno dei fornitori della combinazione ha (e che un altro ha)."""
    totale: float
    """Euro degli articoli che la combinazione ha, ciascuno dal suo piu' economico."""
    in_piu: float
    """Euro in piu' del minimo, sugli stessi articoli."""


@dataclass(frozen=True)
class UnFornitore:
    fornitore: str
    ha: int
    """Gli articoli dell'ordine che il fornitore ha."""
    da_lui: float
    """Euro di quegli articoli, ai suoi prezzi."""
    non_ha: int
    altrove: float
    """Euro degli articoli che non ha, dal piu' economico degli altri."""
    in_comune: float
    """Euro degli articoli che hanno tutti i fornitori, ai suoi prezzi."""

    @property
    def totale(self) -> float:
        return self.da_lui + self.altrove


@dataclass
class Ordine:
    righe: list[RigaDellOrdine]

    @property
    def ordinabili(self) -> list[RigaDellOrdine]:
        return [r for r in self.righe if r.offerte]

    @property
    def senza_fornitore(self) -> list[RigaDellOrdine]:
        return [r for r in self.righe if not r.offerte]

    @property
    def fornitori(self) -> list[str]:
        """I fornitori da cui si ordina che hanno almeno un articolo dell'ordine."""
        return sorted({v.fornitore for r in self.righe for v in r.offerte})

    @property
    def totale(self) -> float:
        """Gli articoli che un fornitore ha, ciascuno dal piu' economico."""
        return sum(r.totale for r in self.ordinabili)

    @property
    def totale_di_riferimento(self) -> float:
        return sum(r.totale for r in self.senza_fornitore)

    def per_fornitore(self) -> dict[str, list[RigaDellOrdine]]:
        """Gli articoli di ciascun fornitore; il fornitore con l'ordine piu' grande per primo."""
        gruppi: dict[str, list[RigaDellOrdine]] = {}
        for riga in self.ordinabili:
            assert riga.scelta is not None
            gruppi.setdefault(riga.scelta.fornitore, []).append(riga)
        return dict(sorted(gruppi.items(), key=lambda g: (-sum(r.totale for r in g[1]), g[0])))

    @property
    def articoli_in_comune(self) -> list[RigaDellOrdine]:
        """Gli articoli che tutti i fornitori dell'ordine hanno."""
        tutti = set(self.fornitori)
        return [r for r in self.ordinabili if tutti <= {v.fornitore for v in r.offerte}]

    def un_fornitore(self) -> list[UnFornitore]:
        """Per ogni fornitore, la minuteria comprata da lui (quello che non ha, altrove); il piu'
        economico sul totale per primo."""
        in_comune = self.articoli_in_comune
        risultato = []
        for fornitore in self.fornitori:
            solo = frozenset({fornitore})
            da_lui = altrove = 0.0
            ha = 0
            for riga in self.ordinabili:
                prezzo = riga.prezzo_da(solo)
                if prezzo is None:
                    assert riga.scelta is not None
                    altrove += riga.quantita * riga.scelta.prezzo
                else:
                    ha += 1
                    da_lui += riga.quantita * prezzo
            comune = sum(r.quantita * (r.prezzo_da(solo) or 0.0) for r in in_comune)
            risultato.append(UnFornitore(fornitore, ha, da_lui, len(self.ordinabili) - ha, altrove, comune))
        return sorted(risultato, key=lambda u: (u.totale, u.fornitore))

    def combinazioni(self) -> list[Combinazione]:
        tutti = self.fornitori
        if len(tutti) <= MASSIMO_PER_TUTTE_LE_COMBINAZIONI:
            gruppi = [c for n in range(1, len(tutti) + 1) for c in combinations(tutti, n)]
        else:
            gruppi = [(f,) for f in tutti] + [tuple(tutti)]
        risultato = []
        for gruppo in gruppi:
            insieme = frozenset(gruppo)
            totale = minimo = 0.0
            scoperti = 0
            for riga in self.ordinabili:
                prezzo = riga.prezzo_da(insieme)
                if prezzo is None:
                    scoperti += 1
                    continue
                assert riga.scelta is not None
                totale += riga.quantita * prezzo
                minimo += riga.quantita * riga.scelta.prezzo
            risultato.append(Combinazione(tuple(gruppo), scoperti, totale, totale - minimo))
        return sorted(risultato, key=lambda c: (len(c.fornitori), c.scoperti, c.in_piu, c.fornitori))


def ordine_della_minuteria(costo: "Costo") -> Ordine:
    """Gli articoli del costo `costo`, ciascuno col fornitore piu' economico."""
    listino: Listino = costo.listino
    quantita: dict[str, float] = {}
    voci: dict[str, list[str]] = {}
    for riga in costo.righe:
        if not riga.prezzata or riga.quantita is None:
            continue
        for codice, n in riga.codici:
            quantita[codice] = quantita.get(codice, 0.0) + riga.quantita * n
            if riga.rif not in voci.setdefault(codice, []):
                voci[codice].append(riga.rif)
    righe = []
    for codice, q in quantita.items():
        offerte = tuple(sorted(listino.ordinabili(codice), key=lambda v: (v.prezzo, v.fornitore)))
        di_riferimento = None if offerte else listino.get(codice)
        voce = offerte[0] if offerte else di_riferimento
        righe.append(RigaDellOrdine(
            codice=codice, quantita=q, um=voce.um if voce else "", descrizione=voce.descrizione if voce else "",
            voci=voci[codice], offerte=offerte, riferimento=di_riferimento,
        ))
    righe.sort(key=lambda r: -r.totale)
    return Ordine(righe)


def _euro(valore: float) -> str:
    intero, decimali = f"{valore:,.2f}".split(".")
    return f"{intero.replace(',', '.')},{decimali}"


def _prezzo(valore: float) -> str:
    """Il prezzo per unita': tre decimali sotto l'euro (il tubo al metro), due sopra."""
    testo = f"{valore:,.3f}" if valore < 1 else f"{valore:,.2f}"
    intero, decimali = testo.split(".")
    return f"{intero.replace(',', '.')},{decimali}"


def _quantita(valore: float) -> str:
    testo = f"{valore:.2f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")


def ordine_in_markdown(ordine: Ordine) -> list[str]:
    """La sezione «Dove comprare» del costo della minuteria."""
    gruppi = ordine.per_fornitore()
    righe = [
        "## Dove comprare",
        "",
        "Ogni articolo dal fornitore che lo vende al prezzo più basso, fra quelli da cui Nove C ordina (la tabella "
        "«I fornitori» del listino). Le quantità sono quelle della distinta, sommate per articolo; al banco si "
        "comprano le confezioni intere (colonna Confezione). I prezzi hanno la data del loro documento, e il conto non "
        "tiene trasporto, ordine minimo e condizioni di pagamento.",
        "",
    ]
    if not gruppi:
        righe += ["Nessun articolo della distinta ha il prezzo di un fornitore da cui si ordina.", ""]
    else:
        parti = ", ".join(f"{f} {_euro(sum(r.totale for r in rr))} € ({len(rr)} articoli)" for f, rr in gruppi.items())
        righe.append(
            f"- **Ogni articolo dal più economico: {_euro(ordine.totale)} €** in {len(gruppi)} "
            f"{'ordine' if len(gruppi) == 1 else 'ordini'} — {parti}."
        )
    senza = ordine.senza_fornitore
    if senza:
        righe.append(
            f"- **Senza un fornitore: {len(senza)} articoli**, {_euro(ordine.totale_di_riferimento)} € a prezzi di "
            "riferimento (online, o le fatture di un installatore): da comprare dove si trovano. Sono in fondo."
        )
    uno = ordine.un_fornitore()
    if len(uno) > 1:
        primo = uno[0]
        comune = ordine.articoli_in_comune
        parita = min(uno, key=lambda u: (u.in_comune, u.fornitore)) if comune else None
        frase = (
            f"- **Un fornitore solo per tutta la minuteria: il più economico è {primo.fornitore}**, "
            f"{_euro(primo.totale)} € ({_euro(primo.da_lui)} € da {primo.fornitore}"
            + (f", {_euro(primo.altrove)} € per i {primo.non_ha} articoli che non ha, da comprare altrove" if primo.non_ha else "")
            + f"): {_euro(primo.totale - ordine.totale)} € in più che dividere l'ordine."
        )
        if parita is not None:
            frase += (
                f" A parità di articoli (i {len(comune)} che hanno tutti) il più economico è {parita.fornitore}."
            )
        righe.append(frase)
    righe.append("")
    if len(uno) > 1:
        comune = ordine.articoli_in_comune
        righe += [
            "### Un fornitore solo",
            "",
            "Tutta la minuteria da un fornitore: gli articoli che ha ai suoi prezzi, quelli che non ha dal più economico "
            "degli altri (andrebbero comprati altrove), così i totali sono sullo stesso paniere. L'ultima colonna è il "
            f"conto sui soli {len(comune)} articoli che hanno tutti: dove il listino di un fornitore è incompleto, è "
            "quella che dice chi costa meno a parità di articoli.",
            "",
            "| Fornitore | Articoli che ha | € da lui | Articoli che non ha | € di quelli, altrove | Totale € | "
            "In più dell'ordine diviso € | € sugli articoli che hanno tutti |",
            "|---|--:|--:|--:|--:|--:|--:|--:|",
        ]
        for u in uno:
            righe.append(
                f"| {u.fornitore} | {u.ha} | {_euro(u.da_lui)} | {u.non_ha} | {_euro(u.altrove)} | {_euro(u.totale)} | "
                f"{_euro(u.totale - ordine.totale)} | {_euro(u.in_comune) if comune else '—'} |"
            )
        righe.append("")
    combinazioni = ordine.combinazioni()
    if len(ordine.fornitori) > 1:
        righe += [
            "### Con meno ordini",
            "",
            "Quanto costa comprare da un gruppo di fornitori soltanto: gli articoli che quel gruppo non ha restano da "
            "comprare altrove, e il confronto col minimo è sugli stessi articoli.",
            "",
            "| Fornitori | Ordini | Articoli che non hanno | € degli articoli che hanno | € in più del minimo |",
            "|---|--:|--:|--:|--:|",
        ]
        for c in combinazioni:
            righe.append(
                f"| {' + '.join(c.fornitori)} | {len(c.fornitori)} | {c.scoperti} | {_euro(c.totale)} | "
                f"{_euro(c.in_piu)} |"
            )
        righe.append("")
    for fornitore, rr in gruppi.items():
        righe += [
            f"### L'ordine a {fornitore} — {len(rr)} articoli, {_euro(sum(r.totale for r in rr))} €",
            "",
            "| Codice | Articolo | Cod. fornitore | Confezione | Q.tà | UM | €/UM | € | Gli altri | Voci |",
            "|---|---|---|---|--:|---|--:|--:|---|---|",
        ]
        for r in rr:
            assert r.scelta is not None
            altri = " · ".join(f"{v.fornitore} {_prezzo(v.prezzo)}" for v in r.offerte[1:]) or "—"
            righe.append(
                f"| {r.codice} | {r.scelta.descrizione} | {r.scelta.articolo} | {r.scelta.confezione} | "
                f"{_quantita(r.quantita)} | {r.um} | {_prezzo(r.scelta.prezzo)} | {_euro(r.totale)} | {altri} | "
                f"{', '.join(r.voci)} |"
            )
        righe.append("")
    if senza:
        righe += [
            "### Senza un fornitore",
            "",
            "| Codice | Voce | Q.tà | UM | €/UM di riferimento | € | Da dove |",
            "|---|---|--:|---|--:|--:|---|",
        ]
        for r in senza:
            fonte = r.riferimento.fonte if r.riferimento else ""
            prezzo = _prezzo(r.riferimento.prezzo) if r.riferimento else ""
            righe.append(
                f"| {r.codice} | {r.descrizione} | {_quantita(r.quantita)} | {r.um} | {prezzo} | {_euro(r.totale)} | "
                f"{fonte} |"
            )
        righe.append("")
    return righe


def _offerta(voce: VoceDelListino) -> dict[str, Any]:
    return {"fornitore": voce.fornitore, "prezzo_eur": round(voce.prezzo, 4), "articolo": voce.descrizione,
            "codice_fornitore": voce.articolo, "confezione": voce.confezione, "fonte": voce.fonte}


def ordine_in_json(ordine: Ordine) -> dict[str, Any]:
    return {
        "fornitori": ordine.fornitori,
        "totale_eur": round(ordine.totale, 2),
        "per_fornitore": {
            fornitore: {
                "totale_eur": round(sum(r.totale for r in rr), 2),
                "righe": [
                    {"codice": r.codice, "quantita": round(r.quantita, 4), "um": r.um,
                     "totale_eur": round(r.totale, 2), "voci": r.voci,
                     **({"scelta": _offerta(r.scelta)} if r.scelta else {}),
                     "altri": [_offerta(v) for v in r.offerte[1:]]}
                    for r in rr
                ],
            }
            for fornitore, rr in ordine.per_fornitore().items()
        },
        "senza_fornitore": [
            {"codice": r.codice, "quantita": round(r.quantita, 4), "um": r.um, "totale_eur": round(r.totale, 2),
             "voci": r.voci, "riferimento": _offerta(r.riferimento) if r.riferimento else None}
            for r in ordine.senza_fornitore
        ],
        "totale_di_riferimento_eur": round(ordine.totale_di_riferimento, 2),
        "un_fornitore": [
            {"fornitore": u.fornitore, "ha": u.ha, "da_lui_eur": round(u.da_lui, 2), "non_ha": u.non_ha,
             "altrove_eur": round(u.altrove, 2), "totale_eur": round(u.totale, 2),
             "in_piu_eur": round(u.totale - ordine.totale, 2), "in_comune_eur": round(u.in_comune, 2)}
            for u in ordine.un_fornitore()
        ],
        "articoli_in_comune": len(ordine.articoli_in_comune),
        "combinazioni": [
            {"fornitori": list(c.fornitori), "scoperti": c.scoperti, "totale_eur": round(c.totale, 2),
             "in_piu_eur": round(c.in_piu, 2)}
            for c in ordine.combinazioni()
        ],
    }
