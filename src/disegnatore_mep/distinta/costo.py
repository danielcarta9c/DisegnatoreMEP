"""Il costo della minuteria: la distinta prezzata con il listino (REL-021, I-284).

Un conto **interno a Nove C**: quanto costa, a prezzi di listino, il materiale che la
distinta conta — per confrontare i preventivi degli installatori, o per comprarlo. Non
entra nel documento per l'installatore, che resta senza prezzi (D-235); si scrive accanto,
in un file suo.

Che cosa si prezza: le voci di materiale (sezioni S, B, C, D, I, E e le voci senza regola
della X). Non si prezzano le apparecchiature (A: macchine, accumuli, bollitori, che Nove C
compra a parte), le opere e le attivita' (F, G, H, Z, V, e le voci a corpo: manodopera,
non minuteria) e le voci del Committente. Ogni voce prezzata dice i suoi codici del listino, il prezzo netto
per unita' e il conto; una voce senza codice, o con un codice che il listino non ha, o con
la quantita' DA DEFINIRE, e' **DA PREZZARE** e lo dice: non si stima.

Il prezzo e' il **consumo**: quantita' × prezzo per unita' di misura del listino. Le
confezioni intere (il rotolo da 50 m per 12 m di tubo) costano di piu': il conto lo dice,
non le arrotonda.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .calcolo import DA_DEFINIRE, Distinta, Voce
from .listino import Listino
from .lunghezze import in_parole

SEZIONI_DI_MATERIALE = ("S", "B", "C", "D", "I", "E", "X")
"""Le sezioni la cui roba si compra; le altre sono macchine, opere o attivita'."""

DA_PREZZARE = "DA PREZZARE"


@dataclass
class RigaDelCosto:
    rif: str
    sezione: str
    testo: str
    quantita: float | None
    um: str
    codici: list[tuple[str, float]]
    """Per unita' della voce, quante unita' di ciascun codice."""
    unitario: float | None
    """Euro netti per unita' della voce."""
    totale: float | None
    conto: str
    manca: str = ""
    nota: str = ""

    @property
    def prezzata(self) -> bool:
        return self.totale is not None


@dataclass
class Costo:
    progetto: dict[str, str]
    listino: Listino
    righe: list[RigaDelCosto] = field(default_factory=list)
    fuori: list[tuple[str, str]] = field(default_factory=list)
    """Le voci che non si prezzano, con il perche' (sezione)."""

    @property
    def totale(self) -> float:
        return sum(r.totale or 0.0 for r in self.righe)

    @property
    def da_prezzare(self) -> list[RigaDelCosto]:
        return [r for r in self.righe if not r.prezzata]

    def per_sezione(self) -> dict[str, float]:
        totali: dict[str, float] = {}
        for riga in self.righe:
            totali[riga.sezione] = totali.get(riga.sezione, 0.0) + (riga.totale or 0.0)
        return totali


def _euro(valore: float) -> str:
    intero, decimali = f"{valore:,.2f}".split(".")
    return f"{intero.replace(',', '.')},{decimali}"


def _riga(voce: Voce, listino: Listino) -> RigaDelCosto:
    prezzo = voce.prezzo
    riga = RigaDelCosto(
        rif=voce.rif, sezione=voce.sezione, testo=voce.testo, quantita=voce.quantita, um=voce.um,
        codici=list(prezzo.codici) if prezzo else [], unitario=None, totale=None, conto="",
        nota=prezzo.nota if prezzo else "",
    )
    if prezzo is None:
        riga.manca = "le regole non le danno un codice del listino"
        return riga
    if prezzo.manca:
        riga.manca = prezzo.manca
        return riga
    parti, unitario = [], 0.0
    for codice, n in prezzo.codici:
        trovata = listino.get(codice)
        if trovata is None:
            riga.manca = f"il listino non ha il codice {codice}"
            return riga
        unitario += n * trovata.prezzo
        parti.append(f"{in_parole(n)} × {codice} {_euro(trovata.prezzo)} €/{trovata.um}" if n != 1 else
                     f"{codice} {_euro(trovata.prezzo)} €/{trovata.um}")
    riga.unitario = unitario
    if voce.quantita is None:
        riga.manca = f"quantita' {DA_DEFINIRE}"
        riga.conto = " + ".join(parti)
        return riga
    riga.totale = voce.quantita * unitario
    riga.conto = f"{in_parole(voce.quantita)} {voce.um} × ({' + '.join(parti)})"
    return riga


def prezza_la_distinta(distinta: Distinta, listino: Listino) -> Costo:
    costo = Costo(progetto=dict(distinta.progetto), listino=listino)
    for voce in distinta.voci:
        if voce.sezione not in SEZIONI_DI_MATERIALE or voce.um == "a corpo":
            costo.fuori.append((voce.rif, voce.sezione))
            continue
        if voce.fornitura and voce.fornitura not in (distinta.regole.distinta.get("fornitura_installatore"), DA_DEFINIRE):
            costo.fuori.append((voce.rif, voce.sezione))
            continue
        costo.righe.append(_riga(voce, listino))
    return costo


def costo_in_json(costo: Costo) -> dict[str, Any]:
    return {
        "formato": "costo-minuteria",
        "versione": 1,
        "progetto": costo.progetto,
        "listino": {"titolo": costo.listino.titolo, "revisione": costo.listino.revisione,
                    "percorso": costo.listino.percorso.name},
        "totale_eur": round(costo.totale, 2),
        "per_sezione_eur": {k: round(v, 2) for k, v in costo.per_sezione().items()},
        "righe": [
            {
                "rif": r.rif, "testo": r.testo, "quantita": r.quantita, "um": r.um,
                "codici": [{"codice": c, "n": n} for c, n in r.codici],
                "unitario_eur": None if r.unitario is None else round(r.unitario, 4),
                "totale_eur": None if r.totale is None else round(r.totale, 2),
                "conto": r.conto, "da_prezzare": r.manca, "nota": r.nota,
            }
            for r in costo.righe
        ],
    }


def costo_in_markdown(costo: Costo, titoli: dict[str, str]) -> str:
    nome = costo.progetto.get("project_name") or costo.progetto.get("drawing_title") or "impianto"
    prezzate = [r for r in costo.righe if r.prezzata]
    righe = [
        f"# Costo della minuteria — {nome}",
        "",
        "> **Uso interno Nove C.** Non va all'installatore: il suo documento resta senza prezzi. È il costo, a "
        "prezzi di listino, del materiale che la distinta conta (tubi, raccordi, valvolame, canali, cavi, accessori), "
        "**escluse le apparecchiature** della sezione A (macchine, unità interne ed esterne, accumuli, bollitori, "
        "plenum motorizzati: si comprano a parte) e la manodopera.",
        "",
        f"- **Listino:** {costo.listino.titolo}, revisione {costo.listino.revisione or '—'}. Prezzi netti, IVA esclusa.",
        f"- **Totale prezzato: {_euro(costo.totale)} €**, su {len(prezzate)} voci di {len(costo.righe)}.",
        f"- **Da prezzare: {len(costo.da_prezzare)} voci**, che il totale non contiene (elencate in fondo, ciascuna "
        "col suo perché).",
        "- Il conto è quantità × prezzo per unità del listino. Le quantità sono quelle della distinta: già maggiorate "
        "per l'offerta a corpo (+15%, i minimi delle linee), e dove la distinta conta confezioni (il flessibile in "
        "rotoli da 10 m) si pagano le confezioni intere; il resto è il consumo, e al banco le confezioni intere costano "
        "di più.",
        "",
        "## Per sezione",
        "",
        "| Sezione | Voci prezzate | Da prezzare | Totale € |",
        "|---|--:|--:|--:|",
    ]
    for lettera, totale in costo.per_sezione().items():
        della = [r for r in costo.righe if r.sezione == lettera]
        righe.append(
            f"| {lettera} — {titoli.get(lettera, '')} | {sum(1 for r in della if r.prezzata)} | "
            f"{sum(1 for r in della if not r.prezzata)} | {_euro(totale)} |"
        )
    righe += [f"| **Totale** | {len(prezzate)} | {len(costo.da_prezzare)} | **{_euro(costo.totale)}** |", ""]
    righe += ["## Le voci prezzate", "", "| Rif. | Voce | Q.tà | UM | € unitario | € totale | Conto | Nota |",
              "|---|---|--:|---|--:|--:|---|---|"]
    for r in prezzate:
        righe.append(
            f"| {r.rif} | {r.testo} | {in_parole(r.quantita or 0)} | {r.um} | {_euro(r.unitario or 0)} | "
            f"{_euro(r.totale or 0)} | {r.conto} | {r.nota} |"
        )
    righe += ["", "## Da prezzare", ""]
    if costo.da_prezzare:
        righe += ["| Rif. | Voce | Q.tà | UM | Perché | € unitario se noto |", "|---|---|--:|---|---|--:|"]
        for r in costo.da_prezzare:
            quantita = DA_DEFINIRE if r.quantita is None else in_parole(r.quantita)
            unitario = "" if r.unitario is None else _euro(r.unitario)
            righe.append(f"| {r.rif} | {r.testo} | {quantita} | {r.um} | {r.manca} | {unitario} |")
    else:
        righe.append("Nessuna: tutte le voci di materiale hanno un prezzo.")
    righe.append("")
    return "\n".join(righe)


def scrivi_il_costo(costo: Costo, uscita: Path, titoli: dict[str, str]) -> list[Path]:
    uscita.mkdir(parents=True, exist_ok=True)
    md = uscita / "costo-minuteria.md"
    md.write_text(costo_in_markdown(costo, titoli), encoding="utf-8")
    js = uscita / "costo-minuteria.json"
    js.write_text(json.dumps(costo_in_json(costo), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [md, js]
