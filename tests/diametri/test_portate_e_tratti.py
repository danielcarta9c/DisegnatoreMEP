"""La portata di ogni tratto, e il tratto che porta un'etichetta sola (REL-007).

Il PO (I-143, I-153): «serve un solo tag per ogni tratto, anche se ci sono valvole in
mezzo o valvole a tre vie», e «nel caso di piu' generatori in parallelo ne serve uno
per tratta fino al raccordo e uno dopo il raccordo». Qui lo si misura sui grafi
approvati, insieme alle portate che i dati di prova danno: le potenze e i salti termici
dei generatori, le portate dei circolatori e dei confini sanitari.
"""

from collections.abc import Callable

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.calcolatore import portata_da_potenza
from disegnatore_mep.diametri.tratti import TrattoDelDiametro, tratti_del_diametro
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of
from disegnatore_mep.model.project import ProjectModel

Costruttore = Callable[..., ProjectModel]


def _tratto(tratti: tuple[TrattoDelDiametro, ...], da: str, a: str) -> TrattoDelDiametro:
    """Il tratto che va dal pezzo `da` al pezzo `a`, in un verso o nell'altro."""
    trovati = [
        item for item in tratti if {item.capi[0].component_id, item.capi[1].component_id} == {da, a}
    ]
    assert len(trovati) == 1, (
        da,
        a,
        [(t.capi[0].component_id, t.capi[1].component_id) for t in tratti],
    )
    return trovati[0]


def _pezzi_toccati(tratto: TrattoDelDiametro, modello: ProjectModel) -> set[str]:
    connessioni = {item.id: item for item in modello.connections}
    return {
        ref.component_id
        for connection_id in tratto.connection_ids
        for ref in (connessioni[connection_id].endpoint_a, connessioni[connection_id].endpoint_b)
    }


def test_con_due_generatori_un_tratto_fino_al_raccordo_e_uno_dopo(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 1: due pompe di calore da 15 kW che si uniscono sul raccordo di
    mandata e si dividono su quello di ritorno."""
    tratti = tratti_del_diametro(modello("1"), catalogo)
    q = portata_da_potenza(15, 5)
    for pdc in ("pdc-master", "pdc-slave"):
        for tratto in (
            _tratto(tratti, pdc, "collettore-mandata"),
            _tratto(tratti, "collettore-ritorno", pdc),
        ):
            assert tratto.portata_m3h == pytest.approx(q)
            assert tratto.diametro is not None and tratto.diametro.dn == 32
            assert tratto.potenza_kw == pytest.approx(15)
    for tratto in (
        _tratto(tratti, "collettore-mandata", "accumulo"),
        _tratto(tratti, "accumulo", "collettore-ritorno"),
    ):
        assert tratto.portata_m3h == pytest.approx(2 * q)
        assert tratto.diametro is not None and tratto.diametro.dn == 40
        assert tratto.potenza_kw == pytest.approx(30)


def test_la_cascata_si_somma_a_ogni_raccordo(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 5: tre pompe di calore da 40 kW. Ogni ramo la sua, fra i due raccordi
    due, dopo il secondo tutte e tre — sulla mandata e sul ritorno."""
    tratti = tratti_del_diametro(modello("5"), catalogo)
    q = portata_da_potenza(40, 5)
    assert _tratto(tratti, "pdc-1", "cascata-mandata-b").portata_m3h == pytest.approx(q)
    assert _tratto(tratti, "pdc-2", "cascata-mandata-a").portata_m3h == pytest.approx(q)
    assert _tratto(tratti, "pdc-3", "cascata-mandata-a").portata_m3h == pytest.approx(q)
    fra = _tratto(tratti, "cascata-mandata-a", "cascata-mandata-b")
    assert fra.portata_m3h == pytest.approx(2 * q)
    assert fra.diametro is not None and fra.diametro.dn == 50
    tutte = _tratto(tratti, "cascata-mandata-b", "volano")
    assert tutte.portata_m3h == pytest.approx(3 * q)
    assert tutte.diametro is not None and tutte.diametro.dn == 65
    assert _tratto(tratti, "cascata-ritorno-a", "cascata-ritorno-b").portata_m3h == pytest.approx(
        2 * q
    )


def test_valvole_e_valvole_a_tre_vie_non_spezzano_il_tratto(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """I-143. Impianto 2: dalla pompa di calore al volano si passa per la
    derivazione della sicurezza, una valvola e la deviatrice — un tratto solo, e il
    ramo della deviatrice verso il bollitore e' un tratto suo. Impianto 5: dal
    ripartitore al pannello si passa per la miscelatrice e il circolatore — uno
    solo. Impianto 4: dal raccordo di ritorno alla caldaia si passa per la
    commutatrice — uno solo."""
    m2 = modello("2")
    tratti = tratti_del_diametro(m2, catalogo)
    dritto = _tratto(tratti, "pdc", "volano")
    assert len(dritto.chiavi) == 3
    assert {"deviatrice", "tee-valve-safety-pdc-water-supply"} <= _pezzi_toccati(dritto, m2)
    ramo = _tratto(tratti, "deviatrice", "bollitore")
    assert ramo.portata_m3h == pytest.approx(dritto.portata_m3h)

    m5 = modello("5")
    radiante = _tratto(tratti_del_diametro(m5, catalogo), "secondario-mandata-b", "pavimento-radiante")
    assert {"miscelatrice-radiante", "circolatore-radiante"} <= _pezzi_toccati(radiante, m5)

    m4 = modello("4")
    caldaia = _tratto(tratti_del_diametro(m4, catalogo), "collettore-ritorno", "caldaia")
    assert "commutatrice-ritorno" in _pezzi_toccati(caldaia, m4)


def test_i_rami_di_servizio_non_sono_tratti_e_non_portano_il_dn(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """D-193, punto 7: sicurezze, vasi, riempimento, strumenti, scarichi — lo stacco
    su cui pendono non porta portata e non porta il DN."""
    for impianto in ("1", "5", "6"):
        m = modello(impianto)
        trunks = tratte_del_progetto(m, catalogo)
        livelli = hierarchy_of(m, catalogo, trunks)
        di_servizio = {
            connection_id
            for trunk in trunks
            if livelli[trunk.connection_ids] is Level.SERVIZIO
            for connection_id in trunk.connection_ids
        }
        assert di_servizio, impianto
        for tratto in tratti_del_diametro(m, catalogo):
            assert not tratto.connection_ids & di_servizio, impianto


def test_le_tre_vie_si_provano_in_ogni_posizione(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 4: la caldaia manda al collettore o allo scambiatore, e riprende dal
    collettore o dallo scambiatore. Le posizioni che i dati non reggono si scartano;
    in quelle che reggono ogni tratto prende la portata piu' grande — tutta quella
    della caldaia, da qualunque parte vada."""
    tratti = tratti_del_diametro(modello("4"), catalogo)
    caldaia = portata_da_potenza(25, 10)
    pdc = portata_da_potenza(16, 5)
    assert _tratto(tratti, "deviatrice-caldaia", "scambiatore").portata_m3h == pytest.approx(caldaia)
    assert _tratto(tratti, "scambiatore", "commutatrice-ritorno").portata_m3h == pytest.approx(caldaia)
    assert _tratto(tratti, "caldaia", "collettore-mandata").portata_m3h == pytest.approx(caldaia)
    assert _tratto(tratti, "collettore-mandata", "disgiuntore").portata_m3h == pytest.approx(
        caldaia + pdc
    )


def test_la_miscelatrice_dimensiona_il_bipasso_sulla_portata_piena(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 5: nelle due posizioni estreme la miscelatrice prende tutto dalla
    mandata o tutto dal bipasso, e il bipasso porta la portata del circolatore."""
    tratti = tratti_del_diametro(modello("5"), catalogo)
    assert _tratto(tratti, "ritorno-radiante", "miscelatrice-radiante").portata_m3h == pytest.approx(5)
    assert _tratto(tratti, "secondario-mandata-b", "pavimento-radiante").portata_m3h == pytest.approx(5)
    assert _tratto(tratti, "secondario-mandata-a", "secondario-mandata-b").portata_m3h == pytest.approx(
        3.2 + 5
    )


def test_il_solare_prende_la_portata_del_circolatore_all_andata_e_al_ritorno(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 6: il circolatore solare sta sul ritorno ai collettori, e la sua
    portata attraversa il collettore e il serpentino: l'andata la porta uguale."""
    tratti = tratti_del_diametro(modello("6"), catalogo)
    solari = {
        (ref.component_id, ref.port_id): item
        for item in tratti
        for ref in item.capi
        if ref.component_id == "collettore-solare"
    }
    andata = solari[("collettore-solare", "supply")]
    ritorno = solari[("collettore-solare", "return")]
    assert andata is not ritorno
    assert andata.portata_m3h == pytest.approx(1.2)
    assert ritorno.portata_m3h == pytest.approx(1.2)
    assert andata.fonti == ("circolatore-solare",)
    assert andata.diametro is not None and andata.diametro.dn == 20


def test_il_sanitario_prende_la_portata_di_progetto_delle_utenze(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """I-157: acqua fredda, calda e ricircolo dalla portata del progettista."""
    tratti = tratti_del_diametro(modello("5"), catalogo)
    acs = _tratto(tratti, "bollitore", "utenze")
    assert acs.portata_m3h == pytest.approx(2)
    assert acs.diametro is not None and acs.diametro.dn == 25
    assert _tratto(tratti, "acquedotto", "bollitore").portata_m3h == pytest.approx(2)
    ricircolo = _tratto(tratti, "bollitore", "ricircolo-utenze")
    assert ricircolo.portata_m3h == pytest.approx(0.8)
    assert ricircolo.diametro is not None and ricircolo.diametro.dn == 20


def test_deterministico(modello: Costruttore, catalogo: ComponentRegistry) -> None:
    for impianto in ("1", "4", "5", "6"):
        assert tratti_del_diametro(modello(impianto), catalogo) == tratti_del_diametro(
            modello(impianto), catalogo
        )
