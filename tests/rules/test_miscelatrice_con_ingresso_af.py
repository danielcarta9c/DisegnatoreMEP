"""La miscelatrice termostatica ha l'ingresso dell'acqua fredda (**D-175**).

Il PO, il 23 settembre 2026, guardando le tavole approvate:

    «Si la miscelatrice termostatica ha necessita' di ingresso Af e quindi la
    libreria va aggiornata e anche la regola di disegno (serve il pezzetto di af
    in ingresso). Anche lei e' una di quelle valvole che deve poter ruotare e
    specchiare per evitare sormonti o curve non necessarie.»

Fino a quel giorno la voce aveva due attacchi, tutt'e due sull'acqua calda: il
simbolo disegnava la terza via, ma la terza via non arrivava a niente. L'avevano
scritto due agenti in camera pulita come domanda per il progettista, sugli
impianti 1, 2, 3 e 5.

Tre cose si provano qui, e sono le tre parti della disposizione:

1. **la libreria**: tre attacchi, l'acqua fredda sul terzo, e non piu' un organo
   in linea — il simbolo non dichiara piu' l'interruzione di linea;
2. **la regola**: la miscelatrice sta ancora *dentro* la tubazione dell'acqua
   calda, e in piu' riceve l'acqua fredda dal **proprio** confine di rete, con
   la propria rete, come il gruppo di riempimento (I-061) — non da una
   derivazione sulla linea dell'acquedotto;
3. **il piano la gira**: la rotazione di una tre vie non si deduce (C2), e la
   miscelatrice ha tre vicini.
"""
# categoria: difende il contenuto — D-175, la miscelatrice termostatica con il proprio ingresso di acqua fredda

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PortFlow
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

MISCELATRICE = "mixing-valve-thermostatic"
COLD = "cold_water"
DHW = "domestic_hot_water"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def completato(nome: str) -> ProjectModel:
    regole = RuleRegistry.from_directory(RULES)
    regole.cross_check(catalog())
    completo, _, _ = saturate(load_project(PROVA / nome), catalog(), regole)
    return completo


def _vicini(model: ProjectModel, component_id: str) -> dict[str, tuple[str, str, str]]:
    """Per ogni attacco del pezzo: chi sta all'altro capo, con quale attacco, e la rete."""
    found: dict[str, tuple[str, str, str]] = {}
    for connection in model.connections:
        for mio, suo in (
            (connection.endpoint_a, connection.endpoint_b),
            (connection.endpoint_b, connection.endpoint_a),
        ):
            if mio.component_id == component_id:
                found[mio.port_id] = (suo.component_id, suo.port_id, connection.network_id)
    return found


def test_la_miscelatrice_ha_tre_attacchi_e_l_acqua_fredda_sul_terzo() -> None:
    """La libreria: `hot_in` e `out` sull'acqua calda, `cold_in` sulla fredda.

    E il simbolo porta la terza via **in basso**, dove il corpo la disegnava
    gia': la gamba arriva adesso fino al bordo, sulla porta."""
    risolto = catalog().resolve(MISCELATRICE)
    porte = {port.id: port for port in risolto.definition.ports}
    assert set(porte) == {"hot_in", "cold_in", "out"}
    assert (porte["hot_in"].medium, porte["hot_in"].flow) == (DHW, PortFlow.IN)
    assert (porte["out"].medium, porte["out"].flow) == (DHW, PortFlow.OUT)
    assert (porte["cold_in"].medium, porte["cold_in"].flow) == (COLD, PortFlow.IN)

    manifesto = risolto.symbol.manifest
    facce = {port.id: port.face for port in manifesto.ports}
    assert facce == {
        "hot_in": PortFace.LEFT,
        "out": PortFace.RIGHT,
        "cold_in": PortFace.BOTTOM,
    }
    assert manifesto.version == "2.0.0"


def test_la_miscelatrice_non_e_piu_un_organo_in_linea() -> None:
    """Il motore non la posa piu' da solo sulla tratta: la posa il piano.

    E' la conseguenza del terzo attacco, e non una scelta a parte: un organo in
    linea ha due porte opposte e interrompe la linea che lo attraversa; con tre
    porte il pezzo e' una tre vie, e la sua giacitura e' di chi compone."""
    risolto = catalog().resolve(MISCELATRICE)
    assert not risolto.is_inline
    assert risolto.symbol.manifest.inline_gap_mm is None


def test_la_regola_le_porta_il_pezzetto_di_acqua_fredda_in_ingresso() -> None:
    """Sull'impianto 2 — «sull'uscita sanitaria e' prevista una valvola
    miscelatrice» — la miscelatrice sta sulla linea dal bollitore alle utenze, e
    l'acqua fredda le arriva dal proprio confine, su una rete sua.

    Il confine **non e' l'acquedotto** che il progettista ha dichiarato, e la sua
    rete non tocca nessun altro utente: e' la regola di I-061, «si fanno piu'
    ingressi», che adesso vale anche per lei."""
    model = completato("prova-2-pdc-deviatrice-acs.json")
    definizioni = {item.id: item.definition_id for item in model.components}
    sigle = {item.id: item.tag for item in model.components}
    miscelatrici = [item for item, definition in definizioni.items() if definition == MISCELATRICE]
    assert len(miscelatrici) == 1, miscelatrici
    miscelatrice = miscelatrici[0]

    vicini = _vicini(model, miscelatrice)
    assert set(vicini) == {"hot_in", "cold_in", "out"}, vicini
    reti = {item.id: item.medium for item in model.networks}
    assert reti[vicini["hot_in"][2]] == DHW
    assert reti[vicini["out"][2]] == DHW
    assert vicini["hot_in"][2] == vicini["out"][2], "la linea calda e' una sola"

    rete_fredda = vicini["cold_in"][2]
    assert reti[rete_fredda] == COLD
    capi = {
        ref.component_id
        for connection in model.connections
        if connection.network_id == rete_fredda
        for ref in (connection.endpoint_a, connection.endpoint_b)
    }
    confini = [item for item in capi if "boundary" in catalog().get(definizioni[item]).functions]
    assert len(confini) == 1, sorted(capi)
    assert confini[0] != "acquedotto", (
        "la miscelatrice pesca dall'ingresso dichiarato dal progettista invece di "
        "portare il proprio"
    )
    assert sigle[confini[0]] not in (None, sigle["acquedotto"]), sigle[confini[0]]
    # Il tratto e' corto: fra il confine e la miscelatrice c'e' solo il corredo
    # del confine — nessun altro utente, nessuna derivazione.
    utenti = {
        item
        for item in capi
        if item not in confini
        and not catalog().resolve(definizioni[item]).is_inline
    }
    assert utenti == {miscelatrice}, sorted(utenti)


def test_ogni_miscelatrice_dei_cinque_impianti_ha_la_terza_via_collegata() -> None:
    """Nessuna miscelatrice termostatica resta con la terza via nel vuoto.

    Sui cinque impianti di prova la regola la mette dove c'e' una riserva di
    acqua calda sanitaria — 1, 2, 3 e 5 — e ogni volta con il proprio confine;
    il 4 fa l'acqua calda istantanea e non ne ha."""
    trovate: dict[str, int] = {}
    for path in sorted(PROVA.glob("prova-*.json")):
        model = completato(path.name)
        definizioni = {item.id: item.definition_id for item in model.components}
        for item, definition in definizioni.items():
            if definition != MISCELATRICE:
                continue
            vicini = _vicini(model, item)
            assert set(vicini) == {"hot_in", "cold_in", "out"}, (path.name, vicini)
            altro = vicini["cold_in"][0]
            catena = [altro]
            # Dalla terza via si risale fino al confine, attraverso il solo
            # corredo in linea del confine.
            while "boundary" not in catalog().get(definizioni[catena[-1]]).functions:
                avanti = [
                    suo
                    for suo, _, _ in _vicini(model, catena[-1]).values()
                    if suo not in (item, *catena)
                ]
                assert len(avanti) == 1, (path.name, catena, avanti)
                catena.append(avanti[0])
            trovate[path.stem] = trovate.get(path.stem, 0) + 1
    assert sorted(trovate) == [
        "prova-1-due-pdc-accumulo-combinato",
        "prova-2-pdc-deviatrice-acs",
        "prova-3-pdc-diretta-pavimento",
        "prova-5-cascata-tre-pdc",
    ], trovate
    assert set(trovate.values()) == {1}, trovate
