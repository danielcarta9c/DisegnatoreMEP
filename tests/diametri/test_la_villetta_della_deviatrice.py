"""La villetta con la deviatrice dell'ACS e la verifica della prevalenza (I-270).

Il PO, su una commessa reale (villetta, Shenling 12 kW, volano a 4 attacchi, ACS su
deviatrice): «con una deviatrice il calcolo somma i due rami sul ritorno comune (Øi 32
invece di Øi 25 a parita' di portata della PdC); e non verifica le perdite di carico
contro la prevalenza utile della pompa a bordo».

**La somma.** La deviatrice manda l'acqua **o** al volano **o** al serpentino: sul
ritorno comune passa la portata della macchina, non la somma dei rami. Qui lo si misura
sulla villetta di riferimento (`docs/collaudi/REL-015/pdc-regola/`), che ha la stessa
centrale: 12 kW con 5 K sono 2,067 m³/h su **ogni** tratto del primario, ritorno comune
compreso. **Dal 4 novembre 2026 (I-279, I-281)** la tavola scrive il tubo da comprare e
l'attacco della macchina non e' piu' un minimo: ogni tratto del primario e' **MS 32×3**,
2,067 m³/h a 1,08 m/s nei suoi 26 mm, sotto gli 1,3 del suo pollice (1"), ed e' la prova
che la portata non e' sommata — sommata (4,13 m³/h) darebbe 2,16 m/s nel 32×3, e MS
40×3,5. Prima di I-281 il ritorno comune era Øi 32 per D-223 (l'attacco 1¼" della
ThermaX 12 kW); ora all'attacco c'e' una riduzione, detta come informazione.

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
    # Prima di I-279 e I-281 qui c'era «Øi 32», l'attacco 1¼" (D-223): ora il tubo lo
    # sceglie la sola velocita', e sul ritorno comune e' quello dei rami.
    for da, a in (("conf-ritorno-pdc", "pdc"), ("volano", "conf-ritorno-pdc"), ("bollitore", "conf-ritorno-pdc")):
        tratto = _tratto(tratti, da, a)
        assert tratto.diametro is not None and tratto.diametro.scritta == "MS 32×3", (da, a)
        assert tratto.diametro.velocita_m_s == pytest.approx(1.081, abs=1e-3)


def test_con_o_senza_il_manuale_il_tubo_e_quello_della_velocita(
    catalogo: ComponentRegistry,
) -> None:
    """Tolta la marca il ritorno comune e' lo stesso MS 32×3: l'attacco non entra nella
    scelta (I-281). Sommata, 4,13 m³/h, la portata darebbe MS 40×3,5."""
    from disegnatore_mep.diametri.tubi import tubo_per

    modello, del_progetto = _modello(_villetta(senza=("marca",)), catalogo)
    comune = _tratto(tratti_del_diametro(modello, del_progetto), "conf-ritorno-pdc", "pdc")
    assert comune.portata_m3h == pytest.approx(portata_da_potenza(12, 5))
    assert comune.diametro is not None and comune.diametro.scritta == "MS 32×3"
    sommata = tubo_per(2 * portata_da_potenza(12, 5))
    assert sommata is not None and sommata.scritta == "MS 40×3,5"


def test_l_attacco_piu_grande_del_tubo_e_una_riduzione(catalogo: ComponentRegistry) -> None:
    """La ThermaX 12 kW ha l'attacco 1¼", il tubo e' MS 32×3 (1"): una riduzione per
    attacco, in una funzione sola (I-281), che il passo dopo legge per posarla."""
    from disegnatore_mep.diametri.costruttori import riduzioni_all_attacco

    modello, del_progetto = _modello(_villetta(), catalogo)
    riduzioni = riduzioni_all_attacco(modello, del_progetto)
    assert len(riduzioni) == 2 and {item.macchina for item in riduzioni} == {"pdc"}
    assert all(item.in_parole == 'attacco 1¼", tubo MS 32×3 (1"): riduzione all\'attacco' for item in riduzioni)
    # Senza la marca il manuale non si conosce: nessuna riduzione.
    modello, del_progetto = _modello(_villetta(senza=("marca",)), catalogo)
    assert riduzioni_all_attacco(modello, del_progetto) == []


def test_la_perdita_distribuita_fatta_a_mano() -> None:
    """2,067 m³/h d'acqua a 40 °C in acciaio (ε 0,045 mm), a mano:

    - 32 mm interni: v = 0,5742·10⁻³ / 8,042·10⁻⁴ = 0,7139 m/s; Re = 0,7139 · 0,032 /
      0,658·10⁻⁶ = 34 719; f = 0,25 / log₁₀(3,801·10⁻⁴ + 4,699·10⁻⁴)² = 0,02652;
      Δp/L = 0,02652 / 0,032 · 1000 · 0,7139² / 2 = 211,2 Pa/m;
    - 25 mm interni: v = 1,1697 m/s; Re = 44 441; f = 0,02663; Δp/L = 728,6 Pa/m;

    e nel multistrato MS 32×3 (26 mm interni, ε 0,007 mm, I-279): v = 1,0814 m/s,
    Re = 42 731, f = 0,25 / log₁₀(7,277·10⁻⁵ + 3,902·10⁻⁴)² = 0,02248,
    Δp/L = 0,02248 / 0,026 · 1000 · 1,0814² / 2 = 505,7 Pa/m.
    """
    q = portata_da_potenza(12, 5)
    assert perdita_distribuita_pa_m(q, 32) == pytest.approx(211.2, rel=2e-3)
    assert perdita_distribuita_pa_m(q, 25) == pytest.approx(728.6, rel=2e-3)
    assert perdita_distribuita_pa_m(q, 26, rugosita_m=0.007e-3) == pytest.approx(505.7, rel=2e-3)
    assert fattore_d_attrito(34719, 0.045e-3, 0.032) == pytest.approx(0.02652, rel=2e-3)
    # In laminare 64/Re, e il rame liscio perde meno dell'acciaio.
    assert fattore_d_attrito(1000, 0.045e-3, 0.032) == pytest.approx(0.064)
    assert perdita_distribuita_pa_m(q, 32, rugosita_m=0.0015e-3) < perdita_distribuita_pa_m(q, 32)


@pytest.mark.parametrize("grafo", ["grafo.json", "grafo-completo.json"])
def test_il_giro_del_serpentino_e_il_piu_costoso(grafo: str, catalogo: ComponentRegistry) -> None:
    """Due giri, uno per posizione della deviatrice, tutti in MS 32×3 (I-279; prima Øi 32 e
    Øi 25 d'acciaio, 14,17 kPa). Volano: 28 m, 505,7 · 28 = 14,16 kPa. Serpentino: 32 m,
    505,7 · 32 = 16,18 kPa; con il 30 % di concentrate 21,04 kPa.

    Sul grafo completo le regole hanno spezzato le tubazioni coi T di servizio e
    riordinato il ritorno: la lunghezza data resta su un pezzo solo, e il conto e' lo
    stesso."""
    testo = _villetta(grafo, pdc={"prevalenza_utile_kpa": 10}, lunghezze=_lunghezze_per(grafo))
    modello, del_progetto = _modello(testo, catalogo)
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert verifica.macchina == "pdc"
    assert verifica.giri == 2
    assert verifica.attraverso == ("bollitore",)
    assert [(t.da, t.a, t.tubo.scritta, t.lunghezza_m) for t in verifica.giro] == [
        ("pdc", "deviatrice", "MS 32×3", 12.0),
        ("deviatrice", "bollitore", "MS 32×3", 4.0),
        ("bollitore", "conf-ritorno-pdc", "MS 32×3", 4.0),
        ("conf-ritorno-pdc", "pdc", "MS 32×3", 12.0),
    ]
    assert verifica.distribuite_kpa == pytest.approx(16.18, abs=0.03)
    assert MAGGIORAZIONE_CONCENTRATE == 0.30
    assert verifica.totale_kpa == pytest.approx(21.04, abs=0.04)
    assert verifica.supera and not verifica.assunta


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
    assert "21,0 kPa" in avviso and "10,0 utili" in avviso and "bollitore" in avviso
    assert "indicativo" not in avviso
    modello, del_progetto = _modello(
        _villetta(pdc={"prevalenza_utile_kpa": 40}, lunghezze=LUNGHEZZE), catalogo
    )
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert not verifica.supera
    assert avvisi_della_prevalenza(modello, del_progetto) == []


@pytest.mark.parametrize(
    ("pdc", "lunghezze", "senza"),
    [
        # Senza la marca: per una Shenling la prevalenza c'e' comunque, indicativa (I-281).
        pytest.param({}, LUNGHEZZE, ("marca",), id="senza-prevalenza"),
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


def test_la_shenling_senza_prevalenza_si_verifica_con_8_metri(catalogo: ComponentRegistry) -> None:
    """Il PO: la pompa a bordo «dovrebbe stare sui 8/9 metri» (I-281). Senza il dato del
    progettista si verifica con 8 m (78,45 kPa), e l'avviso dice che e' indicativo. Sul
    giro di 32 m in MS 32×3 (21,0 kPa) basta; con le lunghezze quadruplicate, 128 m, il giro
    perde 84,1 kPa e non basta: e' la «troppa distanza» del PO."""
    modello, del_progetto = _modello(_villetta(lunghezze=LUNGHEZZE), catalogo)
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert verifica.assunta and verifica.prevalenza_utile_kpa == pytest.approx(8 * 9.80665)
    assert not verifica.supera
    assert avvisi_della_prevalenza(modello, del_progetto) == []
    lontano = {chi: 4 * metri for chi, metri in LUNGHEZZE.items()}
    modello, del_progetto = _modello(_villetta(lunghezze=lontano), catalogo)
    (verifica,) = verifiche_della_prevalenza(modello, del_progetto)
    assert verifica.totale_kpa == pytest.approx(84.14, abs=0.15) and verifica.supera
    (avviso,) = avvisi_della_prevalenza(modello, del_progetto)
    assert "8 m, indicativo del PO; il valore vero è la curva del manuale alla portata" in avviso


def test_senza_la_richiesta_dei_diametri_non_si_verifica(catalogo: ComponentRegistry) -> None:
    testo = _villetta(pdc={"prevalenza_utile_kpa": 10}, lunghezze=LUNGHEZZE)
    del testo["diametri"]
    modello, del_progetto = _modello(testo, catalogo)
    assert verifiche_della_prevalenza(modello, del_progetto) == ()


@pytest.mark.parametrize(("metri", "supera"), [(2.1, True), (2.2, False)])
def test_la_prevalenza_in_metri_di_colonna_d_acqua(
    metri: float, supera: bool, catalogo: ComponentRegistry
) -> None:
    """2,1 m c.a. sono 2,1 · 9,807 = 20,59 kPa, sotto i 21,04 del giro in MS 32×3; 2,2 m
    sono 21,57 (prima di I-279, in Øi 32 e Øi 25 d'acciaio, il giro era 14,17 kPa)."""
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
    assert "GT-01: il giro primario piu' costoso (32,0 m di tubo, attraverso BOL-01) perde 21,0 kPa" in uscita
    # L'attacco 1¼" della ThermaX 12 kW sul tubo MS 32×3: una riduzione, che `completa`
    # posa dopo il giunto e dice come informazione (I-281, D-233). Dal 4 novembre 2026 la
    # riga e' una per macchina, con il pezzo aggiunto (prima: «GT-01, mandata: attacco
    # 1¼", tubo MS 32×3 (1"): riduzione all'attacco», un'informazione e basta).
    assert "Riduzioni agli attacchi delle macchine (informazione)" in uscita
    assert 'riduzione 1¼"×1" aggiunta su mandata e ritorno di GT-01' in uscita
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
