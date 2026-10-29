"""I difetti della pianta trovati dal collaudo indipendente REL-012 (t1), uno per uno.

Il caso e' `examples/pianta/casi/collaudo-t1.json`: la pianta del collaudo, una
planimetria inventata data a parole, con le lunghezze del progettista sui
tracciati e la tratta quadro – sezionatore – UE come una tratta sola. Ogni
prova misura sulla tavola finita, con un conto suo: non legge i rilievi che la
tavola stessa scrive, salvo dove la prova e' proprio che la tavola li dica.
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.pianta import instrada
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.controlli import Rilievi, _le_linee_sui_pezzi
from disegnatore_mep.pianta.griglia import costruisci_la_griglia
from disegnatore_mep.pianta.modello import ErroreDellaPianta, Pianta, carica_pianta
from disegnatore_mep.pianta.scritte import RICHIAMO_MASSIMO_MM
from disegnatore_mep.pianta.tavola import COLORE_FUORI, Linea

from .conftest import CASI, RADICE

Rettangolo = tuple[float, float, float, float]


def _riquadro(s: tuple[float, float, float, float, float]) -> Rettangolo:
    x0, y0, x1, y1, m = s
    return (min(x0, x1) - m, min(y0, y1) - m, max(x0, x1) + m, max(y0, y1) + m)


def _si_toccano(a: Rettangolo, b: Rettangolo) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _richiami(esito: Esito) -> list[tuple[str, float, list[str], list[str]]]:
    """Per richiamo: di chi, quanto e' lungo, che rettangoli attraversa (muri e
    pezzi, salvo il suo e salvo il muro da cui esce di traverso), che linee."""
    out = []
    for tavola in [esito.tavola, *(esito.dettagli or [])]:
        for chi, posata in tavola.scritte:
            if posata.richiamo is None:
                continue
            x0, y0, x1, y1 = posata.richiamo
            s = (x0, y0, x1, y1, 0.09)
            lungo = abs(x1 - x0) + abs(y1 - y0)
            ammessi = tavola.ammessi.get(chi, set())
            rettangoli = []
            for di, r in tavola.rettangoli:
                if di == chi or di in ammessi or not _si_toccano(_riquadro(s), r):
                    continue
                parte_dentro = r[0] <= x0 <= r[2] and r[1] <= y0 <= r[3]
                stretto_e_di_traverso = (
                    di.startswith("muro ") and parte_dentro
                    and ((y0 == y1 and r[2] - r[0] < r[3] - r[1]) or (x0 == x1 and r[3] - r[1] < r[2] - r[0]))
                )
                if not stretto_e_di_traverso:
                    rettangoli.append(di)
            proprie = {f"tratta {t}" for t in chi.split()[1:]} if chi.startswith(("tratta", "fascio")) else set()
            linee = sorted({
                di for di, q in tavola.linee
                if di != f"richiamo:{chi}" and di not in proprie and _si_toccano(_riquadro(s), _riquadro(q))
            })
            out.append((chi, lungo, rettangoli, linee))
    return out


# --- 1. i richiami si misurano ----------------------------------------------------------


@pytest.mark.parametrize("nome", sorted(CASI))
def test_un_richiamo_e_corto_e_non_attraversa_muri_pezzi_ne_piu_di_una_linea(
    esiti: dict[str, Esito], nome: str
) -> None:
    """Collaudo t1, §3: i richiami attraversavano la UI, il fascio frigo, una
    tramezza e mezzo corridoio (58 mm di carta, 2,9 m), e il controllo «scritte
    che toccano una linea: 0» non li vedeva."""
    for chi, lungo, rettangoli, linee in _richiami(esiti[nome]):
        assert lungo <= RICHIAMO_MASSIMO_MM + 1e-6, (chi, lungo)
        assert rettangoli == [], (chi, rettangoli)
        assert len(linee) <= 1, (chi, linee)


def test_il_controllo_conta_i_richiami_e_lo_dice(esiti: dict[str, Esito]) -> None:
    esito = esiti["collaudo"]
    dati = json.loads(next(p for p in esito.file if p.name == "collaudo-t1.tracciati.json").read_text())
    rilievi = dati["rilievi"]
    assert rilievi["richiami"] == len(_richiami(esito))
    assert rilievi["richiamo_massimo_mm"] == RICHIAMO_MASSIMO_MM
    assert rilievi["richiami_su_una_linea"] == sum(1 for *_, linee in _richiami(esito) if linee)
    assert rilievi["richiami_lunghi"] == rilievi["richiami_che_attraversano"] == 0


def test_un_richiamo_lungo_ferma_la_consegna() -> None:
    """La misura non e' una promessa: un richiamo di 3 m che passa un muro,
    messo a mano, il controllo lo trova e lo dice bloccante."""
    from disegnatore_mep.pianta.controlli import _i_richiami
    from disegnatore_mep.pianta.scritte import ScrittaPosata

    rilievi = Rilievi()
    posata = ScrittaPosata("F1", 100.0, 50.0, 8.0, True, (100.0, 47.0, 104.0, 51.0), (40.0, 49.0, 99.0, 49.0))
    _i_richiami(rilievi, carica_pianta(CASI["muro"]), [("foratura F1", posata)], [],
                [("muro tramezza", (60.0, 0.0, 62.0, 200.0))], {})
    assert rilievi.richiami_lunghi and rilievi.richiami_che_attraversano
    assert any("richiami" in b for b in rilievi.bloccanti)


def test_dove_non_c_e_posto_la_scritta_va_in_legenda_numerata(esiti: dict[str, Esito]) -> None:
    """Un numero cerchiato accanto alla linea o al pezzo, e il testo nella
    colonna sotto lo stesso numero: non un richiamo lungo."""
    esito = esiti["collaudo"]
    in_legenda = [s for _, s in esito.tavola.scritte if s.numero is not None]
    assert in_legenda, "il nodo della UI a 1:50 ha almeno una scritta in legenda"
    svg = next(p for p in esito.file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "SCRITTE IN LEGENDA" in svg
    for s in in_legenda:
        assert s.in_legenda and s.in_legenda.replace('"', "&quot;") in svg


# --- 2. le lunghezze sono quelle del progettista ----------------------------------------

DELLA_DISTINTA = {
    "T01": 7, "T02": 5, "T03": 6, "T04": 8.5, "T06": 12, "T07": 12, "T08": 10.5, "T09": 10.5,
    "T10": 22, "T11": 13, "T12": 9.5, "T13": 7, "T14": 11.5, "T15": 8.5,
}
"""La colonna «L quot.» della distinta del collaudo t1
(`lavoro/distinta/tabelle-del-foglio.json`), sullo stesso grafo: la pianta deve
dare gli stessi numeri."""


def test_pianta_e_distinta_danno_lo_stesso_numero(esiti: dict[str, Esito]) -> None:
    """Collaudo t1, §3: T01 era «L 4,5 m» in pianta (dalla misura, 2,9 m) e 7 m
    in distinta (dai 5 m del progettista). Ora la pianta quota i 5 m, con la
    regola della distinta."""
    lunghe = {lu.tratta: lu for lu in esiti["collaudo"].lunghezze}
    assert {t: lunghe[t].da_quotare_m for t in DELLA_DISTINTA} == DELLA_DISTINTA
    testi = [s.in_legenda or s.testo for _, s in esiti["collaudo"].tavola.scritte]
    testi += [s.in_legenda or s.testo for t in esiti["collaudo"].dettagli or [] for _, s in t.scritte]
    assert "T01 · Ø200 · L 7 m" in testi


def test_la_misura_e_un_controllo_e_lo_scarto_si_dice(esiti: dict[str, Esito]) -> None:
    esito = esiti["collaudo"]
    dati = json.loads(next(p for p in esito.file if p.name == "collaudo-t1.tracciati.json").read_text())
    per_tratta = {t["tratta"]: t for t in dati["tratte"]}
    t01 = per_tratta["T01"]
    assert (t01["lunghezza_data_m"], t01["lunghezza_usata_m"], t01["lunghezza_usata_da"]) == (5, 5, "progettista")
    assert t01["lunghezza_misurata_m"] < 5
    for tratta in per_tratta.values():
        if tratta["lunghezza_data_m"]:
            oltre = tratta["lunghezza_misurata_m"] > tratta["lunghezza_data_m"] * 1.15 + 1e-9
            assert tratta["misura_oltre_lo_scarto"] == oltre, tratta["tratta"]
    oltre = [t for t, v in per_tratta.items() if v["misura_oltre_lo_scarto"]]
    assert oltre
    avviso = next(a for a in dati["avvisi"] if a.startswith("Misura oltre"))
    assert all(t in avviso for t in oltre)
    svg = next(p for p in esito.file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "L mis." in svg and "L prog." in svg and "AVVISI" in svg


def test_senza_la_lunghezza_del_progettista_si_quota_la_misura_e_si_dice(esiti: dict[str, Esito]) -> None:
    dati = json.loads(next(p for p in esiti["collaudo"].file if p.name.endswith(".tracciati.json")).read_text())
    t16 = next(t for t in dati["tratte"] if t["tratta"] == "T16")
    assert t16["lunghezza_data_m"] is None and t16["lunghezza_usata_da"] == "misura"
    assert t16["lunghezza_usata_m"] == t16["lunghezza_misurata_m"]
    assert any("T16" in a and "misura" in a for a in dati["avvisi"])


def test_la_regola_e_il_dato_della_distinta_letto_come_lo_legge_lei(
    esiti: dict[str, Esito], tmp_path: Path
) -> None:
    """La pianta non importa la distinta (spenta di default, D-213): ne legge
    il dato. Qui si prova che e' lo stesso dato che legge il caricatore della
    distinta, dalla cartella del repository e dal fascio della skill."""
    from disegnatore_mep.distinta.regole import carica_regole
    from disegnatore_mep.pianta.lunghezze import leggi_la_regola
    from disegnatore_mep.skill import fascio_della_cartella

    regola = esiti["collaudo"].regola
    assert regola is not None and regola.della_distinta
    cartella = RADICE / "rules" / "distinta"
    assert regola.distinta == carica_regole(cartella).lunghezze
    fascio = tmp_path / "distinta.json"
    fascio.write_text(fascio_della_cartella(cartella, "distinta"), encoding="utf-8")
    assert leggi_la_regola(fascio) == carica_regole(fascio).lunghezze


@pytest.mark.parametrize("stimata", [0.0, 0.1, 0.885, 1.4, 2.0, 2.85, 3.0, 4.05, 5.0, 7.0, 8.7, 9.0, 10.0, 18.0, 31.3])
def test_la_formula_della_pianta_e_quella_della_distinta(stimata: float) -> None:
    """Le due formule, valore per valore, con e senza minimi: lo stesso numero
    e lo stesso conto scritto."""
    from disegnatore_mep.distinta import lunghezze as della_distinta
    from disegnatore_mep.pianta import lunghezze as della_pianta

    regola = json.loads((RADICE / "rules" / "distinta" / "lunghezze.json").read_text(encoding="utf-8"))["regola"]
    for minimi in ([], [(12.0, "minimo frigo")], [(5.0, "minimo bus"), (14.0, "segue T06 + 1 m:")]):
        attesa = della_distinta.da_quotare(stimata, regola, [della_distinta.Minimo(m, p) for m, p in minimi])
        valore, calcolo = della_pianta.maggiora(stimata, regola, [della_pianta.Minimo(m, p) for m, p in minimi])
        assert (valore, calcolo) == (attesa.da_quotare, attesa.calcolo)


# --- 3. una tratta attraversa gli organi in linea ----------------------------------------


def test_una_tratta_passa_per_il_sezionatore_con_un_numero_solo(esiti: dict[str, Esito]) -> None:
    """Collaudo t1, §2.2.7: lo schema numera quadro – sezionatore – UE come T10,
    e la pianta voleva «T10b»."""
    esito = esiti["collaudo"]
    t10 = next(p for p in esito.percorsi if p.tratta == "T10")
    assert len(t10.tronchi) == 2
    sz = next(p for p in esito.pianta.pezzi if p.sigla == "SZ-01").rettangolo
    fine_del_primo, inizio_del_secondo = t10.tronchi[0][-1], t10.tronchi[1][0]
    for x, y in (fine_del_primo, inizio_del_secondo):
        assert sz[0] - 1e-6 <= x <= sz[2] + 1e-6 and sz[1] - 1e-6 <= y <= sz[3] + 1e-6
    misurata = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for linea in t10.tronchi for a, b in zip(linea, linea[1:], strict=False))
    assert t10.lunghezza_m == pytest.approx(misurata)
    scritte = [s.in_legenda or s.testo for _, s in esito.tavola.scritte]
    scritte += [s.in_legenda or s.testo for t in esito.dettagli or [] for _, s in t.scritte]
    assert sum(1 for testo in scritte if testo.startswith("T10 ")) == 1
    assert not any(t.tratta.startswith("T10b") for t in esito.pianta.tracciati)
    assert all("/" not in a.tratta for p in esito.percorsi for a in p.attraversamenti)


def test_passa_per_accetta_anche_l_id_del_pezzo(tmp_path: Path) -> None:
    dati = json.loads(CASI["collaudo"].read_text(encoding="utf-8"))
    for pezzo in dati["pezzi"]:
        if pezzo["sigla"] == "SZ-01":
            pezzo["id"] = "sezionatore"
        if pezzo["sigla"] == "QE-01":
            pezzo["id"] = "quadro"
    t10 = next(t for t in dati["tracciati"] if t["tratta"] == "T10")
    t10["passa_per"], t10["da"] = ["sezionatore"], "quadro"
    pianta = Pianta.model_validate(dati)
    t10 = next(t for t in pianta.tracciati if t.tratta == "T10")
    assert (t10.estremo_da.pezzo, t10.passa_per) == ("QE-01", ["SZ-01"])
    t10_rotta = dict(next(t for t in dati["tracciati"] if t["tratta"] == "T10"), passa_per=["non-c-e"])
    dati["tracciati"] = [t10_rotta if t["tratta"] == "T10" else t for t in dati["tracciati"]]
    with pytest.raises(ValueError, match="passa per il pezzo 'non-c-e'"):
        Pianta.model_validate(dati)


# --- 4. il controsoffitto che manca -------------------------------------------------------


def test_le_linee_frigo_passano_dal_controsoffitto_non_dal_soggiorno(esiti: dict[str, Esito]) -> None:
    """Collaudo t1, §3: le linee frigo facevano il giro del soggiorno (7,95 m
    senza controsoffitto, foratura nel muro perimetrale ovest). Ora passano
    dall'ingresso, che il controsoffitto ce l'ha, ed escono sulla facciata
    dell'UE. L'esterno non e' «controsoffitto che manca»: e' la facciata."""
    esito = esiti["collaudo"]
    frigo = [p for p in esito.percorsi if p.tratta in ("T06", "T07", "T11")]
    assert all(p.fuori_dal_controsoffitto_m <= 1.0 for p in frigo), [p.fuori_dal_controsoffitto_m for p in frigo]
    muri_forati = {f.muro for f in esito.forature if "T06" in f.tratte}
    assert "m-ovest" not in muri_forati and "m-sud" in muri_forati


def test_il_tratto_fuori_dal_controsoffitto_si_vede_sulla_tavola(esiti: dict[str, Esito]) -> None:
    """La console lo diceva e la tavola no: ora c'e' la fascia, in legenda e
    negli avvisi."""
    esito = esiti["collaudo"]
    fuori = [p for p in esito.percorsi if p.fuori_dal_controsoffitto_m > 0]
    assert fuori
    fasce = [q for q in esito.tavola.primitive if isinstance(q, Linea) and q.colore == COLORE_FUORI]
    assert len(fasce) >= sum(len(p.fuori) for p in fuori)
    svg = next(p for p in esito.file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "Fuori dal controsoffitto" in svg
    for p in fuori:
        assert sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for t in p.fuori for a, b in zip(t, t[1:], strict=False)) == pytest.approx(
            p.fuori_dal_controsoffitto_m, abs=0.051
        )


def test_l_esterno_e_quello_raggiungibile_dal_bordo_senza_passare_muri() -> None:
    pianta = carica_pianta(CASI["collaudo"])
    g = costruisci_la_griglia(pianta)

    def nodo(x: float, y: float) -> int:
        return g.nodo(round(g.colonna_di(x)), round(g.riga_di(y)))

    assert g.esterno[nodo(2.3, 9.2)]  # il terrazzo, sotto l'UE
    assert not g.esterno[nodo(3.0, 6.5)]  # il soggiorno
    assert not g.esterno[nodo(6.0, 4.3)] or g.pezzo[nodo(6.0, 4.3)]  # il corridoio


def test_l_instradamento_resta_quello_dell_ordine_dichiarato() -> None:
    pianta = carica_pianta(CASI["collaudo"])
    ordine = [t.tratta for t in instrada.ordine_di_instradamento(instrada.tronchi_da_instradare(pianta)[0])]
    assert ordine.index("T10/1") < ordine.index("T10/2")


# --- 5. velette e messaggi d'errore --------------------------------------------------------


def test_una_veletta_scritta_come_una_stanza_dice_il_campo_e_l_esempio(tmp_path: Path) -> None:
    """Collaudo t1, §2.2.5: «velette.0.rettangolo: Field required /
    velette.0.poligono: Extra inputs are not permitted»."""
    dati = json.loads(CASI["collaudo"].read_text(encoding="utf-8"))
    dati["velette"] = [{"id": "v", "poligono": [[0.3, 4.95], [2.3, 4.95], [2.3, 5.45]]}]
    rotta = tmp_path / "rotta.json"
    rotta.write_text(json.dumps(dati), encoding="utf-8")
    with pytest.raises(ErroreDellaPianta) as errore:
        carica_pianta(rotta)
    testo = str(errore.value)
    assert "manca il campo «rettangolo»" in testo and "[x0, y0, x1, y1]" in testo
    assert "il campo «poligono» non c'e'" in testo and "i campi sono: id, rettangolo" in testo
    assert '"rettangolo": [0.30, 4.95, 2.30, 5.45]' in testo
    assert "Field required" not in testo and "Extra inputs" not in testo


# --- 5, 6, 7. le istruzioni ------------------------------------------------------------------

ISTRUZIONI = (RADICE / "skill" / "pianta" / "ISTRUZIONI.md").read_text(encoding="utf-8")


def test_le_istruzioni_dicono_il_formato_delle_velette() -> None:
    assert '"velette": [{"id": "veletta-soggiorno", "rettangolo": [0.30, 4.95, 2.30, 5.45]}]' in ISTRUZIONI


def test_le_istruzioni_accettano_la_planimetria_a_parole() -> None:
    assert "planimetria a parole" in ISTRUZIONI
    assert "misure interne" in ISTRUZIONI


def test_le_istruzioni_dicono_da_dove_vengono_sigle_e_numeri_di_tratta() -> None:
    assert "tabella delle apparecchiature" in ISTRUZIONI
    assert "tabelle-del-foglio.json" in ISTRUZIONI and "distinta.json" in ISTRUZIONI
    for campo in ("lunghezza_m", "passa_per", "dettagli"):
        assert f"`{campo}`" in ISTRUZIONI, campo


def test_la_nota_della_tavola_non_promette_quello_che_non_e_vero(esiti: dict[str, Esito]) -> None:
    """Collaudo t1, §2.2.6: «le sigle e i numeri di tratta sono quelli dello
    schema funzionale» era falso. La nota dice che cosa vale, e lo fa valere
    l'agente."""
    svg = next(p for p in esiti["collaudo"].file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "Sigle e numeri di tratta come lo schema funzionale e la distinta." in svg
    assert "sono quelli dello schema funzionale" not in svg


# --- 8. il nodo fitto ------------------------------------------------------------------------


@pytest.mark.parametrize("nome", sorted(CASI))
def test_nessuna_linea_passa_sopra_un_pezzo_che_non_e_suo(esiti: dict[str, Esito], nome: str) -> None:
    esito = esiti[nome]
    assert esito.rilievi.linee_sui_pezzi == []
    capi = {t.tratta: {t.estremo_da.pezzo, t.estremo_a.pezzo, *t.passa_per} for t in esito.pianta.tracciati}
    pezzi = {p.sigla: p.rettangolo for p in esito.pianta.pezzi}
    for percorso in esito.percorsi:
        for linea in percorso.linee:
            for (ax, ay), (bx, by) in zip(linea, linea[1:], strict=False):
                for sigla, (x0, y0, x1, y1) in pezzi.items():
                    if sigla in capi[percorso.tratta]:
                        continue
                    dentro_x = min(ax, bx) < x1 - 1e-6 and max(ax, bx) > x0 + 1e-6
                    dentro_y = min(ay, by) < y1 - 1e-6 and max(ay, by) > y0 + 1e-6
                    if ax == bx:
                        dentro_x = x0 + 1e-6 < ax < x1 - 1e-6
                    if ay == by:
                        dentro_y = y0 + 1e-6 < ay < y1 - 1e-6
                    assert not (dentro_x and dentro_y), (percorso.tratta, sigla)


def test_il_controllo_trova_una_linea_sopra_un_pezzo() -> None:
    rilievi = Rilievi()
    pianta = carica_pianta(CASI["collaudo"])
    _le_linee_sui_pezzi(rilievi, pianta, [("tratta T12", (10.0, 20.0, 40.0, 20.0, 0.15))],
                        [("pezzo UI-01", (20.0, 15.0, 30.0, 25.0)), ("pezzo TZ-01", (35.0, 18.0, 45.0, 22.0))])
    assert rilievi.linee_sui_pezzi == ["T12 sopra UI-01"]
    assert any("sopra un pezzo" in b for b in rilievi.bloccanti)


def test_dove_1_50_e_troppo_fitto_c_e_il_dettaglio_a_1_20(esiti: dict[str, Esito]) -> None:
    """Il nodo UI + plenum + centrale: le scritte che a 1:50 non stanno vanno in
    un riquadro di dettaglio a 1:20, su una tavola a parte, e la tavola intera
    incornicia la zona e lo dice."""
    esito = esiti["collaudo"]
    assert esito.dettagli and esito.dettagli[0].scala == 20
    assert esito.rilievi.scritte_nel_dettaglio
    nomi = {p.name for p in esito.file}
    assert {"collaudo-t1-dettaglio-A.pdf", "collaudo-t1-dettaglio-A.svg", "collaudo-t1-dettaglio-A.png"} <= nomi
    svg = next(p for p in esito.file if p.name == "collaudo-t1.svg").read_text(encoding="utf-8")
    assert "Dettaglio A 1:20" in svg
    # Le scritte rimandate stanno nel dettaglio, libere.
    nel_dettaglio = {chi for chi, s in esito.dettagli[0].scritte if s.libera}
    for voce in esito.rilievi.scritte_nel_dettaglio:
        assert voce.split(" (dettaglio")[0] in nel_dettaglio


def test_i_dettagli_si_possono_spegnere(tmp_path: Path) -> None:
    dati = json.loads(CASI["collaudo"].read_text(encoding="utf-8"))
    dati["dettagli"] = []
    spenta = tmp_path / "senza-dettagli.json"
    spenta.write_text(json.dumps(dati), encoding="utf-8")
    esito = disegna_la_pianta(spenta, tmp_path, None, dxf=False, png=False)
    assert not esito.dettagli
    assert esito.rilievi.bloccanti, "senza dettaglio il nodo fitto ferma la consegna, e lo dice"
