"""I difetti della pianta trovati dal terzo collaudo indipendente (REL-012, t3, sulla 1.6.0).

«La pianta esce con 0 ma non si consegna»: il cavo UI-UE faceva il giro
dell'edificio all'esterno, l'alimentazione dell'UE usciva dalla porta di casa,
la centrale e la ripresa erano spostate perche' la pianta non sovrapponeva due
pezzi, le sigle e i numeri di tratta si ricopiavano a mano, la linea diceva la
L da quotare mentre lo schema diceva quella del progettista, il fascio frigo
stava insieme per il 58 % e i sormonti erano 16.

Il caso e' `examples/pianta/casi/collaudo-t3.json`, con le posizioni vere del
testo del progettista, la distinta e il grafo del collaudo accanto.
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.griglia import costruisci_la_griglia
from disegnatore_mep.pianta.modello import ErroreDellaPianta, carica_pianta
from disegnatore_mep.skill import cartelle_del_repository
from disegnatore_mep.skill import main as skill

from .conftest import APPARTAMENTO, CASI, CATALOGO, CONFRONTI, NOMI, RADICE

T3 = CASI["collaudo-t3"]
DISTINTA, GRAFO = CONFRONTI["collaudo-t3"]


def _dati(esito: Esito) -> dict:
    return json.loads(next(p for p in esito.file if p.name.endswith(".tracciati.json")).read_text(encoding="utf-8"))


def _variante(tmp_path: Path, cambia, nome: str = "variante.json") -> Path:  # type: ignore[no-untyped-def]
    dati = json.loads(T3.read_text(encoding="utf-8"))
    cambia(dati)
    percorso = tmp_path / nome
    percorso.write_text(json.dumps(dati, ensure_ascii=False), encoding="utf-8")
    return percorso


def _testi(esito: Esito) -> list[str]:
    return [
        s.in_legenda or s.testo
        for tavola in [esito.tavola, *(esito.dettagli or [])] for chi, s in tavola.scritte
        if chi.startswith(("tratta", "fascio"))
    ]


# --- 1. fuori dall'edificio solo nelle zone esterne dichiarate ---------------------------


def test_nessuna_tratta_corre_fuori_dalle_zone_esterne(esiti: dict[str, Esito]) -> None:
    """Il cavo UI-UE usciva dal muro ovest e girava attorno all'edificio: ora
    tutto quello che e' fuori sta sul terrazzo dichiarato."""
    esito = esiti["collaudo-t3"]
    griglia = costruisci_la_griglia(esito.pianta)
    (x0, y0, x1, y1), = [z.rettangolo for z in esito.pianta.zone_esterne]
    for percorso in esito.percorsi:
        assert percorso.fuori_dalle_zone_m == 0, percorso.tratta
        for k in percorso.nodi:
            if griglia.esterno[k] and not griglia.pezzo[k]:
                x, y = griglia.punto(k)
                assert x0 - 0.31 <= x <= x1 + 0.31 and y0 - 0.31 <= y <= y1 + 0.31, (percorso.tratta, x, y)
    assert esito.rilievi.fuori_dalle_zone_esterne == []
    muri_forati = {f.muro for f in esito.forature if {"T06", "T07", "T11"} & set(f.tratte)}
    assert "m-ovest" not in muri_forati and "m-sud" in muri_forati


def test_senza_la_zona_esterna_uscire_ferma_la_consegna(tmp_path: Path) -> None:
    """Senza il terrazzo, e con l'unita' esterna a un metro e mezzo dalla
    facciata, la si raggiunge solo da fuori: si disegna, ma e' un rilievo
    bloccante, con la tratta e i metri. Accosto a un pezzo esterno (30 cm) si
    passa anche senza zona: e' la strada dal muro al pezzo."""
    def lontana(dati: dict) -> None:
        dati.pop("zone_esterne")
        next(p for p in dati["pezzi"] if p["sigla"] == "UE-01")["y"] = 10.1

    sorgente = _variante(tmp_path, lontana)
    esito = disegna_la_pianta(sorgente, tmp_path / "out", None, dxf=False, png=False)
    assert esito.rilievi.fuori_dalle_zone_esterne
    assert any("esce dall'edificio fuori dalle zone esterne dichiarate" in b for b in esito.rilievi.bloccanti)
    assert any("Fuori dall'edificio" in a for a in esito.avvisi or [])


def test_la_porta_di_casa_non_e_un_passaggio_per_i_cavi() -> None:
    """L'alimentazione dell'UE usciva dalla porta di casa, in traccia (una
    porta lascia passare traccia e pavimento): nel muro perimetrale no."""
    pianta = carica_pianta(T3)
    porta = next(a for a in pianta.aperture if a.id == "porta-di-casa")
    interna = next(a for a in pianta.aperture if a.id == "porta-ingresso")
    assert pianta.quote_ammesse(porta) == ()
    assert pianta.quote_ammesse(interna) == ("traccia", "pavimento")


def test_l_alimentazione_dell_ue_non_esce_dalla_porta(esiti: dict[str, Esito]) -> None:
    t10 = next(p for p in esiti["collaudo-t3"].percorsi if p.tratta == "T10")
    assert all(a.apertura != "porta-di-casa" for a in t10.attraversamenti)


def test_una_zona_esterna_vuole_il_rettangolo_ordinato(tmp_path: Path) -> None:
    sorgente = _variante(tmp_path, lambda d: d["zone_esterne"][0].update(rettangolo=[7.35, 8.6, 0.0, 10.1]))
    with pytest.raises(ErroreDellaPianta, match="terrazzo"):
        carica_pianta(sorgente)


# --- 2. pezzi sovrapposti a quote diverse ------------------------------------------------


def test_la_centrale_sopra_il_plenum_e_la_ripresa_sotto_la_ui(esiti: dict[str, Esito]) -> None:
    """Le posizioni del testo: centrale sopra il plenum, ripresa sotto la UI.
    Prima davano 5 tratte non instradate e 8 linee sopra un pezzo; il
    collaudatore li aveva spostati."""
    esito = esiti["collaudo-t3"]
    pezzi = {p.sigla: p for p in esito.pianta.pezzi}
    assert (pezzi["CZ-01"].x, pezzi["CZ-01"].y) == (pezzi["PLZ-01"].x, pezzi["PLZ-01"].y)
    assert pezzi["CZ-01"].sovrapposto_a == "PLZ-01" and pezzi["RA-01"].sovrapposto_a == "UI-01"
    assert esito.rilievi.tratte_cedute == [] and esito.rilievi.linee_sui_pezzi == []
    assert esito.rilievi.pezzi_sovrapposti == []
    assert esito.rilievi.bloccanti == []


def test_le_linee_della_centrale_partono_dal_suo_ingombro(esiti: dict[str, Esito]) -> None:
    esito = esiti["collaudo-t3"]
    x0, y0, x1, y1 = next(p for p in esito.pianta.pezzi if p.sigla == "CZ-01").rettangolo
    for tracciato, percorso in zip(esito.pianta.tracciati, esito.percorsi, strict=True):
        if "CZ-01" not in (tracciato.estremo_da.pezzo, tracciato.estremo_a.pezzo):
            continue
        capo = percorso.punti[0] if tracciato.estremo_da.pezzo == "CZ-01" else percorso.punti[-1]
        sul_bordo = (abs(capo[0] - x0) < 1e-6 or abs(capo[0] - x1) < 1e-6) and y0 - 1e-6 <= capo[1] <= y1 + 1e-6
        sul_bordo |= (abs(capo[1] - y0) < 1e-6 or abs(capo[1] - y1) < 1e-6) and x0 - 1e-6 <= capo[0] <= x1 + 1e-6
        assert sul_bordo, (tracciato.tratta, capo)


def test_il_pezzo_sotto_e_tratteggiato_e_la_nota_lo_dice(esiti: dict[str, Esito]) -> None:
    svg = next(p for p in esiti["collaudo-t3"].file if p.name == "collaudo-t3.svg").read_text(encoding="utf-8")
    assert "RA-01 sotto UI-01" in svg and "CZ-01 sopra PLZ-01" in svg
    assert "Pezzo sotto un altro" in svg


def test_due_pezzi_sovrapposti_senza_dichiararlo_fermano_la_consegna(tmp_path: Path) -> None:
    def togli(dati: dict) -> None:
        for pezzo in dati["pezzi"]:
            pezzo.pop("sovrapposto_a", None)
            pezzo.pop("sta", None)

    esito = disegna_la_pianta(_variante(tmp_path, togli), tmp_path / "out", None, dxf=False, png=False)
    assert "CZ-01 e PLZ-01" in " ".join(esito.rilievi.pezzi_sovrapposti) or "PLZ-01 e CZ-01" in " ".join(
        esito.rilievi.pezzi_sovrapposti
    )
    assert any("pezzi sovrapposti" in b for b in esito.rilievi.bloccanti)


def test_sovrapposto_a_un_pezzo_che_non_c_e(tmp_path: Path) -> None:
    def sbaglia(dati: dict) -> None:
        next(p for p in dati["pezzi"] if p["sigla"] == "CZ-01")["sovrapposto_a"] = "PLZ-99"

    with pytest.raises(ErroreDellaPianta, match="PLZ-99"):
        carica_pianta(_variante(tmp_path, sbaglia))


def test_sovrapposto_a_accetta_l_id_del_grafo(tmp_path: Path) -> None:
    def con_l_id(dati: dict) -> None:
        next(p for p in dati["pezzi"] if p["sigla"] == "CZ-01")["sovrapposto_a"] = "plenum"

    pianta = carica_pianta(_variante(tmp_path, con_l_id))
    assert next(p for p in pianta.pezzi if p.sigla == "CZ-01").sovrapposto_a == "PLZ-01"


# --- 3. sigle e numeri di tratta controllati con la distinta e il grafo ------------------


def test_con_la_distinta_e_il_grafo_concordano(esiti: dict[str, Esito]) -> None:
    esito = esiti["collaudo-t3"]
    assert esito.confronto is not None
    assert esito.confronto.fonti == ["la distinta", "il grafo"]
    assert esito.confronto.avvisi == [] and esito.confronto.bloccanti == []
    svg = next(p for p in esito.file if p.name == "collaudo-t3.svg").read_text(encoding="utf-8")
    assert "Controllati con la distinta e il grafo: concordano." in svg


def test_un_numero_di_tratta_che_collega_pezzi_diversi_ferma(tmp_path: Path) -> None:
    """Collaudo t3, §3: T03 e T04 incrociati con TA-03 e TA-04."""
    def scambia(dati: dict) -> None:
        t03 = next(t for t in dati["tracciati"] if t["tratta"] == "T03")
        t04 = next(t for t in dati["tracciati"] if t["tratta"] == "T04")
        t03["a"], t04["a"] = t04["a"], t03["a"]

    esito = disegna_la_pianta(_variante(tmp_path, scambia), tmp_path / "out", None, dxf=False, png=False,
                              distinta=DISTINTA)
    bloccanti = " ".join(esito.rilievi.bloccanti)
    assert "T03 collega pezzi diversi" in bloccanti and "T04 collega pezzi diversi" in bloccanti
    assert "questi capi nella distinta sono T04" in bloccanti


def test_le_altre_discordanze_sono_avvisi(tmp_path: Path) -> None:
    def cambia(dati: dict) -> None:
        dati["tracciati"] = [t for t in dati["tracciati"] if t["tratta"] != "T16"]
        next(t for t in dati["tracciati"] if t["tratta"] == "T01")["lunghezza_m"] = 6
        next(t for t in dati["tracciati"] if t["tratta"] == "T02")["tratta"] = "T22"

    esito = disegna_la_pianta(_variante(tmp_path, cambia), tmp_path / "out", None, dxf=False, png=False,
                              distinta=DISTINTA)
    avvisi = " ".join(esito.rilievi.confronto)
    assert "T01: L 6 m in pianta, 5 m nella distinta" in avvisi
    assert "T16 della distinta (UI-01 – CF-01) non e' in pianta" in avvisi
    assert "T22 (PLZ-01 – TA-02) non c'e' nella distinta; con questi capi nella distinta c'e' T02" in avvisi
    assert "T05" not in avvisi  # la ripresa e' un raccordo diretto: non va in pianta
    assert esito.rilievi.confronto_bloccante == []
    assert not [b for b in esito.rilievi.bloccanti if "Discordanza" in b or "collega" in b]


def test_senza_lunghezza_la_prende_dalla_distinta(tmp_path: Path) -> None:
    def togli(dati: dict) -> None:
        for t in dati["tracciati"]:
            t.pop("lunghezza_m", None)

    esito = disegna_la_pianta(_variante(tmp_path, togli), tmp_path / "out", None, dxf=False, png=False,
                              distinta=DISTINTA)
    per_tratta = {t["tratta"]: t for t in _dati(esito)["tratte"]}
    assert per_tratta["T10"]["lunghezza_data_m"] == 18 and per_tratta["T10"]["lunghezza_data_da"] == "distinta"
    assert per_tratta["T10"]["lunghezza_da_quotare_m"] == 22
    assert any("dalla distinta" in a for a in esito.avvisi or [])


def test_senza_distinta_la_lunghezza_la_da_il_grafo(tmp_path: Path) -> None:
    def togli(dati: dict) -> None:
        for t in dati["tracciati"]:
            t.pop("lunghezza_m", None)

    esito = disegna_la_pianta(_variante(tmp_path, togli), tmp_path / "out", None, dxf=False, png=False,
                              grafo=GRAFO, catalogo=CATALOGO, nomi=NOMI)
    per_tratta = {t["tratta"]: t for t in _dati(esito)["tratte"]}
    assert per_tratta["T10"]["lunghezza_data_m"] == 18 and per_tratta["T10"]["lunghezza_data_da"] == "grafo"


def test_il_grafo_dice_la_sigla_dello_schema(tmp_path: Path) -> None:
    def rinomina(dati: dict) -> None:
        next(p for p in dati["pezzi"] if p["sigla"] == "SZ-01")["sigla"] = "SEZ-1"
        for t in dati["tracciati"]:
            t["passa_per"] = ["SEZ-1" if n == "SZ-01" else n for n in t.get("passa_per", [])]

    esito = disegna_la_pianta(_variante(tmp_path, rinomina), tmp_path / "out", None, dxf=False, png=False,
                              grafo=GRAFO, catalogo=CATALOGO, nomi=NOMI)
    assert "SEZ-1 (sezionatore-ue): lo schema lo chiama SZ-01." in esito.rilievi.confronto


def test_il_comando_della_skill_accetta_distinta_e_grafo(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    uscita = skill(
        ["pianta", str(T3), "--out", str(tmp_path), "--senza-dxf", "--distinta", str(DISTINTA), "--grafo", str(GRAFO)],
        cartelle_del_repository(RADICE),
    )
    assert uscita == 0
    assert "Confronto con la distinta e il grafo: 0 bloccanti, 0 avvisi" in capsys.readouterr().out


# --- 4. la scritta sulla linea dice la lunghezza del progettista --------------------------


def test_la_scritta_dice_la_lunghezza_del_progettista_come_lo_schema(esiti: dict[str, Esito]) -> None:
    """Lo schema scrive «Ø200 · L 5 m», la pianta scriveva «T01 · Ø200 · L 7 m»."""
    esito = esiti["collaudo-t3"]
    testi = _testi(esito)
    assert "T01 · Ø200 · L 5 m" in testi and "T15 · 2×0,75 · L 2 m" in testi
    assert not [t for t in testi if t.startswith("T01 ") and "L 7 m" in t]
    t01 = next(t for t in _dati(esito)["tratte"] if t["tratta"] == "T01")
    assert t01["lunghezza_da_quotare_m"] == 7  # la L da quotare resta nella tabella


def test_la_scritta_del_fascio_non_da_un_numero_solo_a_lunghezze_diverse(esiti: dict[str, Esito]) -> None:
    """«T06+T07+T11 · L 13 m» per 9, 9 e 10 m era sbagliata."""
    testi = _testi(esiti["collaudo-t3"])
    fascio = [t for t in testi if t.startswith("T06+T07+T11")]
    assert fascio == ["T06+T07+T11 · L 9 m / 9 m / 10 m"]


# --- 5. fascio e sormonti --------------------------------------------------------------


def test_il_fascio_frigo_sta_insieme_e_i_sormonti_sono_pochi(esiti: dict[str, Esito]) -> None:
    """Sulla 1.6.0: fascio al 58 %, 16 sormonti, un tracciato oltre il +15 %."""
    esito = esiti["collaudo-t3"]
    assert esito.rilievi.fasci["frigo"] >= 0.95
    assert len(esito.rilievi.sormonti) <= 6
    assert not [s for s in esito.rilievi.sormonti if s[:3] in ("T06", "T07", "T11") and s[6:9] in ("T06", "T07", "T11")]


# --- 6. l'esempio della skill ------------------------------------------------------------


def test_l_esempio_usa_passa_per_gli_id_di_catalogo_la_zona_e_il_pezzo_sovrapposto() -> None:
    dati = json.loads(APPARTAMENTO.read_text(encoding="utf-8"))
    catalogo = {json.loads(p.read_text(encoding="utf-8"))["id"] for p in CATALOGO.glob("*.json")}
    assert {p["tipo"] for p in dati["pezzi"]} <= catalogo
    linea_ue = [t for t in dati["tracciati"] if t["da"] == "QE-01" and t["a"] == "UE-01"]
    assert len(linea_ue) == 1 and linea_ue[0]["passa_per"] == ["SZ-01"]
    assert not [t for t in dati["tracciati"] if "SZ-01" in (t["da"], t["a"])]
    assert dati["zone_esterne"]
    assert any(p.get("sovrapposto_a") for p in dati["pezzi"])


# --- 7. gli ingombri da confermare ---------------------------------------------------------


def test_gli_ingombri_da_confermare_li_scrive_la_tavola(esiti: dict[str, Esito]) -> None:
    svg = next(p for p in esiti["collaudo-t3"].file if p.name == "collaudo-t3.svg").read_text(encoding="utf-8")
    assert "Ingombri da confermare" in svg and "UI-01, PLZ-01, CZ-01, RA-01" in svg
    svg_t1 = next(p for p in esiti["collaudo"].file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "Ingombri da confermare" not in svg_t1


# --- 8. le forature della pianta per la distinta ---------------------------------------------


def test_i_tracciati_dicono_gli_attraversamenti_per_il_grafo(esiti: dict[str, Esito]) -> None:
    """Le pareti interne forate dal percorso, piu' il foro del pezzo a parete al
    capo (la bocchetta nella tramezza): il dato `attraversamenti` della
    tubazione, che la distinta conta come pareti interne. Il perimetrale a parte."""
    esito = esiti["collaudo-t3"]
    dati = _dati(esito)
    per_tratta = {t["tratta"]: t for t in dati["tratte"]}
    perimetrali = {m.id for m in esito.pianta.muri if m.tipo == "perimetrale"}
    for tratta, percorso in zip(esito.pianta.tracciati, esito.percorsi, strict=True):
        forati = [a.muro for a in percorso.attraversamenti if a.forato]
        a_parete = [
            muro for sigla, muro in esito.fori_dei_pezzi if sigla in (tratta.estremo_da.pezzo, tratta.estremo_a.pezzo)
        ]
        tutti = forati + a_parete
        voce = per_tratta[tratta.tratta]
        assert voce["attraversamenti_di_parete"] == sum(1 for m in tutti if m not in perimetrali), tratta.tratta
        assert voce["fori_nel_perimetrale"] == sum(1 for m in tutti if m in perimetrali), tratta.tratta
    assert dati["per_il_grafo"]["attraversamenti"]["T01"] == per_tratta["T01"]["attraversamenti_di_parete"] >= 1
    assert per_tratta["T07"]["attraversamenti_di_parete"] >= 1 and per_tratta["T07"]["fori_nel_perimetrale"] == 1


# --- le istruzioni -------------------------------------------------------------------------

ISTRUZIONI = (RADICE / "skill" / "pianta" / "ISTRUZIONI.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("parola", [
    "`zone_esterne`", "`sovrapposto_a`", "`--distinta`", "`--grafo`", "`ingombro_da_confermare`",
    "`attraversamenti`", "porta di casa", "scheda del costruttore", "L quot.",
])
def test_le_istruzioni_dicono_le_cose_nuove(parola: str) -> None:
    assert parola in ISTRUZIONI

