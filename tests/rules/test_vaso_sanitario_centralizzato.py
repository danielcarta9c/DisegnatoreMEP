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
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import GapReason, RuleGap
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleProposalTemplate
from disegnatore_mep.validation.topology import validate_project

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


# --- senza «centralizzata»: la risposta del progettista, e il vaso scritto a mano (I-272) ---
#
# Su una commessa reale (villetta, ACS non centralizzata) il vaso sanitario e' finito **a
# monte** del gruppo di sicurezza. La regola, senza il dato, non lo posa: chiede. Ma alla
# risposta «il bollitore non lo ha, mettilo» il grafo non aveva una forma, e il vaso si
# scriveva a mano sull'acqua fredda (Capire §5, «appeso»). Un pezzo scritto dal progettista
# e' un punto fisso: le regole posano il gruppo di sicurezza, con il non ritorno dentro,
# sull'attacco del bollitore, cioe' **fra** il vaso e il bollitore. Il vaso restava dietro il
# non ritorno, dove la dilatazione non lo trova (D-178).

VASO_A_MONTE = "DHW_EXPANSION_UPSTREAM_OF_THE_CHECK"


def _con_il_bordo(progetto: ProjectModel, **campi: list[str]) -> ProjectModel:
    documento = progetto.model_dump(mode="json")
    for item in documento["components"]:
        if item["id"] == "bollitore":
            item.update(campi)
    return ProjectModel.model_validate(documento)


def _con_il_vaso_a_mano(progetto: ProjectModel) -> ProjectModel:
    """Il vaso come lo scrive Capire §5: un raccordo sull'acqua fredda fra l'acquedotto e il
    bollitore, e dal braccio il vaso."""
    documento = progetto.model_dump(mode="json")
    tubo = next(
        item
        for item in documento["connections"]
        if {item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"]}
        == {"acquedotto", "bollitore"}
    )
    rete = tubo["network_id"]
    documento["connections"].remove(tubo)
    documento["components"] += [
        {"id": "tee-vaso", "definition_id": "tee-branch-cold"},
        {"id": "vaso-sanitario", "definition_id": "expansion-connection-dhw"},
    ]

    def tubo_fra(ident: str, a: tuple[str, str], b: tuple[str, str]) -> dict[str, object]:
        return {
            "id": ident,
            "network_id": rete,
            "endpoint_a": {"component_id": a[0], "port_id": a[1]},
            "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        }

    documento["connections"] += [
        tubo_fra("tv-1", ("acquedotto", "a"), ("tee-vaso", "a")),
        tubo_fra("tv-2", ("tee-vaso", "b"), ("bollitore", "cold_in")),
        tubo_fra("tv-3", ("tee-vaso", "branch"), ("vaso-sanitario", "a")),
    ]
    return ProjectModel.model_validate(documento)


def test_detto_che_il_bollitore_non_lo_ha_il_vaso_si_posa_fra_il_non_ritorno_e_il_bollitore() -> None:
    """La risposta alla domanda della regola — «il bollitore non porta il vaso dentro» — si
    scrive sul bollitore, `non_a_bordo: ["expansion"]`. Il vaso allora lo posa la regola, con
    il suo ordine: attaccato al bollitore, e il gruppo di sicurezza dal lato dell'acquedotto."""
    progetto = _con_il_bordo(
        load_project(PROVA / "prova-2-pdc-deviatrice-acs.json"), non_a_bordo=[EXPANSION]
    )
    done, gaps = _saturato(progetto)
    assert _domande_sul_vaso(gaps) == [], _domande_sul_vaso(gaps)

    fila = _dal_serbatoio(done, "bollitore")
    vasi = [i for i, item in enumerate(fila) if EXPANSION in _funzioni(done, item)]
    ritegni = [i for i, item in enumerate(fila) if NON_RETURN in _funzioni(done, item)]
    assert vasi and ritegni, fila
    assert vasi[0] < ritegni[0], f"il vaso deve stare fra il non ritorno e il bollitore: {fila}"
    assert validate_project(done, catalog()).ok


def test_il_vaso_scritto_a_mano_sull_acqua_fredda_ferma_la_validazione() -> None:
    """Il caso della commessa: il vaso scritto a mano, senza il gruppo. Le regole gli
    metterebbero il gruppo fra lui e il bollitore; la validazione lo dice prima, e dice la
    risposta giusta."""
    progetto = _con_il_vaso_a_mano(load_project(PROVA / "prova-2-pdc-deviatrice-acs.json"))
    esito = validate_project(progetto, catalog())
    trovati = [item for item in esito.issues if item.code == VASO_A_MONTE]
    assert trovati, [item.code for item in esito.issues]
    assert "non_a_bordo" in trovati[0].message

    # Completato, il vaso sta davvero a monte del gruppo: la stessa prova lo ferma.
    done, _ = _saturato(progetto)
    fila = _dal_serbatoio(done, "bollitore")
    primo_ritegno = min(i for i, item in enumerate(fila) if NON_RETURN in _funzioni(done, item))
    assert fila.index("vaso-sanitario") > primo_ritegno, fila
    assert VASO_A_MONTE in {item.code for item in validate_project(done, catalog()).issues}


def test_il_vaso_della_regola_passa_la_prova() -> None:
    """Con l'ACS centralizzata il vaso e' della regola, e sta dove deve: la prova tace."""
    done, _ = _saturato(load_project(PROVA / "prova-5-cascata-tre-pdc.json"))
    assert VASO_A_MONTE not in {item.code for item in validate_project(done, catalog()).issues}


def test_il_bordo_non_si_dice_in_due_modi() -> None:
    """Una funzione a bordo e insieme non a bordo e' un grafo che si contraddice; un nome
    sconosciuto non toglierebbe niente, in silenzio."""
    progetto = load_project(PROVA / "prova-2-pdc-deviatrice-acs.json")
    with pytest.raises(ValidationError, match="non_a_bordo"):
        _con_il_bordo(progetto, a_bordo=[EXPANSION], non_a_bordo=[EXPANSION])
    esito = validate_project(_con_il_bordo(progetto, non_a_bordo=["vaso"]), catalog())
    assert "UNKNOWN_ON_BOARD_FUNCTION" in {item.code for item in esito.issues}


def test_senza_risposta_il_grafo_non_scrive_il_campo() -> None:
    """I grafi agli atti restano identici byte per byte."""
    assert "non_a_bordo" not in canonical_json(load_project(PROVA / "prova-2-pdc-deviatrice-acs.json"))
