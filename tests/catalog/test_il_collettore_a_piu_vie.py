"""Il collettore di zona con ritorno a piu' vie (REL-016, D3 del collaudo della 1.7.0).

Il collaudo indipendente della 1.7.0 (`docs/collaudi/REL-015/collaudo-1.7.0/RAPPORTO.md`, D3):
«il catalogo non ha un collettore a piu' di 2 vie. `catalogo zone-manifold-pair` da' le porte
`out_1, out_2, ret_1, ret_2`, e basta. Il "collettore a 6 vie" del caso 2 non si puo' disegnare:
sulla tavola c'e' un pannello rappresentativo». Adesso il collettore con ritorno ha una voce
per numero di vie, da tre a dodici, come il plenum di zona da due a sei uscite: lo stesso
disegno di quello a due, una coppia ogni 20 mm.

Il collettore a due vie (`zone-manifold-pair`) resta **byte per byte** quello della 1.7.0: le
tavole idroniche del banco lo usano, e non devono cambiare. Rosse sul commit di partenza.
"""
# categoria: difende il motore

import contextlib
import hashlib
import io
import json
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
D3 = ROOT / "docs" / "collaudi" / "REL-016" / "d3"

VIE = range(3, 13)
IN_LETTERE = {
    3: "tre", 4: "quattro", 5: "cinque", 6: "sei", 7: "sette", 8: "otto", 9: "nove",
    10: "dieci", 11: "undici", 12: "dodici",
}

IL_DUE_DELLA_1_7_0 = {
    "assets/symbols/zone-manifold-pair.json": "b2c9a2c8008fa75fff91c5dddb1406e9b48a7ba5268c85f5f590031daf55a8e1",
    "assets/symbols/zone-manifold-pair.svg": "6413acfa1c1944b5b5edaaa3d294196a60dae8a9cd38bc7715eb98211c9e9e4a",
    "examples/layout/catalog/zone-manifold-pair.json": "4e169594e0b89ae234416d29b61e099b97b90fc2c63e92d1292560f04ddab07c",
}
"""L'impronta dei tre file del collettore a due vie sul commit di partenza (58354456, la 1.7.1)."""


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@pytest.mark.parametrize("vie", VIE)
def test_il_catalogo_ha_il_collettore_da_tre_a_dodici_vie(vie: int) -> None:
    """Una voce per numero, col nome che dice le vie, i mestieri e i caratteri di quello a
    due, e una mandata e un ritorno per via, tutti obbligatori."""
    voce = catalogo().get(f"zone-manifold-pair-{vie}")
    due = catalogo().get("zone-manifold-pair")
    assert voce.name == f"Collettore di zona con ritorno a {IN_LETTERE[vie]} vie"
    assert voce.functions == due.functions
    assert voce.traits == due.traits
    assert voce.symbol_id == f"zone-manifold-pair-{vie}"
    mandate = [f"out_{indice}" for indice in range(1, vie + 1)]
    ritorni = [f"ret_{indice}" for indice in range(1, vie + 1)]
    assert [porta.id for porta in voce.ports] == ["in", "out", *mandate, *ritorni]
    assert all(porta.required for porta in voce.ports)
    verso = {porta.id: porta.flow.value for porta in voce.ports}
    assert {verso[porta] for porta in ["in", *ritorni]} == {"in"}
    assert {verso[porta] for porta in ["out", *mandate]} == {"out"}
    # I passaggi di quello a due: l'ingresso con tutte le mandate, i ritorni con l'uscita.
    assert voce.passaggi == [["in", *mandate], [*ritorni, "out"]]


@pytest.mark.parametrize("vie", VIE)
def test_il_simbolo_ha_una_coppia_ogni_20_mm(vie: int) -> None:
    """Come quello a due: alto 15, ingresso e uscita a sinistra a 10 mm, e sotto le coppie
    mandata-ritorno a 10 mm come gli attacchi dei terminali, una coppia ogni 20 mm."""
    manifesto = simboli().get(f"zone-manifold-pair-{vie}").manifest
    assert (manifesto.width_mm, manifesto.height_mm) == (20.0 * vie, 15.0)
    assert manifesto.allowed_rotations_deg == [0]
    porte = {porta.id: (porta.face.value, porta.x_mm, porta.y_mm) for porta in manifesto.ports}
    assert porte.pop("in") == ("left", 0.0, 2.5)
    assert porte.pop("out") == ("left", 0.0, 12.5)
    for indice in range(vie):
        assert porte.pop(f"out_{indice + 1}") == ("bottom", 7.5 + 20 * indice, 15.0)
        assert porte.pop(f"ret_{indice + 1}") == ("bottom", 17.5 + 20 * indice, 15.0)
    assert porte == {}


@pytest.mark.parametrize("vie", VIE)
def test_il_segno_e_quello_del_collettore_a_due(vie: int) -> None:
    """Due barre continue lunghe tutto il collettore, e ogni discesa di mandata interrotta
    davanti alla barra del ritorno (REL-015, I-231): lo stesso segno, piu' lungo."""
    corpo = simboli().get(f"zone-manifold-pair-{vie}").body
    larghezza = 20.0 * vie - 2.0
    assert corpo.count("<rect ") == 2
    assert corpo.count(f'width="{larghezza:g}"') == 2
    for indice in range(vie):
        x = f"{7.5 + 20 * indice:g}"
        assert f'<line x1="{x}" y1="3.5" x2="{x}" y2="10.75"/>' in corpo
        assert f'<line x1="{x}" y1="14.25" x2="{x}" y2="15"/>' in corpo


def test_il_collettore_a_due_vie_e_quello_della_1_7_0() -> None:
    """Le 24 tavole idroniche del banco usano `zone-manifold-pair`: manifesto, corpo e voce
    restano i file della 1.7.0, all'ultimo byte."""
    for percorso, impronta in IL_DUE_DELLA_1_7_0.items():
        assert hashlib.sha256((ROOT / percorso).read_bytes()).hexdigest() == impronta, percorso


def test_la_villetta_del_collaudo_col_collettore_a_sei_vie_si_disegna(tmp_path: Path) -> None:
    """Il caso del collaudo, con il collettore a sei vie e sei pannelli al posto del pannello
    rappresentativo, si valida, si completa e si disegna col suo piano: nessuna tratta
    ceduta, nessun rilievo bloccante, e il collettore a sei vie sulla tavola e in legenda."""
    grafo = json.loads((D3 / "grafo.json").read_text(encoding="utf-8"))
    pezzi = {c["id"]: c["definition_id"] for c in grafo["components"]}
    assert pezzi["collettore"] == "zone-manifold-pair-6"
    assert sorted(i for i, d in pezzi.items() if d == "underfloor-panel") == [f"pannello-{v}" for v in range(1, 7)]
    cartelle = cartelle_del_repository(ROOT)
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        assert main(["valida", str(D3 / "grafo.json")], cartelle) == 0
        assert main(["completa", str(D3 / "grafo.json"), "--out", str(tmp_path / "gc.json")], cartelle) == 0
        codice = main(
            ["disegna", str(tmp_path / "gc.json"), "--piano", str(D3 / "piano.json"),
             "--out", str(tmp_path / "tavola"), "--senza-dxf"],
            cartelle,
        )
    assert codice == 0, uscita.getvalue()
    assert "tratte cedute 0 · rilievi bloccanti 0" in uscita.getvalue()
    svg = next((tmp_path / "tavola").glob("*.svg")).read_text(encoding="utf-8")
    # Il simbolo sulla tavola e nella legenda, col nome che va a capo dopo «zona».
    assert svg.count('data-symbol-id="zone-manifold-pair-6"') == 2
    assert ">con ritorno a sei vie<" in svg


def test_capire_dice_quale_voce_per_un_collettore_a_n_vie() -> None:
    """Senza queste righe Capire non saprebbe che la voce dice le vie, e tornerebbe al
    pannello rappresentativo del collaudo."""
    testo = (ROOT / "skill" / "capire" / "ISTRUZIONI.md").read_text(encoding="utf-8")
    assert "`zone-manifold-pair-3` … `zone-manifold-pair-12`" in testo
    assert "`zone-manifold-pair-6`" in testo
    comporre = (ROOT / "skill" / "comporre" / "ISTRUZIONI.md").read_text(encoding="utf-8")
    assert "**+5 + 20·(n−1)**" in comporre
