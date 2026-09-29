"""Il calcolatore dei diametri (REL-007): dalla portata il DN, dalla potenza la portata.

**Le basi le ha fissate il PO** (**D-193**), e qui non si sceglie niente:

- **il DN e' il diametro interno netto** (I-150): il numero del DN, in
  millimetri, e' la sezione su cui si calcola la velocita'. Il materiale lo
  sceglie l'installatore, o il progettista, a parita' di diametro interno;
- **la serie** e' quella dei valori preferiti della EN ISO 6708 (SRC-051);
- **la velocita' massima cresce col diametro** (I-154): la tab. 9 del Quaderno
  Caleffi n. 5, colonna degli edifici residenziali e terziari (SRC-048), portata
  dai pollici ai DN — 3/4" e' DN 20, 3" e' DN 80;
- **il DN e' il piu' piccolo della serie in cui la velocita' non supera la sua
  massima**: e' il «DN standard subito piu' grande» con cui il PO lavora (I-151);
- **l'acqua** ha calore specifico 4,18 kJ/(kg·K) e densita' 1000 kg/m³, le
  costanti della skill dei computi PdC di Nove C (SRC-052). La densita' vera fra
  10 e 90 °C scende del 3,5 % (SRC-049): a quel punto il DN non cambia, se non
  proprio sul bordo fra due.

Il calcolatore **non inventa**: riceve la potenza e il salto termico, o la
portata, che ha dato il progettista (D-087, D-191). Chi li cerca nel grafo e'
`portate.py`; chi decide quali tratti portano il DN e' `tratti.py`.
"""

from dataclasses import dataclass
from math import pi

SERIE_DEI_DN: tuple[int, ...] = (10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300)
"""I DN che il calcolatore sceglie, dal piu' piccolo: i valori preferiti della
EN ISO 6708 (SRC-051), fino a DN 300. Oltre, il calcolatore non risponde."""

VELOCITA_MASSIMA_M_S: dict[int, float] = {
    10: 1.1,
    15: 1.1,
    20: 1.1,
    25: 1.3,
    32: 1.6,
    40: 1.8,
    50: 2.0,
    65: 2.2,
    80: 2.5,
    100: 2.5,
    125: 2.5,
    150: 2.5,
    200: 2.5,
    250: 2.5,
    300: 2.5,
}
"""La velocita' massima di ciascun DN, in m/s (**D-193**, punto 3).

La tab. 9 del Quaderno Caleffi n. 5 (SRC-048) dice «fino a 3/4"» 1,1 m/s: vale
per DN 20 e per quelli piu' piccoli. Dice «oltre 3"» 2,5 m/s, e 2,5 e' anche
il valore che il PO usava per tutti (I-151): da DN 80 in su."""

CALORE_SPECIFICO_KJ_KG_K = 4.18
"""Il calore specifico dell'acqua, come nella skill dei computi PdC (SRC-052)."""

DENSITA_KG_M3 = 1000.0
"""La densita' dell'acqua, come nella skill dei computi PdC (SRC-052)."""

SECONDI_ALL_ORA = 3600.0

_TOLLERANZA_RELATIVA = 1e-9
"""Quanto una velocita' puo' superare la massima ed essere ancora la massima.

Serve al bordo esatto fra due DN: la portata che da' proprio 1,1 m/s in un DN 20
deve restare DN 20, e il conto in virgola mobile puo' dare 1,1000000000000002.
Un miliardesimo non sposta nessun caso vero."""


@dataclass(frozen=True)
class Diametro:
    """Il DN scelto per una portata, con la velocita' che l'acqua ci ha."""

    dn: int
    velocita_m_s: float
    velocita_massima_m_s: float

    @property
    def scritta(self) -> str:
        """Come si scrive sulla tavola (**D-193**, punto 5; I-155)."""
        return f"Øi {self.dn}"


def portata_da_potenza(potenza_kw: float, salto_termico_k: float) -> float:
    """La portata in m³/h che porta questa potenza con questo salto termico.

    m = P / (c · ΔT) in kg/s; diviso per la densita' e' m³/s. Per 15 kW e 5 K:
    15 / (4,18 · 5) = 0,7177 kg/s, cioe' 2,584 m³/h.
    """
    if potenza_kw <= 0 or salto_termico_k <= 0:
        raise ValueError(
            f"potenza e salto termico devono essere positivi: {potenza_kw} kW, "
            f"{salto_termico_k} K"
        )
    kg_al_secondo = potenza_kw / (CALORE_SPECIFICO_KJ_KG_K * salto_termico_k)
    return kg_al_secondo / DENSITA_KG_M3 * SECONDI_ALL_ORA


def potenza_da_portata(portata_m3h: float, salto_termico_k: float) -> float:
    """La potenza in kW che una portata porta con questo salto termico: l'inversa
    di `portata_da_potenza`, per il foglio dei calcoli."""
    return portata_m3h / SECONDI_ALL_ORA * DENSITA_KG_M3 * CALORE_SPECIFICO_KJ_KG_K * salto_termico_k


def sezione_m2(dn: int) -> float:
    """La sezione interna di un DN, letto come diametro interno netto (I-150)."""
    return pi * (dn / 1000.0) ** 2 / 4.0


def velocita_m_s(portata_m3h: float, dn: int) -> float:
    """La velocita' media dell'acqua in un DN: portata diviso sezione (SRC-049)."""
    return portata_m3h / SECONDI_ALL_ORA / sezione_m2(dn)


def diametro_per(portata_m3h: float) -> Diametro | None:
    """Il piu' piccolo DN della serie in cui la velocita' non supera la sua massima.

    `None` quando nemmeno DN 300 basta: il calcolatore non estrapola, e il tratto
    resta senza DN — il foglio dei calcoli lo dice.
    """
    if portata_m3h <= 0:
        raise ValueError(f"la portata deve essere positiva: {portata_m3h} m³/h")
    for dn in SERIE_DEI_DN:
        velocita = velocita_m_s(portata_m3h, dn)
        massima = VELOCITA_MASSIMA_M_S[dn]
        if velocita <= massima * (1 + _TOLLERANZA_RELATIVA):
            return Diametro(dn=dn, velocita_m_s=velocita, velocita_massima_m_s=massima)
    return None


def portata_massima_m3h(dn: int) -> float:
    """La portata piu' grande che un DN porta alla sua velocita' massima: il bordo
    oltre il quale il calcolatore passa al DN successivo."""
    return VELOCITA_MASSIMA_M_S[dn] * sezione_m2(dn) * SECONDI_ALL_ORA


__all__ = [
    "CALORE_SPECIFICO_KJ_KG_K",
    "DENSITA_KG_M3",
    "Diametro",
    "SERIE_DEI_DN",
    "VELOCITA_MASSIMA_M_S",
    "diametro_per",
    "portata_da_potenza",
    "portata_massima_m3h",
    "potenza_da_portata",
    "sezione_m2",
    "velocita_m_s",
]
