"""I due grafi di prova del blocco A di REL-026 (I-300): casi anonimi, scritti apposta.

    python docs/collaudi/REL-026/blocco-a/fai-i-grafi.py

- `grafo-plenum-di-mandata.json` — una pompa di calore idronica e tre ventilconvettori
  canalizzati col lato aria (`fan-coil-ducted-air`), ognuno col suo plenum di mandata non
  motorizzato: a due, a tre e a sei uscite (`supply-plenum-2/3/6`), le bocchette, la ripresa,
  la condensa con il sifone, il quadro e un termostato per ventilconvettore sul consenso.
  Due ventilconvettori hanno marca e modello (A-4: entrano in tabella), il terzo no.
- `grafo-plenum-motorizzato.json` — la richiesta del PO del 13 novembre 2026: lo stesso
  ventilconvettore col plenum **motorizzato** di zona che c'e' gia' (`zoning-plenum-4`, PLZ),
  la sua centrale di zona e i termostati sul bus della centrale, come nell'aria-aria AA-01.

Nessun dato di commessa: nomi, indirizzo e codici sono di prova.
"""

import json
from pathlib import Path
from typing import Any

QUI = Path(__file__).resolve().parent


def metadati(project_id: str, nome: str, codice: str, numero: str) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "client": "Committente (dati omessi)",
        "project_name": nome,
        "commission_code": codice,
        "revision": "00",
        "issue_date": "2026-11-13",
        "address": "Indirizzo omesso",
        "sheet_title": "Schema funzionale — ventilconvettori canalizzati idronici",
        "sheet_number": numero,
        "drawn_by": "Nove C",
        "header_note": "Caso di prova REL-026",
    }


def rete(ident: str, nome: str, dominio: str, fluido: str) -> dict[str, Any]:
    return {"id": ident, "name": nome, "domain": dominio, "medium": fluido}


def pezzo(ident: str, voce: str, **proprieta: Any) -> dict[str, Any]:
    return {"id": ident, "definition_id": voce, "properties": proprieta}


def tubo(ident: str, rete_id: str, a: str, b: str, **dati: Any) -> dict[str, Any]:
    (pa, qa), (pb, qb) = a.split("."), b.split(".")
    voce: dict[str, Any] = {
        "id": ident,
        "network_id": rete_id,
        "endpoint_a": {"component_id": pa, "port_id": qa},
        "endpoint_b": {"component_id": pb, "port_id": qb},
    }
    for chiave in ("sezione", "lunghezza_m", "scritta"):
        if chiave in dati:
            voce[chiave] = dati.pop(chiave)
    voce["properties"] = dati
    return voce


def lato_aria(n: int, stanze: list[str], reti: list[dict[str, Any]], pezzi: list[dict[str, Any]],
              tubi: list[dict[str, Any]], plenum: str | None) -> None:
    """Il lato aria del ventilconvettore `fc-n`: la mandata al plenum (se c'e') e alle
    bocchette, la ripresa, la condensa col sifone."""
    fc = f"fc-{n}"
    reti += [
        rete(f"mandata-aria-{n}", f"Mandata aria {n}", "aeraulic", "supply_air"),
        rete(f"ripresa-aria-{n}", f"Ripresa aria {n}", "aeraulic", "return_air"),
        rete(f"condensa-{n}", f"Scarico condensa {n}", "condensate", "condensate"),
    ]
    pezzi += [
        pezzo(f"ra-{n}", "return-air-terminal", etichetta="ripresa con filtro"),
        pezzo(f"sif-{n}", "condensate-trap"),
        pezzo(f"sc-{n}", "condensate-outlet", etichetta="allaccio allo scarico"),
    ]
    tubi += [
        tubo(f"rip-{n}", f"ripresa-aria-{n}", f"ra-{n}.a", f"{fc}.return", lunghezza_m=0),
        tubo(f"cd-{n}a", f"condensa-{n}", f"{fc}.drain", f"sif-{n}.a", sezione="Ø32", lunghezza_m=3),
        tubo(f"cd-{n}b", f"condensa-{n}", f"sif-{n}.b", f"sc-{n}.a"),
    ]
    if plenum is not None:
        tubi.append(tubo(f"ma-{n}", f"mandata-aria-{n}", f"{fc}.supply", f"{plenum}.in", lunghezza_m=0))
    for k, stanza in enumerate(stanze, start=1):
        bocchetta = f"b-{n}-{k}"
        pezzi.append(pezzo(bocchetta, "air-supply-terminal", etichetta=stanza, dimensione="300×150"))
        tubi.append(
            tubo(f"ma-{n}-{k}", f"mandata-aria-{n}", f"{plenum}.out_{k}", f"{bocchetta}.a",
                 sezione="Ø160", lunghezza_m=float(2 + k))
        )


def grafo_plenum_di_mandata() -> dict[str, Any]:
    reti = [rete("impianto", "Circuito dei ventilconvettori", "hydronic", "heating_water")]
    pezzi = [
        pezzo("pdc", "heat-pump-air-water", power_kw=9, delta_t_k=5, tipo="monoblocco, all'esterno",
              volume_minimo="verificato"),
        pezzo("rip-m1", "tee-split"),
        pezzo("rip-m2", "tee-split"),
        pezzo("conf-r1", "tee-junction"),
        pezzo("conf-r2", "tee-junction"),
        pezzo("fc-1", "fan-coil-ducted-air", marca="Marca di prova", modello="FCC-30 di prova", power_kw=3,
              delta_t_k=5, etichetta="zona notte"),
        pezzo("fc-2", "fan-coil-ducted-air", marca="Marca di prova", modello="FCC-30 di prova", power_kw=3,
              delta_t_k=5, etichetta="zona studio"),
        pezzo("fc-3", "fan-coil-ducted-air", power_kw=3, delta_t_k=5, etichetta="zona giorno"),
        pezzo("pl-1", "supply-plenum-2"),
        pezzo("pl-2", "supply-plenum-3"),
        pezzo("pl-3", "supply-plenum-6"),
        pezzo("quadro", "electrical-panel", etichetta="quadro elettrico esistente"),
        *(pezzo(f"tz-{n}", "room-thermostat", etichetta=f"zona {n}") for n in (1, 2, 3)),
    ]
    # La distribuzione: le utenze nell'ordine dei numeri, il ritorno che specchia la mandata
    # (capire.md §4.4).
    tubi = [
        tubo("m1", "impianto", "pdc.water_supply", "rip-m1.a", lunghezza_m=6),
        tubo("m2", "impianto", "rip-m1.c", "fc-1.in", lunghezza_m=4),
        tubo("m3", "impianto", "rip-m1.b", "rip-m2.a", lunghezza_m=3),
        tubo("m4", "impianto", "rip-m2.c", "fc-2.in", lunghezza_m=4),
        tubo("m5", "impianto", "rip-m2.b", "fc-3.in", lunghezza_m=5),
        tubo("r5", "impianto", "fc-3.out", "conf-r2.c", lunghezza_m=5),
        tubo("r4", "impianto", "fc-2.out", "conf-r2.a", lunghezza_m=4),
        tubo("r3", "impianto", "conf-r2.b", "conf-r1.c", lunghezza_m=3),
        tubo("r2", "impianto", "fc-1.out", "conf-r1.a", lunghezza_m=4),
        tubo("r1", "impianto", "conf-r1.b", "pdc.water_return", lunghezza_m=6),
    ]
    lato_aria(1, ["Camera 1", "Camera 2"], reti, pezzi, tubi, "pl-1")
    lato_aria(2, ["Studio", "Bagno", "Disimpegno"], reti, pezzi, tubi, "pl-2")
    lato_aria(3, ["Soggiorno 1", "Soggiorno 2", "Cucina", "Pranzo", "Ingresso", "Corridoio"], reti, pezzi, tubi,
              "pl-3")
    reti += [
        rete("linea-pdc", "Alimentazione pompa di calore", "control", "power_supply"),
        *(rete(f"linea-fc-{n}", f"Alimentazione ventilconvettore {n}", "control", "power_supply") for n in (1, 2, 3)),
        *(rete(f"consenso-{n}", f"Consenso del termostato {n}", "control", "control_bus") for n in (1, 2, 3)),
    ]
    tubi += [
        tubo("e-pdc", "linea-pdc", "quadro.out_1", "pdc.power", sezione="3G2,5", lunghezza_m=12),
        *(tubo(f"e-fc-{n}", f"linea-fc-{n}", f"quadro.out_{n + 1}", f"fc-{n}.power", sezione="3G1,5",
               lunghezza_m=8.0 + n) for n in (1, 2, 3)),
        *(tubo(f"b-tz-{n}", f"consenso-{n}", f"tz-{n}.a", f"fc-{n}.consenso_in", sezione="2×0,75",
               lunghezza_m=6) for n in (1, 2, 3)),
    ]
    return {
        "schema_version": "1.1.0",
        "metadata": metadati("rel026-canalizzati-plenum-di-mandata",
                             "Tre ventilconvettori canalizzati idronici con plenum di mandata", "PROVA-A", "M.01"),
        "plant_regime": "up_to_35_kw",
        "diametri": {"reti": ["impianto"]},
        "networks": reti,
        "components": pezzi,
        "connections": tubi,
        "assumptions": [
            {
                "id": "a1",
                "text": "Caso di prova anonimo: la distribuzione ai tre ventilconvettori e' scritta con le "
                        "ripartizioni e le confluenze a T, il ritorno che specchia la mandata. Il volume minimo "
                        "della pompa di calore e' dichiarato verificato: il caso non porta il volano.",
                "status": "approved",
            }
        ],
        "rule_applications": [],
        "subsystems": [],
        "sheets": [],
    }


def grafo_plenum_motorizzato() -> dict[str, Any]:
    reti = [rete("impianto", "Circuito del ventilconvettore", "hydronic", "heating_water")]
    pezzi = [
        pezzo("pdc", "heat-pump-air-water", power_kw=5, delta_t_k=5, tipo="monoblocco, all'esterno",
              volume_minimo="verificato"),
        pezzo("fc-1", "fan-coil-ducted-air", marca="Marca di prova", modello="FCC-50 di prova", power_kw=5,
              delta_t_k=5),
        pezzo("plz-1", "zoning-plenum-4", marca="Marca di prova", modello="plenum motorizzato a 4 serrande"),
        pezzo("centrale", "zone-controller", marca="Marca di prova", modello="centrale di zona",
              compreso_in="plz-1"),
        pezzo("quadro", "electrical-panel", etichetta="quadro elettrico esistente"),
        *(pezzo(f"tz-{n}", "room-thermostat", etichetta=f"Z{n}") for n in (1, 2, 3, 4)),
    ]
    tubi = [
        tubo("m1", "impianto", "pdc.water_supply", "fc-1.in", lunghezza_m=8),
        tubo("r1", "impianto", "fc-1.out", "pdc.water_return", lunghezza_m=8),
    ]
    lato_aria(1, ["Camera 1", "Camera 2", "Soggiorno", "Studio"], reti, pezzi, tubi, "plz-1")
    reti += [
        rete("linea-pdc", "Alimentazione pompa di calore", "control", "power_supply"),
        rete("linea-fc-1", "Alimentazione ventilconvettore", "control", "power_supply"),
        rete("linea-centrale", "Alimentazione centrale di zona", "control", "power_supply"),
        rete("serrande", "Comando motori serrande", "control", "control_bus"),
        rete("bus-zona", "Bus della centrale ai termostati", "control", "control_bus"),
        rete("bus-fc", "Collegamento centrale-ventilconvettore", "control", "control_bus"),
    ]
    tubi += [
        tubo("e-pdc", "linea-pdc", "quadro.out_1", "pdc.power", sezione="3G2,5", lunghezza_m=12),
        tubo("e-fc-1", "linea-fc-1", "quadro.out_2", "fc-1.power", sezione="3G1,5", lunghezza_m=9),
        tubo("e-centrale", "linea-centrale", "quadro.out_3", "centrale.power", sezione="3G1,5", lunghezza_m=9),
        tubo("e-serrande", "serrande", "plz-1.motori", "centrale.serrande", scritta="di fabbrica", lunghezza_m=0),
        # La centrale di zona del catalogo parla con la macchina dalla porta `p1p2`, la linea P1-P2
        # delle unita' interne ad espansione diretta (AA-01). Il ventilconvettore idronico la
        # linea P1-P2 non ce l'ha: qui va sul suo bus, ed e' un rilievo del rapporto (REL-026).
        tubo("b-fc", "bus-fc", "centrale.p1p2", "fc-1.bus", sezione="bus", lunghezza_m=2),
        *(tubo(f"b-tz-{n}", "bus-zona", f"centrale.bus_{n}", f"tz-{n}.a", sezione="bus", lunghezza_m=6)
          for n in (1, 2, 3, 4)),
    ]
    return {
        "schema_version": "1.1.0",
        "metadata": metadati("rel026-canalizzato-plenum-motorizzato",
                             "Ventilconvettore canalizzato idronico con plenum motorizzato di zona", "PROVA-B",
                             "M.02"),
        "plant_regime": "up_to_35_kw",
        "diametri": {"reti": ["impianto"]},
        "networks": reti,
        "components": pezzi,
        "connections": tubi,
        "assumptions": [
            {
                "id": "a1",
                "text": "La centrale di zona del catalogo ha la sola porta P1-P2 verso la macchina, quella delle "
                        "unita' interne ad espansione diretta: col ventilconvettore idronico il collegamento e' "
                        "scritto sul bus del ventilconvettore, da confermare col progettista.",
                "status": "proposed",
            }
        ],
        "rule_applications": [],
        "subsystems": [],
        "sheets": [],
    }


def main() -> None:
    for nome, grafo in (
        ("grafo-plenum-di-mandata.json", grafo_plenum_di_mandata()),
        ("grafo-plenum-motorizzato.json", grafo_plenum_motorizzato()),
    ):
        (QUI / nome).write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"scritto {nome}")


if __name__ == "__main__":
    main()
