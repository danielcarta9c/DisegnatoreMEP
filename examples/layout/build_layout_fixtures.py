"""Genera il caso di accettazione D-011: PDC, ACS, volano a quattro attacchi, due zone.

E' il primo impianto che il motore di layout deve disegnare in modo
riconoscibile da un termotecnico. Non e' una struttura speciale nel codice:
e' un file di dati, come qualunque altro progetto.

Il catalogo qui accanto porta la sola **semantica** delle porte — dominio,
fluido, verso, obbligatorieta', molteplicita' — mentre la geometria vive nei
manifesti di `assets/symbols/` e le due si uniscono per identificativo di
porta (D-043).

Nessun accessorio che l'ingegnere non abbia nominato: finche' il motore delle
regole non esiste, la skill disegna esattamente cio' che il modello contiene
(D-040). Il filtro e la valvola di intercettazione ci sono perche' fanno parte
dell'impianto descritto, non perche' qualcosa li abbia aggiunti.
"""

import json
from pathlib import Path
from typing import Any

from disegnatore_mep.model.project import SCHEMA_VERSION

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "examples" / "layout"
CATALOG = ROOT / "catalog"

VERSION = "1.0.0"
SOURCE = "CONV-FOUNDATION"

MAINTAINABLE = "maintainable"
FOULS_CIRCUIT = "fouls_circuit"
NEEDS_DEBRIS_PROTECTION = "needs_debris_protection"
PRODUCES_AIR = "produces_air"
NEEDS_OVERPRESSURE_PROTECTION = "needs_overpressure_protection"
HOLDS_ITS_OWN_VOLUME = "holds_its_own_volume"
SHUTOFF_ORDINARY = "shutoff_ordinary"
INLINE = "attachment_inline"

HEATING = "heating_water"
DHW = "domestic_hot_water"
# Il fluido dell'acqua fredda sanitaria si chiama "cold_water" ovunque: nelle
# altre voci del catalogo, nelle condizioni delle regole e nelle reti dei
# progetti d'esempio. Qui era rimasto un nome diverso da quando il generatore
# non veniva piu' rieseguito, e rigenerare il catalogo cambiava in silenzio il
# fluido del bollitore.
COLD = "cold_water"


def service_port(port_id: str, serves: str, medium: str = HEATING) -> dict[str, Any]:
    """Un attacco di servizio: esiste per una funzione precisa (D-101).

    Non e' del flusso principale e non e' obbligatorio che qualcuno lo usi: un
    volano ha lo scarico anche in un impianto in cui nessuno lo collega. Il
    verso e' neutro, perche' uno stacco non e' un percorso.

    Cosa dichiara ciascuna macchina viene dai cataloghi dei costruttori
    (SRC-017, SRC-018), non dalla nostra memoria.
    """
    return {
        "id": port_id,
        "domain": "hydronic",
        "medium": medium,
        "flow": "bidirectional",
        "required": False,
        "stub": True,
        "serves": serves,
    }


def branch_port(medium: str = HEATING) -> dict[str, Any]:
    """Il braccio di un raccordo: uno stacco senza una funzione dichiarata.

    Cosa ci pendera' lo decide l'impianto, non il pezzo — ma chi cammina lungo
    la tubazione deve sapere che di li' la corsa non prosegue."""
    return {
        "id": "branch",
        "domain": "hydronic",
        "medium": medium,
        "flow": "bidirectional",
        "required": False,
        "stub": True,
    }


def hydronic_port(
    port_id: str,
    flow: str,
    medium: str = HEATING,
    required: bool = True,
) -> dict[str, Any]:
    """Un attacco, e porta una tubazione sola (D-100).

    Il massimo per attacco non si dichiara piu': non era configurabile per
    davvero, e i due soli posti in cui diceva «due» erano i due punti in cui il
    modello stava rappresentando un raccordo che non aveva.
    """
    return {
        "id": port_id,
        "domain": "hydronic",
        "medium": medium,
        "flow": flow,
        "required": required,
    }


def definition(
    definition_id: str,
    name: str,
    functions: list[str],
    traits: list[str],
    ports: list[dict[str, Any]],
    symbol_id: str | None = None,
    stored_medium: str | None = None,
) -> dict[str, Any]:
    """Una voce di catalogo. `traits` non ha default **per scelta**: un
    componente che non dichiara come si isola non deve poter nascere da qui piu'
    di quanto possa nascere da un file scritto a mano (P1).

    `stored_medium` e' obbligatorio per chi dichiara di tenere un volume
    proprio: dire quale acqua tiene in serbo e' cio' che distingue lo scarico
    del serbatoio dallo scarico del circuito che lo attraversa. Il generatore lo
    deve scrivere, altrimenti rigenerare il catalogo lo cancella e la catena non
    carica piu' — ed e' successo davvero.
    """
    entry: dict[str, Any] = {
        "id": definition_id,
        "version": VERSION,
        "name": name,
        "functions": functions,
        "traits": traits,
    }
    if stored_medium is not None:
        entry["stored_medium"] = stored_medium
    entry.update(
        {
            "symbol_id": symbol_id or definition_id,
            "composite": False,
            "ports": ports,
            "sources": [SOURCE],
        }
    )
    return entry


DEFINITIONS: list[dict[str, Any]] = [
    definition(
        "heat-pump-air-water",
        "Pompa di calore aria-acqua",
        ["heat_generation"],
        [
            MAINTAINABLE,
            NEEDS_DEBRIS_PROTECTION,
            PRODUCES_AIR,
            NEEDS_OVERPRESSURE_PROTECTION,
            SHUTOFF_ORDINARY,
            INLINE,
        ],
        [
            hydronic_port("water_supply", "out"),
            hydronic_port("water_return", "in"),
        ],
    ),
    definition(
        # **Confluenza.** Il ritorno della macchina raccoglie sia il circuito del
        # volano sia quello del serpentino: le due tubazioni si uniscono qui
        # invece che sullo stesso bocchello (D-100). Tutti e tre gli attacchi
        # sono sul percorso. Non si smonta in esercizio: non chiede valvole.
        "tee-junction",
        "Raccordo a T",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in"),
            hydronic_port("c", "in"),
            hydronic_port("b", "out"),
        ],
    ),
    definition(
        "tee-junction-dhw",
        "Raccordo a T sanitario",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", DHW),
            hydronic_port("c", "in", DHW),
            hydronic_port("b", "out", DHW),
        ],
        symbol_id="tee-junction",
    ),
    definition(
        "tee-junction-cold",
        "Raccordo a T sull'acqua fredda",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", COLD),
            hydronic_port("c", "in", COLD),
            hydronic_port("b", "out", COLD),
        ],
        symbol_id="tee-junction",
    ),
    definition(
        # **Ripartizione.** Una tubazione si sdoppia verso due strade: il ritorno
        # comune che rientra su due macchine in parallelo, la mandata sanitaria
        # che alimenta le utenze e il ricircolo. E' il gemello della confluenza,
        # e come lei ha tutti e tre gli attacchi sul percorso.
        "tee-split",
        "Ripartizione a T",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", HEATING),
            hydronic_port("b", "out", HEATING),
            hydronic_port("c", "out", HEATING),
        ],
        symbol_id="tee-junction",
    ),
    definition(
        # **Ripartizione.** Una tubazione si sdoppia verso due strade: il ritorno
        # comune che rientra su due macchine in parallelo, la mandata sanitaria
        # che alimenta le utenze e il ricircolo. E' il gemello della confluenza,
        # e come lei ha tutti e tre gli attacchi sul percorso.
        "tee-split-dhw",
        "Ripartizione a T sanitario",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", DHW),
            hydronic_port("b", "out", DHW),
            hydronic_port("c", "out", DHW),
        ],
        symbol_id="tee-junction",
    ),
    definition(
        # **Ripartizione.** Una tubazione si sdoppia verso due strade: il ritorno
        # comune che rientra su due macchine in parallelo, la mandata sanitaria
        # che alimenta le utenze e il ricircolo. E' il gemello della confluenza,
        # e come lei ha tutti e tre gli attacchi sul percorso.
        "tee-split-cold",
        "Ripartizione a T sull'acqua fredda",
        ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", COLD),
            hydronic_port("b", "out", COLD),
            hydronic_port("c", "out", COLD),
        ],
        symbol_id="tee-junction",
    ),
    definition(
        # **Derivazione.** Un accessorio pende da uno stacco e la macchina non ha
        # l'attacco dedicato: si salda un T sul tubo e l'accessorio pende dal
        # braccio (D-101). Il braccio **non e' sul percorso**, e lo dichiara.
        "tee-branch",
        "Derivazione a T",
        ["branch_off"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in"),
            hydronic_port("b", "out"),
            branch_port(),
        ],
        symbol_id="tee-branch",
    ),
    definition(
        "tee-branch-dhw",
        "Derivazione a T sanitaria",
        ["branch_off"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", DHW),
            hydronic_port("b", "out", DHW),
            branch_port(DHW),
        ],
        symbol_id="tee-branch",
    ),
    definition(
        "tee-branch-cold",
        "Derivazione a T sull'acqua fredda",
        ["branch_off"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", COLD),
            hydronic_port("b", "out", COLD),
            branch_port(COLD),
        ],
        symbol_id="tee-branch",
    ),
    # --- le famiglie dei cinque impianti di prova del committente -----------
    # Dato puro: nessuna riga di motore le conosce.
    definition(
        "gas-boiler",
        "Caldaia a condensazione",
        ["heat_generation"],
        [
            MAINTAINABLE,
            NEEDS_DEBRIS_PROTECTION,
            PRODUCES_AIR,
            NEEDS_OVERPRESSURE_PROTECTION,
            SHUTOFF_ORDINARY,
            INLINE,
        ],
        [
            hydronic_port("water_supply", "out"),
            hydronic_port("water_return", "in"),
        ],
    ),
    definition(
        "plate-heat-exchanger",
        "Scambiatore a piastre",
        ["heat_exchange"],
        [MAINTAINABLE, NEEDS_DEBRIS_PROTECTION, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("primary_in", "in"),
            hydronic_port("primary_out", "out"),
            hydronic_port("secondary_in", "in", COLD),
            hydronic_port("secondary_out", "out", DHW),
        ],
    ),
    definition(
        "fan-coil",
        "Ventilconvettore",
        ["emission"],
        [MAINTAINABLE, FOULS_CIRCUIT, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("in", "in"), hydronic_port("out", "out")],
    ),
    definition(
        "ahu-coil",
        "Batteria di trattamento aria",
        ["emission"],
        [MAINTAINABLE, FOULS_CIRCUIT, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("in", "in"), hydronic_port("out", "out")],
    ),
    definition(
        "buffer-two-port",
        "Volano termico a due attacchi",
        ["thermal_storage"],
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in"),
            hydronic_port("b", "out"),
            service_port("vent", "air_release"),
            service_port("drain", "drain"),
            service_port("probe", "temperature_measurement"),
        ],
        stored_medium=HEATING,
    ),
    definition(
        # L'accumulo combinato: volume tecnico a quattro tubi e serpentino
        # sanitario dentro lo stesso serbatoio. Cio' che tiene **in serbo** e'
        # l'acqua di riscaldamento; il sanitario ci passa dentro scambiando.
        "buffer-combined",
        "Accumulo combinato",
        ["hydraulic_separation", "thermal_storage"],
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("primary_in", "in"),
            hydronic_port("primary_out", "out"),
            hydronic_port("secondary_out", "out"),
            hydronic_port("secondary_in", "in"),
            hydronic_port("cold_in", "in", COLD),
            hydronic_port("dhw_out", "out", DHW),
            service_port("vent", "air_release"),
            service_port("drain", "drain"),
            service_port("probe", "temperature_measurement"),
        ],
        stored_medium=HEATING,
    ),
    definition(
        # Boiler in pompa di calore: produce e accumula acqua calda sanitaria
        # per conto proprio, senza toccare il circuito di riscaldamento.
        "dhw-heat-pump",
        "Boiler in pompa di calore",
        ["heat_generation", "dhw_storage"],
        [
            MAINTAINABLE,
            NEEDS_OVERPRESSURE_PROTECTION,
            HOLDS_ITS_OWN_VOLUME,
            SHUTOFF_ORDINARY,
            INLINE,
        ],
        [
            hydronic_port("cold_in", "in", COLD),
            hydronic_port("dhw_out", "out", DHW),
            service_port("probe", "temperature_measurement", DHW),
        ],
        stored_medium=DHW,
    ),
    definition(
        "mixing-valve-3way",
        "Valvola miscelatrice a tre vie",
        ["circuit_mixing"],
        [MAINTAINABLE, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("hot_in", "in"),
            hydronic_port("cold_in", "in"),
            hydronic_port("out", "out"),
        ],
    ),
    definition(
        "pump-circulator-dhw",
        "Pompa di ricircolo sanitario",
        ["circulation"],
        [MAINTAINABLE, NEEDS_DEBRIS_PROTECTION, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("a", "in", DHW), hydronic_port("b", "out", DHW)],
        symbol_id="pump-circulator",
    ),
    definition(
        "valve-check-dhw-hot",
        "Valvola di ritegno sull'acqua calda",
        ["non_return"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "bidirectional", DHW),
            hydronic_port("b", "bidirectional", DHW),
        ],
        symbol_id="valve-check",
    ),
    definition(
        "diverting-valve-3way",
        "Valvola deviatrice a tre vie",
        ["diversion"],
        [MAINTAINABLE, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("in", "in"),
            hydronic_port("out_a", "out"),
            hydronic_port("out_b", "out"),
        ],
    ),
    definition(
        "buffer-four-port",
        "Volano termico a quattro attacchi",
        ["hydraulic_separation", "thermal_storage"],
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("primary_in", "in"),
            hydronic_port("primary_out", "out"),
            hydronic_port("secondary_out", "out"),
            hydronic_port("secondary_in", "in"),
            # Gli attacchi di servizio che i costruttori dichiarano in legenda:
            # Rehau T-Puffer elenca sfiato, scarico, termometro e sonda;
            # Cordivari li chiama connessioni per strumentazione (SRC-017,
            # SRC-018). Nessuno dei due dichiara un attacco per il vaso o per
            # la ricarica: quelli stanno sulla tubazione.
            service_port("vent", "air_release"),
            service_port("drain", "drain"),
            service_port("probe", "temperature_measurement"),
        ],
        stored_medium=HEATING,
    ),
    definition(
        "dhw-cylinder",
        "Bollitore ACS",
        ["dhw_storage"],
        [
            MAINTAINABLE,
            NEEDS_OVERPRESSURE_PROTECTION,
            HOLDS_ITS_OWN_VOLUME,
            SHUTOFF_ORDINARY,
            INLINE,
        ],
        [
            hydronic_port("coil_in", "in"),
            hydronic_port("coil_out", "out"),
            # La distribuzione sanitaria e' fuori dal perimetro di questo
            # schema: le due porte esistono ma non sono obbligatorie.
            hydronic_port("dhw_out", "out", DHW, required=False),
            hydronic_port("cold_in", "in", COLD, required=False),
            # Il bollitore dichiara la sede della sonda, e **non** lo scarico:
            # nessuno dei cataloghi letti lo prevede, e il manuale prescrive che
            # sicurezza e vaso li preveda l'installazione, sulla tubazione
            # (SRC-018). Lo si svuota con una derivazione.
            service_port("probe", "temperature_measurement", DHW),
        ],
        stored_medium=DHW,
    ),
    definition(
        "pump-circulator",
        "Pompa di circolazione",
        ["circulation"],
        [MAINTAINABLE, NEEDS_DEBRIS_PROTECTION, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("a", "in"), hydronic_port("b", "out")],
    ),
    definition(
        "zone-manifold",
        "Collettore di zona",
        ["distribution"],
        [MAINTAINABLE, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("in", "in"),
            hydronic_port("out_1", "out"),
            hydronic_port("out_2", "out"),
        ],
    ),
    definition(
        "radiator",
        "Radiatore",
        ["emission"],
        [MAINTAINABLE, FOULS_CIRCUIT, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("in", "in"), hydronic_port("out", "out")],
    ),
    definition(
        "underfloor-panel",
        "Pannello radiante",
        ["emission"],
        [MAINTAINABLE, FOULS_CIRCUIT, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("in", "in"), hydronic_port("out", "out")],
    ),
    definition(
        "strainer",
        "Filtro a Y",
        ["filtration"],
        [MAINTAINABLE, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "bidirectional"),
            hydronic_port("b", "bidirectional"),
        ],
    ),
    definition(
        "valve-isolation",
        "Valvola di intercettazione",
        ["isolation"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "bidirectional"),
            hydronic_port("b", "bidirectional"),
        ],
    ),
]

NETWORKS = [
    {
        "id": "primary",
        "name": "Circuito primario",
        "domain": "hydronic",
        "medium": HEATING,
    },
    {
        "id": "secondary",
        "name": "Circuito secondario",
        "domain": "hydronic",
        "medium": HEATING,
    },
]

COMPONENTS = [
    ("hp", "heat-pump-air-water", "PDC-01"),
    ("dv", "diverting-valve-3way", "VD-01"),
    ("strainer", "strainer", "FIL-01"),
    ("buffer", "buffer-four-port", "VOL-01"),
    ("cylinder", "dhw-cylinder", "BOL-01"),
    ("shutoff", "valve-isolation", "VI-01"),
    ("pump-secondary", "pump-circulator", "CIR-02"),
    ("manifold", "zone-manifold", "COL-01"),
    ("radiators", "radiator", "RAD-01"),
    ("underfloor", "underfloor-panel", "PAV-01"),
    # I due punti in cui due tubazioni diventano una: il ritorno al generatore,
    # dove rientrano il volano e il serpentino, e il ritorno al volano, dove
    # rientrano le due zone. Erano due attacchi con due tubazioni ciascuno.
    ("tee-return-generator", "tee-junction", None),
    ("tee-return-buffer", "tee-junction", None),
]

PROPERTIES: dict[str, dict[str, Any]] = {
    "buffer": {"volume_l": 200},
    "cylinder": {"volume_l": 300},
    "pump-secondary": {"flow_rate_m3h": 1.2},
}


def connection(cid: str, network: str, a: tuple[str, str], b: tuple[str, str]) -> dict[str, Any]:
    return {
        "id": cid,
        "network_id": network,
        "endpoint_a": {"component_id": a[0], "port_id": a[1]},
        "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        "properties": {},
    }


CONNECTIONS = [
    # Primario: la pompa di calore alimenta la deviatrice, che manda al volano
    # o al serpentino del bollitore.
    connection("p1", "primary", ("hp", "water_supply"), ("dv", "in")),
    connection("p2", "primary", ("dv", "out_a"), ("strainer", "a")),
    connection("p3", "primary", ("strainer", "b"), ("buffer", "primary_in")),
    connection("p4", "primary", ("buffer", "primary_out"), ("shutoff", "a")),
    # I due ritorni — volano e serpentino — si uniscono nel raccordo, e dal
    # raccordo riparte una tubazione sola verso il generatore.
    connection("p5", "primary", ("shutoff", "b"), ("tee-return-generator", "a")),
    connection("p6", "primary", ("dv", "out_b"), ("cylinder", "coil_in")),
    connection("p7", "primary", ("cylinder", "coil_out"), ("tee-return-generator", "c")),
    connection("p8", "primary", ("tee-return-generator", "b"), ("hp", "water_return")),
    # Secondario: circolatore dedicato, collettore a due zone, terminali misti.
    connection("s1", "secondary", ("buffer", "secondary_out"), ("pump-secondary", "a")),
    connection("s2", "secondary", ("pump-secondary", "b"), ("manifold", "in")),
    connection("s3", "secondary", ("manifold", "out_1"), ("radiators", "in")),
    connection("s4", "secondary", ("manifold", "out_2"), ("underfloor", "in")),
    connection("s5", "secondary", ("radiators", "out"), ("tee-return-buffer", "a")),
    connection("s6", "secondary", ("underfloor", "out"), ("tee-return-buffer", "c")),
    connection("s7", "secondary", ("tee-return-buffer", "b"), ("buffer", "secondary_in")),
]

SUBSYSTEMS = [
    {
        "id": "generation",
        "name": "Generazione",
        "component_ids": ["hp", "dv"],
        "network_ids": ["primary"],
    },
    {
        "id": "storage",
        "name": "Accumuli e primario",
        "component_ids": [
            "strainer",
            "buffer",
            "cylinder",
            "shutoff",
            "tee-return-generator",
            "tee-return-buffer",
        ],
        "network_ids": ["primary"],
    },
    {
        "id": "distribution",
        "name": "Distribuzione",
        "component_ids": ["pump-secondary", "manifold"],
        "network_ids": ["secondary"],
    },
    {
        "id": "zones",
        "name": "Zone",
        "component_ids": ["radiators", "underfloor"],
        "network_ids": ["secondary"],
    },
]

SHEETS = [
    {
        "id": "t1",
        "title": "Schema funzionale centrale termica",
        "subsystem_ids": ["generation", "storage", "distribution", "zones"],
        "band_assignments": [
            {"subsystem_id": "generation", "band": "generation", "order": 0},
            {"subsystem_id": "storage", "band": "primary", "order": 0},
            {"subsystem_id": "distribution", "band": "distribution", "order": 0},
            {"subsystem_id": "zones", "band": "terminal", "order": 0},
        ],
    }
]


def project() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "project_id": "heat-pump-dhw-buffer-two-zones",
            "client": "Nove C",
            "project_name": "PDC con ACS, volano a quattro attacchi e due zone",
            "commission_code": "DEV-011",
            "revision": "00",
            "issue_date": "2026-08-04",
        },
        "subsystems": SUBSYSTEMS,
        "networks": NETWORKS,
        "components": [
            {
                "id": component_id,
                "definition_id": definition_id,
                "tag": tag,
                "properties": PROPERTIES.get(component_id, {}),
            }
            for component_id, definition_id, tag in COMPONENTS
        ],
        "connections": CONNECTIONS,
        "assumptions": [],
        "rule_applications": [],
        "sheets": SHEETS,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    CATALOG.mkdir(parents=True, exist_ok=True)
    for item in DEFINITIONS:
        write_json(CATALOG / f"{item['id']}.json", item)
    write_json(ROOT / "heat-pump-dhw-buffer-two-zones.json", project())


if __name__ == "__main__":
    main()
