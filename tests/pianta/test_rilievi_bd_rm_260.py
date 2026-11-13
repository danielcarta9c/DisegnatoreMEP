"""I rilievi d'uso della 2.0.0 sulla pianta (REL-026, blocco B; I-300).

La sessione che ha usato la 2.0.0 sulla commessa BD.RM.260 ha lavorato su una copia
della skill e ha annotato che cosa ha dovuto cambiare (`docs/input-pm/2026-11-13-
rilievi-bd-rm-260/`). I file della commessa non entrano nel repository: ogni voce si
prova qui su un caso del repository o su un caso anonimo scritto apposta.

- B-1 il nome corto dei fluidi idronici nella tabella delle tratte;
- B-2 `sagome_muri`, il retino dei muri sulle sagome vere;
- B-3 le forature spente di base;
- B-4 le lunghezze dalla pianta al grafo, in un passaggio solo;
- B-5 il confronto con grafo e distinta non cambia il foglio.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.modello import ErroreDellaPianta, Fluido, carica_pianta
from disegnatore_mep.pianta.scritte import misura
from disegnatore_mep.pianta.tavola import (
    COLONNE_DELLE_TRATTE,
    CORPO_COLONNA_PT,
    LAYER_MURI,
    Area,
    nome_corto_del_fluido,
    pezzi_dei_muri,
)

from .conftest import CASI

SAGOME = CASI["sagome"]


def _variante(sorgente: Path, cartella: Path, cambia: Any, nome: str = "variante.json") -> Path:
    dati = json.loads(sorgente.read_text(encoding="utf-8"))
    cambia(dati)
    cartella.mkdir(parents=True, exist_ok=True)
    percorso = cartella / nome
    percorso.write_text(json.dumps(dati, ensure_ascii=False, indent=2), encoding="utf-8")
    return percorso


def _aree_dei_muri(esito_o_tavola: Any) -> list[Area]:
    tavola = getattr(esito_o_tavola, "tavola", esito_o_tavola)
    return [p for p in tavola.primitive if isinstance(p, Area) and p.layer == LAYER_MURI]

# --- B-1. il nome corto dei fluidi idronici ---------------------------------------------------


@pytest.mark.parametrize("fluido", Fluido.__args__)  # type: ignore[attr-defined]
def test_il_nome_del_fluido_sta_nella_sua_colonna(fluido: str) -> None:
    """BD.RM.260: «Acqua di riscaldamento» finiva sopra la colonna «Da»."""
    x = {titolo: x for titolo, x, _ in COLONNE_DELLE_TRATTE}
    larghezza = misura(nome_corto_del_fluido(fluido), CORPO_COLONNA_PT, False)[0]
    assert larghezza <= x["Da"] - x["Fluido"] - 1.0, (fluido, nome_corto_del_fluido(fluido), larghezza)


def test_i_nomi_corti_degli_idronici() -> None:
    assert nome_corto_del_fluido("heating_water") == "Acqua risc."
    assert nome_corto_del_fluido("domestic_hot_water") == "ACS"
    assert nome_corto_del_fluido("cold_water") == "AFS"
    assert nome_corto_del_fluido("supply_air") == "Aria di mandata"


# --- B-2. il retino dei muri sulle sagome vere ------------------------------------------------


def test_con_le_sagome_il_retino_sta_sulle_sagome(esiti: dict[str, Esito]) -> None:
    """Un'area per sagoma, con i suoi vertici: nessun rettangolo asse-spessore."""
    esito = esiti["sagome"]
    aree = _aree_dei_muri(esito)
    assert len(aree) == len(esito.pianta.sagome_muri) == 17
    ox, oy, xmin, ymin, k = esito.tavola.trasforma
    for area, sagoma in zip(aree, esito.pianta.sagome_muri, strict=True):
        in_metri = [v for x, y in area.punti for v in ((x - ox) / k + xmin, (y - oy) / k + ymin)]
        assert in_metri == pytest.approx([v for q in sagoma for v in q], abs=1e-3)
    # La tramezza a L e' un poligono solo, di sei vertici.
    assert max(len(a.punti) for a in aree) == 6


def test_senza_le_sagome_il_retino_e_quello_di_sempre(tmp_path: Path, esiti: dict[str, Esito]) -> None:
    """Senza `sagome_muri`, un rettangolo per tratto pieno di muro, come prima; e il
    percorso dei tracciati e' lo stesso: l'instradatore conosce i muri, non le sagome."""
    senza = _variante(SAGOME, tmp_path, lambda d: d.pop("sagome_muri"))
    esito = disegna_la_pianta(senza, tmp_path / "out", None, dxf=False, png=False)
    assert len(_aree_dei_muri(esito)) == len(pezzi_dei_muri(esito.pianta))
    con = esiti["sagome"]
    assert [p.punti for p in esito.percorsi] == [p.punti for p in con.percorsi]
    assert [lu.misurata_m for lu in esito.lunghezze] == [lu.misurata_m for lu in con.lunghezze]


def test_con_le_sagome_gli_ingombri_restano_i_muri(esiti: dict[str, Esito]) -> None:
    """Le scritte e i controlli misurano ancora i muri asse-spessore."""
    esito = esiti["sagome"]
    muri = {di for di, _ in esito.tavola.rettangoli if di.startswith("muro ")}
    assert muri == {f"muro {m.id}" for m in esito.pianta.muri}
    assert esito.rilievi.bloccanti == []


def test_nel_dettaglio_le_sagome_si_ritagliano(esiti: dict[str, Esito]) -> None:
    """Il riquadro A prende l'angolo della tramezza a L: le sagome che ci cadono si
    ritagliano sulla zona, e niente esce dalla cornice."""
    esito = esiti["sagome"]
    (dettaglio,) = esito.dettagli or []
    assert esito.pianta.dettagli
    x0, y0, x1, y1 = esito.pianta.dettagli[0].rettangolo
    ox, oy, xmin, ymin, k = dettaglio.trasforma
    aree = _aree_dei_muri(dettaglio)
    assert aree
    for area in aree:
        for x, y in area.punti:
            xm, ym = (x - ox) / k + xmin, (y - oy) / k + ymin
            assert x0 - 1e-3 <= xm <= x1 + 1e-3 and y0 - 1e-3 <= ym <= y1 + 1e-3
    # La L intera sta nel riquadro: si ritrova con i suoi sei vertici.
    assert any(len(a.punti) == 6 for a in aree)


def test_nel_dxf_le_sagome_sono_campiture_sul_layer_dei_muri(esiti: dict[str, Esito]) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    esito = esiti["sagome"]
    dxf = next(p for p in esito.file if p.name == "sagome-muri.dxf")
    documento = ezdxf.readfile(dxf)
    campiture = [h for h in documento.modelspace().query("HATCH") if h.dxf.layer == LAYER_MURI]
    assert len(campiture) == len(esito.pianta.sagome_muri)
    vertici = sorted(len(h.paths[0].vertices) for h in campiture)
    assert vertici == sorted(len(s) for s in esito.pianta.sagome_muri)


def test_una_sagoma_vuole_tre_punti(tmp_path: Path) -> None:
    rotta = _variante(SAGOME, tmp_path, lambda d: d["sagome_muri"].append([[0.0, 0.0], [1.0, 0.0]]))
    with pytest.raises(ErroreDellaPianta, match="sagome_muri"):
        carica_pianta(rotta)


def test_muri_visibili_non_c_e(tmp_path: Path) -> None:
    """Il campo della copia della commessa (`sfondo.muri_visibili`) era un residuo
    della rev02 e non entra (LEGGIMI B4)."""
    rotta = _variante(CASI["corridoio"], tmp_path, lambda d: d["sfondo"].update(muri_visibili=False))
    with pytest.raises(ErroreDellaPianta, match="muri_visibili"):
        carica_pianta(rotta)
