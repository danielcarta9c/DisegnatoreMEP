"""La tavola di prova di REL-012, fase 1: la parte comune del motore, su un caso piccolo.

    PYTHONPATH=src python3 examples/aria_elettrico/tavola_di_prova.py <cartella-di-uscita>

Un'unita' esterna e un'unita' interna canalizzata, una bocchetta, una ripresa, lo
scarico della condensa col sifone, il quadro col sezionatore di prossimita' e il
comando a filo: **refrigerante, aria, condensa, alimentazione, collegamento UI-UE e
bus** sulla stessa tavola. Mostra:

- i fluidi senza verso — una riga sola in legenda, nessuna freccia su refrigerante,
  cavi e bus, le frecce su aria e condensa (`layout.fluidi`, proposta);
- la scritta di ogni tratto come dato del grafo, «Ø · L», con la sua riga di legenda
  (`diametri.scritte`); il cavo dell'alimentazione ne ha due, una per tubazione;
- le zone delle tabelle chieste dal piano (`zone_tabelle`) e le tabelle disegnate dal
  motore (`graphics.tabelle`): le tratte a destra, le note e un computo di prova in
  basso, che continua nella colonna accanto;
- il sezionatore dalla parte della macchina, la sigla e la scritta libera del comando
  che sta in tabella, le sigle della famiglia per tutti (§6 del kit).

**Non e' un progetto e non ha dati di un cliente.** I simboli e le voci di catalogo
dell'aria-aria sono quelli del kit del PO (`docs/input-pm/2026-10-29-kit-aria-aria/`),
letti accanto alla libreria di oggi: nella libreria li porta la fase 2.
"""

import shutil
import sys
import tempfile
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.scritte import numero_italiano, testo_della_tubazione
from disegnatore_mep.graphics.cartiglio import Cartiglio, CartiglioDellaTavola, valori_del_cartiglio
from disegnatore_mep.graphics.pdf import scrivi_pdf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import (
    ColonnaDellaTabella,
    RigaDellaTabellaLibera,
    TabellaNelleZone,
)
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano

QUI = Path(__file__).resolve().parent
ROOT = QUI.parents[1]
KIT = ROOT / "docs" / "input-pm" / "2026-10-29-kit-aria-aria" / "per-il-repo"
GRAFO = QUI / "grafo-di-prova.json"
PIANO = QUI / "piano-di-prova.json"
NAMING = ROOT / "naming"
CARTIGLIO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"


def cartelle_di_prova(base: Path) -> tuple[Path, Path]:
    """Simboli e catalogo di oggi, con quelli del kit accanto, in `base`."""
    simboli, catalogo = base / "simboli", base / "catalogo"
    shutil.copytree(ROOT / "assets" / "symbols", simboli)
    shutil.copytree(ROOT / "examples" / "layout" / "catalog", catalogo)
    for sorgente, destinazione in (
        (KIT / "assets" / "symbols", simboli),
        (KIT / "examples" / "layout" / "catalog", catalogo),
    ):
        for file in sorted(sorgente.iterdir()):
            if not (destinazione / file.name).exists():
                shutil.copy(file, destinazione / file.name)
    return simboli, catalogo


def _da_a(modello: ProjectModel, tubazione: str) -> str:
    tubo = next(item for item in modello.connections if item.id == tubazione)
    return f"{tubo.endpoint_a.component_id} - {tubo.endpoint_b.component_id}"


def tabelle_di_prova(modello: ProjectModel) -> list[TabellaNelleZone]:
    """Le tabelle che un altro modulo — qui la prova, domani la distinta — passa al
    motore: le tratte dai dati del grafo, a destra; le note e un computo di prova,
    in basso."""
    tratte = [
        RigaDellaTabellaLibera(
            celle=[
                item.id,
                _da_a(modello, item.id),
                item.sezione or "",
                numero_italiano(item.lunghezza_m) if item.lunghezza_m is not None else "",
            ]
        )
        for item in modello.connections
        if testo_della_tubazione(item) is not None
    ]
    note = [
        RigaDellaTabellaLibera(sezione="A. Fluidi senza verso (proposta della sessione)"),
        RigaDellaTabellaLibera(
            celle=[
                "A.1",
                "Aria, refrigerante, condensa, alimentazione, collegamento e bus hanno una riga sola "
                "in legenda. Refrigerante, cavi e bus non portano la freccia di flusso: la macchina e' "
                "reversibile, e su un cavo la freccia non dice niente.",
            ]
        ),
        RigaDellaTabellaLibera(sezione="B. Scritte dei tratti"),
        RigaDellaTabellaLibera(
            celle=[
                "B.1",
                "Sezione e lunghezza sono dati del progettista, non un dimensionamento: la pendenza "
                "della condensa ≥ 1 % e l'isolamento ≥ 13 mm si leggono qui, e nel PDF diventano >=.",
            ]
        ),
        RigaDellaTabellaLibera(celle=["B.2", "Quadro → sezionatore → unita' esterna: due cavi, due scritte."]),
    ]
    computo = [
        RigaDellaTabellaLibera(sezione="C. Computo di prova (quantita' finte)"),
        *(
            RigaDellaTabellaLibera(celle=[f"C.{n}", f"Voce di prova numero {n}", "m", numero_italiano(n * 1.5)])
            for n in range(1, 25)
        ),
    ]
    return [
        TabellaNelleZone(
            titolo="TABELLA DELLE TRATTE — dati del progettista",
            colonne=[
                ColonnaDellaTabella(intestazione="Tubazione", larghezza_mm=22),
                ColonnaDellaTabella(intestazione="Da - a", larghezza_mm=50),
                ColonnaDellaTabella(intestazione="Sezione", larghezza_mm=50),
                ColonnaDellaTabella(intestazione="L m", larghezza_mm=17, a_destra=True),
            ],
            righe=tratte,
            zona="destra",
        ),
        TabellaNelleZone(
            titolo="NOTE DELLA TAVOLA DI PROVA",
            colonne=[
                ColonnaDellaTabella(intestazione="Rif.", larghezza_mm=12),
                ColonnaDellaTabella(intestazione="Nota", larghezza_mm=150),
            ],
            righe=note,
            zona="basso",
        ),
        TabellaNelleZone(
            titolo="COMPUTO DI PROVA — continua nella colonna accanto",
            colonne=[
                ColonnaDellaTabella(intestazione="Rif.", larghezza_mm=12),
                ColonnaDellaTabella(intestazione="Voce", larghezza_mm=70),
                ColonnaDellaTabella(intestazione="UM", larghezza_mm=12),
                ColonnaDellaTabella(intestazione="Q.tà", larghezza_mm=16, a_destra=True),
            ],
            righe=computo,
            zona="basso",
        ),
    ]


def esegui(simboli: SymbolRegistry, catalogo: ComponentRegistry) -> tuple[ProjectModel, EsitoDelPiano]:
    modello = load_project(GRAFO)
    piano = carica_piano(PIANO)
    esito = esegui_piano(modello, piano, catalogo, simboli, NAMING, tabelle=tabelle_di_prova(modello))
    return modello, esito


def disegna(uscita: Path) -> EsitoDelPiano:
    """SVG, PDF, DXF, i rilievi e l'anteprima PNG della tavola di prova in `uscita`."""
    from disegnatore_mep.graphics.dxf import write_dxf
    from disegnatore_mep.skill import anteprima

    uscita.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as provvisoria:
        cartella_simboli, cartella_catalogo = cartelle_di_prova(Path(provvisoria))
        simboli = SymbolRegistry.from_directory(cartella_simboli)
        catalogo = ComponentRegistry.from_directory(cartella_catalogo, symbols=simboli)
        modello, esito = esegui(simboli, catalogo)
        if esito.disegno is None:
            raise SystemExit(f"la tavola di prova non si instrada: {esito.errore}")
        foglio = esito.disegno.sheets[0]
        tavola = CartiglioDellaTavola(
            cartiglio=Cartiglio.da_file(CARTIGLIO), valori=valori_del_cartiglio(modello, foglio.sheet_id)
        )
        nome = f"{modello.metadata.project_id}-{foglio.sheet_id}"
        svg = uscita / f"{nome}.svg"
        svg.write_text(render_sheet(foglio, esito.frame, simboli, tavola), encoding="utf-8")
        pdf = scrivi_pdf(svg, titolo=modello.metadata.project_name)
        write_dxf(foglio, esito.frame, simboli, svg.with_suffix(".dxf"), tavola)
        anteprima(svg, uscita / f"{nome}.png", 110)
        righe = [f"# Rilievi della tavola di prova — {foglio.title}", ""]
        righe += [f"- `{item.code}` ({item.severity.value}): {item.message}" for item in esito.rilievi] or [
            "- nessun rilievo"
        ]
        righe += ["", "## Sostituzioni del PDF", ""]
        righe += [f"- «{item.carattere}» in «{item.scritta}» -> «{item.con}»" for item in pdf.sostituzioni] or [
            "- nessuna"
        ]
        (uscita / f"{nome}-rilievi.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    return esito


if __name__ == "__main__":
    esito = disegna(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tavola-di-prova"))
    print(f"rilievi: {[(item.code, item.severity.value) for item in esito.rilievi]}")
