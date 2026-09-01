"""I controlli geometrici della specifica §12.2.

I controlli tecnici rispondono a «questo impianto sta in piedi?»; questi
rispondono a «questa tavola e' disegnata bene?». Nessuno dei due giudica la
qualita' percettiva: quella la dice solo l'occhio, e la stampa (§12.4).
"""

from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    SheetGeometry,
    intrudes_into,
)
from disegnatore_mep.layout.labels import CHAR_WIDTH_RATIO
from disegnatore_mep.model.types import IssueSeverity

from .issues import ValidationIssue, ValidationReport

TOLERANCE_MM = 1e-6


def _issue(code: str, message: str, entity_ids: list[str]) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=IssueSeverity.BLOCKING,
        message=message,
        entity_ids=entity_ids,
    )


def _overlap(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> bool:
    return (
        first[0] < second[2] - TOLERANCE_MM
        and second[0] < first[2] - TOLERANCE_MM
        and first[1] < second[3] - TOLERANCE_MM
        and second[1] < first[3] - TOLERANCE_MM
    )


def _box(symbol: PlacedSymbol) -> tuple[float, float, float, float]:
    return (symbol.origin.x_mm, symbol.origin.y_mm, symbol.right_mm, symbol.bottom_mm)


def validate_sheet_geometry(
    sheet: SheetGeometry, frame: SheetFrame
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    drawing = frame.drawing_rect_mm
    legend_band = frame.legend_rect_mm

    for symbol in sheet.symbols:
        box = _box(symbol)
        if not (
            drawing.x_mm - TOLERANCE_MM <= box[0]
            and drawing.y_mm - TOLERANCE_MM <= box[1]
            and box[2] <= drawing.right_mm + TOLERANCE_MM
            and box[3] <= drawing.bottom_mm + TOLERANCE_MM
        ):
            issues.append(
                _issue(
                    "SYMBOL_OUTSIDE_DRAWING_AREA",
                    f"symbol {symbol.component_id} leaves the drawing area",
                    [sheet.sheet_id, symbol.component_id],
                )
            )

    for index, first in enumerate(sheet.symbols):
        for second in sheet.symbols[index + 1 :]:
            if _overlap(_box(first), _box(second)):
                issues.append(
                    _issue(
                        "SYMBOL_OVERLAP",
                        f"symbols {first.component_id} and {second.component_id} overlap",
                        sorted([sheet.sheet_id, first.component_id, second.component_id]),
                    )
                )

    for route in sheet.routes:
        for segment in route.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                if (
                    abs(before.x_mm - after.x_mm) > TOLERANCE_MM
                    and abs(before.y_mm - after.y_mm) > TOLERANCE_MM
                ):
                    issues.append(
                        _issue(
                            "SEGMENT_NOT_ORTHOGONAL",
                            f"a segment of run {route.connection_ids} is neither "
                            f"horizontal nor vertical",
                            [sheet.sheet_id, *route.connection_ids],
                        )
                    )
                for symbol in sheet.symbols:
                    # D-027 — **attraversare basta**, non serve essere coperti,
                    # e il contenimento resta quello che era. La misura vecchia
                    # guardava solo se il riquadro contenesse il tratto, e non
                    # vedeva chi entrava da un lato e usciva dall'altro; quella
                    # nuova le si **aggiunge**, non la sostituisce, perche' la
                    # vecchia prendeva anche la linea che corre a filo del
                    # fianco — un difetto di rappresentazione che non tocca al
                    # disegnatore riscrivere. Il tratto che termina su un
                    # attacco resta ammesso per costruzione: una porta sta sul
                    # perimetro, quindi quel tratto tocca il bordo, non entra
                    # nel corpo e non ci corre dentro.
                    if intrudes_into(_box(symbol), before, after):
                        issues.append(
                            _issue(
                                "LINE_UNDER_SYMBOL",
                                f"a run passes under symbol {symbol.component_id} "
                                f"instead of being broken by it",
                                [sheet.sheet_id, symbol.component_id],
                            )
                        )

    height = frame.standard.text_small_mm
    boxes = [_box(symbol) for symbol in sheet.symbols]
    for label in sheet.labels:
        width = len(label.text) * height * CHAR_WIDTH_RATIO
        box = (
            label.anchor.x_mm,
            label.anchor.y_mm - height,
            label.anchor.x_mm + width,
            label.anchor.y_mm,
        )
        if any(_overlap(box, other) for other in boxes):
            issues.append(
                _issue(
                    "LABEL_COLLISION",
                    f"label {label.id} collides with something already drawn",
                    [sheet.sheet_id, label.id],
                )
            )
        boxes.append(box)

    anchors = [item.anchor for item in sheet.legend]
    anchors += [item.anchor for item in sheet.network_keys]
    for anchor in anchors:
        if not (
            legend_band.x_mm - TOLERANCE_MM <= anchor.x_mm <= legend_band.right_mm + TOLERANCE_MM
            and legend_band.y_mm - TOLERANCE_MM <= anchor.y_mm <= legend_band.bottom_mm + TOLERANCE_MM
        ):
            issues.append(
                _issue(
                    "LEGEND_OUTSIDE_ITS_BAND",
                    "a legend entry falls outside the legend band",
                    [sheet.sheet_id],
                )
            )

    denominations = {entry.name for entry in sheet.legend}
    for label in sheet.labels:
        if label.text in denominations:
            issues.append(
                _issue(
                    "LABEL_REPEATS_THE_LEGEND",
                    f"label {label.id} repeats a denomination the legend already "
                    f"carries: the legend says what, the tag says how much (D-052)",
                    [sheet.sheet_id, label.id],
                )
            )

    return issues


def validate_drawing_geometry(
    drawing: DrawingGeometry, frame: SheetFrame
) -> ValidationReport:
    """Tutti i controlli geometrici, piu' l'accoppiamento dei rimandi.

    L'accoppiamento si verifica sull'intero disegno e non su una tavola: un
    rimando senza gemello e' proprio il difetto che una verifica per tavola non
    puo' vedere.
    """
    issues: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        issues.extend(validate_sheet_geometry(sheet, frame))

    pairs: dict[str, list[str]] = {}
    for sheet in drawing.sheets:
        for reference in sheet.cross_references:
            pairs.setdefault(reference.pair_id, []).append(sheet.sheet_id)
    for pair_id, sheets in sorted(pairs.items()):
        if len(sheets) != 2:
            issues.append(
                _issue(
                    "UNPAIRED_CROSS_REFERENCE",
                    f"cross reference {pair_id} appears on {len(sheets)} sheets: "
                    f"a continuation needs exactly two ends",
                    [pair_id, *sorted(sheets)],
                )
            )

    unique = {(item.code, tuple(item.entity_ids), item.message): item for item in issues}
    ordered = sorted(
        unique.values(), key=lambda item: (item.code, item.entity_ids, item.message)
    )
    return ValidationReport(issues=ordered)
