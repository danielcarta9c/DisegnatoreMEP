"""L'interruttore magnetotermico differenziale della linea: i suoi dati, e come si scrivono
(REL-018, I-278).

Il PO, sulla tavola dell'elettrico uscita in sessione per una commessa: «è uscita senza le
protezioni elettriche (che interruttori ecc... ) non so mi sembra ci siamo persi qualcosa
rispetto al lavoro fatto sulla parte aria». Il pezzo e' `circuit-breaker-rcbo`, passante
sulla linea all'uscita del quadro, sigla QF-nn; i suoi dati sono del progettista, e per le
Shenling li propone `elettrico.costruttori` dal manuale e dalla specifica Nove C.

**I dati, con un nome fisso** (Capire §4.8, accanto ai dati elettrici di I-277):

| dato | chiave | forma |
|---|---|---|
| poli | `poli` | testo, «2P» o «4P» |
| curva | `curva` | testo, «C» |
| corrente nominale | `in_a` | numero, in A |
| corrente differenziale | `idn_ma` | numero, in mA |
| tipo del differenziale | `tipo_differenziale` | testo, «A», «F», «B» |
| ad alta velocita' | `alta_velocita` | vero o falso |

I due numeri li controlla il modello come gli altri dati con l'unita'
(`model.project.CHIAVI_DEI_DATI_NUMERICI`): positivi, o il grafo non carica.
"""

import re
from collections.abc import Mapping

from disegnatore_mep.model.types import JsonPrimitive

FUNZIONE_DI_PROTEZIONE = "circuit_protection"
"""Il mestiere dell'interruttore della linea: la sua famiglia e' QF (`naming/families.json`)."""

VOCE_DELL_INTERRUTTORE = "circuit-breaker-rcbo"
"""La voce di catalogo dell'interruttore magnetotermico differenziale."""

POLI = "poli"
CURVA = "curva"
IN_A = "in_a"
IDN_MA = "idn_ma"
TIPO_DIFFERENZIALE = "tipo_differenziale"
ALTA_VELOCITA = "alta_velocita"

DATI_DELLA_PROTEZIONE: tuple[str, ...] = (POLI, CURVA, IN_A, IDN_MA, TIPO_DIFFERENZIALE, ALTA_VELOCITA)
"""I dati dell'interruttore, nell'ordine in cui `completa` li scrive e li dice."""


def _testo(valore: JsonPrimitive | None) -> str | None:
    if not isinstance(valore, str) or not valore.strip() or valore.strip().upper() == "ND":
        return None
    return valore.strip()


def _numero(valore: JsonPrimitive | None) -> str | None:
    if isinstance(valore, bool) or not isinstance(valore, int | float):
        return None
    testo = str(valore) if isinstance(valore, int) else f"{valore:.3f}".rstrip("0").rstrip(".")
    return testo.replace(".", ",")


def scritta_della_protezione(proprieta: Mapping[str, JsonPrimitive]) -> list[str]:
    """Le caratteristiche dell'interruttore come la tabella le scrive: «2P C32» e «Idn 30 mA
    tipo B», due celle unite dal separatore della tabella. Un dato che manca non si scrive:
    senza la curva la corrente nominale si scrive con l'unita' («2P 32 A»), senza la Idn il
    tipo resta da solo («tipo B»). L'alta velocita' non si scrive: e' una qualita' che la
    distinta e la specifica dicono, e la cella resta corta."""
    poli, curva = _testo(proprieta.get(POLI)), _testo(proprieta.get(CURVA))
    nominale = _numero(proprieta.get(IN_A))
    taglia = (
        f"{curva}{nominale}" if curva and nominale else f"{nominale} A" if nominale else curva
    )
    prima = " ".join(item for item in (poli, taglia) if item)
    idn, tipo = _numero(proprieta.get(IDN_MA)), _testo(proprieta.get(TIPO_DIFFERENZIALE))
    seconda = " ".join(item for item in (f"Idn {idn} mA" if idn else None, f"tipo {tipo}" if tipo else None) if item)
    return [item for item in (prima, seconda) if item]


_SEZIONE_DEL_CAVO = re.compile(
    r"^\s*(?:(?P<conduttori>\d+)\s*[GgXx×]\s*)?(?P<mm2>\d+(?:[.,]\d+)?)\s*(?:mm2|mm²|mmq)?\s*$"
)


def sezione_in_mm2(testo: str | None) -> float | None:
    """La sezione di un conduttore da come il progettista scrive il cavo: «3G6» e «3x6» sono
    6 mm², «5G2,5» 2,5, «6 mm²» 6. Un testo che non si legge cosi' — «FG16OR16 3G6», «Ø200»
    — e' `None`: la skill non indovina, e non avvisa."""
    if not testo:
        return None
    trovato = _SEZIONE_DEL_CAVO.match(testo)
    if trovato is None:
        return None
    return float(trovato.group("mm2").replace(",", "."))


__all__ = [
    "ALTA_VELOCITA",
    "CURVA",
    "DATI_DELLA_PROTEZIONE",
    "FUNZIONE_DI_PROTEZIONE",
    "IDN_MA",
    "IN_A",
    "POLI",
    "TIPO_DIFFERENZIALE",
    "VOCE_DELL_INTERRUTTORE",
    "scritta_della_protezione",
    "sezione_in_mm2",
]
