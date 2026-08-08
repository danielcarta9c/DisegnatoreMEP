"""Collaudo indipendente del pezzo «Capire» — la prova in camera pulita del 7 agosto 2026.

Scritte da zero da un collaudatore a contesto separato: non ha scritto le istruzioni
(`skill/capire/ISTRUZIONI.md`) e non ha prodotto i grafi che giudica
(`skill/capire/prova-2026-08-07/impianto-1..5/grafo.json`).

**Storia del file.** Nate col collaudo del **giro 2**, che respinse su un difetto solo —
il quinto grafo non attraversava il resto della catena. Estese dal collaudo del **giro 3**,
sempre a contesto separato, che le ha rieseguite sui grafi nuovi, ne ha corretta una
sbagliata (vedi `test_le_esclusioni_esplicite_sono_dichiarate`) e ne ha aggiunte undici,
piu' dure: quelle della sezione 6, in fondo.

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
6. **Che non abbiano dei buchi che il confronto col metro non vede**: niente pezzi
   staccati, niente numeri inventati, niente fluidi fuori tabella, niente domande su
   cio' che il testo ha gia' scritto, e le due letture che le istruzioni non coprono
   alla lettera — il ramo che nasce da una valvola deviatrice, e il regime quando solo
   una parte delle macchine dichiara la potenza — inchiodate nella forma in cui i grafi
   le hanno risolte.

I difetti ancora aperti sono inchiodati con `xfail(strict=True)`, col motivo per esteso.
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
    1: [r"ricircolo"],
    2: [r"ricircolo"],
    3: [r"separatore idraulico", r"non collegat[ao] idraulicamente"],
    4: [r"bollitore"],
    5: [],
}
"""Le esclusioni esplicite del testo, come **espressioni regolari**.

Al giro 2 erano stringhe secche, e sul terzo impianto la stringa era «non collegato
idraulicamente» — il maschile, come sta nel testo del committente («un boiler … non
collegato idraulicamente»). L'agente del giro 3 l'ha dichiarata al femminile, perche' nella
sua frase il soggetto e' la produzione: «la produzione di ACS e' completamente separata e
**non collegata** idraulicamente all'impianto di riscaldamento». Stessa informazione, stesso
avvertimento a chi viene dopo, concordanza diversa: la prova rossa era un difetto **della
prova**, non del grafo, e il collaudo del giro 3 l'ha corretta allargando il confronto alla
concordanza invece che al carattere.

Resta invece giusto **pretendere** la dichiarazione, anche se qui il grafo mostra il boiler
staccato: §4.5 la vuole perche' serva a chi legge dopo — un boiler separato per distrazione
e un boiler separato per prescrizione si disegnano uguali, e solo la voce dichiarata dice al
pezzo che completa di non collegarlo."""
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
    """§4.5: «non e' previsto X» e' informazione, e va in una voce dichiarata.

    Si confronta sulla sostanza, non sul carattere: vedi la nota su `ESCLUSIONI`."""
    voci = assunzioni(grafo(n))
    persi = [k for k in ESCLUSIONI[n] if not re.search(k, voci)]
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


def _metro_5_senza_ritegno() -> Json:
    """Il quinto impianto letto a mano, tolta la valvola di ritegno del ricircolo.

    E' ferramenta (`non_return`): il testo non la nomina e ISTRUZIONI.md §5 la vieta
    alla prima stesura. La lettura manuale ce l'ha messa in silenzio, quindi la
    differenza si classifica nel **terzo esito** di CONSEGNA.md §2 — assunzione tacita
    del metro — e il metro **non si tocca**: si cortocircuita qui, nel confronto,
    ricucendo i due tubi che il ritegno separava."""
    manuale = profilo(metro(5))
    entra = next(a for a in manuale["archi"] if a[2] == "ritegno-ricircolo")
    esce = next(a for a in manuale["archi"] if a[0] == "ritegno-ricircolo")
    manuale["archi"] = [a for a in manuale["archi"] if "ritegno-ricircolo" not in (a[0], a[2])]
    manuale["archi"].append((entra[0], entra[1], esce[2], esce[3], entra[4]))
    manuale["nodi"].pop("ritegno-ricircolo")
    manuale["componenti"] = Counter(manuale["nodi"].values())
    return manuale


def test_quinto_impianto_topologia_identica_a_meno_del_ritegno() -> None:
    """L'impianto 5 differisce dalla lettura manuale in **una cosa sola**: la valvola
    di ritegno che il metro porta sul ricircolo sanitario, e che l'interprete non puo'
    disegnare.

    Al giro 2 le differenze erano due: c'era anche il lato secondario tagliato in
    quattro reti, tre delle quali cominciavano su un raccordo — ed era il difetto che
    rompeva la catena. Corretto il §4.2, quella differenza non c'e' piu': il confronto
    qui si fa **sulle reti**, con la loro molteplicita' (`per_fluido=False`), non piu'
    sui soli fluidi. E' la forma piu' stretta del confronto che il contratto ammette."""
    pulita, manuale = profilo(grafo(5)), _metro_5_senza_ritegno()
    assert dict(profilo(metro(5))["componenti"] - pulita["componenti"]) == {
        "valve-check-dhw-hot": 1
    }
    assert not (pulita["componenti"] - profilo(metro(5))["componenti"])
    assert pulita["reti"] == manuale["reti"], (
        f"impianto 5: le reti non combaciano — {dict(pulita['reti'])} contro {dict(manuale['reti'])}"
    )
    assert corrispondenza(pulita, manuale) is not None, (
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


CORREDO_DI_RETE = {
    "dirt-separation-before-what-it-would-ruin",
    "expansion-on-closed-circuit",
    "filling-unit-on-return",
    "gauge-where-the-plant-is-charged",
}


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_completatore_digerisce_il_grafo(n: int) -> None:
    """Le regole e l'assemblatore girano sui cinque grafi senza rompersi.

    Cio' che si misura qui e' il pezzo 1: che i grafi dell'agente attraversino
    il resto della catena. I punti aperti non sono un difetto dell'interprete
    — sono la risposta del completatore quando l'impianto non offre dove
    posare — e il **quarto impianto e' proprio quel caso**: l'ibrido non ha un
    ritorno generale, perche' il ramo del sanitario rientra a valle del
    collettore, e le quattro regole del corredo di rete lo dicono invece di
    scegliere un ramo. Che sia una proprieta' dell'impianto e non della
    fixture lo prova questo file: qui il grafo lo ha scritto un agente in
    camera pulita, e l'esito e' lo stesso.
    """
    cat, rl, _, _ = _catena()
    modello = load_project(PROVA / f"impianto-{n}" / "grafo.json")
    completo, proposte, buchi = saturate(modello, cat, rl)
    assert len(completo.components) > len(modello.components)
    assert proposte
    attesi = CORREDO_DI_RETE if n == 4 else set()
    assert {b.rule_id for b in buchi} == attesi, (
        f"impianto {n}: punti aperti inattesi {[b.key for b in buchi]}"
    )


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


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_documento_finale_e_deterministico(n: int) -> None:
    """L'esito che si consegna — il documento del grafo — e' identico carattere per
    carattere anche riscrivendo lo stesso impianto in un altro ordine.

    Al giro 2 questa prova girava sui soli primi quattro impianti, perche' sul quinto
    il documento non usciva affatto. Ora gira su tutti e cinque."""
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


# ------------------------------------------------------------------ 6. il giro 3
#
# Undici prove aggiunte dal collaudo del giro 3. Cercano quello che il confronto col
# metro non vede: un pezzo staccato, un numero inventato, una domanda inutile, e le due
# letture che le istruzioni non coprono alla lettera.


FLUIDI_AMMESSI = frozenset(
    m["medium"] for m in json.loads((ROOT / "naming" / "media.json").read_text())["media"]
)
"""I fluidi che `naming/media.json` sa tradurre in parole. §4.2: non se ne inventano altri."""


def domande(d: Json) -> list[str]:
    """Le frasi delle voci dichiarate che finiscono con un punto interrogativo."""
    return [
        f.strip()
        for a in d["assumptions"]
        for f in re.split(r"(?<=[.?!])\s+", a["text"])
        if f.strip().endswith("?")
    ]


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessun_componente_resta_staccato(n: int) -> None:
    """Un pezzo senza nemmeno una tubazione non e' un impianto: e' un pezzo dimenticato.

    Il confronto col metro non lo vedrebbe se anche il metro lo dimenticasse, e la
    prova sugli attacchi obbligatori non lo vede quando il pezzo di attacchi
    obbligatori non ne ha."""
    d = grafo(n)
    toccati = {
        c[lato]["component_id"] for c in d["connections"] for lato in ("endpoint_a", "endpoint_b")
    }
    staccati = sorted(c["id"] for c in d["components"] if c["id"] not in toccati)
    assert staccati == [], f"grafo {n}: pezzi senza nessuna tubazione {staccati}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessun_numero_inventato_nelle_proprieta(n: int) -> None:
    """§3 e §6: in `properties` vanno i dati che il testo da', «trascritti come stanno».

    Il rovescio della prova sui dati trascritti: li' si controlla che non ne manchi
    nessuno, qui che non ce ne sia **uno in piu'**. Una potenza, un volume o una
    temperatura che il testo non scrive e' un'invenzione, e §6 la vieta per nome."""
    fonte = frasi_dell_impianto(n)
    inventati = [
        (c["id"], k, v)
        for c in grafo(n)["components"]
        for k, v in c["properties"].items()
        if re.search(r"\d", str(v)) and str(v).lower() not in fonte
    ]
    assert inventati == [], f"grafo {n}: numeri che il testo non scrive {inventati}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_i_fluidi_sono_quelli_della_tabella_dei_nomi(n: int) -> None:
    """§4.2: «Non inventare un fluido che la tabella non ha» — a partire dal
    raffrescamento, che un fluido suo non ce l'ha e che tre impianti su cinque
    nominano."""
    fuori = sorted(
        {r["medium"] for r in grafo(n)["networks"] if r["medium"] not in FLUIDI_AMMESSI}
    )
    assert fuori == [], f"grafo {n}: fluidi che la tabella dei nomi non ha {fuori}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_ogni_rete_dichiarata_porta_almeno_una_tubazione(n: int) -> None:
    """Una rete senza tubi e' una rete annunciata e non scritta: il resto della catena
    la trova vuota e non sa dire ne' che acqua porta ne' dove va."""
    d = grafo(n)
    usate = {c["network_id"] for c in d["connections"]}
    vuote = sorted(r["id"] for r in d["networks"] if r["id"] not in usate)
    assert vuote == [], f"grafo {n}: reti dichiarate e mai usate {vuote}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_la_valvola_deviatrice_non_apre_una_rete_nuova(n: int) -> None:
    """Il primo dei due casi che le istruzioni non coprono alla lettera, e che tre
    agenti su cinque hanno segnalato senza vedersi fra loro.

    §4.2 dice che una rete parte da una macchina che la alimenta o da un confine, mai
    da un raccordo, e che i rami che si staccano da una **ripartizione** restano nella
    rete da cui nascono. Una **valvola deviatrice** non e' ne' l'una ne' l'altra cosa:
    §5 la mette fra i pezzi di topologia, ma non alimenta niente. Alla lettera, il §4.2
    non dice cosa fare del ramo che ne esce.

    Il collaudo del giro 3 ha giudicato che **non e' un difetto che respinge**: tutti e
    tre i grafi che hanno una deviatrice (2, 4, 5) hanno tenuto i rami dentro la rete
    della macchina che li alimenta, tutti e tre l'hanno dichiarato, e tutti e tre
    combaciano con la lettura manuale. L'istruzione e' imprecisa, i grafi sono giusti.
    Qui si presidia la lettura giusta, perche' un giro futuro non la cambi in silenzio:
    **tutte le tubazioni di una deviatrice stanno su una rete sola**."""
    d = grafo(n)
    per_id = {c["id"]: c["definition_id"] for c in d["components"]}
    guai = []
    for c in d["components"]:
        if "diversion" not in mestieri(c["definition_id"]):
            continue
        reti = {
            x["network_id"]
            for x in d["connections"]
            if c["id"] in (x["endpoint_a"]["component_id"], x["endpoint_b"]["component_id"])
        }
        if len(reti) != 1:
            guai.append((c["id"], sorted(reti)))
    assert guai == [], (
        f"grafo {n}: una valvola deviatrice apre una rete nuova invece di restare "
        f"in quella della macchina che la alimenta: {guai} (componenti: {len(per_id)})"
    )


def test_il_regime_esce_anche_quando_una_potenza_non_e_scritta() -> None:
    """Il secondo dei due casi che le istruzioni non coprono alla lettera.

    Il terzo impianto e' l'unico con **due** macchine che generano calore e **una sola**
    potenza scritta: la pompa di calore da 8 kW, e il boiler in pompa di calore da 200
    litri di cui il testo il volume lo da' e la potenza no. §4.6 prevede due casi soli —
    il testo da' le potenze, oppure non le da' — e questo non e' ne' l'uno ne' l'altro.

    Il collaudo del giro 3 ha giudicato che **non e' un difetto**: omettere il campo
    avrebbe buttato via gli 8 kW che l'ingegnere ha scritto, e sarebbe diventata una
    domanda su un dato gia' dato (D-108). Il regime esce, il conto e' scritto, la
    lacuna e' dichiarata — ed e' lo stesso regime della lettura manuale. Qui si
    presidiano tutte e tre le cose insieme."""
    d = grafo(3)
    senza_potenza = [
        c["id"]
        for c in d["components"]
        if "heat_generation" in mestieri(c["definition_id"]) and "potenza" not in c["properties"]
    ]
    assert senza_potenza, "il terzo impianto doveva avere un generatore senza potenza scritta"
    assert d.get("plant_regime") == "up_to_35_kw", "il regime doveva uscire lo stesso"
    voci = [a["text"].lower() for a in d["assumptions"]]
    assert any("8 kw" in v and "35" in v for v in voci), "il conto del regime non e' scritto"
    assert any("boiler" in v and "potenza" in v for v in voci), (
        "la potenza che il testo non da' non e' dichiarata come lacuna"
    )


@pytest.mark.parametrize("n", IMPIANTI)
def test_il_regime_combacia_con_la_lettura_manuale(n: int) -> None:
    """Il regime non entra nel confronto topologico del contratto, ma e' una delle
    quattro cose da cui dipende il resto della catena (`COSA_DECIDE.md` §3): si
    confronta col metro a parte."""
    assert grafo(n).get("plant_regime") == metro(n).get("plant_regime")


@pytest.mark.parametrize("n", IMPIANTI)
def test_nessuna_domanda_su_un_dato_che_il_testo_scrive(n: int) -> None:
    """D-108, nella sua forma generale: cio' che si puo' ricavare non si chiede.

    La prova sul regime inchioda il caso singolo. Qui si guarda **ogni** domanda che i
    grafi girano all'ingegnere: nessuna puo' chiedere una potenza, un volume, una taglia,
    un diametro o una marca, perche' o il testo li scrive — e allora sono gia' nel grafo
    — o non li scrive, e allora §6 dice che non compaiono e non si chiedono.

    Si cercano le **forme interrogative** del dato, non la parola: «volume tecnico» in
    mezzo a una domanda su un raccordo non e' una domanda su un volume."""
    vietate = re.compile(
        r"\b(quant[ei] (kw|litri)"
        r"|(che|quale|qual e'|quanta) (potenza|volume|taglia|marca|modello|diametro)"
        r"|sotto o sopra i 35)\b"
    )
    colpevoli = [f for f in domande(grafo(n)) if vietate.search(f.lower())]
    assert colpevoli == [], f"grafo {n}: domande su dati che non si chiedono {colpevoli}"


@pytest.mark.parametrize("n", IMPIANTI)
def test_dal_metro_manca_solo_la_ferramenta_che_il_metro_ha_messo(n: int) -> None:
    """La tabella di classificazione di CONSEGNA.md §2, scritta come prova.

    Su tutti e cinque gli impianti, i pezzi che stanno nella lettura manuale e non nel
    grafo della camera pulita sono **solo** ferramenta — e la ferramenta il §5 la vieta
    alla prima stesura. Quindi: nessuna differenza cade nel primo esito (detto dal testo
    e perso). E nessun pezzo sta nel grafo e non nel metro: nessuna differenza cade nel
    secondo esito (inventato). Le uniche differenze sono del terzo esito, a carico del
    metro, che il contratto vieta di correggere."""
    pulita, manuale = profilo(grafo(n)), profilo(metro(n))
    solo_metro = manuale["componenti"] - pulita["componenti"]
    non_ferramenta = sorted(k for k in solo_metro if not (mestieri(k) & FERRAMENTA))
    assert non_ferramenta == [], (
        f"impianto {n}: il metro ha pezzi che il grafo non ha e che non sono "
        f"ferramenta — sarebbero informazione persa: {non_ferramenta}"
    )
    solo_pulita = sorted(pulita["componenti"] - manuale["componenti"])
    assert solo_pulita == [], (
        f"impianto {n}: il grafo ha pezzi che il metro non ha — da classificare "
        f"uno per uno prima di approvare: {solo_pulita}"
    )


@pytest.mark.parametrize("n", IMPIANTI)
def test_i_dati_dell_ingegnere_stanno_nel_grafo_e_non_nel_metro(n: int) -> None:
    """L'altra faccia del terzo esito, quella in cui la camera pulita **vince**.

    Le cinque letture manuali non portano nemmeno una `properties`: le potenze, i
    volumi e il nome commerciale che l'ingegnere ha scritto, a mano si erano persi. I
    grafi della camera pulita li trascrivono tutti, come vuole §4.5. Non e' una
    differenza da classificare: e' il pezzo 1 che lavora meglio della lettura a mano, e
    va registrato perche' non si perda di nuovo."""
    assert not any(c["properties"] for c in metro(n)["components"]), (
        "la lettura manuale ha guadagnato delle properties: rifare la classificazione"
    )
    assert sum(len(c["properties"]) for c in grafo(n)["components"]) >= 2


@pytest.mark.parametrize(
    "n",
    [
        pytest.param(
            1,
            marks=pytest.mark.xfail(
                strict=True,
                reason=(
                    "DIFETTO APERTO, minore, del giro 3 — impianto 1. CONSEGNA.md §1 punto 2 "
                    "vuole l'elenco delle domande in «italiano piano, niente identificativi "
                    "interni, ogni voce comprensibile da sola»: e' la lista che l'ingegnere "
                    "legge, e i nomi interni del JSON lui non li ha mai visti. La voce a2 del "
                    "primo grafo finisce con «(pdc-1 e pdc-2 sono intercambiabili)», che sono "
                    "gli id di due componenti. Non respinge — non e' un pezzo perso ne' "
                    "inventato, e la frase resta comprensibile anche senza la parentesi, che "
                    "ripete quello che la frase ha appena detto — ma e' una regola scritta e "
                    "violata, e resta aperta finche' il grafo non si corregge. Gli altri "
                    "quattro grafi sono puliti."
                ),
            ),
        ),
        2,
        3,
        4,
        5,
    ],
)
def test_le_voci_dichiarate_non_portano_identificativi_interni(n: int) -> None:
    """CONSEGNA.md §1: le voci di `assumptions` le legge l'ingegnere, non il programma.

    Si cercano solo gli identificativi che **contengono una cifra** (`pdc-1`, `s13`,
    `rip-mandata-secondari-2`): sono quelli che nessuno puo' scambiare per una parola
    italiana. Gli id parlanti che coincidono con una parola — «accumulo», «caldaia»,
    «bollitore» — restano fuori: nel testo di una voce sono la parola, non il codice."""
    d = grafo(n)
    interni = {
        x["id"]
        for x in (*d["components"], *d["networks"], *d["connections"])
        if re.search(r"\d", x["id"])
    }
    citati = sorted(
        {
            i
            for i in interni
            for a in d["assumptions"]
            if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", a["text"])
        }
    )
    assert citati == [], f"grafo {n}: identificativi interni nelle voci dichiarate {citati}"
