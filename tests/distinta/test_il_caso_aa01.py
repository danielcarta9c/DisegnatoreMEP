"""Il caso di prova AA-01: la distinta del grafo coincide col computo del kit.

Il computo del kit e' `docs/input-pm/2026-10-29-kit-aria-aria/lavoro/dimensionamento.py`
(e la tavola `tavole/AA-01_M.02_anteprima.png`), cablato a mano su quel caso. Qui
ogni voce del kit ha la sua voce nella distinta, con la stessa quantita' — oppure
una quantita' diversa e il perche', scritto in `DIFFERENZE`. Le differenze vanno
tutte **in su**: il criterio del PO e' «meglio sbagliare un po' in su che in giu'».
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.distinta import Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.documento import documento_della_distinta
from disegnatore_mep.distinta.uscite import (
    distinta_in_json,
    foglio_dei_calcoli,
    scrivi_le_uscite,
    tabelle_del_foglio,
)
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import AA01, ROOT, sigle

KIT: list[tuple[str, str, float]] = [
    # (rif del kit, la regola della distinta che la fa, quantita' del kit)
    ("A.1", "corredo/split-outdoor-unit/apparecchiatura", 1),
    ("A.2", "corredo/ducted-indoor-unit/apparecchiatura", 1),
    ("A.3", "corredo/zoning-plenum-5/apparecchiatura", 1),
    ("A.4", "corredo/room-thermostat/apparecchiatura", 4),
    ("A.5", "corredo/wired-remote/apparecchiatura", 1),
    ("B.1", "fluidi/supply_air/flessibile-in-confezioni", 4),
    ("B.2", "corredo/air-supply-terminal/plenum-porta-bocchetta", 5),
    ("B.3", "corredo/return-air-terminal/plenum-di-ripresa", 1),
    ("B.4", "corredo/ducted-indoor-unit/giunto-antivibrante-ripresa", 1),
    ("B.5", "fluidi/supply_air/curva-in-lamiera", 4),
    ("B.6", "fluidi/supply_air/manicotto-di-riserva", 2),
    ("B.7", "fluidi/supply_air/fascette", 36),
    ("B.8", "fluidi/supply_air/nastro-alluminio", 2),
    ("B.9", "fluidi/supply_air/sostegni", 25),
    ("B.10", "corredo/ducted-indoor-unit/kit-sospensione", 10),
    ("B.11", "corredo/zoning-plenum-5/isolamento-raccordi-plenum", 1),
    ("C.1", "fluidi/refrigerant_liquid/tubo-rame-liquido", 12),
    ("C.2", "fluidi/refrigerant_gas/tubo-rame-gas", 12),
    ("C.3", "fluidi/refrigerant_*/manicotti-a-brasare", 4),
    ("C.4", "fluidi/refrigerant_gas/nastro-e-manicotti-isolanti", 1),
    ("C.5", "corredo/split-outdoor-unit/canalina-esterna", 4),
    ("C.6", "corredo/split-outdoor-unit/accessori-canalina", 1),
    ("C.7", "fluidi/refrigerant_gas/collari-linee-frigo", 10),
    ("C.8", "corredo/split-outdoor-unit/staffe-unita-esterna", 1),
    ("C.9", "corredo/split-outdoor-unit/scarico-condensa-unita-esterna", 4),
    ("C.10", "fluidi/refrigerant_gas/carica-aggiuntiva", 0.2),
    ("D.1", "fluidi/condensate/tubo-pvc", 10),
    ("D.2", "corredo/ducted-indoor-unit/raccordo-condensa-unita-interna", 1),
    ("D.3", "fluidi/condensate/curve-condensa", 6),
    ("D.4", "fluidi/condensate/manicotti-condensa", 3),
    ("D.5", "corredo/condensate-trap/sifone", 1),
    ("D.6", "corredo/condensate-outlet/innesto-sullo-scarico", 1),
    ("D.7", "fluidi/condensate/collari-condensa", 10),
    ("D.8", "fluidi/condensate/isolamento-anticondensa", 5),
    ("D.9", "fluidi/condensate/collante-pvc", 1),
    ("E.1", "fluidi/power_supply/cavo-di-alimentazione 3G2,5", 20),
    ("E.2", "fluidi/power_supply/protezione-della-linea C16", 1),
    ("E.3", "corredo/isolator-switch/sezionatore", 1),
    ("E.4", "fluidi/power_supply/protezione-della-linea C6", 1),
    ("E.5", "fluidi/power_supply/cavo-di-alimentazione 3G1,5", 15),
    ("E.6", "corredo/electrical-panel/aggiornamento-schema-quadro", 1),
    ("E.7", "fluidi/interconnection/cavo-di-collegamento", 13),
    ("E.8", "fluidi/control_bus/cavo-di-bus Airzone", 29),
    ("E.9", "fluidi/control_bus/cavo-di-bus P1-P2", 8.5),
    ("E.10", "fluidi/power_supply/corrugato-di-potenza", 40),
    ("E.11", "fluidi/control_bus/corrugato-di-bus", 40),
    ("E.12", "fluidi/power_supply/scatola-di-derivazione", 2),
    ("E.13", "corredo/room-thermostat/scatola-503", 5),
    ("F.1", "corredo/split-outdoor-unit/carotaggio-parete-esterna", 1),
    ("F.2", "fluidi/refrigerant_gas/foratura-linee-frigo", 2),
    ("F.3", "fluidi/supply_air/foratura-per-flessibile", 7),
    ("F.4", "fluidi/condensate/foratura-condensa", 1),
    ("F.5", "corredo/condensate-outlet/traccia-condensa", 3),
    ("F.6", "corredo/electrical-panel/tracce-dal-quadro", 5),
    ("F.7", "corredo/room-thermostat/traccia-per-apparecchio-a-parete", 5),
    ("Z.1", "corredo/ducted-indoor-unit/controsoffitto-zona-macchina", 1),
    ("Z.2", "corredo/ducted-indoor-unit/botola-di-ispezione", 2),
    ("Z.3", "fluidi/supply_air/velette-per-le-bocchette", 1),
    ("Z.4", "corredo/air-supply-terminal/bocchetta-di-mandata", 5),
    ("Z.5", "corredo/return-air-terminal/griglia-di-ripresa", 1),
    ("Z.6", "corredo/air-supply-terminal/griglia-di-transito", 5),
    ("Z.7", "attivita/chiusure-e-ripristini", 1),
]
"""Le 62 voci del computo del kit (A-F e Z), nell'ordine del kit."""

DIFFERENZE: dict[str, tuple[float, str]] = {
    "B.5": (5, "una curva per ramo, non per le sole uscite strette che il kit sceglieva a mano"),
    "B.7": (40, "8 fascette per ramo, curva compresa: la curva in piu' ne porta 4"),
    "B.9": (27, "L / 1,2 m per eccesso + 1 per ramo; il kit scriveva 25 a mano"),
    "D.8": (10, "su tutta la condensa: il tratto in controsoffitto (5 m nel kit) lo sa solo la pianta"),
    "E.9": (10.5, "il minimo di 5 m vale per tutto il bus, come dice il rapporto; il codice del kit lo dava ai soli termostati"),
}
"""Dove la distinta conta diversamente dal kit, e perche'. Tutte in su."""

IN_GIU_DEL_COMMITTENTE: dict[str, tuple[float, str]] = {
    "Z.6": (
        4,
        "griglie di transito per locale servito (collaudo REL-012 t1, §2.4.2): B4 e B5 sono nel soggiorno, che ne "
        "vuole una; il kit ne contava una anche per la porta fra i due disimpegni, che non e' un locale servito e "
        "che il grafo non conosce",
    ),
}
"""Dove la distinta conta meno del kit: solo opere del Committente (sezione Z), escluse
dall'offerta dell'installatore, quindi fuori dal criterio «meglio in su»."""


@pytest.fixture(scope="module")
def distinta(regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]) -> Distinta:
    grafo = json.loads(AA01.read_text(encoding="utf-8"))
    return componi_la_distinta(grafo, regole, *nomi, sigle(grafo))


def _quantita(distinta: Distinta, chiave: str) -> float:
    regola, _, filtro = chiave.partition(" ")
    if "*" in regola:
        prefisso, suffisso = regola.split("*")
        voci = [v for v in distinta.voci if v.regola.startswith(prefisso) and suffisso.split("/")[-1] in v.regola]
    else:
        voci = [v for v in distinta.voci if regola in v.regola.split(" + ")]
    voci = [v for v in voci if filtro in v.testo]
    assert voci, chiave
    assert all(v.quantita is not None for v in voci), chiave
    return sum(v.quantita or 0 for v in voci)


@pytest.mark.parametrize(("rif", "regola", "nel_kit"), KIT, ids=[k[0] for k in KIT])
def test_ogni_voce_del_kit_e_nella_distinta(distinta: Distinta, rif: str, regola: str, nel_kit: float) -> None:
    attesa, _ = {**DIFFERENZE, **IN_GIU_DEL_COMMITTENTE}.get(rif, (nel_kit, ""))
    assert _quantita(distinta, regola) == pytest.approx(attesa), rif


def test_le_differenze_col_kit_sono_tutte_in_su() -> None:
    nel_kit = {rif: q for rif, _, q in KIT}
    for rif, (nostra, perche) in DIFFERENZE.items():
        assert nostra > nel_kit[rif], f"{rif}: {perche}"


def test_quello_che_conta_meno_del_kit_e_solo_del_committente(distinta: Distinta) -> None:
    nel_kit = {rif: (regola, q) for rif, regola, q in KIT}
    for rif, (nostra, perche) in IN_GIU_DEL_COMMITTENTE.items():
        regola, quanti = nel_kit[rif]
        assert nostra < quanti, f"{rif}: {perche}"
        voci = [v for v in distinta.voci if regola in v.regola.split(" + ")]
        assert voci and all(v.sezione == "Z" and v.fornitura == "committente" for v in voci), rif


def test_le_sezioni_e_il_numero_delle_voci(distinta: Distinta) -> None:
    """A-F e Z come il kit (62 voci; i manicotti a brasare sono due righe, una per
    diametro: 63); G una attivita' in piu' (le due DiCo in due righe); V le stesse
    cinque varianti; niente in X."""
    conta = {lettera: len(distinta.voci_della_sezione(lettera)) for lettera in "ABCDEFXZGV"}
    assert conta == {"A": 5, "B": 11, "C": 11, "D": 9, "E": 13, "F": 7, "X": 0, "Z": 7, "G": 12, "V": 5}
    assert not distinta.da_definire
    assert not distinta.domande


def test_le_tratte_sono_quelle_del_kit(distinta: Distinta) -> None:
    """Le 18 tratte della tabella della M.02, con le stesse lunghezze da quotare;
    l'unica diversa e' la P1-P2 corta (3 m nel kit, 5 col minimo del bus), e la
    verifica della scritta lo dice.

    **La numerazione non e' piu' quella del kit** (collaudo T3 di REL-012): dentro ogni
    fluido le tratte vanno nell'ordine delle sigle che collegano, come la colonna
    «Da - a», cosi' che T0n vada a TA-0n. Sul kit cambiano due gruppi: le alimentazioni
    (QE-01 - CZ-01 prima di QE-01 - SZ-01 - UE-01: kit T11 e T10, ora T10 e T11) e i bus
    (CZ-01 - TZ-01…04 prima delle due P1-P2 dell'unita' interna: kit T15-T18 ora T13-T16,
    kit T14 UI-01 - CF-01 ora T17, kit T13 UI-01 - CZ-01 ora T18)."""
    lunghezze = [(t.num, distinta.da_a(t), t.da_quotare_m) for t in distinta.tratte_in_tabella]
    assert lunghezze == [
        ("T01", "PLZ-01 - B1", 6.0),
        ("T02", "PLZ-01 - B2", 3.5),
        ("T03", "PLZ-01 - B3", 6.0),
        ("T04", "PLZ-01 - B4", 3.5),
        ("T05", "PLZ-01 - B5", 7.0),
        ("T06", "RA-01 - UI-01", None),
        ("T07", "UE-01 - UI-01", 12.0),
        ("T08", "UE-01 - UI-01", 12.0),
        ("T09", "UI-01 - SIF-01 - AL-01", 10.0),
        ("T10", "QE-01 - CZ-01", 15.0),
        ("T11", "QE-01 - SZ-01 - UE-01", 20.0),
        ("T12", "UE-01 - UI-01", 13.0),
        ("T13", "CZ-01 - TZ-01", 9.0),
        ("T14", "CZ-01 - TZ-02", 7.0),
        ("T15", "CZ-01 - TZ-03", 7.5),
        ("T16", "CZ-01 - TZ-04", 5.5),
        ("T17", "UI-01 - CF-01", 5.5),
        ("T18", "UI-01 - CZ-01", 5.0),
    ]
    scritte = [e for e in distinta.verifica if e.controllo == "scritta sulla tavola" and e.esito == "oltre"]
    assert [(e.dove, e.valore) for e in scritte] == [("T18", "«P1-P2 · L 3 m»")]


def test_la_verifica_dell_aria_segnala_e_non_corregge(distinta: Distinta) -> None:
    velocita = {e.dove: round(e.misura or 0, 2) for e in distinta.verifica if e.controllo == "velocità"}
    assert velocita == {"T01": 2.39, "T02": 2.48, "T03": 1.86, "T04": 2.43, "T05": 2.43, "T06": 1.2}
    assert all(e.esito == "entro" for e in distinta.verifica if e.controllo == "velocità")
    transito = next(v for v in distinta.voci if v.regola.endswith("griglia-di-transito"))
    assert transito.note == (
        "Aeff min.: Camera 13 m² 0,05 m², Camera 15 m² 0,052 m², Camera 16 m² 0,039 m², Soggiorno-cucina 0,102 m²"
    )


def test_le_tabelle_del_foglio(distinta: Distinta) -> None:
    tabelle = tabelle_del_foglio(distinta)
    assert [t["id"] for t in tabelle["tabelle"]] == ["tratte", "computo", "attivita", "note"]
    for tabella in tabelle["tabelle"]:
        for sezione in tabella["sezioni"]:
            for riga in sezione["righe"]:
                assert len(riga) == len(tabella["colonne"]), tabella["id"]
                assert all(isinstance(c, str) and "≥" not in c and "≤" not in c for c in riga)
    computo = tabelle["tabelle"][1]
    assert [s["titolo"][0] for s in computo["sezioni"]] == list("ABCDEFZ")
    tratte = tabelle["tabelle"][0]["sezioni"][0]["righe"]
    assert tratte[0] == ["T01", "PLZ-01 - B1", "Ø200", "flessibile coibentato", "270", "2,4", "4,1", "6"]


def test_due_volte_lo_stesso_grafo_danno_la_stessa_distinta(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], tmp_path: Path
) -> None:
    grafo = json.loads(AA01.read_text(encoding="utf-8"))
    prima, seconda = (componi_la_distinta(grafo, regole, *nomi) for _ in range(2))
    assert distinta_in_json(prima) == distinta_in_json(seconda)
    assert tabelle_del_foglio(prima) == tabelle_del_foglio(seconda)
    assert foglio_dei_calcoli(prima) == foglio_dei_calcoli(seconda)
    assert documento_della_distinta(prima) == documento_della_distinta(seconda)
    scrivi_le_uscite(prima, tmp_path / "a")
    scrivi_le_uscite(seconda, tmp_path / "b")
    for nome in ("distinta.json", "tabelle-del-foglio.json", "distinta-calcoli.md"):
        assert (tmp_path / "a" / nome).read_bytes() == (tmp_path / "b" / nome).read_bytes()


def test_il_comando_della_skill(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Senza la skill dei report il documento esce in Markdown, col nome parlante del
    cartiglio; niente Excel e niente CSV (I-232)."""
    assert main(["distinta", str(AA01), "--out", str(tmp_path)], cartelle_del_repository(ROOT)) == 0
    uscita = capsys.readouterr().out
    assert "Distinta: 80 voci" in uscita and "Nessuna voce DA DEFINIRE." in uscita
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin.md",
        "distinta-calcoli.md",
        "distinta.json",
        "tabelle-del-foglio.json",
    ]
