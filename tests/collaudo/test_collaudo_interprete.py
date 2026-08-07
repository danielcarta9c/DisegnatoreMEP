"""Collaudo indipendente del pezzo «Capire» — la prova in camera pulita del 7 agosto 2026.

Scritte da zero da un collaudatore a contesto separato: non ha scritto le istruzioni
(`skill/capire/ISTRUZIONI.md`) e non ha prodotto i grafi che giudica
(`skill/capire/prova-2026-08-07/impianto-1..5/grafo.json`).

Cosa misurano queste prove, in ordine:

1. **Che i grafi stiano in piedi da soli**: caricano, non contengono ferramenta, non
   mettono due tubi su un attacco, vanno da una porta che esce a una che entra, non
   toccano gli attacchi di servizio, non lasciano scoperto nessun attacco obbligatorio.
2. **Che dicano quello che il testo dice**: le potenze e i volumi scritti
   dall'ingegnere si ritrovano nel grafo, il regime e' *ricavato* dalle potenze e non
   chiesto, le esclusioni esplicite e la logica di regolazione sono voci dichiarate,
   i raccordi sono esattamente N-1 in ogni punto d'incontro descritto.
3. **Che non aggiungano niente**: ogni pezzo che non e' un raccordo o un confine
   risale a una parola del testo del committente.
4. **Che combacino con il metro**: la lettura manuale congelata in `examples/prova/`,
   confrontata sulle reti, sui componenti e sulle tubazioni — sigle e sottosistemi
   restano fuori per costruzione, come impone `skill/capire/CONSEGNA.md` §2.
5. **Che il seguito della catena li digerisca**, e in modo deterministico.

L'unico difetto trovato e' inchiodato in fondo con `xfail(strict=True)`.
"""

import importlib.util
import json
import re
from collections import Counter, defaultdict
from typing import Any

import pytest
from helpers import ROOT, catalog, naming, permuted, rules

from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.rules.apply import saturate

PROVA = ROOT / "skill" / "capire" / "prova-2026-08-07"
METRO = ROOT / "examples" / "prova"
TESTO = METRO / "input" / "2026-08-06-impianti-di-prova.txt"
CATALOGO = ROOT / "examples" / "layout" / "catalog"

IMPIANTI = (1, 2, 3, 4, 5)

LETTURA_MANUALE = {
    1: "prova-1-due-pdc-accumulo-combinato.json",
    2: "prova-2-pdc-deviatrice-acs.json",
    3: "prova-3-pdc-diretta-pavimento.json",
    4: "prova-4-ibrido-pdc-caldaia.json",
    5: "prova-5-cascata-tre-pdc.json",
}

FERRAMENTA = frozenset(
    {
        "isolation",
        "isolation_locked_open",
        "non_return",
        "safety",
        "expansion",
        "filtration",
        "sludge_separation",
        "air_release",
        "filling",
        "drain",
        "pressure_control",
        "pressure_measurement",
        "temperature_measurement",
        "dhw_mixing",
    }
)
"""I mestieri che ISTRUZIONI.md §5 vieta alla prima stesura."""

AMMESSI = frozenset(
    {
        "heat_generation",
        "thermal_storage",
        "dhw_storage",
        "hydraulic_separation",
        "heat_exchange",
        "circulation",
        "distribution",
        "emission",
        "diversion",
        "circuit_mixing",
        "junction",
        "branch_off",
        "boundary",
    }
)
"""I mestieri che ISTRUZIONI.md §5 ammette alla prima stesura."""


Json = dict[str, Any]
Arco = tuple[str, str, str, str, str]


# --------------------------------------------------------------------------- attrezzi


def voci_di_catalogo() -> dict[str, Json]:
    return {json.loads(p.read_text())["id"]: json.loads(p.read_text()) for p in CATALOGO.glob("*.json")}


CAT = voci_di_catalogo()


def grafo(n: int) -> Json:
    dati: Json = json.loads((PROVA / f"impianto-{n}" / "grafo.json").read_text())
    return dati


def metro(n: int) -> Json:
    dati: Json = json.loads((METRO / LETTURA_MANUALE[n]).read_text())
    return dati


def frasi_dell_impianto(n: int) -> str:
    """Il solo testo del committente per l'impianto n, dal file originale."""
    pezzi = re.split(r"\n## Esempio \d+", TESTO.read_text())
    return pezzi[n].lower().replace("’", "'")


def porte(definition_id: str) -> dict[str, Json]:
    return {p["id"]: p for p in CAT[definition_id]["ports"]}


def mestieri(definition_id: str) -> set[str]:
    return set(CAT[definition_id]["functions"])


def attacchi_usati(d: Json) -> Counter[tuple[str, str]]:
    usati: Counter[tuple[str, str]] = Counter()
    for c in d["connections"]:
        for lato in ("endpoint_a", "endpoint_b"):
            usati[(c[lato]["component_id"], c[lato]["port_id"])] += 1
    return usati


def assunzioni(d: Json) -> str:
    """Tutte le voci dichiarate, in un testo solo, minuscolo e senza accenti."""
    grezzo = " ".join(a["text"] for a in d["assumptions"]).lower()
    return grezzo.replace("'", "'").replace("è", "e").replace("à", "a").replace("ò", "o")


# ------------------------------------------- 1. i grafi stanno in piedi da soli


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_grafo_carica(n: int) -> None:
    """Un file che non carica non e' una consegna (CONSEGNA.md §1)."""
    load_project(PROVA / f"impianto-{n}" / "grafo.json")


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessun_pezzo_di_ferramenta(n: int) -> None:
    """§5: la ferramenta la aggiunge il pezzo delle regole, non l'interprete."""
    colpevoli = [
        (c["id"], c["definition_id"], sorted(mestieri(c["definition_id"]) & FERRAMENTA))
        for c in grafo(n)["components"]
        if mestieri(c["definition_id"]) & FERRAMENTA
    ]
    assert colpevoli == [], f"pezzi di ferramenta nel grafo {n}: {colpevoli}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_ogni_pezzo_ha_un_mestiere_ammesso(n: int) -> None:
    fuori = [
        (c["id"], c["definition_id"])
        for c in grafo(n)["components"]
        if not (mestieri(c["definition_id"]) & AMMESSI)
    ]
    assert fuori == [], f"pezzi con mestiere non ammesso nel grafo {n}: {fuori}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_un_attacco_porta_una_tubazione_sola(n: int) -> None:
    """§4.3, prima regola dura."""
    doppi = [k for k, v in attacchi_usati(grafo(n)).items() if v > 1]
    assert doppi == [], f"attacchi con due tubazioni nel grafo {n}: {doppi}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_verso_fluido_e_attacchi_di_ogni_tubazione(n: int) -> None:
    """§4.3: da porta che esce a porta che entra, stesso fluido, mai uno stub."""
    d = grafo(n)
    reti = {x["id"]: x for x in d["networks"]}
    comps = {c["id"]: c for c in d["components"]}
    guai: list[str] = []
    for c in d["connections"]:
        rete = reti[c["network_id"]]
        for lato, verso in (("endpoint_a", "out"), ("endpoint_b", "in")):
            ep = c[lato]
            definizione = comps[ep["component_id"]]["definition_id"]
            porta = porte(definizione).get(ep["port_id"])
            if porta is None:
                guai.append(f"{c['id']}: attacco inventato {definizione}.{ep['port_id']}")
                continue
            if porta.get("stub"):
                guai.append(f"{c['id']}: tocca un attacco di servizio {ep['component_id']}.{ep['port_id']}")
            if porta["flow"] not in (verso, "bidirectional"):
                guai.append(f"{c['id']}: verso sbagliato su {ep['component_id']}.{ep['port_id']}")
            if porta["medium"] != rete["medium"]:
                guai.append(
                    f"{c['id']}: la rete porta {rete['medium']} e l'attacco "
                    f"{ep['component_id']}.{ep['port_id']} porta {porta['medium']}"
                )
    assert guai == [], f"grafo {n}: {guai}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessun_attacco_obbligatorio_resta_scoperto(n: int) -> None:
    """§4.3 in coda: un obbligatorio libero e' un collegamento descritto e perso."""
    d = grafo(n)
    usati = attacchi_usati(d)
    scoperti = [
        f"{c['id']}.{p['id']}"
        for c in d["components"]
        for p in CAT[c["definition_id"]]["ports"]
        if p.get("required") and not p.get("stub") and usati[(c["id"], p["id"])] == 0
    ]
    assert scoperti == [], f"grafo {n}: attacchi obbligatori scoperti {scoperti}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_forma_del_file(n: int) -> None:
    """§3 e §9: versione, sigle non inventate, liste dei pezzi successivi vuote."""
    d = grafo(n)
    assert d["schema_version"] == "1.1.0"
    sigle = [c["id"] for c in d["components"] if c["tag"] is not None]
    assert sigle == [], f"grafo {n}: sigle inventate su {sigle}"
    assert d["subsystems"] == []
    assert d["rule_applications"] == []
    assert d["sheets"] == []
    assert all(a["status"] == "proposed" for a in d["assumptions"])


# --------------------------------------- 2. il grafo dice quello che il testo dice


REGIME_ATTESO = {
    1: ("up_to_35_kw", "12 + 12 = 24 kW"),
    2: ("up_to_35_kw", "15 kW"),
    3: ("up_to_35_kw", "8 kW, unica potenza scritta"),
    4: ("up_to_35_kw", "10 + 24 = 34 kW"),
    5: ("over_35_kw", "35 + 35 + 35 = 105 kW"),
}


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_regime_e_ricavato_e_non_chiesto(n: int) -> None:
    """§4.6 e D-108: le potenze ci sono, quindi il regime si ricava, non si chiede."""
    d = grafo(n)
    atteso, conto = REGIME_ATTESO[n]
    assert d.get("plant_regime") == atteso, f"grafo {n}: il regime doveva uscire da {conto}"
    testo_voci = assunzioni(d)
    assert "sotto o sopra i 35 kw" not in testo_voci, (
        f"grafo {n}: il regime e' stato chiesto invece che ricavato"
    )
    assert "non e' stato ricavato" not in testo_voci


DATI_DEL_TESTO = {
    1: ["12 kW", "12 kW", "200 litri", "ECOcombi"],
    2: ["15 kW", "100 litri"],
    3: ["8 kW", "50 litri", "200 litri"],
    4: ["10 kW", "24 kW", "150 litri"],
    5: ["35 kW", "35 kW", "35 kW", "500 litri", "500 litri"],
}


@pytest.mark.parametrize("n", IMPIANTI)
def test_i_dati_scritti_dall_ingegnere_sono_trascritti(n: int) -> None:
    """§4.5: potenze, volumi e nomi commerciali detti dal testo finiscono in properties."""
    valori: Counter[str] = Counter()
    for c in grafo(n)["components"]:
        valori.update(str(v) for v in c["properties"].values())
    mancanti = Counter(DATI_DEL_TESTO[n]) - valori
    assert not mancanti, f"grafo {n}: dati del testo non trascritti {dict(mancanti)}"


ESCLUSIONI = {
    1: ["ricircolo"],
    2: ["ricircolo"],
    3: ["separatore idraulico", "non collegato idraulicamente"],
    4: ["bollitore"],
    5: [],
}
NOMINE_DI_FERRAMENTA = {
    1: ["carico automatico", "scarico"],
    2: ["carico automatico", "scarico", "miscelatrice"],
    3: ["carico automatico", "scarico"],
    4: ["carico automatico", "scarico"],
    5: ["miscelatrice termostatica"],
}
REGOLAZIONE = {
    1: ["master"],
    2: ["priorita"],
    3: ["regolazione di zona"],
    4: ["priorita", "temperatura esterna"],
    5: ["cascata", "priorita"],
}


@pytest.mark.parametrize("n", IMPIANTI)
def test_le_esclusioni_esplicite_sono_dichiarate(n: int) -> None:
    """§4.5: «non e' previsto X» e' informazione, e va in una voce dichiarata."""
    voci = assunzioni(grafo(n))
    persi = [k for k in ESCLUSIONI[n] if k not in voci]
    assert persi == [], f"grafo {n}: esclusioni del testo non dichiarate {persi}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_le_nomine_di_ferramenta_non_vanno_perse(n: int) -> None:
    """§5: la ferramenta resta fuori dal grafo, ma la nomina resta dichiarata."""
    voci = assunzioni(grafo(n))
    persi = [k for k in NOMINE_DI_FERRAMENTA[n] if k not in voci]
    assert persi == [], f"grafo {n}: accessori nominati dal testo e non dichiarati {persi}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_la_logica_di_regolazione_non_va_persa(n: int) -> None:
    """§4.5: master, cascata, priorita' non sono pezzi, ma non si perdono."""
    voci = assunzioni(grafo(n))
    persi = [k for k in REGOLAZIONE[n] if k not in voci]
    assert persi == [], f"grafo {n}: logica di regolazione non dichiarata {persi}"


RACCORDI_ATTESI = {
    # impianto: quanti pezzi della famiglia «raccordo» e perche'
    1: (2, "due macchine in parallelo: 1 confluenza in mandata, 1 ripartizione in ritorno"),
    2: (1, "due ritorni su un solo attacco della pompa: 1 confluenza"),
    3: (1, "due ritorni di zona su un solo ingresso del volano: 1 confluenza"),
    4: (
        3,
        "due generatori in parallelo (1+1) piu' il ritorno dello scambiatore "
        "che rientra sul ritorno della caldaia (1)",
    ),
    5: (
        12,
        "tre pompe in parallelo (2+2), i due ritorni sul primario (1), "
        "tre circuiti secondari (2+2), la miscelazione del pavimento (1), "
        "l'anello di ricircolo sanitario (1+1)",
    ),
}


@pytest.mark.parametrize("n", IMPIANTI)
def test_i_raccordi_sono_n_meno_uno(n: int) -> None:
    """§4.4: dove N tubazioni si incontrano servono N-1 raccordi. Non uno di piu'."""
    quanti = sum(
        1 for c in grafo(n)["components"] if "junction" in mestieri(c["definition_id"])
    )
    atteso, perche = RACCORDI_ATTESI[n]
    assert quanti == atteso, f"grafo {n}: {quanti} raccordi invece di {atteso} — {perche}"


def test_il_quinto_impianto_ha_tutti_e_tre_i_circuiti_secondari() -> None:
    """Il testo dice «tre circuiti secondari indipendenti» e li elenca: batterie
    delle UTA, fan-coil, pavimento radiante miscelato. Perderne uno, o tornare a
    supporre un collettore a due sole uscite, e' un difetto."""
    d = grafo(5)
    quante = Counter(c["definition_id"] for c in d["components"])
    assert quante["ahu-coil"] >= 1, "manca il circuito delle batterie delle UTA"
    assert quante["fan-coil"] >= 1, "manca il circuito dei fan-coil"
    assert quante["underfloor-panel"] >= 1, "manca il circuito del pavimento radiante"
    assert quante["mixing-valve-3way"] >= 1, "il pavimento radiante non e' miscelato"
    assert quante["zone-manifold"] == 0, (
        "il collettore di catalogo ha due sole uscite: usarlo per tre circuiti "
        "significherebbe perderne uno"
    )
    assert quante["pump-circulator"] == 3, (
        "«ogni circuito e' dotato del proprio circolatore»: tre circuiti, tre circolatori"
    )
    assert quante["pump-circulator-dhw"] == 1, "il ricircolo sanitario ha il proprio circolatore"


# --------------------------------------------- 3. nel grafo non c'e' niente di piu'

PAROLE_DEL_TESTO = {
    "heat-pump-air-water": ("pompa di calore aria-acqua", "pompe di calore aria-acqua"),
    "gas-boiler": ("caldaia a condensazione",),
    "buffer-combined": ("accumulo ecocombi",),
    "buffer-four-port": ("volume tecnico",),
    "buffer-two-port": ("volume tecnico",),
    "dhw-cylinder": ("bollitore",),
    "dhw-heat-pump": ("boiler in pompa di calore",),
    "plate-heat-exchanger": ("scambiatore di calore a piastre",),
    "diverting-valve-3way": ("valvola a tre vie",),
    "mixing-valve-3way": ("circuito miscelato",),
    "zone-manifold": ("collettore",),
    "pump-circulator": ("circolatore",),
    "pump-circulator-dhw": ("circolatore",),
    "radiator": ("radiatori",),
    "fan-coil": ("fan-coil",),
    "underfloor-panel": ("pavimento radiante", "radiante a pavimento"),
    "ahu-coil": ("batterie",),
}
"""Per ogni pezzo che non e' un raccordo o un confine, le parole che lo giustificano."""


@pytest.mark.parametrize("n", IMPIANTI)
def test_ogni_pezzo_risale_a_una_parola_del_testo(n: int) -> None:
    """Criterio 1 di CONSEGNA.md §2. I raccordi e i confini restano fuori: i primi
    li impone la topologia descritta (§4.4), i secondi li impone la forma aperta del
    circuito sanitario (§4.3), e in entrambi i casi i grafi li dichiarano."""
    fonte = frasi_dell_impianto(n)
    inventati = []
    for c in grafo(n)["components"]:
        d_id = c["definition_id"]
        if mestieri(d_id) & {"junction", "branch_off", "boundary"}:
            continue
        parole = PAROLE_DEL_TESTO.get(d_id)
        assert parole is not None, f"voce di catalogo non prevista dal collaudo: {d_id}"
        if not any(p in fonte for p in parole):
            inventati.append((c["id"], d_id, parole))
    assert inventati == [], f"grafo {n}: pezzi senza una frase dietro {inventati}"


# ------------------------------------------------ 4. il confronto con il metro


def profilo(d: Json) -> Json:
    reti = {x["id"]: x for x in d["networks"]}
    archi = [
        (
            c["endpoint_a"]["component_id"],
            c["endpoint_a"]["port_id"],
            c["endpoint_b"]["component_id"],
            c["endpoint_b"]["port_id"],
            reti[c["network_id"]]["medium"],
        )
        for c in d["connections"]
    ]
    return {
        "reti": Counter((x["domain"], x["medium"]) for x in d["networks"]),
        "fluidi": Counter({(x["domain"], x["medium"]) for x in d["networks"]}),
        "componenti": Counter(c["definition_id"] for c in d["components"]),
        "nodi": {c["id"]: c["definition_id"] for c in d["components"]},
        "archi": archi,
    }


def _etichette(nodi: dict[str, str], archi: list[Arco], giri: int = 6) -> dict[str, str]:
    """Raffinamento alla Weisfeiler-Leman, con attacchi e fluidi sugli archi."""
    lab = dict(nodi)
    inc: dict[str, list[tuple[str, str, str, str]]] = defaultdict(list)
    for ca, pa, cb, pb, m in archi:
        inc[ca].append(("out", pa, m, cb))
        inc[cb].append(("in", pb, m, ca))
    for _ in range(giri):
        nuovo = {c: str((lab[c], tuple(sorted((v, p, m, lab[o]) for v, p, m, o in inc[c])))) for c in nodi}
        mappa = {v: f"L{i}" for i, v in enumerate(sorted(set(nuovo.values())))}
        lab = {c: mappa[v] for c, v in nuovo.items()}
    return lab


def corrispondenza(pa: Json, pb: Json, per_fluido: bool = False) -> dict[str, str] | None:
    """La corrispondenza fra i nodi che manda tubazioni in tubazioni, o None.

    Confronta cosi' com'e' scritto nel contratto: la voce di catalogo di ogni pezzo,
    e per ogni tubo la coppia (attacco, attacco) sul fluido della rete. I nomi
    interni dei pezzi non contano: due file corretti li scelgono diversi.
    """
    chiave = "fluidi" if per_fluido else "reti"
    if pa[chiave] != pb[chiave] or pa["componenti"] != pb["componenti"]:
        return None
    la, lb = _etichette(pa["nodi"], pa["archi"]), _etichette(pb["nodi"], pb["archi"])
    if Counter(la.values()) != Counter(lb.values()):
        return None
    archi_b = set(pb["archi"])
    candidati = {c: [d for d in pb["nodi"] if lb[d] == la[c]] for c in pa["nodi"]}
    ordine = sorted(pa["nodi"], key=lambda c: (len(candidati[c]), c))
    mappa: dict[str, str] = {}
    usati: set[str] = set()

    def prova(i: int) -> bool:
        if i == len(ordine):
            return True
        c = ordine[i]
        for d in candidati[c]:
            if d in usati:
                continue
            mappa[c] = d
            usati.add(d)
            coerente = all(
                (mappa[ca], pa_, mappa[cb], pb_, m) in archi_b
                for ca, pa_, cb, pb_, m in pa["archi"]
                if ca in mappa and cb in mappa
            )
            if coerente and prova(i + 1):
                return True
            usati.discard(d)
            del mappa[c]
        return False

    return dict(mappa) if prova(0) else None


@pytest.mark.parametrize("n", (1, 2, 3, 4))
def test_topologia_identica_alla_lettura_manuale(n: int) -> None:
    """CONSEGNA.md §2: si confronta su reti, componenti e tubazioni. Sui primi
    quattro impianti i due grafi coincidono arco per arco."""
    assert corrispondenza(profilo(grafo(n)), profilo(metro(n))) is not None, (
        f"impianto {n}: la topologia della camera pulita non combacia con la lettura manuale"
    )


def test_quinto_impianto_topologia_identica_a_meno_di_due_differenze_note() -> None:
    """L'impianto 5 differisce dalla lettura manuale in due sole cose, e nessuna
    delle due e' un difetto dell'interprete:

    1. la lettura manuale porta una **valvola di ritegno** sul ricircolo sanitario.
       E' ferramenta (`non_return`), il testo non la nomina, e ISTRUZIONI.md §5 la
       vieta alla prima stesura: e' un'assunzione tacita della lettura manuale.
    2. la camera pulita taglia il lato secondario in quattro reti invece di una.
       Stessi fluidi, stessi pezzi, stessi tubi: cambia solo il raggruppamento, che
       la camera pulita dichiara e la lettura manuale risolve in silenzio.

    Tolto il ritegno e confrontate le reti sui soli fluidi, i due grafi coincidono.
    """
    pulita, manuale = profilo(grafo(5)), profilo(metro(5))
    solo_manuale = manuale["componenti"] - pulita["componenti"]
    assert dict(solo_manuale) == {"valve-check-dhw-hot": 1}
    assert not (pulita["componenti"] - manuale["componenti"])

    # si cortocircuita il ritegno, ricucendo i due tubi che separava
    entra = next(a for a in manuale["archi"] if a[2] == "ritegno-ricircolo")
    esce = next(a for a in manuale["archi"] if a[0] == "ritegno-ricircolo")
    manuale["archi"] = [a for a in manuale["archi"] if "ritegno-ricircolo" not in (a[0], a[2])]
    manuale["archi"].append((entra[0], entra[1], esce[2], esce[3], entra[4]))
    manuale["nodi"].pop("ritegno-ricircolo")
    manuale["componenti"] = Counter(manuale["nodi"].values())

    assert corrispondenza(pulita, manuale, per_fluido=True) is not None, (
        "impianto 5: tolta la valvola di ritegno, la topologia doveva coincidere"
    )


# ------------------------------------- 5. il seguito della catena, e il determinismo


def _catena() -> tuple[Any, Any, Any, Any]:
    cat, rl, nm = catalog(), rules(), naming()
    rl.cross_check(cat)
    spec = importlib.util.spec_from_file_location(
        "build_plant_graph", ROOT / "examples" / "graph" / "build_plant_graph.py"
    )
    assert spec and spec.loader
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return cat, rl, nm, modulo


def _contenuto(modello: Any) -> Json:
    """Il contenuto del modello completato, senza l'ordine delle liste: i pezzi,
    le tubazioni con i loro capi, i sottosistemi."""
    return {
        "componenti": sorted((c.id, c.definition_id) for c in modello.components),
        "tubazioni": sorted(
            (
                x.network_id,
                x.endpoint_a.component_id,
                x.endpoint_a.port_id,
                x.endpoint_b.component_id,
                x.endpoint_b.port_id,
            )
            for x in modello.connections
        ),
        "sottosistemi": sorted(
            (s.id, tuple(sorted(s.component_ids)), tuple(sorted(s.network_ids)))
            for s in modello.subsystems
        ),
    }


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_completatore_digerisce_il_grafo(n: int) -> None:
    """Le regole e l'assemblatore girano sui cinque grafi senza rompersi, e non
    lasciano punti aperti."""
    cat, rl, _, _ = _catena()
    modello = load_project(PROVA / f"impianto-{n}" / "grafo.json")
    completo, proposte, buchi = saturate(modello, cat, rl)
    assert len(completo.components) > len(modello.components)
    assert proposte
    assert buchi == [], f"impianto {n}: il completatore lascia punti aperti {[b.key for b in buchi]}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_completatore_e_deterministico(n: int) -> None:
    """Rimescolando componenti, tubazioni e reti nel file, il modello completato
    non cambia: stessi pezzi, stesse tubazioni, stessi sottosistemi."""
    cat, rl, _, _ = _catena()
    modello = load_project(PROVA / f"impianto-{n}" / "grafo.json")
    atteso = _contenuto(saturate(modello, cat, rl)[0])
    for seme in range(1, 21):
        ottenuto = _contenuto(saturate(permuted(modello, seme), cat, rl)[0])
        assert ottenuto == atteso, f"impianto {n}: il completatore cambia esito col seme {seme}"


@pytest.mark.parametrize("n", (1, 2, 3, 4))
def test_il_documento_finale_e_deterministico(n: int) -> None:
    """L'esito che si consegna — il documento del grafo — e' identico carattere per
    carattere anche riscrivendo lo stesso impianto in un altro ordine."""
    cat, rl, nm, costruttore = _catena()
    modello = load_project(PROVA / f"impianto-{n}" / "grafo.json")
    completo, _, buchi = saturate(modello, cat, rl)
    atteso = costruttore.build(completo, cat, nm, buchi)
    for seme in range(1, 21):
        c2, _, b2 = saturate(permuted(modello, seme), cat, rl)
        assert costruttore.build(c2, cat, nm, b2) == atteso, (
            f"impianto {n}: il documento cambia col seme {seme}"
        )


# ------------------------------------------- il difetto 1, chiuso e tenuto chiuso


def test_il_documento_esce_per_tutti_e_cinque_gli_impianti() -> None:
    """Il difetto 1 del collaudo del giro 2, ora chiuso e presidiato.

    Al giro 2 il quinto grafo rompeva la catena: `NamingError`, «nessuna famiglia
    di linea per il fluido heating_water che parte da other in verso return».
    L'agente aveva tagliato il lato secondario in quattro reti, e tre cominciavano
    su un **raccordo** — mentre le famiglie di linea sanno nominare solo cio' che
    parte da un generatore o da una riserva. Il grafo era fedele e la scelta
    dichiarata: il buco era delle istruzioni, che dicevano cos'e' una rete e mai
    dove una rete puo' cominciare.

    Corretto il §4.2, la prova gira senza marcatore — che e' esattamente come il
    collaudo del giro 2 aveva detto di riprodurla."""
    cat, rl, nm, costruttore = _catena()
    for n in IMPIANTI:
        modello = load_project(PROVA / f"impianto-{n}" / "grafo.json")
        completo, _, buchi = saturate(modello, cat, rl)
        costruttore.build(completo, cat, nm, buchi)


#: I mestieri che possono far **cominciare** una rete: una macchina che la
#: alimenta, oppure un confine. Sono quelli da cui le famiglie di linea sanno
#: dire che acqua porta la linea e da che parte va.
SORGENTI = {"heat_generation", "thermal_storage", "dhw_storage", "boundary", "heat_exchange"}


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessuna_rete_comincia_su_un_raccordo(n: int) -> None:
    """La causa del difetto 1, presidiata nella sua forma generale.

    Non basta che oggi il documento esca: la regola del §4.2 dice che una rete
    parte da una macchina che la alimenta o da un confine, **mai da un
    raccordo**. Una rete fatta di soli raccordi, circolatori e terminali e' una
    rete che il resto della catena non sa nominare — ed e' esattamente il grafo
    che al giro 2 rompeva la catena. Qui si controlla la proprieta', non il
    sintomo: cosi' il difetto non puo' rientrare da un'altra porta."""
    d = grafo(n)
    di_rete: dict[str, set[str]] = defaultdict(set)
    per_id = {c["id"]: c["definition_id"] for c in d["components"]}
    for c in d["connections"]:
        for lato in ("endpoint_a", "endpoint_b"):
            di_rete[c["network_id"]] |= mestieri(per_id[c[lato]["component_id"]])

    orfane = sorted(r for r, m in di_rete.items() if not (m & SORGENTI))
    assert orfane == [], (
        f"grafo {n}: queste reti non hanno una macchina che le alimenti ne' un "
        f"confine, quindi cominciano su un raccordo: {orfane}"
    )
