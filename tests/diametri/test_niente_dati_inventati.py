"""Il DN non inventa niente, e compare solo dove il progettista lo chiede (REL-007).

D-087 regge per tutto tranne i diametri, e per i diametri D-191 dice come: il
calcolatore **calcola dai dati del progettista**. Quindi: senza la sua richiesta
nessun tratto porta il DN; senza i suoi dati quel tratto non lo porta; una rete
esistente non lo porta mai (I-145). E un grafo scritto prima di REL-007 non cambia di
un byte.
"""

import json
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.tratti import tratti_da_etichettare, tratti_del_diametro
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.model.project import ProjectModel

from .conftest import APPROVATI, IMPIANTI, IMPIANTO_6, documento

Costruttore = Callable[..., ProjectModel]


def test_senza_la_richiesta_nessun_tratto_porta_il_dn(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Con tutti i dati — potenze, salti termici, portate —, ma senza richiesta."""
    for impianto in IMPIANTI:
        m = modello(impianto, con_la_richiesta=False)
        assert m.diametri is None
        assert tratti_da_etichettare(m, catalogo) == ()
        assert not any(item.porta_il_dn for item in tratti_del_diametro(m, catalogo))


def test_senza_salto_termico_la_potenza_non_basta(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Impianto 1 con le potenze delle pompe di calore e senza i loro salti termici:
    il primario resta senza DN, e il perche' e' scritto."""
    testo = documento("1")
    for pezzo in testo["components"]:
        pezzo["properties"].pop("delta_t_k", None)
    m = ProjectModel.model_validate(testo)
    primario = [item for item in tratti_del_diametro(m, catalogo) if item.reti == ("primario",)]
    assert primario
    for tratto in primario:
        assert tratto.portata_m3h is None and not tratto.porta_il_dn
        assert tratto.perche_senza_dn == "la portata non viene dai dati del progettista"
    etichettati = tratti_da_etichettare(m, catalogo)
    assert all("primario" not in item.reti for item in etichettati)


def test_il_solare_non_si_dimensiona_con_la_potenza(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """I-157: il fluido solare non e' acqua, e la sua portata la da' il progettista.
    Con potenza e salto termico sul collettore e senza la portata del circolatore,
    il circuito solare resta senza DN."""
    testo = documento("6")
    for pezzo in testo["components"]:
        if pezzo["id"] == "collettore-solare":
            pezzo["properties"].update({"power_kw": 10, "delta_t_k": 10})
        if pezzo["id"] == "circolatore-solare":
            pezzo["properties"].pop("flow_rate_m3h", None)
    m = ProjectModel.model_validate(testo)
    solari = [item for item in tratti_del_diametro(m, catalogo) if item.reti == ("circuito-solare",)]
    assert solari and all(item.portata_m3h is None for item in solari)


def test_una_rete_esistente_si_disegna_senza_dn(
    modello: Costruttore, catalogo: ComponentRegistry
) -> None:
    """Il retrofit (I-145): la centrale si progetta, la distribuzione esistente no."""
    m = modello("1", variante="1-retrofit")
    assert {item.id for item in m.networks if item.esistente} == {"secondario", "sanitaria"}
    tratti = tratti_del_diametro(m, catalogo)
    esistenti = [item for item in tratti if set(item.reti) & {"secondario", "sanitaria"}]
    assert esistenti
    assert all(not item.porta_il_dn and item.perche_senza_dn == "rete esistente" for item in esistenti)
    assert all(item.reti == ("primario",) for item in tratti_da_etichettare(m, catalogo))
    assert len(tratti_da_etichettare(m, catalogo)) == 6


def test_i_diametri_non_si_chiedono_su_una_rete_esistente_o_che_non_c_e() -> None:
    testo = documento("1", variante="1-retrofit")
    testo["diametri"] = {"reti": ["primario", "secondario"]}
    with pytest.raises(ValidationError, match="esistente"):
        ProjectModel.model_validate(testo)
    testo["diametri"] = {"reti": ["primario", "rete-che-non-c-e"]}
    with pytest.raises(ValidationError, match="non ha"):
        ProjectModel.model_validate(testo)
    testo["diametri"] = {"reti": ["primario", "primario"]}
    with pytest.raises(ValidationError, match="due volte"):
        ProjectModel.model_validate(testo)
    testo["diametri"] = {"reti": []}
    with pytest.raises(ValidationError):
        ProjectModel.model_validate(testo)


@pytest.mark.parametrize("valore", ["5 K", 0, -5, True])
def test_il_salto_termico_e_un_numero_positivo(valore: object) -> None:
    testo = documento("1")
    testo["components"][0]["properties"]["delta_t_k"] = valore
    with pytest.raises(ValidationError, match="delta_t_k"):
        ProjectModel.model_validate(testo)


def test_i_grafi_agli_atti_non_cambiano_di_un_byte() -> None:
    """Richiesta e rete esistente sono campi additivi: un grafo scritto prima, riletto
    e riscritto, e' identico — e cosi' la sua impronta."""
    grafi = [APPROVATI / f"grafo-completo-{n}.json" for n in range(1, 6)]
    grafi.append(IMPIANTO_6 / "grafo-completo-6.json")
    for grafo in grafi:
        testo = grafo.read_text(encoding="utf-8").strip()
        m = ProjectModel.model_validate(json.loads(testo))
        assert canonical_json(m) == testo, grafo.name
        scritto = m.model_dump(mode="json")
        assert "diametri" not in scritto
        assert all("esistente" not in rete for rete in scritto["networks"])


def test_richiesta_e_rete_esistente_si_rileggono_come_sono_scritte(tmp_path: Path) -> None:
    m = ProjectModel.model_validate(documento("1", variante="1-retrofit"))
    scritto = m.model_dump(mode="json")
    assert scritto["diametri"] == {"reti": ["primario"]}
    assert {rete["id"] for rete in scritto["networks"] if rete.get("esistente")} == {
        "secondario",
        "sanitaria",
    }
    assert ProjectModel.model_validate(scritto) == m
