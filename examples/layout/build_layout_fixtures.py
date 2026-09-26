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
BRANCH = "attachment_branch"
SHUTOFF_NEVER = "shutoff_never"
SHUTOFF_LOCKABLE_ONLY = "shutoff_lockable_only"
SHUTOFF_INSTRUMENT_TAP = "shutoff_instrument_tap"

HEATING = "heating_water"
DHW = "domestic_hot_water"
# Il fluido dell'acqua fredda sanitaria si chiama "cold_water" ovunque: nelle
# altre voci del catalogo, nelle condizioni delle regole e nelle reti dei
# progetti d'esempio. Qui era rimasto un nome diverso da quando il generatore
# non veniva piu' rieseguito, e rigenerare il catalogo cambiava in silenzio il
# fluido del bollitore.
COLD = "cold_water"
SOLAR = "solar_fluid"
"""Il fluido del circuito solare (`REL-003`, D-187): si chiama «fluido solare», si
disegna magenta sia in mandata sia in ritorno (D-186), e **le regole non
aggiungono niente** sulle sue reti — il gruppo di circolazione lo descrive il
progettista. Il circuito si riempie di fluido antigelo, non dall'acquedotto."""


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


def recirculation_port() -> dict[str, Any]:
    """L'attacco del ricircolo di un accumulo di acqua calda sanitaria (**D-176**).

    Il PO, il 23 settembre 2026: «ACS-ritorno dopo il Circolatore va
    nell'accumulo ACS (se ho accumulo) altrimenti idraulicamente e termicamente
    non ha senso». E' un attacco del **flusso** — il ricircolo ci entra come una
    linea vera — e l'accumulo lo ha anche dove l'impianto il ricircolo non lo
    ha: li' e' **tappato**, e libero non e' un difetto."""
    port = hydronic_port("recirculation_in", "in", DHW, required=False)
    port["plugged_when_unused"] = True
    return port


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


def state(state_id: str, name: str, *groups: list[str]) -> dict[str, Any]:
    """Una configurazione ammessa di un multivia (DRAW-006, blocco C).

    Dichiara **quali porte comunicano** in quello stato: una deviatrice a tre
    vie manda l'ingresso su un ramo oppure sull'altro, e i due rami non sono mai
    in comunicazione fra loro.
    """
    return {"id": state_id, "name": name, "connects": [list(item) for item in groups]}


def definition(
    definition_id: str,
    name: str,
    functions: list[str],
    traits: list[str],
    ports: list[dict[str, Any]],
    symbol_id: str | None = None,
    stored_medium: str | None = None,
    carries_on_board: list[str] | None = None,
    fills_from: str | None = None,
    hydraulic_states: list[dict[str, Any]] | None = None,
    composite: bool = False,
    variant: dict[str, Any] | None = None,
    sources: list[str] | None = None,
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
    # Cio' che la macchina porta a bordo di fabbrica (D-106): un fatto della
    # macchina, dichiarato dal suo catalogo, che le regole leggono per non
    # aggiungere cio' che sta gia' dentro il mantello.
    if carries_on_board is not None:
        entry["carries_on_board"] = carries_on_board
    if stored_medium is not None:
        entry["stored_medium"] = stored_medium
    # Da quale attacco la riserva si riempie (C2): un fatto della macchina,
    # dai cataloghi dei costruttori. Dove si riempie, da li' si svuota.
    if fills_from is not None:
        entry["fills_from"] = fills_from
    # Le configurazioni ammesse di un multivia: solo chi ne ha piu' d'una le
    # dichiara, e chi tace resta com'e' sempre stato.
    if hydraulic_states is not None:
        entry["hydraulic_states"] = hydraulic_states
    entry["symbol_id"] = symbol_id or definition_id
    # La stessa macchina di un'altra voce, con un altro simbolo: si sceglie solo
    # quando il testo la nomina (D-187). Chi la dichiara la scrive qui, e il
    # registro controlla che mestieri e attacchi siano quelli della voce base.
    if variant is not None:
        entry["variant"] = variant
    entry.update(
        {
            "composite": composite,
            "ports": ports,
            "sources": [SOURCE, *(sources or [])],
        }
    )
    return entry


GENERATOR_TRAITS = [
    MAINTAINABLE,
    NEEDS_DEBRIS_PROTECTION,
    PRODUCES_AIR,
    NEEDS_OVERPRESSURE_PROTECTION,
    SHUTOFF_ORDINARY,
    INLINE,
]
"""I caratteri della pompa di calore e della caldaia: le varianti li hanno uguali."""

D187 = "D-187: il PO, 26 settembre 2026 (I-130)"


def solar_accessory(
    definition_id: str,
    name: str,
    functions: list[str],
    traits: list[str],
    ports: list[dict[str, Any]],
    symbol_id: str,
) -> dict[str, Any]:
    """Un accessorio del circuito solare: lo stesso pezzo, con il fluido solare.

    Ogni voce dichiara il fluido dei propri attacchi, come fanno i pezzi
    sanitari: il circolatore del solare e' il circolatore, disegnato con lo
    stesso simbolo, e cambia soltanto cio' che ci scorre dentro (D-184)."""
    return definition(
        definition_id, name, functions, traits, ports, symbol_id=symbol_id, sources=[D187]
    )


REL_003: list[dict[str, Any]] = [
    # --- i simboli nuovi della prima release (`REL-003`, D-184, D-187) -------
    # **Tre varianti**: la stessa macchina del fratello — stessi mestieri, stessi
    # attacchi —, un altro simbolo. Si sceglie solo quando il testo la nomina con
    # le parole del PO, e mai per potenza.
    definition(
        "heat-pump-air-water-large",
        "Pompa di calore aria-acqua di alta potenza",
        ["heat_generation"],
        GENERATOR_TRAITS,
        [
            hydronic_port("water_supply", "out"),
            hydronic_port("water_return", "in"),
        ],
        # Il circolatore a bordo, come la monoblocco domestica: cosi' la
        # disegnano Caleffi (SRC-030, fig. 47) e il progetto di Padova (SRC-031),
        # e cosi' l'ha confermato il PO (D-187).
        carries_on_board=["circulation"],
        variant={"of": "heat-pump-air-water", "named_as": ["alta potenza", "grande taglia"]},
        sources=[D187],
    ),
    definition(
        "gas-boiler-modular",
        "Caldaia modulare a condensazione",
        ["heat_generation"],
        GENERATOR_TRAITS,
        [
            hydronic_port("water_supply", "out"),
            hydronic_port("water_return", "in"),
        ],
        # Il PO, 26 settembre 2026: «anche loro le danno sempre con circolatore
        # integrato» (D-187). E' la differenza di contenuto con la murale, che
        # non dichiara niente a bordo.
        carries_on_board=["circulation"],
        variant={"of": "gas-boiler", "named_as": ["modulare", "a moduli"]},
        sources=[D187],
    ),
    definition(
        "fan-coil-ducted",
        "Ventilconvettore canalizzato",
        ["emission"],
        [MAINTAINABLE, FOULS_CIRCUIT, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("in", "in"), hydronic_port("out", "out")],
        variant={"of": "fan-coil", "named_as": ["canalizzato", "canalizzabile"]},
        sources=[D187],
    ),
    # **Il solare.** Il collettore e' un generatore (D-187), sigla GT; i suoi
    # attacchi portano il fluido solare, e sulle reti di quel fluido le regole
    # non aggiungono niente: i caratteri dicono che cosa e' vero del pezzo, non
    # accendono corredo.
    definition(
        "solar-collector",
        "Collettore solare",
        ["heat_generation"],
        [MAINTAINABLE, PRODUCES_AIR, NEEDS_OVERPRESSURE_PROTECTION, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("supply", "out", SOLAR),
            hydronic_port("return", "in", SOLAR),
        ],
        sources=[D187],
    ),
    definition(
        # Il bollitore a due serpentini: il serpentino di integrazione dove sta
        # quello del bollitore a un serpentino, il solare sotto. Non e' una
        # variante: ha attacchi che nessun'altra voce ha, ed e' da quelli che lo
        # si sceglie (D-187).
        "dhw-cylinder-twin-coil",
        "Bollitore ACS a due serpentini",
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
            hydronic_port("solar_coil_in", "in", SOLAR),
            hydronic_port("solar_coil_out", "out", SOLAR),
            hydronic_port("dhw_out", "out", DHW, required=False),
            hydronic_port("cold_in", "in", COLD, required=False),
            service_port("probe", "temperature_measurement", DHW),
            recirculation_port(),
        ],
        stored_medium=DHW,
        fills_from="cold_in",
        sources=[D187],
    ),
    # Gli accessori del circuito solare: quelli del gruppo di circolazione
    # (D-184) — circolatore, ritegno, sicurezza, vaso, manometro, termometro,
    # intercettazione — piu' lo sfogo dell'aria, lo scarico e i raccordi.
    solar_accessory(
        "pump-circulator-solar", "Pompa di circolazione solare", ["circulation"],
        [MAINTAINABLE, NEEDS_DEBRIS_PROTECTION, SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("a", "in", SOLAR), hydronic_port("b", "out", SOLAR)],
        "pump-circulator",
    ),
    solar_accessory(
        "valve-check-solar", "Valvola di ritegno solare", ["non_return"],
        [SHUTOFF_ORDINARY, INLINE],
        [hydronic_port("a", "in", SOLAR), hydronic_port("b", "out", SOLAR)],
        "valve-check",
    ),
    solar_accessory(
        "valve-isolation-solar", "Valvola di intercettazione solare", ["isolation"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "bidirectional", SOLAR),
            hydronic_port("b", "bidirectional", SOLAR),
        ],
        "valve-isolation",
    ),
    solar_accessory(
        "valve-safety-solar", "Valvola di sicurezza solare", ["safety"],
        [SHUTOFF_NEVER, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "valve-safety",
    ),
    solar_accessory(
        "expansion-connection-solar", "Vaso di espansione solare", ["expansion"],
        [MAINTAINABLE, SHUTOFF_LOCKABLE_ONLY, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "expansion-connection",
    ),
    solar_accessory(
        "pressure-gauge-solar", "Manometro solare", ["pressure_measurement"],
        [MAINTAINABLE, SHUTOFF_INSTRUMENT_TAP, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "pressure-gauge",
    ),
    solar_accessory(
        "thermometer-solar", "Termometro solare", ["temperature_measurement"],
        [SHUTOFF_ORDINARY, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "thermometer",
    ),
    solar_accessory(
        "air-vent-solar", "Valvola di sfogo aria solare", ["air_release"],
        [SHUTOFF_ORDINARY, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "air-vent",
    ),
    solar_accessory(
        "drain-connection-solar", "Attacco di carico e scarico solare", ["drain"],
        [SHUTOFF_ORDINARY, BRANCH],
        [hydronic_port("a", "bidirectional", SOLAR)],
        "drain-connection",
    ),
    solar_accessory(
        "tee-junction-solar", "Raccordo a T solare", ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", SOLAR),
            hydronic_port("c", "in", SOLAR),
            hydronic_port("b", "out", SOLAR),
        ],
        "tee-junction",
    ),
    solar_accessory(
        "tee-split-solar", "Ripartizione a T solare", ["junction"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", SOLAR),
            hydronic_port("b", "out", SOLAR),
            hydronic_port("c", "out", SOLAR),
        ],
        "tee-junction",
    ),
    solar_accessory(
        "tee-branch-solar", "Derivazione a T solare", ["branch_off"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", SOLAR),
            hydronic_port("b", "out", SOLAR),
            branch_port(SOLAR),
        ],
        "tee-branch",
    ),
]

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
        # Le monoblocco comuni portano a bordo il circolatore primario, non il
        # vaso di espansione (D-106; SRC-019, p. 15): nessuna regola deve
        # aggiungere un circolatore che sta gia' dentro il mantello.
        carries_on_board=["circulation"],
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
        # La riserva chiusa si scalda e dilata: e' il fatto per cui la
        # sicurezza della piccola centrale sta sul serbatoio (D-106), e il
        # bollitore sanitario lo dichiarava gia'.
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, NEEDS_OVERPRESSURE_PROTECTION, SHUTOFF_ORDINARY, INLINE],
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
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, NEEDS_OVERPRESSURE_PROTECTION, SHUTOFF_ORDINARY, INLINE],
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
            recirculation_port(),
        ],
        stored_medium=DHW,
        fills_from="cold_in",
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
        # **Ha un verso, come ogni ritegno** (I-114): il simbolo porta la
        # freccia del flusso, e il motore la gira nel verso della tratta solo se
        # il catalogo dichiara ingresso e uscita. Fino al 24 settembre 2026 le
        # due porte erano «bidirezionali», e sul ricircolo dell'impianto 5 la
        # freccia puntava contro il flusso: l'ha visto il PO sulla tavola.
        "valve-check-dhw-hot",
        "Valvola di ritegno sull'acqua calda",
        ["non_return"],
        [SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("a", "in", DHW),
            hydronic_port("b", "out", DHW),
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
        # I due stati della deviazione. L'ingresso comunica con un ramo oppure
        # con l'altro; i due rami non comunicano mai fra loro, e attraversarli
        # insieme descriverebbe un passaggio che non esiste (DRAW-006, blocco C).
        hydraulic_states=[
            state("verso_a", "Deviazione sul primo ramo", ["in", "out_a"]),
            state("verso_b", "Deviazione sul secondo ramo", ["in", "out_b"]),
        ],
    ),
    definition(
        "switching-valve-3way",
        "Valvola commutatrice a tre vie",
        ["circuit_switching"],
        [MAINTAINABLE, SHUTOFF_ORDINARY, INLINE],
        [
            hydronic_port("in_a", "in"),
            hydronic_port("in_b", "in"),
            hydronic_port("out", "out"),
        ],
        # **Due ingressi e un'uscita: l'organo che sceglie da dove si pesca.**
        # Serve perche' un circuito sanitario dedicato sia davvero dedicato
        # (D-137): la caldaia deve poter pescare dal primario quando fa
        # riscaldamento e dallo scambiatore quando fa sanitario, e senza questo
        # organo, mentre fa sanitario, pesca da tutt'e due — e' il «ritorno che
        # torna ovunque» che il PO ha visto guardando la tavola 4.
        #
        # ⛔ **Non e' la miscelatrice.** `mixing-valve-3way` ha la geometria
        # giusta — due ingressi, un'uscita — ma dichiara `circuit_mixing`, che
        # e' un altro mestiere: miscelare vuol dire far uscire i due ingressi
        # **insieme**, commutare vuol dire farne passare **uno per volta**. Una
        # funzione non si piega per far tornare un disegno (D-069).
        hydraulic_states=[
            state("da_primario", "Pesca dal primario", ["in_a", "out"]),
            state("da_sanitario", "Pesca dal sanitario", ["in_b", "out"]),
        ],
    ),
    definition(
        "buffer-four-port",
        "Volano termico a quattro attacchi",
        ["hydraulic_separation", "thermal_storage"],
        [MAINTAINABLE, HOLDS_ITS_OWN_VOLUME, NEEDS_OVERPRESSURE_PROTECTION, SHUTOFF_ORDINARY, INLINE],
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
            recirculation_port(),
        ],
        stored_medium=DHW,
        # La riserva si riempie dall'ingresso dell'acqua fredda (SRC-018,
        # SRC-026): e' da li' che la si svuota, con la derivazione (C2).
        fills_from="cold_in",
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
    *REL_003,
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
