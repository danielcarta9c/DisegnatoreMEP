"""Quali fluidi la tavola disegna **senza verso**: le due convenzioni in un posto solo.

Sull'idronico ogni linea ha un verso, e la tavola lo dice due volte: in legenda —
«acqua di riscaldamento — andata», «— ritorno», due colori — e sulla linea, con la
freccia di flusso. L'aria, il refrigerante, la condensa, l'elettrico e il bus non
sono fatti cosi', e il kit aria-aria del PO lo ha mostrato sulla tavola M.02
(`docs/input-pm/2026-10-29-kit-aria-aria/`, REL-012): comparivano «Aria di mandata
— andata» e frecce su cavi e bus.

Le due convenzioni sono **diverse** e stanno qui, una accanto all'altra, perche' si
cambiano insieme e da un posto solo:

- `FLUIDI_SENZA_VERSO` — **una riga sola in legenda** e lo stesso tratto comunque la
  linea si percorra (`legend.style_for`): l'aria di mandata e' quella, non ha un
  ritorno che si disegni d'altro colore;
- `FLUIDI_SENZA_FRECCIA` — **nessuna freccia di flusso** sulla linea
  (`flow.classify_trunks` da' alla tratta `FlowKind.NO_ARROW`, che SVG, DXF e il
  preflight leggono). Il refrigerante perche' la macchina e' reversibile: liquido e
  gas cambiano verso fra caldo e freddo, e una freccia sarebbe giusta in una stagione
  sola. L'elettrico e il bus perche' una freccia su un cavo non dice niente. **Le
  frecce restano** sull'aria e sulla condensa, che un verso ce l'hanno.

⚠ **E' una proposta della sessione** (REL-012, fase 1, 29 ottobre 2026): le frecce
sono una convenzione grafica del PO (D-213, punto 6), e il PO decide guardando la
tavola. Per cambiarla basta togliere o aggiungere un fluido qui.

Un fluido idronico non e' in nessuno dei due elenchi: le tavole idroniche non
cambiano.
"""

FLUIDI_SENZA_VERSO: frozenset[str] = frozenset(
    {
        "supply_air",
        "return_air",
        "refrigerant_liquid",
        "refrigerant_gas",
        "condensate",
        "power_supply",
        "interconnection",
        "control_bus",
    }
)
"""I fluidi con **una riga sola** in legenda e un tratto solo, in qualunque verso."""

FLUIDI_SENZA_FRECCIA: frozenset[str] = frozenset(
    {
        "refrigerant_liquid",
        "refrigerant_gas",
        "power_supply",
        "interconnection",
        "control_bus",
    }
)
"""I fluidi le cui linee **non portano la freccia di flusso** (proposta, D-213 punto 6)."""


def ha_un_verso(medium: str) -> bool:
    """Il fluido si disegna in andata e ritorno, con due righe di legenda."""
    return medium not in FLUIDI_SENZA_VERSO


def porta_la_freccia(medium: str) -> bool:
    """Le linee del fluido portano la freccia di flusso."""
    return medium not in FLUIDI_SENZA_FRECCIA


__all__ = ["FLUIDI_SENZA_FRECCIA", "FLUIDI_SENZA_VERSO", "ha_un_verso", "porta_la_freccia"]
