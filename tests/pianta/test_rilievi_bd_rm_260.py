"""I rilievi d'uso della 2.0.0 sulla pianta (REL-026, blocco B; I-300).

La sessione che ha usato la 2.0.0 sulla commessa BD.RM.260 ha lavorato su una copia
della skill e ha annotato che cosa ha dovuto cambiare (`docs/input-pm/2026-11-13-
rilievi-bd-rm-260/`). I file della commessa non entrano nel repository: ogni voce si
prova qui su un caso del repository o su un caso anonimo scritto apposta.

- B-1 il nome corto dei fluidi idronici nella tabella delle tratte;
- B-2 `sagome_muri`, il retino dei muri sulle sagome vere;
- B-3 le forature spente di base;
- B-4 le lunghezze dalla pianta al grafo, in un passaggio solo;
- B-5 il confronto con grafo e distinta non cambia il foglio.
"""

from __future__ import annotations

import pytest

from disegnatore_mep.pianta.modello import Fluido
from disegnatore_mep.pianta.scritte import misura
from disegnatore_mep.pianta.tavola import COLONNE_DELLE_TRATTE, CORPO_COLONNA_PT, nome_corto_del_fluido

# --- B-1. il nome corto dei fluidi idronici ---------------------------------------------------


@pytest.mark.parametrize("fluido", Fluido.__args__)  # type: ignore[attr-defined]
def test_il_nome_del_fluido_sta_nella_sua_colonna(fluido: str) -> None:
    """BD.RM.260: «Acqua di riscaldamento» finiva sopra la colonna «Da»."""
    x = {titolo: x for titolo, x, _ in COLONNE_DELLE_TRATTE}
    larghezza = misura(nome_corto_del_fluido(fluido), CORPO_COLONNA_PT, False)[0]
    assert larghezza <= x["Da"] - x["Fluido"] - 1.0, (fluido, nome_corto_del_fluido(fluido), larghezza)


def test_i_nomi_corti_degli_idronici() -> None:
    assert nome_corto_del_fluido("heating_water") == "Acqua risc."
    assert nome_corto_del_fluido("domestic_hot_water") == "ACS"
    assert nome_corto_del_fluido("cold_water") == "AFS"
    assert nome_corto_del_fluido("supply_air") == "Aria di mandata"
