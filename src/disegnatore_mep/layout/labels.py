"""I testi del disegno: solo quelli che aggiungono informazione.

D-052 divide i ruoli: la legenda dice **cosa** e' un simbolo, il tag dice
**quanto** o **quale**. Un tag che ripetesse la denominazione gia' presente in
legenda saturerebbe la tavola senza aggiungere nulla, quindi qui non si scrive
mai il nome di un componente — solo la sua sigla e i suoi valori.

Tutto cio' che si legge e' in italiano (D-051): le sigle vengono dal modello,
le unita' da questa tabella.
"""

from disegnatore_mep.graphics.standard import GraphicStandard
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import JsonPrimitive

from .geometry import PlacedLabel, PlacedSymbol, Point

TAG_GAP_MM = 1.5
"""Stacco fra il riquadro del simbolo e la sigla scritta sopra."""

VALUE_GAP_MM = 1.5
"""Stacco fra il riquadro e il valore scritto sotto."""

CALLOUT_LINE_GAP_MM = 0.5
"""Interlinea fra due testi dello stesso richiamo."""

CHAR_WIDTH_RATIO = 0.6
"""Larghezza media di un carattere rispetto al corpo, per un sans-serif.

Stima: la tavola non incorpora metriche di font. Serve a capire se due testi si
sovrappongono, quindi un errore in eccesso e' innocuo.
"""

UNITS: dict[str, str] = {
    "volume_l": "l",
    "flow_rate_m3h": "m³/h",
    "power_kw": "kW",
    "head_kpa": "kPa",
    "diameter_dn": "DN",
    "temperature_c": "°C",
}
"""Unita' delle proprieta' che si scrivono in tavola.

Una proprieta' che non compare qui non viene stampata: meglio non dirlo che
dirlo senza unita', e la distinta la riportera' comunque per intero.
"""


def format_value(key: str, value: JsonPrimitive) -> str | None:
    unit = UNITS.get(key)
    if unit is None or value is None or isinstance(value, bool):
        return None
    if key == "diameter_dn":
        return f"{unit}{value:g}" if isinstance(value, int | float) else f"{unit}{value}"
    if isinstance(value, float):
        return f"{value:g}".replace(".", ",") + f" {unit}"
    return f"{value} {unit}"


def place_labels(
    project: ProjectModel,
    placed: list[PlacedSymbol],
    standard: GraphicStandard,
    callout_y_mm: float | None = None,
) -> list[PlacedLabel]:
    """Sigle e valori, fuori dal corpo, con linea di richiamo.

    E' il meccanismo di una tavola vera: i testi non si infilano fra i
    componenti sperando che ci stiano, escono sotto il disegno e una linea
    sottile li riporta al pezzo. Sopra il simbolo non ci sta nulla quando il
    disegno si infittisce, e infatti prima collidevano.

    Deterministico: l'ordine segue quello dei simboli posati, e a parita' di
    ascissa i testi scendono di una riga per volta.
    """
    properties = {item.id: item.properties for item in project.components}
    height = standard.text_small_mm
    taken: list[tuple[float, float, float, float]] = [
        (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)
        for item in placed
    ]
    labels: list[PlacedLabel] = []

    def free_slot(x_mm: float, y_mm: float, text: str, upward: bool) -> Point:
        """Il primo posto libero, cercato **allontanandosi** dal simbolo.

        Una sigla scritta sopra il simbolo che cercasse spazio scendendo
        entrerebbe nel simbolo stesso e non ne uscirebbe piu': il verso della
        ricerca segue quello dell'ancoraggio.
        """
        width = len(text) * height * CHAR_WIDTH_RATIO
        stride = -height if upward else height
        candidate_y = y_mm
        for _ in range(24):
            box = (x_mm, candidate_y - height, x_mm + width, candidate_y)
            clash = any(
                box[0] < other[2]
                and other[0] < box[2]
                and box[1] < other[3]
                and other[1] < box[3]
                for other in taken
            )
            if not clash:
                taken.append(box)
                return Point(x_mm=x_mm, y_mm=candidate_y)
            candidate_y += stride
        taken.append((x_mm, candidate_y - height, x_mm + width, candidate_y))
        return Point(x_mm=x_mm, y_mm=candidate_y)

    for item in placed:
        texts: list[tuple[str, str, str]] = []
        if item.tag:
            texts.append((f"{item.component_id}-tag", item.tag, "tag"))
        for key in sorted(properties.get(item.component_id, {})):
            value = format_value(key, properties[item.component_id][key])
            if value is not None:
                texts.append((f"{item.component_id}-{key}", value, "data"))
        if not texts:
            continue

        if callout_y_mm is None:
            for label_id, text, role in texts:
                labels.append(
                    PlacedLabel(
                        id=label_id,
                        text=text,
                        role=role,
                        anchor=free_slot(
                            item.origin.x_mm,
                            item.bottom_mm + VALUE_GAP_MM + height,
                            text,
                            upward=False,
                        ),
                    )
                )
            continue

        # Fuori dal corpo, con la linea di richiamo che riporta al pezzo.
        attach = Point(
            x_mm=item.origin.x_mm + item.width_mm / 2, y_mm=item.bottom_mm
        )
        for offset, (label_id, text, role) in enumerate(texts):
            anchor = free_slot(
                item.origin.x_mm,
                callout_y_mm + offset * (height + CALLOUT_LINE_GAP_MM),
                text,
                upward=False,
            )
            labels.append(
                PlacedLabel(
                    id=label_id,
                    text=text,
                    role=role,
                    anchor=anchor,
                    leader_from=attach if offset == 0 else None,
                )
            )
    return labels
