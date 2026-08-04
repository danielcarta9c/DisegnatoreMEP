"""Come si compone una tavola: livelli, non colonne.

Le regole vengono da una tavola di riferimento fornita dal PM — uno schema di
pompa di calore monoblocco con ACS, compensatore e circolatore — misurata per
ricavarne proporzioni e quote. Prima di questo il motore impilava i componenti
in quattro colonne verticali: geometricamente valido, e non uno schema.

Quello che una tavola vera fa, e che qui si codifica:

- c'è una **linea di terra**, e le macchine ci stanno **sopra**, allineate in
  basso. Non sono appese in aria;
- l'impianto si sviluppa **da sinistra a destra** seguendo il processo:
  generazione, primario, distribuzione, utenza;
- le tubazioni corrono su **corsie orizzontali a quote fisse**, con la
  **mandata sopra il ritorno**;
- gli **ausiliari** — filtro, vaso, gruppo di riempimento — stanno **in basso**,
  fra la corsia di ritorno e la terra;
- la **regolazione** corre tratteggiata **sopra tutto**;
- le denominazioni stanno **fuori dal corpo**, sopra e sotto, con linea di
  richiamo.

Le percentuali sono quelle misurate sul riferimento, riferite all'altezza
dell'area di disegno.
"""

from dataclasses import dataclass
from enum import StrEnum

CONTROL_BAND = 0.15
"""Quota della corsia di regolazione, tratteggiata, sopra tutto il resto."""

UPPER_SUPPLY = 0.45
UPPER_RETURN = 0.50
"""Corsie alte: il primario che scavalca i componenti bassi."""

LOWER_SUPPLY = 0.63
LOWER_RETURN = 0.72
"""Corsie basse: gli attacchi delle macchine appoggiate a terra."""

AUXILIARY_BAND = 0.78
"""Quota degli ausiliari: sotto il ritorno, sopra la terra."""

GROUND_LINE = 0.83
"""La linea di terra. Le macchine ci appoggiano sopra."""

CALLOUT_BAND = 0.95
"""Le denominazioni sotto la linea di terra, con linea di richiamo."""

CALLOUT_GAP_MM = 10.0
"""Quanto sotto la linea di terra corre la riga dei richiami.

E' una distanza, non una frazione del foglio: quattro passi di griglia bastano
a scavalcare il tratteggio del terreno e a staccare il testo. Misurata come
frazione, su una A3 apriva ventotto millimetri di vuoto fra il disegno e i
propri richiami, e il blocco da centrare risultava alto il doppio di quello
che disegna davvero."""

SUPPLY_RETURN_GAP = UPPER_RETURN - UPPER_SUPPLY
"""Distacco fra mandata e ritorno: 9% dell'altezza sul riferimento."""


class Standing(StrEnum):
    """Come un componente sta sulla tavola.

    Non è il dominio né la funzione impiantistica: è dove il disegno lo mette.
    Un bollitore e una pompa di calore stanno a terra, un circolatore sta su una
    tubazione, un vaso di espansione pende sotto il ritorno.
    """

    GROUND = "ground"
    """Appoggiato alla linea di terra, allineato in basso: macchine e accumuli."""

    RAIL = "rail"
    """Sulla tubazione, alla quota della corsia: valvole, circolatori, strumenti."""

    AUXILIARY = "auxiliary"
    """Appeso sotto il ritorno: vaso, filtro, gruppo di riempimento, scarichi."""


GROUND_HEIGHT_MM = 20.0
"""Da quest'altezza in su un componente si considera una macchina che sta a terra.

È la soglia che separa un accumulo da un apparecchio: sul riferimento la
distanza fra i due gruppi è netta — 18% dell'altezza del corpo contro 5% — e
qualunque valore in mezzo dà la stessa classificazione.
"""

AUXILIARY_FUNCTIONS = frozenset(
    {
        "expansion",
        "filtration",
        "filling",
        "air_release",
        "drain",
        "water_treatment",
    }
)
"""Funzioni che portano un componente sotto la corsia di ritorno.

Sono funzioni di **catalogo**, non nomi di componente: un filtro sta in basso
perché filtra, non perché si chiama filtro.
"""


@dataclass(frozen=True)
class Levels:
    """Le quote della tavola, gia' portate su nodi di griglia.

    Snappate una volta sola e condivise: se il posizionamento arrotondasse per
    conto proprio, una macchina finirebbe accanto alla linea di terra invece che
    sopra, e lo scarto non si vedrebbe finche' non lo si misura.
    """

    control_mm: float
    upper_supply_mm: float
    upper_return_mm: float
    lower_supply_mm: float
    lower_return_mm: float
    auxiliary_mm: float
    ground_mm: float
    callout_mm: float


def levels_of(top_mm: float, height_mm: float, step_mm: float) -> Levels:
    def at(fraction: float) -> float:
        return top_mm + round(height_mm * fraction / step_mm) * step_mm

    return Levels(
        control_mm=at(CONTROL_BAND),
        upper_supply_mm=at(UPPER_SUPPLY),
        upper_return_mm=at(UPPER_RETURN),
        lower_supply_mm=at(LOWER_SUPPLY),
        lower_return_mm=at(LOWER_RETURN),
        auxiliary_mm=at(AUXILIARY_BAND),
        ground_mm=at(GROUND_LINE),
        callout_mm=at(CALLOUT_BAND),
    )


def standing_of(height_mm: float, functions: frozenset[str], is_inline: bool) -> Standing:
    """Dove va posato un componente, dalla sua taglia e dalle sue funzioni."""
    if functions & AUXILIARY_FUNCTIONS:
        return Standing.AUXILIARY
    if is_inline:
        return Standing.RAIL
    if height_mm >= GROUND_HEIGHT_MM:
        return Standing.GROUND
    return Standing.RAIL
