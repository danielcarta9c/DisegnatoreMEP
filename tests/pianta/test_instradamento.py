"""L'instradatore della pianta: la regola del PO (I-229), misurata.

«i sormonti fra linee si pagano, si pagano le curve, anche i tratti diagonali
NON si fanno mai + importante seguire le macro linee architettoniche».
"""

from pathlib import Path

import pytest

from disegnatore_mep.pianta import instrada
from disegnatore_mep.pianta.comando import Esito, forature
from disegnatore_mep.pianta.controlli import controlla, diagonale, segmenti
from disegnatore_mep.pianta.griglia import costruisci_la_griglia
from disegnatore_mep.pianta.modello import Pianta, carica_pianta

from .conftest import CASI


@pytest.mark.parametrize("nome", sorted(CASI))
def test_mai_un_tratto_diagonale(esiti: dict[str, Esito], nome: str) -> None:
    """Vincolo duro, e si misura sulla tavola: tracciati e richiami."""
    esito = esiti[nome]
    assert esito.rilievi.diagonali == []
    for percorso in esito.percorsi:
        assert not any(diagonale(a, b) for a, b in segmenti(percorso.punti)), percorso.tratta
    for chi, (x0, y0, x1, y1, _) in esito.tavola.linee:
        if chi.startswith(("tratta", "richiamo")):
            assert not diagonale((x0, y0), (x1, y1)), chi


@pytest.mark.parametrize("nome", sorted(CASI))
def test_nessuna_sovrapposizione_e_nessuna_tratta_ceduta(esiti: dict[str, Esito], nome: str) -> None:
    rilievi = esiti[nome].rilievi
    assert rilievi.sovrapposizioni == []
    assert rilievi.tratte_cedute == []


def test_il_percorso_segue_il_muro_quando_c_e_una_corsia(esiti: dict[str, Esito]) -> None:
    """Nel corridoio largo 1,2 m, fra due pezzi contro il muro nord, il canale
    sta nella corsia lungo il muro — fra 15 e 30 cm dalla faccia —, non in mezzo."""
    esito = esiti["corridoio"]
    t01 = next(p for p in esito.percorsi if p.tratta == "T01")
    griglia = costruisci_la_griglia(esito.pianta)
    parametri = esito.pianta.parametri
    nella_corsia = [
        parametri.corsia_da_m - 1e-9 <= griglia.distanza[k] * griglia.passo <= parametri.corsia_a_m + 1e-9
        for k in t01.nodi
    ]
    assert sum(nella_corsia) / len(nella_corsia) >= 0.9


def test_il_sormonto_obbligato_e_uno_solo(esiti: dict[str, Esito]) -> None:
    """T01 e T02 hanno i capi alternati su due muri: si incrociano per forza, una volta."""
    sormonti = esiti["incrocio"].rilievi.sormonti
    assert [s for s in sormonti if s.startswith("T01 × T02")] and len(sormonti) == 1


def test_un_sormonto_evitabile_non_c_e(esiti: dict[str, Esito]) -> None:
    """Dal plenum, il ramo lontano non sbarra la strada al ramo vicino."""
    assert not [s for s in esiti["incrocio"].rilievi.sormonti if "T03" in s or "T04" in s]


def test_senza_il_ripasso_il_sormonto_evitabile_torna(monkeypatch: pytest.MonkeyPatch) -> None:
    """La prova che il ripasso serve: al primo giro il ramo lontano prende la
    corsia, e il vicino lo deve sormontare."""
    monkeypatch.setattr(instrada, "GIRI_DI_RIPASSO", 0)
    pianta = carica_pianta(CASI["incrocio"])
    percorsi = instrada.instrada_tutto(pianta, costruisci_la_griglia(pianta))
    sormonti = controlla(pianta, percorsi, [], [], [], []).sormonti
    assert any("T03 × T04" in s for s in sormonti)


def test_il_fascio_corre_parallelo(esiti: dict[str, Esito]) -> None:
    """Tre linee frigo fra le stesse macchine: accanto, al passo del fascio,
    e mai incrociate fra loro."""
    for nome, membri in (("corridoio", ("T02", "T03", "T04")), ("appartamento", ("T07", "T08", "T09"))):
        esito = esiti[nome]
        assert esito.rilievi.fasci["frigo"] >= 0.95, nome
        assert not [s for s in esito.rilievi.sormonti if s[:3] in membri and s[6:9] in membri]
        nodi = [set(p.nodi) for p in esito.percorsi if p.tratta in membri]
        assert all(not (a & b) for i, a in enumerate(nodi) for b in nodi[i + 1:])


def test_un_muro_senza_aperture_si_fora_e_lo_dice(esiti: dict[str, Esito]) -> None:
    esito = esiti["muro"]
    assert [(f.muro, f.tratte) for f in esito.forature] == [("tramezza", ("T01",))]
    assert len(esito.rilievi.fori_fuori_dalle_aperture) == 1


def test_un_foro_dichiarato_si_usa_invece_di_forare() -> None:
    dati = carica_pianta(CASI["muro"]).model_dump()
    dati["aperture"] = [
        {"id": "foro", "muro": "tramezza", "centro": [4.0, 0.6], "larghezza": 0.3, "tipo": "foro"}
    ]
    pianta = Pianta.model_validate(dati)
    percorsi = instrada.instrada_tutto(pianta, costruisci_la_griglia(pianta))
    assert forature(pianta, percorsi) == []
    assert [a.apertura for a in percorsi[0].attraversamenti] == ["foro"]


def test_una_porta_non_e_un_passaggio_per_il_controsoffitto() -> None:
    """Sopra la porta c'e' l'architrave: un canale in controsoffitto la fora,
    un cavo in traccia ci passa."""
    dati = carica_pianta(CASI["muro"]).model_dump()
    dati["aperture"] = [
        {"id": "porta", "muro": "tramezza", "centro": [4.0, 1.5], "larghezza": 0.9, "tipo": "porta"}
    ]
    dati["tracciati"].append(
        {"tratta": "T02", "da": "A", "a": "B", "fluido": "control_bus", "quota": "traccia"}
    )
    pianta = Pianta.model_validate(dati)
    percorsi = instrada.instrada_tutto(pianta, costruisci_la_griglia(pianta))
    canale, cavo = percorsi
    assert [a.forato for a in canale.attraversamenti] == [True]
    assert [(a.apertura, a.forato) for a in cavo.attraversamenti] == [("porta", False)]


def test_l_ordine_e_dichiarato_e_stabile() -> None:
    """Prima i canali, poi i tubi, la condensa, i cavi, il bus; a parita', per tratta."""
    pianta = carica_pianta(CASI["appartamento"])
    ordine = [t.tratta for t in instrada.ordine_di_instradamento(pianta.tracciati)]
    assert ordine[:6] == ["T01", "T02", "T03", "T04", "T05", "T06"]
    assert ordine.index("T07") < ordine.index("T10") < ordine.index("T11") < ordine.index("T14")
    assert ordine == [t.tratta for t in instrada.ordine_di_instradamento(list(reversed(pianta.tracciati)))]


def test_la_pianta_inventata_non_e_del_cliente() -> None:
    """Il caso di prova e' inventato: niente catastale, niente raster."""
    pianta = carica_pianta(CASI["appartamento"])
    assert pianta.sfondo is None
    assert "inventata" in " ".join(pianta.note)
    assert not list(Path(CASI["appartamento"]).parent.glob("*.png"))
