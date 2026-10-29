"""Il grafo del collaudo T2 di REL-012 (centrale con pompa di calore, volano, bollitore,
due zone, elettrico e regolazione su tavola a parte), rifatto dopo le correzioni.

E' il grafo del collaudo (`../grafo.json`) con **due cambiamenti**:

1. il comando dei due circolatori di zona dal regolatore, che il collaudo aveva dovuto
   lasciare fuori (assunzione a13) perche' il circolatore aveva un attacco elettrico
   solo. Adesso ha anche `comando` (collaudo T2, §2.2.10): alimentato dal quadro di
   centrale, acceso dalle uscite 3 e 4 del regolatore. L'assunzione a13 dice che cosa e'
   stato disegnato;
2. quale **uscita del quadro** alimenta che cosa (sotto, `USCITE_DEL_QUADRO`): gli stessi
   cinque cavi sugli stessi cinque pezzi, su morsetti scelti guardando il simbolo.

    python3 docs/collaudi/REL-012/collaudo-t2/dopo/fai-il-grafo.py [uscita.json]
"""

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
uscita = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "grafo.json"
grafo = json.loads((QUI.parent / "grafo.json").read_text(encoding="utf-8"))

grafo["networks"] += [
    {"id": "cmd-circ-pannelli", "name": "Comando circolatore pannelli", "domain": "control", "medium": "power_supply"},
    {"id": "cmd-circ-radiatori", "name": "Comando circolatore radiatori", "domain": "control", "medium": "power_supply"},
]
grafo["connections"] += [
    {
        "id": "t37",
        "network_id": "cmd-circ-pannelli",
        "endpoint_a": {"component_id": "regolatore", "port_id": "out_3"},
        "endpoint_b": {"component_id": "circ-pannelli", "port_id": "comando"},
        "properties": {},
    },
    {
        "id": "t38",
        "network_id": "cmd-circ-radiatori",
        "endpoint_a": {"component_id": "regolatore", "port_id": "out_4"},
        "endpoint_b": {"component_id": "circ-radiatori", "port_id": "comando"},
        "properties": {},
    },
]
# **Le uscite del quadro, scelte sulla geometria** (rapporto §2.1.4). Il collaudo le
# aveva scelte al passo 1, prima di vedere dove stanno sul simbolo, e lo dice: con due
# cavi sui circolatori di zona la tavola dell'elettrico non si compone senza un
# andata-e-ritorno (B12, bloccante) o un fascio di incroci. Un'uscita del quadro e'
# un morsetto come un altro: si cambia quale, non che cosa alimenta.
USCITE_DEL_QUADRO = {
    "t25": "out_6",  # pompa di calore, dal fianco sinistro
    "t27": "out_3",  # circolatore pannelli, dal fianco destro
    "t28": "out_2",  # circolatore radiatori, da sopra
    "t29": "out_1",  # circolatore del ricircolo, da sopra
    "t30": "out_4",  # regolatore, da sotto
}
for tubazione in grafo["connections"]:
    if tubazione["id"] in USCITE_DEL_QUADRO:
        assert tubazione["endpoint_a"]["component_id"] == "quadro", tubazione["id"]
        tubazione["endpoint_a"]["port_id"] = USCITE_DEL_QUADRO[tubazione["id"]]

for assunzione in grafo["assumptions"]:
    if assunzione["id"] == "a13":
        assunzione["text"] = (
            "Il regolatore comanda i due circolatori di zona: ciascuno e' alimentato dal "
            "quadro di centrale e acceso da un'uscita del regolatore (pannelli dall'uscita 3, "
            "radiatori dall'uscita 4), due cavi sullo stesso circolatore. Se invece i "
            "circolatori si alimentano attraverso le uscite del regolatore, dimmelo e lo "
            "ridisegno cosi'."
        )

uscita.write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"scritto {uscita}")
