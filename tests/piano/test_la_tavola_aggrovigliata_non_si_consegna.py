"""Una tavola aggrovigliata non si consegna (REL-016, D1 del collaudo della 1.7.0).

Il collaudo indipendente della 1.7.0 ha posato i raccordi del ritorno della villetta
nell'ordine inverso a quello della catena, e il gruppo di riempimento senza girarlo
(`docs/collaudi/REL-016/casi-del-collaudo/villetta-piano-groviglio.json`). A vista il
ritorno verso la pompa di calore sale, torna indietro e scavalca sé stesso due volte, e
il defangatore sta su una piega; `disegna` diceva «rilievi bloccanti 0», perche' lo
vedevano solo le regole del piano, che sono avvisi.

**Le misure**: la linea che scavalca sé stessa (`RUN_CROSSES_ITSELF`, nel preflight) e
l'organo in linea sulla piega (`INLINE_ORGAN_BREAKS_THE_RUN`, B4) fermano la tavola; la
stessa villetta col piano buono (`villetta-piano-buono.json`) non ne prende nessuno. E
`mep.py pezzi` dice in che ordine i raccordi stanno lungo la catena, cosi' chi compone li
posa in quell'ordine. Rosse sul commit di partenza (`5835445`): nessuno dei due rilievi
era bloccante, e `pezzi` non diceva l'ordine.
"""
# categoria: difende il motore

import contextlib
import io
from functools import cache
from pathlib import Path

from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.validation.issues import ValidationIssue
from disegnatore_mep.validation.regole import rilievi_delle_regole

ROOT = Path(__file__).resolve().parents[2]
CASI = ROOT / "docs" / "collaudi" / "REL-016" / "casi-del-collaudo"


@cache
def _grafo_completo() -> Path:
    """Il grafo della villetta, di prima stesura, completato da `completa` come lo fa un
    agente: una volta per tutto il file."""
    from tempfile import mkdtemp

    from disegnatore_mep.skill import cartelle_del_repository, main

    uscita = Path(mkdtemp(prefix="villetta-")) / "grafo-completo.json"
    with contextlib.redirect_stdout(io.StringIO()):
        main(
            ["completa", str(CASI / "villetta-grafo.json"), "--out", str(uscita)],
            cartelle_del_repository(ROOT),
        )
    return uscita


def _disegna(piano: str) -> tuple[EsitoDelPiano, list[ValidationIssue]]:
    """La tavola del piano, coi rilievi del preflight e quelli delle regole."""
    from disegnatore_mep.skill import _Dati, cartelle_del_repository

    cartelle = cartelle_del_repository(ROOT)
    dati = _Dati(cartelle)
    esito = esegui_piano(
        load_project(_grafo_completo()), carica_piano(CASI / piano), dati.catalogo, dati.simboli, cartelle.naming
    )
    assert esito.disegno is not None, esito.errore
    regole = rilievi_delle_regole(esito.disegno, esito.frame, esito.catalogo, esito.modello)
    return esito, regole


def _bloccanti(esito: EsitoDelPiano, regole: list[ValidationIssue]) -> list[ValidationIssue]:
    return [*esito.bloccanti, *(item for item in regole if item.severity is IssueSeverity.BLOCKING)]


def test_la_villetta_aggrovigliata_ha_un_rilievo_bloccante() -> None:
    """Il ritorno si scavalca due volte, e il defangatore sta sulla piega: due bloccanti."""
    esito, regole = _disegna("villetta-piano-groviglio.json")
    bloccanti = _bloccanti(esito, regole)
    codici = {item.code for item in bloccanti}
    assert "RUN_CROSSES_ITSELF" in codici, [item.code for item in bloccanti]
    assert "INLINE_ORGAN_BREAKS_THE_RUN" in codici
    groviglio = next(item for item in bloccanti if item.code == "RUN_CROSSES_ITSELF")
    assert "2 volte" in groviglio.message
    assert "tee-pressure-gauge-pdc-water-return" in groviglio.message
    assert "mep.py pezzi" in groviglio.message


def test_la_villetta_col_piano_buono_non_ha_bloccanti() -> None:
    """Gli stessi pezzi, coi raccordi nell'ordine della catena: la tavola si consegna."""
    esito, regole = _disegna("villetta-piano-buono.json")
    assert _bloccanti(esito, regole) == []


def test_disegna_ferma_la_tavola_aggrovigliata(tmp_path: Path) -> None:
    """Il comando dell'agente dice i bloccanti e non da' la tavola per consegnabile."""
    from disegnatore_mep.skill import cartelle_del_repository, main

    testo = io.StringIO()
    with contextlib.redirect_stdout(testo):
        codice = main(
            [
                "disegna", str(_grafo_completo()), "--piano", str(CASI / "villetta-piano-groviglio.json"),
                "--out", str(tmp_path), "--senza-dxf",
            ],
            cartelle_del_repository(ROOT),
        )
    assert codice == 2
    assert "rilievi bloccanti 2" in testo.getvalue()
    rilievi = next(tmp_path.glob("*-rilievi.md")).read_text(encoding="utf-8")
    bloccanti = rilievi.split("## Bloccanti")[1].split("## Da approvare")[0]
    assert "RUN_CROSSES_ITSELF" in bloccanti and "INLINE_ORGAN_BREAKS_THE_RUN" in bloccanti
    regole = rilievi.split("## Le regole del piano")[1]
    assert "INLINE_ORGAN_BREAKS_THE_RUN" not in regole, "un bloccante si dice una volta sola"


def test_pezzi_dice_l_ordine_dei_raccordi_lungo_la_catena() -> None:
    """Il ritorno della villetta: dalla pompa di calore, gli organi in linea, poi i tre
    raccordi nell'ordine della catena — vaso, riempimento, manometro — e la confluenza."""
    from disegnatore_mep.skill import cartelle_del_repository, main

    testo = io.StringIO()
    with contextlib.redirect_stdout(testo):
        main(["pezzi", str(_grafo_completo()), "--vista", "idraulica"], cartelle_del_repository(ROOT))
    uscita = testo.getvalue()
    assert "In che ordine stanno lungo le tratte" in uscita
    ritorno = next(riga for riga in uscita.splitlines() if "pdc.water_return" in riga)
    fila = [
        "pdc.water_return",
        "dirt-separator-pdc-water-return (in linea)",
        "tee-expansion-connection-pdc-water-return",
        "tee-filling-unit-pdc-water-return-b",
        "tee-pressure-gauge-pdc-water-return",
        "confluenza.b",
    ]
    posti = [ritorno.find(pezzo) for pezzo in fila]
    assert -1 not in posti, ritorno
    assert posti == sorted(posti), ritorno
