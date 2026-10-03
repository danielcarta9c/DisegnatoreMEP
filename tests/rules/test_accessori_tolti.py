"""Togliere un accessorio delle regole, e dire che una macchina lo porta a bordo (REL-009, I-192).

Il progettista, sul primo caso reale (I-191): «è fondamentale che la skill possa togliere
cose che il progettista gli dice di togliere, come accessori ecc.». La tavola di un
impianto costruito dice che cosa c'e', e lui sa che cosa non c'e'.

Le prove stanno sul caso stesso, ricostruito anonimo
(`docs/collaudi/REL-009/caso-reale-1/grafo-prima-stesura.json`), con le scelte T1–T5
del documento del progettista:

- un accessorio tolto non si posa, a nessun rilancio, e non torna come punto aperto;
- chi pendeva da lui se ne va con lui — le intercettazioni del separatore tolto;
- una voce che non toglie niente si riconosce;
- il bordo dichiarato sulla singola macchina vale come quello del catalogo, tranne dove
  la regola vuole il pezzo comunque (la sicurezza di ogni generatore, D-182);
- un nome di funzione sconosciuto nel bordo ferma la validazione.
"""

# categoria: difende il contenuto — I-192, il progettista toglie quello che sul costruito non c'e'

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import Saturation, saturation
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-1" / "grafo-prima-stesura.json"

TERMINALI = [
    f"valve-isolation-{tipo}-mz{zona}-{n}-{lato}"
    for zona, quanti in ((1, 3), (2, 5))
    for n in range(1, quanti + 1)
    for tipo in ("fc", "rad")
    for lato in ("in", "out")
]
"""T1: le 32 intercettazioni su ingresso e uscita di ogni ventilconvettore e di ogni
pannello. Sul costruito le valvole stanno sulle uscite del collettore."""

DEL_PRIMARIO = [
    f"{pezzo}-{raccordo}"
    for raccordo in ("ts-pa-a", "ts-pr-3-a")
    for pezzo in ("dirt-separator", "expansion-connection", "filling-unit", "pressure-gauge")
]
"""T4 e T5: defangatore, vaso, riempimento e manometro sul ritorno dei due primari."""

SEPARATORI = ["air-separator-tj-pa-b", "air-separator-tj-pr-3-b"]
"""T3: i separatori d'aria sulla mandata ai due volani."""


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


def _caso(**cambi: Any) -> ProjectModel:
    documento = json.loads(CASO.read_text(encoding="utf-8"))
    documento.update(cambi)
    return ProjectModel.model_validate(documento)


def _tolti(*pezzi: str) -> list[dict[str, str]]:
    return [{"pezzo": pezzo, "motivo": "sul costruito non c'e'"} for pezzo in pezzi]


@cache
def _senza_scelte() -> Saturation:
    return saturation(load_project(CASO), catalog(), rules())


def test_la_misura_di_partenza_e_quella_del_documento() -> None:
    """La 1.2.2 sul grafo del caso: 70 pezzi diventano 207, nessun punto aperto."""
    risultato = _senza_scelte()
    assert len(risultato.model.components) == 207
    assert len(risultato.model.connections) == 228
    assert risultato.gaps == []
    posati = {item.id for item in risultato.model.components}
    assert set(TERMINALI + DEL_PRIMARIO + SEPARATORI) <= posati, "i pezzi che le prove tolgono ci sono"


def test_un_accessorio_tolto_non_si_posa_e_non_torna_come_punto_aperto() -> None:
    tolti = TERMINALI + DEL_PRIMARIO + SEPARATORI
    risultato = saturation(_caso(accessori_tolti=_tolti(*tolti)), catalog(), rules())
    posati = {item.id for item in risultato.model.components}
    assert not set(tolti) & posati
    assert sorted(item.component_id for item in risultato.withheld) == sorted(tolti)
    assert risultato.gaps == []
    # Chi pendeva da un pezzo tolto se ne va con lui: le due intercettazioni del
    # separatore, la valvola bloccata aperta del vaso, il rubinetto del manometro.
    assert not [item for item in posati if item.startswith(("valve-isolation-air-separator", "valve-gauge-cock"))]
    assert len(risultato.model.components) == 149


def test_la_scelta_regge_a_ogni_rilancio() -> None:
    """Le regole rilanciate sul grafo completo non propongono niente: il grafo porta
    le sue scelte, e il pezzo tolto resta tolto."""
    primo = saturation(_caso(accessori_tolti=_tolti(*SEPARATORI)), catalog(), rules())
    secondo = saturation(primo.model, catalog(), rules())
    assert secondo.applied == []
    assert canonical_json(secondo.model) == canonical_json(primo.model)
    assert [item.pezzo for item in secondo.model.accessori_tolti] == SEPARATORI


def test_una_voce_che_non_toglie_niente_si_riconosce() -> None:
    risultato = saturation(
        _caso(accessori_tolti=_tolti("valve-safety-pdc-x9-water-supply")), catalog(), rules()
    )
    assert risultato.withheld == []
    assert len(risultato.model.components) == 207


def test_il_bordo_della_singola_macchina_vale_come_quello_del_catalogo() -> None:
    """Il filtro sul ritorno: se il progettista dice che quella pompa lo porta dentro,
    la regola non lo posa, su quella pompa sola."""
    documento = json.loads(CASO.read_text(encoding="utf-8"))
    for pezzo in documento["components"]:
        if pezzo["id"] == "pdc-r1":
            pezzo["a_bordo"] = ["filtration"]
    risultato = saturation(ProjectModel.model_validate(documento), catalog(), rules())
    posati = {item.id for item in risultato.model.components}
    assert "strainer-pdc-r1-water-return" not in posati
    assert "strainer-pdc-r2-water-return" in posati


def test_dove_la_regola_vuole_il_pezzo_comunque_il_bordo_non_basta() -> None:
    """La sicurezza di ogni generatore (D-182): dichiarata a bordo, si posa lo stesso.
    Per toglierla c'e' «togli», con il motivo."""
    documento = json.loads(CASO.read_text(encoding="utf-8"))
    for pezzo in documento["components"]:
        if pezzo["id"] == "pdc-r1":
            pezzo["a_bordo"] = ["safety"]
    posati = {
        item.id
        for item in saturation(ProjectModel.model_validate(documento), catalog(), rules()).model.components
    }
    assert "valve-safety-pdc-r1-water-supply" in posati
    documento["accessori_tolti"] = _tolti("valve-safety-pdc-r1-water-supply")
    posati = {
        item.id
        for item in saturation(ProjectModel.model_validate(documento), catalog(), rules()).model.components
    }
    assert "valve-safety-pdc-r1-water-supply" not in posati


def test_un_nome_di_funzione_sconosciuto_nel_bordo_ferma_la_validazione() -> None:
    documento = json.loads(CASO.read_text(encoding="utf-8"))
    documento["components"][0]["a_bordo"] = ["valvola-di-sicurezza"]
    esito = validate_project(ProjectModel.model_validate(documento), catalog())
    assert not esito.ok
    assert [item.code for item in esito.issues if item.code == "UNKNOWN_ON_BOARD_FUNCTION"]


def test_un_pezzo_non_si_toglie_due_volte_ne_se_e_nel_grafo() -> None:
    with pytest.raises(ValidationError, match="tolto due volte"):
        _caso(accessori_tolti=_tolti("air-separator-tj-pa-b", "air-separator-tj-pa-b"))
    with pytest.raises(ValidationError, match="nel grafo e fra quelli tolti"):
        _caso(accessori_tolti=_tolti("pdc-r1"))


def test_senza_scelte_il_grafo_non_scrive_i_campi_nuovi() -> None:
    """I grafi agli atti restano identici byte per byte: un campo vuoto non si scrive."""
    scritto = canonical_json(load_project(CASO))
    assert "accessori_tolti" not in scritto
    assert "a_bordo" not in scritto


def test_spostare_e_togliere_da_un_posto_e_posare_nell_altro() -> None:
    """T5: vaso, riempimento e manometro del primario stanno sul secondario, in
    centrale. La regola li posa sull'attacco indicato, con quello che ne pende: la
    valvola bloccata aperta del vaso, il rubinetto del manometro, il ponte del
    riempimento con il suo confine d'acquedotto."""
    spostati = [
        {"pezzo": f"{pezzo}-ts-pr-3-a", "motivo": "sta sul secondario, in centrale", "altrove": "tj-mz.b"}
        for pezzo in ("expansion-connection", "filling-unit", "pressure-gauge")
    ]
    risultato = saturation(_caso(accessori_tolti=spostati), catalog(), rules())
    pezzi = {item.id: item for item in risultato.model.components}
    reti = {
        ref.component_id: connessione.network_id
        for connessione in risultato.model.connections
        for ref in (connessione.endpoint_a, connessione.endpoint_b)
    }
    for pezzo in ("expansion-connection", "filling-unit", "pressure-gauge"):
        assert f"{pezzo}-ts-pr-3-a" not in pezzi
        assert reti[f"{pezzo}-tj-mz-b"] == "secondario-risc"
    assert "valve-isolation-locked-open-expansion-connection-tj-mz-b-a" in pezzi
    assert "valve-gauge-cock-3way-pressure-gauge-tj-mz-b-a" in pezzi
    assert "inlet-filling-unit-tj-mz-b" in pezzi
    assert len(pezzi) == 207, "spostati, non tolti"
    secondo = saturation(risultato.model, catalog(), rules())
    assert secondo.applied == []


def test_si_sposta_solo_su_un_attacco_collegato() -> None:
    """Uno scarico o uno sfiato del volano pende gia' dall'attacco di servizio: il suo
    nome cita l'attacco da cui la regola parte (`drain-connection-volano-risc-primary-in`
    sta su `volano-risc.drain`). Si sposta su una tubazione."""
    spostato = [{"pezzo": "expansion-connection-ts-pr-3-a", "motivo": "altrove", "altrove": "volano-risc.drain"}]
    esito = validate_project(_caso(accessori_tolti=spostato), catalog())
    assert [item.code for item in esito.issues] == ["UNKNOWN_RELOCATION_PORT"]
