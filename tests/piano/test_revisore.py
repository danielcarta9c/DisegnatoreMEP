"""Il revisore: l'anello si chiude, e non peggiora in silenzio (**D-153**).

# categoria: difende una regola del piano — D-153, una regola e' un controllo che sa nominare la propria violazione

Quello che si difende qui sono i **criteri 1, 2 e 3** di `DRAW-015`:

1. il revisore gira su un impianto vero e ne esce **un piano corretto**;
2. **ogni correzione porta il nome della regola** che la motiva — una
   correzione senza regola sarebbe il solutore travestito;
3. **non peggiora in silenzio**: se un giro peggiora l'ordine, si ferma, nomina
   le misure peggiorate e consegna il giro precedente.

Il banco e' l'impianto 4 composto (`docs/collaudi/PROVA-PIANO/impianto-4.json`)
— l'ibrido pompa di calore + caldaia, il piu' largo dei cinque, quindi quello
in cui un pezzo si puo' spostare senza che il piano smetta di instradarsi. Si
guasta apposta: **il radiatore dentro la fascia dello scambiatore** e' una
violazione di **A1** che il revisore sa curare, ed e' il modo di misurare che
l'anello **gira**, non solo che si ferma.
"""

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.formato import PezzoNelPiano, PianoDiComposizione, carica_piano
from disegnatore_mep.piano.revisore import (
    CODICI_DELLE_REGOLE,
    CURE,
    REGOLA_DEL_RILIEVO,
    Punteggio,
    Revisione,
    revisiona,
)
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.regole import ORDINE_DELLE_REGOLE

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "examples" / "prova"
PIANI = ROOT / "docs" / "collaudi" / "PROVA-PIANO"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"

IMPIANTO = "prova-4-ibrido-pdc-caldaia.json"
PIANO = "impianto-4.json"


@cache
def _simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def _catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=_simboli())


@cache
def _modello() -> ProjectModel:
    """Il progetto completo **in forma canonica**: la catena di `rules --apply-all`.

    Il perche' del passaggio canonico sta in `test_esecutore.py`: la posa di
    partenza legge l'ordine del file, e i piani agli atti sono stati composti
    contro quello che `rules --apply-all --out` scrive.
    """
    regole = RuleRegistry.from_directory(RULES)
    regole.cross_check(_catalogo())
    completo, _, _ = saturate(load_project(PROVA / IMPIANTO), _catalogo(), regole)
    return ProjectModel.model_validate_json(canonical_json(completo))


def _revisiona(piano: PianoDiComposizione, tetto: int = 3) -> Revisione:
    return revisiona(_modello(), piano, _catalogo(), _simboli(), NAMING, tetto=tetto)


@cache
def _sul_piano_agli_atti() -> Revisione:
    return _revisiona(carica_piano(PIANI / PIANO))


def _guastato() -> PianoDiComposizione:
    """Il piano agli atti con **il radiatore dentro la fascia dello scambiatore**.

    `radiatori` e' un terminale, quindi **distribuzione**, e nel piano sta a
    x=420, oltre lo scambiatore (x=300..312,5). Portandolo a x=310 le due fasce
    si accavallano in orizzontale: e' una violazione di **A1** netta, su un
    pezzo che ha davvero una fascia propria, e il piano continua a instradarsi
    — cosa che a x=305 non fa piu' (misurato: «la tratta s1-a non ha un
    rettilineo di 12,5 mm per il circolatore»).

    Non si usa `utenze` per guastare, e il perche' e' una misura: un **confine
    di rete** non ha una posizione propria — «va accanto all'utente che serve»
    (`flow.BOUNDARY_FUNCTION`, I-061) — e per questo `fascia_del_pezzo` non lo
    classifica. Un pezzo che non sceglie dove stare non puo' violare una fascia.
    """
    piano = carica_piano(PIANI / PIANO)
    pezzi = dict(piano.pezzi)
    vecchio = pezzi["radiatori"]
    pezzi["radiatori"] = PezzoNelPiano(x=310.0, y=vecchio.y)
    return piano.model_copy(update={"pezzi": pezzi})


# --- l'anello gira ------------------------------------------------------------


def test_l_anello_gira_e_consegna_un_piano_corretto() -> None:
    """Criterio 1: entra un piano, escono i giri e **un piano corretto**."""
    esito = _revisiona(_guastato())
    assert len(esito.giri) >= 2, "un giro solo non e' un anello"
    assert esito.piano_finale.pezzi, "il piano corretto non puo' essere vuoto"
    assert esito.giro_migliore.esito.disegno is not None


def test_il_revisore_chiude_la_violazione_che_sa_curare() -> None:
    """Il piano guastato viola A1, e dopo la cura quella violazione non c'e' piu'."""
    esito = _revisiona(_guastato())
    prima = [
        item
        for item in esito.giri[0].rilievi
        if item.code == "PIECE_OUTSIDE_ITS_BAND"
    ]
    assert prima, "il guasto doveva produrre una violazione di A1"
    dopo = [
        item
        for item in esito.giro_migliore.rilievi
        if item.code == "PIECE_OUTSIDE_ITS_BAND"
    ]
    assert len(dopo) < len(prima), (
        f"A1 non e' migliorata: {len(prima)} -> {len(dopo)}. "
        f"Si e' fermato perche': {esito.perche_si_e_fermato}"
    )


def test_il_pezzo_spostato_e_quello_a_valle() -> None:
    """La cura di A1 sposta il pezzo della fascia **a valle**, non quello a monte.

    L'ordine del processo si legge da sinistra a destra (D-060): fra due fasce
    che si accavallano, quella nel posto sbagliato e' la piu' a valle. Curare
    l'altra allontanerebbe i due pezzi l'uno dall'altro e allargherebbe il
    disegno da solo — ed e' misurato: curando il pezzo a monte, sull'impianto 1
    il piano non si instradava piu'.
    """
    esito = _revisiona(_guastato())
    correzioni = [
        correzione
        for giro in esito.giri
        for correzione in giro.correzioni
        if correzione.regola == "A1"
    ]
    assert correzioni, "nessuna correzione di A1"
    assert all(item.pezzo == "radiatori" for item in correzioni), [
        item.pezzo for item in correzioni
    ]
    assert all(item.a[0] > item.da[0] for item in correzioni), "A1 sposta a destra"


# --- ogni correzione porta la propria regola (criterio 2) ---------------------


@pytest.mark.parametrize("guasto", [True, False], ids=["piano-guastato", "piano-agli-atti"])
def test_ogni_correzione_porta_il_nome_della_regola(guasto: bool) -> None:
    """Criterio 2, ed e' quello che separa il revisore dal solutore."""
    esito = _revisiona(_guastato()) if guasto else _sul_piano_agli_atti()
    correzioni = [
        correzione for giro in esito.giri for correzione in giro.correzioni
    ]
    for correzione in correzioni:
        assert correzione.regola, correzione
        assert correzione.regola in set(REGOLA_DEL_RILIEVO.values()), correzione.regola
        assert correzione.rilievo, correzione
        assert correzione.perche, "una correzione dice anche il rilievo che l'ha voluta"
        assert correzione.da != correzione.a, "una correzione che non sposta non si scrive"


def test_ogni_cura_conosciuta_ha_la_propria_regola() -> None:
    """Non si puo' aggiungere una cura senza dire quale regola la motiva."""
    assert set(CURE) <= set(REGOLA_DEL_RILIEVO)


# --- non peggiora in silenzio (criterio 3) ------------------------------------


def test_si_ferma_sempre_dicendo_perche() -> None:
    """Il criterio non ammette un arresto muto: in tutti i casi si dice perche'."""
    for esito in (_sul_piano_agli_atti(), _revisiona(_guastato())):
        assert esito.perche_si_e_fermato.strip()


def test_consegna_il_giro_migliore_e_mai_uno_peggiore() -> None:
    """Criterio 3: il giro consegnato non e' peggiore di nessuno dei precedenti."""
    for esito in (_sul_piano_agli_atti(), _revisiona(_guastato())):
        consegnato = esito.giro_migliore.punteggio.ordine
        for giro in esito.giri:
            assert consegnato <= giro.punteggio.ordine or giro.numero > esito.migliore


def test_un_giro_che_peggiora_nomina_le_misure_peggiorate() -> None:
    """Se un giro peggiora, il motivo dell'arresto **le nomina una per una**."""
    esito = _sul_piano_agli_atti()
    # Non e' un `skip`: se questo giro non peggiora, non c'e' niente da nominare
    # e la prova e' vera a vuoto. Cio' che si difende e' l'implicazione — **se**
    # peggiora, **allora** lo dice — e l'altra meta' (l'arresto parla sempre) la
    # difende `test_si_ferma_sempre_dicendo_perche`.
    if "peggiorat" in esito.perche_si_e_fermato:
        prima = esito.giri[esito.migliore].punteggio
        poi = esito.giri[-1].punteggio
        for voce in poi.peggiorate(prima):
            assert voce in esito.perche_si_e_fermato, voce


def test_il_punteggio_e_lessicografico_e_non_una_somma() -> None:
    """Una tratta ceduta non si compra con dieci pieghe in meno.

    E' la forma della domanda che ha ucciso il solutore (**D-151**): una somma
    pesata si compra sempre, un ordine lessicografico no.
    """
    ceduta = Punteggio(0, 1, 0, 0, 0, 0)
    piegata = Punteggio(0, 0, 0, 0, 50, 50)
    assert piegata.ordine < ceduta.ordine


def test_una_violazione_si_conta_una_volta_sola() -> None:
    """`RUN_WITH_TOO_MANY_BENDS` non e' una violazione: su un'autostrada dice la
    stessa cosa di `HIGHWAY_IS_NOT_STRAIGHT`, e contarle tutt'e due gonfierebbe
    il punteggio di una tavola che ha un difetto solo."""
    assert "RUN_WITH_TOO_MANY_BENDS" not in CODICI_DELLE_REGOLE
    assert "HIGHWAY_IS_NOT_STRAIGHT" in CODICI_DELLE_REGOLE
    esito = _sul_piano_agli_atti()
    giro = esito.giri[0]
    regole = sum(1 for item in giro.rilievi if item.code in CODICI_DELLE_REGOLE)
    assert giro.punteggio.violazioni == regole


def test_ogni_regola_misurata_conta_come_violazione() -> None:
    """Una regola nuova in `validation/regole.py` non puo' finire fra gli avvisi.

    **Il difetto vero, misurato il 20 settembre.** `CODICI_DELLE_REGOLE` era una
    lista scritta a mano di quattro codici: **A4** e' entrata in
    `ORDINE_DELLE_REGOLE` e il suo rilievo — un confine di rete a mezzo foglio
    dal pezzo che serve — e' finito fra gli **avvisi**, cioe' l'ultima voce del
    punteggio, comprabile con una piega in meno. Adesso la lista si **ricava**,
    e questa prova sorveglia che resti ricavata.
    """
    attese = {
        "PIECE_OUTSIDE_ITS_BAND",
        "SERVICE_STUB_LONGER_THAN_ITS_MINIMUM",
        "HIGHWAY_IS_NOT_STRAIGHT",
        "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
        "INLINE_ORGAN_BREAKS_THE_RUN",
    }
    assert set(CODICI_DELLE_REGOLE) == attese, "il punteggio conta altre violazioni"
    portate = {REGOLA_DEL_RILIEVO[codice] for codice in CODICI_DELLE_REGOLE}
    assert portate == set(ORDINE_DELLE_REGOLE), "una regola misurata non e' contata"


def test_non_smonta_una_catena_gia_dritta() -> None:
    """La guardia piu' importante: non si rompe cio' che e' a posto.

    Misurato il 20 settembre sull'impianto 1: senza, la cura di B1 sulla tratta
    `radiatori -> accumulo` spostava l'accumulo e piegava **le due primarie**,
    che erano due rette, portando lo squilibrio fra i quadranti da 5,2 a 11,5.
    """
    esito = _sul_piano_agli_atti()
    dritte_prima = {
        item.code for item in esito.giri[0].rilievi if item.code in CODICI_DELLE_REGOLE
    }
    consegnato = {
        item.code
        for item in esito.giro_migliore.rilievi
        if item.code in CODICI_DELLE_REGOLE
    }
    assert consegnato <= dritte_prima, "la revisione ha introdotto una violazione nuova"
