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
- **l'alimentazione dal quadro** della macchina (col sezionatore, 3G6, 15 m, come nel collaudo) e
  dei tre circolatori: alimentati dal quadro e accesi dalla macchina, due cavi sullo stesso
  circolatore, come nel collaudo rifatto (`collaudo-t2/dopo/`). Proposta;
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
rete("cmd-circ-radiatori", "Comando circolatore radiatori dalla pompa di calore", "power_supply")
rete("cmd-circ-pannelli", "Comando circolatore pannelli dalla pompa di calore", "power_supply")
rete("cmd-circ-ricircolo", "Comando circolatore ricircolo dalla pompa di calore", "power_supply")
tratto("t44", "cmd-deviatrice", ("pdc", "out_acs"), ("deviatrice", "comando"))
tratto("t45", "cmd-miscelatrice", ("pdc", "out_miscelatrice"), ("miscelatrice", "comando"))
tratto("t46", "cmd-circ-radiatori", ("pdc", "out_pompa_zona_1"), ("circ-radiatori", "comando"))
tratto("t47", "cmd-circ-pannelli", ("pdc", "out_pompa_zona_2"), ("circ-pannelli", "comando"))
tratto("t48", "cmd-circ-ricircolo", ("pdc", "out_pompa_ricircolo"), ("circ-ricircolo", "comando"))

rete("bus-comando-a-filo", "Comando a filo della pompa di calore", "control_bus")
tratto("t49", "bus-comando-a-filo", ("comando-a-filo", "a"), ("pdc", "comando_a_filo"))

# **Le uscite del quadro, scelte sulla geometria della tavola dell'elettrico** (capire.md
# §4.8: un'uscita del quadro e' un morsetto come un altro). Stessi quattro cavi del collaudo.
USCITE_DEL_QUADRO = {
    "t25": "out_6",  # pompa di calore, da sinistra, sotto la macchina
    "t29": "out_1",  # circolatore del ricircolo, il piu' basso: la discesa piu' vicina
    "t27": "out_2",  # circolatore pannelli, la discesa di mezzo
    "t28": "out_3",  # circolatore radiatori, il piu' alto: la discesa piu' lontana
}
for item in grafo["connections"]:
    if item["id"] in USCITE_DEL_QUADRO:
        assert item["endpoint_a"]["component_id"] == "quadro", item["id"]
        item["endpoint_a"]["port_id"] = USCITE_DEL_QUADRO[item["id"]]

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
        "(3G6, 15 m, scritta sul tratto quadro-sezionatore per la linea intera). Mancano sezione "
        "e lunghezza di: tre alimentazioni dei circolatori, cinque comandi dalla pompa di calore "
        "(deviatrice, miscelatrice, tre circolatori), cavi delle tre sonde, comando a filo. "
        "Senza, quei tratti restano senza scritta."
    ),
    "a15": (
        "La logica di regolazione (curva climatica, priorita' ACS con la deviatrice, "
        "temperatura del volano) e' della pompa di calore e non e' topologia: sul grafo si "
        "vedono le sonde e i comandi, non la logica. La sonda esterna e' a bordo della macchina "
        "e non si disegna."
    ),
    "a20": (
        "Circolatori: ciascuno e' alimentato dal quadro di centrale e acceso da un'uscita della "
        "pompa di calore, due cavi sullo stesso circolatore. Se un'uscita della macchina "
        "alimenta il circolatore direttamente, il cavo dal quadro non serve: dimmelo e lo tolgo."
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
    "a24": (
        "Morsetti della pompa di calore: il testo non li da', e sulla tavola non sono scritti; "
        "ogni cavo dice a quale sonda, valvola o circolatore va."
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
