"""La tratta del prelievo ACS e la giacitura del prelievo (criterio 8).

Il PO, il 14 settembre 2026, guardando la tavola 2:

    «Il primo gomito in uscita non e' sbagliato perche' il disegnatore ha
    tentato di tenere il flusso di lettura da sinistra a destra. Giusto. Non
    capisco pero' perche' abbia forzato a mettersi ACS.01 verso l'alto, pagando
    cosi' una curva inutile. Bastava mettere ACS.01 verso destra ed era
    meglio.»

Lo strumento legge una geometria gia' scritta e stampa, per ogni **confine di
rete** della tavola: la giacitura con cui e' posato e la faccia su cui porta il
proprio attacco, e per la tratta che lo raggiunge le pieghe e la spezzata. Con
questo si chiude il criterio 8, che chiede due cose: nessuna piega oltre quella
che tiene il flusso di lettura da sinistra a destra, e la bocchetta che non
guarda in basso.

    python docs/collaudi/DRAW-010/il-prelievo-acs.py <modello-completo.json> <geometria.json>
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
BOUNDARY = "boundary"


def main(model_path: Path, geometry_path: Path) -> int:
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    model = load_project(model_path)
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    definitions = {item.id: item.definition_id for item in model.components}
    confini = [
        item.id
        for item in model.components
        if BOUNDARY in catalog.get(item.definition_id).functions
    ]
    pipes = {item.id: item for item in model.connections}
    for sheet in geometry["sheets"]:
        placed = {item["component_id"]: item for item in sheet["symbols"]}
        print(f"== tavola {sheet['sheet_id']}")
        for component_id in confini:
            here = placed.get(component_id)
            if here is None:
                print(f"   {component_id}: non e' su questa tavola")
                continue
            resolved = catalog.resolve(definitions[component_id])
            turned = resolved.symbol.manifest.rotated(here["rotation_deg"])
            face = turned.ports[0].face.value
            flow = resolved.definition.ports[0].flow.value
            specie = "ingresso" if flow == "out" else "prelievo"
            print(
                f"   {component_id} ({specie}): rotazione {here['rotation_deg']}, "
                f"attacco sulla faccia {face}"
            )
            for route in sheet["routes"]:
                touched = {
                    ref["component_id"]
                    for key in route["connection_ids"]
                    if key in pipes
                    for ref in (
                        pipes[key].endpoint_a.model_dump(),
                        pipes[key].endpoint_b.model_dump(),
                    )
                }
                if component_id not in touched:
                    continue
                pieghe = sum(
                    max(len(segment) - 2, 0) for segment in route["segments"]
                )
                spezzata = [
                    [(point["x_mm"], point["y_mm"]) for point in segment]
                    for segment in route["segments"]
                ]
                print(
                    f"      tratta {route['connection_ids'][0]}: "
                    f"pieghe={pieghe}  {spezzata}"
                )
        print()
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
