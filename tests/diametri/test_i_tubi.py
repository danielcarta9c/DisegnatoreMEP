"""Il tubo da comprare (I-279, I-281): il calcolo sceglie il tubo commerciale nel suo materiale.

Il PO: «Ø32 è quello che compro al banco. quindi il diametro interno è piu' piccolo.» La
tavola scrive «MS 32×3», «DN 25 (1")», «Cu 28×1», e non piu' «Øi 32»; il tubo e' il piu'
piccolo del materiale in cui la velocita', sul diametro interno reale, non supera la
massima del suo pollice (tab. 9 del Quaderno Caleffi n. 5, D-193). I numeri a mano:

- 12 kW con 5 K: 12 / (4,18 · 5) = 0,5742 kg/s, 2,067 m³/h;
- MS 26×3 (20 mm, ¾", 1,1 m/s): 2,067 / 3600 / (π · 0,020² / 4) = 1,83 m/s, troppo;
- MS 32×3 (26 mm, 1", 1,3 m/s): 0,5742·10⁻³ / 5,309·10⁻⁴ = 1,081 m/s, basta;
- acciaio DN 20 (21,7 mm, ¾"): 1,55 m/s, troppo; DN 25 (27,3 mm, 1"): 0,981 m/s, basta;
- rame Cu 22×1 (20 mm, ¾"): 1,83 m/s; Cu 28×1 (26 mm, 1"): 1,081 m/s, basta;
- 15 kW con 5 K: 2,584 m³/h; nel MS 32×3 1,352 m/s, oltre 1,3: MS 40×3,5 (33 mm, 1¼",
  1,6 m/s), 0,839 m/s. E' quello che il PO fa: «sulla 12 mettiamo il 32 … sulla 15 il 40».
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.calcolatore import portata_da_potenza
from disegnatore_mep.diametri.foglio import foglio_in_markdown, righe_del_calcolo
from disegnatore_mep.diametri.scritte import tratti_da_scrivere
from disegnatore_mep.diametri.tratti import (
    avvisi_dei_tubi,
    pollici_dei_pezzi,
    tratti_del_diametro,
    tubi_delle_tubazioni,
)
from disegnatore_mep.diametri.tubi import (
    MATERIALE_PREDEFINITO,
    tabelle,
    tubi_del_materiale,
    tubo_dal_testo,
    tubo_per,
)
from disegnatore_mep.graphics.note import (
    NOTA_ISOLAMENTO,
    nota_dell_isolamento,
    spessore_dell_isolante_mm,
)
from disegnatore_mep.layout.diametri import voci_dei_materiali
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"


def _villetta(
    potenza: float = 12,
    sezioni: dict[str, str] | None = None,
    materiale: str | None = None,
    grafo: str = "grafo-completo.json",
) -> dict[str, Any]:
    testo: dict[str, Any] = json.loads((VILLETTA / grafo).read_text(encoding="utf-8"))
    for pezzo in testo["components"]:
        if pezzo["id"] == "pdc":
            pezzo["properties"].update({"delta_t_k": 5, "power_kw": potenza})
    for tubo in testo["connections"]:
        if sezioni and tubo["network_id"] in sezioni:
            tubo["sezione"] = sezioni[tubo["network_id"]]
    testo["diametri"] = {"reti": ["primario"]}
    if materiale is not None:
        testo["materiale_tubazioni"] = materiale
    return testo


def _modello(testo: dict[str, Any], catalogo: ComponentRegistry) -> tuple[ProjectModel, ComponentRegistry]:
    modello = ProjectModel.model_validate(testo)
    return modello, catalogo.per_il_progetto(modello)


# --- la scelta ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("materiale", "scritta", "interno", "velocita"),
    [
        ("multistrato", "MS 32×3", 26.0, 1.081),
        ("acciaio", 'DN 25 (1")', 27.3, 0.981),
        ("rame", "Cu 28×1", 26.0, 1.081),
    ],
)
def test_dodici_kw_con_cinque_kelvin(materiale: str, scritta: str, interno: float, velocita: float) -> None:
    portata = portata_da_potenza(12, 5)
    assert portata == pytest.approx(2.067, abs=1e-3)
    scelto = tubo_per(portata, materiale)  # type: ignore[arg-type]
    assert scelto is not None
    assert scelto.scritta == scritta
    assert scelto.tubo.interno_mm == interno
    assert scelto.tubo.pollici == '1"' and scelto.velocita_massima_m_s == 1.3
    assert scelto.velocita_m_s == pytest.approx(velocita, abs=1e-3)
    assert scelto.velocita_m_s <= 1.3


def test_quindici_kw_passa_al_quaranta() -> None:
    """I-281: la sola velocita' da' il 40 sulla 15 kW."""
    portata = portata_da_potenza(15, 5)
    assert tubi_del_materiale("multistrato")[3].velocita_m_s(portata) == pytest.approx(1.352, abs=1e-3)
    scelto = tubo_per(portata)
    assert scelto is not None and scelto.scritta == "MS 40×3,5"
    assert scelto.velocita_m_s == pytest.approx(0.839, abs=1e-3) and scelto.velocita_massima_m_s == 1.6
    assert MATERIALE_PREDEFINITO == "multistrato"


def test_l_oi_minimo_e_quello_della_massima_del_tubo_scelto() -> None:
    """2,067 m³/h a 1,3 m/s: √(4 · 5,742·10⁻⁴ / (π · 1,3)) = 23,7 mm, sotto i 26 del 32×3."""
    scelto = tubo_per(portata_da_potenza(12, 5))
    assert scelto is not None and scelto.interno_minimo_mm == pytest.approx(23.7, abs=0.05)


def test_oltre_l_ultimo_tubo_non_si_inventa() -> None:
    ultimo = tubi_del_materiale("multistrato")[-1]
    assert ultimo.scritta == "MS 63×4,5"
    assert tubo_per(ultimo.portata_massima_m3h * 0.999) is not None
    assert tubo_per(ultimo.portata_massima_m3h * 1.001) is None
    assert tubo_per(ultimo.portata_massima_m3h * 1.001, "acciaio") is not None


def test_le_tabelle_sono_quelle_delle_fonti() -> None:
    """SRC-053 (Giacomini R999), SRC-055 (UNI EN 10255 serie media, da Viega), SRC-056
    (UNI EN 1057, da Oppo); i pollici da SRC-054 (Bampi, tabella 5)."""
    misure = {
        materiale: [(t.esterno_mm, t.spessore_mm, t.interno_mm, t.pollici) for t in tubi_del_materiale(materiale)]
        for materiale in ("multistrato", "acciaio", "rame")
    }
    assert misure["multistrato"] == [
        (16, 2, 12, '3/8"'), (20, 2, 16, '½"'), (26, 3, 20, '¾"'), (32, 3, 26, '1"'),
        (40, 3.5, 33, '1¼"'), (50, 4, 42, '1½"'), (63, 4.5, 54, '2"'),
    ]
    assert misure["acciaio"] == [
        (21.3, 2.6, 16.1, '½"'), (26.9, 2.6, 21.7, '¾"'), (33.7, 3.2, 27.3, '1"'), (42.4, 3.2, 36.0, '1¼"'),
        (48.3, 3.2, 41.9, '1½"'), (60.3, 3.6, 53.1, '2"'), (76.1, 3.6, 68.9, '2½"'), (88.9, 4.0, 80.9, '3"'),
        (114.3, 4.5, 105.3, '4"'),
    ]
    assert misure["rame"] == [
        (18, 1, 16, '½"'), (22, 1, 20, '¾"'), (28, 1, 26, '1"'), (35, 1.2, 32.6, '1¼"'), (42, 1.2, 39.6, '1½"'),
        (54, 1.5, 51, '2"'),
    ]
    for materiale, righe in misure.items():
        for esterno, spessore, interno, _ in righe:
            assert interno == pytest.approx(esterno - 2 * spessore, abs=1e-9), (materiale, esterno)
    assert [t.dn for t in tubi_del_materiale("acciaio")] == [15, 20, 25, 32, 40, 50, 65, 80, 100]
    assert tabelle().dn_del_pollice['1"'] == 25 and tabelle().dn_del_pollice['1¼"'] == 32


@pytest.mark.parametrize(
    ("testo", "atteso"),
    [
        ("MS 32×3", "MS 32×3"),
        ("32x3", "MS 32×3"),
        ("multistrato 40x3,5", "MS 40×3,5"),
        ("DN 25", 'DN 25 (1")'),
        ('DN 25 (1")', 'DN 25 (1")'),
        ('1"', 'DN 25 (1")'),
        ('1 1/4"', 'DN 32 (1¼")'),
        ('1¼"', 'DN 32 (1¼")'),
        ("Cu 28×1", "Cu 28×1"),
        ("rame 35x1,2", "Cu 35×1,2"),
        ("22x1", "Cu 22×1"),
        ("3G6", None),
        ("Ø200", None),
        ("1000×250", None),
        ("MS 33×3", None),
    ],
)
def test_il_tubo_del_progettista_nelle_tre_notazioni(testo: str, atteso: str | None) -> None:
    tubo = tubo_dal_testo(testo)
    assert (None if tubo is None else tubo.scritta) == atteso


# --- il grafo ------------------------------------------------------------------------


def test_il_materiale_e_un_dato_additivo_del_grafo() -> None:
    testo = _villetta()
    assert "materiale_tubazioni" not in ProjectModel.model_validate(testo).model_dump(mode="json")
    testo["materiale_tubazioni"] = "acciaio"
    for rete in testo["networks"]:
        if rete["id"] == "primario":
            rete["materiale_tubazioni"] = "rame"
    modello = ProjectModel.model_validate(testo)
    dati = modello.model_dump(mode="json")
    assert dati["materiale_tubazioni"] == "acciaio"
    assert {r["id"]: r.get("materiale_tubazioni") for r in dati["networks"]}["primario"] == "rame"
    assert all("materiale_tubazioni" not in r for r in dati["networks"] if r["id"] != "primario")
    with pytest.raises(ValueError):
        ProjectModel.model_validate({**testo, "materiale_tubazioni": "pvc"})


@pytest.mark.parametrize(
    ("materiale", "scritta", "legenda"),
    [
        (None, "MS 32×3", ("MS", "multistrato, diametro esterno × spessore")),
        ("acciaio", 'DN 25 (1")', ("DN", "diametro nominale acciaio")),
        ("rame", "Cu 28×1", ("Cu", "rame, diametro esterno × spessore")),
    ],
)
def test_la_scritta_e_la_legenda_secondo_il_materiale(
    materiale: str | None, scritta: str, legenda: tuple[str, str], catalogo: ComponentRegistry
) -> None:
    modello, del_progetto = _modello(_villetta(materiale=materiale), catalogo)
    scritte, calcolati = tratti_da_scrivere(modello, del_progetto)
    assert all(item.tubazione in ("t25", "t26") for item in scritte), "solo la linea elettrica della macchina"
    assert {item.scritta for item in calcolati} == {scritta}
    materiali = {item.diametro.tubo.materiale for item in calcolati if item.diametro is not None}
    assert voci_dei_materiali(materiali) == [legenda]


def test_la_legenda_dice_solo_i_materiali_presenti_in_ordine() -> None:
    assert voci_dei_materiali(["rame", "multistrato", "rame"]) == [
        ("MS", "multistrato, diametro esterno × spessore"),
        ("Cu", "rame, diametro esterno × spessore"),
    ]
    assert voci_dei_materiali([]) == []


# --- il tubo del progettista ----------------------------------------------------------


def test_il_tubo_del_progettista_vince_e_se_e_piccolo_lo_si_dice(catalogo: ComponentRegistry) -> None:
    """15 kW su tutto il primario in MS 32×3, come due commesse realizzate: la tavola
    scrive MS 32×3, e l'avviso dice 1,35 m/s oltre 1,3 e che il calcolo sceglierebbe il
    40×3,5. Non blocca."""
    modello, del_progetto = _modello(_villetta(15, {"primario": "MS 32×3"}), catalogo)
    scritte, calcolati = tratti_da_scrivere(modello, del_progetto)
    assert calcolati == ()
    assert {item.scritta for item in scritte if item.tubo is not None} == {"MS 32×3"}
    avvisi = avvisi_dei_tubi(modello, del_progetto)
    assert len(avvisi) == 5, avvisi
    assert all(
        "MS 32×3 del progettista (Øi 26 mm), 2,58 m³/h a 1,35 m/s, oltre la massima di 1,3 m/s" in a
        and "il calcolo sceglierebbe MS 40×3,5" in a
        for a in avvisi
    )
    # Con 12 kW il suo 32×3 basta: nessun avviso.
    modello, del_progetto = _modello(_villetta(12, {"primario": "32x3"}), catalogo)
    assert avvisi_dei_tubi(modello, del_progetto) == []
    # Un testo che non si legge come un tubo non si controlla, e non si dice niente.
    modello, del_progetto = _modello(_villetta(15, {"primario": "tubo esistente"}), catalogo)
    assert avvisi_dei_tubi(modello, del_progetto) == []


def test_oltre_l_ultimo_tubo_il_tratto_resta_senza_e_lo_si_dice(catalogo: ComponentRegistry) -> None:
    """150 kW con 5 K sono 25,8 m³/h: oltre il MS 63×4,5 (16,5 m³/h a 2 m/s). Il tratto
    resta senza tubo, e l'avviso lo dice; in acciaio e' un DN 65 (2½"), 68,9 mm a 1,93 m/s."""
    modello, del_progetto = _modello(_villetta(150), catalogo)
    avvisi = avvisi_dei_tubi(modello, del_progetto)
    assert avvisi and all("oltre MS 63×4,5, l'ultimo tubo della tabella del multistrato" in a for a in avvisi)
    assert all(t.diametro is None for t in tratti_del_diametro(modello, del_progetto) if t.reti == ("primario",))
    modello, del_progetto = _modello(_villetta(150, materiale="acciaio"), catalogo)
    assert avvisi_dei_tubi(modello, del_progetto) == []
    scritte = {t.scritta for t in tratti_del_diametro(modello, del_progetto) if t.reti == ("primario",)}
    assert scritte == {'DN 65 (2½")'}


def test_completa_stampa_l_avviso_dei_tubi(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from disegnatore_mep.skill import cartelle_del_repository, main

    grafo, completo = tmp_path / "grafo.json", tmp_path / "grafo-completo.json"
    testo = _villetta(15, {"primario": "MS 32×3"}, grafo="grafo.json")
    grafo.write_text(json.dumps(testo, ensure_ascii=False), encoding="utf-8")
    assert main(["completa", str(grafo), "--out", str(completo)], cartelle_del_repository(ROOT)) == 0
    uscita = capsys.readouterr().out
    assert "Avvisi dei tubi" in uscita
    assert "il calcolo sceglierebbe MS 40×3,5" in uscita


# --- il foglio dei calcoli ------------------------------------------------------------


def test_il_foglio_dei_calcoli_porta_l_oi_accanto_al_tubo(catalogo: ComponentRegistry) -> None:
    modello, del_progetto = _modello(_villetta(), catalogo)
    righe = [r for r in righe_del_calcolo(modello, del_progetto, {}) if r.tubo is not None]
    assert righe and all(r.tubo == "MS 32×3" and r.interno_mm == 26.0 for r in righe)
    assert all(r.interno_minimo_mm == pytest.approx(23.7, abs=0.05) for r in righe)
    testo = foglio_in_markdown(righe)
    assert "| portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s |" in testo
    assert "| 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |" in testo
    modello, del_progetto = _modello(_villetta(15, {"primario": "MS 32×3"}), catalogo)
    righe = [r for r in righe_del_calcolo(modello, del_progetto, {}) if r.tubo is not None]
    assert all(r.del_progettista for r in righe)
    assert all(r.nota == "del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5" for r in righe)


# --- la distinta e l'isolamento ---------------------------------------------------------


def test_la_distinta_dice_il_tubo_e_il_pollice_degli_accessori(catalogo: ComponentRegistry) -> None:
    modello, del_progetto = _modello(_villetta(), catalogo)
    tubi = tubi_delle_tubazioni(modello, del_progetto)
    tratti = tratti_del_diametro(modello, del_progetto)
    primario = {c for item in tratti if item.reti == ("primario",) for c in item.connection_ids}
    # Gli stacchi di servizio — vaso, sicurezza, manometro, riempimento — non hanno il tubo
    # del calcolo (D-193, punto 7).
    assert set(tubi) == primario and not any(c.startswith("stub-") for c in tubi)
    assert {t.dicitura for t in tubi.values()} == {"multistrato MS 32×3"}
    pollici = pollici_dei_pezzi(modello, del_progetto)
    assert pollici["deviatrice"] == '1"' and pollici["strainer-pdc-water-return"] == '1"'
    assert "pdc" not in pollici and "volano" not in pollici, "le macchine non hanno il pollice del tubo"


def test_la_distinta_dal_comando(tmp_path: Path) -> None:
    from disegnatore_mep.distinta.comando import esegui

    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(json.dumps(_villetta(), ensure_ascii=False), encoding="utf-8")
    esegui(
        grafo, tmp_path / "distinta", None, ROOT / "rules" / "distinta", ROOT / "examples" / "layout" / "catalog",
        ROOT / "naming", cartella_dei_simboli=ROOT / "assets" / "symbols",
    )
    testo = next((tmp_path / "distinta").glob("Distinta_*.md")).read_text(encoding="utf-8")
    # Da REL-020 l'acqua ha il suo corredo: il tubo della tavola e il pollice degli accessori
    # stanno nelle voci della sezione I, non piu' nella X.
    assert "Tubo multistrato MS 32×3, nudo" in testo
    assert 'Valvola deviatrice a tre vie 1" con attuatore 230 V' in testo
    assert 'Filtro a Y 1" FF' in testo


def test_la_nota_dell_isolamento_sui_tubi_veri() -> None:
    """DPR 412/93, Allegato B, λ 0,040: per diametro esterno, sotto 20 mm 20; 20-39 30;
    40-59 40; 60-79 50; 80-99 55; da 100 60."""
    assert [spessore_dell_isolante_mm(d) for d in (16, 20, 32, 39.9, 40, 63, 76.1, 88.9, 114.3)] == [
        20, 30, 30, 30, 40, 50, 50, 55, 60,
    ]
    tubi = [t for t in tubi_del_materiale("multistrato") if t.esterno_mm in (32, 40)]
    nota = nota_dell_isolamento([*tubi, tubi[0]])
    assert "(MS 32×3: 30 mm; MS 40×3,5: 40 mm)" in nota
    assert nota_dell_isolamento([]) == NOTA_ISOLAMENTO


def test_nell_esecutivo_la_nota_dice_i_tubi_della_tavola(catalogo: ComponentRegistry) -> None:
    from disegnatore_mep.graphics.note import note_di_posa

    testo = _villetta()
    testo["metadata"]["livello"] = "esecutivo"
    modello, del_progetto = _modello(testo, catalogo)
    tubi = list(tubi_delle_tubazioni(modello, del_progetto).values())
    note = note_di_posa(
        modello, del_progetto, (p.id for p in modello.components), (c.network_id for c in modello.connections), tubi
    )
    assert note[0].startswith("Isolamento delle tubazioni") and "(MS 32×3: 30 mm)" in note[0]
