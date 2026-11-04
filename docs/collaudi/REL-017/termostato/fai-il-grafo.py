"""Il termostato ambiente a contatto sulla linea del circolatore (I-269): il grafo minimo.

Il PO, da una commessa reale (villetta, PdC Shenling 12 kW, circolatore secondario verso il
pavimento radiante): la pompa di calore regola da se', e il circolatore del secondario e'
alimentato dal quadro **attraverso il contatto del termostato ambiente** — il termostato in
chiamata accende il circolatore. Il catalogo aveva solo il termostato di zona su bus
(`room-thermostat`, un attacco `control_bus`): collegato al circolatore la validazione lo
fermava (`PORT_MEDIUM_MISMATCH`), e il ripiego con una `scritta` sulla linea del quadro
lasciava una linea che «attraversa un pezzo che non c'e'».

Qui l'impianto e' il minimo che regge la validazione: una pompa di calore, il circolatore e i
radiatori sul suo circuito, il quadro che alimenta la macchina e, **attraverso il termostato
ambiente a contatto** (`room-thermostat-contact`, passante come il sezionatore), il
circolatore. Una rete sola per la linea del circolatore; nessun relè (D-228 vale per il
circolatore comandato da un'uscita della pompa di calore). Sezione e lunghezza dei cavi non
sono date: la distinta li chiede.

    python3 docs/collaudi/REL-017/termostato/fai-il-grafo.py [uscita.json]
"""

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
uscita = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "grafo.json"


def tratto(ident: str, rete: str, a: tuple[str, str], b: tuple[str, str]) -> dict[str, object]:
    return {
        "id": ident,
        "network_id": rete,
        "endpoint_a": {"component_id": a[0], "port_id": a[1]},
        "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        "properties": {},
    }


grafo = {
    "schema_version": "1.1.0",
    "metadata": {
        "project_id": "termostato-a-contatto",
        "client": "ND",
        "project_name": "Circolatore acceso dal termostato ambiente a contatto",
        "commission_code": "ND",
        "revision": "00",
        "issue_date": "2026-11-04",
    },
    "plant_regime": "up_to_35_kw",
    "networks": [
        {"id": "primario", "name": "Circuito dei radiatori", "domain": "hydronic", "medium": "heating_water"},
        {"id": "el-pdc", "name": "Alimentazione pompa di calore", "domain": "control", "medium": "power_supply"},
        {
            "id": "el-circ",
            "name": "Alimentazione circolatore dal quadro, attraverso il termostato",
            "domain": "control",
            "medium": "power_supply",
        },
    ],
    "components": [
        {
            "id": "pdc",
            "definition_id": "heat-pump-air-water",
            "tag": None,
            "properties": {"power_kw": 12, "marca": "Shenling", "modello": "ThermaX R290"},
        },
        {"id": "circ", "definition_id": "pump-circulator", "tag": None, "properties": {}},
        {"id": "radiatori", "definition_id": "radiator", "tag": None, "properties": {}},
        {"id": "quadro", "definition_id": "electrical-panel", "tag": None, "properties": {"etichetta": "quadro di centrale"}},
        {
            "id": "termostato",
            "definition_id": "room-thermostat-contact",
            "tag": None,
            "properties": {"etichetta": "soggiorno", "contatto": "5(2) A 250 V"},
        },
    ],
    "connections": [
        tratto("t1", "primario", ("pdc", "water_supply"), ("circ", "a")),
        tratto("t2", "primario", ("circ", "b"), ("radiatori", "in")),
        tratto("t3", "primario", ("radiatori", "out"), ("pdc", "water_return")),
        tratto("t4", "el-pdc", ("quadro", "out_1"), ("pdc", "power")),
        # La linea del circolatore: dal quadro al termostato, e dal termostato al circolatore.
        tratto("t5", "el-circ", ("quadro", "out_3"), ("termostato", "a")),
        tratto("t6", "el-circ", ("termostato", "b"), ("circ", "power")),
    ],
    "assumptions": [
        {
            "id": "a1",
            "text": (
                "Il circolatore è alimentato dal quadro attraverso il contatto del termostato "
                "ambiente, senza relè: la pompa di calore regola da sé e non comanda il "
                "circolatore. Se la portata del contatto non basta per il circolatore, dimmelo e "
                "metto un relè d'appoggio comandato dal termostato."
            ),
            "status": "proposed",
        },
        {
            "id": "a2",
            "text": (
                "Sezione e lunghezza dei cavi non date: la linea del circolatore va dal quadro "
                "al termostato e torna al circolatore, e senza i due tratti la distinta la "
                "lascia DA DEFINIRE."
            ),
            "status": "proposed",
        },
    ],
    "rule_applications": [],
    "subsystems": [],
    "sheets": [],
}

uscita.write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"scritto {uscita}")
