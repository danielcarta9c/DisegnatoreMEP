"""Dove si ferma la tavola 4, cella per cella (DRAW-013 §D)."""
from pathlib import Path
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3, ORDINARY_FRAMES
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids, compose_sheet, compose_drawing, ComposeJournal
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import lay_the_spine, carry_the_rest
from disegnatore_mep.layout.improve import improve_sheet
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.errors import LayoutError
ROOT = Path("/home/user/DisegnatoreMEP")
cat = ComponentRegistry.from_directory(ROOT/"examples/layout/catalog", symbols=SymbolRegistry.from_directory(ROOT/"assets/symbols"))
proj = load_project(ROOT/"docs/collaudi/DRAW-013/dopo/prova-4-ibrido-pdc-caldaia-completo.json")
for frame in ORDINARY_FRAMES:
    r = frame.drawing_rect_mm
    print(f"formato {frame.standard.sheet_width_mm:g} x {frame.standard.sheet_height_mm:g}: area x {r.x_mm}..{r.right_mm}, y {r.y_mm}..{r.bottom_mm}")
    inline = inline_component_ids(proj, cat)
    try:
        part = partition_project(proj, build_trunks(proj, inline))[0]
        first = place_sheet(proj, part, cat, frame, inline)
    except LayoutError as e:
        print("   la posa iniziale si ferma:", e); continue
    grid = GridSpace(origin=r, standard=frame.standard)
    print(f"   griglia: {grid.cols} colonne (0..{grid.cols}), {grid.rows} righe")
    spine = lay_the_spine(proj, part, cat, frame, first)
    seeded = carry_the_rest(proj, part, cat, first, spine, frame)
    try:
        improved = improve_sheet(proj, part, cat, frame, seeded, inline, spine)
    except LayoutError as e:
        print("   il ciclo si ferma:", e); improved = seeded
    for etichetta, posa in (("posa iniziale", first), ("seminata dal tronco", seeded), ("dopo il ciclo", improved)):
        fuori = [(s.component_id, s.origin.x_mm, s.origin.y_mm, s.right_mm, s.bottom_mm)
                 for s in posa if s.origin.x_mm < r.x_mm - 1e-6 or s.right_mm > r.right_mm + 1e-6
                 or s.origin.y_mm < r.y_mm - 1e-6 or s.bottom_mm > r.bottom_mm + 1e-6]
        print(f"   {etichetta}: {len(posa)} pezzi, {len(fuori)} fuori dall'area")
        for f in fuori:
            print(f"      {f[0]}: x {f[1]}..{f[3]}  y {f[2]}..{f[4]}")
    try:
        compose_sheet(proj, part, cat, frame, inline)
        print("   LA TAVOLA ESCE")
    except LayoutError as e:
        print("   la tavola NON esce:", e)
