"""Il grafo del caso reale come l'ha disegnato la 1.3.0 nella sessione di lavoro del PO.

    python3 docs/collaudi/REL-009/caso-reale-2/costruisci_grafo.py

Parte dalla prima stesura anonima di `caso-reale-1/` e ci mette le scelte del progettista che
la tavola del PO del 3 ottobre 2026 mostra (I-200 … I-205). La tavola porta i dati del cliente e
non e' nel repository: questo grafo e' **ricostruito** da quello che vi e' disegnato, con nomi
nostri, e non e' il file della sessione di lavoro.

Le scelte:

- su ogni pompa di calore il ritegno sull'uscita, il giunto antivibrante sui due attacchi, lo
  sfiato con valvola a sfera sul ritorno (I-193, I-197); lo sfiato con la sua valvola sui due
  volani. Dal 5 ottobre 2026 sfiato e rubinetto sono un pezzo solo, `air-vent` (I-211);
- i collettori d'appartamento con il ritorno (`zone-manifold-pair`), con le valvole manuali
  sulle due uscite verso i terminali; i ritorni dei terminali entrano nel collettore;
- il volano dell'ACS a sei attacchi, con i due attacchi predisposti «al solare termico»;
- il contatore di calore sul ritorno del primario, al piede del volano grande;
- il riduttore di pressione sull'acqua fredda;
- i collettori, il bollitore, la pompa di ricircolo e le reti sanitarie esistenti.

E quello che il progettista toglie e sposta (`accessori_tolti`), con i nomi che le regole
danno, come la tavola lo mostra: niente termometri, separatori d'aria e defangatori sui
primari (T3, T4); vaso e manometro dei primari sul ritorno dei secondari (T5); niente valvole
sulle uscite dei terminali (T1) ne' sugli attacchi predisposti. Le valvole di sicurezza delle
pompe di calore **restano**: si disegnano sempre (D-202), anche se la tavola del PO non le ha.
"""

import json
from pathlib import Path
from typing import Any

QUI = Path(__file__).resolve().parent
PRIMA = QUI.parent / "caso-reale-1" / "grafo-prima-stesura.json"

GENERATORI = ("pdc-r1", "pdc-r2", "pdc-r3", "pdc-r4", "pdc-a1", "pdc-a2")
RETE_DEL_GENERATORE = {pezzo: "primario-risc" for pezzo in GENERATORI[:4]} | {
    "pdc-a1": "primario-acs",
    "pdc-a2": "primario-acs",
}
APPARTAMENTI = [(1, k) for k in range(1, 4)] + [(2, k) for k in range(1, 6)]


def _tolti() -> list[dict[str, str]]:
    costruito = "sul costruito non c'e'"
    voci = [(f"thermometer-pdc-{n}-water-supply", costruito, None) for n in ("r1", "r2", "r3", "r4", "a1", "a2")]
    voci += [(f"air-separator-{t}", "T3: sul costruito non c'e'", None) for t in ("tj-pr-3-b", "tj-pa-b")]
    voci += [(f"dirt-separator-{t}", "T4: sul costruito non c'e'", None) for t in ("ts-pr-3-a", "ts-pa-a")]
    for pezzo in ("expansion-connection", "pressure-gauge"):
        voci.append((f"{pezzo}-ts-pr-3-a", "T5: sta sul ritorno del secondario", "tj-mz.b"))
        voci.append((f"{pezzo}-ts-pa-a", "T5: sta sul ritorno del secondario", "volano-acs.secondary_in"))
    voci += [
        (f"valve-isolation-{terminale}-mz{zona}-{k}-out", "T1: le valvole stanno sulle uscite del collettore", None)
        for zona, k in APPARTAMENTI
        for terminale in ("fc", "rad")
    ]
    # Le valvole sugli attacchi predisposti le mette la regola del confine, e prendono il
    # nome dal confine. Finche' lo sfiato del volano aveva la sua valvola le metteva la
    # regola del volano, col nome del volano: con lo sfiato col rubinetto (I-211)
    # `completa` le ha dette «tolti che non tolgono niente», e i nomi sono questi.
    voci += [(f"valve-isolation-solare-{lato}-a", costruito, None) for lato in ("mandata", "ritorno")]
    return [
        {"pezzo": pezzo, "motivo": motivo} | ({"altrove": altrove} if altrove else {})
        for pezzo, motivo, altrove in voci
    ]


def _pezzo(ident: str, voce: str, **proprieta: Any) -> dict[str, Any]:
    return {"id": ident, "definition_id": voce, "tag": None, "properties": dict(proprieta)}


def _tubo(ident: str, a: str, b: str, rete: str) -> dict[str, Any]:
    pa, porta_a = a.split(".")
    pb, porta_b = b.split(".")
    return {
        "id": ident,
        "endpoint_a": {"component_id": pa, "port_id": porta_a},
        "endpoint_b": {"component_id": pb, "port_id": porta_b},
        "network_id": rete,
    }


def costruisci() -> dict[str, Any]:
    grafo = json.loads(PRIMA.read_text(encoding="utf-8"))
    grafo["metadata"]["project_id"] = "centrale-pdc-condominio-caso-reale-2"
    grafo["metadata"]["client"] = "Condominio (caso reale, anonimo)"
    pezzi = {item["id"]: item for item in grafo["components"]}
    tubi = {item["id"]: item for item in grafo["connections"]}
    nuovi: list[dict[str, Any]] = []
    numero = iter(range(100, 1000))

    def tubo(a: str, b: str, rete: str) -> None:
        nuovi.append(_tubo(f"t{next(numero)}", a, b, rete))

    def spezza(ident: str, *in_mezzo: tuple[str, str, str]) -> None:
        """La tubazione `ident` passa dentro i pezzi in mezzo: (pezzo, entra, esce)."""
        vecchio = tubi.pop(ident)
        rete = vecchio["network_id"]
        capo = f"{vecchio['endpoint_a']['component_id']}.{vecchio['endpoint_a']['port_id']}"
        for pezzo, entra, esce in in_mezzo:
            tubo(capo, f"{pezzo}.{entra}", rete)
            capo = f"{pezzo}.{esce}"
        tubo(capo, f"{vecchio['endpoint_b']['component_id']}.{vecchio['endpoint_b']['port_id']}", rete)

    def tubo_che_tocca(pezzo: str, porta: str) -> str:
        return next(
            ident
            for ident, item in tubi.items()
            for ref in (item["endpoint_a"], item["endpoint_b"])
            if ref["component_id"] == pezzo and ref["port_id"] == porta
        )

    # Le pompe di calore: ritegno e giunto sulla mandata, giunto e sfiato sul ritorno. Lo
    # sfiato porta il suo rubinetto (I-211): la valvola sullo stacco non si scrive.
    for pdc in GENERATORI:
        rete = RETE_DEL_GENERATORE[pdc]
        n = pdc.removeprefix("pdc-")
        pezzi[f"ritegno-{n}"] = _pezzo(f"ritegno-{n}", "valve-check")
        pezzi[f"giunto-mandata-{n}"] = _pezzo(f"giunto-mandata-{n}", "flexible-joint")
        pezzi[f"giunto-ritorno-{n}"] = _pezzo(f"giunto-ritorno-{n}", "flexible-joint")
        pezzi[f"tee-sfiato-{n}"] = _pezzo(f"tee-sfiato-{n}", "tee-branch")
        pezzi[f"sfiato-{n}"] = _pezzo(f"sfiato-{n}", "air-vent")
        mandata = tubo_che_tocca(pdc, "water_supply")
        spezza(mandata, (f"ritegno-{n}", "a", "b"), (f"giunto-mandata-{n}", "a", "b"))
        ritorno = tubo_che_tocca(pdc, "water_return")
        spezza(ritorno, (f"giunto-ritorno-{n}", "a", "b"), (f"tee-sfiato-{n}", "a", "b"))
        tubo(f"tee-sfiato-{n}.branch", f"sfiato-{n}.a", rete)

    # Lo sfiato, col suo rubinetto, sull'attacco di sfiato dei due volani.
    for volano, rete in (("volano-risc", "primario-risc"), ("volano-acs", "primario-acs")):
        pezzi[f"sfiato-{volano}"] = _pezzo(f"sfiato-{volano}", "air-vent")
        tubo(f"{volano}.vent", f"sfiato-{volano}.a", rete)

    # Il contatore di calore sul ritorno del primario, al piede del volano grande.
    pezzi["contatore"] = _pezzo("contatore", "heat-meter", servizio="contabilizzatore sul ritorno del primario")
    spezza("t008", ("contatore", "a", "b"))

    # I collettori d'appartamento con il ritorno; le valvole manuali sulle due uscite.
    for zona, k in APPARTAMENTI:
        c, fc, rad, rit = (f"{voce}-mz{zona}-{k}" for voce in ("coll", "fc", "rad", "rit"))
        pezzi[c]["definition_id"] = "zone-manifold-pair"
        pezzi[c]["esistente"] = True
        valle = next(
            ident for ident, item in tubi.items()
            if item["endpoint_a"]["component_id"] == rit and item["endpoint_a"]["port_id"] == "b"
        )
        confluenza = tubi.pop(valle)
        for ident in [i for i, item in tubi.items() if rit in (item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"])]:
            tubi.pop(ident)
        del pezzi[rit]
        for uscita, terminale, ritorno in (("out_1", fc, "ret_1"), ("out_2", rad, "ret_2")):
            valvola = f"valvola-{uscita.replace('_', '')}-mz{zona}-{k}"
            pezzi[valvola] = _pezzo(valvola, "valve-isolation")
            spezza(tubo_che_tocca(c, uscita), (valvola, "a", "b"))
            tubo(f"{terminale}.out", f"{c}.{ritorno}", "secondario-risc")
        arrivo = confluenza["endpoint_b"]
        tubo(f"{c}.out", f"{arrivo['component_id']}.{arrivo['port_id']}", "secondario-risc")

    # Il volano dell'ACS a sei attacchi, con i due predisposti per il solare termico.
    pezzi["volano-acs"]["definition_id"] = "buffer-six-port"
    pezzi["solare-mandata"] = _pezzo("solare-mandata", "capped-connection", etichetta="al solare termico")
    pezzi["solare-ritorno"] = _pezzo("solare-ritorno", "capped-connection")
    grafo["networks"].append(
        {"id": "predisposizione", "name": "Attacchi predisposti per il solare termico", "domain": "hydronic", "medium": "heating_water"}
    )
    tubo("solare-mandata.a", "volano-acs.aux_in", "predisposizione")
    tubo("volano-acs.aux_out", "solare-ritorno.a", "predisposizione")

    # Il riduttore di pressione sull'acqua fredda; le parti sanitarie esistenti.
    pezzi["riduttore"] = _pezzo("riduttore", "pressure-reducer")
    spezza("t088", ("riduttore", "a", "b"))
    for esistente in ("bollitore", "pompa-ricircolo"):
        pezzi[esistente]["esistente"] = True

    grafo["accessori_tolti"] = _tolti()
    grafo["components"] = list(pezzi.values())
    grafo["connections"] = list(tubi.values()) + nuovi
    grafo["assumptions"] = [
        item for item in grafo["assumptions"]
        if item["id"] not in ("a-contabilizzatore", "a-predisposizione-solare", "a-ferramenta-foto", "a-trattamento-acqua")
    ] + [
        {
            "id": "a-ricostruzione",
            "text": (
                "Ricostruito dalla tavola del caso fatta con la 1.3.0 nella sessione di lavoro del PO "
                "(3 ottobre 2026, I-200 … I-205): stessi pezzi e stesse scelte, nomi nostri, senza i dati del cliente."
            ),
            "status": "approved",
        }
    ]
    return grafo


if __name__ == "__main__":
    uscita = QUI / "grafo-prima-stesura.json"
    uscita.write_text(json.dumps(costruisci(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(uscita)
