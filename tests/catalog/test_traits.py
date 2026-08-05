"""Il vocabolario delle proprieta' dichiarate (P1).

Quattro cose vanno presidiate qui, e nessuna e' un numero:

1. **Nessuna proprieta' e' il nome di un componente travestito.** E' la prova
   che regge D-069 e D-090 dal lato del catalogo. Non basta rifiutare la
   coincidenza letterale con un identificativo — `expansion_vessel` non e'
   `expansion-connection` e passerebbe: il confronto e' **parola per parola**,
   nelle due direzioni, contro gli identificativi **e** i nomi italiani.
2. **Ogni componente dichiara come si chiude.** Nessun valore sottinteso: un
   regime non scritto sarebbe una scelta presa dal programma al posto di chi
   compila il catalogo (D-094).
3. **Una proprieta' sbagliata non sparisce in silenzio.** Il vocabolario e'
   chiuso: il catalogo non si carica, e l'errore nomina il valore rifiutato.
4. **Il debito degli accessori su stacco resta visibile.** Chi dichiara di
   pendere dal tubo ha ancora due porte passanti, cioe' e' disegnato in linea:
   e' il debito che D-094 apre e che P4 deve chiudere.
"""

import json
import re
from pathlib import Path

import pytest

from disegnatore_mep.catalog.errors import CatalogError
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    ATTACHMENT_STYLES,
    SHUTOFF_REGIMES,
    ComponentDefinition,
    ComponentTrait,
)
from disegnatore_mep.model.types import Domain, PortFlow

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED = ROOT / "examples" / "layout" / "catalog"
FOUNDATION = ROOT / "examples" / "foundation" / "catalog"
CATALOGUES = (PUBLISHED, FOUNDATION)
PM_DOCUMENT = ROOT / "docs" / "prodotto" / "PROPRIETA_COMPONENTI.md"


def definitions(directory: Path) -> tuple[ComponentDefinition, ...]:
    return ComponentRegistry.from_directory(directory).all()


def every_definition() -> tuple[ComponentDefinition, ...]:
    return tuple(item for directory in CATALOGUES for item in definitions(directory))


def payload(directory: Path, stem: str) -> dict[str, object]:
    loaded: dict[str, object] = json.loads((directory / f"{stem}.json").read_text("utf-8"))
    return loaded


def loading(tmp_path: Path, altered: dict[str, object]) -> None:
    (tmp_path / "probe.json").write_text(json.dumps(altered), encoding="utf-8")
    ComponentRegistry.from_directory(tmp_path)


def probe(**changes: object) -> dict[str, object]:
    """Una voce di catalogo vera, con le sole proprieta' cambiate."""
    return {**payload(PUBLISHED, "strainer"), **changes}


# --- 1. nessuna proprieta' e' un componente travestito -------------------------

# Particelle e sigle: non identificano un componente, e pretendere che una
# proprieta' non le usi vieterebbe l'inglese e l'italiano correnti.
ENGLISH_PARTICLES = frozenset({"a", "an", "the", "of", "on", "in", "to", "for", "and", "or"})
ITALIAN_PARTICLES = frozenset({"di", "da", "del", "della", "dei", "delle", "con", "per", "d"})
ARTICLES = frozenset({"e", "il", "la", "lo", "le", "i", "gli", "un", "uno", "una", "y"})
ABBREVIATIONS = frozenset({"acs", "dhw", "vrv", "off", "up"})
PARTICLES = ENGLISH_PARTICLES | ITALIAN_PARTICLES | ARTICLES | ABBREVIATIONS
"""Le parole che il confronto ignora, ed e' l'unica indulgenza che si concede."""

ROOT_LENGTH = 4
"""Sotto le quattro lettere una radice condivisa non significa niente."""


def words(text: str) -> frozenset[str]:
    """Le parole significative di un identificativo o di un nome italiano."""
    found = re.split(r"[^0-9a-zà-ÿ]+", text.lower())
    return frozenset(item for item in found if item and item not in PARTICLES)


def catalogue_words() -> frozenset[str]:
    found: set[str] = set()
    for definition in every_definition():
        found |= words(definition.id)
        found |= words(definition.name)
        found |= words(definition.symbol_id)
    return frozenset(found)


def shares_a_root(first: str, second: str) -> bool:
    """Una parola comincia o finisce con l'altra: `drainable` e `drain`.

    Non e' la stessa parola, ma e' la stessa cosa detta al participio, ed e'
    esattamente il modo in cui il nome di un componente rientrerebbe."""
    long, short = (first, second) if len(first) >= len(second) else (second, first)
    if len(short) < ROOT_LENGTH or long == short:
        return False
    return long.startswith(short) or long.endswith(short)


def collides(word: str, catalogued: frozenset[str]) -> bool:
    return any(word == other or shares_a_root(word, other) for other in catalogued)


def test_no_trait_shares_a_word_with_a_component() -> None:
    """La guardia, nelle due direzioni.

    Fallisce sia se una proprieta' usa una parola con cui si chiama un
    componente (`safety_device`, `is_a_buffer_tank`), sia se quella parola
    compare nella proprieta' come radice (`expansion_vessel`)."""
    catalogued = catalogue_words()
    assert catalogued, "senza voci di catalogo la prova non dimostrerebbe nulla"
    guilty = sorted(
        (trait.value, mine, theirs)
        for trait in ComponentTrait
        for mine in words(trait.value)
        for theirs in catalogued
        if mine == theirs or shares_a_root(mine, theirs)
    )
    assert not guilty, guilty


def test_the_guard_catches_a_property_that_is_a_component_in_disguise() -> None:
    """La prova della prova, sui travestimenti che il collaudo ha citato.

    Senza, la guardia potrebbe non catturare piu' niente e nessuno se ne
    accorgerebbe: passerebbe perche' non trova nulla, non perche' non c'e'."""
    catalogued = catalogue_words()
    for disguised in ("expansion_vessel", "is_a_buffer_tank", "safety_device", "drainable"):
        assert any(collides(word, catalogued) for word in words(disguised)), disguised


def test_every_trait_is_a_lowercase_word_and_not_a_sentence() -> None:
    for trait in ComponentTrait:
        assert trait.value == trait.name.lower()
        assert trait.value.replace("_", "").isalpha()


# --- 2. ogni componente dichiara i due regimi obbligatori ----------------------


@pytest.mark.parametrize("directory", CATALOGUES, ids=lambda item: item.parent.name)
def test_every_component_declares_how_it_is_shut_off(directory: Path) -> None:
    loaded = definitions(directory)
    assert loaded
    for definition in loaded:
        assert definition.shutoff_regime in SHUTOFF_REGIMES, definition.id
        assert len(definition.trait_set & SHUTOFF_REGIMES) == 1, definition.id


@pytest.mark.parametrize("directory", CATALOGUES, ids=lambda item: item.parent.name)
def test_every_component_declares_how_it_attaches(directory: Path) -> None:
    for definition in definitions(directory):
        assert definition.attachment in ATTACHMENT_STYLES, definition.id
        assert len(definition.trait_set & ATTACHMENT_STYLES) == 1, definition.id


def test_the_vocabulary_has_no_dead_entry() -> None:
    """Una proprieta' che nessuno dichiara non serve a nessuna regola.

    E' il freno all'inflazione del vocabolario: si aggiunge una proprieta'
    quando un componente ha davvero quel fatto da dichiarare, non prima."""
    declared = {trait for item in every_definition() for trait in item.trait_set}
    assert set(ComponentTrait) - declared == set()


def test_what_is_serviced_can_always_be_shut_off() -> None:
    """La proprieta' che rende dicibile la regola dell'intercettazione.

    Cio' che si smonta in esercizio va chiuso; quindi non puo' insieme
    dichiarare di non chiudersi mai. Vale su tutti i cataloghi, senza nominare
    un componente."""
    for definition in every_definition():
        if definition.has_trait(ComponentTrait.MAINTAINABLE):
            assert definition.shutoff_regime is not ComponentTrait.SHUTOFF_NEVER


def test_nothing_outside_the_water_declares_itself_serviceable() -> None:
    """«Si manutiene» vuol dire «lo si smonta chiudendo il fluido attorno».

    Un canale d'aria e una linea frigorifera non si chiudono con una valvola:
    se un componente di quei domini si dichiarasse manutenibile, la regola
    dell'intercettazione andrebbe a mettere valvole su un canale."""
    for definition in every_definition():
        if definition.has_trait(ComponentTrait.MAINTAINABLE):
            domains = {port.domain for port in definition.ports}
            assert Domain.HYDRONIC in domains, (definition.id, sorted(domains))


# --- 3. il vocabolario e' chiuso, e l'errore nomina cio' che rifiuta -----------


def test_an_unknown_trait_stops_the_catalogue_and_names_it(tmp_path: Path) -> None:
    with pytest.raises(CatalogError) as raised:
        loading(tmp_path, probe(traits=["manutenibile", "shutoff_ordinary", "attachment_inline"]))
    assert "manutenibile" in str(raised.value)


def test_a_component_without_traits_does_not_load(tmp_path: Path) -> None:
    without = {key: value for key, value in probe().items() if key != "traits"}
    with pytest.raises(CatalogError, match="traits"):
        loading(tmp_path, without)


def test_a_component_that_declares_no_shutoff_regime_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="non dichiara il regime di intercettazione") as raised:
        loading(tmp_path, probe(traits=["maintainable", "attachment_inline"]))
    message = str(raised.value)
    assert "strainer" in message
    for regime in SHUTOFF_REGIMES:
        assert regime.value in message


def test_a_component_that_declares_two_shutoff_regimes_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="più di una scelta per il regime"):
        loading(
            tmp_path,
            probe(traits=["shutoff_ordinary", "shutoff_never", "attachment_inline"]),
        )


def test_a_component_that_declares_no_attachment_style_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="non dichiara come si attacca"):
        loading(tmp_path, probe(traits=["maintainable", "shutoff_ordinary"]))


def test_a_component_that_declares_two_attachment_styles_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="più di una scelta per come si attacca"):
        loading(
            tmp_path,
            probe(traits=["shutoff_ordinary", "attachment_inline", "attachment_branch"]),
        )


def test_a_trait_declared_twice_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="due volte la stessa proprietà"):
        loading(
            tmp_path,
            probe(traits=["maintainable", "maintainable", "shutoff_ordinary", "attachment_inline"]),
        )


def test_being_serviced_and_never_closing_do_not_load_together(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="la prima chiede le valvole che la seconda vieta"):
        loading(tmp_path, probe(traits=["maintainable", "shutoff_never", "attachment_branch"]))


# --- 4. il debito aperto da D-094, tenuto in vista ----------------------------

DRAWN_IN_LINE_THOUGH_DECLARED_ON_A_BRANCH = frozenset(
    {
        "drain-connection",
        "expansion-connection",
        "expansion-connection-dhw",
        "filling-unit",
        "pressure-gauge",
        "thermometer",
        "valve-safety",
        "valve-safety-dhw",
    }
)
"""Chi dichiara di pendere dal tubo ma ha ancora due porte passanti.

E' il debito che **D-094** apre e che P4 deve chiudere: finche' un accessorio su
stacco ha una porta di ingresso e una di uscita, il disegno lo spezza sulla
tratta come se il fluido ci passasse attraverso, e la derivazione resta nascosta
nel corpo del simbolo — la scorciatoia che D-094 ritira."""


def looks_like_a_run_through(definition: ComponentDefinition) -> bool:
    flows = {port.flow for port in definition.ports}
    return len(definition.ports) == 2 and PortFlow.IN in flows and PortFlow.OUT in flows


def test_the_branch_accessories_still_drawn_in_line_are_the_known_ones() -> None:
    """Il debito e' congelato: cambiarlo obbliga a passare da qui.

    Se questa prova fallisce, **D-094** e' in gioco. Un componente **uscito**
    dall'elenco e' il debito che si chiude: va tolto anche da qui e dalla riga
    di `docs/DEFERRED.md`. Un componente **entrato** e' un accessorio su stacco
    nuovo disegnato ancora in linea: non si aggiunge all'elenco per far passare
    la prova, si guarda perche' e' nato cosi'."""
    found = {
        definition.id
        for definition in every_definition()
        if definition.attachment is ComponentTrait.ATTACHMENT_BRANCH
        and looks_like_a_run_through(definition)
    }
    assert found == DRAWN_IN_LINE_THOUGH_DECLARED_ON_A_BRANCH, {
        "usciti dal debito, D-094 chiuso per loro": sorted(
            DRAWN_IN_LINE_THOUGH_DECLARED_ON_A_BRANCH - found
        ),
        "entrati nel debito, D-094 violato di nuovo": sorted(
            found - DRAWN_IN_LINE_THOUGH_DECLARED_ON_A_BRANCH
        ),
    }


# --- 5. l'artefatto che il committente approva --------------------------------


def first_table_rows(text: str) -> list[str]:
    """Le righe della prima tabella del documento, intestazione esclusa."""
    rows: list[str] = []
    started = False
    for line in text.splitlines():
        if line.startswith("|"):
            started = True
            rows.append(line)
        elif started:
            break
    return rows[2:]


def test_the_document_for_the_pm_defines_every_property() -> None:
    """Una riga per proprieta', in italiano: e' cio' che il committente approva.

    La prova conta le righe invece di cercare i nomi tecnici apposta: quel
    documento non deve contenerne nessuno."""
    assert PM_DOCUMENT.is_file()
    rows = first_table_rows(PM_DOCUMENT.read_text("utf-8"))
    assert len(rows) == len(ComponentTrait), [row.split("|")[1] for row in rows]
    for row in rows:
        assert row.count("|") >= 4, row
