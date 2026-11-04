"""Il tubo da comprare (I-279): il calcolo sceglie un tubo commerciale, nel suo materiale.

Il PO, il 4 novembre 2026: «il dimensionamento va fatto come dice lui. Ø32 è quello
che compro al banco. quindi il diametro interno è piu' piccolo.» Fino alla 1.10.0 la
tavola scriveva «Øi 32», il diametro interno netto minimo (D-193, punti 1 e 5): un
progettista l'ha letto come il suo 32 di sempre, il multistrato 32×3, che dentro ne ha
26. Da qui la tavola **nomina il tubo che si compra**, nella notazione del suo
materiale:

- **multistrato** «MS 32×3» — diametro esterno × spessore;
- **acciaio** «DN 25 (1")» — il diametro nominale e il pollice;
- **rame** «Cu 28×1» — diametro esterno × spessore.

**Il calcolo resta quello di D-193**, la velocita' massima della tab. 9 del Quaderno
Caleffi n. 5 (`calcolatore`), ma si fa sul **diametro interno reale** del tubo: il tubo
e' il piu' piccolo del materiale in cui la velocita' non supera la massima **del suo
pollice**. Il pollice e' quello dei raccordi e degli accessori in linea, dalla tabella
di equivalenza del produttore (MS 32×3 = 1", quindi 1,3 m/s): la tab. 9 e' scritta in
pollici. Le tabelle stanno in `tubi.json`, qui accanto, con le loro fonti.

Il materiale e' un dato del grafo (`ProjectModel.materiale_tubazioni`, e la rete lo
puo' cambiare): **senza, multistrato**, lo standard di Nove C. L'Øi resta solo nel
foglio dei calcoli, accanto al tubo scelto.
"""

import json
import re
from dataclasses import dataclass
from functools import cache
from math import pi, sqrt
from pathlib import Path
from typing import Any

from disegnatore_mep.model.project import MaterialeDelleTubazioni

from .calcolatore import SECONDI_ALL_ORA, VELOCITA_MASSIMA_M_S

Materiale = MaterialeDelleTubazioni
MATERIALI: tuple[Materiale, ...] = ("multistrato", "acciaio", "rame")
MATERIALE_PREDEFINITO: Materiale = "multistrato"
"""Senza un materiale dichiarato, il multistrato: e' lo standard di Nove C (I-279)."""

DATI = Path(__file__).with_name("tubi.json")
"""Le tabelle dei tubi, con le fonti: viaggiano col motore, nella skill."""

_TOLLERANZA_RELATIVA = 1e-9
"""Come nel calcolatore: la portata che da' proprio la massima resta in quel tubo."""


def _numero(valore: float) -> str:
    testo = f"{valore:.2f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")


@dataclass(frozen=True)
class Tubo:
    """Un tubo commerciale: quello che si compra al banco."""

    materiale: Materiale
    esterno_mm: float
    spessore_mm: float
    interno_mm: float
    """Il diametro interno reale, quello su cui si calcola la velocita'."""
    pollici: str
    """Il pollice dei raccordi e degli accessori in linea: «1"», «1¼"»."""
    dn: int | None = None
    """Il diametro nominale dell'acciaio; `None` per multistrato e rame."""

    @property
    def scritta(self) -> str:
        """Come si scrive sulla tavola: «MS 32×3», «DN 25 (1")», «Cu 28×1»."""
        if self.materiale == "acciaio":
            return f"DN {self.dn} ({self.pollici})"
        sigla = tabelle().sigle[self.materiale]
        return f"{sigla} {_numero(self.esterno_mm)}×{_numero(self.spessore_mm)}"

    @property
    def dicitura(self) -> str:
        """Come lo dice la distinta: «multistrato MS 32×3», «acciaio DN 25 (1")»."""
        return f"{tabelle().nomi[self.materiale]} {self.scritta}"

    @property
    def dn_del_pollice(self) -> int:
        """Il DN della tabella delle velocita' (D-193) che corrisponde al pollice."""
        return tabelle().dn_del_pollice[self.pollici]

    @property
    def velocita_massima_m_s(self) -> float:
        """La massima del suo pollice, dalla tab. 9 del Quaderno Caleffi n. 5."""
        return VELOCITA_MASSIMA_M_S[self.dn_del_pollice]

    @property
    def sezione_m2(self) -> float:
        return pi * (self.interno_mm / 1000.0) ** 2 / 4.0

    def velocita_m_s(self, portata_m3h: float) -> float:
        return portata_m3h / SECONDI_ALL_ORA / self.sezione_m2

    @property
    def portata_massima_m3h(self) -> float:
        return self.velocita_massima_m_s * self.sezione_m2 * SECONDI_ALL_ORA


@dataclass(frozen=True)
class Tabelle:
    tubi: dict[Materiale, tuple[Tubo, ...]]
    sigle: dict[Materiale, str]
    nomi: dict[Materiale, str]
    legende: dict[Materiale, str]
    dn_del_pollice: dict[str, int]
    pollici: tuple[str, ...]
    """I pollici dal piu' piccolo."""


@cache
def tabelle() -> Tabelle:
    dati: dict[str, Any] = json.loads(DATI.read_text(encoding="utf-8"))
    tubi: dict[Materiale, tuple[Tubo, ...]] = {}
    sigle: dict[Materiale, str] = {}
    nomi: dict[Materiale, str] = {}
    legende: dict[Materiale, str] = {}
    for materiale in MATERIALI:
        voce = dati["materiali"][materiale]
        sigle[materiale] = str(voce["sigla"])
        nomi[materiale] = str(voce["nome"])
        legende[materiale] = str(voce["legenda"])
        tubi[materiale] = tuple(
            Tubo(
                materiale=materiale,
                esterno_mm=float(riga["esterno_mm"]),
                spessore_mm=float(riga["spessore_mm"]),
                interno_mm=float(riga["interno_mm"]),
                pollici=str(riga["pollici"]),
                dn=int(riga["dn"]) if "dn" in riga else None,
            )
            for riga in voce["tubi"]
        )
    dn_del_pollice = {str(k): int(v) for k, v in dati["dn_del_pollice"].items()}
    return Tabelle(
        tubi=tubi,
        sigle=sigle,
        nomi=nomi,
        legende=legende,
        dn_del_pollice=dn_del_pollice,
        pollici=tuple(sorted(dn_del_pollice, key=dn_del_pollice.__getitem__)),
    )


def tubi_del_materiale(materiale: Materiale) -> tuple[Tubo, ...]:
    return tabelle().tubi[materiale]


def ordine_del_pollice(pollici: str) -> int:
    """Il posto del pollice nella serie, dal piu' piccolo: per confrontarli."""
    return tabelle().pollici.index(pollici)


def legenda_del_materiale(materiale: Materiale) -> tuple[str, str]:
    """La riga della legenda: il campione e la spiegazione — «MS», «multistrato,
    diametro esterno × spessore»."""
    return tabelle().sigle[materiale], tabelle().legende[materiale]


@dataclass(frozen=True)
class TuboScelto:
    """Il tubo che il calcolo sceglie per una portata, con i suoi numeri."""

    tubo: Tubo
    velocita_m_s: float
    """La velocita' reale, nel diametro interno reale."""
    interno_minimo_mm: float
    """Il diametro interno sotto il quale la velocita' supererebbe la massima del
    pollice del tubo scelto: l'Øi minimo del foglio dei calcoli."""

    @property
    def velocita_massima_m_s(self) -> float:
        return self.tubo.velocita_massima_m_s

    @property
    def dn(self) -> int:
        """Il DN della tabella delle velocita' del suo pollice (1" = DN 25)."""
        return self.tubo.dn_del_pollice

    @property
    def scritta(self) -> str:
        return self.tubo.scritta


def _sta_nel_limite(tubo: Tubo, portata_m3h: float) -> bool:
    return tubo.velocita_m_s(portata_m3h) <= tubo.velocita_massima_m_s * (1 + _TOLLERANZA_RELATIVA)


def tubo_per(portata_m3h: float, materiale: Materiale = MATERIALE_PREDEFINITO) -> TuboScelto | None:
    """Il piu' piccolo tubo del materiale in cui la velocita' reale non supera la
    massima del suo pollice. **Solo la velocita'**: l'attacco della macchina non e' un
    minimo (I-281), e dove il tubo e' piu' piccolo dell'attacco c'e' una riduzione
    (`costruttori.riduzioni_all_attacco`).

    `None` quando nemmeno l'ultimo tubo della tabella basta: il calcolo non inventa
    un tubo che la tabella non ha, e il foglio dei calcoli lo dice."""
    if portata_m3h <= 0:
        raise ValueError(f"la portata deve essere positiva: {portata_m3h} m³/h")
    scelto = next((tubo for tubo in tubi_del_materiale(materiale) if _sta_nel_limite(tubo, portata_m3h)), None)
    if scelto is None:
        return None
    minimo = sqrt(4 * portata_m3h / SECONDI_ALL_ORA / (pi * scelto.velocita_massima_m_s)) * 1000
    return TuboScelto(tubo=scelto, velocita_m_s=scelto.velocita_m_s(portata_m3h), interno_minimo_mm=minimo)


def ultimo_tubo(materiale: Materiale) -> Tubo:
    return tubi_del_materiale(materiale)[-1]


# --- il dato del progettista ----------------------------------------------------

_DECIMALE = r"\d+(?:[.,]\d+)?"
_PER = r"\s*[x×X*]\s*"
_POLLICI_IN_TESTO: dict[str, str] = {
    "3/8": '3/8"',
    "1/2": '½"',
    "½": '½"',
    "3/4": '¾"',
    "¾": '¾"',
    "1": '1"',
    "1 1/4": '1¼"',
    "1¼": '1¼"',
    "1 1/2": '1½"',
    "1½": '1½"',
    "2": '2"',
    "2 1/2": '2½"',
    "2½": '2½"',
    "3": '3"',
    "4": '4"',
}


def _a_numero(testo: str) -> float:
    return float(testo.replace(",", "."))


def _per_misure(materiale: Materiale, esterno: float, spessore: float) -> Tubo | None:
    return next(
        (
            t
            for t in tubi_del_materiale(materiale)
            if abs(t.esterno_mm - esterno) < 1e-6 and abs(t.spessore_mm - spessore) < 1e-6
        ),
        None,
    )


def _acciaio_per_dn(dn: int) -> Tubo | None:
    return next((t for t in tubi_del_materiale("acciaio") if t.dn == dn), None)


def _acciaio_per_pollici(pollici: str) -> Tubo | None:
    return next((t for t in tubi_del_materiale("acciaio") if t.pollici == pollici), None)


def tubo_dal_testo(testo: str | None) -> Tubo | None:
    """Il tubo che il progettista ha scritto nella `sezione` di una tubazione, nelle
    tre notazioni: «MS 32×3», «32x3», «multistrato 32x3»; «DN 25», «DN 25 (1")»,
    «1"», «1 1/4"»; «Cu 28×1», «rame 28x1». `None` se non si legge, o se la tabella
    non ha quel tubo: allora non si controlla niente, e non si dice niente."""
    if not testo:
        return None
    pulito = testo.strip().replace("”", '"').replace("″", '"').replace("''", '"')
    minuscolo = pulito.lower()
    misure = re.search(rf"({_DECIMALE}){_PER}({_DECIMALE})", pulito)
    if misure is not None:
        esterno, spessore = _a_numero(misure.group(1)), _a_numero(misure.group(2))
        if re.search(r"\bcu\b|rame", minuscolo):
            return _per_misure("rame", esterno, spessore)
        if re.search(r"\bms\b|multistrato", minuscolo):
            return _per_misure("multistrato", esterno, spessore)
        return _per_misure("multistrato", esterno, spessore) or _per_misure("rame", esterno, spessore)
    dn = re.search(r"\bdn\s*(\d+)\b", minuscolo)
    if dn is not None:
        return _acciaio_per_dn(int(dn.group(1)))
    pollice = re.search(r'(\d\s+\d/\d|\d/\d|\d[¼½¾]|[½¾]|\d)\s*"', pulito)
    if pollice is not None:
        chiave = re.sub(r"\s+", " ", pollice.group(1))
        normale = _POLLICI_IN_TESTO.get(chiave)
        return None if normale is None else _acciaio_per_pollici(normale)
    return None


__all__ = [
    "DATI",
    "MATERIALE_PREDEFINITO",
    "MATERIALI",
    "Materiale",
    "Tubo",
    "TuboScelto",
    "legenda_del_materiale",
    "ordine_del_pollice",
    "tabelle",
    "tubi_del_materiale",
    "tubo_dal_testo",
    "tubo_per",
    "ultimo_tubo",
]
