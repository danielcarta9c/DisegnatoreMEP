"""Caso di prova aria-aria — canalizzato Daikin FBA60A9 + RXM60A + Airzone Easyzone 5 uscite.
Rilievo dalla planimetria catastale 1:200 (300 dpi, 59,06 px/m), dimensionamento e computo
quantita' per la quotazione a corpo dell'installatore. Criterio: in dubbio, per eccesso.
Unica fonte dei numeri di tavole, tabelle ed Excel: scrive dim.json.  (rev. 01 dopo la revisione)
"""
import json
import math
from pathlib import Path

OUT = Path(__file__).parent / "dim.json"


def arrot(x, passo=0.5):
    return math.ceil(x / passo - 1e-9) * passo


def da_quotare(stima, minimo=0.0):
    """Regola unica: (L stimata + 1 m) x 1,15, per eccesso al mezzo metro; mai sotto il minimo dato."""
    return max(arrot((stima + 1.0) * 1.15), minimo)


def virgola(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def lungh(pts):
    return sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(pts, pts[1:]))


# --------------------------------------------------------------- dati di macchina
# FBA60A9 / RXM: Daikin, scheda FBA-A9 + RXM-R e product table RXM-A (daikin.it); plenum: scheda Easyzone QAI.
UI = dict(modello="Daikin FBA60A9", portata_alta_m3h=1080, portata_bassa_m3h=749, esp_nom_pa=30, esp_max_pa=150,
          dim="1000×800×245 mm", peso_kg=35)
UE = dict(modello="Daikin RXM60A", l_max_m=30, l_senza_carica_m=10, carica_agg_kg_m=0.020, dislivello_max_m=20,
          peso_kg=49)
PLZ = dict(modello="Airzone Easyzone, es. AZEZ8DAIBS07M5 con gateway AZX6GTCDA1", dim="1425×250×454 mm")

# --------------------------------------------------------------- rilievo (m)
# Origine: spigolo esterno NO-SO della pianta (alto a sinistra del catastale), x verso NE, y verso SE.
# Due disimpegni separati da una tramezza con porta a x 5,45 (pilastri 5,42/5,45): ovest x 3,47-5,40,
# est (ingresso) x 5,50-9,06; y 3,95-5,70 netti. UI, plenum e ripresa nel disimpegno EST.
BLOCCO = dict(plenum=(6.00, 4.12, 6.45, 5.54), ui=(6.45, 4.33, 7.25, 5.33), ripresa=(7.25, 4.33, 7.50, 5.33))
TRAMEZZA_X = 5.45
ZONE = [("Z1", "Camera 13 m²", 270), ("Z2", "Camera 15 m²", 280), ("Z3", "Camera 16 m²", 210),
        ("Z4", "Soggiorno-cucina 24 m²", 550)]
# uscite sul fronte ovest del plenum (x 6,00) e percorsi indicativi fino alla bocchetta
PERCORSI_ARIA = {
    "B1": ("Z1", [(6.0, 4.55), (3.85, 4.55), (3.85, 3.92)], 0.5),   # tramezza: +0,5 m per l'architrave
    "B2": ("Z2", [(6.0, 4.26), (5.80, 4.26), (5.80, 3.92)], 0.0),
    "B3": ("Z3", [(6.0, 4.83), (4.00, 4.83), (4.00, 5.73)], 0.5),
    "B4": ("Z4", [(6.0, 5.40), (5.95, 5.40), (5.95, 5.73)], 0.0),
    "B5": ("Z4", [(6.0, 5.12), (5.70, 5.12), (5.70, 6.20), (8.30, 6.20)], 0.0),  # in veletta nel soggiorno
}
MIN_FLEX = 2.0            # lunghezza minima di un ramo (acustica): l'eccesso resta in ansa
QE = (8.85, 5.62)         # quadro elettrico presunto, vicino all'ingresso: da confermare
UE_POS = (9.55, 2.60)     # UE a parete sotto il portico (fronte NE), indicativa
PERCORSO_FRIGO = [(7.05, 4.40), (9.06, 4.40), (9.30, 4.40), (9.30, 2.60), (9.55, 2.60)]
PERCORSO_COND = [(6.80, 4.18), (3.50, 4.18), (3.25, 4.18), (3.25, 4.70), (2.40, 4.70)]
TERMOSTATI = {"TZ-01": ("Z1", (3.20, 3.70)), "TZ-02": ("Z2", (7.60, 3.70)),
              "TZ-03": ("Z3", (3.20, 6.00)), "TZ-04": ("Z4", (7.70, 5.95))}
CENTRALE = (6.20, 5.50)
MADOKA = (8.60, 4.00)

# --------------------------------------------------------------- aeraulica
D_FLEX = 0.200
RHO, NU = 1.2, 1.5e-5


def dp_lineare(q_m3h, d=D_FLEX, eps=0.09e-3, k_flex=2.0):
    """Pa/m: Haaland su lamiera, per 2 il flessibile coibentato steso (ASHRAE: 1,5-2x)."""
    v = q_m3h / 3600 / (math.pi * d ** 2 / 4)
    re = v * d / NU
    f = (-1.8 * math.log10((eps / d / 3.7) ** 1.11 + 6.9 / re)) ** -2
    return k_flex * f / d * RHO * v ** 2 / 2, v


portata_zona = {z: q for z, _, q in ZONE}
nome_zona = {z: n for z, n, _ in ZONE}
n_bocchette = {z: sum(1 for v in PERCORSI_ARIA.values() if v[0] == z) for z in portata_zona}

tratte, bocchette = [], []
for bid, (zid, pts, extra) in PERCORSI_ARIA.items():
    qb = portata_zona[zid] / n_bocchette[zid]
    stima = max(lungh(pts) + extra + 0.3 + 0.5, MIN_FLEX)   # + discesa nel plenum di bocchetta + curve
    quot = da_quotare(stima)
    dpl, v = dp_lineare(qb)
    pdin = RHO * v ** 2 / 2
    dp = dpl * quot + 3 * 0.8 * pdin + 1.0 * pdin
    tratte.append(dict(id=f"A-{bid}", rete="aria-mandata", zona=zid, da="PLZ-01", a=bid,
                       materiale="flessibile coibentato", dn="Ø200", portata_m3h=round(qb), v_ms=round(v, 2),
                       l_stima_m=round(stima, 1), l_quot_m=quot, dp_pa=round(dp, 1)))
    bocchette.append(dict(id=bid, zona=zid, ambiente=nome_zona[zid], portata_m3h=round(qb)))

l_flex = sum(t["l_quot_m"] for t in tratte)
pezzi = sorted((t["l_quot_m"] for t in tratte), reverse=True)
confezioni = []
for pz in pezzi:                       # tratti interi, senza giunte, in confezioni da 10 m
    for c in confezioni:
        if sum(c) + pz <= 10.0 - 0.5:  # 0,5 m di sfrido per confezione
            c.append(pz)
            break
    else:
        confezioni.append([pz])
n_conf = max(len(confezioni), math.ceil(l_flex * 1.25 / 10))

ESP = dict(rami=max(t["dp_pa"] for t in tratte), bocchetta=10, plenum_airzone=15, ripresa_filtro=20, transiti=5)
ESP["totale"] = round(sum(ESP.values()) / 5) * 5

RIP = dict(griglia="1000×250", area_lorda=0.25, portata=1080)
RIP["v_lorda"] = round(RIP["portata"] / 3600 / RIP["area_lorda"], 2)
TRANSITO = [("Camera 13 m²", 270), ("Camera 15 m²", 280), ("Camera 16 m²", 210), ("Soggiorno-cucina", 550),
            ("porta fra i disimpegni (ritorno di Z1 e Z3)", 480)]
transito = [dict(dove=d, portata=q, aeff_min_m2=round(q / 3600 / 1.5, 3)) for d, q in TRANSITO]

# --------------------------------------------------------------- refrigerante
frigo_stima = lungh(PERCORSO_FRIGO) + 1.0 + 1.0   # + discesa alla UE e raccordi
FRIGO_STIMA = max(round(frigo_stima, 1), 8.0)
FRIGO_QUOT = da_quotare(FRIGO_STIMA, 12.0)        # 12 m: facciata della UE da confermare
carica_riserva = max(0.2, (FRIGO_QUOT - UE["l_senza_carica_m"]) * UE["carica_agg_kg_m"])

# --------------------------------------------------------------- condensa
cond_stima = round(lungh(PERCORSO_COND) + 0.4 + 2.0 + 0.3, 1)   # attraversamenti, discesa in traccia, raccordi
cond_quot = da_quotare(cond_stima, 10.0)

# --------------------------------------------------------------- elettrico e bus
EL = [
    ("E-1", "alimentazione-ue", "QE-01", "UE-01", "FG16OR16 3G2,5", 15.0, 20.0),
    ("E-2", "collegamento", "UE-01", "UI-01", "4G1,5 doppio isolamento", FRIGO_STIMA + 1.0, FRIGO_QUOT + 1.0),
    ("E-3", "alimentazione-airzone", "QE-01", "CZ-01", "FG16OR16 3G1,5", 12.0, 15.0),
    ("E-4", "p1p2", "UI-01", "CZ-01", "2×0,75 (P1-P2)", 1.5, 0.0),
    ("E-5", "p1p2", "UI-01", "CF-01", "2×0,75 (P1-P2)", lungh([(7.0, 4.4), MADOKA]) + 1.2 + 0.5, 0.0),
]
for tid, (zid, pos) in TERMOSTATI.items():
    st = lungh([CENTRALE, (pos[0], CENTRALE[1] if zid in ("Z3", "Z4") else 4.02), pos]) + 1.2 + 0.5
    EL.append((f"E-{tid}", "bus-airzone", "CZ-01", tid, "cavo bus Airzone", round(st, 1), 5.0))
for eid, rete, da, a, cavo, st, minimo in EL:
    tratte.append(dict(id=eid, rete=rete, da=da, a=a, materiale=cavo, dn="", portata_m3h=None, v_ms=None,
                       l_stima_m=round(st, 1), l_quot_m=da_quotare(st, minimo), dp_pa=None))
tratte += [
    dict(id="R-L", rete="frigo-liquido", da="UE-01", a="UI-01", materiale="Cu ricotto, isol. ≥ 10 mm",
         dn="Ø6,35 (1/4\")", portata_m3h=None, v_ms=None, l_stima_m=FRIGO_STIMA, l_quot_m=FRIGO_QUOT, dp_pa=None),
    dict(id="R-G", rete="frigo-gas", da="UE-01", a="UI-01", materiale="Cu ricotto, isol. ≥ 13 mm",
         dn="Ø12,7 (1/2\")", portata_m3h=None, v_ms=None, l_stima_m=FRIGO_STIMA, l_quot_m=FRIGO_QUOT, dp_pa=None),
    dict(id="C-1", rete="condensa", da="UI-01", a="scarico bagno", materiale="PVC rigido, i ≥ 1%",
         dn="Ø32", portata_m3h=None, v_ms=None, l_stima_m=cond_stima, l_quot_m=cond_quot, dp_pa=None),
    dict(id="A-RIP", rete="aria-ripresa", da="RA-01", a="UI-01", materiale="plenum di ripresa coibentato",
         dn=RIP["griglia"], portata_m3h=1080, v_ms=RIP["v_lorda"], l_stima_m=None, l_quot_m=None, dp_pa=None),
]
ORDINE = ["A-B1", "A-B2", "A-B3", "A-B4", "A-B5", "A-RIP", "R-L", "R-G", "C-1",
          "E-1", "E-2", "E-3", "E-4", "E-5", "E-TZ-01", "E-TZ-02", "E-TZ-03", "E-TZ-04"]
T = {t["id"]: t for t in tratte}
for i, tid in enumerate(ORDINE, start=1):
    T[tid]["num"] = f"T{i:02d}"
L = {t["id"]: t["l_quot_m"] for t in tratte}
l_bus = sum(L[f"E-{t}"] for t in TERMOSTATI)
l_p1p2 = L["E-4"] + L["E-5"]

# --------------------------------------------------------------- computo
F_NC, F_INST, F_COMM = "Nove C", "installatore", "committente"
bom = []


def voce(cat, descr, um, q, note="", fornitura=F_INST):
    bom.append(dict(cat=cat, voce=descr, um=um, q=q, note=note, fornitura=fornitura))


C = "A. Apparecchiature (fornite da Nove C, posa dell'installatore)"
voce(C, f"Unità esterna Daikin RXM60A, R32 ({UE['peso_kg']} kg)", "n", 1, "", F_NC)
voce(C, f"Unità interna canalizzata Daikin FBA60A9, {UI['dim']}, {UI['peso_kg']} kg", "n", 1, "pompa condensa a bordo", F_NC)
voce(C, f"Plenum motorizzato Airzone Easyzone 5 uscite Ø200 (es. AZEZ8DAIBS07M5, gateway AZX6GTCDA1), {PLZ['dim']}, Wi-Fi", "n", 1,
     "codice da confermare col distributore", F_NC)
voce(C, "Termostato di zona Airzone Blueface, a filo", "n", 4, "", F_NC)
voce(C, "Comando a filo Daikin Madoka BRC1H52W", "n", 1, "", F_NC)

C = "B. Distribuzione aria"
voce(C, "Condotto flessibile coibentato Ø200 (isolamento 25 mm, barriera vapore), confezione da 10 m", "conf.", n_conf,
     f"{l_flex:g} m in {len(tratte) and 5} tratti interi: " + " + ".join(f"{t['l_quot_m']:g}".replace(".", ",")
                                                                      for t in tratte[:5]) + " m")
voce(C, "Plenum porta-bocchetta coibentato per bocchetta 400×200, attacco Ø200 laterale o dall'alto", "n", 5)
voce(C, f"Plenum di ripresa coibentato con filtro ispezionabile, bocca {RIP['griglia']}, sulla bocca di aspirazione UI",
     "n", 1, "unico filtro del sistema")
voce(C, "Giunto antivibrante in tela fra UI e plenum di ripresa", "n", 1)
voce(C, "Curva 90° Ø200 in lamiera zincata, alle uscite con cambio di direzione stretto", "n", 4)
voce(C, "Manicotto di giunzione Ø200", "n", 2, "riserva")
voce(C, "Fascetta di serraggio Ø200 (anima e mantello)", "n", 36)
voce(C, "Nastro alluminio rinforzato 50 mm", "rotolo", 2)
voce(C, "Sostegno per flessibile (fascia o collare con pendino), passo ≤ 1,2 m", "n", 25)
voce(C, "Kit sospensione: barra filettata M10, tassello per solaio in laterocemento, antivibrante", "n", 10,
     "UI 4, plenum 4, ripresa 2")
voce(C, "Isolamento elastomerico adesivo per raccordi e plenum", "rotolo", 1)

C = "C. Circuito frigorifero e unità esterna"
voce(C, "Tubo rame ricotto pre-isolato 1/4\" (6,35 × 0,8), isolamento ≥ 10 mm, resistente a 120 °C", "m",
     FRIGO_QUOT, f"stimati {FRIGO_STIMA:g} m".replace(".", ","))
voce(C, "Tubo rame ricotto pre-isolato 1/2\" (12,7 × 0,8), isolamento ≥ 13 mm, resistente a 120 °C", "m",
     FRIGO_QUOT, f"stimati {FRIGO_STIMA:g} m".replace(".", ","))
voce(C, "Manicotto a brasare 1/4\" e 1/2\" (riserva, posa in tratta unica)", "n", 4)
voce(C, "Nastro di finitura e manicotti isolanti per le giunzioni a cartella", "kit", 1)
voce(C, "Canalina coprilinee esterna 80×60", "m", 4)
voce(C, "Accessori canalina: curva 2, terminale a muro 1, giunto 2", "kit", 1)
voce(C, "Collare di sostegno linee in controsoffitto", "n", 10)
voce(C, "Staffe a parete per UE (portata ≥ 100 kg) con antivibranti", "kit", 1, "o piedini a terra, secondo posizione")
voce(C, "Scarico condensa della UE (funziona anche in caldo): raccordo e tubo Ø16 fino a pluviale o pozzetto", "m", 4)
voce(C, "Refrigerante R32, riserva per carica aggiuntiva", "kg", round(carica_riserva, 2),
     "precarica fino a 10 m; oltre, 20 g/m")

C = "D. Scarico condensa"
voce(C, "Tubo PVC rigido Ø32", "m", cond_quot, f"stimati {cond_stima:g} m, pendenza ≥ 1%".replace(".", ","))
voce(C, "Raccordo di adattamento dall'attacco VP20 della UI (Øe 26) al Ø32, con fascetta", "n", 1)
voce(C, "Curva 87°-90° Ø32", "n", 6)
voce(C, "Manicotto Ø32", "n", 3)
voce(C, "Sifone ispezionabile per condensa, uscita Ø40", "n", 1)
voce(C, "Innesto sullo scarico del bagno Ø40 (braga 45° o presa su sifone lavabo)", "n", 1)
voce(C, "Collare per tubo condensa", "n", 10)
voce(C, "Isolamento anticondensa 9 mm, tratto in controsoffitto", "m", 5)
voce(C, "Collante e pulitore PVC", "n", 1)

C = "E. Elettrico, comando e regolazione"
voce(C, "Cavo FG16OR16 3G2,5, alimentazione UE dal quadro", "m", L["E-1"], "posizione quadro da sopralluogo")
voce(C, "Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA, dedicato UE", "n", 1,
     "verificare targa RXM60A (RXM60R: MCA 15,9 A, fus. 16 A)")
voce(C, "Sezionatore onnipolare di prossimità IP55, apertura contatti ≥ 3 mm", "n", 1, "accanto alla UE")
voce(C, "Magnetotermico 1P+N C6, linea dedicata centrale Airzone", "n", 1)
voce(C, "Cavo FG16OR16 3G1,5, alimentazione centrale Airzone (linea dedicata)", "m", L["E-3"])
voce(C, "Aggiornamento dello schema del quadro elettrico", "a corpo", 1)
voce(C, "Cavo di collegamento UI-UE 4G1,5 a doppio isolamento", "m", L["E-2"])
voce(C, "Cavo bus Airzone, schermato", "m", l_bus, "4 termostati, posa a stella dalla centrale")
voce(C, "Cavo 2×0,75 P1-P2 (gateway Airzone e Madoka)", "m", l_p1p2)
voce(C, "Tubo corrugato Ø25 (linee di potenza E.1 ed E.5)", "m", 40)
voce(C, "Tubo corrugato Ø20 (bus e linee P1-P2)", "m", 40)
voce(C, "Scatola di derivazione IP55", "n", 2)
voce(C, "Scatola 503 per termostati e Madoka", "n", 5)

C = "F. Assistenze murarie (aperture comprese; chiusure e ripristini del Committente)"
voce(C, "Carotaggio parete esterna Ø80 con guaina passante e sigillatura", "n", 1)
voce(C, "Foratura di parete interna Ø80 per linee frigorifere e cavi", "n", 2)
voce(C, "Foratura di tramezza Ø250 (o vano 450×250) per flessibili e plenum di bocchetta", "n", 7,
     "5 bocchette e 2 nella tramezza fra i disimpegni")
voce(C, "Foratura per la condensa verso il bagno", "n", 1)
voce(C, "Traccia per la condensa nel bagno", "m", 3)
voce(C, "Tracce per le linee dal quadro al controsoffitto", "m", 5)
voce(C, "Tracce per termostati e Madoka", "n", 5)

C = "Z. Opere del Committente (escluse dall'offerta, da coordinare)"
voce(C, "Controsoffitto dei due disimpegni: altezza libera ≥ 35 cm sotto il solaio in zona UI e plenum", "a corpo", 1, "", F_COMM)
voce(C, "Botola di ispezione ≥ 600×600 sotto UI (filtro, pompa, scheda) e sotto plenum e centrale", "n", 2, "", F_COMM)
voce(C, "Velette o controsoffitti per le bocchette, altezza utile ≥ 30 cm; veletta nel soggiorno per B5", "a corpo", 1, "", F_COMM)
voce(C, "Bocchette di mandata 400×200 a doppio filare con serranda (Aeff ≥ 0,055 m²)", "n", 5, "B1-B5", F_COMM)
voce(C, f"Griglia di ripresa {RIP['griglia']} senza filtro, apribile per accedere al filtro", "n", 1, "", F_COMM)
voce(C, "Griglie di transito o luce sotto porta: camere Aeff ≥ 0,05 m² (n 3), soggiorno ≥ 0,10, porta fra i disimpegni ≥ 0,09",
     "n", 5, "senza, la portata cala e cresce il rumore", F_COMM)
voce(C, "Chiusura e ripristino di fori, tracce e passaggi", "a corpo", 1, "", F_COMM)

ATTIVITA = [
    "Posa UI in controsoffitto su sospensioni antivibranti, con plenum Airzone e plenum di ripresa.",
    "Posa UE a parete su staffe con antivibranti; canalina esterna e scarico condensa della UE.",
    "Linee frigorifere: posa e cartelle; prova di tenuta in azoto prima della chiusura del controsoffitto, circuito lasciato in pressione con manometro fino al secondo accesso, con verbale; vuoto, apertura rubinetti, eventuale carica, registrazione F-Gas.",
    "Distribuzione aria: 5 flessibili Ø200 con plenum porta-bocchetta, sostegni e sigillature, bocche protette fino alle bocchette.",
    "Scarico condensa con sifone e allaccio allo scarico del bagno; prova di scarico e della pompa prima della chiusura.",
    "Linee elettriche dedicate dal quadro (UE con sezionatore, centrale Airzone); collegamento UI-UE, linee P1-P2, bus Airzone, posa di 4 termostati e del Madoka.",
    "Messa in servizio con Nove C, al secondo accesso: regolazione automatica della prevalenza UI e misura delle portate per zona, configurazione Airzone (S4a-S4b su TZ-04, Z4 zona di sfogo, aperture minime), ruoli di Madoka e gateway sul P1-P2, app; collaudo con verbale.",
    "Dichiarazioni di conformità D.M. 37/2008 lettera a (linee elettriche) e lettera c (climatizzazione) con allegati; documenti per libretto, CURIT e F-Gas.",
    "Cantiere: POS e oneri della sicurezza (presenza dell'impresa del Committente), trabattello e mezzi di sollevamento.",
    "Trasporto, ricevimento e custodia delle apparecchiature fornite da Nove C fino al collaudo; protezioni di UI, plenum e bocche durante le opere edili.",
    "Pulizia finale e smaltimento di imballi e residui di lavorazione.",
]
VARIANTI = [
    ("V.1", "Linea frigorifera completa oltre la quantità di computo (coppia pre-isolata, cavo UI-UE, canalina, R32)", "m"),
    ("V.2", "Flessibile Ø200 posato oltre la quantità di computo, con fascette e sostegni", "m"),
    ("V.3", "Cavo FG16OR16 3G2,5 in corrugato oltre la quantità di computo", "m"),
    ("V.4", "Accesso aggiuntivo in cantiere (oltre i due previsti)", "n"),
    ("V.5", "Centralino aggiuntivo 8 moduli, se il quadro non ha 4 moduli liberi", "n"),
]

NOTE = [
    "Lunghezze dalla planimetria catastale 1:200 (±10-15%) sui tracciati della tavola M.03. «L da quotare» = "
    "(L stimata + 1 m) × 1,15, per eccesso; linee frigorifere 12 m e condensa 10 m per l'incertezza dei percorsi.",
    "Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica in sopralluogo prima "
    "dell'offerta; le varianti hanno solo il prezzo unitario.",
    "UI, plenum e ripresa nel controsoffitto del disimpegno est (ingresso); i rami B1 e B3 e la condensa attraversano la "
    "tramezza verso il disimpegno ovest; B5 corre nella veletta del soggiorno.",
    "Portate massime di zona dal carico estivo, non contemporanee: con tutte le zone aperte i 1080 m³/h della UI si "
    f"ripartiscono. Velocità nei flessibili Ø200 da {virgola(min(t['v_ms'] for t in tratte[:5]))} a "
    f"{virgola(max(t['v_ms'] for t in tratte[:5]))} m/s; ripresa {virgola(RIP['v_lorda'])} m/s sulla sezione lorda.",
    f"Prevalenza utile stimata circa {ESP['totale']:.0f} Pa (rami {ESP['rami']:.0f}, bocchetta {ESP['bocchetta']}, plenum "
    f"{ESP['plenum_airzone']}, ripresa e filtro {ESP['ripresa_filtro']}, transiti {ESP['transiti']}), nel campo della FBA60A9 "
    f"(fino a {UI['esp_max_pa']} Pa): regolazione automatica in messa in servizio.",
    f"La velocità minima della UI (circa {round(UI['portata_bassa_m3h'], -1):.0f} m³/h) supera la portata di ogni camera: Z4 (S4a-S4b) è la "
    "zona di sfogo, con apertura minima tarata; le camere non in chiamata restano chiuse. Nessuna serranda di bypass.",
    f"Linee frigorifere entro i 10 m di precarica senza carica aggiuntiva; oltre, 20 g/m di R32 (massimo {UE['l_max_m']} m, "
    f"dislivello massimo {UE['dislivello_max_m']} m).",
    "UE a parete sul fronte NE sotto il portico, a distanza dalla PdC idronica del riscaldamento e fuori dalla sua zona di rispetto; quadro "
    "elettrico presunto all'ingresso: posizioni da confermare in sopralluogo, prima della gara.",
    "Condensa con la pompa a bordo UI allo scarico del bagno, con sifone ispezionabile.",
    "Bocchette 400×200 a doppio filare (Aeff ≥ 0,055 m²), griglia di ripresa 1000×250 e griglie di transito sono del "
    "Committente (Z.4-Z.6): i plenum porta-bocchetta B.2 sono per bocchette 400×200.",
    "Due accessi: posa di macchine, canali e linee con le prove prima della chiusura del controsoffitto; messa in "
    "servizio e collaudo dopo controsoffitto e bocchette.",
]

dati = dict(ui=UI, ue=UE, plz=PLZ, blocco=BLOCCO, tramezza_x=TRAMEZZA_X,
            percorsi_aria={k: dict(zona=v[0], punti=v[1]) for k, v in PERCORSI_ARIA.items()},
            percorso_frigo=PERCORSO_FRIGO, percorso_cond=PERCORSO_COND, termostati=TERMOSTATI,
            centrale=CENTRALE, madoka=MADOKA, qe=QE, ue_pos=UE_POS,
            zone=[dict(id=z, nome=n, portata=q) for z, n, q in ZONE],
            tratte=tratte, ordine=ORDINE, bocchette=bocchette, esp=ESP, ripresa=RIP, transito=transito,
            l_flex_m=l_flex, confezioni=confezioni, l_bus_m=l_bus, cond=dict(stima=cond_stima, quot=cond_quot),
            bom=bom, note=NOTE, attivita=ATTIVITA, varianti=VARIANTI)
OUT.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    for tid in ORDINE:
        t = T[tid]
        print(f"{t['num']} {tid:9s} {t['rete']:22s} {t['da']:>7s}->{t['a']:<14s} {t['dn']:>14s} "
              f"{str(t['portata_m3h'] or ''):>5s} {str(t['v_ms'] or ''):>5s} {str(t['l_stima_m'] or ''):>5s} "
              f"{str(t['l_quot_m'] or ''):>5s} {str(t['dp_pa'] or ''):>5s}")
    print("flex", l_flex, "confezioni", confezioni, n_conf, "bus", l_bus, "ESP", ESP, "rip", RIP)
    print("frigo", FRIGO_STIMA, FRIGO_QUOT, "cond", cond_stima, cond_quot, "R32", carica_riserva)
    print(len(bom), "voci")
    for n in NOTE:
        print("-", n)
