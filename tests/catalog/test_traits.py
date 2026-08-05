"""Il vocabolario delle proprieta' dichiarate (P1).

Tre cose vanno presidiate qui, e nessuna e' un numero:

1. **Nessuna proprieta' e' il nome di un componente travestito.** E' la prova
   che regge D-069 e D-090 dal lato del catalogo: se una proprieta' coincidesse
   con una voce di catalogo, la regola che la legge nominerebbe quel pezzo
   scrivendolo in un altro modo.
2. **Ogni componente dichiara come si isola.** Nessun default implicito: un
   regime non scritto sarebbe una scelta presa dal programma al posto di chi
   compila il catalogo (D-094).
3. **Una proprieta' sbagliata non sparisce in silenzio.** Il vocabolario e'
   chiuso: il catalogo non si carica, e l'errore nomina il valore rifiutato.
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.errors import CatalogError
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    ATTACHMENT_STYLES,
    ISOLATION_REGIMES,
    ComponentDefinition,
    ComponentTrait,
)

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED = ROOT / "examples" / "layout" / "catalog"
FOUNDATION = ROOT / "examples" / "foundation" / "catalog"
CATALOGUES = (PUBLISHED, FOUNDATION)
PM_DOCUMENT = ROOT / "docs" / "prodotto" / "PROPRIETA_COMPONENTI.md"


def definitions(directory: Path) -> tuple[ComponentDefinition, ...]:
    return ComponentRegistry.from_directory(directory).all()


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


def normalised(name: str) -> str:
    """Trattini e trattini bassi sono lo stesso segno, per questa prova.

    Un identificativo di catalogo si scrive `dirt-separator` e una proprieta'
    `fouls_circuit`: senza normalizzare, una proprieta' chiamata
    `drain_connection` passerebbe accanto all'omonima voce di catalogo."""
    return name.replace("-", "_")


def catalogued_names() -> set[str]:
    names: set[str] = set()
    for directory in CATALOGUES:
        for definition in definitions(directory):
            names.add(normalised(definition.id))
            names.add(normalised(definition.symbol_id))
    return names


def test_no_trait_is_a_component_in_disguise() -> None:
    names = catalogued_names()
    assert names, "senza voci di catalogo la prova non dimostrerebbe nulla"
    guilty = sorted(
        (trait.value, name)
        for trait in ComponentTrait
        for name in names
        if name in normalised(trait.value)
    )
    assert not guilty, guilty


def test_every_trait_is_a_lowercase_word_and_not_a_sentence() -> None:
    for trait in ComponentTrait:
        assert trait.value == trait.name.lower()
        assert trait.value.replace("_", "").isalpha()


# --- 2. ogni componente dichiara i due regimi obbligatori ----------------------


@pytest.mark.parametrize("directory", CATALOGUES, ids=lambda item: item.parent.name)
def test_every_component_declares_how_it_is_isolated(directory: Path) -> None:
    loaded = definitions(directory)
    assert loaded
    for definition in loaded:
        assert definition.isolation_regime in ISOLATION_REGIMES, definition.id
        assert len(definition.trait_set & ISOLATION_REGIMES) == 1, definition.id


@pytest.mark.parametrize("directory", CATALOGUES, ids=lambda item: item.parent.name)
def test_every_component_declares_how_it_attaches(directory: Path) -> None:
    for definition in definitions(directory):
        assert definition.attachment in ATTACHMENT_STYLES, definition.id
        assert len(definition.trait_set & ATTACHMENT_STYLES) == 1, definition.id


def test_the_vocabulary_has_no_dead_entry() -> None:
    """Una proprieta' che nessuno dichiara non serve a nessuna regola.

    E' il freno all'inflazione del vocabolario: si aggiunge una proprieta'
    quando un componente ha davvero quel fatto da dichiarare, non prima."""
    declared = {
        trait
        for directory in CATALOGUES
        for definition in definitions(directory)
        for trait in definition.trait_set
    }
    assert set(ComponentTrait) - declared == set()


def test_what_is_serviced_can_always_be_shut_off() -> None:
    """La proprieta' che rende dicibile la regola dell'intercettazione.

    Cio' che si manutiene va isolato; quindi non puo' insieme dichiarare di non
    isolarsi mai. Vale su tutti i cataloghi, senza nominare un componente."""
    for directory in CATALOGUES:
        for definition in definitions(directory):
            if definition.has_trait(ComponentTrait.MAINTAINABLE):
                assert definition.isolation_regime is not ComponentTrait.ISOLATION_NEVER


# --- 3. il vocabolario e' chiuso, e l'errore nomina cio' che rifiuta -----------


def test_an_unknown_trait_stops_the_catalogue_and_names_it(tmp_path: Path) -> None:
    with pytest.raises(CatalogError) as raised:
        loading(tmp_path, probe(traits=["manutenibile", "isolation_normal", "attachment_inline"]))
    assert "manutenibile" in str(raised.value)


def test_a_component_without_traits_does_not_load(tmp_path: Path) -> None:
    without = {key: value for key, value in probe().items() if key != "traits"}
    with pytest.raises(CatalogError, match="traits"):
        loading(tmp_path, without)


def test_a_component_that_declares_no_isolation_regime_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="no isolation regime") as raised:
        loading(tmp_path, probe(traits=["maintainable", "attachment_inline"]))
    message = str(raised.value)
    assert "strainer" in message
    for regime in ISOLATION_REGIMES:
        assert regime.value in message


def test_a_component_that_declares_two_isolation_regimes_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="more than one isolation regime"):
        loading(
            tmp_path,
            probe(traits=["isolation_normal", "isolation_never", "attachment_inline"]),
        )


def test_a_component_that_declares_no_attachment_style_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="no attachment style"):
        loading(tmp_path, probe(traits=["maintainable", "isolation_normal"]))


def test_a_component_that_declares_two_attachment_styles_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="more than one attachment style"):
        loading(
            tmp_path,
            probe(traits=["isolation_normal", "attachment_inline", "attachment_branch"]),
        )


def test_a_trait_declared_twice_does_not_load(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="the same trait twice"):
        loading(
            tmp_path,
            probe(traits=["maintainable", "maintainable", "isolation_normal", "attachment_inline"]),
        )


def test_being_serviced_and_never_being_shut_off_do_not_load_together(tmp_path: Path) -> None:
    with pytest.raises(CatalogError, match="asks for the valves that the second forbids"):
        loading(tmp_path, probe(traits=["maintainable", "isolation_never", "attachment_branch"]))


# --- 4. l'artefatto che il committente approva --------------------------------


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
