"""REL-027: il listino a piu' fornitori e «Dove comprare» (I-302, I-303)."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.costo import (
    Costo,
    RigaDelCosto,
    costo_in_markdown,
    prezza_la_distinta,
)
from disegnatore_mep.distinta.listino import ErroreDelListino, leggi_il_listino
from disegnatore_mep.distinta.ordine import ordine_della_minuteria
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import ROOT
from .test_il_corredo_idronico_e_il_costo import LISTINO, _centrale

INTESTAZIONE = "| ID | Voce | Articolo | Codice | Fornitore | Rif. | Confezione | Netto conf. € | Netto/UM € | UM | Note |\n"
SEPARATORE = "|---|---|---|---|---|---|---|--:|--:|---|---|\n"
FORNITORI = (
    "## I fornitori\n\n| Fornitore | Si ordina | Come si paga | Da dove vengono i prezzi | Capitolo |\n"
    "|---|---|---|---|---|\n| Alfa | sì | | | |\n| Beta | sì | | | |\n| Gamma | no | | | |\n\n"
)


@pytest.fixture(scope="module")
def listino() -> Any:
    return leggi_il_listino(LISTINO)


def _riga(codice: str, fornitore: str, prezzo: str, um: str = "cad") -> str:
    return f"| {codice} | Voce {codice} | Articolo {codice} {fornitore} | A-{codice} | {fornitore} | D r. 1 | 1 pz | {prezzo} | {prezzo} | {um} | |\n"


def _listino(tmp_path: Path, righe: str, fornitori: str = FORNITORI) -> Path:
    percorso = tmp_path / "listino.md"
    percorso.write_text(
        f"# Listino\n\n**Revisione 99, 1 gennaio 2027.**\n\n{fornitori}## 4. Offerte — 1 gennaio 2027\n\n"
        f"{INTESTAZIONE}{SEPARATORE}{righe}",
        encoding="utf-8",
    )
    return percorso


def _costo(listino: Any, voci: list[tuple[str, float, list[tuple[str, float]]]]) -> Costo:
    costo = Costo(progetto={}, listino=listino)
    for rif, quantita, codici in voci:
        unitario = sum(n * listino.get(c).prezzo for c, n in codici)
        costo.righe.append(RigaDelCosto(rif, "I", rif, quantita, "n", codici, unitario, quantita * unitario, ""))
    return costo


def test_ogni_riga_delle_offerte_e_nel_listino_una_volta() -> None:
    """Criterio 1: le 4 + 42 righe degli ordini Abbattista e le 81 del preventivo Idrosanitaria,
    ciascuna una volta, col suo fornitore (anche quelle senza ID e le apparecchiature)."""
    testo = LISTINO.read_text(encoding="utf-8")
    riferimenti = re.findall(r"^\| [^|]+ \| [^|]+ \| [^|]+ \| [^|]+ \| (\w+) \| ((?:OC|XC) \d+) r\. (\d+) \|", testo, re.M)
    visti: dict[tuple[str, str], list[int]] = {}
    for fornitore, documento, riga in riferimenti:
        visti.setdefault((fornitore, documento), []).append(int(riga))
    assert sorted(visti[("Abbattista", "OC 0185611")]) == list(range(1, 5))
    assert sorted(visti[("Abbattista", "OC 0188404")]) == list(range(1, 43))
    assert sorted(visti[("Idrosanitaria", "XC 2704331")]) == list(range(1, 82))
    assert set(visti) == {("Abbattista", "OC 0185611"), ("Abbattista", "OC 0188404"), ("Idrosanitaria", "XC 2704331")}


def test_un_codice_ha_un_prezzo_per_fornitore(tmp_path: Path) -> None:
    listino = leggi_il_listino(_listino(tmp_path, _riga("I01", "Alfa", "2,00") + _riga("I01", "Beta", "1,50")))
    assert [(v.fornitore, v.prezzo) for v in listino.offerte("I01")] == [("Beta", 1.5), ("Alfa", 2.0)]
    assert listino.get("I01").fornitore == "Beta" and listino.get("I01").articolo == "A-I01"


def test_lo_stesso_codice_due_volte_dallo_stesso_fornitore_ferma_il_listino(tmp_path: Path) -> None:
    with pytest.raises(ErroreDelListino, match="I01 ha due prezzi da Alfa"):
        leggi_il_listino(_listino(tmp_path, _riga("I01", "Alfa", "2,00") + _riga("I01", "Alfa", "1,50")))


def test_un_fornitore_che_la_tabella_non_ha_ferma_il_listino(tmp_path: Path) -> None:
    with pytest.raises(ErroreDelListino, match="Delta"):
        leggi_il_listino(_listino(tmp_path, _riga("I01", "Delta", "2,00")))


def test_una_riga_senza_id_si_documenta_e_non_si_legge(tmp_path: Path) -> None:
    listino = leggi_il_listino(_listino(tmp_path, _riga("—", "Alfa", "2,00") + _riga("I02", "Alfa", "1,00")))
    assert set(listino.righe) == {"I02"}


def test_il_prezzo_e_il_piu_basso_fra_chi_si_ordina_e_poi_il_riferimento(tmp_path: Path) -> None:
    """Criterio 3: Gamma non si ordina; il suo prezzo vale solo dove nessun altro ha l'articolo."""
    listino = leggi_il_listino(_listino(
        tmp_path, _riga("I01", "Alfa", "2,00") + _riga("I01", "Gamma", "0,50") + _riga("I02", "Gamma", "3,00"),
    ))
    assert listino.get("I01").fornitore == "Alfa"
    assert listino.get("I02").fornitore == "Gamma"
    assert [v.fornitore for v in listino.ordinabili("I02")] == []


def test_il_listino_vero_ordina_dai_tre_fornitori_e_non_da_bricoman(listino: Any) -> None:
    assert {f for f, d in listino.fornitori.items() if d.si_ordina} == {"Tecnomat", "Abbattista", "Idrosanitaria"}
    assert not listino.si_ordina("Bricoman") and not listino.si_ordina("riferimento online")
    gomito = listino.offerte("I13")
    assert {v.fornitore for v in gomito} == {"Tecnomat", "Abbattista", "Idrosanitaria"}
    assert listino.get("I13") == min(gomito, key=lambda v: v.prezzo)
    # il nipplo da 1": Bricoman (2,13) è un riferimento, Idrosanitaria e Abbattista si ordinano
    assert listino.get("I83c").fornitore == "Idrosanitaria"


def test_l_ordine_va_al_piu_economico_e_dice_le_combinazioni(tmp_path: Path) -> None:
    """Tre articoli, due fornitori: I01 costa meno da Beta, I02 da Alfa, I03 lo ha solo Alfa."""
    listino = leggi_il_listino(_listino(tmp_path, (
        _riga("I01", "Alfa", "2,00") + _riga("I01", "Beta", "1,00")
        + _riga("I02", "Alfa", "3,00") + _riga("I02", "Beta", "4,00")
        + _riga("I03", "Alfa", "5,00") + _riga("I04", "Gamma", "7,00")
    )))
    costo = _costo(listino, [("V1", 10, [("I01", 1.0)]), ("V2", 2, [("I02", 1.0), ("I01", 2.0)]),
                             ("V3", 1, [("I03", 1.0)]), ("V4", 1, [("I04", 1.0)])])
    ordine = ordine_della_minuteria(costo)
    gruppi = ordine.per_fornitore()
    assert {f: sorted(r.codice for r in rr) for f, rr in gruppi.items()} == {"Alfa": ["I02", "I03"], "Beta": ["I01"]}
    i01 = next(r for r in ordine.righe if r.codice == "I01")
    assert i01.quantita == pytest.approx(14) and i01.voci == ["V1", "V2"]
    assert ordine.totale == pytest.approx(14 * 1 + 2 * 3 + 5)
    assert [r.codice for r in ordine.senza_fornitore] == ["I04"]
    assert ordine.totale + ordine.totale_di_riferimento == pytest.approx(costo.totale)
    combinazioni = {c.fornitori: c for c in ordine.combinazioni()}
    assert combinazioni[("Alfa", "Beta")].in_piu == pytest.approx(0) and combinazioni[("Alfa", "Beta")].scoperti == 0
    assert combinazioni[("Alfa",)].scoperti == 0 and combinazioni[("Alfa",)].in_piu == pytest.approx(14 * 1)
    assert combinazioni[("Beta",)].scoperti == 1
    assert combinazioni[("Beta",)].in_piu == pytest.approx(2 * (4 - 3))
    md = "\n".join(costo_in_markdown(costo, {}).splitlines())
    assert "## Dove comprare" in md and "### L'ordine a Alfa — 2 articoli" in md and "### Senza un fornitore" in md


def test_la_distinta_prezzata_ha_l_ordine_e_i_conti_tornano(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    """Criterio 4: il totale degli ordini più gli articoli senza fornitore è il totale del costo."""
    costo = prezza_la_distinta(componi_la_distinta(_centrale(), regole, *nomi), listino)
    ordine = ordine_della_minuteria(costo)
    assert ordine.per_fornitore()
    assert ordine.totale + ordine.totale_di_riferimento == pytest.approx(costo.totale)
    for riga in ordine.ordinabili:
        assert riga.scelta == min(riga.offerte, key=lambda v: v.prezzo)
    tutti = tuple(ordine.fornitori)
    assert next(c for c in ordine.combinazioni() if c.fornitori == tutti).in_piu == pytest.approx(0)


def test_il_comando_scrive_dove_comprare(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(json.dumps(_centrale(), ensure_ascii=False), encoding="utf-8")
    main(
        ["distinta", str(grafo), "--out", str(tmp_path / "d"), "--costo", "--fornitura", "confermata"],
        cartelle_del_repository(ROOT),
    )
    assert "Dove comprare:" in capsys.readouterr().out
    md = (tmp_path / "d" / "interno" / "costo-minuteria.md").read_text(encoding="utf-8")
    assert "## Dove comprare" in md and "### L'ordine a " in md and "### Con meno ordini" in md
    dati = json.loads((tmp_path / "d" / "interno" / "costo-minuteria.json").read_text(encoding="utf-8"))
    assert dati["versione"] == 2 and dati["ordine"]["per_fornitore"]
    assert dati["ordine"]["totale_eur"] + dati["ordine"]["totale_di_riferimento_eur"] == pytest.approx(
        dati["totale_eur"], abs=0.02
    )


def test_un_fornitore_solo_sullo_stesso_paniere(tmp_path: Path) -> None:
    """I-306: tutta la minuteria da un fornitore. Alfa ha tutto (I01 2,00; I02 3,00; I03 5,00),
    Beta solo I01 e I02 (1,00; 4,00): il suo totale compra I03 altrove, da Alfa."""
    listino = leggi_il_listino(_listino(tmp_path, (
        _riga("I01", "Alfa", "2,00") + _riga("I01", "Beta", "1,00")
        + _riga("I02", "Alfa", "3,00") + _riga("I02", "Beta", "4,00")
        + _riga("I03", "Alfa", "5,00")
    )))
    costo = _costo(listino, [("V1", 10, [("I01", 1.0)]), ("V2", 2, [("I02", 1.0)]), ("V3", 1, [("I03", 1.0)])])
    ordine = ordine_della_minuteria(costo)
    uno = {u.fornitore: u for u in ordine.un_fornitore()}
    assert uno["Alfa"].totale == pytest.approx(10 * 2 + 2 * 3 + 5) and uno["Alfa"].non_ha == 0
    assert uno["Beta"].da_lui == pytest.approx(10 * 1 + 2 * 4) and uno["Beta"].non_ha == 1
    assert uno["Beta"].altrove == pytest.approx(5) and uno["Beta"].totale == pytest.approx(23)
    assert [u.fornitore for u in ordine.un_fornitore()] == ["Beta", "Alfa"]
    assert [r.codice for r in ordine.articoli_in_comune] == ["I01", "I02"]
    assert uno["Alfa"].in_comune == pytest.approx(26) and uno["Beta"].in_comune == pytest.approx(18)
    md = costo_in_markdown(costo, {})
    assert "### Un fornitore solo" in md
    assert "Un fornitore solo per tutta la minuteria: il più economico è Beta" in md


def test_con_i_fornitori_si_ordina_soltanto_da_quelli(tmp_path: Path) -> None:
    listino = leggi_il_listino(_listino(tmp_path, _riga("I01", "Alfa", "2,00") + _riga("I01", "Beta", "1,00")))
    solo_alfa = listino.con_i_fornitori(["Alfa"])
    assert solo_alfa.get("I01").fornitore == "Alfa"
    assert [v.fornitore for v in solo_alfa.offerte("I01")] == ["Beta", "Alfa"], "gli altri prezzi restano"
    with pytest.raises(ErroreDelListino, match="Delta"):
        listino.con_i_fornitori(["Delta"])


def test_il_comando_con_un_fornitore_scelto(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(json.dumps(_centrale(), ensure_ascii=False), encoding="utf-8")
    main(
        ["distinta", str(grafo), "--out", str(tmp_path / "d"), "--costo", "--fornitura", "confermata",
         "--fornitori", "Idrosanitaria"],
        cartelle_del_repository(ROOT),
    )
    assert "Si ordina soltanto da: Idrosanitaria." in capsys.readouterr().out
    dati = json.loads((tmp_path / "d" / "interno" / "costo-minuteria.json").read_text(encoding="utf-8"))
    assert list(dati["ordine"]["per_fornitore"]) == ["Idrosanitaria"]


def _riga_con_nota(codice: str, fornitore: str, prezzo: str, nota: str) -> str:
    return _riga(codice, fornitore, prezzo).replace(" | |\n", f" | {nota} |\n")


def test_lo_scostamento_non_si_sceglie_e_diventa_un_avviso(tmp_path: Path) -> None:
    """I-307: la marca non conta, la prescrizione sì. Beta costa meno ma si scosta (⚠): si sceglie
    Alfa, e Beta è un avviso col risparmio. I02 lo hanno solo con lo scostamento: si prende, avvisato."""
    listino = leggi_il_listino(_listino(tmp_path, (
        _riga("I01", "Alfa", "10,00") + _riga_con_nota("I01", "Beta", "4,00", "⚠ senza disconnettore; altro")
        + _riga_con_nota("I02", "Alfa", "3,00", "⚠ attacco 3/8")
    )))
    beta = next(v for v in listino.offerte("I01") if v.fornitore == "Beta")
    assert beta.scostamento == "senza disconnettore"
    assert listino.get("I01").fornitore == "Alfa" and listino.get("I02").scostamento == "attacco 3/8"
    costo = _costo(listino, [("V1", 2, [("I01", 1.0)]), ("V2", 1, [("I02", 1.0)])])
    ordine = ordine_della_minuteria(costo)
    i01 = next(r for r in ordine.righe if r.codice == "I01")
    assert i01.scelta is not None and i01.scelta.fornitore == "Alfa" and i01.avvisi == [beta]
    assert i01.descrizione == "Articolo I01 Alfa", "la descrizione è quella dell'articolo scelto"
    i02 = next(r for r in ordine.righe if r.codice == "I02")
    assert i02.scelta is not None and i02.scelta.scostamento and i02.avvisi == [i02.scelta]
    assert ordine.totale == pytest.approx(2 * 10 + 3)
    assert {u.fornitore: u.ha for u in ordine.un_fornitore()} == {"Alfa": 2}, "lo scostamento non conta come «ha»"
    md = costo_in_markdown(costo, {})
    assert "### Avvisi sul prezzo" in md and "Beta 4,00 | senza disconnettore | 12,00 |" in md
    assert "nessun articolo rispetta la voce: Alfa 3,00 ⚠" in md


def test_nel_listino_vero_il_filler_e_il_manometro_0_12_sono_avvisi(listino: Any) -> None:
    """I-308, I-309: il gruppo di riempimento senza disconnettore e il manometro 0–12 non si scelgono."""
    assert listino.get("I47").fornitore == "Idrosanitaria" and "DISCONNETTORE" in listino.get("I47").descrizione
    assert {v.fornitore for v in listino.offerte("I47") if v.scostamento} == {"Tecnomat", "Abbattista"}
    assert listino.get("I44").fornitore == "Idrosanitaria" and "0-6BAR" in listino.get("I44").descrizione
