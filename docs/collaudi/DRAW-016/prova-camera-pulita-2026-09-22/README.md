# L'impianto 5 ricomposto sul grafo corretto — 22 settembre 2026

> ✅ **Approvata dal PO il 23 settembre 2026: «la tavola va bene»** (**I-108**). È la prima tavola
> approvata dopo D-166, e vale per questa. **È il metro del pavimento di B1**: i 7 rilievi di B1
> che porta sono falsi, e il pavimento è giusto quando non la accusa più.
>
> **Chiuso lo stesso giorno** (**D-173**, proposta al PO): il pavimento conta adesso anche le
> pieghe **fra due pezzi** — la L fra due porte su assi perpendicolari, e il gradino di una
> coppia con interassi diversi — e questa tavola **non porta più nessun rilievo di B1**. La
> guardia è `tests/validation/test_il_pavimento_di_b1.py`. La tavola e il piano non sono
> cambiati: è cambiato il metro con cui si misura.

**Che cos'è.** La tavola dell'impianto 5 **come il PO l'aveva chiesta**: dorsale unica, nell'ordine
del suo testo, con il ritorno che specchia la mandata (**D-172**). Il grafo del 21 settembre
aveva un ritorno inverso che la skill aveva inventato, su tutt'e due i collettori; corretto quello,
il pianificatore ha ricomposto **da zero**.

**Il protocollo è quello del 21 settembre**, perché le due misure siano confrontabili: un agente
avviato da zero con **soltanto** `skill/comporre/ISTRUZIONI.md`, `CONSEGNA.md`, lo scheletro e i
manifesti dei simboli; **vietati** i piani già esistenti, le tavole già fatte, il registro delle
decisioni, HANDOFF e il work package. L'agente dichiara di non averne aperto nessuno; ha lanciato
un solo `git status`, in lettura.

**Che cosa NON è.** Non è prodotto e **non si corregge a mano**: è la misura del pianificatore a
questa data. `scheletro-5.json` è il grafo ridotto a macchine e collettori, **senza valvole**
(`../riduci-a-scheletro.py`), e differisce da quello del 21 **solo** nei quattro attacchi corretti.

## La misura, rieseguita dalla sessione (D-152)

Rieseguito il piano finale, **dopo** la sua ultima scrittura:

| | 21 settembre, grafo col ritorno inverso | **22 settembre, grafo corretto** |
|---|---|---|
| formato | A3 | **A3** |
| tratte cedute / rilievi bloccanti | 0 / 0 | **0 / 0** |
| spezzate piegate | 12 | **9** |
| pieghe | 16 | **9** |
| incroci | 5 | **5** |

⚠ **Non è un confronto pulito**: fra le due prove sono cambiati il grafo (D-172) **e** le istruzioni
(D-170, D-171). Dice che la tavola è migliorata; non dice di quanto per ciascuna causa.

**Che cosa si vede.** Il **pettine** di B12 nell'ordine del testo — UTA, fan-coil, radiante — su
due colonne adiacenti, il ritorno verso il volano e la mandata verso le utenze, ogni utenza presa
**da sinistra** con mandata sopra e ritorno sotto. Sul primario **PDC-01 va dritta al volano** con
mandata e ritorno, e i due collettori della cascata stanno **addosso alle pompe**. Nessuna terza
colonna.

## ⚠ La tavola è giusta e i numeri dicono di no — verificato

Escono **7 `HIGHWAY_IS_NOT_STRAIGHT`**. L'agente ha scritto che la tavola gli sembra giusta; la
sessione li ha guardati **uno per uno sulla tavola**, e **nessuna di quelle pieghe è una scelta di
chi compone**:

| catena | perché la piega c'è |
|---|---|
| `m6`, `m9` (PDC-03 sui due collettori), `m18 + m20` (radiante sul ritorno) | un collettore **verticale** (B3) finisce con **un gomito** nell'ultima macchina, che ha l'attacco sul fianco |
| `m12` (deviatrice → bollitore), `m13 + m14` (ritorno della serpentina) | una **L fra due pezzi** con le facce perpendicolari, la cui giacitura è già fissata dal resto — il bollitore sta in piedi, la via dritta della deviatrice sta sulla mandata primaria |
| `m22 + m15` (mandata dell'UTA) | un **gradino** obbligato dall'interasse: il volano ha la coppia a **15**, il terminale a **10** (D-167, e la questione dell'altezza del simbolo è aperta al PO). È anche l'unico `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` |
| `m28 + m29 + m30` (anello del ricircolo) | l'anello è contato **come autostrada**: è una domanda di classificazione, non di posa |

**Ne discende un difetto di D-171, ed è della sessione.** Il pavimento di B1 conta soltanto le
pieghe imposte **dentro un pezzo** — fra due facce dello stesso raccordo. Non vede quelle imposte
**dalla combinazione** di due pezzi, e in particolare **il gomito in fondo a un collettore
verticale**. «B1 contro B3 si chiude» era vero **a metà**: per una catena che attraversa il
collettore sì, per quella che ci finisce dentro no.

**Chiuso il 23 settembre 2026** (**D-173**): le sette pieghe erano tutte **fra due pezzi con le
porte su assi perpendicolari** — anche il gradino di `m15`, che su questa tavola la testa della
colonna prende con una L, e l'anello, le cui due L e la curva della presa sono esattamente le tre
pieghe che fa. Contate quelle, i rilievi di B1 sono zero. Resta il rilievo di B11 sulla coppia
della batteria, ed è vero: la coppia passa da 15 a 10 e lo fa per forza (D-167).

## Gli altri rilievi dell'agente

**Verificati e corretti:**
- **le coordinate negative non si instradano**. Le istruzioni dicevano che contano solo le
  posizioni relative; il motore invece **instrada prima di traslare**. Lo stesso piano spostato di
  (−20, −105) risponde «every orthogonal path is blocked». Corretta la frase in `ISTRUZIONI.md`;
  **resta il difetto del motore**, che dovrebbe traslare prima;
- **«la deduzione prova solo 4 giaciture»**: falso — ne prova 8 (D-169). Era il **rapporto** a
  stampare la sola rotazione e a tacere lo specchio, e l'agente l'ha letto. Corretto il rapporto.

**Riferiti e non ancora verificati:** le istruzioni di B3 si contraddicono per le macchine
impilate («ritorno più vicino», poi «scambiali»); il motore tratta i raccordi a T come punti e
assegna i bracci per direzione senza rispettare `a/b/c`; il controllo di B3 conta anche il
raccordo di by-pass della miscelatrice fra i raccordi del collettore.
