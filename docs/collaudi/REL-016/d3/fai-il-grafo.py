"""Il grafo della villetta del collaudo della 1.7.0, col collettore a sei vie (REL-016, D3).

    python3 docs/collaudi/REL-016/d3/fai-il-grafo.py

Parte dal grafo del collaudo (`../casi-del-collaudo/villetta-grafo.json`), dove l'impianto a
pavimento era un pannello rappresentativo con la scritta «impianto a pavimento (collettore a 6
vie)» perche' il catalogo non aveva un collettore a piu' di due vie, e lo sostituisce con quello
che il testo dice: il collettore con ritorno a sei vie (`zone-manifold-pair-6`) e i suoi sei
circuiti, un pannello per via. Il resto del grafo non cambia. Scrive `grafo.json` qui accanto.
"""

import json
from pathlib import Path

QUI = Path(__file__).resolve().parent
CASO = QUI.parent / "casi-del-collaudo" / "villetta-grafo.json"
VIE = 6


def estremo(componente: str, porta: str) -> dict[str, str]:
    return {"component_id": componente, "port_id": porta}


def tubazione(indice: str, rete: str, a: tuple[str, str], b: tuple[str, str]) -> dict:
    return {"id": indice, "network_id": rete, "endpoint_a": estremo(*a), "endpoint_b": estremo(*b), "properties": {}}


def main() -> None:
    grafo = json.loads(CASO.read_text(encoding="utf-8"))
    grafo["components"] = [c for c in grafo["components"] if c["id"] != "pannelli"]
    grafo["components"] += [
        {"id": "collettore", "definition_id": f"zone-manifold-pair-{VIE}", "tag": None, "properties": {}},
        *(
            {"id": f"pannello-{via}", "definition_id": "underfloor-panel", "tag": None, "properties": {}}
            for via in range(1, VIE + 1)
        ),
    ]
    # Le due tubazioni che andavano al pannello rappresentativo vanno al collettore; poi
    # una mandata e un ritorno per via.
    tubazioni = []
    for c in grafo["connections"]:
        if c["id"] == "c8":
            c = tubazione("c8", "impianto", ("circolatore", "b"), ("collettore", "in"))
        elif c["id"] == "c9":
            c = tubazione("c9", "impianto", ("collettore", "out"), ("volano", "secondary_in"))
        tubazioni.append(c)
    for via in range(1, VIE + 1):
        tubazioni += [
            tubazione(f"v{via}m", "impianto", ("collettore", f"out_{via}"), (f"pannello-{via}", "in")),
            tubazione(f"v{via}r", "impianto", (f"pannello-{via}", "out"), ("collettore", f"ret_{via}")),
        ]
    grafo["connections"] = tubazioni
    for ipotesi in grafo["assumptions"]:
        if ipotesi["id"] == "a2":
            ipotesi["text"] = (
                "Collettore a pavimento a 6 vie: collettore con ritorno a sei vie, un pannello per via "
                "(sei circuiti). I circuiti non hanno nome nel testo: nessuna scritta."
            )
    (QUI / "grafo.json").write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
