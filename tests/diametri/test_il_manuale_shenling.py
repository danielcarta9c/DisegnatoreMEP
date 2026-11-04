"""I numeri del manuale Shenling che la skill controlla (REL-011, D-223, D-226, I-281)."""

import json
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.costruttori import (
    avvisi_del_costruttore,
    dati_del_modello,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ComponentInstance

ROOT = Path(__file__).resolve().parents[2]
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json"


def _catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )


def _pdc(potenza: float, marca: str = "Shenling") -> ComponentInstance:
    return ComponentInstance(
        id="gt-01", definition_id="heat-pump-air-water", properties={"power_kw": potenza, "marca": marca}
    )


def test_l_attacco_in_pollici() -> None:
    """L'attacco non e' piu' un DN minimo (I-281, che supera D-223 punto 1): e' il
    pollice della macchina, con cui si dice la riduzione."""
    attacco_6 = dati_del_modello(_pdc(6))
    attacco_15 = dati_del_modello(_pdc(15))
    assert attacco_6 is not None and attacco_6.attacco == '1"'
    assert attacco_15 is not None and attacco_15.attacco == '1¼"'
    assert dati_del_modello(_pdc(15, "Daikin")) is None
    assert dati_del_modello(_pdc(11)) is None, "una taglia che il manuale non ha non si indovina"
    assert attacco_15.prevalenza_indicativa_m == 8.0, "il valore basso degli «8/9 metri» del PO (I-281)"


def test_sul_caso_reale_i_volani_bastano() -> None:
    """Quattro unita' da 15 kW su 1000 l (minimo 160) e due su 200 l (minimo 80)."""
    assert avvisi_del_costruttore(load_project(CASO), _catalogo()) == []


def test_il_volano_piccolo_si_segnala(tmp_path: Path) -> None:
    dati = json.loads(CASO.read_text(encoding="utf-8"))
    for pezzo in dati["components"]:
        if pezzo["properties"].get("volume_l") == 200:
            pezzo["properties"]["volume_l"] = 50
    (tmp_path / "g.json").write_text(json.dumps(dati), encoding="utf-8")
    avvisi = avvisi_del_costruttore(load_project(tmp_path / "g.json"), _catalogo())
    assert len(avvisi) == 1 and "50 l" in avvisi[0] and "almeno 80" in avvisi[0]


def test_la_portata_fuori_campo_si_segnala(tmp_path: Path) -> None:
    dati = json.loads(CASO.read_text(encoding="utf-8"))
    for pezzo in dati["components"]:
        if pezzo["properties"].get("power_kw") == 15:
            pezzo["properties"]["delta_t_k"] = 3
            break
    (tmp_path / "g.json").write_text(json.dumps(dati), encoding="utf-8")
    avvisi = avvisi_del_costruttore(load_project(tmp_path / "g.json"), _catalogo())
    assert any("fuori dal campo" in a and "4,31 m³/h" in a for a in avvisi), avvisi


def test_il_volano_in_serie_si_segnala() -> None:
    """L'impianto di prova 3 ha una sola pompa di calore con il volano a due attacchi in
    serie sul ritorno: la specifica Nove C non lo ammette (D-226)."""
    from disegnatore_mep.rules.apply import saturate
    from disegnatore_mep.rules.registry import RuleRegistry

    catalogo = _catalogo()
    grafo = load_project(ROOT / "examples" / "prova" / "prova-3-pdc-diretta-pavimento.json")
    completo, _, _ = saturate(grafo, catalogo, RuleRegistry.from_directory(ROOT / "rules" / "hydronic"))
    assert any("due attacchi, in serie" in avviso for avviso in avvisi_del_costruttore(completo, catalogo))
