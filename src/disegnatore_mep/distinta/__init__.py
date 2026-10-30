"""La distinta materiali per l'installatore (REL-013, **proposta** D-213).

Dal grafo completo alla distinta: le quantita' per voce, ciascuna con la regola che
l'ha prodotta; le sezioni del kit AA-01 (A apparecchiature, B aria, C frigorifero,
D condensa, E elettrico, F assistenze murarie, Z opere del committente, G attivita' a
corpo, H voci dell'installatore, V varianti; X quello che non ha regola); le
lunghezze dai dati del progettista con la maggiorazione; la verifica dell'aria, che
segnala e non corregge.

**Spenta di default**, come i diametri (D-191): la fa solo `mep.py distinta`, quando
il progettista la chiede. Le regole sono dati, in `rules/distinta/`, ogni voce con
`fonte` e `perche`. Dove manca un dato: DA DEFINIRE e una domanda, mai un numero
inventato.

- `regole` — carica e controlla le regole;
- `grafo` — legge il grafo dal JSON, tollerante, e ne fa i tratti;
- `lunghezze`, `confezioni` — la maggiorazione, i pezzi interi nelle confezioni;
- `calcolo` — compone la distinta;
- `uscite` — JSON, tabelle per il foglio, foglio dei calcoli;
- `documento` — il documento per l'installatore: copertina e capitoli, come dati (I-232);
- `impaginazione` — il documento in PDF col motore dei report Nove C, o in Markdown;
- `comando` — il comando della skill.
"""

from .calcolo import DA_DEFINIRE, Distinta, EsitoDellaVerifica, Voce, componi_la_distinta
from .regole import ErroreDelleRegole, RegoleDellaDistinta, carica_regole
from .uscite import distinta_in_json, scrivi_le_uscite, tabelle_del_foglio

__all__ = [
    "DA_DEFINIRE",
    "Distinta",
    "ErroreDelleRegole",
    "EsitoDellaVerifica",
    "RegoleDellaDistinta",
    "Voce",
    "carica_regole",
    "componi_la_distinta",
    "distinta_in_json",
    "scrivi_le_uscite",
    "tabelle_del_foglio",
]
