"""Perche' l'anello impediva la separazione (DRAW-010, criterio 2).

Fino a DRAW-009 `_Spine._relieve` allontanava due pezzi che si toccano
spostando il **sottoalbero** oltre la tratta che porta al piu' lontano dei due:
cosi' la retta resta retta. Su un circuito chiuso il tronco non e' un albero ma
un **anello**, e la camminata che cerca quel sottoalbero — `_beyond`, in ampiezza
dal vicino e senza fermarsi mai — torna indietro dall'altro capo dell'anello e
si porta dentro anche l'ancora. La guardia «l'ancora sta nel blocco» scartava
allora **tutte e due** le candidate, `_push_apart` tornava `False` alla prima
coppia e il ciclo di `_relieve` si fermava li: la posa usciva coi pezzi addosso,
e le coppie successive non venivano nemmeno guardate.

Questo strumento non lo racconta: lo misura. Per ogni impianto stampa

1. le coppie che si sovrappongono e quelle piu' vicine dello stacco ammesso
   nella posa che `lay_the_spine` + `carry_the_rest` consegnano;
2. **la mossa di prima**, coppia per coppia: le due candidate che generava, il
   sottoalbero che `_beyond` calcolava e perche' ciascuna si scartava. Il
   calcolo e' rifatto qui dentro, sulla posa di adesso, cosi' che la diagnosi
   resti verificabile anche dopo la correzione;
3. **la mossa di adesso**: i gruppi che i vincoli d'asse tengono insieme, le
   candidate ammesse con il loro blocco e il loro scorrimento, e quale vince.

    python docs/collaudi/DRAW-010/perche-l-anello-non-separava.py
    python docs/collaudi/DRAW-010/perche-l-anello-non-separava.py 2
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.layout.geometry import PlacedSymbol  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.place import (  # noqa: E402
    ROW_GAP_MM,
    hanging_children,
    place_sheet,
)
from disegnatore_mep.layout.spine import _Spine, carry_the_rest  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.model.project import ProjectModel  # noqa: E402
from disegnatore_mep.rules.apply import saturate  # noqa: E402
from disegnatore_mep.rules.registry import RuleRegistry  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

TOLERANCE_MM = 1e-6

IMPIANTI = {
    1: "prova-1-due-pdc-accumulo-combinato.json",
    2: "prova-2-pdc-deviatrice-acs.json",
    3: "prova-3-pdc-diretta-pavimento.json",
    4: "prova-4-ibrido-pdc-caldaia.json",
    5: "prova-5-cascata-tre-pdc.json",
}


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def completato(name: str) -> ProjectModel:
    registry = catalog()
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(registry)
    done, _, _ = saturate(load_project(PROVA / name), registry, rules)
    return done


def _overlap(one: PlacedSymbol, two: PlacedSymbol, gap_mm: float) -> bool:
    return (
        one.origin.x_mm < two.right_mm + gap_mm - TOLERANCE_MM
        and two.origin.x_mm - gap_mm < one.right_mm - TOLERANCE_MM
        and one.origin.y_mm < two.bottom_mm + gap_mm - TOLERANCE_MM
        and two.origin.y_mm - gap_mm < one.bottom_mm - TOLERANCE_MM
    )


class _Watched(_Spine):
    """Lo stesso costruttore, con un diario di cio' che `_relieve` prova.

    Il diario si scrive **prima** che la posa cambi, cosi' che ogni riga
    descriva la stessa posa in cui la coppia si e' trovata addosso.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.diary: list[str] = []

    # -- la mossa di prima, rifatta qui ---------------------------------------

    def _sottoalbero(self, edges, origin: str, first: str) -> list[str]:  # type: ignore[no-untyped-def]
        """`_beyond` com'era: in ampiezza dal vicino, senza fermarsi mai."""
        seen = {origin, first}
        frontier = [first]
        found = [first]
        while frontier:
            onward: list[str] = []
            for item in frontier:
                for _, _, other, _ in edges.get(item, ()):
                    if other in seen:
                        continue
                    seen.add(other)
                    found.append(other)
                    onward.append(other)
            frontier = onward
        return found

    def _mossa_di_prima(self, one: str, two: str) -> None:
        edges = self._edges()
        for victim, anchor in ((two, one), (one, two)):
            edge = next(
                (item for item in edges.get(victim, ()) if item[2] in self.laid), None
            )
            if edge is None:
                self.diary.append(
                    f"       candidata «sposta {victim}»: SCARTATA — nessuna "
                    f"autostrada esce da {victim}"
                )
                continue
            peer, peer_port = edge[2], edge[3]
            _, face = self.port_at(self.laid[peer], peer_port)
            block = self._sottoalbero(edges, peer, victim)
            self.diary.append(
                f"       candidata «sposta {victim}»: allunga la campata "
                f"{peer}.{peer_port} -> {victim}, verso {face.value}"
            )
            self.diary.append(
                f"         sottoalbero di _beyond ({len(block)}): {', '.join(block)}"
            )
            if anchor in block:
                self.diary.append(
                    f"         SCARTATA — l'ancora {anchor} sta nel "
                    f"sottoalbero: l'anello lo riporta dentro, e spostarlo "
                    f"porta dietro tutti e due senza separarli"
                )
            else:
                self.diary.append("         ammessa")

    # -- la mossa di adesso ---------------------------------------------------

    def _push_apart(self, one: str, two: str) -> bool:  # type: ignore[override]
        self.diary.append(f"   coppia addosso: {one} <-> {two}")
        self.diary.append("     la mossa di prima (DRAW-009):")
        self._mossa_di_prima(one, two)
        self.diary.append("     la mossa di adesso (DRAW-010):")
        for axis in (0, 1):
            nome = "x" if axis == 0 else "y"
            for victim, anchor in ((one, two), (two, one)):
                for sign in (1, -1):
                    verso = "avanti" if sign > 0 else "indietro"
                    block = self._follow(axis, sign, victim)
                    testa = f"       {nome} {verso:9s} «sposta {victim}»"
                    if anchor in block:
                        self.diary.append(
                            f"{testa}: SCARTATA — l'ancora {anchor} e' nel "
                            f"blocco ({len(block)} pezzi)"
                        )
                        continue
                    room = self._clearance(victim, anchor, axis, sign)
                    if room <= TOLERANCE_MM:
                        self.diary.append(
                            f"{testa}: SCARTATA — in quel verso i due non si "
                            f"separano"
                        )
                        continue
                    if room > 40 * self.step:
                        self.diary.append(
                            f"{testa}: SCARTATA — {room:g} mm oltre il tetto "
                            f"della compattazione"
                        )
                        continue
                    self.diary.append(
                        f"{testa}: AMMESSA — scorre {room:g} mm, blocco "
                        f"({len(block)}): {', '.join(block)}"
                    )
        prima = {item: self.laid[item].origin for item in self.participants}
        moved = super()._push_apart(one, two)
        if not moved:
            self.diary.append("     esito: NESSUNA MOSSA, la coppia resta addosso")
            return False
        scarti = sorted(
            (
                item,
                round(self.laid[item].origin.x_mm - prima[item].x_mm, 1),
                round(self.laid[item].origin.y_mm - prima[item].y_mm, 1),
            )
            for item in self.participants
            if self.laid[item].origin != prima[item]
        )
        detto = ", ".join(f"{item} ({dx:+g}, {dy:+g})" for item, dx, dy in scarti)
        self.diary.append(f"     esito: separati — {detto}")
        return True


def _posa(name: str, watched: bool):  # type: ignore[no-untyped-def]
    model = completato(name)
    registry = catalog()
    inline = inline_component_ids(model, registry)
    partition = partition_project(model, build_trunks(model, inline))[0]
    first = place_sheet(model, partition, registry, NOVE_C_A3, inline)
    builder = (_Watched if watched else _Spine)(
        model, partition, registry, NOVE_C_A3, first
    )
    layout = builder.build()
    seeded = carry_the_rest(model, partition, registry, first, layout, NOVE_C_A3)
    return builder, layout, seeded


def _units(name: str) -> dict[str, str]:
    """Chi appartiene alla stessa figura: dentro una figura basta non
    sovrapporsi, fra figure diverse vale lo stacco (D-062). E' la stessa
    lettura di `Improver.leader_of`."""
    model = completato(name)
    registry = catalog()
    inline = inline_component_ids(model, registry)
    partition = partition_project(model, build_trunks(model, inline))[0]
    known = frozenset(item.id for item in model.components)
    children = hanging_children(model, partition, registry, known)
    parent = {child: father for father, items in children.items() for child, _ in items}
    leader: dict[str, str] = {}
    for item in known:
        head = item
        seen = {head}
        while head in parent and parent[head] not in seen:
            head = parent[head]
            seen.add(head)
        leader[item] = head
    return leader


def _gruppi(builder: _Spine) -> None:
    for axis in (0, 1):
        nome = "x" if axis == 0 else "y"
        demands = builder.axes[axis]
        groups: dict[str, list[str]] = {}
        for item in builder.participants:
            groups.setdefault(demands.leader[item], []).append(item)
        print(f"   i gruppi dell'asse {nome} (una retta li tiene insieme):")
        for name, members in sorted(groups.items()):
            print(f"     {name}: {', '.join(members)}")


def _report(number: int) -> None:
    name = IMPIANTI[number]
    print(f"== impianto {number} — {name}")
    builder, _, seeded = _posa(name, watched=True)
    leader = _units(name)
    where = {item.component_id: item for item in seeded}
    ids = sorted(where)
    sovrapposte = []
    vicine = []
    for index, one in enumerate(ids):
        for two in ids[index + 1 :]:
            gap = 0.0 if leader.get(one) == leader.get(two) else ROW_GAP_MM
            if _overlap(where[one], where[two], 0.0):
                sovrapposte.append((one, two))
            if _overlap(where[one], where[two], gap):
                vicine.append((one, two))
    print(f"   coppie che si sovrappongono davvero          : {len(sovrapposte)}")
    for one, two in sovrapposte:
        print(f"       {one} <-> {two}")
    print(
        f"   coppie piu' vicine dello stacco ammesso      : {len(vicine)}"
        "   (comprese le sovrapposte: e' la regola di is_valid)"
    )
    for one, two in vicine:
        print(f"       {one} <-> {two}")
    _gruppi(builder)
    print("   il diario di _relieve:")
    if not builder.diary:  # type: ignore[attr-defined]
        print("     nessuna coppia addosso fra i partecipanti al tronco")
    for line in builder.diary:  # type: ignore[attr-defined]
        print(line)
    print()


def main(argv: list[str]) -> int:
    wanted = [int(item) for item in argv] or sorted(IMPIANTI)
    for number in wanted:
        _report(number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
