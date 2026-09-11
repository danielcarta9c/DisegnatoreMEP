"""Le prove di DRAW-007, blocco C: l'allineamento del tronco.

Il PO, il 10 settembre 2026:

    «Allineando ingressi e uscite della macchina principale con quelli del
    serbatoio principale automaticamente abbiamo gia' due linee macro
    parallele che diventano la nostra autostrada per le strade secondarie.»

Non e' una rifinitura: e' il primo atto del disegno. Fino a DRAW-006-R1 lo era
in due modi sbagliati, e questo blocco li attacca tutt'e due.

**Il momento.** Le candidate di asse nascevano soltanto in fase di
rifinitura — `self.refining` — cioe' quando la disposizione era gia' decisa.
Si chiedeva al ciclo di raddrizzare due macro-linee dopo aver costruito la
tavola attorno a una posa che non le prevedeva. Sulla tavola 2, alla posa
iniziale, di candidate di asse non ne nasceva **nemmeno una**: la candidata
PDC-puffer non perdeva sul costo, non veniva proprio generata.

**La granularita'.** La mossa muoveva una colonna intera, trascinando pezzi
che con quella coppia di porte non c'entrano: pagava contorno estraneo, e per
quel contorno il costo la respingeva. Deve poter muovere anche **una macchina
col proprio corredo**, che e' la mossa che un disegnatore fa davvero.
"""

import json
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.improve import Improver
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
TAVOLA_2 = ROOT / "examples" / "prova" / "prova-2-pdc-deviatrice-acs.json"
QUATTRO_FASCE = ROOT / "examples" / "layout" / "centrale-pdc-quattro-fasce.json"
"""Il caso di posa congelato: qui le colonne portano piu"di un'unita', che e'
la forma su cui la granularita' della mossa si vede."""


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def _completato(path: Path) -> ProjectModel:
    done, _, _ = saturate(
        load_project(path), catalog(), RuleRegistry.from_directory(ROOT / "rules" / "hydronic")
    )
    return ProjectModel.model_validate(json.loads(canonical_json(done)))


def _improver(project: ProjectModel) -> Improver:
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = partition_project(project, build_trunks(project, inline))[0]
    placed = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    return Improver(project, partition, registry, NOVE_C_A3, placed, inline)


def _assi(improver: Improver, leader: str) -> list[dict[str, object]]:
    return [
        dict(move)
        for kind, move in improver.candidates_by_kind(leader)
        if kind == "asse"
    ]


# ---------------------------------------------------------------------------
# C.1 — l'allineamento del tronco si cerca nella posa, non nella rifinitura
# ---------------------------------------------------------------------------


def test_la_posa_genera_gia_le_candidate_di_asse_fra_le_macchine_di_spina() -> None:
    """Il difetto che questa prova presidia: alla posa iniziale della tavola 2
    non nasceva **nessuna** candidata di asse, perche' nascevano solo a
    rifinitura. La candidata che il PO chiedeva non perdeva sul costo: non
    esisteva."""
    improver = _improver(_completato(TAVOLA_2))
    assert not improver.refining, "questa prova guarda la fase di posa"
    con_assi = [
        leader
        for leader in improver.spine
        if leader in improver.best and _assi(improver, leader)
    ]
    assert con_assi, (
        "nessuna macchina di spina riceve una candidata di asse nella posa: "
        f"spina {sorted(improver.spine)}"
    )


def test_nella_posa_l_asse_guarda_soltanto_il_tronco() -> None:
    """L'asse del tronco e' una struttura; il contorno si sistema dopo. Nella
    posa le candidate di asse riguardano le sole macchine di spina, cosi' la
    fase prima non si disperde dietro a ogni coppia di porte dell'impianto."""
    improver = _improver(_completato(TAVOLA_2))
    fuori = [
        leader
        for leader in improver.scan
        if leader not in improver.parent_of
        and leader not in improver.spine
        and _assi(improver, leader)
    ]
    assert fuori == [], fuori


def test_nella_rifinitura_l_asse_torna_a_guardare_tutto() -> None:
    """L'altro verso: la restrizione vale per la **fase**, non per sempre. A
    rifinitura le coppie di DRAW-006-R1 — attraverso raccordi, catene e
    multivia — si generano come prima, altrimenti questo pacchetto avrebbe
    ristretto la ricerca invece di anticiparla."""
    improver = _improver(_completato(TAVOLA_2))
    prima = {leader: len(_assi(improver, leader)) for leader in improver.scan}
    improver.refining = True
    dopo = {leader: len(_assi(improver, leader)) for leader in improver.scan}
    assert sum(dopo.values()) > sum(prima.values()), (sum(prima.values()), sum(dopo.values()))


# ---------------------------------------------------------------------------
# C.2 — la granularita': una macchina col proprio corredo, non una colonna
# ---------------------------------------------------------------------------


def test_fra_le_candidate_di_asse_ce_n_e_una_che_muove_la_sola_macchina() -> None:
    """Su un pezzo che divide la colonna con altri, l'allineamento deve poter
    muovere **lui e il suo corredo** e basta.

    La prova si verifica da sola: pretende di aver trovato almeno un pezzo la
    cui colonna sia strettamente piu' grande della propria unita', cosi' non
    puo' passare per caso su una forma dove le due cose coincidono.
    """
    improver = _improver(load_project(QUATTRO_FASCE))
    improver.refining = True
    provati: list[str] = []
    for leader in improver.scan:
        if leader in improver.parent_of:
            continue
        unita = set(improver.unit_of(leader))
        if not set(improver.column_of(leader)) > unita:
            continue
        assi = _assi(improver, leader)
        if not assi:
            continue
        provati.append(leader)
        assert any(set(move) <= unita for move in assi), (
            leader,
            "nessuna candidata di asse muove la sola macchina col proprio "
            "corredo: restano quelle a colonna intera, che pagano contorno "
            "estraneo e per quello vengono respinte",
        )
    assert provati, (
        "nessun pezzo di questo impianto divide la colonna con altri e riceve "
        "candidate di asse: la prova non sta misurando niente"
    )


def test_le_candidate_a_colonna_intera_non_sono_sparite() -> None:
    """La granularita' nuova si **aggiunge**, non sostituisce: su una forma
    stretta la colonna intera puo' restare la mossa giusta, e toglierla
    sarebbe restringere la ricerca invece di allargarla."""
    improver = _improver(load_project(QUATTRO_FASCE))
    improver.refining = True
    trovato = False
    for leader in improver.scan:
        if leader in improver.parent_of:
            continue
        unita = set(improver.unit_of(leader))
        if not set(improver.column_of(leader)) > unita:
            continue
        assi = _assi(improver, leader)
        if not assi:
            continue
        trovato = True
        assert any(not set(move) <= unita for move in assi), leader
    assert trovato, "la prova non ha trovato nessun caso da misurare"
