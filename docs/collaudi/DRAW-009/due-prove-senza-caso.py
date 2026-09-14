"""Due prove che restano rosse perche' il grafo nuovo ha tolto loro il caso.

Nessuna delle due e' stata toccata, ammorbidita o convertita: restano rosse, e
questo strumento misura **perche'**, cosi' che il PM giudichi sul numero.

    python docs/collaudi/DRAW-009/due-prove-senza-caso.py

1. `test_la_valvola_che_isola_oltre_un_raccordo_passante_si_stringe_al_raccordo`
   (DRAW-006). Cerca, sull'impianto a due macchine, una tratta che finisca su un
   **raccordo passante** — un raccordo che prosegue verso un pezzo servito — con
   una **valvola di chiusura** come ultimo accessorio in linea da quella parte, e
   non nella catena di una macchina. La prova apre con una guardia: «nessuna
   valvola oltre un raccordo passante: la prova non direbbe nulla». Da §A.1 il
   ponte del riempimento non deriva piu' dalla linea fredda, la scomposizione in
   tratte del ritorno cambia, e su quella fixture il caso non c'e' piu'. La
   guardia fa esattamente il proprio mestiere: grida invece di passare a vuoto.
   Qui sotto, riga per riga, quale delle tre condizioni cade.

2. `test_nessuna_freccia_sui_rami_statici_e_la_freccia_giusta_sugli_altri`.
   Pretende che **ogni** tratta non statica porti almeno una freccia; il
   renderer — e la prova stessa, che ne rifa' la regola — una freccia la mette
   solo su un tratto lungo almeno `2 x ARROW_LENGTH_MM`, cioe' 4,0 mm. Con
   l'ingresso del riempimento posato al proprio minimo la tavola ha adesso una
   tratta ordinaria lunga **un passo**, e le due regole si contraddicono su di
   lei. Non e' una taratura: e' una domanda di rappresentazione — una tratta
   lunga un passo porta una freccia piu' corta, o non ne porta? — e la risposta
   non nasce dal codice.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from layout.test_consegna_e_verifica import (  # noqa: E402
    CLOSING_FUNCTIONS,
    _continues_to_a_serviced_piece,
    due_macchine_con_accumulo_combinato,
)
from layout.test_consegna_e_verifica import catalog as consegna_catalog  # noqa: E402
from layout.test_consegna_e_verifica import rules as consegna_rules  # noqa: E402
from layout.test_rami_di_servizio import CASI, CASI_IDS, _drawing  # noqa: E402

from disegnatore_mep.graphics.sheet import ARROW_LENGTH_MM  # noqa: E402
from disegnatore_mep.layout.chains import machine_chains  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.layout.geometry import FlowKind  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.rules.apply import saturate  # noqa: E402


def _valvola_oltre_un_raccordo() -> None:
    project, _, _ = saturate(
        due_macchine_con_accumulo_combinato(), consegna_catalog(), consegna_rules()
    )
    registry = consegna_catalog()
    definitions = {item.id: item.definition_id for item in project.components}
    inline = inline_component_ids(project, registry)
    trunks = build_trunks(project, inline)
    print("1. la valvola oltre un raccordo passante: le tre condizioni, tratta per tratta")
    print(
        f"   {'tratta':40s} {'capo':40s} {'prosegue':9s} {'ultimo in linea':46s} chiude  in catena"
    )
    found = 0
    for trunk in trunks:
        if not trunk.inline_component_ids:
            continue
        head, tail = machine_chains(project, registry, trunk)
        chained = set(head) | set(tail)
        for near in (trunk.end, trunk.start):
            if not registry.get(definitions[near.component_id]).is_a_fitting:
                continue
            goes_on = _continues_to_a_serviced_piece(project, registry, near, trunks)
            last = (
                trunk.inline_component_ids[-1]
                if near == trunk.end
                else trunk.inline_component_ids[0]
            )
            closes = bool(
                CLOSING_FUNCTIONS & set(registry.get(definitions[last]).functions)
            )
            print(
                f"   {'/'.join(trunk.connection_ids)[:40]:40s} {near.component_id[:40]:40s} "
                f"{str(goes_on):9s} {last[:46]:46s} {str(closes):6s}  {last in chained}"
            )
            if goes_on and closes and last not in chained:
                found += 1
    print(f"   casi che la prova misurerebbe: {found}")
    print()


def _tratte_troppo_corte_per_una_freccia() -> None:
    print("2. le tratte non statiche piu' corte di una freccia")
    print(f"   una freccia chiede almeno 2 x ARROW_LENGTH_MM = {2 * ARROW_LENGTH_MM:g} mm")
    for index, name in enumerate(CASI_IDS):
        sheet = _drawing(index).sheets[0]
        print(f"   {name}:")
        for route in sheet.routes:
            if route.flow_kind is FlowKind.STATIC:
                continue
            longest = 0.0
            for segment in route.segments:
                for before, after in zip(segment, segment[1:], strict=False):
                    longest = max(
                        longest,
                        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm),
                    )
            if longest >= 2 * ARROW_LENGTH_MM:
                continue
            print(
                f"     {'/'.join(route.connection_ids):52s} {route.flow_kind.value:9s} "
                f"tratto piu' lungo = {longest:g} mm"
            )
    _ = CASI
    print()


def main() -> int:
    _valvola_oltre_un_raccordo()
    _tratte_troppo_corte_per_una_freccia()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
