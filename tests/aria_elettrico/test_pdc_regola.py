"""La pompa di calore che regola da se' (REL-015 punto 4, I-230).

Il PO, sulle tavole della 1.6.0: «anche la pdc va alimentata ovviamente poi ci sono le sonde
della psc che vanno nei bollitori e volano ecc. comunque nel manuale Shenling c'e' tutto».

Quattro cose:

1. **le porte di comando della pompa di calore con la regolazione a bordo** — ingressi delle
   sonde e del termostato, uscite verso valvole e circolatori, comando a filo —, con nomi
   generici, facoltative, uguali sulle due voci (la domestica e quella di alta potenza);
2. **non collegate non cambiano niente**: una tavola che usa della pompa di calore solo
   alimentazione e bus (il collaudo T2 rifatto) esce identica a quella disegnata con la
   pompa di calore di prima, che aveva solo quelle due; il banco di REL-011 lo misura sulle
   24 tavole idroniche;
3. **la villetta del collaudo T2 con la regolazione a bordo** (`docs/collaudi/REL-015/
   pdc-regola/`) si valida e si disegna pulita: le sonde e i comandi vanno alla macchina, non
   c'e' un regolatore esterno, zero bloccanti e zero tratte cedute sulle due tavole; ogni
   circolatore passa da un relè d'appoggio da 10 A (D-228, I-259), mai dalla morsettiera;
4. **le istruzioni** di Capire e Comporre lo dicono.
"""
# categoria: difende il motore

import json
from dataclasses import replace
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.types import Domain, IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.vista import vista_del_grafo
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"
T2_RIFATTO = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t2" / "dopo"
CAPIRE = ROOT / "skill" / "capire" / "ISTRUZIONI.md"
COMPORRE = ROOT / "skill" / "comporre" / "ISTRUZIONI.md"

POMPE_DI_CALORE = ("heat-pump-air-water", "heat-pump-air-water-large")
RELE_DEI_CIRCOLATORI = {
    "circ-radiatori": "rele-radiatori",
    "circ-pannelli": "rele-pannelli",
    "circ-ricircolo": "rele-ricircolo",
}
"""Il relè d'appoggio di ogni circolatore della villetta (D-228)."""
INGRESSI = ("sonda_acs", "sonda_accumulo", "sonda_zona_2", "termostato")
USCITE = (
    "out_acs",
    "out_miscelatrice",
    "out_pompa_zona_1",
    "out_pompa_zona_2",
    "out_pompa_ricircolo",
    "out_ausiliario",
)
DI_PRIMA = {"power", "bus"}


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def tavola(cartella: Path, vista: str) -> EsitoDelPiano:
    esito = esegui_piano(
        load_project(cartella / "grafo-completo.json"),
        carica_piano(cartella / f"piano-{vista}.json"),
        catalogo(),
        simboli(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    return esito


# --- 1. le porte ------------------------------------------------------------------------


@pytest.mark.parametrize("voce", POMPE_DI_CALORE)
def test_la_pompa_di_calore_ha_ingressi_uscite_e_comando_a_filo(voce: str) -> None:
    intere = ComponentRegistry.from_directory(CATALOG)
    porte = {porta.id: porta for porta in intere.get(voce).ports}
    attese = {*DI_PRIMA, "comando_a_filo", *INGRESSI, *USCITE}
    assert catalogo().porte_di_comando(voce) == attese
    for nome in attese:
        assert porte[nome].domain is Domain.CONTROL, nome
        assert porte[nome].required is False, nome
    # Le sonde e il termostato entrano come nel regolatore; le uscite sono a 230 V come le
    # sue, e prendono il comando di una valvola o di un circolatore.
    for nome in INGRESSI:
        assert (porte[nome].medium, porte[nome].flow.value) == ("control_bus", "in"), nome
    for nome in USCITE:
        assert (porte[nome].medium, porte[nome].flow.value) == ("power_supply", "out"), nome
    assert porte["comando_a_filo"].medium == "control_bus"


@pytest.mark.parametrize("voce", POMPE_DI_CALORE)
def test_le_porte_stanno_sulle_facce_libere_dall_acqua(voce: str) -> None:
    """Gli ingressi a sinistra, le uscite sopra, il comando a filo sotto; alimentazione e
    bus dove stavano. L'acqua resta sola sul fianco destro."""
    manifesto = simboli().get(voce).manifest
    faccia = {porta.id: porta.face.value for porta in manifesto.control_ports}
    assert {faccia[nome] for nome in INGRESSI} == {"left"}
    assert {faccia[nome] for nome in USCITE} == {"top"}
    assert faccia["comando_a_filo"] == faccia["power"] == faccia["bus"] == "bottom"
    assert (manifesto.port("power").x_mm, manifesto.port("bus").x_mm) == (10.0, 20.0)
    assert {porta.face.value for porta in manifesto.ports} == {"right"}
    # Ogni porta di comando ha il moncone su cui il cavo finisce (collaudo T2, §3.2).
    marcato = simboli().get(voce).monconi_di_comando
    assert set(faccia) <= marcato


def test_i_nomi_sono_generici() -> None:
    """La sigla del costruttore sta nella fonte della voce, non nel nome della porta."""
    voce = ComponentRegistry.from_directory(CATALOG).get("heat-pump-air-water")
    for porta in voce.ports:
        assert not any(sigla in porta.id.upper() for sigla in ("T_DHW", "T_BT", "SV1", "P_C", "CN"))
    fonte = " ".join(voce.sources)
    assert "T_DHW" in fonte and "§5.3" in fonte


# --- 2. non collegate non cambiano niente ------------------------------------------------


def _con_la_pompa_di_calore_di_prima() -> tuple[ComponentRegistry, SymbolRegistry]:
    """Il catalogo e la libreria con la pompa di calore com'era: solo alimentazione e bus."""
    libreria = SymbolRegistry(
        [
            replace(
                item,
                manifest=item.manifest.model_copy(
                    update={"control_ports": [p for p in item.manifest.control_ports if p.id in DI_PRIMA]}
                ),
            )
            if item.manifest.id in POMPE_DI_CALORE
            else item
            for item in simboli().all()
        ]
    )
    intere = ComponentRegistry.from_directory(CATALOG)
    voci = [
        voce.model_copy(
            update={
                "ports": [
                    p for p in voce.ports if p.domain is not Domain.CONTROL or p.id in DI_PRIMA
                ]
            }
        )
        if voce.id in POMPE_DI_CALORE
        else voce
        for voce in intere.all()
    ]
    return ComponentRegistry(voci, libreria), libreria


@pytest.mark.parametrize("vista", ["idraulica", "elettrico"])
def test_alimentazione_e_bus_soli_disegnano_come_prima(vista: str) -> None:
    """Il collaudo T2 rifatto usa della pompa di calore alimentazione e bus: la tavola con
    le porte nuove e' quella con la pompa di calore di prima, geometria e rilievi."""
    grafo = load_project(T2_RIFATTO / "grafo-completo.json")
    piano = carica_piano(T2_RIFATTO / f"piano-{vista}.json")
    oggi = esegui_piano(grafo, piano, catalogo(), simboli(), NAMING)
    vecchio_catalogo, vecchia_libreria = _con_la_pompa_di_calore_di_prima()
    prima = esegui_piano(grafo, piano, vecchio_catalogo, vecchia_libreria, NAMING)
    assert oggi.disegno is not None and prima.disegno is not None
    assert oggi.disegno.model_dump_json() == prima.disegno.model_dump_json()
    assert [item.message for item in oggi.rilievi] == [item.message for item in prima.rilievi]


# --- 3. la villetta con la regolazione a bordo -------------------------------------------


def test_la_villetta_si_valida() -> None:
    for nome in ("grafo.json", "grafo-completo.json"):
        grafo = load_project(VILLETTA / nome)
        rilievi = validate_project(grafo, catalogo().per_il_progetto(grafo))
        bloccanti = [item for item in rilievi.issues if item.severity is IssueSeverity.BLOCKING]
        assert not bloccanti, (nome, [item.message for item in bloccanti])


def test_sonde_e_comandi_vanno_alla_pompa_di_calore() -> None:
    grafo = load_project(VILLETTA / "grafo-completo.json")
    voci = {item.id: item.definition_id for item in grafo.components}
    assert "plant-controller" not in voci.values()
    assert "outdoor-temperature-probe" not in voci.values()
    cavi = {
        frozenset({(t.endpoint_a.component_id, t.endpoint_a.port_id), (t.endpoint_b.component_id, t.endpoint_b.port_id)})
        for t in grafo.connections
    }
    attesi = {
        (("sonda-bollitore", "signal"), ("pdc", "sonda_acs")),
        (("sonda-volano", "signal"), ("pdc", "sonda_accumulo")),
        (("sonda-pannelli", "signal"), ("pdc", "sonda_zona_2")),
        (("pdc", "out_acs"), ("deviatrice", "comando")),
        (("pdc", "out_miscelatrice"), ("miscelatrice", "comando")),
        (("pdc", "out_pompa_zona_1"), ("rele-radiatori", "bobina")),
        (("pdc", "out_pompa_zona_2"), ("rele-pannelli", "bobina")),
        (("pdc", "out_pompa_ricircolo"), ("rele-ricircolo", "bobina")),
        (("comando-a-filo", "a"), ("pdc", "comando_a_filo")),
        (("sez-pdc", "b"), ("pdc", "power")),
    }
    for a, b in attesi:
        assert frozenset({a, b}) in cavi, (a, b)
    # Le sonde del volano e del bollitore sono sui loro attacchi.
    assert frozenset({("volano", "probe"), ("sonda-volano", "a")}) in cavi
    assert frozenset({("bollitore", "probe"), ("sonda-bollitore", "a")}) in cavi
    # **Il relè d'appoggio** (D-228, I-259, il PO: «non alimentiamo mai il circolatore diretto
    # da pdc ma attraverso contattore con Relè di appoggio da 10 A»): l'uscita della macchina
    # va alla bobina, il quadro all'ingresso del contatto, e il contatto al `power` del
    # circolatore. Il `comando` del circolatore resta libero.
    for circolatore, rele in RELE_DEI_CIRCOLATORI.items():
        assert voci[rele] == "interface-relay", rele
        assert frozenset({(rele, "b"), (circolatore, "power")}) in cavi, circolatore
        assert any((rele, "a") in cavo and any(capo[0] == "quadro" for capo in cavo) for cavo in cavi), rele
        assert not any((circolatore, "comando") in cavo for cavo in cavi), circolatore
    # Dal quadro: la pompa di calore, col sezionatore, e i tre relè, ciascuno dalla sua uscita.
    dal_quadro = {
        next(capo for capo in cavo if capo[0] != "quadro"): next(capo[1] for capo in cavo if capo[0] == "quadro")
        for cavo in cavi
        if any(capo[0] == "quadro" for capo in cavo)
    }
    assert set(dal_quadro) == {("sez-pdc", "a"), *((rele, "a") for rele in RELE_DEI_CIRCOLATORI.values())}
    assert len(set(dal_quadro.values())) == len(dal_quadro)


def test_nessun_circolatore_e_alimentato_direttamente_dalla_pompa_di_calore() -> None:
    """D-228: il `power` di un circolatore non e' mai collegato a un'uscita della pompa di
    calore, nel grafo della villetta e nel suo grafo completo. Lo alimenta il contatto di un
    relè d'appoggio, una voce `interface-relay`, la cui bobina e' comandata dalla macchina."""
    for nome in ("grafo.json", "grafo-completo.json"):
        grafo = load_project(VILLETTA / nome)
        voci = {item.id: item.definition_id for item in grafo.components}
        circolatori = {ident for ident, voce in voci.items() if voce.startswith("pump-circulator")}
        assert circolatori, nome
        for tubazione in grafo.connections:
            capi = {
                (tubazione.endpoint_a.component_id, tubazione.endpoint_a.port_id),
                (tubazione.endpoint_b.component_id, tubazione.endpoint_b.port_id),
            }
            alimentati = {ident for ident, porta in capi if ident in circolatori and porta == "power"}
            if not alimentati:
                continue
            altro = next(ident for ident, _ in capi if ident not in alimentati)
            assert voci[altro] == "interface-relay", (nome, tubazione.id, altro)
        # E ogni relè ha la bobina sulla macchina.
        bobine = {
            frozenset(
                {
                    (t.endpoint_a.component_id, t.endpoint_a.port_id),
                    (t.endpoint_b.component_id, t.endpoint_b.port_id),
                }
            )
            for t in grafo.connections
        }
        for rele in (ident for ident, voce in voci.items() if voce == "interface-relay"):
            assert any(
                (rele, "bobina") in cavo and any(capo[0] == "pdc" for capo in cavo) for cavo in bobine
            ), (nome, rele)


@pytest.mark.parametrize("vista", ["idraulica", "elettrico"])
def test_le_due_tavole_della_villetta_escono_pulite(vista: str) -> None:
    esito = tavola(VILLETTA, vista)
    bloccanti = [item for item in esito.rilievi if item.severity is IssueSeverity.BLOCKING]
    assert not bloccanti, [item.message for item in bloccanti]
    assert not esito.cedute


def test_sulla_tavola_dell_elettrico_si_legge_che_cosa_misura_ogni_sonda() -> None:
    """Tre sonde uguali: la sigla e la scritta del pezzo dicono quale cavo va al bollitore,
    quale al volano, quale alla mandata dei pannelli."""
    grafo = load_project(VILLETTA / "grafo-completo.json")
    vista, _ = vista_del_grafo(grafo, "elettrico", catalogo(), NAMING)
    pezzi = {item.id: item for item in vista.components}
    assert {"pdc", "quadro", "sez-pdc", "comando-a-filo", "deviatrice", "miscelatrice"} <= set(pezzi)
    scritte = {
        pezzo: pezzi[pezzo].properties.get("etichetta")
        for pezzo in ("sonda-bollitore", "sonda-volano", "sonda-pannelli")
    }
    assert scritte == {
        "sonda-bollitore": "bollitore",
        "sonda-volano": "volano",
        "sonda-pannelli": "mandata pannelli",
    }
    foglio = tavola(VILLETTA, "elettrico").disegno.sheets[0]  # type: ignore[union-attr]
    testi = {label.text for label in foglio.labels}
    assert {"bollitore", "volano", "mandata pannelli"} <= testi
    # Le sigle dei pezzi col cavo: tre sonde, deviatrice, miscelatrice (collaudo T2, §3.1).
    assert {"SO-01", "SO-02", "SO-03", "VD-01", "VMR-01"} <= testi


# --- 4. le istruzioni ----------------------------------------------------------------------


def test_capire_dice_chi_regola() -> None:
    testo = CAPIRE.read_text(encoding="utf-8")
    for parola in ("sonda_acs", "sonda_accumulo", "out_acs", "regolazione a bordo", "regola la pompa di calore"):
        assert parola in testo, parola


def test_comporre_dice_come_si_posa_l_elettrico_attorno_alla_pompa_di_calore() -> None:
    testo = COMPORRE.read_text(encoding="utf-8")
    assert "la pompa di calore al centro" in testo.lower()


def test_capire_dice_che_il_circolatore_passa_dal_rele() -> None:
    """D-228 sostituisce D-215 per i circolatori: Capire scrive i tre cavi del relè, e non piu'
    il cavo solo dalla morsettiera al `power` del circolatore."""
    testo = CAPIRE.read_text(encoding="utf-8")
    for parola in ("D-228", "interface-relay", "`bobina`", "relè d'appoggio da 10 A"):
        assert parola in testo, parola
    assert "prende alimentazione e comando dalla sua morsettiera" not in testo


def test_comporre_dice_dove_si_posano_i_rele() -> None:
    testo = COMPORRE.read_text(encoding="utf-8").lower()
    assert "i relè d'appoggio in colonna" in testo
    assert "sta sopra il suo relè" in testo


def test_il_rele_d_appoggio_e_una_voce_del_comando() -> None:
    """La voce `interface-relay`: tre attacchi a 230 V, tutti del comando e obbligatori, un
    simbolo che il piano posa (non in linea), la famiglia KA e il corredo passante."""
    voce = catalogo().resolve("interface-relay")
    assert voce.definition.name == "Relè d'appoggio 10 A"
    assert list(voce.definition.functions) == ["power_switching"]
    porte = {porta.id: porta for porta in voce.definition.ports}
    assert set(porte) == {"bobina", "a", "b"}
    assert all(porta.domain is Domain.CONTROL and porta.required for porta in porte.values())
    assert {str(porta.medium) for porta in porte.values()} == {"power_supply"}
    assert [str(porte[ident].flow) for ident in ("bobina", "a", "b")] == ["in", "in", "out"]
    assert not voce.is_inline
    famiglie = json.loads((NAMING / "families.json").read_text(encoding="utf-8"))["families"]
    assert {"function": "power_switching", "prefix": "KA", "name": "Relè d'appoggio"} in famiglie
    corredo = json.loads((ROOT / "rules" / "distinta" / "corredo.json").read_text(encoding="utf-8"))
    rele = corredo["voci"]["interface-relay"]
    assert rele["passante"] is True
    assert [(item["sezione"], item["um"]) for item in rele["voci"]] == [("E", "n")]
