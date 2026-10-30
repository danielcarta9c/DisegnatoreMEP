"""La distinta in un documento a parte, con l'impaginazione dei report Nove C (REL-015, I-232).

Il PO: «Non foglio Excel meglio documento pdf con copertina e impaginazione generata con la
skill report di nove c (senza kpi di copertina e senza la sezione chi siamo).»

- il **contenuto** (`documento.documento_della_distinta`): la copertina e sette capitoli,
  gia' scritti, senza prezzi e senza dati interni — provato a fondo, qui;
- il **disegno** col motore dei report (`impaginazione`): provato con un motore finto
  (`motore_finto/references/`, le stesse funzioni, registra le chiamate) e, dove l'ambiente
  di prova ha la skill dei report, col motore vero (variabile `DISEGNATORE_MEP_REPORT`);
- il **ripiego**: senza la skill dei report, lo stesso contenuto in Markdown.
"""

import json
import os
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import DA_DEFINIRE, Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.documento import (
    VIETATE,
    Chiavi,
    Elenco,
    Paragrafo,
    Tabella,
    documento_della_distinta,
    documento_in_markdown,
    nome_del_file,
    tutti_i_testi,
)
from disegnatore_mep.distinta.impaginazione import (
    MotoreAssente,
    carica_il_motore,
    cartella_del_motore,
    larghezze_delle_colonne,
    per_il_motore,
)
from disegnatore_mep.distinta.regole import la_fornitura
from disegnatore_mep.distinta.uscite import tabelle_del_foglio
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import AA01, COLLAUDO_T1, ROOT, sigle

Nomi = tuple[dict[str, str], dict[str, str]]

MOTORE_FINTO = Path(__file__).resolve().parent / "motore_finto"
COLLAUDO_T3 = Path(__file__).resolve().parent / "collaudo-t3" / "grafo-completo.json"

CAPITOLI = [
    "L'impianto e le avvertenze",
    "Le tratte: sezioni e lunghezze",
    "Il computo per sezioni",
    "Le attività a corpo",
    "Le varianti e le voci dell'installatore",
    "Le voci da definire e le domande",
    "Le note e le regole usate",
]

FONTI_DI_SVILUPPO = re.compile(
    r"lavoro/|\.py\b|\.md\b|RAPPORTO|REVISIONE|rilievo \d|kit AA-01|rules/|sessione di sviluppo|D-\d{3}"
)


def _distinta(grafo: Path, regole: RegoleDellaDistinta, nomi: Nomi, fornitura: str | None = None) -> Distinta:
    dati = json.loads(grafo.read_text(encoding="utf-8"))
    return componi_la_distinta(dati, regole, *nomi, sigle(dati), la_fornitura(regole, fornitura))


@pytest.fixture
def aa01(regole: RegoleDellaDistinta, nomi: Nomi) -> Distinta:
    return _distinta(AA01, regole, nomi)


def _blocchi(capitolo: Any, tipo: type) -> list[Any]:
    return [b for b in capitolo.blocchi if isinstance(b, tipo)]


# --- il contenuto ------------------------------------------------------------------------


def test_sette_capitoli_sempre_gli_stessi(aa01: Distinta, regole: RegoleDellaDistinta, nomi: Nomi) -> None:
    for distinta in (aa01, _distinta(COLLAUDO_T1, regole, nomi), _distinta(COLLAUDO_T3, regole, nomi, "confermata")):
        documento = documento_della_distinta(distinta)
        assert [c.titolo for c in documento.capitoli] == CAPITOLI
        assert [c.numero for c in documento.capitoli] == list(range(1, 8))


def test_la_copertina_senza_kpi(aa01: Distinta) -> None:
    copertina = documento_della_distinta(aa01).copertina
    assert copertina.titolo == ("Distinta materiali", "per l'installatore", "Climatizzazione canalizzata Daikin con zonizzazione Airzone")
    assert copertina.sottotitolo == "Schema funzionale M.02, rev. 00  ·  29.10.2026"
    assert copertina.riquadro == (
        "DISTINTA MATERIALI PER L'INSTALLATORE",
        "A corpo, fisso e invariabile  ·  quantità indicative",
        "Sopralluogo obbligatorio prima dell'offerta",
    )
    assert copertina.piede == "Commessa AA-01 — 29.10.2026"
    assert copertina.riserva == ("Commessa AA-01", "Climatizzazione canalizzata Daikin con zonizzazione Airzone")
    assert not hasattr(copertina, "kpi")


def test_le_avvertenze(aa01: Distinta, regole: RegoleDellaDistinta, nomi: Nomi) -> None:
    """A corpo, fisso e invariabile; quantita' indicative; sopralluogo obbligatorio; la
    fornitura da confermare; la distinta non progetta (REL-015, punto 2)."""
    primo = documento_della_distinta(aa01).capitoli[0]
    chiavi = dict(_blocchi(primo, Chiavi)[0].righe)
    assert chiavi["Commessa"] == "AA-01" and chiavi["Schema funzionale"] == "tavola M.02, rev. 00 del 29.10.2026"
    avvertenze = "\n".join(_blocchi(primo, Elenco)[0].voci)
    for parole in ("PREZZO A CORPO, FISSO E INVARIABILE", "INDICATIVE", "SOPRALLUOGO OBBLIGATORIO", "non progetta"):
        assert parole in avvertenze, parole
    assert "confermare per questa offerta" in avvertenze
    confermata = documento_della_distinta(_distinta(AA01, regole, nomi, "confermata")).capitoli[0]
    assert "Fornitura per questa offerta: apparecchiature fornite da Nove C" in "\n".join(_blocchi(confermata, Elenco)[0].voci)


def test_le_tratte_sono_quelle_della_distinta(aa01: Distinta) -> None:
    secondo = documento_della_distinta(aa01).capitoli[1]
    tratte, verifica = _blocchi(secondo, Tabella)
    righe = tabelle_del_foglio(aa01, ("tratte",))["tabelle"][0]["sezioni"][0]["righe"]
    assert [list(r) for r in tratte.righe] == righe
    assert tratte.righe[0] == ("T01", "PLZ-01 - B1", "Ø200", "flessibile coibentato", "270", "2,4", "4,1", "6")
    assert tratte.intestazioni[-2:] == ("L stimata m", "L da quotare m")
    # La scritta sulla tavola che concorda non interessa l'installatore: solo quella che non concorda.
    scritte = [r for r in verifica.righe if r[1] == "scritta sulla tavola"]
    assert scritte == [("T18", "scritta sulla tavola", "«P1-P2 · L 3 m»", "L 5 m da quotare", "oltre")]
    assert len([r for r in verifica.righe if r[1] == "velocità"]) == 6


def test_il_computo_una_tabella_per_sezione(aa01: Distinta) -> None:
    terzo = documento_della_distinta(aa01).capitoli[2]
    tabelle = _blocchi(terzo, Tabella)
    assert [t.titolo[0] for t in tabelle] == list("ABCDEFZ")
    assert all(t.intestazioni == ("Rif.", "Voce", "UM", "Q.tà", "Fornitura", "Note") for t in tabelle)
    righe = [r for t in tabelle for r in t.righe]
    assert [r[0] for r in righe] == [v.rif for v in aa01.voci if v.sezione in "ABCDEFXZ"]
    assert (righe[5][0], righe[5][3]) == ("B.1", "4")


def test_attivita_varianti_e_righe_vuote(aa01: Distinta) -> None:
    documento = documento_della_distinta(aa01)
    attivita = _blocchi(documento.capitoli[3], Tabella)[0]
    assert attivita.titolo.startswith("G. ") and len(attivita.righe) == 12
    varianti, acca = _blocchi(documento.capitoli[4], Tabella)
    assert varianti.titolo.startswith("V. ") and [r[0] for r in varianti.righe] == [f"V.{i}" for i in range(1, 6)]
    assert acca.titolo.startswith("H. ") and acca.righe == tuple((f"H.{i}", "", "", "", "") for i in range(1, 7))
    assert "referente tecnico dell'installatore" in _blocchi(documento.capitoli[4], Paragrafo)[-1].testo


def test_le_voci_da_definire_e_le_domande(regole: RegoleDellaDistinta, nomi: Nomi, aa01: Distinta) -> None:
    t1 = _distinta(COLLAUDO_T1, regole, nomi)
    sesto = documento_della_distinta(t1).capitoli[5]
    domande = next(e for e in _blocchi(sesto, Elenco) if e.titolo == "Le domande al progettista")
    assert list(domande.voci) == [d.replace("`", "") for d in t1.domande]
    assert all(v.rif in _blocchi(sesto, Paragrafo)[0].testo for v in t1.da_definire)
    nessuna = documento_della_distinta(_distinta(AA01, regole, nomi, "confermata")).capitoli[5]
    assert [e.titolo for e in _blocchi(nessuna, Elenco)] == [
        "Le segnalazioni della verifica (la distinta non corregge)",
        "Le assunzioni della distinta",
    ]
    computo = [r for t in _blocchi(documento_della_distinta(t1).capitoli[2], Tabella) for r in t.righe]
    assert any(r[3] == DA_DEFINIRE for r in computo)


def test_le_regole_in_parole(aa01: Distinta) -> None:
    settimo = documento_della_distinta(aa01).capitoli[6]
    assert list(_blocchi(settimo, Elenco)[0].voci) == aa01.note
    regole = _blocchi(settimo, Tabella)[0]
    tutte = {rif for _, voci in regole.righe for rif in voci.split(", ")}
    assert tutte == {v.rif for v in aa01.voci}
    assert not [r for r in regole.righe if re.search(r"\b(corredo|fluidi|attivita|lunghezze|verifica)/", r[0])]


@pytest.mark.parametrize("grafo", [AA01, COLLAUDO_T1, COLLAUDO_T3])
def test_niente_prezzi_e_niente_dati_interni(grafo: Path, regole: RegoleDellaDistinta, nomi: Nomi) -> None:
    dati = json.loads(grafo.read_text(encoding="utf-8"))
    documento = documento_della_distinta(_distinta(grafo, regole, nomi))
    testi = "\n".join(tutti_i_testi(documento))
    assert [v for v in VIETATE if v in testi] == []
    assert not FONTI_DI_SVILUPPO.search(testi)
    ids = [c["id"] for c in dati["components"] if "-" in c["id"]] + [c["id"] for c in dati["connections"]]
    assert [i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", testi)] == []
    assert "ND" not in re.findall(r"\bND\b", testi)
    assert documento.vietate == VIETATE


def test_il_nome_del_file() -> None:
    assert nome_del_file({"commission_code": "MI.049.01", "project_name": "Canalizzato aria-aria in pompa di calore"}) == (
        "MI.049.01_Distinta_materiali_Canalizzato_aria_aria_in_pompa_di_calore"
    )
    assert nome_del_file({"commission_code": "ND", "project_name": "Canalizzato"}) == "Distinta_materiali_Canalizzato"
    assert nome_del_file({"commission_code": "BD.12", "project_name": ""}) == "BD.12_Distinta_materiali"
    assert nome_del_file({}) == "distinta"
    lungo = nome_del_file({"commission_code": "AA-01", "project_name": "Climatizzazione canalizzata Daikin con zonizzazione"})
    assert lungo == "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin", "niente «con» in coda"


def test_il_markdown_ha_lo_stesso_contenuto(aa01: Distinta) -> None:
    documento = documento_della_distinta(aa01)
    testo = documento_in_markdown(documento)
    for capitolo in documento.capitoli:
        assert f"## {capitolo.numero}. {capitolo.titolo}" in testo
    for cella in tutti_i_testi(documento):
        if cella not in documento.intestazione:  # la testata delle pagine: nel Markdown non c'e'
            assert cella.replace("|", "/") in testo, cella
    assert "| Rif. | Voce | UM | Q.tà | Fornitura | Note |\n|---|---|---|---:|---|---|" in testo


# --- il disegno: la misura delle colonne ---------------------------------------------------


def test_ogni_colonna_e_larga_almeno_la_sua_parola() -> None:
    """«DEFINIRE» e «committente» uscivano dalla cella: la colonna si allarga e lo spazio lo
    cedono le colonne larghe."""
    tabella = Tabella(("Rif.", "Voce", "Q.tà", "Fornitura"), (("B.1", "voce lunga " * 20, "DA DEFINIRE", "committente"),), (0.5, 8.0, 0.3, 0.3))

    def misura(testo: str, carattere: str, corpo: float) -> float:
        return len(testo) * corpo * 0.6

    larghe = larghezze_delle_colonne(tabella, 500.0, misura, "R", "B")
    assert sum(larghe) == pytest.approx(500.0)
    assert larghe[2] >= misura("DEFINIRE", "R", 8.5) + 12 and larghe[3] >= misura("committente", "R", 8.5) + 12
    assert larghe[1] < 8.0 / 9.1 * 500


def test_per_il_motore_i_caratteri() -> None:
    assert per_il_motore("(5 + 1) × 1,15 → 7 m <b> & co") == "(5 + 1) × 1,15 - 7 m &lt;b&gt; &amp; co"


# --- il disegno: col motore finto ------------------------------------------------------------


@pytest.fixture
def finto() -> Any:
    motore = carica_il_motore(MOTORE_FINTO)
    for modulo in (motore.copertina, motore.corpo, motore.controllo):
        modulo.CHIAMATE.clear()
    motore.corpo.AVVISI_DEL_RIEMPIMENTO.clear()
    motore.controllo.PROBLEMI.clear()
    return motore


def test_il_pdf_coi_report_nove_c(finto: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    finto.corpo.AVVISI_DEL_RIEMPIMENTO.append("Pag. 8: riempita al 75% (sotto soglia)")
    finto.controllo.PROBLEMI.append("Stringa vietata '€' presente a pag. 3.")
    codice = main(["distinta", str(AA01), "--out", str(tmp_path), "--report", str(MOTORE_FINTO)], cartelle_del_repository(ROOT))
    assert codice == 0
    uscita = capsys.readouterr().out
    pdf = tmp_path / "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin.pdf"
    assert pdf.read_bytes().startswith(b"%PDF")
    assert not list(tmp_path.glob("*.xlsx")) and not list(tmp_path.glob("*.csv")) and not list(tmp_path.glob("AA-01*.md"))
    # La copertina: senza KPI, e la terza riga che non ci sta passa alla riserva.
    (copertina,) = finto.copertina.CHIAMATE
    assert copertina["KPI_DATA"] == ()
    assert (copertina["TITLE_L1"], copertina["TITLE_L2"], copertina["TITLE_L3"]) == (
        "Distinta materiali", "per l'installatore", "Commessa AA-01",
    )
    assert copertina["SUBTITLE"] == "Climatizzazione canalizzata Daikin con zonizzazione Airzone"
    assert copertina["BOX_HEAD"] == "DISTINTA MATERIALI PER L'INSTALLATORE"
    assert copertina["FTR_RIGHT"] == "Commessa AA-01 — 29.10.2026"
    # Il corpo: senza «Chi siamo», sette capitoli numerati da 1, la testata del documento.
    chiamate = finto.corpo.CHIAMATE
    nomi = [nome for nome, _ in chiamate]
    assert [d["num"] for n, d in chiamate if n == "chapter"] == list(range(1, 8))
    assert [d["title"] for n, d in chiamate if n == "chapter"] == [per_il_motore(t) for t in CAPITOLI]
    assert all(d["include_chi_siamo"] is False for n, d in chiamate if n in ("make_doc", "merge_pdf", "story_plan"))
    assert nomi.index("story_plan") < nomi.index("validate_story") < nomi.index("build") < nomi.index("fill_report") < nomi.index("merge_pdf")
    assert finto.corpo._DOC_HEADER_RIGHT == ["noveC — Distinta materiali, commessa AA-01", "29.10.2026"]
    assert next(d for n, d in chiamate if n == "build")["primo"] != "PageBreak"
    tabelle = [d for n, d in chiamate if n == "std_table"]
    assert all(sum(d["larghezze"]) == pytest.approx(finto.corpo.CONTENT_W) for d in tabelle)
    computo = [d for d in tabelle if d["intestazioni"][:2] == ["Rif.", "Voce"] and len(d["intestazioni"]) == 6]
    assert len({tuple(d["larghezze"]) for d in computo}) == 1, "le sezioni del computo sulle stesse verticali"
    assert any(n == "kv_table" for n in nomi) and any(n == "num_items" for n in nomi)
    # Il controllo finale: non un'offerta, le stringhe vietate, le pagine accanto al PDF.
    (controllo,) = finto.controllo.CHIAMATE
    assert controllo["offer"] is False and "€" in controllo["forbid"]
    assert Path(controllo["out_dir"]) == tmp_path / "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin-pagine"
    assert "Il PDF coi report Nove C: 3 pagine, da guardare una per una:" in uscita
    assert "qa-1.png" in uscita
    assert "  - Pag. 8: riempita al 75% (sotto soglia)" in uscita
    assert "  - Stringa vietata '€' presente a pag. 3." in uscita
    assert "[copertina] la riga «Climatizzazione canalizzata Daikin con zonizzazione Airzone»" not in uscita
    assert "Riempimento pagine (corpo) — finto" not in uscita and "CHECKLIST" not in uscita, "il motore parla, il comando riassume"


def test_il_pdf_dice_le_voci_da_definire_con_l_uscita_2(finto: Any, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    codice = main(["distinta", str(COLLAUDO_T1), "--out", str(tmp_path), "--report", str(MOTORE_FINTO)], cartelle_del_repository(ROOT))
    assert codice == 2
    assert (tmp_path / "Distinta_materiali_Canalizzato_aria_aria_in_pompa_di_calore.pdf").is_file()
    (copertina,) = finto.copertina.CHIAMATE
    assert copertina["TITLE_L3"] == f"Commessa {DA_DEFINIRE}"
    assert copertina["SUBTITLE"] == "Canalizzato aria-aria in pompa di calore - appartamento …"
    uscita = capsys.readouterr().out
    assert "Il controllo dei report — 1 avvisi" in uscita
    assert "  - [copertina] il sottotitolo «Canalizzato aria-aria in pompa di calore - appartamento al secondo piano»" in uscita


# --- il ripiego in Markdown --------------------------------------------------------------------


def test_senza_la_skill_dei_report_il_markdown(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cartelle = cartelle_del_repository(ROOT)
    assert main(["distinta", str(COLLAUDO_T1), "--out", str(tmp_path / "a")], cartelle) == 2
    errore = capsys.readouterr().err
    assert "Il PDF della distinta non c'e': non e' stata data la skill dei report Nove C" in errore
    markdown = tmp_path / "a" / "Distinta_materiali_Canalizzato_aria_aria_in_pompa_di_calore.md"
    assert markdown.read_text(encoding="utf-8").startswith("# Distinta materiali per l'installatore\n")
    assert main(["distinta", str(AA01), "--out", str(tmp_path / "b"), "--report", str(tmp_path)], cartelle) == 0
    assert f"in {tmp_path} non c'e' il motore dei report Nove C" in capsys.readouterr().err
    assert (tmp_path / "b" / "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin.md").is_file()


def test_un_motore_che_non_si_carica_e_un_motore_che_non_c_e(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Il motore vero vuole reportlab e pypdf: dove mancano, la distinta lo dice e scrive
    il Markdown."""
    rotto = tmp_path / "nove-c-report" / "references"
    rotto.mkdir(parents=True)
    for nome in ("nove_c_report_cover.py", "nove_c_report_qa.py"):
        (rotto / nome).write_text("", encoding="utf-8")
    (rotto / "nove_c_report_engine.py").write_text("import libreria_che_non_c_e_davvero\n", encoding="utf-8")
    assert cartella_del_motore(rotto.parent) == rotto
    with pytest.raises(MotoreAssente, match="manca la libreria libreria_che_non_c_e_davvero"):
        carica_il_motore(rotto.parent)
    codice = main(["distinta", str(AA01), "--out", str(tmp_path / "d"), "--report", str(rotto.parent)], cartelle_del_repository(ROOT))
    assert codice == 0
    assert "manca la libreria libreria_che_non_c_e_davvero" in capsys.readouterr().err
    assert [p.suffix for p in (tmp_path / "d").glob("AA-01*")] == [".md"]


def test_il_motore_vero_o_il_ripiego(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Col motore vero, dove l'ambiente di prova ha la skill dei report: il percorso in
    `DISEGNATORE_MEP_REPORT`. Senza, la stessa prova verifica il ripiego in Markdown — non
    e' mai saltata."""
    percorso = os.environ.get("DISEGNATORE_MEP_REPORT")
    argomenti = ["distinta", str(AA01), "--out", str(tmp_path), *(["--report", percorso] if percorso else [])]
    assert main(argomenti, cartelle_del_repository(ROOT)) == 0
    uscita = capsys.readouterr()
    nome = "AA-01_Distinta_materiali_Climatizzazione_canalizzata_Daikin"
    if percorso and cartella_del_motore(Path(percorso)) is not None:
        import pypdf

        pdf = tmp_path / f"{nome}.pdf"
        lettore = pypdf.PdfReader(pdf)
        testo = "\n".join(p.extract_text() or "" for p in lettore.pages)
        assert len(lettore.pages) >= 8
        for titolo in CAPITOLI:
            assert titolo.split(":")[0] in testo, titolo
        assert "PREZZO A CORPO, FISSO E INVARIABILE" in testo and "SOPRALLUOGO OBBLIGATORIO" in testo
        assert "Chi siamo" not in testo and "€" not in testo
        pagine = sorted((tmp_path / f"{nome}-pagine").glob("qa-*.png"))
        assert len(pagine) == len(lettore.pages)
        assert "Stringa vietata" not in uscita.out and "Placeholder" not in uscita.out
    else:
        assert (tmp_path / f"{nome}.md").is_file()
        assert "Il PDF della distinta non c'e'" in uscita.err
