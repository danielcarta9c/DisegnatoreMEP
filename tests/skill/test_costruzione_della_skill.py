"""La cartella della skill si costruisce con un comando, e si ricostruisce identica (REL-001).

Come i generatori della libreria (`tests/catalog/test_generated_fixtures.py`): la
cartella non si copia e non si ritocca a mano, e le prove qui lo tengono su.

- **due costruzioni danno gli stessi byte**, cartella e ZIP;
- la skill passa **i controlli della guida di Anthropic** e del validatore di
  `skill-creator`, e un frontespizio che YAML non legge ferma la costruzione;
- le istruzioni dei tre pezzi arrivano nella skill **cambiate nei soli percorsi**, e una
  sostituzione che non trova il suo posto ferma la costruzione;
- **la skill costruita disegna da sola**: dal grafo di prima stesura alla tavola in PDF,
  con il suo comando e il suo motore, fuori dal repository;
- **lo ZIP si carica su claude.ai**: al massimo 200 file, sotto i 30 MB, un solo
  `SKILL.md`, il frontespizio nei limiti (I-188); e la skill costruita rifa' la tavola
  dell'impianto 7 identica, byte per byte.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
IMPIANTO_7 = ROOT / "docs" / "collaudi" / "REL-001" / "impianto-7"
TAVOLA_7 = ROOT / "docs" / "collaudi" / "REL-001" / "tavole" / "impianto-7-finale-opus-A2.pdf"
BOZZA_6 = ROOT / "docs" / "collaudi" / "REL-003" / "capire-giro-2" / "grafo.json"


def _costruttore() -> ModuleType:
    spec = importlib.util.spec_from_file_location("costruisci_skill", ROOT / "scripts" / "costruisci-skill.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def costruttore() -> ModuleType:
    return _costruttore()


@pytest.fixture(scope="module")
def costruita(costruttore: ModuleType, tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    return costruttore.costruisci(tmp_path_factory.mktemp("skill"))  # type: ignore[no-any-return]


def _contenuto(cartella: Path) -> dict[str, bytes]:
    return {p.relative_to(cartella).as_posix(): p.read_bytes() for p in sorted(cartella.rglob("*")) if p.is_file()}


def test_due_costruzioni_danno_gli_stessi_byte(
    costruttore: ModuleType, costruita: tuple[Path, Path], tmp_path: Path
) -> None:
    skill, archivio = costruita
    seconda, secondo_archivio = costruttore.costruisci(tmp_path)
    assert _contenuto(skill) == _contenuto(seconda)
    assert archivio.read_bytes() == secondo_archivio.read_bytes()


def test_lo_zip_e_la_cartella_con_la_skill_alla_radice(costruita: tuple[Path, Path]) -> None:
    skill, archivio = costruita
    with zipfile.ZipFile(archivio) as zip_:
        nomi = zip_.namelist()
    assert all(nome.startswith("disegnatore-mep/") for nome in nomi)
    assert "disegnatore-mep/SKILL.md" in nomi
    assert len(nomi) == len(_contenuto(skill))
    assert not [n for n in nomi if "__pycache__" in n or n.endswith(".pyc")]


def test_lo_zip_sta_nei_limiti_del_caricamento(costruttore: ModuleType, costruita: tuple[Path, Path]) -> None:
    """Il 2 ottobre lo ZIP di REL-001 si e' fermato al caricamento su claude.ai: 287 file, e
    il limite e' 200 (I-188). Simboli, catalogo e regole stanno adesso in un file ciascuno."""
    _, archivio = costruita
    with zipfile.ZipFile(archivio) as zip_:
        voci = zip_.infolist()
    assert len(voci) <= costruttore.FILE_NELLO_ZIP
    assert not [v.filename for v in voci if v.is_dir()], "nessuna voce di cartella"
    assert [v.filename for v in voci if v.filename.endswith("SKILL.md")] == ["disegnatore-mep/SKILL.md"]
    assert sum(v.file_size for v in voci) < costruttore.BYTE_DELLA_SKILL
    nomi = {v.filename for v in voci}
    assert {f"disegnatore-mep/dati/{f}.json" for f in ("simboli", "catalogo", "regole")} <= nomi
    assert not [n for n in nomi if n.startswith(("disegnatore-mep/dati/simboli/", "disegnatore-mep/dati/catalogo/"))]


def test_troppi_file_fermano_la_costruzione(
    costruttore: ModuleType, costruita: tuple[Path, Path], tmp_path: Path
) -> None:
    skill, _ = costruita
    copia = tmp_path / skill.name
    shutil.copytree(skill, copia)
    for numero in range(costruttore.FILE_NELLO_ZIP):
        (copia / "dati" / f"in-piu-{numero}.json").write_text("{}", encoding="utf-8")
    assert any("il caricamento su claude.ai" in d for d in costruttore.controlla(copia))


def test_la_skill_passa_i_controlli_della_guida(costruttore: ModuleType, costruita: tuple[Path, Path]) -> None:
    skill, _ = costruita
    assert costruttore.controlla(skill) == []
    testo = (skill / "SKILL.md").read_text(encoding="utf-8")
    campi = costruttore._frontespizio(testo)
    assert campi["name"] == "disegnatore-mep"
    assert 0 < len(campi["description"]) <= costruttore.CARATTERI_DELLA_DESCRIZIONE <= 1024
    assert set(campi) <= costruttore.CHIAVI_AMMESSE
    assert campi["license"] and 0 < len(campi["compatibility"]) <= costruttore.CARATTERI_DELLA_COMPATIBILITA
    assert len(testo.split("\n---\n", 1)[1].splitlines()) < 500
    assert [p.relative_to(skill).as_posix() for p in skill.rglob("SKILL.md")] == ["SKILL.md"]


def test_la_skill_non_porta_e_non_propone_il_grafo_da_leggere(costruita: tuple[Path, Path]) -> None:
    """I-186: il grafo da leggere il progettista non lo leggeva («non è leggibile ... token
    sprecati»). Non si scrive, non si manda, e il suo generatore non viaggia nello ZIP."""
    skill, archivio = costruita
    with zipfile.ZipFile(archivio) as zip_:
        assert "disegnatore-mep/scripts/grafo_leggibile.py" not in zip_.namelist()
    testo = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert "da leggere" not in testo and "da-leggere" not in testo


def test_un_frontespizio_che_yaml_non_legge_ferma_la_costruzione(costruttore: ModuleType) -> None:
    """Il 29 settembre la descrizione diceva «dimensiona: disegna», e YAML non la leggeva."""
    with pytest.raises(costruttore.ErroreDiCostruzione, match="YAML"):
        costruttore._frontespizio("---\nname: prova\ndescription: non dimensiona: disegna\n---\n")


def test_le_istruzioni_cambiano_nei_soli_percorsi(costruttore: ModuleType, costruita: tuple[Path, Path]) -> None:
    """Il contenuto di Capire, Comporre e Rivedere non e' di questo pacchetto: nella skill
    si toccano i percorsi e il comando di validazione, e nient'altro."""
    skill, _ = costruita
    for pezzo, sostituzioni in (
        ("capire", costruttore.PERCORSI_DI_CAPIRE),
        ("comporre", costruttore.PERCORSI_DI_COMPORRE),
        ("rivedere", costruttore.PERCORSI_DI_RIVEDERE),
    ):
        sorgente = (ROOT / "skill" / pezzo / "ISTRUZIONI.md").read_text(encoding="utf-8")
        for s in sostituzioni:
            sorgente = sorgente.replace(s.vecchio, s.nuovo)
        nella_skill = (skill / "riferimenti" / f"{pezzo}.md").read_text(encoding="utf-8")
        senza_indice = nella_skill
        if "## Indice" in nella_skill:
            prima, _, dopo = nella_skill.partition("\n\n## Indice\n")
            senza_indice = prima + "\n" + dopo.split("\n\n", 1)[1]
        assert senza_indice.rstrip("\n") == sorgente.rstrip("\n"), pezzo


def test_una_sostituzione_che_non_trova_il_suo_posto_ferma_la_costruzione(costruttore: ModuleType) -> None:
    sostituzione = costruttore.Sostituzione("`assets/symbols/<id>.json`", "`dati/simboli/<id>.json`", 1, "prova")
    with pytest.raises(costruttore.ErroreDiCostruzione, match="0 volte invece di 1"):
        costruttore._sostituisci("un testo che non la contiene", (sostituzione,), "prova")


def test_la_skill_costruita_disegna_da_sola(costruita: tuple[Path, Path], tmp_path: Path) -> None:
    """Con il suo comando e il suo motore, fuori dal repository: dal grafo di prima stesura
    al grafo completo, e dal piano alla tavola in PDF, con i rilievi."""
    skill, _ = costruita
    comando = [sys.executable, str(skill / "scripts" / "mep.py")]

    # La prova non installa niente nell'ambiente di chi la lancia: le librerie facoltative
    # che mancano restano mancanti, e il comando lavora senza.
    ambiente_della_prova = {**os.environ, "MEP_SENZA_INSTALLAZIONI": "1"}

    def esegui(*argomenti: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*comando, *argomenti], capture_output=True, text=True, cwd=skill, timeout=300,
            env=ambiente_della_prova,
        )

    ambiente = esegui("ambiente")
    assert ambiente.returncode == 0, ambiente.stderr
    assert f"Motore: {skill / 'scripts' / 'disegnatore_mep'}" in ambiente.stdout, "il motore e' quello della skill"
    completa = esegui("completa", str(BOZZA_6), "--out", str(tmp_path / "grafo-completo.json"))
    assert completa.returncode == 0, completa.stderr
    disegna = esegui(
        "disegna", str(tmp_path / "grafo-completo.json"),
        "--piano", str(IMPIANTO_6 / "piano-6-a.json"), "--out", str(tmp_path / "tavola"),
    )
    assert disegna.returncode == 0, disegna.stdout + disegna.stderr
    assert "tratte cedute 0 · rilievi bloccanti 0" in disegna.stdout
    assert (tmp_path / "tavola" / "prova-6-centrale-ibrida-solare-t1.pdf").read_bytes().startswith(b"%PDF-1.4")
    assert (tmp_path / "tavola" / "prova-6-centrale-ibrida-solare-t1-rilievi.md").exists()

    # La tavola dell'impianto 7, che la prova in camera pulita di REL-001 ha consegnato:
    # dalla skill costruita esce identica, byte per byte, con i dati riaperti dai fasci.
    sette = esegui(
        "disegna", str(IMPIANTO_7 / "grafo-completo.json"),
        "--piano", str(IMPIANTO_7 / "piano.json"), "--out", str(tmp_path / "tavola-7"),
    )
    assert sette.returncode == 0, sette.stdout + sette.stderr
    pdf = tmp_path / "tavola-7" / "riqualificazione-centrale-pdc-cascata-caldaia-t1.pdf"
    assert pdf.read_bytes() == TAVOLA_7.read_bytes()

    voce = esegui("catalogo", "buffer-four-port")
    assert voce.returncode == 0 and json.loads(voce.stdout)["symbol_id"]
    simbolo = esegui("simbolo", json.loads(voce.stdout)["symbol_id"])
    assert simbolo.returncode == 0 and json.loads(simbolo.stdout)["ports"]
    pezzi = esegui("pezzi", str(IMPIANTO_7 / "grafo-completo.json"))
    assert pezzi.returncode == 0 and "Da posare nel piano" in pezzi.stdout
