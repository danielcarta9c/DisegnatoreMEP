"""Il **piano di composizione**: il formato dichiarato e il suo esecutore.

Da **D-151** il disegno non lo trova un solutore che minimizza una somma
pesata: lo **compone** chi sa come si fa un disegno, e il motore deterministico
esegue quel piano e lo misura (`docs/ARCHITETTURA-DEL-PIANO.md` §1).

Il piano dice **soltanto dove stanno i pezzi**. Quello che si deduce non ci sta
dentro (§4, e C2/C3 di `docs/regole-del-piano.md`): la rotazione di un raccordo,
quella di un pezzo con un attacco solo, la mappa degli attacchi.

Questo pacchetto porta in `src/` quello che era `scripts/piano.py`, cioe' il
pezzo che il 19 e il 20 settembre ha prodotto le due tavole della prova
(`docs/collaudi/PROVA-PIANO/`). Non e' una riscrittura: la logica e le note
misurate nei suoi commenti sono la memoria del progetto e sono qui.

- `formato` — i modelli del piano e il suo caricatore parlante;
- `esecutore` — la deduzione della rotazione e il giro del motore.
"""

from .esecutore import EsitoDelPiano, esegui_piano, orienta
from .formato import (
    FORMATI_ORDINARI,
    ErroreDelPiano,
    PezzoNelPiano,
    PianoDiComposizione,
    carica_piano,
)

__all__ = [
    "FORMATI_ORDINARI",
    "ErroreDelPiano",
    "EsitoDelPiano",
    "PezzoNelPiano",
    "PianoDiComposizione",
    "carica_piano",
    "esegui_piano",
    "orienta",
]
