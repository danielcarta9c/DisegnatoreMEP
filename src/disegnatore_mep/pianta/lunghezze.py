"""Le lunghezze dei tracciati: quella del progettista, quella misurata, e da quotare.

**La lunghezza e' del progettista** (`lunghezza_m` del tracciato: la stessa
del grafo dello schema). Se c'e', la tavola quota **quella**, con la regola
della distinta, e pianta e distinta danno lo stesso numero per la stessa
tratta; la misura in pianta e' un controllo, e se la supera di oltre lo scarto
dichiarato (`parametri.scarto_della_misura`) la tavola lo dice. Se il
progettista non l'ha data, si quota la misura, e la tabella lo dice.

**La regola non e' scritta qui**: e' il dato della distinta,
`rules/distinta/lunghezze.json` (nella skill il fascio `dati/distinta.json`):
la maggiorazione, il minimo della classe del fluido, il minimo scritto sul
tratto, il cavo che segue le linee frigorifere. Qui si legge quel file e si
applica la stessa formula di `distinta/lunghezze.py`.

**Perche' non si importa il modulo della distinta**: la distinta e' spenta di
default e nessun modulo del motore la importa, salvo il comando della skill
(`tests/distinta/test_da_definire.py`, proposta D-213). La pianta ne legge il
**dato**, non il codice; che le due formule diano lo stesso numero lo prova
`tests/pianta/test_collaudo_t1.py`, valore per valore, contro la funzione della
distinta.

Una `maggiorazione` dichiarata nella pianta sostituisce la regola — e la tavola
lo scrive, perche' allora i due numeri possono non coincidere.

La lunghezza misurata e' quella della spezzata disegnata, dal bordo di un pezzo
a quello dell'altro; le salite e le discese non si vedono in pianta, e stanno
nell'aggiunta della regola.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .instrada import Percorso
from .modello import Maggiorazione, Tracciato

TOLLERANZA = 1e-9
"""12 / 1,2 fa 10,000000000000002 in virgola mobile: l'eccesso non conta il rumore."""


class ErroreDellaRegola(ValueError):
    """La regola delle lunghezze non si legge: il messaggio dice dove."""


@dataclass(frozen=True)
class Minimo:
    metri: float
    perche: str


@dataclass(frozen=True)
class Lunghezza:
    tratta: str
    fluido: str
    misurata_m: float
    data_m: float | None
    """La lunghezza del progettista, se l'ha data."""
    da_quotare_m: float
    minimo_m: float | None
    """Il minimo, se e' lui a decidere la lunghezza da quotare."""
    calcolo: str = ""
    """Il conto scritto, come nella distinta: «(5 + 1) × 1,15 = 6,9 → 7 m»."""
    scarto: float | None = None
    """misurata / data - 1, se c'e' la lunghezza data."""
    oltre_lo_scarto: bool = False
    """La misura supera la lunghezza data di oltre lo scarto ammesso."""

    @property
    def usata_m(self) -> float:
        """La lunghezza che si quota: quella data, o la misura."""
        return self.data_m if self.data_m is not None else self.misurata_m

    @property
    def dalla_misura(self) -> bool:
        return self.data_m is None


def in_parole(valore: float, cifre: int = 2) -> str:
    """6 → «6», 3.5 → «3,5»: la virgola, senza zeri in coda."""
    testo = f"{valore:.{cifre}f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",") if testo not in ("", "-0") else "0"


def per_eccesso(valore: float, passo: float) -> float:
    """Il multiplo del passo subito sopra (o uguale)."""
    return round(math.ceil(valore / passo - TOLLERANZA) * passo, 6)


def maggiora(stimata: float, regola: Mapping[str, Any], minimi: Sequence[Minimo] = ()) -> tuple[float, str]:
    """`(L + aggiunta) × fattore`, per eccesso al passo, mai sotto i minimi: la
    formula di `distinta/lunghezze.py`, col suo conto scritto."""
    aggiunta, fattore, passo = float(regola["aggiunta_m"]), float(regola["fattore"]), float(regola["passo_m"])
    grezza = (stimata + aggiunta) * fattore
    risultato = per_eccesso(grezza, passo)
    calcolo = (
        f"({in_parole(stimata)} + {in_parole(aggiunta)}) × {in_parole(fattore)} = {in_parole(grezza)}"
        f" → {in_parole(risultato)} m"
    )
    for minimo in minimi:
        if minimo.metri > risultato + TOLLERANZA:
            risultato = minimo.metri
            calcolo += f"; {minimo.perche} {in_parole(minimo.metri)} m → {in_parole(risultato)} m"
    return risultato, calcolo


def leggi_la_regola(percorso: Path) -> dict[str, Any]:
    """`lunghezze.json` delle regole della distinta: da una cartella
    (`rules/distinta/`) o dal fascio della skill (`dati/distinta.json`)."""
    try:
        if percorso.is_dir():
            dati = json.loads((percorso / "lunghezze.json").read_text(encoding="utf-8"))
        else:
            dati = json.loads(percorso.read_text(encoding="utf-8"))["file"]["lunghezze.json"]
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as errore:
        raise ErroreDellaRegola(f"{percorso}: la regola delle lunghezze non si legge ({errore})") from errore
    regola = dati.get("regola", {}) if isinstance(dati, dict) else {}
    for chiave in ("aggiunta_m", "fattore", "passo_m"):
        if not isinstance(regola.get(chiave), int | float):
            raise ErroreDellaRegola(f"{percorso}: la regola delle lunghezze non ha il numero «{chiave}»")
    return dati


@dataclass(frozen=True)
class Regola:
    """La regola delle lunghezze che vale per la tavola, e da dove viene."""

    distinta: Mapping[str, Any] | None
    """Il contenuto di `lunghezze.json` delle regole della distinta."""
    dichiarata: Maggiorazione | None
    origine: str
    """Per la nota della tavola e per la console: da dove viene la regola."""

    @property
    def della_distinta(self) -> bool:
        return self.dichiarata is None and self.distinta is not None

    @property
    def regola(self) -> Mapping[str, Any]:
        """aggiunta_m, fattore, passo_m."""
        if self.dichiarata is not None or self.distinta is None:
            m = self.dichiarata or Maggiorazione()
            return {"aggiunta_m": m.aggiunta_m, "fattore": m.fattore, "passo_m": m.arrotondamento_m}
        return self.distinta["regola"]

    def minimo_della_classe(self, fluido: str) -> Minimo | None:
        if self.dichiarata is not None or self.distinta is None:
            minimi = (self.dichiarata or Maggiorazione()).minimi_m
            valore = minimi.get(fluido)  # type: ignore[call-overload]
            return Minimo(float(valore), "minimo del fluido") if valore else None
        for classe in self.distinta.get("classi", []):
            if fluido in classe.get("fluidi", []) and float(classe.get("minimo_m", 0)) > 0:
                return Minimo(float(classe["minimo_m"]), f"minimo {classe['classe']}")
        return None

    def segue(self, fluido: str) -> Mapping[str, Any] | None:
        if not self.della_distinta:
            return None
        assert self.distinta is not None
        for voce in self.distinta.get("segue", []):
            if voce.get("fluido") == fluido:
                return voce
        return None

    def minimi_del_testo(self) -> list[str]:
        """I minimi in parole, per la nota della tavola."""
        if not self.della_distinta:
            minimi = (self.dichiarata or Maggiorazione()).minimi_m
            return [f"{f} {in_parole(v)} m" for f, v in sorted(minimi.items())]
        assert self.distinta is not None
        out = [
            f"{c['classe'].replace('_', ' ')} {in_parole(float(c['minimo_m']))} m"
            for c in self.distinta.get("classi", []) if float(c.get("minimo_m", 0)) > 0
        ]
        out += [
            f"il cavo fra le unita' segue le linee frigo + {in_parole(float(s['in_piu_m']))} m"
            for s in self.distinta.get("segue", [])
        ]
        return out


def trova_le_regole_della_distinta(partenza: Path | None = None) -> Path | None:
    """Dove stanno le regole della distinta, risalendo dal modulo: nel
    repository `rules/distinta/`, nella skill il fascio `dati/distinta.json`."""
    qui = (partenza or Path(__file__)).resolve()
    for cartella in qui.parents:
        for candidato in (cartella / "rules" / "distinta", cartella / "dati" / "distinta.json"):
            if candidato.exists():
                return candidato
    return None


def la_regola(dichiarata: Maggiorazione | None, percorso: Path | None = None) -> Regola:
    """La regola della tavola: quella della distinta, salvo una `maggiorazione`
    dichiarata nella pianta."""
    if dichiarata is not None:
        return Regola(None, dichiarata, "dichiarata nella pianta (non e' quella della distinta)")
    trovato = percorso or trova_le_regole_della_distinta()
    if trovato is None:
        return Regola(None, None, "del kit, perche' le regole della distinta non ci sono: va detto")
    return Regola(leggi_la_regola(trovato), None, "della distinta")


def da_quotare(misurata: float, regola: Maggiorazione, fluido: str) -> tuple[float, float | None]:
    """La regola dichiarata nella pianta: `(misurata + aggiunta) × fattore`, per
    eccesso all'arrotondamento, mai sotto il minimo del fluido. Torna anche il
    minimo, se ha deciso lui."""
    passo = regola.arrotondamento_m
    valore = math.ceil((misurata + regola.aggiunta_m) * regola.fattore / passo - 1e-9) * passo
    valore = round(valore, 6)
    minimo = regola.minimi_m.get(fluido)  # type: ignore[call-overload]
    if minimo is not None and minimo > valore:
        return float(minimo), float(minimo)
    return valore, None


def lunghezze(
    tracciati: Sequence[Tracciato], percorsi: Sequence[Percorso], regola: Regola, scarto_ammesso: float = 0.15,
) -> list[Lunghezza]:
    """Le lunghezze di ogni tratta, nell'ordine dei tracciati. Il cavo che
    segue le linee frigorifere si fa dopo di loro, come nella distinta."""
    misurate = {t.tratta: round(p.lunghezza_m, 3) for t, p in zip(tracciati, percorsi, strict=True)}
    fatte: dict[str, Lunghezza] = {}

    def calcola(tracciato: Tracciato, altri: Sequence[Minimo]) -> Lunghezza:
        misurata = misurate[tracciato.tratta]
        data = tracciato.lunghezza_m
        usata = data if data is not None else misurata
        minimi: list[Minimo] = []
        della_classe = regola.minimo_della_classe(tracciato.fluido)
        if della_classe is not None:
            minimi.append(della_classe)
        if tracciato.lunghezza_minima_m:
            minimi.append(Minimo(tracciato.lunghezza_minima_m, "minimo scritto sul tratto"))
        minimi.extend(altri)
        quotare, calcolo = maggiora(usata, regola.regola, minimi)
        maggiorata, _ = maggiora(usata, regola.regola)
        scarto = None if not data else round(misurata / data - 1, 3)
        return Lunghezza(
            tratta=tracciato.tratta, fluido=tracciato.fluido, misurata_m=misurata, data_m=data,
            da_quotare_m=quotare,
            minimo_m=quotare if quotare > maggiorata + TOLLERANZA else None,
            calcolo=calcolo, scarto=scarto,
            oltre_lo_scarto=scarto is not None and scarto > scarto_ammesso + TOLLERANZA,
        )

    for tracciato in tracciati:
        if regola.segue(tracciato.fluido) is None:
            fatte[tracciato.tratta] = calcola(tracciato, ())
    for tracciato in tracciati:
        voce = regola.segue(tracciato.fluido)
        if voce is None:
            continue
        capi = {tracciato.estremo_da.pezzo, tracciato.estremo_a.pezzo}
        seguiti = [
            fatte[t.tratta] for t in tracciati
            if t.fluido in voce["fluidi_seguiti"] and {t.estremo_da.pezzo, t.estremo_a.pezzo} == capi
        ]
        altri: list[Minimo] = []
        if seguiti:
            lunga = max(seguiti, key=lambda lu: lu.da_quotare_m)
            in_piu = float(voce["in_piu_m"])
            altri.append(Minimo(lunga.da_quotare_m + in_piu, f"segue {lunga.tratta} + {in_parole(in_piu)} m:"))
        fatte[tracciato.tratta] = calcola(tracciato, altri)
    return [fatte[t.tratta] for t in tracciati]


def metri(valore: float, decimali: int = 1) -> str:
    """6 → «6», 6.5 → «6,5», 2.35 → «2,4»: la virgola, e niente zeri inutili."""
    testo = f"{valore:.{decimali}f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")
