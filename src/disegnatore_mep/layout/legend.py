"""La fascia della legenda, costruita dai soli simboli usati.

D-052: la tavola porta a destra una legenda con i simboli usati e il loro
significato, una volta sola. Nel corpo del disegno il componente non viene
ri-spiegato. La divisione dei ruoli e' questa:

    legenda   ->  **cosa** e' un simbolo, una volta per tutta la tavola
    tag       ->  **quanto** o **quale**: i litri di un vaso, la sigla di zona
    disegno   ->  **dove** sta e **come** e' collegato

La legenda si costruisce dai simboli **effettivamente posati**, non
dall'intera libreria: una tavola che elencasse venti simboli per usarne sette
sarebbe piu' lunga da leggere, non piu' chiara.
"""

from collections.abc import Sequence

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.model.project import ProjectModel

from .errors import LayoutError
from .geometry import LegendEntry, NetworkKey, PlacedSymbol, Point, RoutedTrunk

ROW_HEIGHT_MM = 7.5
"""Passo verticale fra due voci: tre passi di griglia."""

SECTION_GAP_MM = 5.0
"""Stacco fra la sezione dei simboli e quella dei fluidi."""

INSET_MM = 2.5
"""Rientro delle voci dal bordo della fascia."""

DEFAULT_STYLE = ("#111111", "none")
"""Nero continuo: cio' che una rete senza codifica dichiarata riceve."""

MEDIUM_STYLES: dict[str, tuple[str, str]] = {
    "heating_water": ("#c0392b", "none"),
    "chilled_water": ("#2471a3", "6 2"),
    "domestic_hot_water": ("#d68910", "none"),
    # Il fluido si chiama "cold_water" in tutto il resto del progetto — nel
    # catalogo, nelle condizioni delle regole, nelle reti degli esempi. Finche'
    # qui stava scritto in un altro modo, ogni rete di acqua fredda cadeva sullo
    # stile di default e si disegnava nera continua come una rete senza codifica.
    "cold_water": ("#5dade2", "3 2"),
    "natural_gas": ("#b7950b", "8 2"),
    "supply_air": ("#148f77", "none"),
    "return_air": ("#148f77", "4 2"),
    "refrigerant_liquid": ("#6c3483", "none"),
    "refrigerant_gas": ("#6c3483", "6 2"),
    "condensate": ("#616a6b", "2 2"),
    # Il circuito solare (D-187): magenta, a tratto pieno come l'acqua di
    # riscaldamento. La tonalita' e' una scelta di questa sessione: lontana dal
    # viola del refrigerante e dal rosso del riscaldamento.
    "solar_fluid": ("#c71585", "none"),
}
"""Colore e tratto per fluido (D-057).

La chiave e' il **fluido**, non il dominio: acqua calda e acqua refrigerata
sono entrambe idroniche e devono distinguersi. Il tratto e' ridondante rispetto
al colore per scelta: una tavola di cantiere viene fotocopiata in bianco e nero.
"""


MEDIUM_NAMES: dict[str, str] = {
    "heating_water": "Acqua di riscaldamento",
    "chilled_water": "Acqua refrigerata",
    "domestic_hot_water": "Acqua calda sanitaria",
    "cold_water": "Acqua fredda sanitaria",
    "natural_gas": "Gas naturale",
    "supply_air": "Aria di mandata",
    "return_air": "Aria di ripresa",
    "refrigerant_liquid": "Refrigerante liquido",
    "refrigerant_gas": "Refrigerante gas",
    "condensate": "Condensa",
    "solar_fluid": "Fluido solare",
}
"""Denominazione italiana del fluido, per la legenda (D-051)."""


RECIRCULATION_COLOUR = "#58d68d"
"""Il verde chiaro del **ricircolo** dell'acqua calda sanitaria (**D-176**).

Il PO, il 23 settembre 2026: «la linea di ricircolo ha un colore a se' (io
generalmente uso il verde chiaro)». E' una modifica della convenzione grafica, e
l'ha decisa lui (D-165). Il ricircolo e' il **ritorno** della rete sanitaria —
l'acqua che le utenze non hanno preso e che torna all'accumulo — quindi il
colore sta dove sta il colore di ogni ritorno. La tonalita' e' una scelta di
questa sessione, fra i verdi chiari che non sono gia' della tavola: l'aria di
mandata e' un verde acqua scuro, e un verde piu' chiaro di questo su carta
bianca non si legge."""

SUPPLY_SHIFT = {
    "#c0392b": "#2471a3",
    "#d68910": RECIRCULATION_COLOUR,
    "#148f77": "#117a65",
    "#6c3483": "#5b2c6f",
    # Il solare torna dello stesso magenta con cui va (D-187): il PO, «magenta
    # sia mandata che ritorno».
    "#c71585": "#c71585",
}
"""Il colore del ritorno, dato quello della mandata.

Su una tavola vera mandata e ritorno sono **due linee diverse**: la legenda
tubazioni le elenca separate, «riscaldamento andata» e «riscaldamento ritorno».
Associare lo stile al solo fluido le rendeva indistinguibili.

Il ritorno dell'acqua calda sanitaria era l'azzurro dell'acqua fredda, a tratto
pieno: finche' nessun impianto lo disegnava non se ne accorgeva nessuno. Da
**D-176** e' il verde chiaro del ricircolo.
"""

RETURN_NAMES: dict[str, str] = {"domestic_hot_water": "ricircolo"}
"""Come si chiama in legenda il ritorno di un fluido, dove non si chiama ritorno.

Il ritorno dell'acqua calda sanitaria e' il **ricircolo**, e il PO lo chiama
cosi' (D-176): una rete aperta non ha altro ritorno che quello."""


def style_for(medium: str, supply: bool = True) -> tuple[str, str]:
    colour, dash = MEDIUM_STYLES.get(medium, DEFAULT_STYLE)
    if supply:
        return colour, dash
    return SUPPLY_SHIFT.get(colour, "#5d6d7e"), dash


def build_legend(
    project: ProjectModel,
    placed: list[PlacedSymbol],
    network_ids: tuple[str, ...],
    catalog: ComponentRegistry,
    frame: SheetFrame,
    routes: Sequence[RoutedTrunk] | None = None,
) -> tuple[list[LegendEntry], list[NetworkKey]]:
    """Le due sezioni della legenda: i simboli usati, poi i fluidi.

    Con `routes` — le tratte che la tavola disegna davvero — le righe dei fluidi
    sono **quelle delle linee disegnate**, e nessun'altra. Senza, restano andata e
    ritorno per ogni fluido presente, come le legge chi compone prima di
    instradare.
    """
    band = frame.legend_rect_mm
    definitions = {item.id: item.definition_id for item in project.components}

    names: dict[str, str] = {}
    for item in placed:
        definition_id = definitions.get(item.component_id)
        if definition_id is None:
            continue
        manifest = catalog.resolve(definition_id).symbol.manifest
        names[manifest.id] = manifest.name

    networks = {item.id: item for item in project.networks}
    used = [networks[item] for item in network_ids if item in networks]
    # Una riga per **fluido**, non per rete: primario e secondario portano la
    # stessa acqua di riscaldamento e si disegnano uguali. Due righe identiche
    # in legenda non distinguono nulla e fanno solo cercare la differenza.
    by_medium: dict[str, str] = {}
    for network in used:
        by_medium.setdefault(
            network.medium, MEDIUM_NAMES.get(network.medium, network.name)
        )
    # Una riga per fluido e per servizio: andata e ritorno sono due linee.
    keys = [
        (
            medium,
            f"{name} — {'andata' if supply else RETURN_NAMES.get(medium, 'ritorno')}",
            supply,
        )
        for medium, name in sorted(by_medium.items())
        for supply in (True, False)
    ]
    # **Una riga per ogni linea che la tavola disegna, e nessuna per quelle che
    # non ci sono.** Fino al 23 settembre 2026 la legenda elencava andata e
    # ritorno di ogni fluido, e sulla tavola di una pompa di calore con la
    # caldaia comparivano «Acqua fredda sanitaria — ritorno» e «Acqua calda
    # sanitaria — ritorno»: l'acqua fredda un ritorno non ce l'ha, e quel
    # ricircolo l'impianto non lo aveva. L'ha visto un agente in camera pulita.
    if routes is not None:
        disegnate = {(route.medium, route.supply) for route in routes}
        keys = [key for key in keys if (key[0], key[2]) in disegnate]
    # Il solare va e torna dello stesso magenta (D-187): due righe uguali non
    # distinguono niente, per la stessa ragione per cui primario e secondario ne
    # hanno una sola. Dove andata e ritorno si disegnano uguali, la coppia si
    # scrive una volta: «andata e ritorno».
    andata = {key[0] for key in keys if key[2]}
    ritorno = {key[0] for key in keys if not key[2]}
    uguali = {
        medium
        for medium in andata & ritorno
        if style_for(medium, supply=True) == style_for(medium, supply=False)
    }
    keys = [
        (medium, f"{by_medium[medium]} — andata e ritorno", supply)
        if medium in uguali
        else (medium, name, supply)
        for medium, name, supply in keys
        if medium not in uguali or supply
    ]

    rows = len(names) + (1 if keys else 0) + len(keys)
    needed = rows * ROW_HEIGHT_MM + (SECTION_GAP_MM if keys else 0.0)
    if needed > band.height_mm:
        raise LayoutError(
            f"the legend needs {needed:g}mm but its band is {band.height_mm:g}mm tall: "
            f"{len(names)} symbols and {len(keys)} networks (text is never shrunk to "
            f"fit; split the plant across more sheets)"
        )

    entries: list[LegendEntry] = []
    y_mm = band.y_mm + ROW_HEIGHT_MM
    for symbol_id in sorted(names):
        entries.append(
            LegendEntry(
                symbol_id=symbol_id,
                name=names[symbol_id],
                anchor=Point(x_mm=band.x_mm + INSET_MM, y_mm=y_mm),
            )
        )
        y_mm += ROW_HEIGHT_MM

    network_keys: list[NetworkKey] = []
    if keys:
        y_mm += SECTION_GAP_MM
        for medium, name, supply in keys:
            colour, dash = style_for(medium, supply)
            network_keys.append(
                NetworkKey(
                    medium=medium,
                    name=name,
                    colour=colour,
                    dash=dash,
                    anchor=Point(x_mm=band.x_mm + INSET_MM, y_mm=y_mm),
                )
            )
            y_mm += ROW_HEIGHT_MM

    return entries, network_keys
