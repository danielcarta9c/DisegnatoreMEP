"""REL-026, blocco C: le scritte che non stanno in pianta vanno fuori (C-1), e due tubi
che corrono insieme hanno una scritta sola (C-2).

LEGGIMI M2 di BD.RM.260, il PO: «Niente tavole di dettaglio aperte in automatico per far
stare le scritte. Quando una scritta non sta in pianta va nello spazio bianco fuori dalla
pianta, collegata al pezzo con una linea di richiamo, incolonnata e senza incroci. I
numeri cerchiati con il testo in legenda RESTANO. Il riquadro di dettaglio solo se lo
chiede il progettista. Utile anche: una scritta unica per due tubi che corrono insieme
(M1/R1).»

Ogni prova misura sulla tavola finita con un conto suo, salvo dove la prova e' che la
tavola lo dica.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.pianta import tavola as modulo_tavola
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.controlli import Rilievi, _i_richiami_fuori
from disegnatore_mep.pianta.fuori_pianta import PASSO_MM, STACCO_MM, Fuori
from disegnatore_mep.pianta.scritte import ScrittaPosata, affiancate
from disegnatore_mep.pianta.tavola import FASCIA_DELLA_SCALA_MM, Tavola, estensione

from .conftest import CASI

Rettangolo = tuple[float, float, float, float]
Punto = tuple[float, float]


def _pianta_sulla_carta(esito: Esito, tavola: Tavola) -> Rettangolo:
    """L'ingombro del disegno sulla carta: muri, pezzi, zone esterne, tracciati."""
    ox, oy, xmin, ymin, k = tavola.trasforma
    x0, y0, x1, y1 = estensione(esito.pianta, esito.percorsi)
    return (ox, oy, ox + (x1 - x0) * k, oy + (y1 - y0) * k)


def _fuori(tavola: Tavola) -> list[tuple[str, ScrittaPosata]]:
    return [(chi, s) for chi, s in tavola.scritte if s.richiamo_fuori is not None]


def _si_toccano(a: Rettangolo, b: Rettangolo) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _segmenti(punti: tuple[Punto, ...]) -> list[tuple[Punto, Punto]]:
    return list(zip(punti, punti[1:], strict=False))


def _riquadro(a: Punto, b: Punto, mezzo: float = 0.09) -> Rettangolo:
    return (min(a[0], b[0]) - mezzo, min(a[1], b[1]) - mezzo, max(a[0], b[0]) + mezzo, max(a[1], b[1]) + mezzo)


def _sul_bordo(p: Punto, r: Rettangolo, tolleranza: float = 0.01) -> bool:
    dentro = r[0] - tolleranza <= p[0] <= r[2] + tolleranza and r[1] - tolleranza <= p[1] <= r[3] + tolleranza
    return dentro and min(abs(p[0] - r[0]), abs(p[0] - r[2]), abs(p[1] - r[1]), abs(p[1] - r[3])) <= tolleranza


def _sulla_linea(p: Punto, linee: list[list[Punto]]) -> bool:
    for punti in linee:
        for a, b in _segmenti(tuple(punti)):
            if (abs(a[0] - b[0]) < 1e-6 and abs(p[0] - a[0]) < 0.01 and min(a[1], b[1]) - 0.01 <= p[1] <= max(a[1], b[1]) + 0.01) or (
                abs(a[1] - b[1]) < 1e-6 and abs(p[1] - a[1]) < 0.01 and min(a[0], b[0]) - 0.01 <= p[0] <= max(a[0], b[0]) + 0.01
            ):
                return True
    return False


# --- C-1: i dettagli solo se chiesti -------------------------------------------------------------


@pytest.mark.parametrize("nome", sorted(CASI))
def test_nessun_riquadro_di_dettaglio_nasce_da_solo(esiti: dict[str, Esito], nome: str) -> None:
    esito = esiti[nome]
    dichiarati = [d.id for d in esito.pianta.dettagli or []]
    assert [t.cartiglio is not None for t in esito.dettagli or []] == [True] * len(dichiarati) or not dichiarati
    assert len(esito.dettagli or []) == len(dichiarati)
    if not dichiarati:
        assert not any("-dettaglio-" in p.name for p in esito.file)


# --- C-1: fuori dalla pianta, incolonnate, senza incroci -----------------------------------------


@pytest.mark.parametrize("nome", sorted(CASI))
def test_le_scritte_fuori_stanno_fuori_dalla_pianta_e_dentro_il_campo(esiti: dict[str, Esito], nome: str) -> None:
    esito = esiti[nome]
    tavola = esito.tavola
    pianta = _pianta_sulla_carta(esito, tavola)
    area = tavola.frame.drawing_rect_mm
    for chi, posata in _fuori(tavola):
        r = posata.riquadro
        assert not _si_toccano(r, pianta), (nome, chi, r, pianta)
        assert area.x_mm <= r[0] and r[2] <= area.right_mm, (nome, chi)
        assert area.y_mm <= r[1] and r[3] <= area.y_mm + area.height_mm - FASCIA_DELLA_SCALA_MM, (nome, chi)


@pytest.mark.parametrize("nome", sorted(CASI))
def test_il_richiamo_fuori_parte_dal_suo_oggetto_ed_e_ortogonale_con_al_piu_un_gomito(
    esiti: dict[str, Esito], nome: str
) -> None:
    esito = esiti[nome]
    tavola = esito.tavola
    pezzi = {di[len("pezzo "):]: r for di, r in tavola.rettangoli if di.startswith("pezzo ")}
    ox, oy, xmin, ymin, k = tavola.trasforma
    for chi, posata in _fuori(tavola):
        punti = posata.richiamo_fuori
        assert punti is not None and 2 <= len(punti) <= 3, (chi, punti)
        for a, b in _segmenti(punti):
            assert abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6, (chi, "obliquo", a, b)
        # Arriva sul bordo della scritta, parte dal suo oggetto.
        assert _sul_bordo(punti[-1], posata.riquadro), (chi, punti[-1], posata.riquadro)
        tipo, _, resto = chi.partition(" ")
        if tipo == "pezzo":
            assert _sul_bordo(punti[0], pezzi[resto]), (chi, punti[0])
        else:
            tratte = resto.split()
            linee = [
                [((q[0] - xmin) * k + ox, (q[1] - ymin) * k + oy) for q in linea]
                for p in esito.percorsi if p.tratta in tratte for linea in p.linee
            ]
            assert _sulla_linea(punti[0], linee), (chi, punti[0])


@pytest.mark.parametrize("nome", sorted(CASI))
def test_le_scritte_fuori_sono_incolonnate(esiti: dict[str, Esito], nome: str) -> None:
    """A destra della pianta allineate a sinistra, a sinistra allineate a destra, tutte a
    `STACCO_MM` dalla pianta e su una griglia a passo fisso; sopra e sotto su righe a
    passo fisso dalla pianta."""
    esito = esiti[nome]
    tavola = esito.tavola
    pianta = _pianta_sulla_carta(esito, tavola)
    alto = tavola.frame.drawing_rect_mm.y_mm + 2.0
    for chi, posata in _fuori(tavola):
        punti = posata.richiamo_fuori
        assert punti is not None
        a, b = punti[-2], punti[-1]
        r = posata.riquadro
        if abs(a[1] - b[1]) < 1e-6:  # arriva di fianco: una colonna
            mezzo = b[1]
            assert abs((mezzo - alto) / PASSO_MM - 0.5 - round((mezzo - alto) / PASSO_MM - 0.5)) < 1e-3, (chi, mezzo)
            if b[0] > a[0]:
                assert abs(posata.x - (pianta[2] + STACCO_MM)) < 1e-3, (chi, "a destra, allineata a sinistra")
            else:
                assert abs(r[2] - 0.5 - (pianta[0] - STACCO_MM)) < 1e-3, (chi, "a sinistra, allineata a destra")
        else:  # arriva da sotto o da sopra: una riga
            if b[1] < a[1]:
                righe = (pianta[1] - STACCO_MM - b[1]) / PASSO_MM
            else:
                righe = (b[1] - pianta[3] - STACCO_MM) / PASSO_MM
            assert abs(righe - round(righe)) < 1e-3, (chi, righe)


@pytest.mark.parametrize("nome", sorted(CASI))
def test_i_richiami_non_si_incrociano(esiti: dict[str, Esito], nome: str) -> None:
    """Fra loro, e con i richiami corti: misurato sui segmenti, non letto dai rilievi."""
    tavola = esiti[nome].tavola
    tutti: list[tuple[str, Rettangolo]] = []
    for chi, posata in tavola.scritte:
        if posata.richiamo is not None:
            x0, y0, x1, y1 = posata.richiamo
            tutti.append((chi, _riquadro((x0, y0), (x1, y1))))
        if posata.richiamo_fuori is not None:
            tutti += [(chi, _riquadro(a, b)) for a, b in _segmenti(posata.richiamo_fuori)]
    for indice, (chi, r) in enumerate(tutti):
        for altro, q in tutti[indice + 1:]:
            if chi != altro and (chi in {c for c, _ in _fuori(tavola)} or altro in {c for c, _ in _fuori(tavola)}):
                assert not _si_toccano(r, q), (nome, chi, altro)
    assert esiti[nome].rilievi.richiami_che_si_incrociano == []


def test_i_numeri_in_legenda_restano(esiti: dict[str, Esito]) -> None:
    """I numeri cerchiati col testo in legenda «piacciono»: dove la scritta non sta
    accanto ma il numero si', resta il numero; fuori va solo quello che prima apriva il
    dettaglio."""
    for nome in ("collaudo", "collaudo-t3", "appartamento", "fitta"):
        assert esiti[nome].rilievi.scritte_in_legenda, nome


def test_nel_caso_fitto_le_scritte_vanno_fuori_e_il_foglio_non_cresce(esiti: dict[str, Esito]) -> None:
    """La centrale nel locale tecnico: sette scritte non ci stanno nemmeno come numero.
    Fuori, sul foglio A3: la pianta si sposta da una parte e il margine verso la centrale
    raddoppia, invece di passare all'A2."""
    esito = esiti["fitta"]
    assert esito.tavola.formato == "A3"
    assert len(esito.rilievi.scritte_fuori_pianta) >= 5
    assert esito.rilievi.bloccanti == []
    pianta = _pianta_sulla_carta(esito, esito.tavola)
    area = esito.tavola.frame.drawing_rect_mm
    sinistra, destra = pianta[0] - area.x_mm, area.right_mm - pianta[2]
    assert sinistra > destra + 10, (sinistra, destra)
    dati = json.loads(next(p for p in esito.file if p.name == "centrale-fitta.tracciati.json").read_text())
    assert dati["rilievi"]["scritte_fuori_pianta"] == len(esito.rilievi.scritte_fuori_pianta)
    assert dati["rilievi"]["richiami_che_si_incrociano"] == 0


def test_il_controllo_trova_due_richiami_fuori_che_si_incrociano() -> None:
    """La misura non e' una promessa: due richiami fuori messi a mano a croce, il
    controllo li trova e ferma la consegna."""
    rilievi = Rilievi()
    a = ScrittaPosata("A", 200.0, 20.0, 8.0, False, (199.5, 17.0, 210.0, 21.0),
                      richiamo_fuori=((100.0, 60.0), (100.0, 19.0), (199.5, 19.0)))
    b = ScrittaPosata("B", 200.0, 40.0, 8.0, False, (199.5, 37.0, 210.0, 41.0),
                      richiamo_fuori=((80.0, 39.0), (199.5, 39.0)))
    _i_richiami_fuori(rilievi, [("tratta T01", a), ("tratta T02", b)], [], {})
    assert len(rilievi.scritte_fuori_pianta) == 2
    assert rilievi.richiami_che_si_incrociano
    assert any("si incrociano" in voce for voce in rilievi.bloccanti)


def _senza_posto_sull_a3(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fuori dalla pianta non c'e' posto se il campo del disegno e' quello dell'A3."""
    vera = modulo_tavola.posa_fuori

    def finta(richieste: Any, ingombri: Any, pianta: Any, area: Any, *altri: Any) -> Fuori:
        if area[2] - area[0] < 300:
            return Fuori([None] * len(richieste), [None] * len(richieste))
        return vera(richieste, ingombri, pianta, area, *altri)

    monkeypatch.setattr(modulo_tavola, "posa_fuori", finta)


def test_se_fuori_non_c_e_posto_la_tavola_passa_al_formato_dopo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """La regola con cui il foglio si allarga: prima la pianta si sposta, poi il formato
    successivo con la stessa scala, come per la colonna che non entra."""
    _senza_posto_sull_a3(monkeypatch)
    esito = disegna_la_pianta(CASI["collaudo"], tmp_path, None, dxf=False, png=False)
    assert esito.tavola.formato == "A2" and esito.tavola.scala == 50
    assert esito.rilievi.scritte_fuori_pianta and esito.rilievi.bloccanti == []


def test_a_formato_fissato_la_scritta_senza_posto_si_conta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _senza_posto_sull_a3(monkeypatch)
    dati = json.loads(CASI["collaudo"].read_text(encoding="utf-8"))
    dati["foglio"] = {"formato": "A3", "scala": 50}
    sorgente = tmp_path / "a3.json"
    sorgente.write_text(json.dumps(dati), encoding="utf-8")
    esito = disegna_la_pianta(sorgente, tmp_path, None, dxf=False, png=False)
    assert esito.tavola.formato == "A3"
    assert not all(s.libera for _, s in esito.tavola.scritte)
    assert esito.rilievi.bloccanti, "la scritta senza posto resta dove era provata, e il controllo la conta"


# --- C-2: una scritta per due tubi che corrono insieme --------------------------------------------


def _testi(esito: Esito) -> list[str]:
    return [s.in_legenda or s.testo for chi, s in esito.tavola.scritte if chi.startswith(("tratta", "fascio"))]


def test_due_tubi_che_corrono_insieme_hanno_una_scritta_sola(esiti: dict[str, Esito]) -> None:
    """Mandata e ritorno di FC-02, senza fascio: corrono insieme, una scritta con le due
    sigle, la dimensione e la lunghezza una volta."""
    esito = esiti["fitta"]
    testi = _testi(esito)
    assert "T05/T06 · MS 16 · L 11 m" in testi
    assert not any(t.startswith(("T05 ", "T06 ")) for t in testi)
    chi = [c for c, _ in esito.tavola.scritte]
    assert "fascio T05 T06" in chi or "fascio T06 T05" in chi


def test_la_coppia_di_un_fascio_dice_la_dimensione_una_volta(esiti: dict[str, Esito]) -> None:
    assert "T01/T02 · MS 26 · L 1,5 m" in _testi(esiti["fitta"])
    assert "T03/T04 · MS 16 · L 6 m" in _testi(esiti["fitta"])
    lunghe = {lu.tratta: lu for lu in esiti["sagome"].lunghezze}
    misura = f"{lunghe['T01'].misurata_m:.1f}".replace(".", ",")
    assert any(t.startswith("T01/T02 · MS 26 · L ") for t in _testi(esiti["sagome"])), misura


def test_due_tubi_che_non_corrono_insieme_hanno_ciascuno_la_sua(esiti: dict[str, Esito]) -> None:
    """Mandata e ritorno di FC-04, senza fascio, che l'instradatore porta per strade
    diverse: due scritte, perche' una sola direbbe che corrono insieme."""
    esito = esiti["fitta"]
    linee = {p.tratta: p.linee for p in esito.percorsi}
    assert affiancate(linee["T09"], linee["T10"], 0.2, 0.05) < 0.8
    testi = _testi(esito)
    assert any(t.startswith("T09 · MS 16") for t in testi) and any(t.startswith("T10 · MS 16") for t in testi)


@pytest.mark.parametrize("cambia", ["dimensione", "lunghezza_m"])
def test_non_si_uniscono_tratte_con_dimensione_o_lunghezza_diverse(tmp_path: Path, cambia: str) -> None:
    dati = json.loads(CASI["fitta"].read_text(encoding="utf-8"))
    t06 = next(t for t in dati["tracciati"] if t["tratta"] == "T06")
    t06[cambia] = "MS 20" if cambia == "dimensione" else 12
    sorgente = tmp_path / "diversa.json"
    sorgente.write_text(json.dumps(dati, ensure_ascii=False), encoding="utf-8")
    esito = disegna_la_pianta(sorgente, tmp_path, None, dxf=False, png=False)
    testi = _testi(esito)
    assert not any(t.startswith("T05/T06") for t in testi)
    assert any(t.startswith("T05 · ") for t in testi) and any(t.startswith("T06 · ") for t in testi)


def test_affiancate_misura_la_parte_che_corre_insieme() -> None:
    a = [[(0.0, 0.0), (10.0, 0.0)]]
    accanto = [[(0.0, 0.1), (10.0, 0.1)]]
    meta = [[(0.0, 0.1), (5.0, 0.1), (5.0, 3.0)]]
    lontana = [[(0.0, 1.0), (10.0, 1.0)]]
    assert affiancate(a, accanto, 0.2, 0.05) == pytest.approx(1.0)
    assert affiancate(a, lontana, 0.2, 0.05) == 0.0
    assert 0.3 < affiancate(a, meta, 0.2, 0.05) < 0.6
