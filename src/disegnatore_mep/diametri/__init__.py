"""I diametri delle tubazioni (REL-007, D-191, D-193).

Tre pezzi, e ciascuno fa una cosa:

- `calcolatore` — dalla portata il DN, dalla potenza e dal salto termico la
  portata: funzioni pure, sulle basi che il PO ha fissato (D-193);
- `tubi` — il tubo commerciale da comprare, nel suo materiale, con le tabelle e le
  fonti in `tubi.json` (I-279): «MS 32×3», «DN 25 (1")», «Cu 28×1»;
- `portate` — la portata di ogni tratta, dai soli dati del progettista e per
  conservazione nei nodi;
- `tratti` — il tratto che porta un'etichetta sola: attraversa valvole, valvole
  a tre vie e raccordi di servizio, e si ferma dove la portata cambia.

Chi posa l'etichetta sulla tavola e' `layout.diametri`. Accanto, `perdite` verifica
le perdite del giro primario contro la prevalenza utile della pompa a bordo, quando il
progettista la da' con le lunghezze (I-270): un avviso, non un DN diverso.
"""

from .calcolatore import (
    Diametro,
    diametro_per,
    portata_da_potenza,
    velocita_m_s,
)
from .portate import Portate, portate_delle_tratte
from .tratti import TrattoDelDiametro, tratti_da_etichettare, tratti_del_diametro
from .tubi import Tubo, TuboScelto, tubo_dal_testo, tubo_per

__all__ = [
    "Diametro",
    "Portate",
    "TrattoDelDiametro",
    "Tubo",
    "TuboScelto",
    "diametro_per",
    "portata_da_potenza",
    "portate_delle_tratte",
    "tratti_da_etichettare",
    "tratti_del_diametro",
    "tubo_dal_testo",
    "tubo_per",
    "velocita_m_s",
]
