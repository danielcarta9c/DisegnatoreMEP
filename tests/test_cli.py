import json
from pathlib import Path

from _pytest.capture import CaptureFixture

from disegnatore_mep.cli import main
from disegnatore_mep.model.project import ProjectModel


def test_export_schema(tmp_path: Path) -> None:
    output = tmp_path / "schema.json"
    exit_code = main(["export-schema", str(output)])
    assert exit_code == 0
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["title"] == "ProjectModel"


def test_fingerprint(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    project = ProjectModel.model_validate(
        {
            "metadata": {
                "project_id": "demo",
                "client": "Nove C",
                "project_name": "Demo",
                "commission_code": "MI-001",
                "revision": "00",
                "issue_date": "2026-08-01",
            }
        }
    )
    path = tmp_path / "project.json"
    path.write_text(project.model_dump_json(), encoding="utf-8")
    exit_code = main(["fingerprint", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(captured.out.strip()) == 64


def test_validate_load_error_returns_one(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    assert main(["validate", str(missing), "--catalog", str(catalog)]) == 1


ROOT = Path(__file__).resolve().parents[1]
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"


def test_rules_prints_what_the_catalogue_cannot_offer(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Il difetto per cui P2 e' stato respinto, sul comando che l'ingegnere usa.

    Si toglie dal catalogo lo scarico sanitario e si chiede l'elenco delle
    integrazioni: il bollitore non puo' piu' svuotare la propria riserva, e la
    cosa deve **comparire**. Prima l'ancoraggio veniva scartato in silenzio e
    l'elenco sembrava completo.
    """
    thinned = tmp_path / "catalogo"
    thinned.mkdir()
    for source in sorted(CATALOG.glob("*.json")):
        if source.name == "drain-connection-dhw.json":
            continue
        (thinned / source.name).write_text(source.read_text("utf-8"), encoding="utf-8")

    exit_code = main(
        [
            "rules",
            str(ESSENTIAL),
            "--catalog",
            str(thinned),
            "--symbols",
            str(SYMBOLS),
            "--rules",
            str(RULES),
            "--naming",
            str(NAMING),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Punti aperti" in printed
    assert "acqua calda sanitaria" in printed
    assert "Attacco di scarico" in printed


def test_rules_on_a_complete_model_says_so_and_opens_no_point(
    capsys: CaptureFixture[str], tmp_path: Path
) -> None:
    """L'altro verso: senza lacune, il messaggio di completezza dice il vero.

    Da DRAW-006-R1 il modello completo pubblicato una domanda ce l'ha: il vaso
    sanitario, che l'accumulo non dichiara di portare a bordo (blocco C.2), e
    un dato ignoto non e' un'assenza. Perche' resti provato il verso negativo —
    quello in cui il dossier davvero non ha niente da dire — la domanda si
    chiude dove va chiusa, cioe' **nel catalogo**: qui in una copia di lavoro,
    perche' il dato di un prodotto reale lo dichiara il PM, non questa prova.
    """
    dichiarato = tmp_path / "catalogo"
    dichiarato.mkdir()
    for source in sorted(CATALOG.glob("*.json")):
        (dichiarato / source.name).write_text(source.read_text("utf-8"), encoding="utf-8")
    riserva = dichiarato / "dhw-cylinder.json"
    definition = json.loads(riserva.read_text("utf-8"))
    definition["carries_on_board"] = ["expansion"]
    riserva.write_text(json.dumps(definition, ensure_ascii=False, indent=2), encoding="utf-8")

    exit_code = main(
        [
            "rules",
            str(ROOT / "examples" / "rules" / "centrale-pdc-completa.json"),
            "--catalog",
            str(dichiarato),
            "--symbols",
            str(SYMBOLS),
            "--rules",
            str(RULES),
            "--naming",
            str(NAMING),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Punti aperti" not in printed
    assert "il modello e' gia' completo" in printed


PROVA = ROOT / "examples" / "prova"
COLLAUDO = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_1 = "prova-1-due-pdc-accumulo-combinato.json"


def _completa(impianto: str, tmp_path: Path) -> Path:
    """Il progetto completo, dalla CLI: `rules --apply-all` come lo usa chi compone."""
    completo = tmp_path / "completo.json"
    assert (
        main(
            [
                "rules",
                str(PROVA / impianto),
                "--catalog",
                str(CATALOG),
                "--symbols",
                str(SYMBOLS),
                "--rules",
                str(RULES),
                "--naming",
                str(NAMING),
                "--apply-all",
                "--out",
                str(completo),
            ]
        )
        == 0
    )
    return completo


def _piano(progetto: Path, piano: Path, tmp_path: Path) -> int:
    return main(
        [
            "piano",
            str(progetto),
            "--piano",
            str(piano),
            "--catalog",
            str(CATALOG),
            "--symbols",
            str(SYMBOLS),
            "--naming",
            str(NAMING),
            "--out",
            str(tmp_path / "uscita"),
            "--geometry",
            str(tmp_path / "uscita" / "geometria.json"),
        ]
    )


def test_piano_compone_la_tavola_dell_impianto_1(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """**Criterio 5** dal percorso nuovo: la CLI, non uno script di collaudo.

    Zero rilievi bloccanti e zero tratte cedute, e in testa i pezzi che la
    deduzione ha girato — il tee del manometro compreso, che e' la misura del
    20 settembre.

    Il piano e' quello del pianificatore, agli atti di `DRAW-018`; il grafo e'
    quello che `rules --apply-all` scrive **oggi**, e la prova pretende che
    sia ancora quello su cui il piano e' nato: se le regole cambiano l'impianto
    1, il piano va ricomposto, e questa prova lo dice.
    """
    completo = _completa(IMPIANTO_1, tmp_path)
    assert completo.read_text(encoding="utf-8") == (
        COLLAUDO / "grafo-completo-1.json"
    ).read_text(encoding="utf-8"), "le regole hanno cambiato l'impianto 1: il piano va ricomposto"
    capsys.readouterr()

    esito = _piano(completo, COLLAUDO / "piano-completo-1.json", tmp_path)
    stampato = capsys.readouterr().out

    assert esito == 0
    assert "Girati dalla deduzione (C2)" in stampato
    assert "tee-pressure-gauge-collettore-ritorno-a 0->180" in stampato
    assert "Preflight di qualita'" in stampato
    assert "Tratte cedute: 0 · rilievi bloccanti: 0" in stampato

    tavole = sorted((tmp_path / "uscita").glob("*.svg"))
    assert len(tavole) == 1
    assert "<svg" in tavole[0].read_text(encoding="utf-8")
    geometria = json.loads((tmp_path / "uscita" / "geometria.json").read_text("utf-8"))
    # 25 da D-182: le due sicurezze, una per pompa di calore, portano ciascuna
    # la tratta del proprio stacco.
    assert len(geometria["sheets"][0]["routes"]) == 25
    assert not [r for r in geometria["sheets"][0]["routes"] if r["unresolved"]]


def test_piano_malformato_stampa_il_messaggio_e_non_la_traccia(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """**Criterio 10** sul comando che l'ingegnere usa davvero.

    Uscita 1 come ogni altro errore di caricamento della CLI, e il messaggio
    nomina il pezzo e il campo: non una traccia di stack.
    """
    completo = _completa(IMPIANTO_1, tmp_path)
    storto = tmp_path / "storto.json"
    storto.write_text('{"pezzi": {"accumulo": {"y": 115}}}', encoding="utf-8")
    capsys.readouterr()

    esito = _piano(completo, storto, tmp_path)
    catturato = capsys.readouterr()

    assert esito == 1
    assert "al pezzo «accumulo» manca «x»" in catturato.err
    assert "Traceback" not in catturato.err and "Traceback" not in catturato.out
    assert not (tmp_path / "uscita").exists()


def test_piano_che_nomina_pezzi_inesistenti_li_elenca(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    completo = _completa(IMPIANTO_1, tmp_path)
    fantasma = tmp_path / "fantasma.json"
    fantasma.write_text(
        '{"formato": "A2", "pezzi": {"caldaia-fantasma": {"x": 30, "y": 30}}}',
        encoding="utf-8",
    )
    capsys.readouterr()

    esito = _piano(completo, fantasma, tmp_path)
    catturato = capsys.readouterr()

    assert esito == 1
    assert "non esistono nel modello: caldaia-fantasma" in catturato.err
    assert "Traceback" not in catturato.err


def test_piano_che_non_si_instrada_esce_con_due_e_stampa_la_posa(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Chi compone deve vedere **dove sono finiti i pezzi**, non solo il motivo."""
    completo = _completa(IMPIANTO_1, tmp_path)
    scritto = json.loads((COLLAUDO / "piano-completo-1.json").read_text(encoding="utf-8"))
    ammucchiato = tmp_path / "ammucchiato.json"
    ammucchiato.write_text(
        json.dumps(
            {
                "formato": scritto["formato"],
                "pezzi": {nome: {"x": 60, "y": 60} for nome in scritto["pezzi"]},
            }
        ),
        encoding="utf-8",
    )
    capsys.readouterr()

    esito = _piano(completo, ammucchiato, tmp_path)
    stampato = capsys.readouterr().out

    assert esito == 2
    assert "Il piano non si instrada:" in stampato
    assert "Posa applicata (i pezzi del piano sono marcati con *)" in stampato
    assert "* accumulo" in stampato
    assert not (tmp_path / "uscita").exists()
