"""I cinque impianti di prova del committente, letti come farebbe il primo pezzo.

Il primo pezzo della skill legge la descrizione a parole dell'ingegnere e ne
costruisce il **grafo di prima stesura**: solo cio' che lui ha detto, senza
aggiungere niente. Questo file e' quella lettura, fatta a mano e messa nero su
bianco, per i cinque impianti che il committente ha consegnato il 6 agosto 2026.

**Cosa c'e' dentro, e cosa no.** Ci sono le macchine che il testo nomina, i
circuiti che descrive e le tubazioni che li collegano. Non c'e' **nessun**
accessorio: valvole, filtri, sfiati, vasi e strumenti li aggiungono le regole, e
la fila la decide l'assemblatore. Se un accessorio comparisse qui, la prova non
proverebbe niente.

**Dove il testo non basta, si dichiara.** Ogni impianto porta scritte le
assunzioni che ho dovuto fare per chiudere il grafo: sono le domande che il
primo pezzo girerebbe all'ingegnere invece di risolverle da solo.

    python examples/prova/build_test_plants.py
"""

import json
from pathlib import Path
from typing import Any

from disegnatore_mep.model.project import SCHEMA_VERSION

REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "examples" / "prova"

HEATING = "heating_water"
DHW = "domestic_hot_water"
COLD = "cold_water"


def network(network_id: str, name: str, medium: str) -> dict[str, Any]:
    return {"id": network_id, "name": name, "domain": "hydronic", "medium": medium}


def pipe(pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]) -> dict[str, Any]:
    return {
        "id": pipe_id,
        "network_id": network_id,
        "endpoint_a": {"component_id": a[0], "port_id": a[1]},
        "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        "properties": {},
    }


def plant(
    project_id: str,
    title: str,
    components: list[tuple[str, str, str | None]],
    networks: list[dict[str, Any]],
    pipes: list[dict[str, Any]],
    subsystems: list[dict[str, Any]],
    assumptions: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "project_id": project_id,
            "client": "Nove C",
            "project_name": title,
            "commission_code": "PROVA",
            "revision": "00",
            "issue_date": "2026-08-06",
        },
        "networks": networks,
        "components": [
            {"id": cid, "definition_id": did, "tag": tag, "properties": {}}
            for cid, did, tag in components
        ],
        "connections": pipes,
        "assumptions": [
            {"id": f"a{index + 1}", "text": text, "status": "proposed"}
            for index, text in enumerate(assumptions)
        ],
        "rule_applications": [],
        "subsystems": subsystems,
        "sheets": [],
    }


# ---------------------------------------------------------------------------
# 1 — Due pompe di calore in parallelo con accumulo combinato
# ---------------------------------------------------------------------------

UNO = plant(
    "prova-1-due-pdc-accumulo-combinato",
    "Due pompe di calore in parallelo con accumulo combinato",
    [
        ("pdc-master", "heat-pump-air-water", "PDC-01"),
        ("pdc-slave", "heat-pump-air-water", "PDC-02"),
        ("collettore-mandata", "tee-junction", None),
        ("collettore-ritorno", "tee-split", None),
        ("accumulo", "buffer-combined", "ACC-01"),
        ("circolatore", "pump-circulator", "CIR-01"),
        ("radiatori", "radiator", "RAD-01"),
        ("acquedotto", "cold-water-inlet", "AF-01"),
        ("utenze", "dhw-draw-off", "ACS-01"),
    ],
    [
        network("primario", "Circuito primario", HEATING),
        network("secondario", "Circuito secondario", HEATING),
        network("fredda", "Acqua fredda sanitaria", COLD),
        network("sanitaria", "Acqua calda sanitaria", DHW),
    ],
    [
        # Le due macchine in parallelo si uniscono prima dell'accumulo: due
        # tubazioni non arrivano sullo stesso bocchello (D-100).
        pipe("p1", "primario", ("pdc-master", "water_supply"), ("collettore-mandata", "a")),
        pipe("p2", "primario", ("pdc-slave", "water_supply"), ("collettore-mandata", "c")),
        pipe("p3", "primario", ("collettore-mandata", "b"), ("accumulo", "primary_in")),
        pipe("p4", "primario", ("accumulo", "primary_out"), ("collettore-ritorno", "a")),
        pipe("p5", "primario", ("collettore-ritorno", "b"), ("pdc-master", "water_return")),
        pipe("p6", "primario", ("collettore-ritorno", "c"), ("pdc-slave", "water_return")),
        pipe("s1", "secondario", ("accumulo", "secondary_out"), ("circolatore", "a")),
        pipe("s2", "secondario", ("circolatore", "b"), ("radiatori", "in")),
        pipe("s3", "secondario", ("radiatori", "out"), ("accumulo", "secondary_in")),
        pipe("w1", "fredda", ("acquedotto", "a"), ("accumulo", "cold_in")),
        pipe("w2", "sanitaria", ("accumulo", "dhw_out"), ("utenze", "a")),
    ],
    [
        {
            "id": "generazione",
            "name": "Generazione",
            "component_ids": ["pdc-master", "pdc-slave", "collettore-mandata", "collettore-ritorno"],
            "network_ids": ["primario"],
        },
        {
            "id": "accumulo",
            "name": "Accumulo",
            "component_ids": ["accumulo", "acquedotto", "utenze"],
            "network_ids": ["primario", "fredda", "sanitaria"],
        },
        {
            "id": "distribuzione",
            "name": "Distribuzione",
            "component_ids": ["circolatore", "radiatori"],
            "network_ids": ["secondario"],
        },
    ],
    [
        "Il testo dice che le due macchine sono in parallelo e non dice come si "
        "uniscono: si e' assunto un collettore di mandata e uno di ritorno.",
        "Il carico automatico da acquedotto e lo scarico sono nominati sul volume "
        "tecnico: li aggiungono le regole, non sono scritti qui.",
    ],
)


# ---------------------------------------------------------------------------
# 2 — Pompa di calore con deviazione fra climatizzazione e ACS
# ---------------------------------------------------------------------------

DUE = plant(
    "prova-2-pdc-deviatrice-acs",
    "Pompa di calore con deviazione fra climatizzazione e ACS",
    [
        ("pdc", "heat-pump-air-water", "PDC-01"),
        ("deviatrice", "diverting-valve-3way", "VD-01"),
        ("volano", "buffer-four-port", "VOL-01"),
        ("bollitore", "dhw-cylinder", "BOL-01"),
        ("ritorno", "tee-junction", None),
        ("circolatore", "pump-circulator", "CIR-01"),
        ("ventilconvettori", "fan-coil", "VC-01"),
        ("acquedotto", "cold-water-inlet", "AF-01"),
        ("utenze", "dhw-draw-off", "ACS-01"),
    ],
    [
        network("primario", "Circuito primario", HEATING),
        network("secondario", "Circuito secondario", HEATING),
        network("fredda", "Acqua fredda sanitaria", COLD),
        network("sanitaria", "Acqua calda sanitaria", DHW),
    ],
    [
        pipe("p1", "primario", ("pdc", "water_supply"), ("deviatrice", "in")),
        pipe("p2", "primario", ("deviatrice", "out_a"), ("volano", "primary_in")),
        pipe("p3", "primario", ("volano", "primary_out"), ("ritorno", "a")),
        pipe("p4", "primario", ("deviatrice", "out_b"), ("bollitore", "coil_in")),
        pipe("p5", "primario", ("bollitore", "coil_out"), ("ritorno", "c")),
        pipe("p6", "primario", ("ritorno", "b"), ("pdc", "water_return")),
        pipe("s1", "secondario", ("volano", "secondary_out"), ("circolatore", "a")),
        pipe("s2", "secondario", ("circolatore", "b"), ("ventilconvettori", "in")),
        pipe("s3", "secondario", ("ventilconvettori", "out"), ("volano", "secondary_in")),
        pipe("w1", "fredda", ("acquedotto", "a"), ("bollitore", "cold_in")),
        pipe("w2", "sanitaria", ("bollitore", "dhw_out"), ("utenze", "a")),
    ],
    [
        {
            "id": "generazione",
            "name": "Generazione",
            "component_ids": ["pdc", "deviatrice", "ritorno"],
            "network_ids": ["primario"],
        },
        {
            "id": "accumuli",
            "name": "Accumuli",
            "component_ids": ["volano", "bollitore", "acquedotto", "utenze"],
            "network_ids": ["primario", "fredda", "sanitaria"],
        },
        {
            "id": "distribuzione",
            "name": "Distribuzione",
            "component_ids": ["circolatore", "ventilconvettori"],
            "network_ids": ["secondario"],
        },
    ],
    [
        "La priorita' sanitaria e' una logica di regolazione: sul grafo si vede "
        "la deviatrice, non la priorita'.",
        "La miscelatrice sull'uscita sanitaria e' nominata dal testo e la "
        "aggiungono le regole, che gia' la prevedono.",
    ],
)


# ---------------------------------------------------------------------------
# 3 — Pompa di calore diretta su pavimento radiante
# ---------------------------------------------------------------------------

TRE = plant(
    "prova-3-pdc-diretta-pavimento",
    "Pompa di calore diretta su pavimento radiante, ACS separata",
    [
        ("pdc", "heat-pump-air-water", "PDC-01"),
        ("collettore", "zone-manifold", "COL-01"),
        ("zona-giorno", "underfloor-panel", "PAV-01"),
        ("zona-notte", "underfloor-panel", "PAV-02"),
        ("ritorno-zone", "tee-junction", None),
        ("volano", "buffer-two-port", "VOL-01"),
        ("boiler", "dhw-heat-pump", "BPC-01"),
        ("acquedotto", "cold-water-inlet", "AF-01"),
        ("utenze", "dhw-draw-off", "ACS-01"),
    ],
    [
        network("riscaldamento", "Circuito di riscaldamento", HEATING),
        network("fredda", "Acqua fredda sanitaria", COLD),
        network("sanitaria", "Acqua calda sanitaria", DHW),
    ],
    [
        pipe("p1", "riscaldamento", ("pdc", "water_supply"), ("collettore", "in")),
        pipe("p2", "riscaldamento", ("collettore", "out_1"), ("zona-giorno", "in")),
        pipe("p3", "riscaldamento", ("collettore", "out_2"), ("zona-notte", "in")),
        pipe("p4", "riscaldamento", ("zona-giorno", "out"), ("ritorno-zone", "a")),
        pipe("p5", "riscaldamento", ("zona-notte", "out"), ("ritorno-zone", "c")),
        # Il volano e' **in serie sul ritorno**: aumenta il contenuto d'acqua.
        pipe("p6", "riscaldamento", ("ritorno-zone", "b"), ("volano", "a")),
        pipe("p7", "riscaldamento", ("volano", "b"), ("pdc", "water_return")),
        # L'acqua calda sanitaria e' un impianto a se': non tocca il riscaldamento.
        pipe("w1", "fredda", ("acquedotto", "a"), ("boiler", "cold_in")),
        pipe("w2", "sanitaria", ("boiler", "dhw_out"), ("utenze", "a")),
    ],
    [
        {
            "id": "generazione",
            "name": "Generazione",
            "component_ids": ["pdc", "volano", "ritorno-zone"],
            "network_ids": ["riscaldamento"],
        },
        {
            "id": "zone",
            "name": "Zone radianti",
            "component_ids": ["collettore", "zona-giorno", "zona-notte"],
            "network_ids": ["riscaldamento"],
        },
        {
            "id": "sanitario",
            "name": "Acqua calda sanitaria",
            "component_ids": ["boiler", "acquedotto", "utenze"],
            "network_ids": ["fredda", "sanitaria"],
        },
    ],
    [
        "Il testo dice «piu' circuiti ambiente con regolazione di zona» senza "
        "dirne il numero: se ne sono disegnati due.",
        "Il circolatore e' integrato nella macchina, come il testo dichiara: "
        "non compare come pezzo a se'.",
    ],
)


# ---------------------------------------------------------------------------
# 4 — Sistema ibrido con pompa di calore e caldaia
# ---------------------------------------------------------------------------

QUATTRO = plant(
    "prova-4-ibrido-pdc-caldaia",
    "Sistema ibrido con pompa di calore e caldaia a condensazione",
    [
        ("pdc", "heat-pump-air-water", "PDC-01"),
        ("caldaia", "gas-boiler", "CAL-01"),
        ("collettore-mandata", "tee-junction", None),
        ("collettore-ritorno", "tee-split", None),
        ("volano", "buffer-four-port", "VOL-01"),
        ("circolatore", "pump-circulator", "CIR-01"),
        ("radiatori", "radiator", "RAD-01"),
        ("deviatrice", "diverting-valve-3way", "VD-01"),
        ("scambiatore", "plate-heat-exchanger", "SCA-01"),
        ("ritorno-caldaia", "tee-junction", None),
        ("acquedotto", "cold-water-inlet", "AF-01"),
        ("utenze", "dhw-draw-off", "ACS-01"),
    ],
    [
        network("primario", "Circuito primario", HEATING),
        network("secondario", "Circuito secondario", HEATING),
        network("fredda", "Acqua fredda sanitaria", COLD),
        network("sanitaria", "Acqua calda sanitaria", DHW),
    ],
    [
        # La pompa di calore alimenta il volume tecnico.
        pipe("p1", "primario", ("pdc", "water_supply"), ("collettore-mandata", "a")),
        # La caldaia alimenta il volume tecnico oppure, quando serve ACS, la
        # deviatrice manda il suo circuito allo scambiatore a piastre.
        pipe("p2", "primario", ("caldaia", "water_supply"), ("deviatrice", "in")),
        pipe("p3", "primario", ("deviatrice", "out_a"), ("collettore-mandata", "c")),
        pipe("p4", "primario", ("collettore-mandata", "b"), ("volano", "primary_in")),
        pipe("p5", "primario", ("volano", "primary_out"), ("collettore-ritorno", "a")),
        pipe("p6", "primario", ("collettore-ritorno", "b"), ("pdc", "water_return")),
        pipe("p7", "primario", ("deviatrice", "out_b"), ("scambiatore", "primary_in")),
        pipe("p8", "primario", ("scambiatore", "primary_out"), ("ritorno-caldaia", "c")),
        pipe("p9", "primario", ("collettore-ritorno", "c"), ("ritorno-caldaia", "a")),
        pipe("p10", "primario", ("ritorno-caldaia", "b"), ("caldaia", "water_return")),
        pipe("s1", "secondario", ("volano", "secondary_out"), ("circolatore", "a")),
        pipe("s2", "secondario", ("circolatore", "b"), ("radiatori", "in")),
        pipe("s3", "secondario", ("radiatori", "out"), ("volano", "secondary_in")),
        # L'acqua fredda attraversa lo scambiatore e va alle utenze: istantanea.
        pipe("w1", "fredda", ("acquedotto", "a"), ("scambiatore", "secondary_in")),
        pipe("w2", "sanitaria", ("scambiatore", "secondary_out"), ("utenze", "a")),
    ],
    [
        {
            "id": "generazione",
            "name": "Generazione",
            "component_ids": [
                "pdc",
                "caldaia",
                "deviatrice",
                "collettore-mandata",
                "collettore-ritorno",
                "ritorno-caldaia",
            ],
            "network_ids": ["primario"],
        },
        {
            "id": "accumulo",
            "name": "Accumulo",
            "component_ids": ["volano"],
            "network_ids": ["primario"],
        },
        {
            "id": "distribuzione",
            "name": "Distribuzione",
            "component_ids": ["circolatore", "radiatori"],
            "network_ids": ["secondario"],
        },
        {
            "id": "sanitario",
            "name": "Acqua calda sanitaria istantanea",
            "component_ids": ["scambiatore", "acquedotto", "utenze"],
            "network_ids": ["primario", "fredda", "sanitaria"],
        },
    ],
    [
        "Il ritorno comune ai due generatori e' un'assunzione: il testo dice che "
        "sono in parallelo e non descrive come rientrano.",
        "«La caldaia da' priorita' al sanitario» e' logica di regolazione, non "
        "topologia: sul grafo si vede la deviatrice.",
    ],
)


# ---------------------------------------------------------------------------
# 5 — Tre pompe di calore in cascata con piu' circuiti secondari
# ---------------------------------------------------------------------------

CINQUE = plant(
    "prova-5-cascata-tre-pdc",
    "Tre pompe di calore in cascata con tre circuiti secondari e ACS",
    [
        ("pdc-1", "heat-pump-air-water", "PDC-01"),
        ("pdc-2", "heat-pump-air-water", "PDC-02"),
        ("pdc-3", "heat-pump-air-water", "PDC-03"),
        ("cascata-mandata-a", "tee-junction", None),
        ("cascata-mandata-b", "tee-junction", None),
        ("cascata-ritorno-a", "tee-split", None),
        ("cascata-ritorno-b", "tee-split", None),
        ("deviatrice", "diverting-valve-3way", "VD-01"),
        ("volano", "buffer-four-port", "VOL-01"),
        ("bollitore", "dhw-cylinder", "BOL-01"),
        ("ritorno-primario", "tee-junction", None),
        ("collettore", "zone-manifold", "COL-01"),
        ("circolatore-uta", "pump-circulator", "CIR-01"),
        ("batteria-uta", "ahu-coil", "BAT-01"),
        ("circolatore-fancoil", "pump-circulator", "CIR-02"),
        ("ventilconvettori", "fan-coil", "VC-01"),
        ("ritorno-secondario", "tee-junction", None),
        ("acquedotto", "cold-water-inlet", "AF-01"),
        ("utenze", "dhw-draw-off", "ACS-01"),
        ("ricircolo", "pump-circulator-dhw", "CIR-04"),
        ("ritegno-ricircolo", "valve-check-dhw-hot", "VR-02"),
        ("innesto-ricircolo", "tee-junction-dhw", None),
        ("presa-ricircolo", "tee-split-dhw", None),
    ],
    [
        network("primario", "Circuito primario", HEATING),
        network("secondario", "Circuito secondario", HEATING),
        network("fredda", "Acqua fredda sanitaria", COLD),
        network("sanitaria", "Acqua calda sanitaria", DHW),
    ],
    [
        # Tre macchine in cascata: due confluenze per la mandata, due per il ritorno.
        pipe("p1", "primario", ("pdc-1", "water_supply"), ("cascata-mandata-a", "a")),
        pipe("p2", "primario", ("pdc-2", "water_supply"), ("cascata-mandata-a", "c")),
        pipe("p3", "primario", ("cascata-mandata-a", "b"), ("cascata-mandata-b", "a")),
        pipe("p4", "primario", ("pdc-3", "water_supply"), ("cascata-mandata-b", "c")),
        pipe("p5", "primario", ("cascata-mandata-b", "b"), ("deviatrice", "in")),
        pipe("p6", "primario", ("deviatrice", "out_a"), ("volano", "primary_in")),
        pipe("p7", "primario", ("deviatrice", "out_b"), ("bollitore", "coil_in")),
        pipe("p8", "primario", ("volano", "primary_out"), ("ritorno-primario", "a")),
        pipe("p9", "primario", ("bollitore", "coil_out"), ("ritorno-primario", "c")),
        pipe("p10", "primario", ("ritorno-primario", "b"), ("cascata-ritorno-a", "a")),
        pipe("p11", "primario", ("cascata-ritorno-a", "b"), ("pdc-1", "water_return")),
        pipe("p12", "primario", ("cascata-ritorno-a", "c"), ("cascata-ritorno-b", "a")),
        pipe("p13", "primario", ("cascata-ritorno-b", "b"), ("pdc-2", "water_return")),
        pipe("p14", "primario", ("cascata-ritorno-b", "c"), ("pdc-3", "water_return")),
        # Due circuiti secondari dal volano, ciascuno col proprio circolatore.
        pipe("s1", "secondario", ("volano", "secondary_out"), ("collettore", "in")),
        pipe("s2", "secondario", ("collettore", "out_1"), ("circolatore-uta", "a")),
        pipe("s3", "secondario", ("circolatore-uta", "b"), ("batteria-uta", "in")),
        pipe("s4", "secondario", ("batteria-uta", "out"), ("ritorno-secondario", "a")),
        pipe("s5", "secondario", ("collettore", "out_2"), ("circolatore-fancoil", "a")),
        pipe("s6", "secondario", ("circolatore-fancoil", "b"), ("ventilconvettori", "in")),
        pipe("s7", "secondario", ("ventilconvettori", "out"), ("ritorno-secondario", "c")),
        pipe("s8", "secondario", ("ritorno-secondario", "b"), ("volano", "secondary_in")),
        pipe("w1", "fredda", ("acquedotto", "a"), ("bollitore", "cold_in")),
        # Ricircolo sanitario: dalle utenze torna al bollitore con la propria pompa.
        pipe("w2", "sanitaria", ("bollitore", "dhw_out"), ("innesto-ricircolo", "a")),
        pipe("w3", "sanitaria", ("innesto-ricircolo", "b"), ("presa-ricircolo", "a")),
        pipe("w6", "sanitaria", ("presa-ricircolo", "b"), ("utenze", "a")),
        pipe("w7", "sanitaria", ("presa-ricircolo", "c"), ("ricircolo", "a")),
        pipe("w4", "sanitaria", ("ricircolo", "b"), ("ritegno-ricircolo", "a")),
        pipe("w5", "sanitaria", ("ritegno-ricircolo", "b"), ("innesto-ricircolo", "c")),
    ],
    [
        {
            "id": "generazione",
            "name": "Cascata di generazione",
            "component_ids": [
                "pdc-1",
                "pdc-2",
                "pdc-3",
                "cascata-mandata-a",
                "cascata-mandata-b",
                "cascata-ritorno-a",
                "cascata-ritorno-b",
                "deviatrice",
                "ritorno-primario",
            ],
            "network_ids": ["primario"],
        },
        {
            "id": "accumuli",
            "name": "Accumuli",
            "component_ids": ["volano", "bollitore", "acquedotto", "utenze"],
            "network_ids": ["primario", "fredda", "sanitaria"],
        },
        {
            "id": "distribuzione",
            "name": "Circuiti secondari",
            "component_ids": [
                "collettore",
                "circolatore-uta",
                "batteria-uta",
                "circolatore-fancoil",
                "ventilconvettori",
                "ritorno-secondario",
            ],
            "network_ids": ["secondario"],
        },
        {
            "id": "ricircolo",
            "name": "Ricircolo sanitario",
            "component_ids": ["ricircolo", "ritegno-ricircolo", "innesto-ricircolo", "presa-ricircolo"],
            "network_ids": ["sanitaria"],
        },
    ],
    [
        "Il testo elenca **tre** circuiti secondari — batterie UTA, "
        "ventilconvettori e un circuito miscelato per il pavimento radiante. Il "
        "collettore disponibile ne serve due: il circuito miscelato non e' "
        "disegnato, ed e' una domanda per il progettista.",
        "Il ritorno del ricircolo e' innestato sulla mandata sanitaria: il testo "
        "dice solo che il ricircolo e' collegato al bollitore.",
        "La cascata rientra su tre ritorni distinti con due confluenze: il testo "
        "non descrive come le macchine rientrano.",
    ],
)


PLANTS = {
    "prova-1-due-pdc-accumulo-combinato": UNO,
    "prova-2-pdc-deviatrice-acs": DUE,
    "prova-3-pdc-diretta-pavimento": TRE,
    "prova-4-ibrido-pdc-caldaia": QUATTRO,
    "prova-5-cascata-tre-pdc": CINQUE,
}


def main() -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    for name, payload in PLANTS.items():
        path = ROOT / f"{name}.json"
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"scritto {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
