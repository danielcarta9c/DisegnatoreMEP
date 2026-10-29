"""I fluidi dell'aria, del refrigerante, della condensa, dell'elettrico e del comando
sulla tavola (REL-012, fase 1, punti 1-3).

- **una riga sola in legenda** e lo stesso tratto in qualunque verso;
- **nessuna freccia di flusso** su refrigerante, cavi e bus; le frecce restano su aria
  e condensa (proposta della sessione, `layout.fluidi`: il PO decide sulla tavola);
- **colori ben distinguibili**: sulla M.02 del kit alimentazione e collegamento erano
  due rossi quasi uguali, e qui si misura la distanza fra i colori;
- il gas refrigerante con un tratteggio che si legge anche sul campione corto della
  legenda;
- i layer DXF dell'elettrico e del bus;
- **l'idronico non cambia**: nessun suo fluido e' fra quelli senza verso.
"""

import itertools
from pathlib import Path
from typing import Any

import ezdxf

from disegnatore_mep.graphics.dxf import layer_della_rete, write_dxf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import LEGEND_SWATCH_MM, render_sheet
from disegnatore_mep.layout.fluidi import FLUIDI_SENZA_FRECCIA, FLUIDI_SENZA_VERSO
from disegnatore_mep.layout.geometry import FlowKind
from disegnatore_mep.layout.legend import (
    DEFAULT_STYLE,
    MEDIUM_NAMES,
    MEDIUM_STYLES,
    RECIRCULATION_COLOUR,
    SUPPLY_SHIFT,
    style_for,
)
from disegnatore_mep.model.project import ProjectModel

IDRONICI = ("heating_water", "chilled_water", "domestic_hot_water", "cold_water", "solar_fluid", "natural_gas")
ELETTRICI = ("power_supply", "interconnection", "control_bus")


def _lab(colore: str) -> tuple[float, float, float]:
    """CIELAB (D65) di un colore esadecimale sRGB."""

    def lineare(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lineare(int(colore[i : i + 2], 16) / 255) for i in (1, 3, 5))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def _distanza(primo: str, secondo: str) -> float:
    """ΔE CIE76: sotto 10 due linee sottili si confondono, sopra 25 si distinguono
    senza cercare."""
    return sum((p - q) ** 2 for p, q in zip(_lab(primo), _lab(secondo), strict=True)) ** 0.5


def test_l_idronico_non_e_fra_i_fluidi_senza_verso() -> None:
    assert not set(IDRONICI) & FLUIDI_SENZA_VERSO
    assert not set(IDRONICI) & FLUIDI_SENZA_FRECCIA
    assert FLUIDI_SENZA_FRECCIA <= FLUIDI_SENZA_VERSO
    assert style_for("heating_water", supply=False) != style_for("heating_water", supply=True)


def test_un_fluido_senza_verso_ha_un_tratto_solo() -> None:
    for medium in FLUIDI_SENZA_VERSO:
        assert style_for(medium, supply=False) == style_for(medium, supply=True), medium
        assert medium in MEDIUM_STYLES and medium in MEDIUM_NAMES, medium


def test_l_elettrico_e_il_bus_hanno_colori_che_si_distinguono() -> None:
    """Ognuno dei tre a ΔE >= 25 da ogni altro colore della tavola — mandate, ritorni,
    ricircolo, il nero di una rete senza codifica — e fra loro. Sulla M.02 del kit
    alimentazione e collegamento stavano a 19,7, e l'alimentazione a 8,4 dal rosso del
    riscaldamento; il bus a 7,1 dal blu del ritorno."""
    nuovi = {medium: MEDIUM_STYLES[medium][0] for medium in ELETTRICI}
    altri = {
        colore
        for medium, (colore, _) in MEDIUM_STYLES.items()
        if medium not in ELETTRICI
    } | set(SUPPLY_SHIFT.values()) | {RECIRCULATION_COLOUR, DEFAULT_STYLE[0], "#5d6d7e"}
    for medium, colore in nuovi.items():
        vicino = min(altri, key=lambda altro: _distanza(colore, altro))
        assert _distanza(colore, vicino) >= 25, (medium, colore, vicino, _distanza(colore, vicino))
    for (primo, a), (secondo, b) in itertools.combinations(nuovi.items(), 2):
        assert _distanza(a, b) >= 25, (primo, secondo, _distanza(a, b))
    # E i due rossi del kit erano davvero troppo vicini: la misura li avrebbe fermati.
    assert _distanza("#b03a2e", "#a04000") < 25 and _distanza("#b03a2e", "#c0392b") < 10


def test_ogni_fluido_ha_il_suo_tratto() -> None:
    """Il tratto ripete il colore per la fotocopia in bianco e nero (D-057): i tre
    tratti dell'elettrico e del bus sono diversi fra loro e da ogni altro."""
    tratti = [dash for _, dash in MEDIUM_STYLES.values() if dash != "none"]
    for medium in ELETTRICI:
        assert tratti.count(MEDIUM_STYLES[medium][1]) == 1, medium


def test_il_gas_refrigerante_si_legge_tratteggiato_sul_campione_della_legenda() -> None:
    """Sul campione di 8 mm il tratteggio deve interrompersi almeno due volte: col
    «6 2» di prima si interrompeva una volta sola e il gas si leggeva pieno, come il
    liquido dello stesso viola."""
    pieno, vuoto = (float(item) for item in MEDIUM_STYLES["refrigerant_gas"][1].split())
    assert 2 * (pieno + vuoto) - vuoto <= LEGEND_SWATCH_MM


def test_i_layer_dell_elettrico_e_del_bus() -> None:
    for verso in (True, False):
        assert layer_della_rete("power_supply", verso) == "E-POWR-CIRC"
        assert layer_della_rete("interconnection", verso) == "E-POWR-LINK"
        assert layer_della_rete("control_bus", verso) == "E-CTRL-BUS"
        assert layer_della_rete("return_air", verso) == "M-HVAC-RETN"
        assert layer_della_rete("condensate", verso) == "M-CNDS-PIPE"


def test_sulla_tavola_una_riga_per_fluido_senza_andata_ne_ritorno(tavola: tuple[ProjectModel, Any]) -> None:
    _, esito = tavola
    foglio = esito.disegno.sheets[0]
    righe = [(item.medium, item.name) for item in foglio.network_keys]
    disegnati = {route.medium for route in foglio.routes}
    assert disegnati == {
        "refrigerant_liquid", "refrigerant_gas", "supply_air", "return_air", "condensate", *ELETTRICI
    }
    assert sorted(medium for medium, _ in righe) == sorted(disegnati), "una riga per fluido"
    assert all(nome == MEDIUM_NAMES[medium] for medium, nome in righe), righe
    assert not [nome for _, nome in righe if "— andata" in nome or "— ritorno" in nome]


def test_niente_frecce_su_refrigerante_cavi_e_bus_e_le_frecce_su_aria_e_condensa(
    tavola: tuple[ProjectModel, Any], simboli_aria: SymbolRegistry, tmp_path: Path
) -> None:
    _, esito = tavola
    foglio = esito.disegno.sheets[0]
    for route in foglio.routes:
        if route.medium in FLUIDI_SENZA_FRECCIA:
            assert route.flow_kind is FlowKind.NO_ARROW, route.connection_ids
        else:
            assert route.flow_kind.porta_la_freccia, route.connection_ids
    svg = render_sheet(foglio, esito.frame, simboli_aria)
    colori_con_freccia = {
        frammento.split('fill="')[1].split('"')[0]
        for frammento in svg.split('class="flow-arrow"')[1:]
    }
    assert colori_con_freccia == {
        style_for(medium)[0] for medium in ("supply_air", "return_air", "condensate")
    }
    destinazione = tmp_path / "tavola.dxf"
    write_dxf(foglio, esito.frame, simboli_aria, destinazione)
    documento = ezdxf.readfile(destinazione)
    layer_con_freccia = {
        item.dxf.layer
        for item in documento.modelspace().query("INSERT")
        if item.dxf.name == "NoveC_FlowArrow"
    }
    assert layer_con_freccia == {"M-HVAC-SPLY", "M-HVAC-RETN", "M-CNDS-PIPE"}
    layer = {item.dxf.name: item for item in documento.layers}
    assert {"E-POWR-CIRC", "E-POWR-LINK", "E-CTRL-BUS"} <= set(layer)
    assert layer["E-POWR-CIRC"].description == "Alimentazione elettrica"
