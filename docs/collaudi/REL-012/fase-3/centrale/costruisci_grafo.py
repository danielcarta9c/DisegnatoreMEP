"""Il grafo della centrale di prova di REL-012 fase 3: l'impianto 2 con l'elettrico e il comando.

    python3 docs/collaudi/REL-012/fase-3/centrale/costruisci_grafo.py

Parte dal grafo di prima stesura dell'impianto 2 delle prove
(`examples/prova/prova-2-pdc-deviatrice-acs.json`: pompa di calore, deviatrice fra volano e
bollitore, circolatore e ventilconvettori) e aggiunge, **tutto proposta della sessione**:

- due sonde a immersione, di mandata e di ritorno del secondario, appese a due derivazioni;
- il quadro, che alimenta la pompa di calore attraverso il sezionatore di prossimita' e
  alimenta il regolatore;
- il regolatore, che parla con la pompa di calore sul bus, comanda la deviatrice e accende il
  circolatore con due delle sue uscite, e legge le sonde di mandata, di ritorno ed esterna.

Il circolatore e' alimentato dal regolatore, non dal quadro: il quadro della libreria ha due
uscite (la pompa di calore e il regolatore), e il circolatore lo accende chi lo comanda. Le
sezioni e le lunghezze dei cavi sono dati di prova, come li scriverebbe il progettista: la
skill non dimensiona (I-225).
"""

import json
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[4]


def ref(component_id: str, port_id: str) -> dict[str, str]:
    return {"component_id": component_id, "port_id": port_id}


def main() -> None:
    grafo = json.loads((RADICE / "examples/prova/prova-2-pdc-deviatrice-acs.json").read_text("utf-8"))
    grafo["metadata"].update(
        {
            "project_id": "prova-rel012-fase-3-centrale",
            "client": "Prova del motore (nessun cliente)",
            "project_name": "Prova REL-012 fase 3: la centrale dell'impianto 2 con elettrico e comando",
            "commission_code": "REL-012",
            "issue_date": "2026-10-29",
            "sheet_title": "Centrale termica",
            "sheet_number": "P.04",
            "drawn_by": "Claude",
            "header_note": "Tavola di prova del motore, non un progetto",
        }
    )
    grafo["networks"] += [
        {"id": "alimentazione", "name": "Alimentazione dal quadro", "domain": "control", "medium": "power_supply"},
        {"id": "comandi", "name": "Comandi del regolatore", "domain": "control", "medium": "power_supply"},
        {"id": "bus", "name": "Bus della pompa di calore", "domain": "control", "medium": "control_bus"},
        {"id": "sonde", "name": "Sonde", "domain": "control", "medium": "control_bus"},
    ]
    grafo["components"] += [
        {"id": "tee-sonda-mandata", "definition_id": "tee-branch", "properties": {}},
        {"id": "sonda-mandata", "definition_id": "temperature-probe", "tag": "SO-01", "properties": {"etichetta": "mandata"}},
        {"id": "tee-sonda-ritorno", "definition_id": "tee-branch", "properties": {}},
        {"id": "sonda-ritorno", "definition_id": "temperature-probe", "tag": "SO-02", "properties": {"etichetta": "ritorno"}},
        {"id": "sonda-esterna", "definition_id": "outdoor-temperature-probe", "tag": "SE-01", "properties": {}},
        {"id": "quadro", "definition_id": "electrical-panel", "tag": "QE-01", "properties": {}},
        {"id": "sezionatore-pdc", "definition_id": "isolator-switch", "properties": {}},
        {
            "id": "regolatore",
            "definition_id": "plant-controller",
            "tag": "RG-01",
            "properties": {"marca": "Marca di prova", "modello": "PRV-RG"},
        },
    ]
    tubazioni = []
    for tubazione in grafo["connections"]:
        if tubazione["id"] == "s2":
            # La mandata del secondario passa dalla derivazione della sua sonda.
            tubazioni += [
                {"id": "s2", "network_id": "secondario", "endpoint_a": ref("circolatore", "b"), "endpoint_b": ref("tee-sonda-mandata", "a")},
                {"id": "s2b", "network_id": "secondario", "endpoint_a": ref("tee-sonda-mandata", "b"), "endpoint_b": ref("ventilconvettori", "in")},
                {"id": "s2s", "network_id": "secondario", "endpoint_a": ref("tee-sonda-mandata", "branch"), "endpoint_b": ref("sonda-mandata", "a")},
            ]
        elif tubazione["id"] == "s3":
            # E il ritorno da quella della sua.
            tubazioni += [
                {"id": "s3", "network_id": "secondario", "endpoint_a": ref("ventilconvettori", "out"), "endpoint_b": ref("tee-sonda-ritorno", "a")},
                {"id": "s3b", "network_id": "secondario", "endpoint_a": ref("tee-sonda-ritorno", "b"), "endpoint_b": ref("volano", "secondary_in")},
                {"id": "s3s", "network_id": "secondario", "endpoint_a": ref("tee-sonda-ritorno", "branch"), "endpoint_b": ref("sonda-ritorno", "a")},
            ]
        else:
            tubazioni.append(tubazione)
    grafo["connections"] = tubazioni + [
        {"id": "e1", "network_id": "alimentazione", "endpoint_a": ref("quadro", "out_2"), "endpoint_b": ref("sezionatore-pdc", "a"), "sezione": "5G4", "lunghezza_m": 15},
        {"id": "e2", "network_id": "alimentazione", "endpoint_a": ref("sezionatore-pdc", "b"), "endpoint_b": ref("pdc", "power"), "sezione": "5G4", "lunghezza_m": 1.5},
        {"id": "e3", "network_id": "alimentazione", "endpoint_a": ref("quadro", "out_1"), "endpoint_b": ref("regolatore", "power"), "sezione": "3G1,5", "lunghezza_m": 3},
        {"id": "c1", "network_id": "comandi", "endpoint_a": ref("regolatore", "out_1"), "endpoint_b": ref("deviatrice", "comando"), "sezione": "4G1", "lunghezza_m": 4},
        {"id": "c2", "network_id": "comandi", "endpoint_a": ref("regolatore", "out_3"), "endpoint_b": ref("circolatore", "power"), "sezione": "3G1,5", "lunghezza_m": 4},
        {"id": "b1", "network_id": "bus", "endpoint_a": ref("regolatore", "bus"), "endpoint_b": ref("pdc", "bus"), "sezione": "2x0,75 schermato", "lunghezza_m": 15},
        {"id": "t1", "network_id": "sonde", "endpoint_a": ref("sonda-mandata", "signal"), "endpoint_b": ref("regolatore", "probe_1"), "sezione": "2x0,75", "lunghezza_m": 4},
        {"id": "t2", "network_id": "sonde", "endpoint_a": ref("sonda-ritorno", "signal"), "endpoint_b": ref("regolatore", "probe_3"), "sezione": "2x0,75", "lunghezza_m": 4},
        {"id": "t3", "network_id": "sonde", "endpoint_a": ref("sonda-esterna", "a"), "endpoint_b": ref("regolatore", "probe_2"), "sezione": "2x0,75", "lunghezza_m": 20},
    ]
    (QUI / "grafo-prima-stesura.json").write_text(
        json.dumps(grafo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
