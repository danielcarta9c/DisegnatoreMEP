"""Perche' la regola di §2.5 e la prova di DRAW-007 non possono stare insieme.

`Improver.is_valid` rifiutava ogni candidata che lasciasse due pezzi addosso.
DRAW-009 §2.5 la rende **monotona**: una mossa risponde delle sovrapposizioni
che **crea**, non di quelle che trova — senza di che, sulla tavola 2, dove la
fase del tronco consegna nove coppie sovrapposte, *ogni* candidata e' non
valida e il ciclo resta inchiodato.

Una prova di DRAW-007 —
`test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore` — chiede
il contrario: che una mossa che porta un accumulo **piu' dentro** l'altro sia
rifiutata. Le due cose sono in conflitto, e questo strumento lo misura invece
di raccontarlo.

    python docs/collaudi/DRAW-009/le-due-sovrapposizioni.py

Stampa, in quest'ordine:

1. **la posa da cui la prova di DRAW-007 parte**: i due accumuli sono gia'
   25 x 32,5 mm uno dentro l'altro — la compenetrazione stampata conta anche i
   10 mm di stacco fra figure — cioe' la posa di partenza e' gia' invalida. Cio'
   che la prova chiama «violare la distanza minima» e' quindi «non separare una
   sovrapposizione trovata», che e' esattamente cio' che §2.5 dice che nessuna
   mossa e' tenuta a fare;
2. **che cosa di quella prova regge lo stesso**: delle sue quattro asserzioni
   soltanto la prima cade. Le altre tre — il ciclo non peggiora mai la tavola,
   finisce senza violazioni, e ogni mossa accettata batte strettamente la
   precedente — sono l'invariante da cui la prova prende il nome, e valgono;
3. **il banco della traslazione di blocco**, con la migliore candidata di ogni
   specie, due volte: con la regola consegnata, e con la regola piu' stretta
   («ne' crea ne' approfondisce») che farebbe passare la prova di DRAW-007. Con
   quella piu' stretta la mossa che il pacchetto aggiunge **sparisce**: il
   blocco scende di 7,5 mm perche' i due accumuli erano gia' sovrapposti, e
   quella discesa e' cio' che porta le pieghe da 64 a 32 e gli incroci da 16 a
   zero.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from layout.test_assi_dorsali_tee import (  # noqa: E402
    STEP_MM,
    _improver,
    _plant,
    _posa,
)
from layout.test_assi_dorsali_tee import catalog as tee_catalog  # noqa: E402
from layout.test_traslazione_di_blocco import _banco  # noqa: E402

from disegnatore_mep.layout.geometry import PlacedSymbol, Point  # noqa: E402
from disegnatore_mep.layout.improve import (  # noqa: E402
    ROW_GAP_MM,
    Improver,
    Move,
    _too_close,
)

TOLERANCE_MM = 1e-9


def _penetration(
    one: PlacedSymbol, two: PlacedSymbol, gap_mm: float
) -> tuple[float, float]:
    """Di quanto i due riquadri si compenetrano, sui due assi, con lo stacco."""
    half = gap_mm / 2
    x_mm = (min(one.right_mm, two.right_mm) + half) - (
        max(one.origin.x_mm, two.origin.x_mm) - half
    )
    y_mm = (min(one.bottom_mm, two.bottom_mm) + half) - (
        max(one.origin.y_mm, two.origin.y_mm) - half
    )
    return max(x_mm, 0.0), max(y_mm, 0.0)


def _deepens(improver: Improver, move: Move) -> bool:
    """Vero se la mossa porta due pezzi gia' addosso **piu' dentro**."""
    after = dict(improver.best)
    after.update(move)
    units = {item: improver.leader_of(item) for item in improver.order}
    for item, placed in move.items():
        for other in improver.order:
            if other == item:
                continue
            gap = 0.0 if units[other] == units[item] else ROW_GAP_MM
            if not _too_close(placed, after[other], gap):
                continue
            was = _penetration(improver.best[item], improver.best[other], gap)
            now = _penetration(placed, after[other], gap)
            if now[0] > was[0] + TOLERANCE_MM or now[1] > was[1] + TOLERANCE_MM:
                return True
    return False


def _draw_007() -> None:
    project = _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("serbatoio", "buffer-two-port"),
            ("riserva", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "serbatoio", "a"),
            ("c2", "serbatoio", "b", "terminale", "in"),
            ("c3", "terminale", "out", "macchina", "water_return"),
            ("c4", "riserva", "b", "terminale", "in"),
        ],
        subsystems=[
            ("generazione", ["macchina"]),
            ("accumulo", ["serbatoio", "riserva"]),
            ("utenza", ["terminale"]),
        ],
    )
    placed = _posa(project)
    where = {item.component_id: item for item in placed}
    machine, tank = where["macchina"], where["serbatoio"]
    supply_y = (
        machine.origin.y_mm
        + tee_catalog()
        .resolve("heat-pump-air-water")
        .symbol.manifest.port("water_supply")
        .y_mm
    )
    inlet_y = tee_catalog().resolve("buffer-two-port").symbol.manifest.port("a").y_mm
    aligned = supply_y - inlet_y
    blocked = [
        item.model_copy(
            update={"origin": Point(x_mm=tank.origin.x_mm, y_mm=aligned - STEP_MM)}
        )
        if item.component_id == "riserva"
        else item
        for item in placed
    ]
    improver = _improver(project, blocked)
    one, two = improver.best["serbatoio"], improver.best["riserva"]
    print("1. la posa da cui la prova di DRAW-007 parte")
    for item in (one, two):
        print(
            f"   {item.component_id:10s} y={item.origin.y_mm:6.1f} .. "
            f"{item.bottom_mm:6.1f}  (x={item.origin.x_mm:6.1f}, larghezza {item.width_mm:g})"
        )
    print(
        f"   gia' addosso: {_too_close(one, two, ROW_GAP_MM)}  "
        f"compenetrazione = {_penetration(one, two, ROW_GAP_MM)} mm"
    )
    alone: Move = {
        "serbatoio": one.model_copy(
            update={"origin": Point(x_mm=one.origin.x_mm, y_mm=aligned)}
        )
    }
    print(
        f"   la mossa che la prova vuole rifiutata porta la compenetrazione a "
        f"{_penetration(alone['serbatoio'], two, ROW_GAP_MM)} mm"
    )
    print(f"   is_valid con la regola consegnata: {improver.is_valid(alone)}")
    print(f"   la stessa mossa approfondisce: {_deepens(improver, alone)}")
    print()

    print("2. che cosa di quella prova regge lo stesso")
    before = improver.measure(improver.best)
    assert before is not None
    final = {item.component_id: item for item in improver.run()}
    after = improver.measure(final)
    assert after is not None
    accepted = [entry for entry in improver.journal if entry.accepted]
    keys = [before.cost.key(), *(entry.cost for entry in accepted if entry.cost)]
    print(
        f"   A. la mossa che si allinea da sola e' rifiutata .... "
        f"{not improver.is_valid(alone)}   <- l'unica che cade"
    )
    print(
        f"   B. il ciclo non peggiora mai la tavola ............. "
        f"{not before.cost.beats(after.cost)}   "
        f"({before.cost.key()[:7]} -> {after.cost.key()[:7]})"
    )
    print(
        f"   C. la tavola finisce senza violazioni ............. "
        f"{after.cost.violations == 0}   ({after.cost.violations})"
    )
    print(
        f"   D. ogni mossa accettata batte la precedente ....... "
        f"{all(later < earlier for earlier, later in zip(keys, keys[1:], strict=False))}   "
        f"({len(accepted)} accettate)"
    )
    print()


def _banco_due_regole() -> None:
    improver, block = _banco()
    base = improver.measure(improver.best)
    assert base is not None
    print("3. il banco della traslazione di blocco")
    print(f"   blocco: {', '.join(block)}")
    print(f"   posa di partenza: {base.cost.key()}")
    units = {item: improver.leader_of(item) for item in improver.order}
    addosso = [
        (one, two, _penetration(improver.best[one], improver.best[two], gap))
        for index, one in enumerate(improver.order)
        for two in improver.order[index + 1 :]
        for gap in (0.0 if units[one] == units[two] else ROW_GAP_MM,)
        if _too_close(improver.best[one], improver.best[two], gap)
    ]
    print("   coppie gia' sovrapposte nella posa che la fase del tronco consegna:")
    for one, two, pen in addosso:
        print(f"     {one} <-> {two}  compenetrazione = {pen} mm")
    for strict in (False, True):
        best: dict[str, tuple[tuple[object, ...], Move]] = {}
        for kind, move in improver.candidates_by_kind(block[0]):
            if not improver.is_valid(move):
                continue
            if strict and _deepens(improver, move):
                continue
            found = improver.measure({**improver.best, **move})
            if found is None:
                continue
            key = found.cost.key()
            if kind not in best or key < best[kind][0]:
                best[kind] = (key, move)
        titolo = (
            "con la regola piu' stretta (ne' crea ne' approfondisce)"
            if strict
            else "con la regola consegnata (non crea)"
        )
        print(f"   {titolo}:")
        for kind, (key, move) in sorted(best.items(), key=lambda item: item[1][0]):
            deltas = sorted(
                {
                    (
                        round(placed.origin.x_mm - improver.best[item].origin.x_mm, 1),
                        round(placed.origin.y_mm - improver.best[item].origin.y_mm, 1),
                    )
                    for item, placed in move.items()
                }
            )
            batte = "batte la partenza" if key < base.cost.key() else "non la batte"
            print(f"     {kind:16s} {key}  scarti={deltas}  {batte}")


def main() -> int:
    _draw_007()
    _banco_due_regole()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
