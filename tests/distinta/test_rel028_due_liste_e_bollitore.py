"""REL-028, punti 2a e 2b: le due liste materiali e il bollitore col serpentino.

- **2a** (I-314, D-241): la lista prezzata (CAPEX) prezza anche le apparecchiature, comprese
  quelle fornite da Nove C; la lista senza prezzi per il fornitore le tiene con «fornita da Nove
  C», o le toglie con `--senza-nove-c`.
- **2b** (I-315, I-321, I-323): la superficie del serpentino nel grafo, nella tabella delle
  apparecchiature, nella voce della lista (dal manuale Shenling §2.3), nel listino; un bollitore
  sotto il minimo e' uno scostamento nel confronto; il tubo oltre i 5 m e' un avviso.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.costo import costo_in_markdown, prezza_la_distinta
from disegnatore_mep.distinta.documento import documento_della_lista, tutti_i_testi
from disegnatore_mep.distinta.listino import leggi_il_listino
from disegnatore_mep.distinta.ordine import ordine_della_minuteria
from disegnatore_mep.graphics.tabella import dati_idronici
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import ROOT

LISTINO = ROOT / "skill" / "distinta" / "LISTINO-MINUTERIA.md"


def _tubo(ident: str, a: tuple[str, str], b: tuple[str, str], **proprieta: Any) -> dict[str, Any]:
    return {
        "id": ident, "network_id": "primario",
        "endpoint_a": {"component_id": a[0], "port_id": a[1]},
        "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        "properties": proprieta,
    }


def _impianto(marca: str = "Shenling", superficie: float | None = None, metri: float = 2.0) -> dict[str, Any]:
    """Una pompa di calore che scalda un bollitore da 200 l con la sua acqua di riscaldamento."""
    bollitore: dict[str, Any] = {"volume_l": 200, "marca": "Cordivari", "modello": "Bolly 1 XL WB 200"}
    if superficie is not None:
        bollitore["superficie_scambio_m2"] = superficie
    return {
        "schema_version": "1",
        "metadata": {"project_name": "Prova del bollitore"},
        "distinta": {"tubi": [{"rete": "primario", "tubo": "MS 32×3", "metri": 6, "isolamento": "guaina 19 mm"}]},
        "networks": [{"id": "primario", "name": "Circuito del bollitore", "domain": "hydronic",
                      "medium": "heating_water"}],
        "components": [
            {"id": "pdc", "definition_id": "heat-pump-air-water", "tag": "PDC-01",
             "properties": {"marca": marca, "modello": "ThermaX R290", "power_kw": 12}},
            {"id": "bol", "definition_id": "dhw-cylinder", "tag": "BOL-01", "properties": bollitore},
        ],
        "connections": [
            _tubo("m", ("pdc", "water_supply"), ("bol", "coil_in"), lunghezza_m=metri, sezione="MS 32×3"),
            _tubo("r", ("bol", "coil_out"), ("pdc", "water_return"), lunghezza_m=metri, sezione="MS 32×3"),
        ],
    }


@pytest.fixture(scope="module")
def listino() -> Any:
    return leggi_il_listino(LISTINO)


def _bollitore(distinta: Any) -> Any:
    return next(v for v in distinta.voci if v.testo.startswith("Bollitore ACS"))


# --- 2b: il serpentino ---------------------------------------------------------------------


def test_la_voce_del_bollitore_dice_il_serpentino_minimo_della_shenling(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_impianto(), regole, *nomi)
    voce = _bollitore(distinta)
    assert voce.testo == (
        "Bollitore ACS: Cordivari Bolly 1 XL WB 200 — 200 l, a serpentino maggiorato per pompa di calore, "
        "superficie di scambio non minore di 2,5 m²"
    )
    assert "Shenling 12 kW, serpentina smaltata, manuale §2.3" in voce.note
    assert voce.superficie_minima_m2 == 2.5 and not voce.da_definire


def test_il_serpentino_inox_e_le_taglie_piccole(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    grafo = _impianto()
    grafo["components"][1]["properties"]["serpentino"] = "inox"
    assert _bollitore(componi_la_distinta(grafo, regole, *nomi)).superficie_minima_m2 == 1.6
    grafo = _impianto()
    grafo["components"][0]["properties"]["power_kw"] = 9
    assert _bollitore(componi_la_distinta(grafo, regole, *nomi)).superficie_minima_m2 == 2.0


def test_una_pompa_di_calore_che_non_e_shenling_fa_una_domanda(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_impianto(marca="Haier"), regole, *nomi)
    voce = _bollitore(distinta)
    assert "superficie di scambio non minore di DA DEFINIRE m²" in voce.testo
    assert voce.da_definire and any("superficie minima del serpentino" in d for d in distinta.domande)
    assert any(m.dato == "superficie_minima_scambio_m2" and m.chi == "BOL-01" for m in distinta.mancanti)
    # Il minimo lo puo' dare il progettista (o il PO) sul bollitore: non si inventa.
    grafo = _impianto(marca="Haier")
    grafo["components"][1]["properties"]["superficie_minima_scambio_m2"] = 1.8
    voce = _bollitore(componi_la_distinta(grafo, regole, *nomi))
    assert voce.testo.endswith("non minore di 1,8 m²") and not voce.da_definire


def test_un_bollitore_senza_pompa_di_calore_non_cambia(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    grafo = _impianto()
    grafo["components"][0]["definition_id"] = "gas-boiler"
    voce = _bollitore(componi_la_distinta(grafo, regole, *nomi))
    assert voce.testo == "Bollitore ACS: Cordivari Bolly 1 XL WB 200" and voce.superficie_minima_m2 is None


def test_il_serpentino_piccolo_e_il_tubo_lungo_sono_avvisi(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_impianto(superficie=0.8, metri=6), regole, *nomi)
    avvisi = "\n".join(distinta.avvisi)
    assert "BOL-01: serpentino 0,8 m², sotto il minimo di 2,5 m²" in avvisi
    assert "BOL-01: 6 m di tubo dalla pompa di calore PDC-01" in avvisi and "sotto i 5 m" in avvisi
    assert "serpentino del bollitore scelto 0,8 m²" in _bollitore(distinta).note
    giusto = componi_la_distinta(_impianto(superficie=2.5, metri=2), regole, *nomi)
    assert not [a for a in giusto.avvisi if "BOL-01" in a]


def test_la_superficie_va_nella_tabella_delle_apparecchiature() -> None:
    assert dati_idronici(("dhw_storage",), {"volume_l": 200, "superficie_scambio_m2": 2.5}) == ["200 l", "serpentino 2,5 m²"]


def test_il_listino_dice_il_serpentino_e_il_confronto_lo_usa(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    righe = {v.fornitore: v for v in listino.righe["M10b"]}
    assert righe["Abbattista"].superficie_m2 == 2.0 and righe["Idrosanitaria"].superficie_m2 == 0.8
    costo = prezza_la_distinta(componi_la_distinta(_impianto(), regole, *nomi), listino)
    riga = next(r for r in costo.righe if r.testo.startswith("Bollitore ACS"))
    # Tutti e due sotto i 2,5 m² della 12 kW: il conto prende il meno caro e lo avvisa.
    assert riga.prezzata and "sotto il minimo di 2,5 m²" in riga.conto
    ordine = ordine_della_minuteria(costo)
    bollitore = next(r for r in ordine.righe if r.codice == "M10b")
    assert {v.fornitore for v in bollitore.avvisi} == {"Idrosanitaria"}
    # Con la 9 kW (2,0 m²) il bollitore di Abbattista rispetta la voce, e vince anche se costa di piu'.
    grafo = _impianto()
    grafo["components"][0]["properties"]["power_kw"] = 9
    ordine = ordine_della_minuteria(prezza_la_distinta(componi_la_distinta(grafo, regole, *nomi), listino))
    bollitore = next(r for r in ordine.righe if r.codice == "M10b")
    assert bollitore.scelta is not None and bollitore.scelta.fornitore == "Abbattista"
    assert [v.fornitore for v in bollitore.avvisi] == ["Idrosanitaria"]


# --- 2a: le due liste ----------------------------------------------------------------------


def test_la_lista_prezzata_prezza_anche_le_apparecchiature_di_nove_c(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    distinta = componi_la_distinta(_impianto(), regole, *nomi)
    assert {v.fornitura for v in distinta.voci_della_sezione("A")} == {"Nove C"}
    costo = prezza_la_distinta(distinta, listino)
    apparecchiature = {r.testo.split(":")[0]: r for r in costo.righe if r.sezione == "A"}
    assert set(apparecchiature) == {"Pompa di calore aria-acqua", "Bollitore ACS"}
    # La Shenling 12 kW ha nel listino solo la Haier di Idrosanitaria: la prende, e la avvisa.
    pompa = apparecchiature["Pompa di calore aria-acqua"]
    assert pompa.prezzata and "Haier" in pompa.conto and "fornita da Nove C" in pompa.nota
    md = costo_in_markdown(costo, {})
    assert "Lista materiali prezzata (CAPEX)" in md and "anche quelle fornite da Nove C" in md


def test_una_macchina_senza_codice_e_da_prezzare(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    grafo = _impianto()
    grafo["components"][0]["properties"]["power_kw"] = 6
    costo = prezza_la_distinta(componi_la_distinta(grafo, regole, *nomi), listino)
    pompa = next(r for r in costo.righe if r.testo.startswith("Pompa di calore"))
    assert not pompa.prezzata and "Shenling 6" in pompa.manca


def test_le_voci_del_committente_restano_fuori(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    from disegnatore_mep.distinta.regole import la_fornitura

    distinta = componi_la_distinta(
        _impianto(), regole, *nomi, fornitura=la_fornitura(regole, "apparecchiature=committente")
    )
    costo = prezza_la_distinta(distinta, listino)
    assert not [r for r in costo.righe if r.sezione == "A"]


def test_la_lista_per_il_fornitore_dice_fornita_da_nove_c_o_le_toglie(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_impianto(), regole, *nomi)
    testi = "\n".join(tutti_i_testi(documento_della_lista(distinta)))
    assert "fornita da Nove C: non si quota" in testi
    assert "superficie di scambio non minore di 2,5 m²" in testi
    assert "€" not in testi
    senza = "\n".join(tutti_i_testi(documento_della_lista(distinta, senza_nove_c=True)))
    assert "Bollitore ACS" not in senza and "Pompa di calore aria-acqua" not in senza
    assert "Le voci fornite da Nove C non sono in questa lista" in senza


def test_il_comando_ha_l_opzione_senza_nove_c(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(json.dumps(_impianto(), ensure_ascii=False), encoding="utf-8")
    main(["distinta", str(grafo), "--out", str(tmp_path / "d"), "--lista", "--senza-nove-c"],
         cartelle_del_repository(ROOT))
    capsys.readouterr()
    documento = next((tmp_path / "d").glob("Lista_*.md")).read_text(encoding="utf-8")
    assert "Bollitore ACS" not in documento and "non sono in questa lista" in documento
    codice = main(["distinta", str(grafo), "--out", str(tmp_path / "e"), "--senza-nove-c"], cartelle_del_repository(ROOT))
    assert codice == 1 and "--senza-nove-c vale con --lista" in capsys.readouterr().err
