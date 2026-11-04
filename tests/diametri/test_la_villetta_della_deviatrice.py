"""La villetta con la deviatrice dell'ACS e la verifica della prevalenza (I-270).

Il PO, su una commessa reale (villetta, Shenling 12 kW, volano a 4 attacchi, ACS su
deviatrice): «con una deviatrice il calcolo somma i due rami sul ritorno comune (Øi 32
invece di Øi 25 a parita' di portata della PdC); e non verifica le perdite di carico
contro la prevalenza utile della pompa a bordo».

**La somma.** La deviatrice manda l'acqua **o** al volano **o** al serpentino: sul
ritorno comune passa la portata della macchina, non la somma dei rami. Qui lo si misura
sulla villetta di riferimento (`docs/collaudi/REL-015/pdc-regola/`), che ha la stessa
centrale: 12 kW con 5 K sono 2,067 m³/h su **ogni** tratto del primario, ritorno comune
compreso. Sul ritorno comune il DN e' 32 e non 25 **per D-223**, non per una somma:
l'attacco della ThermaX 12 kW e' 1¼", e sul tratto fra la macchina e il collettore il
DN non scende sotto. Senza la marca Shenling lo stesso tratto e' Øi 25 — la portata
della macchina, 1,17 m/s, sotto gli 1,3 del DN 25 —, ed e' la prova che la portata non
e' sommata: sommata (4,13 m³/h) darebbe Øi 32 anche senza il manuale.

**La prevalenza.** Con la prevalenza utile della pompa e le lunghezze dei tratti la
skill verifica il giro piu' costoso; i numeri sono fatti a mano qui sotto.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.calcolatore import portata_da_potenza
from disegnatore_mep.diametri.perdite import (
    MAGGIORAZIONE_CONCENTRATE,
    avvisi_della_prevalenza,
    fattore_d_attrito,
    perdita_distribuita_pa_m,
    verifiche_della_prevalenza,
)
from disegnatore_mep.diametri.tratti import TrattoDelDiametro, tratti_del_diametro
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"

LUNGHEZZE = {"t1": 12.0, "t2": 2.0, "t3": 4.0, "t4": 2.0, "t5": 4.0, "t6": 12.0}
"""Le tubazioni del primario della villetta: pompa di calore → deviatrice 12 m, deviatrice
→ volano 2 m, deviatrice → serpentino 4 m, volano → T 2 m, serpentino → T 4 m, T →
pompa di calore 12 m."""


def _villetta(
    grafo: str = "grafo.json",
    pdc: dict[str, Any] | None = None,
    lunghezze: dict[str, float] | None = None,
    senza: tuple[str, ...] = (),
) -> dict[str, Any]:
    testo: dict[str, Any] = json.loads((VILLETTA / grafo).read_text(encoding="utf-8"))
    for pezzo in testo["components"]:
        if pezzo["id"] == "pdc":
            pezzo["properties"].update({"delta_t_k": 5, **(pdc or {})})
            for chiave in senza:
                pezzo["properties"].pop(chiave, None)
    for tubo in testo["connections"]:
        if lunghezze and tubo["id"] in lunghezze:
            tubo["lunghezza_m"] = lunghezze[tubo["id"]]
    testo["diametri"] = {"reti": ["primario"]}
    return testo


def _modello(testo: dict[str, Any], catalogo: ComponentRegistry) -> tuple[ProjectModel, ComponentRegistry]:
    modello = ProjectModel.model_validate(testo)
    return modello, catalogo.per_il_progetto(modello)


def _tratto(tratti: tuple[TrattoDelDiametro, ...], da: str, a: str) -> TrattoDelDiametro:
    trovati = [t for t in tratti if (t.capi[0].component_id, t.capi[1].component_id) == (da, a)]
    assert len(trovati) == 1, [(t.capi[0].component_id, t.capi[1].component_id) for t in tratti]
    return trovati[0]


@pytest.mark.parametrize("grafo", ["grafo.json", "grafo-completo.json"])
def test_sul_ritorno_comune_passa_la_portata_della_macchina_non_la_somma(
    grafo: str, catalogo: ComponentRegistry
) -> None:
    modello, del_progetto = _modello(_villetta(grafo), catalogo)
    tratti = tratti_del_diametro(modello, del_progetto)
    q = portata_da_potenza(12, 5)
    assert q == pytest.approx(2.067, abs=1e-3)
    primario = [t for t in tratti if t.reti == ("primario",)]
    assert len(primario) == 5
    for tratto in primario:
        assert tratto.portata_m3h == pytest.approx(q), (tratto.capi, tratto.portata_m3h)
    comune = _tratto(tratti, "conf-ritorno-pdc", "pdc")
    assert comune.portata_m3h == pytest.approx(q)
    # Øi 32 e' l'attacco 1¼" della ThermaX 12 kW (D-223), non una somma.
    assert comune.diametro is not None and comune.diametro.dn == 32
    # I due rami della deviatrice, che il manuale non tocca: la portata della macchina in Øi 25.
    for da, a in (("volano", "conf-ritorno-pdc"), ("bollitore", "conf-ritorno-pdc")):
        ramo = _tratto(tratti, da, a)
        assert ramo.diametro is not None and ramo.diametro.dn == 25


def test_senza_il_manuale_il_ritorno_comune_e_quello_della_portata_della_macchina(
    catalogo: ComponentRegistry,
) -> None:
    """Tolta la marca, D-223 non vale: il ritorno comune prende il DN della sola portata
    della macchina, Øi 25. Sommata, 4,13 m³/h, darebbe Øi 32 (1,43 m/s in DN 32)."""
    modello, del_progetto = _modello(_villetta(senza=("marca",)), catalogo)
    comune = _tratto(tratti_del_diametro(modello, del_progetto), "conf-ritorno-pdc", "pdc")
    assert comune.portata_m3h == pytest.approx(portata_da_potenza(12, 5))
    assert comune.diametro is not None and comune.diametro.dn == 25
    assert comune.diametro.velocita_m_s == pytest.approx(1.170, abs=1e-3)


def test_la_perdita_distribuita_fatta_a_mano() -> None:
    """2,067 m³/h d'acqua a 40 °C in acciaio (ε 0,045 mm), a mano:

    - DN 32: v = 0,5742·10⁻³ / 8,042·10⁻⁴ = 0,7139 m/s; Re = 0,7139 · 0,032 / 0,658·10⁻⁶
      = 34 719; f = 0,25 / log₁₀(3,801·10⁻⁴ + 4,699·10⁻⁴)² = 0,02652;
      Δp/L = 0,02652 / 0,032 · 1000 · 0,7139² / 2 = 211,2 Pa/m;
    - DN 25: v = 1,1697 m/s; Re = 44 441; f = 0,02663; Δp/L = 728,6 Pa/m.
    """
    q = portata_da_potenza(12, 5)
    assert perdita_distribuita_pa_m(q, 32) == pytest.approx(211.2, rel=2e-3)
    assert perdita_distribuita_pa_m(q, 25) == pytest.approx(728.6, rel=2e-3)
    assert fattore_d_attrito(34719, 0.045e-3, 0.032) == pytest.approx(0.02652, rel=2e-3)
    # In laminare 64/Re, e il rame liscio perde meno dell'acciaio.
    assert fattore_d_attrito(1000, 0.045e-3, 0.032) == pytest.approx(0.064)
    assert perdita_distribuita_pa_m(q, 32, rugosita_m=0.0015e-3) < perdita_distribuita_pa_m(q, 32)


@pytest.mark.parametrize("grafo", ["grafo.json", "grafo-completo.json"])
def test_il_giro_del_serpentino_e_il_piu_costoso(grafo: str, catalogo: ComponentRegistry) -> None:
    """Due giri, uno per posizione della deviatrice. Volano: 26 m in Øi 32 e 2 m in Øi 25,
    211,2 · 26 + 728,6 · 2 = 6,95 kPa. Serpentino: 24 m in Øi 32 e 8 m in Øi 25,
    211,2 · 24 + 728,6 · 8 = 10,90 kPa; con il 30 % di concentrate 14,17 kPa.

    Sul grafo completo le regole hanno spezzato le tubazioni coi T di servizio e
    riordinato il ritorno: la lunghezza data resta su un pezzo solo, e il conto e' lo
    stesso."""
    testo = _villetta(grafo, pdc={"prevalenza_utile_kpa": 10}, lunghezze=_lunghezze_per(grafo))
    modello, del_progetto = _modello(testo, catalogo)
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert verifica.macchina == "pdc"
    assert verifica.giri == 2
    assert verifica.attraverso == ("bollitore",)
    assert [(t.da, t.a, t.dn, t.lunghezza_m) for t in verifica.giro] == [
        ("pdc", "deviatrice", 32, 12.0),
        ("deviatrice", "bollitore", 25, 4.0),
        ("bollitore", "conf-ritorno-pdc", 25, 4.0),
        ("conf-ritorno-pdc", "pdc", 32, 12.0),
    ]
    assert verifica.distribuite_kpa == pytest.approx(10.90, abs=0.02)
    assert MAGGIORAZIONE_CONCENTRATE == 0.30
    assert verifica.totale_kpa == pytest.approx(14.17, abs=0.03)
    assert verifica.supera


def _lunghezze_per(grafo: str) -> dict[str, float]:
    """Sul grafo completo le tubazioni del progettista hanno cambiato nome: la lunghezza
    sta sul primo pezzo (`rules.apply`, `assembly.runs`)."""
    if grafo == "grafo.json":
        return LUNGHEZZE
    return {"t1-a": 12.0, "t2-a": 2.0, "t3-a": 4.0, "t4-a": 2.0, "t5-a": 4.0, "t6-a-a-1-a": 12.0}


def test_l_avviso_solo_se_il_giro_costa_piu_della_prevalenza(catalogo: ComponentRegistry) -> None:
    modello, del_progetto = _modello(
        _villetta(pdc={"prevalenza_utile_kpa": 10}, lunghezze=LUNGHEZZE), catalogo
    )
    (avviso,) = avvisi_della_prevalenza(modello, del_progetto)
    assert "14,2 kPa" in avviso and "10,0 utili" in avviso and "bollitore" in avviso
    modello, del_progetto = _modello(
        _villetta(pdc={"prevalenza_utile_kpa": 40}, lunghezze=LUNGHEZZE), catalogo
    )
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert not verifica.supera
    assert avvisi_della_prevalenza(modello, del_progetto) == []


@pytest.mark.parametrize(
    ("pdc", "lunghezze", "senza"),
    [
        pytest.param({}, LUNGHEZZE, (), id="senza-prevalenza"),
        pytest.param({"prevalenza_utile_kpa": 10}, None, (), id="senza-lunghezze"),
        pytest.param(
            {"prevalenza_utile_kpa": 10},
            {k: v for k, v in LUNGHEZZE.items() if k != "t5"},
            (),
            id="un-tratto-senza-lunghezza",
        ),
        pytest.param({"prevalenza_utile_kpa": 10}, LUNGHEZZE, ("delta_t_k",), id="senza-salto-termico"),
    ],
)
def test_senza_i_dati_non_si_dice_niente(
    pdc: dict[str, Any],
    lunghezze: dict[str, float] | None,
    senza: tuple[str, ...],
    catalogo: ComponentRegistry,
) -> None:
    testo = _villetta(pdc=pdc, lunghezze=lunghezze, senza=senza)
    modello, del_progetto = _modello(testo, catalogo)
    assert verifiche_della_prevalenza(modello, del_progetto) == ()
    assert avvisi_della_prevalenza(modello, del_progetto) == []


def test_senza_la_richiesta_dei_diametri_non_si_verifica(catalogo: ComponentRegistry) -> None:
    testo = _villetta(pdc={"prevalenza_utile_kpa": 10}, lunghezze=LUNGHEZZE)
    del testo["diametri"]
    modello, del_progetto = _modello(testo, catalogo)
    assert verifiche_della_prevalenza(modello, del_progetto) == ()


@pytest.mark.parametrize(("metri", "supera"), [(1.4, True), (1.5, False)])
def test_la_prevalenza_in_metri_di_colonna_d_acqua(
    metri: float, supera: bool, catalogo: ComponentRegistry
) -> None:
    """1,4 m c.a. sono 1,4 · 9,807 = 13,73 kPa, sotto i 14,17 del giro; 1,5 m sono 14,71."""
    modello, del_progetto = _modello(
        _villetta(pdc={"prevalenza_utile_m": metri}, lunghezze=LUNGHEZZE), catalogo
    )
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert verifica.prevalenza_utile_kpa == pytest.approx(metri * 9.80665)
    assert verifica.supera is supera


def test_la_prevalenza_e_un_numero_in_kpa(catalogo: ComponentRegistry) -> None:
    with pytest.raises(ValueError, match="prevalenza_utile_kpa must be a positive number in kPa"):
        _modello(_villetta(pdc={"prevalenza_utile_kpa": "50 kPa"}), catalogo)


def test_completa_e_disegna_dicono_l_avviso_e_il_grafo_completo_tiene_le_lunghezze(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Il comando, come lo usa l'agente: `completa` scrive l'avviso fra i suoi, e le
    lunghezze del progettista arrivano nel grafo completo — anche sul ritorno, che le
    regole spezzano e poi riordinano (`assembly.runs`): prima li' si perdevano."""
    from disegnatore_mep.skill import cartelle_del_repository, main

    cartelle = cartelle_del_repository(ROOT)
    grafo, completo = tmp_path / "grafo.json", tmp_path / "grafo-completo.json"
    testo = _villetta(pdc={"prevalenza_utile_kpa": 10}, lunghezze=LUNGHEZZE)
    grafo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
    assert main(["completa", str(grafo), "--out", str(completo)], cartelle) == 0
    uscita = capsys.readouterr().out
    assert "Avvisi della prevalenza della pompa a bordo" in uscita
    assert "GT-01: il giro primario piu' costoso (32,0 m di tubo, attraverso BOL-01) perde 14,2 kPa" in uscita
    tubi = json.loads(completo.read_text(encoding="utf-8"))["connections"]
    date = {
        tubo["id"]: tubo["lunghezza_m"]
        for tubo in tubi
        if tubo["network_id"] == "primario" and "lunghezza_m" in tubo
    }
    assert sorted(date.values()) == sorted(LUNGHEZZE.values())
    assert date["t6-a-a-1-a"] == 12.0

    # Anche «esistente» resta sulle meta' di un tubo che le regole riordinano.
    testo["connections"] = [
        {**tubo, "esistente": True} if tubo["id"] == "t6" else tubo for tubo in testo["connections"]
    ]
    grafo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
    secondo = tmp_path / "grafo-completo-esistente.json"
    assert main(["completa", str(grafo), "--out", str(secondo)], cartelle) == 0
    capsys.readouterr()
    ritorno = [t for t in json.loads(secondo.read_text(encoding="utf-8"))["connections"] if t["id"].startswith("t6")]
    assert len(ritorno) > 2 and all(t.get("esistente") for t in ritorno), ritorno

    tavola = tmp_path / "tavola"
    piano = VILLETTA / "piano-idraulica.json"
    argomenti = ["disegna", str(completo), "--piano", str(piano), "--out", str(tavola), "--senza-dxf"]
    assert main(argomenti, cartelle) == 0
    assert "Avvisi della prevalenza della pompa a bordo" in capsys.readouterr().out
