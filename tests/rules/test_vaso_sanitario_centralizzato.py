"""Il vaso di espansione sanitario negli impianti con ACS centralizzata (**D-178**).

Il PO, il 23 settembre 2026:

    «quando abbiamo impianti centralizzati con ACS (quindi parliamo di accumuli
    ACS da 1000 litri in su) conviene mettere un vaso di espansione sanitario, ma
    non sulla mandata ACS calda. Va normalmente collegato sull'ingresso AF del
    bollitore, nel tratto compreso fra il dispositivo di non ritorno e il
    bollitore.»

e il 24, alla domanda sull'impianto 5 — il testo dice «ACS centralizzata
mediante un bollitore da 500 litri» —: **conta «centralizzata»** (I-113), non la
soglia dei 1000 litri.

Fino a quel giorno la regola del vaso sanitario non lo aggiungeva mai da sola:
molti accumuli lo portano dentro, e dove il catalogo tace chiedeva al
progettista. Una prova per parte, come chiede il pacchetto:

- **con l'ACS centralizzata** — il dato che il progettista scrive e «Capire»
  trascrive nelle proprieta' dell'accumulo — il vaso si posa senza chiedere, e
  sta fra il dispositivo di non ritorno e il bollitore;
- **senza**, la regola chiede come prima.
"""

# categoria: difende il contenuto — D-178, il vaso sanitario dove l'ACS e' centralizzata, fra il non ritorno e il bollitore

from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import GapReason, RuleGap
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleProposalTemplate

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "examples" / "prova"
REGOLA = "expansion-on-the-stored-volume-feed"
EXPANSION = "expansion"
NON_RETURN = "non_return"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(ROOT / "rules" / "hydronic")
    registry.cross_check(catalog())
    return registry


def _saturato(model: ProjectModel) -> tuple[ProjectModel, list[RuleGap]]:
    done, _, gaps = saturate(model, catalog(), rules())
    return done, gaps


def _funzioni(model: ProjectModel, component_id: str) -> frozenset[str]:
    """Quello che il pezzo fa, compreso cio' che porta a bordo."""
    definition = catalog().get(
        next(item.definition_id for item in model.components if item.id == component_id)
    )
    return frozenset((*definition.functions, *definition.carries_on_board))


def _dal_serbatoio(model: ProjectModel, serbatoio: str) -> list[str]:
    """I pezzi dell'alimentazione fredda, dal serbatoio verso l'acquedotto.

    Per ogni raccordo si guarda anche cio' che gli pende dal braccio: il vaso
    sta su uno stacco, e il suo posto nella fila e' quello del suo raccordo."""
    pezzi: list[str] = []
    precedente, attuale, porta = serbatoio, None, "cold_in"
    for connection in model.connections:
        if (connection.endpoint_b.component_id, connection.endpoint_b.port_id) == (
            serbatoio,
            porta,
        ):
            attuale = connection.endpoint_a.component_id
    while attuale is not None:
        appesi = [
            (connection.endpoint_b.component_id)
            for connection in model.connections
            if connection.endpoint_a.component_id == attuale
            and connection.endpoint_a.port_id == "branch"
        ]
        pezzi.append(attuale)
        for appeso in appesi:
            pezzi.extend(_fino_in_fondo(model, attuale, appeso))
        entrante = [
            connection.endpoint_a.component_id
            for connection in model.connections
            if connection.endpoint_b.component_id == attuale
            and connection.endpoint_a.component_id != precedente
        ]
        precedente, attuale = attuale, entrante[0] if entrante else None
    return pezzi


def _fino_in_fondo(model: ProjectModel, radice: str, primo: str) -> list[str]:
    """Lo stacco, dal raccordo fino all'accessorio in fondo."""
    catena, visti = [primo], {radice, primo}
    while True:
        avanti = [
            ref.component_id
            for connection in model.connections
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if catena[-1] in (connection.endpoint_a.component_id, connection.endpoint_b.component_id)
            and ref.component_id not in visti
        ]
        if len(avanti) != 1:
            return catena
        catena.append(avanti[0])
        visti.add(avanti[0])


def _domande_sul_vaso(gaps: list[RuleGap]) -> list[RuleGap]:
    return [gap for gap in gaps if gap.rule_id == REGOLA]


def test_con_l_acs_centralizzata_il_vaso_si_posa_fra_il_non_ritorno_e_il_bollitore() -> None:
    """L'impianto 5: «La produzione di ACS e' centralizzata mediante un bollitore
    da 500 litri». Il vaso c'e', nessuno lo chiede, e dal bollitore si incontra
    **prima il vaso, poi il dispositivo di non ritorno** — che qui e' dentro il
    gruppo di sicurezza sanitario."""
    progetto = load_project(PROVA / "prova-5-cascata-tre-pdc.json")
    bollitore = next(item for item in progetto.components if item.id == "bollitore")
    assert bollitore.properties.get("produzione") == "centralizzata"

    done, gaps = _saturato(progetto)
    assert _domande_sul_vaso(gaps) == [], _domande_sul_vaso(gaps)

    fila = _dal_serbatoio(done, "bollitore")
    vasi = [i for i, item in enumerate(fila) if EXPANSION in _funzioni(done, item)]
    ritegni = [i for i, item in enumerate(fila) if NON_RETURN in _funzioni(done, item)]
    assert vasi, f"nessun vaso sull'alimentazione fredda del bollitore: {fila}"
    assert ritegni, f"nessun dispositivo di non ritorno: {fila}"
    assert vasi[0] < ritegni[0], (
        f"il vaso deve stare fra il non ritorno e il bollitore, e la fila dal "
        f"bollitore e' {fila}"
    )

    # Mai sulla mandata calda.
    calde = {item.id for item in done.networks if item.medium == "domestic_hot_water"}
    for connection in done.connections:
        if connection.network_id not in calde:
            continue
        for ref in (connection.endpoint_a, connection.endpoint_b):
            assert EXPANSION not in _funzioni(done, ref.component_id), ref.component_id


def test_senza_il_dato_la_regola_chiede_come_prima() -> None:
    """L'impianto 2 non dice come e' prodotta l'acqua calda: il vaso non nasce,
    e resta la domanda di sempre — il catalogo non dice se il bollitore lo porta
    dentro."""
    done, gaps = _saturato(load_project(PROVA / "prova-2-pdc-deviatrice-acs.json"))
    domande = _domande_sul_vaso(gaps)
    assert [gap.reason for gap in domande] == [GapReason.ON_BOARD_UNKNOWN], domande
    assert not any(
        EXPANSION in _funzioni(done, item)
        for item in _dal_serbatoio(done, "bollitore")
    )


def test_il_dato_e_la_parola_del_progettista_trascritta_com_e() -> None:
    """Maiuscole e spazi non contano: e' una parola del testo, non un codice. E
    un altro valore non toglie la domanda."""
    progetto = load_project(PROVA / "prova-2-pdc-deviatrice-acs.json")

    def con(valore: str) -> ProjectModel:
        return progetto.model_copy(
            update={
                "components": [
                    item.model_copy(update={"properties": {"produzione": valore}})
                    if item.id == "bollitore"
                    else item
                    for item in progetto.components
                ]
            }
        )

    _, gaps = _saturato(con(" Centralizzata "))
    assert _domande_sul_vaso(gaps) == []
    _, gaps = _saturato(con("autonoma"))
    assert [gap.reason for gap in _domande_sul_vaso(gaps)] == [GapReason.ON_BOARD_UNKNOWN]


def test_una_regola_che_non_chiede_non_puo_dire_quando_non_chiedere() -> None:
    """La clausola toglie una domanda: su una regola che non ne fa e' un errore
    di scrittura, e si ferma al caricamento."""
    with pytest.raises(ValidationError, match="unless_the_anchor_declares"):
        RuleProposalTemplate.model_validate(
            {
                "provides_function": EXPANSION,
                "placement": "on_inlet",
                "inlet_port": "a",
                "outlet_port": "b",
                "unless_the_anchor_declares": {"produzione": "centralizzata"},
            }
        )
