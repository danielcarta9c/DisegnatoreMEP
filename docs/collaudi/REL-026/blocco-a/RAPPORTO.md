# REL-026, blocco A — il rapporto dell'agente esecutivo

**13 novembre 2026.** Agente della sessione (D-152), ramo `worktree-agent-a988d9876b597adb1`, base
`d9c8f2e` (il ramo `claude/magical-wright-ffrf86` con il pacchetto REL-026). Quello che riferisco
**non è una misura finché la sessione non l'ha rieseguito**: per ogni voce c'è il comando.

> **Prima di tutto, la base.** Il worktree era stato creato sul `main` locale fermo alla 1.15.0
> (`54262a1`), che non ha il pacchetto REL-026 né la 2.0.0. Prima di qualunque modifica ho
> riallineato il mio ramo, che non aveva commit, a `d9c8f2e` (`git reset --hard d9c8f2e`). Il
> worktree dell'altro agente (blocco B) era sulla stessa base vecchia: da controllare.

## 1. Le tavole (D-146)

Escono tutte, per la strada della skill costruita (`rifai.sh`: `costruisci-skill.py` in una
cartella temporanea → `valida` → `completa` → `disegna` → `anteprima`; la distinta a parte).

| tavola | file | esito del preflight |
|---|---|---|
| tre ventilconvettori canalizzati idronici coi plenum di mandata a **2, 3 e 6** uscite — idraulica (A2) | `plenum-di-mandata/tavola/rel026-canalizzati-plenum-di-mandata-idraulica-t1.png` | 0 bloccanti; avvisi `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR` (B3), `SHEET_TOO_FULL` 66 %, `DRAWING_TOUCHES_THE_BORDER` |
| lo stesso, elettrico e comando (A3) | `plenum-di-mandata/tavola/rel026-canalizzati-plenum-di-mandata-elettrico-t1.png` | 0 bloccanti, nessun avviso |
| un ventilconvettore canalizzato idronico col **plenum motorizzato** di zona a 4 serrande, la centrale e 4 termostati — tavola unica (A3) | `plenum-motorizzato/tavola/rel026-canalizzato-plenum-motorizzato-t1.png` | 0 bloccanti; `SHEET_TOO_FULL` 76 %, `DRAWING_TOUCHES_THE_BORDER` |
| il T1 di REL-023 (esecutivo) col **vaso sanitario** dimensionato dal comando: «VE-02 Vaso di espansione sanitario · 12 l · precarica 3,0 bar», «6 bar» accanto al gruppo di sicurezza | `vaso-sanitario/tavola/villetta-pdc-volano-bollitore-idraulica-t1.png` | 0 bloccanti; `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` (c'era già nel T1) |
| il foglio dei simboli nuovi accanto ai fratelli che non cambiano: il ventilconvettore col lato aria e l'unità interna canalizzata, i plenum di mandata 2…6 e i plenum di zona 2…6 | `simboli-nuovi.png` | — |

I grafi sono casi anonimi scritti apposta (`fai-i-grafi.py`); i piani sono scritti a mano e sono
materiale di collaudo, non prodotto (D-155).

### Che cosa mi sembra sbagliato sulle tavole, anche con i numeri a posto

1. > **Corretto il 13 novembre 2026, dopo i commenti del PO sulla tavola.** Quello che segue era
   > sbagliato: il motore **specchia** i raccordi (D-169, `"specchio": true` nel piano), e il dente
   > veniva dal grafo e dal piano di questo caso di prova — la dorsale del ritorno scritta sul braccio
   > `c` delle confluenze invece che sulla via dritta `a`–`b`, e i raccordi girati senza specchio. Con
   > la dorsale su `a`–`b` e `{"rotazione": 90, "specchio": true}` il ritorno è una verticale sola:
   > le pieghe passano da 8 a 4 e il rilievo B3 sparisce. Grafo, piano e tavola sono rifatti; la
   > regola è nelle istruzioni di Capire e di Comporre (`docs/collaudi/REL-026/RAPPORTO.md`, §7).

   **La confluenza del ritorno non può stare dritta** (avviso B3 sulla idraulica). I raccordi a T
   del catalogo hanno il braccio da una parte sola del verso del flusso, e il motore li **ruota** ma
   non li specchia. Con tutti gli attacchi d'acqua dei ventilconvettori a sinistra (D-167), una
   distribuzione a ritorno diretto in colonna o ha una piega a ogni confluenza (così è disegnata: la
   dorsale del ritorno fa un dente fra le due confluenze) o costringe i ritorni a incrociare la
   dorsale della mandata (e la incrociano due volte, col salto). Non è un difetto del blocco A, ma
   lo trova chiunque disegni più terminali sulla stessa dorsale.
2. **Le sigle si contano dal basso**: TE-01 è il ventilconvettore più in basso (zona giorno), PL-01 il
   plenum a sei uscite, le bocchette TA-01…06 sono le sue. È l'ordine della lettura dell'impianto
   (la via dritta dei raccordi prima del braccio); non l'ho toccato.
3. **«nr» cambia fra le due tavole dello stesso grafo.** Sulla idraulica entrano in tabella solo i due
   ventilconvettori con la marca (A-4), e TE-02 è «Ventilconvettore canalizzato **nr 1**»; sulla
   tavola dell'elettrico entrano tutti e tre, e lo stesso TE-02 è «**nr 2**». La regola del «nr» (I-141)
   conta le righe della tavola; con A-4 i terminali sono un sottoinsieme diverso sulle due tavole.
   **Da decidere dal PO** (contare sul grafo intero, o togliere il «nr» dove c'è la sigla).
4. **Il plenum di mandata a due uscite ha l'ingresso a 1,25 mm dal centro delle uscite**: il passo
   delle uscite (12,5) è di cinque passi di griglia, e con un numero pari di uscite il centro esatto
   non è una quota di griglia (§ A-2). Si vede, appena.
5. **Il disegno del plenum di mandata** è quello del plenum di zona senza le serrande: nel plenum a due
   e a tre uscite il collettore interno, le linee delle uscite e la parete destra si leggono come un
   rettangolo dentro il rettangolo. È la forma chiesta («il motorizzato senza serrande né motori»),
   e va giudicata.
6. **La distinta parla di «unità interna» anche per il ventilconvettore**: il plenum di ripresa (B.8)
   «sulla bocca di aspirazione dell'unità interna; l'eventuale filtro di serie dell'unità interna si
   toglie», e l'attività «distribuzione aria» porta «UI e plenum arretrati verso il portico», testo
   di una commessa aria-aria. Sono regole che c'erano; non le ho toccate.

## 2. Voce per voce

### A-1 — i pezzi nuovi: `fan-coil-ducted-air`, `supply-plenum-2` … `supply-plenum-6`, la famiglia PL

**Fatto.** Catalogo e simboli sono **generati** nel repository: le voci stanno in
`examples/layout/build_layout_fixtures.py` (lista `REL_026`), i simboli in
`examples/graphics/build_symbols.py`; i file in `examples/layout/catalog/` e `assets/symbols/` sono la
loro rigenerazione (`tests/catalog/test_generated_fixtures.py` lo controlla). `costruisci-skill.py`
li impacchetta in `dati/catalogo.json` e `dati/simboli.json`. La famiglia in `naming/families.json`:
`{"function": "air_distribution", "prefix": "PL", "name": "Plenum di mandata"}`, subito dopo
`air_zoning`. Il mestiere non è un enum: nessuno schema da toccare; aggiunto all'elenco dei mestieri
dell'aria-aria in `skill/capire/ISTRUZIONI.md`.

- **`fan-coil-ducted-air`** «Ventilconvettore canalizzato», `emission`, caratteri del
  ventilconvettore canalizzato (`maintainable`, `fouls_circuit`): `in`/`out` d'acqua obbligatori;
  `supply`, `return`, `drain` facoltativi (come nella copia della commessa); `power`, `bus`,
  `consenso_in`, `consenso` di comando, facoltativi e messi da parte se non collegati. Simbolo 40×30,
  il corpo dell'unità interna canalizzata con gli attacchi d'acqua al posto delle linee frigorifere,
  mai ruotato come quella. Non è una variante di `fan-coil-ducted`: una variante ha gli stessi
  attacchi (D-188).
- **`supply-plenum-N`** «Plenum di mandata a N uscite», `air_distribution`, `in` + `out_1…out_N`,
  tutti obbligatori: il plenum di zona senza serrande né motori, stesso riquadro (40 × 12,5·N − 5),
  stesse uscite, generato dalla stessa funzione di misura (`zoning_plenum_size/outlets`).
- Il generatore dei simboli: un moncone che sta già in un gruppo `data-port` non si marca anche
  `data-moncone` (il registro non accetta gruppi annidati); nessun simbolo esistente cambia.

Prove: `tests/catalog/test_voci_rel026.py` (25: si caricano e si risolvono, sigle TE e PL, la
famiglia dopo `air_zoning`, PLZ resta PLZ, plenum di mandata = plenum di zona senza motori, ingresso
centrato, il ventilconvettore e i suoi domini); aggiornate le prove che contano i simboli (95 → 101,
87 → 93), la lista dei simboli che non ruotano, e la prova dei monconi dei simboli idronici (il nuovo
simbolo misto ha i monconi d'aria nei loro gruppi, quelli d'acqua no). Il generatore rifatto non
cambia nessun file esistente (`git status` dopo la rigenerazione: solo file nuovi).

### A-2 — il plenum a due uscite con l'ingresso centrato, e B4

**Come B4 tratta un pezzo a tre attacchi.** `validation/regole.py`, `organi_che_spezzano_il_tratto`:
soggetto è un pezzo non raccordo con al più 3 attacchi di percorso (le porte di comando **contano**,
se il catalogo del progetto le ha) che ne ha due su facce opposte; se le due tratte attaccate lì non
hanno la stessa giacitura, rilievo **bloccante**. Il plenum a due uscite ha tre attacchi — `in` a
sinistra, `out_1` e `out_2` a destra — e (`in`, `out_1`) sono su facce opposte: con l'ingresso al
centro le due tratte corrono a quote diverse e la tavola si fermava. È per questo che la copia della
commessa aveva messo l'ingresso in asse con la prima uscita. La posa non lo tratta da organo: il
simbolo non è `inline`, `highways` conta solo l'asse delle facce, il revisore (`_cura_b4`) agisce
solo sul rilievo di B4.

**La correzione** (`_coppia_in_linea`): il terzo attacco deve uscire **di lato**, com'è scritto in
D-154 e nella docstring stessa («con tre attacchi il terzo sta per forza su una faccia
perpendicolare»); se sta sulla stessa faccia di uno della coppia il pezzo non è una tre vie, e non è
soggetto di B4. Sedici righe in un punto solo.

**Che cos'altro tocca.** Ho cercato nel catalogo (ogni voce, con ogni sottoinsieme delle porte di
comando che un grafo può collegare) i pezzi con tre attacchi di percorso e due sulla stessa faccia:
oltre al plenum, solo ventilconvettori, caldaie e pompe di calore con **un solo cavo** collegato
sulla faccia opposta agli attacchi d'acqua, dove B4 avrebbe confrontato un tubo con un cavo — un
falso rilievo che la correzione toglie. Il banco non cambia (28 su 28 uguali dopo A-1…A-4).

**Le quote.** Con un numero dispari di uscite l'ingresso è in asse con quella di mezzo (17,5 nel tre,
30 nel cinque). Con un numero pari il centro delle uscite cade a mezzo passo di griglia (11,25 nel
due), e un attacco fuori griglia non si instrada (D-054): l'ingresso va sulla quota di griglia più
vicina al centro e, fra le due a pari distanza, su quella che è il centro del riquadro — **10** nel
due, **22,5** nel quattro, **35** nel sei. L'altra scelta possibile era la quota di sotto (12,5 nel
due, che è anche l'ingresso del plenum di zona a due serrande): **da decidere dal PO**.

**Il plenum di zona motorizzato non l'ho toccato.** Il difetto di B4 non lo ha, ma per un caso: la sua
porta `motori` non è una porta di comando del simbolo, quindi conta fra gli attacchi di percorso
(quattro o più) e B4 non lo guarda mai. Ha però l'ingresso fisso a 12,5 per tutte le taglie (la
quota della mandata dell'unità interna): **non è centrato** — nel due a mezzo passo sotto il centro,
dal tre al sei vicino alla prima uscita (si vede in `simboli-nuovi.png`). Lo segnalo, come chiesto.

Prove: `tests/validation/test_regole_del_piano.py` — il plenum a due uscite col canale d'ingresso a
una quota e le uscite ad altre **non dà rilievi** (la prova fallisce senza la correzione: rieseguita
togliendo la modifica, `1 failed`); la deviatrice, col terzo attacco di lato, **sulla piega resta un
rilievo bloccante**.

### A-3 — le porte di comando non si attraversano

**Fatto** (`diametri/portate.py`, `_attraversati`): le porte del dominio `control` non entrano nel
percorso. Il meccanismo del difetto: il catalogo del progetto (`per_il_progetto`) mette da parte le
porte di comando non collegate; con `power` e `out_acs` collegate la pompa di calore ha sul fluido
`power_supply` un'entrata e un'uscita sole, che il calcolo contava come seconda coppia attraversata,
e con due coppie non leggeva più la portata della macchina.

Prove: `tests/diametri/test_le_porte_di_comando_non_si_attraversano.py` — la pompa di calore con
`power` e la sola `out_acs` collegate (prima: nessun dato, la portata del primario `None`; dopo:
quella di 8 kW / 5 K), e il ventilconvettore col lato aria con `consenso_in` e `consenso` collegati
(lo stesso difetto sul bus). Le due prove falliscono senza la correzione (`2 failed`), passano con.

### A-4 — i terminali con marca o modello in tabella

**Fatto** (`graphics/tabella.py`): `emission` fra i mestieri che entrano solo con marca o modello,
potenza e portata fra le caratteristiche. Sulla tavola A: TE-02 e TE-03 (con la marca) in tabella con
«3 kW», TE-01 (senza) no. Prove: `tests/graphics/test_i_terminali_con_marca_in_tabella.py` (radiatore e
ventilconvettore senza marca restano fuori; marca vuota non conta). Il banco non cambia.

**Attenzione** (da dire al progettista): sui terminali d'acqua `flow_rate_m3h` è la **portata
d'acqua** che il calcolo dei diametri legge; la portata d'aria del ventilconvettore canalizzato non va
lì (sta sui canali, come nell'AA-01). E il «nr» delle due tavole (§1, punto 3).

### A-5 — il vaso sanitario

> **Aggiornato il 13 novembre 2026 (I-301).** Il PO ha rimesso alla sessione la scelta della precarica. Da qui in
> poi: **precarica = pressione di rete − 0,2 bar** (catalogo tecnico Reflex «Reflex, Refix — Expansion vessels»,
> RE1884en, pp. 48, 49, 53, che richiama la DIN 4807-5, non letta), e il volume nominale col fattore che ne segue,
> `Vn = Ve · (pe + 1)(pa + 1) / [(p0 + 1)(pe − pa)]`. Gli esempi qui sotto sono quelli di prima della scelta: i numeri
> nuovi sono in `docs/collaudi/REL-026/RAPPORTO.md`, §8.

**Fatto**: `vaso --sanitario --tmax <°C di accumulo> --rete <bar> --taratura <bar> [--bollitore <l>]`
(`vaso/calcolatore.py`, `dimensiona_il_vaso_sanitario`; `vaso/comando.py`, `applica_sanitario`).

**La fonte letta**: Caleffi, focus tecnico «Il dimensionamento degli impianti idrosanitari — Vasi
d'espansione e accumuli», documento 0851415 (© 2015), letto il 13 novembre 2026 dal sito Caleffi:
p. 2 (temperatura dell'acqua fredda), p. 4 (il metodo), p. 5 (l'esempio). **Nessuna norma letta.**

**Il metodo** (pressioni relative in bar, `+ 1` per l'assoluta):

- coefficiente `e = ρ(T_fredda) / ρ(T_max) − 1`, densità di Kell come per il riscaldamento (la
  tabella di Caleffi, riferita a 4 °C, dà gli stessi valori al decimillesimo); `T_fredda = 10 °C`
  (Caleffi p. 2: 10÷12 °C al nord, 12÷15 al centro, 15÷18 al sud; il più freddo dà il vaso più grande);
- `Ve = e · V_bollitore` — solo l'acqua del bollitore: rete e ricircolo si trascurano (Caleffi p. 4);
- precarica `p0 = pressione di rete` (o taratura del riduttore): è la pressione iniziale della formula
  di Caleffi. **Che la precarica sia quella è un ragionamento sulla formula, non una frase letta**;
- pressione finale `pe = 0,9 · taratura` sopra i 5 bar (Caleffi p. 4: `Pe = 0,9 Pvs + 1`); fino a 5 bar
  `pe = taratura − 0,5` (lo scarto del vaso di riscaldamento, uso comune, non letto per il sanitario:
  Caleffi nelle pagine lette non scrive il caso sotto i 5 bar; a 5 bar le due regole danno 4,5);
- `Vn = Ve · (pe + 1) / (pe − p0)`, lo stesso fattore di pressione del riscaldamento, **senza riserva**;
- taglia: la prima della serie **d'uso comune, non letta su un catalogo** — 2, 5, 8, 12, **18**, 24, 35,
  50, 60, 80, 100, 150, 200, 300, 500 l — non sotto `Vn`; oltre 500 l non sceglie e lo dice;
- avvisi: meno di 0,3 bar fra rete e finale; rete non sotto la finale → errore «serve un riduttore».

Costanti con un nome in un punto solo (`TEMPERATURA_DELL_ACQUA_FREDDA_C`, `SCARTO_SANITARIO_FRAZIONE`,
`SOGLIA_DELLO_SCARTO_BAR`, `SERIE_DEI_VASI_SANITARI_L`, e `SALTO_MINIMO_BAR` comune ai due vasi).

**Gli esempi** (comando `python -c` sul calcolatore, e il comando sul T1):

| dati | e | Ve | p0 | pe | Vn | taglia |
|---|---|---|---|---|---|---|
| Caleffi p. 5: 1000 l, 80 °C, rete 3, valvola 7 | 0,02871 | 28,71 l | 3,0 | 6,3 | **63,51 l** (Caleffi 63,49) | 80 l |
| 200 l, 60 °C, rete 3, valvola 6 | 0,01678 | 3,357 l | 3,0 | 5,4 | 3,357 · 6,4 / 2,4 = **8,95 l** | **12 l** |
| 300 l, 65 °C, rete 4, valvola 6 | 0,01952 | 5,857 l | 4,0 | 5,4 | 5,857 · 6,4 / 1,4 = **26,78 l** | **35 l** |
| 500 l, 70 °C, rete 3, valvola 8 | 0,02243 | 11,21 l | 3,0 | 7,2 | **21,89 l** | 24 l |

Sull'esempio di Caleffi il loro programma propone un vaso da 60 l per 63,49 l calcolati: la loro
scelta della taglia non è «la prima non sotto». La nostra è quella del vaso di riscaldamento. **Da
decidere dal PO.** Il riscontro della commessa (18 l, precarica 3,5 bar, ingressi ignoti): 18 l è nella
serie; il metodo non è tarato su quel numero.

**Dove arriva**: come il vaso di riscaldamento — `volume_l` sul vaso sempre, `precarica_bar`
nell'esecutivo, e nell'esecutivo la taratura accanto alla sicurezza del sanitario; la tabella della
tavola e la voce della distinta («Vaso di espansione sanitario {volume_l} l») la leggono. Sul T1:

```
Vaso sanitario: coefficiente 0.0168, espansione 3.4 l; precarica 3 bar (la rete), finale 5,4 bar; nominale 9.0 l → 12 l.
Livello del progetto: esecutivo. Scritto sul grafo:
  - volume del bollitore dal grafo: bollitore, 200 l
  - dhw-safety-group-bollitore-cold-in: «6 bar»
  - expansion-connection-dhw-bollitore-cold-in: 12 l · precarica 3,0 bar
```

Senza `--bollitore` il volume è il `volume_l` del bollitore sul circuito del vaso, e il comando lo
dice; senza `--taratura` il sanitario non parte (la valvola del riscaldamento, 3 bar, non vale).
Documentazione: `skill/SKILL.md` +2 righe (461 su 500), il dettaglio in `skill/capire/ISTRUZIONI.md`
§3; la domanda della distinta su `volume_l` dice che il sanitario lo scrive il comando.

Prove: `tests/vaso/test_il_vaso_sanitario.py` (17: l'esempio di Caleffi, il coefficiente contro la
sua tabella a 60/70/80 °C, la pressione finale da 3 a 8 bar, la precarica, 18 l nella serie, il
riduttore, l'avviso, oltre la serie, i dati che non bastano, il comando nel definitivo e
nell'esecutivo, il grafo senza vaso sanitario, la riga di comando).

### A-6 — la distinta con le voci nuove

**Che cosa esce** (`plenum-di-mandata/distinta/…md`, `plenum-motorizzato/distinta/…md`):

- il ventilconvettore canalizzato col lato aria e i plenum di mandata **non hanno corredo**: escono
  nella sezione X, «Ventilconvettore canalizzato: fornitura e corredo di posa DA DEFINIRE» (3),
  «Plenum di mandata a due / tre / sei uscite: …» (1 ciascuno), **colonna Fornitura DA DEFINIRE**, con
  la domanda al progettista. È l'uso del repository per una voce senza regola: chi li fornisce, se il
  ventilconvettore è un'apparecchiatura di Nove C (sezione A), sospensioni, raccordo della condensa,
  giunto sulla ripresa, botola, sono **contenuto MEP che non ho inventato**;
- quello che è deciso vale anche per loro: canali Ø160, plenum porta-bocchetta (11), sifoni (3),
  tubi della condensa; il plenum di ripresa e le griglie;
- **una regola toccata**: `fan-coil-ducted-air` fra i `confini` delle giunzioni, come
  `fan-coil-ducted` — l'attacco d'acqua del terminale vuole il tubo: 6 «Raccordo diritto a pressare
  … all'attacco» al posto di 6 nippli da ½";
- col plenum motorizzato: «Plenum motorizzato di zona a quattro serrande» in sezione A (Nove C), col
  suo corredo (sospensione, isolamento, botola), «comprende CZ-01 (Centrale di zona)»; il
  ventilconvettore in X. Le attività della posa e della messa in servizio valgono per l'unità interna
  (`ducted-indoor-unit`) e non per il ventilconvettore: non le ho estese.

Prove: `tests/distinta/test_le_voci_di_rel026.py` (9: X con fornitura DA DEFINIRE e domanda, niente in
A, lato aria e condensa, il confine, **le cinque taglie** del plenum di mandata, il plenum motorizzato);
`SENZA_CORREDO` della prova di copertura con le sei voci nuove e il perché.

### La richiesta aggiunta: il ventilconvettore idronico col plenum motorizzato

**Regge fino alla tavola e alla distinta** (tavola e distinta sopra, banco
`plenum-motorizzato-rel026`), con **un difetto trovato**: la centrale di zona del catalogo
(`zone-controller`) ha la porta **`p1p2` obbligatoria**, la linea P1-P2 delle unità interne ad
espansione diretta; il ventilconvettore idronico non ce l'ha. Senza collegarla `valida` ferma il grafo:

```
Bloccanti — la tavola non si consegna
  - required port p1p2 is unconnected
    codice: REQUIRED_PORT_UNCONNECTED · centrale, p1p2
```

Nel caso B l'ho collegata al `bus` del ventilconvettore con un'assunzione dichiarata («da confermare
col progettista»). Come la centrale comanda davvero un ventilconvettore ad acqua (consenso, valvola,
velocità) è contenuto MEP: **da decidere dal PO** (una porta della centrale per le macchine idroniche,
o un'altra voce). Le serrande (`motori` → `serrande`) e i termostati sul bus della centrale funzionano
come nell'AA-01. Istruzioni: in `skill/capire/ISTRUZIONI.md` §4.8 il canalizzato idronico, il plenum
motorizzato se il testo dice serrande, motori o centrale, di mandata se lo dice senza, una domanda se
dice solo «plenum»; N = uscite collegate.

### Il banco

Aggiunti due casi, `plenum-di-mandata-rel026` (completa, idraulica + elettrico, distinta) e
`plenum-motorizzato-rel026` (completa, tavola unica, distinta), registrati con
`scripts/banco.py --registra --caso …`: 30 casi. **Nessuna tavola esistente cambiata.** Un'impronta
esistente sì, **la distinta del T1** (`t1-rel023`, `distinta/distinta.json`): misurato col diff
delle due distinte fatte con il `corredo.json` di prima e di adesso, l'unica riga diversa è
l'impronta delle regole (`"impronta": "4ed0b8034a230fed"` → `"13d6f4ef01e2a96a"`), che cambia perché
`corredo.json` ha una riga in più (il confine del ventilconvettore col lato aria); le voci sono le
stesse. Registrata con `--registra --caso t1-rel023`. Gli SVG del banco dei due casi nuovi sono
identici a quelli in questa cartella (stesse sha256). Se il blocco B tocca la distinta (le forature
fuori dal conteggio, B-3), `tests/banco/impronte.json` si riregistra dopo la fusione dei due rami.

## 3. I controlli

Rieseguiti alla fine, sull'ultimo commit del ramo, nel `.venv` del worktree (il pacchetto importato
è quello del worktree: `src/disegnatore_mep/__init__.py` del worktree).

| controllo | comando | esito |
|---|---|---|
| la suite | `.venv/bin/python -m pytest -q -p no:cacheprovider` | **3005 passed, 15 skipped, 11 xfailed** (base `d9c8f2e`: 2922 passed, 15 skipped, 11 xfailed): 0 failed, nessuno skip o xfail nuovo |
| ruff | `.venv/bin/python -m ruff check src tests scripts skill/scripts` (quello della CI) | `All checks passed!` |
| mypy | `.venv/bin/python -m mypy` (quello della CI) | `Success: no issues found in 127 source files` |
| il banco | `.venv/bin/python scripts/banco.py` | `30 uguali, 0 cambiati, su 30` |
| banco e release come prove | `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_il_banco.py tests/test_le_release.py` | `37 passed` |
| la skill si carica | `.venv/bin/python scripts/costruisci-skill.py --out <cartella temporanea>` | `150 file, 3483 kB`, ZIP 1086 kB, «Controlli … (al massimo 200 file): passati». I simboli nuovi non pesano sul conto dei file: stanno nel fascio `dati/simboli.json` (93 simboli), le voci in `dati/catalogo.json` (124) |
| SKILL.md | `wc -l skill/SKILL.md` | 461 righe (tetto 500) |

Le prove che ho cambiato, e perché (nessuna allentata): i conteggi dei simboli (95 → 101 e 87 → 93,
con la riga della storia), la lista dei simboli che non ruotano (i sei nuovi), i monconi dei simboli
idronici (il simbolo misto nuovo con i suoi tre gruppi d'aria, dichiarati uno per uno),
`SENZA_CORREDO` (le sei voci nuove, col perché).

## 4. Da decidere dal PO

1. La forma dei simboli nuovi e la sigla PL (proposte; `simboli-nuovi.png` e le tavole).
2. La quota dell'ingresso dei plenum a uscite pari: il centro del riquadro (10 / 22,5 / 35, scelta
   fatta) o la quota di sotto (12,5 / 25 / 37,5; 12,5 è quella del plenum di zona a due).
3. Il nome del ventilconvettore col lato aria: «Ventilconvettore canalizzato», uguale a
   `fan-coil-ducted` (dalla copia della commessa); se i due stanno sullo stesso foglio, due righe di
   legenda con lo stesso nome.
4. Le porte `consenso_in`/`consenso` venute dalla copia della commessa: tenute, facoltative, perché il
   grafo della commessa le usa; che cosa siano lo decide il PO.
5. Il corredo di distinta del ventilconvettore canalizzato idronico e dei plenum di mandata, e le
   attività di posa e messa in servizio del ventilconvettore (oggi X, DA DEFINIRE).
6. Il metodo del vaso sanitario: precarica = rete, 10 % / 0,5 bar, la serie, la scelta della taglia
   (prima non sotto, contro i 60 l di Caleffi per 63,5), l'acqua fredda fissa a 10 °C (nessuna
   opzione per il sud).
7. Il raggio della correzione di B4 (toglie anche i falsi rilievi tubo/cavo sulle macchine con un
   solo cavo sulla faccia opposta).
8. La centrale di zona con una macchina idronica (`p1p2` obbligatoria).
9. Il «nr» della tabella che cambia fra idraulica ed elettrico.
10. La confluenza dritta sulla dorsale (i raccordi che non si specchiano).

## 5. Che cosa non ho fatto o non ho potuto verificare

- **Il grafo vero di BD.RM.260 non l'ho provato**: non è nel repository e non l'ho avuto. Le
  modifiche sono provate sui casi anonimi e sui casi del repository.
- Il **PDF della distinta** non esce: manca la skill dei report Nove C (`--report`); c'è il Markdown.
- **La CI su GitHub** non è girata: niente push e niente PR, come da incarico. Le versioni e la
  release non le ho toccate; lo ZIP l'ho solo misurato in una cartella temporanea.
- Nessuna **norma** letta per il vaso sanitario; la serie delle taglie non viene da un catalogo.
- I plenum di mandata a 4 e 5 uscite sono sul foglio dei simboli e nella prova della distinta, non su
  una tavola d'impianto.
- La tavola dell'elettrico del caso B non c'è: è una tavola unica (I-227).
