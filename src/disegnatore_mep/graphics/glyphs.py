"""I glifi che il renderer disegna da solo: la freccia di verso di una porta.

Un corpo SVG e' un segno fermo. Il verso dell'acqua non lo e': lo stesso
confine di rete e' uscente sull'acquedotto ed entrante sulle utenze, e la sua
freccia deve puntare nel verso **locale** dell'acqua (DRAW-005, I-032). Il
manifesto dichiara dove la freccia sta e quanto e' lunga; qui la si traccia,
puntata secondo il verso della porta.
"""

from disegnatore_mep.model.types import PortFlow

from .symbol import FlowGlyph, PortFace

_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}
"""Il verso uscente di ciascuna faccia, con y verso il basso come in SVG."""


def flow_glyph_path(glyph: FlowGlyph, face: PortFace, flow: str | None) -> str:
    """La freccia di una porta, in coordinate locali del riquadro gia' ruotato.

    Punta **verso la porta** se l'acqua esce dal simbolo (`out`, o verso
    ignoto: cosi' la pubblica la libreria), **verso l'interno** se vi entra
    (`in`). Una porta senza verso — bidirezionale — non porta freccia: una
    freccia che mentisse sarebbe peggio di nessuna freccia.
    """
    if flow == PortFlow.BIDIRECTIONAL.value:
        return ""
    outward = _DIRECTION[face]
    sign = -1.0 if flow == PortFlow.IN.value else 1.0
    along = (outward[0] * sign, outward[1] * sign)
    across = (-along[1], along[0])
    half = glyph.length_mm / 2
    tip = (glyph.x_mm + along[0] * half, glyph.y_mm + along[1] * half)
    base = (glyph.x_mm - along[0] * half, glyph.y_mm - along[1] * half)
    left = (base[0] + across[0] * glyph.half_width_mm, base[1] + across[1] * glyph.half_width_mm)
    right = (base[0] - across[0] * glyph.half_width_mm, base[1] - across[1] * glyph.half_width_mm)
    return (
        f'<path class="flow-glyph" data-port="{glyph.port}" '
        f'd="M{tip[0]:g} {tip[1]:g} L{left[0]:g} {left[1]:g} L{right[0]:g} {right[1]:g} Z" '
        f'fill="black" stroke="none"/>'
    )


__all__ = ["flow_glyph_path"]
