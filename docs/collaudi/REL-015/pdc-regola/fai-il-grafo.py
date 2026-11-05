"""La villetta del collaudo T2 di REL-012 **con la regolazione a bordo della pompa di calore**
(REL-015 punto 4, I-230).

Il PO, sulle tavole della 1.6.0: «anche la pdc va alimentata ovviamente poi ci sono le sonde
della psc che vanno nei bollitori e volano ecc. comunque nel manuale Shenling c'e' tutto».

L'impianto e' quello del collaudo (`docs/collaudi/REL-012/collaudo-t2/grafo.json`): Shenling
ThermaX R290 12 kW, volano 100 l a quattro attacchi, bollitore 300 l con la deviatrice sulla
mandata, collettore con la zona pannelli miscelata e la zona radiatori diretta, ricircolo. Cambia
**chi regola**: la scheda del modulo idraulico della macchina (manuale d'installazione e d'uso,
§5.3, pp. 39-41; applicazioni §4.1, pp. 24-28, e §4.2, p. 29), non un regolatore climatico
esterno. Quindi:

- **via** il regolatore, la sonda esterna (la T_AM e' sulla scheda principale della macchina,
  §5.3 p. 42: non si cabla in campo), l'alimentazione del regolatore e il bus Modbus fra
  regolatore e macchina;
- **la sonda nel volano** (T_BT, §4.1: «se si vuole il controllo sulla temperatura del
  serbatoio»), sull'attacco `probe` del volano, che nel collaudo restava libero;
- **le tre sonde alla macchina**: bollitore -> `sonda_acs` (T_DHW), volano -> `sonda_accumulo`
  (T_BT), mandata dei pannelli dopo la miscelatrice -> `sonda_zona_2` (T_FW2);
- **i comandi dalla macchina**: deviatrice <- `out_acs` (SV1), miscelatrice <- `out_miscelatrice`
  (SV2), circolatore dei radiatori <- `out_pompa_zona_1` (P_C1), circolatore dei pannelli <-
  `out_pompa_zona_2` (P_C2), circolatore del ricircolo <- `out_pompa_ricircolo` (P_C4);
- **l'alimentazione dal quadro** della macchina (3G6, 15 m, come nel collaudo), **protetta
  nel quadro dall'interruttore magnetotermico differenziale** QF-01 (REL-018, I-278: specifica
  tecnica di installazione PdC Shenling Nove C Rev. 01, §3.2–3.4) e **senza il sezionatore
  locale** del collaudo, che la specifica (§3.2) non chiede come regola. I dati
  dell'interruttore e quelli elettrici della macchina li scrive `completa` dal manuale e dalla
  specifica. **I tre circolatori passano da un relè d'appoggio da 10 A** (D-228, I-259, il PO:
  «non alimentiamo mai il circolatore diretto da pdc ma attraverso contattore con Relè di
  appoggio da 10 A»): l'uscita della macchina eccita la bobina del relè, e il circolatore prende
  l'alimentazione attraverso il contatto, da un'uscita protetta del quadro. Un relè per
  circolatore; il `comando` del circolatore resta libero. Supera D-215 (un cavo solo dalla
  morsettiera al `power` del circolatore), che vale ancora per le valvole;
- **il comando a filo** della macchina (CN35), come voce `wired-remote`.

Niente morsetti sulla tavola: il progettista non li ha dati. Le sigle della scheda stanno qui e
nella fonte della voce di catalogo, non nel grafo.

    python3 docs/collaudi/REL-015/pdc-regola/fai-il-grafo.py [uscita.json]
"""

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
uscita = Path(sys.argv[1]) if len(sys.argv) > 1 else QUI / "grafo.json"
grafo = json.loads((RADICE / "docs/collaudi/REL-012/collaudo-t2/grafo.json").read_text(encoding="utf-8"))

grafo["metadata"]["project_id"] = "centrale-termica-villetta-pdc-regola"
grafo["metadata"]["issue_date"] = "2026-10-30"

# --- via il regolatore esterno e cio' che serviva solo a lui -------------------------------
TOLTI = {"regolatore", "sonda-esterna"}
grafo["components"] = [c for c in grafo["components"] if c["id"] not in TOLTI]
RETI_TOLTE = {"el-regolatore", "sg-sonda-esterna", "bus-pdc"}
grafo["networks"] = [n for n in grafo["networks"] if n["id"] not in RETI_TOLTE]
# I cavi verso il regolatore si riscrivono sotto, verso la macchina.
grafo["connections"] = [
    t
    for t in grafo["connections"]
    if t["endpoint_a"]["component_id"] not in TOLTI and t["endpoint_b"]["component_id"] not in TOLTI
]

# --- la sonda del volano -----------------------------------------------------------------
grafo["components"].append(
    {
        "id": "sonda-volano",
        "definition_id": "temperature-probe",
        "tag": None,
        "properties": {"funzione": "sonda del volano"},
    }
)
grafo["components"].append(
    {"id": "comando-a-filo", "definition_id": "wired-remote", "tag": None, "properties": {}}
)

# **Che cosa misura ogni sonda**, scritto accanto al pezzo (proposta): sulla tavola
# dell'elettrico tre sonde uguali, con la sola sigla, non dicono quale cavo va al bollitore e
# quale al volano (collaudo T2, §3.1). Sui circolatori no: sulla tavola idraulica il
# circolatore dei radiatori sta stretto fra la mandata e il ritorno dei pannelli, la scritta
# non ci sta (rilievo bloccante), e per farle posto bisognava piegare la zona radiatori.
ETICHETTE = {
    "sonda-bollitore": "bollitore",
    "sonda-volano": "volano",
    "sonda-pannelli": "mandata pannelli",
}
for item in grafo["components"]:
    if item["id"] in ETICHETTE:
        item["properties"]["etichetta"] = ETICHETTE[item["id"]]


def rete(ident: str, nome: str, medium: str) -> None:
    grafo["networks"].append({"id": ident, "name": nome, "domain": "control", "medium": medium})


def tratto(ident: str, rete_id: str, a: tuple[str, str], b: tuple[str, str]) -> None:
    grafo["connections"].append(
        {
            "id": ident,
            "network_id": rete_id,
            "endpoint_a": {"component_id": a[0], "port_id": a[1]},
            "endpoint_b": {"component_id": b[0], "port_id": b[1]},
            "properties": {},
        }
    )


# La sonda del volano pende dal suo attacco, come quella del bollitore dal suo.
tratto("t40", "primario", ("volano", "probe"), ("sonda-volano", "a"))

for ident, nome in (
    ("sg-sonda-bollitore", "Sonda del bollitore alla pompa di calore"),
    ("sg-sonda-volano", "Sonda del volano alla pompa di calore"),
    ("sg-sonda-pannelli", "Sonda di mandata pannelli alla pompa di calore"),
):
    for item in grafo["networks"]:
        if item["id"] == ident:
            item["name"] = nome
    if not any(item["id"] == ident for item in grafo["networks"]):
        rete(ident, nome, "control_bus")
tratto("t41", "sg-sonda-bollitore", ("sonda-bollitore", "signal"), ("pdc", "sonda_acs"))
tratto("t42", "sg-sonda-volano", ("sonda-volano", "signal"), ("pdc", "sonda_accumulo"))
tratto("t43", "sg-sonda-pannelli", ("sonda-pannelli", "signal"), ("pdc", "sonda_zona_2"))

for ident, nome in (
    ("cmd-deviatrice", "Comando deviatrice ACS dalla pompa di calore"),
    ("cmd-miscelatrice", "Comando miscelatrice pannelli dalla pompa di calore"),
):
    for item in grafo["networks"]:
        if item["id"] == ident:
            item["name"] = nome
# Le valvole: comandate direttamente dall'uscita della macchina, un cavo solo (D-215).
tratto("t44", "cmd-deviatrice", ("pdc", "out_acs"), ("deviatrice", "comando"))
tratto("t45", "cmd-miscelatrice", ("pdc", "out_miscelatrice"), ("miscelatrice", "comando"))

# **I circolatori: attraverso un relè d'appoggio da 10 A** (D-228, I-259). L'uscita della
# macchina va alla bobina del relè; la linea del circolatore parte da un'uscita del quadro,
# attraversa il contatto del relè (`a` -> `b`) e arriva al `power` del circolatore. Le linee
# dal quadro del collaudo si riscrivono: dal quadro al relè, e dal relè al circolatore.
#
# **Quale uscita del quadro, scelta sulla geometria della tavola dell'elettrico** (capire.md
# §4.8): il relè del ricircolo, il piu' basso, dalla prima uscita sopra; quello dei pannelli
# dalla seconda; quello dei radiatori, il piu' alto, dall'uscita a destra. La pompa di calore
# da un'uscita sotto: il quadro sta accanto ai relè, e il cavo della macchina scende e le
# arriva da sotto.
CAVI_DAL_QUADRO = {"t27", "t28", "t29"}
grafo["connections"] = [t for t in grafo["connections"] if t["id"] not in CAVI_DAL_QUADRO]
for ident, nome in (
    ("el-circ-radiatori", "Alimentazione circolatore radiatori dal quadro, attraverso il relè"),
    ("el-circ-pannelli", "Alimentazione circolatore pannelli dal quadro, attraverso il relè"),
    ("el-circ-ricircolo", "Alimentazione circolatore ricircolo dal quadro, attraverso il relè"),
):
    for item in grafo["networks"]:
        if item["id"] == ident:
            item["name"] = nome
rete("cmd-circ-radiatori", "Comando del relè del circolatore radiatori dalla pompa di calore", "power_supply")
rete("cmd-circ-pannelli", "Comando del relè del circolatore pannelli dalla pompa di calore", "power_supply")
rete("cmd-circ-ricircolo", "Comando del relè del circolatore ricircolo dalla pompa di calore", "power_supply")
RELE = (
    # (circolatore, relè, uscita della macchina, uscita del quadro, tratti)
    ("circ-radiatori", "rele-radiatori", "out_pompa_zona_1", "out_3", ("t46", "t50", "t51")),
    ("circ-pannelli", "rele-pannelli", "out_pompa_zona_2", "out_2", ("t47", "t52", "t53")),
    ("circ-ricircolo", "rele-ricircolo", "out_pompa_ricircolo", "out_1", ("t48", "t54", "t55")),
)
for circolatore, rele, uscita_della_macchina, uscita_del_quadro, (bobina, dal_quadro, al_circolatore) in RELE:
    zona = circolatore.removeprefix("circ-")
    grafo["components"].append(
        {"id": rele, "definition_id": "interface-relay", "tag": None, "properties": {}}
    )
    tratto(bobina, f"cmd-circ-{zona}", ("pdc", uscita_della_macchina), (rele, "bobina"))
    tratto(dal_quadro, f"el-circ-{zona}", ("quadro", uscita_del_quadro), (rele, "a"))
    tratto(al_circolatore, f"el-circ-{zona}", (rele, "b"), (circolatore, "power"))

rete("bus-comando-a-filo", "Comando a filo della pompa di calore", "control_bus")
tratto("t49", "bus-comando-a-filo", ("comando-a-filo", "a"), ("pdc", "comando_a_filo"))

# **L'uscita del quadro, scelta sulla geometria della tavola dell'elettrico** (capire.md §4.8:
# un'uscita del quadro e' un morsetto come un altro): la pompa di calore da un'uscita sotto,
# le tre sopra e a destra ai relè.
for item in grafo["connections"]:
    if item["id"] == "t25":
        assert item["endpoint_a"]["component_id"] == "quadro", item["id"]
        item["endpoint_a"]["port_id"] = "out_5"

# --- la protezione della linea della macchina (REL-018, I-278) ------------------------------
# Via il sezionatore locale del collaudo (specifica Nove C §3.2: non e' la regola), e
# l'interruttore magnetotermico differenziale nel quadro, all'uscita della linea. Il cavo del
# progettista — 3G6, 15 m — e' il tratto dall'interruttore alla macchina; quello dal quadro
# all'interruttore sta dentro il quadro, e non ha scritta.
grafo["components"] = [c for c in grafo["components"] if c["id"] != "sez-pdc"]
grafo["components"].append(
    {"id": "qf-pdc", "definition_id": "circuit-breaker-rcbo", "tag": None, "properties": {}}
)
for item in grafo["connections"]:
    if item["id"] == "t25":
        assert item["endpoint_b"]["component_id"] == "sez-pdc", item["id"]
        item["endpoint_b"]["component_id"] = "qf-pdc"
        item.pop("sezione", None)
        item.pop("lunghezza_m", None)
    if item["id"] == "t26":
        assert item["endpoint_a"]["component_id"] == "sez-pdc", item["id"]
        item["endpoint_a"]["component_id"] = "qf-pdc"
        item["sezione"] = "3G6"
        item["lunghezza_m"] = 15

# --- le assunzioni ------------------------------------------------------------------------
ASSUNZIONI = {
    "a12": None,  # l'alimentazione del regolatore: il regolatore non c'e' piu'
    "a13": (
        "Chi regola: la pompa di calore, con la regolazione a bordo (prima interpretazione). Le "
        "sonde del bollitore, del volano e di mandata dei pannelli sono cablate alla macchina, e "
        "la macchina comanda la deviatrice, la miscelatrice e i tre circolatori; non c'e' un "
        "regolatore esterno. Se invece la centrale ha un regolatore suo, dimmelo e ridisegno "
        "sonde e comandi verso di lui."
    ),
    "a14": (
        "Sezioni e lunghezze delle linee: il testo da' solo la linea della pompa di calore "
        "(3G6, 15 m, scritta sul tratto dall'interruttore alla macchina per la linea intera). Mancano sezione "
        "e lunghezza di: due comandi dalla pompa di calore (deviatrice, miscelatrice), tre "
        "comandi dei relè dei circolatori, tre linee dal quadro ai circolatori attraverso i "
        "relè, cavi delle tre sonde, comando a filo. "
        "Senza, quei tratti restano senza scritta."
    ),
    "a15": (
        "La logica di regolazione (curva climatica, priorita' ACS con la deviatrice, "
        "temperatura del volano) e' della pompa di calore e non e' topologia: sul grafo si "
        "vedono le sonde e i comandi, non la logica. La sonda esterna e' a bordo della macchina "
        "e non si disegna."
    ),
    "a20": (
        "Circolatori: mai alimentati dalla morsettiera della pompa di calore (D-228). Ogni "
        "circolatore ha il suo relè d'appoggio da 10 A: l'uscita della macchina ne comanda la "
        "bobina, e il circolatore e' alimentato attraverso il contatto da un'uscita del quadro. "
        "Il relè sta nel quadro, con la protezione dedicata della linea del circolatore "
        "(sulla tavola dell'elettrico e' disegnato fra la macchina e il circolatore); se sta in "
        "una scatola a parte, dimmelo."
    ),
    "a21": (
        "Sonda del volano: il testo non la nomina; e' disegnata sull'attacco della sonda del "
        "volano, cablata alla pompa di calore, perche' la macchina regoli sulla temperatura del "
        "volano. Se non la vuoi, la tolgo."
    ),
    "a22": (
        "Comando a filo della pompa di calore: disegnato vicino alla macchina, collegato a lei. "
        "Dove sta (in centrale o in casa) e la lunghezza del cavo non sono detti."
    ),
    "a23": (
        "Nessun collegamento a un sistema di supervisione: il testo non lo nomina. Il bus della "
        "pompa di calore resta libero."
    ),
    "a25": (
        "Protezione della linea della pompa di calore: un interruttore magnetotermico "
        "differenziale nel quadro (specifica Nove C §3.2), con i dati che completa scrive dal "
        "manuale Shenling e dalla specifica; niente sezionatore locale, che la specifica non "
        "chiede come regola. Se lo vuoi accanto alla macchina, dimmelo."
    ),
    "a24": (
        "Morsetti della pompa di calore: il testo non li da', e sulla tavola non sono scritti; "
        "ogni cavo dice a quale sonda, valvola o relè va."
    ),
}
nuove = []
for item in grafo["assumptions"]:
    if item["id"] in ASSUNZIONI:
        testo = ASSUNZIONI.pop(item["id"])
        if testo is None:
            continue
        item = {**item, "text": testo, "status": "proposed"}
    nuove.append(item)
nuove += [{"id": ident, "text": testo, "status": "proposed"} for ident, testo in ASSUNZIONI.items()]
grafo["assumptions"] = nuove

uscita.write_text(json.dumps(grafo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"scritto {uscita}")
