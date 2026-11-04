"""Una scritta per tratto, niente sugli stacchi e sui pezzetti fra due T (I-279).

Sulla commessa il progettista aveva scritto la sezione su ogni tubazione del primario, e
la tavola si fermava (`RUN_LABEL_OMITTED`) finche' non le cancellava a mano da quelle
corte fra due derivazioni e dagli stacchi dei pezzi appesi — vaso, sicurezza, manometro,
riempimento. Qui la villetta di riferimento (`docs/collaudi/REL-015/pdc-regola/`, il suo
piano dell'idraulica) con i diametri chiesti, prima col solo calcolo e poi con la
sezione del progettista su **tutte** le tubazioni del primario: nessun rilievo che
blocca, al piu' una scritta per tratto, e nessuna sugli stacchi.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.scritte import tratti_da_scrivere
from disegnatore_mep.diametri.tratti import tratti_del_diametro
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"


def _grafo(sezione: str | None) -> dict[str, Any]:
    testo: dict[str, Any] = json.loads((VILLETTA / "grafo-completo.json").read_text(encoding="utf-8"))
    for pezzo in testo["components"]:
        if pezzo["id"] == "pdc":
            pezzo["properties"]["delta_t_k"] = 5
    if sezione is not None:
        for tubo in testo["connections"]:
            if tubo["network_id"] == "primario":
                tubo["sezione"] = sezione
    testo["diametri"] = {"reti": ["primario"]}
    return testo


@pytest.mark.parametrize("sezione", [None, "MS 32×3"], ids=["calcolo", "del-progettista"])
def test_la_villetta_una_scritta_per_tratto(
    sezione: str | None, catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> None:
    modello = ProjectModel.model_validate(_grafo(sezione))
    del_progetto = catalogo.per_il_progetto(modello)
    esito = esegui_piano(
        modello, carica_piano(VILLETTA / "piano-idraulica.json"), del_progetto, simboli, ROOT / "naming"
    )
    assert esito.disegno is not None
    (foglio,) = esito.disegno.sheets
    codici = [r.code for r in esito.rilievi]
    assert "RUN_LABEL_OMITTED" not in codici and not esito.bloccanti, codici
    assert not [c for c in codici if c.startswith("DIAMETER_")], codici

    primario = [t for t in tratti_del_diametro(modello, del_progetto) if t.reti == ("primario",)]
    assert len(primario) == 5
    sul_primario = [
        e for e in foglio.diametri if set(e.connection_ids) & {c.id for c in modello.connections if c.network_id == "primario"}
    ]
    # Al piu' una scritta per tratto, e il primario ne ha una per tratto: cinque.
    for tratto in primario:
        quante = [e for e in sul_primario if set(e.connection_ids) & tratto.connection_ids]
        assert len(quante) == 1, (tratto.capi, [e.testo for e in quante])
        assert set(quante[0].connection_ids) == set(tratto.connection_ids)
    assert len(sul_primario) == 5
    assert {e.testo for e in sul_primario} == {"MS 32×3"}
    assert all(e.del_progettista is (sezione is not None) for e in sul_primario)
    # Niente sugli stacchi dei pezzi appesi.
    stacchi = {c.id for c in modello.connections if c.network_id == "primario" and c.id.startswith("stub-")}
    assert stacchi
    assert not any(set(e.connection_ids) & stacchi for e in foglio.diametri)


def test_una_sezione_diversa_su_una_tubazione_si_scrive_a_parte(catalogo: ComponentRegistry) -> None:
    """Un tubo diverso in mezzo al tratto non si nasconde: ogni tratta del motore la sua."""
    testo = _grafo("MS 32×3")
    for tubo in testo["connections"]:
        if tubo["id"] == "t1-a":
            tubo["sezione"] = "MS 40×3,5"
    modello = ProjectModel.model_validate(testo)
    scritte, _ = tratti_da_scrivere(modello, catalogo.per_il_progetto(modello))
    testi = sorted(s.scritta for s in scritte if s.tubo is not None)
    assert "MS 40×3,5" in testi and testi.count("MS 40×3,5") == 1


def test_il_tratto_fra_due_raccordi_con_lo_stesso_tubo_del_vicino_cede(
    modello: Callable[..., ProjectModel], catalogo: ComponentRegistry
) -> None:
    """Impianto 5, in acciaio: il ritorno fra il T dove si uniscono volano e bollitore e il
    T della cascata porta DN 65 come il tratto del volano che ci arriva; il ritorno dei
    radianti fra la miscelatrice e il T del secondario, DN 32 come il tratto dei radianti.
    Sono fra due raccordi e continuano il tubo del vicino: cedono (`ripetuto`). Il tratto
    fra i due T della cascata, DN 50, no: il suo tubo e' diverso da quelli accanto."""
    impianto = modello("5")
    del_progetto = catalogo.per_il_progetto(impianto)
    _, calcolati = tratti_da_scrivere(impianto, del_progetto)
    raccordi = {p.id for p in impianto.components if del_progetto.get(p.definition_id).is_a_fitting}
    ripetuti = {(t.capi[0].component_id, t.capi[1].component_id): t.scritta for t in calcolati if t.ripetuto}
    assert ripetuti == {
        ("ritorno-primario", "cascata-ritorno-a"): 'DN 65 (2½")',
        ("ritorno-radiante", "secondario-ritorno-a"): 'DN 32 (1¼")',
    }
    assert {capo for coppia in ripetuti for capo in coppia} <= raccordi
    capi = {(t.capi[0].component_id, t.capi[1].component_id): t for t in calcolati}
    fra_i_t = capi[("cascata-ritorno-a", "cascata-ritorno-b")]
    assert not fra_i_t.ripetuto and fra_i_t.scritta == 'DN 50 (2")'
