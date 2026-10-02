#!/usr/bin/env python3
"""Costruisce la cartella della skill Disegnatore MEP, e il suo ZIP (REL-001).

    python3 scripts/costruisci-skill.py [--out <cartella>]

Scrive `<cartella>/disegnatore-mep/` — la skill — e `<cartella>/disegnatore-mep.zip` —
quella che si carica in Claude —; di norma `<cartella>` e' `outputs/skill`, che git
ignora. **La cartella non si copia e non si ritocca a mano**: si ricostruisce, come i
generatori della libreria, e due costruzioni dagli stessi file danno gli stessi byte,
ZIP compreso (`tests/skill/test_costruzione_della_skill.py`).

Che cosa ci mette, e da dove:

| nella skill | dal repository |
|---|---|
| `SKILL.md` | `skill/SKILL.md` — l'ingresso |
| `riferimenti/capire.md`, `comporre.md`, `rivedere.md` | le istruzioni in `skill/<pezzo>/ISTRUZIONI.md` |
| `riferimenti/regole-del-piano.md` | `docs/regole-del-piano.md` |
| `scripts/mep.py` | `skill/scripts/mep.py` — il comando |
| `scripts/disegnatore_mep/` | `src/disegnatore_mep/` — il motore, tutto |
| `scripts/grafo_leggibile.py` | `examples/graph/build_plant_graph.py` — chi scrive il grafo da leggere |
| `dati/simboli.json` | `assets/symbols/`, in un file solo |
| `dati/catalogo.json` | `examples/layout/catalog/`, in un file solo |
| `dati/regole.json` | `rules/hydronic/`, in un file solo |
| `dati/naming/` | `naming/` |
| `dati/cartiglio/` | `assets/cartigli/Cartiglio_NoveC_A3.json` e il suo logo |
| `dati/schema/project.schema.json` | `schemas/project.schema.json` |
| `LICENSE.txt` | `LICENSE` |

**Simboli, catalogo e regole stanno in un file ciascuno** (`disegnatore_mep.skill.FASCI`):
il caricamento su claude.ai accetta al massimo 200 file, e quelle tre cartelle da sole
ne erano 183 (I-171). Il comando li riapre da se', e una voce o un manifesto si
leggono con `mep.py catalogo <id>` e `mep.py simbolo <id>`.

**Le istruzioni dei tre pezzi si copiano come sono**, e cambiano solo **i percorsi** —
nel repository una voce del catalogo e' un file di `examples/layout/catalog`, nella
skill la stampa `mep.py catalogo <id>` — e **il comando di validazione** di Capire, che
nel repository chiama l'interprete di sviluppo e nella skill `scripts/mep.py`. Ogni sostituzione dichiara
quante volte deve applicarsi: se il testo di partenza cambia e una sostituzione non
trova piu' il suo posto, la costruzione si ferma e lo dice, invece di lasciare nella
skill un percorso che li' non esiste. Ai file lunghi piu' di cento righe si mette in
testa l'indice dei capitoli, come la guida di Anthropic chiede.

**I controlli della guida** «Skill authoring best practices», del validatore di
`skill-creator` e del caricamento su claude.ai girano qui, a ogni costruzione: il nome e
la descrizione nei loro limiti, i soli campi ammessi nel frontespizio, un solo
`SKILL.md`, il corpo sotto le 500 righe, ogni file che `SKILL.md` nomina presente, nessun
percorso del repository rimasto nei riferimenti; e lo ZIP con al massimo 200 file, sotto
i 30 MB, la skill in una cartella sola alla radice e nessuna voce di cartella.
"""

import argparse
import hashlib
import re
import shutil
import stat
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.skill import FASCI, fascio_della_cartella  # noqa: E402

NOME = "disegnatore-mep"
USCITA = ROOT / "outputs" / "skill"

DATA_DELLO_ZIP = (1980, 1, 1, 0, 0, 0)
"""La data di ogni voce dello ZIP: la prima che il formato ammette. Con la data vera
dei file, due costruzioni dagli stessi file darebbero due ZIP diversi."""

RIGHE_PER_L_INDICE = 100
"""Oltre questa lunghezza un file di riferimento porta l'indice dei capitoli in testa
(«Structure longer reference files with table of contents», guida di Anthropic)."""

RIGHE_MASSIME_DI_SKILL_MD = 500
"""Il corpo di `SKILL.md` sta sotto le 500 righe (guida di Anthropic, «Token budgets»)."""

CHIAVI_AMMESSE = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
"""Le chiavi del frontespizio che il validatore di `skill-creator` accetta."""

CARATTERI_DELLA_DESCRIZIONE = 200
"""La descrizione per claude.ai: «200 characters maximum» (centro d'aiuto di Anthropic,
«Creating custom Skills», 22 luglio 2026). La specifica ne ammette 1024, e anche quelli si
controllano; si tiene la misura piu' stretta."""

CARATTERI_DELLA_COMPATIBILITA = 500
"""Il campo `compatibility`: al massimo 500 caratteri (validatore di `skill-creator`)."""

FILE_NELLO_ZIP = 200
"""Il caricamento su claude.ai: «Zip contains too many files (maximum 200)» — lo ZIP di
`REL-001`, con 287 file, si e' fermato li' (I-171)."""

BYTE_DELLA_SKILL = 30 * 1024 * 1024
"""«Total upload size must be under 30 MB (uncompressed)» (Anthropic, guida delle Skills
per l'API); su claude.ai 30 MB e' anche il limite di ogni file."""

FUORI_DAL_PACCHETTO = {"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}


@dataclass(frozen=True)
class Sostituzione:
    vecchio: str
    nuovo: str
    volte: int
    perche: str


PERCORSI_DI_CAPIRE = (
    Sostituzione("| Cosa | Dove sta nel repository | A cosa serve |",
                 "| Cosa | Dove sta nella skill | A cosa serve |", 1,
                 "la tabella dice dove stanno i file"),
    Sostituzione("`examples/layout/catalog/*.json` (un file per pezzo)",
                 "`python3 scripts/mep.py catalogo` (una riga per voce), `catalogo <id>` (la voce intera)",
                 1, "il catalogo sta in un file solo, e una voce la stampa il comando"),
    Sostituzione("`naming/families.json`", "`dati/naming/families.json`", 2, "i mestieri"),
    Sostituzione("`naming/media.json`", "`dati/naming/media.json`", 2, "i fluidi"),
    Sostituzione("`schemas/project.schema.json`", "`dati/schema/project.schema.json`", 1,
                 "lo schema del modello"),
    Sostituzione("**eseguirlo non è leggere il repository**",
                 "**eseguirlo non è leggere la cartella della skill**", 1,
                 "nella skill non c'e' un repository"),
    Sostituzione("Il comando va lanciato **dalla radice del repository**, dove vive\n"
                 "   l'interprete Python,",
                 "Il comando va lanciato **dalla cartella della skill**, dove vive\n"
                 "   il comando,", 1, "da dove si lancia il comando"),
    Sostituzione("Eseguire questo comando non è leggere il repository:",
                 "Eseguire questo comando non è leggere la cartella della skill:", 1,
                 "nella skill non c'e' un repository"),
    Sostituzione(".venv/bin/python -c \"from pathlib import Path; from disegnatore_mep.io.project_json "
                 "import load_project; load_project(Path('/percorso/completo/del/tuo/file.json'))\"",
                 "python3 scripts/mep.py valida /percorso/completo/del/tuo/file.json", 1,
                 "il comando di validazione della skill"),
    Sostituzione("Nessun output = il file carica.",
                 "«Il grafo si legge», e nessun rilievo bloccante = il file carica.", 1,
                 "che cosa stampa il comando di validazione della skill"),
)

PERCORSI_DI_COMPORRE = (
    Sostituzione("(`assets/symbols/<id>.json`)", "(`python3 scripts/mep.py simbolo <id>`)", 1,
                 "i manifesti stanno in un file solo, e uno lo stampa il comando"),
    Sostituzione("`examples/layout/catalog/<definition_id>.json`",
                 "`python3 scripts/mep.py catalogo <definition_id>`", 1,
                 "il catalogo sta in un file solo, e una voce la stampa il comando"),
    Sostituzione("`assets/symbols/<symbol_id>.json`", "`python3 scripts/mep.py simbolo <symbol_id>`", 1,
                 "i manifesti stanno in un file solo, e uno lo stampa il comando"),
)

PERCORSI_DI_RIVEDERE = (
    Sostituzione("(`regole-del-piano.md`)", "(`riferimenti/regole-del-piano.md`)", 1, "le regole"),
)

NOTA_DELLE_REGOLE = (
    "> **Nella skill.** I rimandi a `docs/…` e ai collaudi sono le fonti di ogni regola nel "
    "repository del progetto: dicono da dove viene la regola, e nella skill non ci sono.\n"
)

PERCORSI_DEL_REPOSITORY = re.compile(
    r"(?<![\w/])(examples/layout|assets/symbols|assets/cartigli|schemas/|rules/hydronic|\.venv/|"
    r"naming/(?:families|media|lines)\.json)"
)
"""Percorsi che esistono nel repository e non nella skill: nei riferimenti non restano."""


class ErroreDiCostruzione(RuntimeError):
    """La skill non si costruisce: si dice perche', e non si scrive niente di mezzo."""


def _sostituisci(testo: str, sostituzioni: tuple[Sostituzione, ...], nome: str) -> str:
    for s in sostituzioni:
        trovate = testo.count(s.vecchio)
        if trovate != s.volte:
            raise ErroreDiCostruzione(
                f"{nome}: «{s.vecchio[:60]}» ({s.perche}) si trova {trovate} volte invece di "
                f"{s.volte}: il testo di partenza e' cambiato, e la sostituzione va rivista"
            )
        testo = testo.replace(s.vecchio, s.nuovo)
    return testo


def _con_l_indice(testo: str) -> str:
    """Mette l'indice dei capitoli dopo il titolo di un file lungo."""
    righe = testo.splitlines()
    if len(righe) <= RIGHE_PER_L_INDICE:
        return testo
    capitoli = [r[3:].strip() for r in righe if r.startswith("## ")]
    indice = ["## Indice", "", *[f"- {c}" for c in capitoli], ""]
    titolo = next(i for i, r in enumerate(righe) if r.startswith("# "))
    return "\n".join([*righe[: titolo + 1], "", *indice, *righe[titolo + 1 :]]) + "\n"


def _copia(sorgente: Path, destinazione: Path) -> None:
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(sorgente, destinazione)


def _copia_cartella(sorgente: Path, destinazione: Path, estensioni: tuple[str, ...] | None = None) -> None:
    for percorso in sorted(sorgente.rglob("*")):
        relativo = percorso.relative_to(sorgente)
        if not percorso.is_file() or FUORI_DAL_PACCHETTO & set(relativo.parts):
            continue
        if percorso.suffix == ".pyc" or (estensioni and percorso.suffix not in estensioni):
            continue
        _copia(percorso, destinazione / relativo)


def _scrivi(percorso: Path, testo: str) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    percorso.write_text(testo, encoding="utf-8", newline="\n")


INDICATORI_YAML = tuple("-?:,[]{}#&*!|>'\"%@`")
"""I caratteri con cui un valore YAML senza virgolette non puo' cominciare."""


def _frontespizio(testo: str) -> dict[str, str]:
    """Il frontespizio, letto con le regole dei valori YAML senza virgolette: una riga
    per chiave, e nel valore niente «: » e niente « #», che per YAML cominciano un'altra
    chiave o un commento. Claude rifiuta un frontespizio che YAML non legge, e il
    29 settembre la descrizione con «dimensiona: disegna» l'avrebbe fatto."""
    trovato = re.match(r"^---\n(.*?)\n---\n", testo, re.S)
    if trovato is None:
        raise ErroreDiCostruzione("SKILL.md non comincia con il frontespizio fra due righe ---")
    campi: dict[str, str] = {}
    for riga in trovato.group(1).splitlines():
        chiave, separatore, valore = riga.partition(": ")
        valore = valore.strip()
        if not separatore or not re.fullmatch(r"[a-z-]+", chiave):
            raise ErroreDiCostruzione(f"riga del frontespizio che YAML non legge: {riga[:60]!r}")
        if ": " in valore or " #" in valore or valore.endswith(":") or valore.startswith(INDICATORI_YAML):
            raise ErroreDiCostruzione(
                f"il valore di {chiave!r} va scritto senza «: », « #» e senza cominciare con "
                f"un segno di YAML: cosi' com'e' Claude non lo legge"
            )
        campi[chiave] = valore
    return campi


def controlla(skill: Path) -> list[str]:
    """I controlli della guida di Anthropic e del validatore di `skill-creator`: la lista
    di quello che non va, vuota se va tutto."""
    difetti: list[str] = []
    ingresso = skill / "SKILL.md"
    testo = ingresso.read_text(encoding="utf-8")
    campi = _frontespizio(testo)
    nome, descrizione = campi.get("name", ""), campi.get("description", "")
    if set(campi) - CHIAVI_AMMESSE:
        difetti.append(f"chiavi del frontespizio non ammesse: {sorted(set(campi) - CHIAVI_AMMESSE)}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", nome) or len(nome) > 64:
        difetti.append(f"il nome {nome!r} non e' minuscole, cifre e trattini entro 64 caratteri")
    if "anthropic" in nome or "claude" in nome:
        difetti.append(f"il nome {nome!r} contiene una parola riservata")
    if nome != skill.name:
        difetti.append(f"il nome {nome!r} non e' quello della cartella {skill.name!r}")
    if not descrizione or len(descrizione) > 1024:
        difetti.append(f"la descrizione ha {len(descrizione)} caratteri: vuota o oltre 1024")
    if len(descrizione) > CARATTERI_DELLA_DESCRIZIONE:
        difetti.append(
            f"la descrizione ha {len(descrizione)} caratteri: claude.ai ne vuole al massimo "
            f"{CARATTERI_DELLA_DESCRIZIONE}"
        )
    if len(campi.get("compatibility", "")) > CARATTERI_DELLA_COMPATIBILITA:
        difetti.append(f"il campo compatibility supera {CARATTERI_DELLA_COMPATIBILITA} caratteri")
    if "<" in descrizione or ">" in descrizione:
        difetti.append("la descrizione contiene parentesi angolari")
    corpo = testo.split("\n---\n", 1)[1]
    if len(corpo.splitlines()) >= RIGHE_MASSIME_DI_SKILL_MD:
        difetti.append(f"il corpo di SKILL.md ha {len(corpo.splitlines())} righe")
    altri = [p for p in skill.rglob("SKILL.md") if p != ingresso]
    if altri:
        difetti.append(f"altri SKILL.md oltre all'ingresso: {altri}")
    for nominato in sorted(set(re.findall(r"\]\(([^)#]+)\)", corpo))):
        if not (skill / nominato).exists():
            difetti.append(f"SKILL.md rimanda a {nominato}, che nella skill non c'e'")
    for nominato in sorted(set(re.findall(r"`((?:scripts|dati|riferimenti)/[^`<$ ]+)`", corpo))):
        if not (skill / nominato.rstrip("/")).exists():
            difetti.append(f"SKILL.md nomina {nominato}, che nella skill non c'e'")
    for riferimento in sorted((skill / "riferimenti").glob("*.md")):
        contenuto = riferimento.read_text(encoding="utf-8")
        if riferimento.name != "regole-del-piano.md":
            for trovato in PERCORSI_DEL_REPOSITORY.findall(contenuto):
                difetti.append(f"{riferimento.name}: percorso del repository rimasto: {trovato}")
        if len(contenuto.splitlines()) > RIGHE_PER_L_INDICE and "## Indice" not in contenuto:
            difetti.append(f"{riferimento.name}: oltre {RIGHE_PER_L_INDICE} righe senza indice")
        if f"riferimenti/{riferimento.name}" not in corpo:
            difetti.append(f"{riferimento.name}: SKILL.md non lo nomina (i riferimenti stanno a un livello)")
    file = [p for p in skill.rglob("*") if p.is_file()]
    if len(file) > FILE_NELLO_ZIP:
        difetti.append(f"la skill ha {len(file)} file: il caricamento su claude.ai ne accetta {FILE_NELLO_ZIP}")
    if sum(p.stat().st_size for p in file) >= BYTE_DELLA_SKILL:
        difetti.append("la skill supera i 30 MB")
    for percorso in sorted(skill.rglob("*")):
        relativo = percorso.relative_to(skill)
        if percorso.suffix == ".md" and re.search(r"[\w.-]\\[\w.-]", percorso.read_text(encoding="utf-8")):
            difetti.append(f"{relativo}: un percorso con la barra rovesciata")
        if FUORI_DAL_PACCHETTO & set(relativo.parts) or percorso.suffix == ".pyc":
            difetti.append(f"{relativo}: non va nel pacchetto")
    return difetti


def costruisci(uscita: Path) -> tuple[Path, Path]:
    """La cartella della skill e il suo ZIP, dentro `uscita`."""
    skill = uscita / NOME
    if skill.exists():
        shutil.rmtree(skill)
    skill.mkdir(parents=True)

    _copia(ROOT / "skill" / "SKILL.md", skill / "SKILL.md")
    riferimenti = skill / "riferimenti"
    for pezzo, sostituzioni in (
        ("capire", PERCORSI_DI_CAPIRE),
        ("comporre", PERCORSI_DI_COMPORRE),
        ("rivedere", PERCORSI_DI_RIVEDERE),
    ):
        testo = (ROOT / "skill" / pezzo / "ISTRUZIONI.md").read_text(encoding="utf-8")
        _scrivi(riferimenti / f"{pezzo}.md", _con_l_indice(_sostituisci(testo, sostituzioni, pezzo)))
    regole = (ROOT / "docs" / "regole-del-piano.md").read_text(encoding="utf-8")
    titolo, _, resto = regole.partition("\n")
    _scrivi(riferimenti / "regole-del-piano.md", _con_l_indice(f"{titolo}\n\n{NOTA_DELLE_REGOLE}{resto}"))

    scripts = skill / "scripts"
    _copia(ROOT / "skill" / "scripts" / "mep.py", scripts / "mep.py")
    _copia(ROOT / "examples" / "graph" / "build_plant_graph.py", scripts / "grafo_leggibile.py")
    _copia_cartella(ROOT / "src" / "disegnatore_mep", scripts / "disegnatore_mep")

    dati = skill / "dati"
    for nome, sorgente in zip(
        FASCI, (ROOT / "assets" / "symbols", ROOT / "examples" / "layout" / "catalog", ROOT / "rules" / "hydronic"),
        strict=True,
    ):
        _scrivi(dati / f"{nome}.json", fascio_della_cartella(sorgente, nome))
    _copia_cartella(ROOT / "naming", dati / "naming", (".json",))
    for nome in ("Cartiglio_NoveC_A3.json", "Cartiglio_NoveC_A3-logo.jpg"):
        _copia(ROOT / "assets" / "cartigli" / nome, dati / "cartiglio" / nome)
    _copia(ROOT / "schemas" / "project.schema.json", dati / "schema" / "project.schema.json")
    _copia(ROOT / "LICENSE", skill / "LICENSE.txt")

    difetti = controlla(skill)
    if difetti:
        shutil.rmtree(skill)
        raise ErroreDiCostruzione("la skill non passa i controlli:\n  - " + "\n  - ".join(difetti))

    archivio = uscita / f"{NOME}.zip"
    with zipfile.ZipFile(archivio, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zip_:
        for percorso in sorted(skill.rglob("*")):
            if not percorso.is_file():
                continue
            voce = zipfile.ZipInfo(percorso.relative_to(uscita).as_posix(), DATA_DELLO_ZIP)
            voce.compress_type = zipfile.ZIP_DEFLATED
            voce.external_attr = (stat.S_IFREG | 0o644) << 16
            zip_.writestr(voce, percorso.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(archivio) as zip_:
        voci = zip_.infolist()
    # Come lo legge il caricamento: le voci, non i file della cartella.
    if len(voci) > FILE_NELLO_ZIP or any(
        v.is_dir() or not v.filename.startswith(f"{NOME}/") or "\\" in v.filename for v in voci
    ):
        archivio.unlink()
        raise ErroreDiCostruzione(
            f"lo ZIP ha {len(voci)} voci, o una voce di cartella, o una voce fuori da {NOME}/: "
            f"il caricamento su claude.ai ne vuole al massimo {FILE_NELLO_ZIP}, tutte in {NOME}/"
        )
    return skill, archivio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Costruisce la skill Disegnatore MEP e il suo ZIP.")
    parser.add_argument("--out", type=Path, default=USCITA)
    args = parser.parse_args(argv)
    try:
        skill, archivio = costruisci(args.out)
    except ErroreDiCostruzione as errore:
        print(f"Errore: {errore}", file=sys.stderr)
        return 1
    file = [p for p in skill.rglob("*") if p.is_file()]
    print(f"Skill: {skill} ({len(file)} file, {sum(p.stat().st_size for p in file) // 1024} kB)")
    print(f"ZIP:   {archivio} ({archivio.stat().st_size // 1024} kB, "
          f"sha256 {hashlib.sha256(archivio.read_bytes()).hexdigest()[:16]})")
    print("Controlli della guida di Anthropic e di skill-creator: passati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
