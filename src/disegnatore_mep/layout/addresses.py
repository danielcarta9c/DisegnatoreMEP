"""Gli indirizzi dei nodi, attivati esplicitamente sopra una tavola finita.

La tavola di consegna porta le sigle delle macchine principali, e basta. Gli
indirizzi dei nodi (D-105, D-110) sono un **velo** che il PO chiede quando gli
serve puntare un pezzo e nominarlo (I-030): si posano sopra simboli e tubazioni
gia' definitivi e non ne spostano uno. Le due tavole — consegna e verifica —
sono percio' la stessa identica tavola, una con le scritte in piu'; ed e' il
contratto che le prove tengono vero.

Nessuna modalita' entra nella posa o nell'instradamento: il velo si aggiunge
qui, dopo, e da nessun'altra parte.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.lines import read_lines
from disegnatore_mep.graph.naming import LineNaming, Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.model.project import ProjectModel

from .geometry import DrawingGeometry
from .labels import place_addresses

VERIFY_MARK = "MODALITÀ VERIFICA"
"""Come si riconosce a colpo d'occhio una tavola che non e' una consegna.

Sta nell'intestazione, dove il progettista la vede prima del disegno: una tavola
con gli indirizzi addosso non e' quella che va in cantiere, e confonderle
costerebbe piu' di quanto la verifica faccia risparmiare (D-110)."""


def with_addresses(
    drawing: DrawingGeometry,
    project: ProjectModel,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    naming_dir: Path,
) -> DrawingGeometry:
    """La stessa tavola, con l'indirizzo di ogni nodo scritto accanto (D-110).

    Le etichette si posano **sopra una tavola gia' finita** e non spostano
    niente: le due modalita' danno percio' la stessa identica tavola, una con un
    velo in piu'. E' il punto della decisione, e va tenuto vero: cio' che il
    progettista verifica dev'essere esattamente cio' che gli viene consegnato.
    """
    lines = read_lines(
        project,
        catalog,
        read_plant(project, catalog, Naming.from_directory(naming_dir)),
        LineNaming.from_directory(naming_dir),
    )
    sheets = []
    for sheet in drawing.sheets:
        sheets.append(
            sheet.model_copy(
                update={
                    "title": f"{sheet.title} · {VERIFY_MARK}",
                    "labels": [
                        *sheet.labels,
                        *place_addresses(
                            sheet.symbols,
                            lines.addresses,
                            frame.standard,
                            routes=sheet.routes,
                            already=sheet.labels,
                            area=frame.drawing_rect_mm,
                        ),
                    ],
                }
            )
        )
    return drawing.model_copy(update={"sheets": sheets})


__all__ = ["VERIFY_MARK", "with_addresses"]
