"""L'interruttore magnetotermico differenziale sulla linea della pompa di calore (REL-018,
I-278): il grafo minimo.

Il PO, sulla tavola dell'elettrico uscita in sessione per una commessa: «è uscita senza le
protezioni elettriche (che interruttori ecc... ) non so mi sembra ci siamo persi qualcosa
rispetto al lavoro fatto sulla parte aria». La specifica tecnica di installazione PdC Shenling
Nove C Rev. 01 (§3.2–3.4) vuole nel quadro un magnetotermico differenziale bipolare, curva C,
Idn 30 mA, tipo B, ad alta velocita', e nessun sezionatore locale come regola.

Qui l'impianto e' il minimo che regge la validazione: una Shenling ThermaX R290 da 12 kW col
circolatore e i radiatori sul suo circuito, e il quadro che la alimenta **attraverso
l'interruttore** (`circuit-breaker-rcbo`, passante come il sezionatore): dal quadro (`out_1`)
all'interruttore (`a`), e dall'interruttore (`b`) alla macchina (`power`), una rete sola. Il
cavo e' del progettista — 3G6, 15 m — e sta sul tratto dall'interruttore alla macchina: il
tratto dal quadro all'interruttore e' dentro il quadro. **I dati dell'interruttore e quelli
elettrici della macchina non sono dati**: li scrive `completa` dal manuale e dalla specifica
(2P C32, Idn 30 mA tipo B; 230 V 1~, 30 A, 3G6), e lo dice.

    python3 docs/collaudi/REL-018/protezione/fai-il-grafo.py [uscita.json]
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
        "project_id": "protezione-della-linea",
        "client": "ND",
        "project_name": "Protezione della linea della pompa di calore",
        "commission_code": "ND",
        "revision": "00",
        "issue_date": "2026-11-04",
    },
    "plant_regime": "up_to_35_kw",
    "networks": [
        {"id": "primario", "name": "Circuito dei radiatori", "domain": "hydronic", "medium": "heating_water"},
        {"id": "el-pdc", "name": "Alimentazione pompa di calore", "domain": "control", "medium": "power_supply"},
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
        {"id": "qf-pdc", "definition_id": "circuit-breaker-rcbo", "tag": None, "properties": {}},
    ],
    "connections": [
        tratto("t1", "primario", ("pdc", "water_supply"), ("circ", "a")),
        tratto("t2", "primario", ("circ", "b"), ("radiatori", "in")),
        tratto("t3", "primario", ("radiatori", "out"), ("pdc", "water_return")),
        # La linea della pompa di calore: dal quadro all'interruttore, nel quadro, e
        # dall'interruttore alla macchina, col cavo del progettista.
        tratto("t4", "el-pdc", ("quadro", "out_1"), ("qf-pdc", "a")),
        {**tratto("t5", "el-pdc", ("qf-pdc", "b"), ("pdc", "power")), "sezione": "3G6", "lunghezza_m": 15},
    ],
    "assumptions": [
        {
            "id": "a1",
            "text": (
                "La linea della pompa di calore è protetta nel quadro da un interruttore "
                "magnetotermico differenziale (specifica Nove C §3.2); niente sezionatore "
                "locale, che la specifica non chiede come regola. Se lo vuoi, dimmelo e lo "
                "metto accanto alla macchina."
            ),
            "status": "proposed",
        },
        {
            "id": "a2",
            "text": (
                "Poli, curva, In, Idn e tipo dell'interruttore non dati: li scrive completa dal "
                "manuale Shenling (§7.4 p. 55) e dalla specifica Nove C (§3.3), con la "
                "regola «vale il maggiore»."
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
