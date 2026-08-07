# Verbale del collaudo indipendente del pezzo «Capire»

**Data** 7 agosto 2026 · **Oggetto** `skill/capire/ISTRUZIONI.md` · **Metro**
`examples/prova/prova-*.json` (congelate, non toccate) · **Consegne giudicate**
`skill/capire/prova-2026-08-07/impianto-1..5/`

Chi scrive non ha redatto le istruzioni né prodotto i grafi. Le tabelle di rilettura
scritte dagli agenti non sono state usate come prova: i cinque testi sono stati riletti
frase per frase contro i cinque grafi da chi firma.

---

# VERDETTO: RESPINTO

**Un solo difetto, e non tocca la fedeltà.** Sulla fedeltà il pezzo è pulito: su
cinque impianti e 82 tubazioni non c'è **una** differenza nei due esiti che
respingono. Niente detto dal testo e perso, niente inventato.

Il difetto è altrove, ed è il criterio 7 a scoprirlo: **il quinto grafo della camera
pulita non attraversa il resto della catena**. Le istruzioni, sul taglio delle reti,
non danno alcun criterio, e permettono un grafo fedele che il passo successivo non sa
nominare. È esattamente il caso che `CONSEGNA.md` §3 governa — «se una differenza
rivela un buco delle istruzioni, la correzione si fa alle istruzioni, si registra, e la
prova si ripete da capo con un agente nuovo».

**Cosa serve per riaprire:** una riga in §4.2 che dica dove una rete può cominciare
(oppure una riga in più nella tabella delle famiglie di linea). Non una riscrittura.
Poi la prova si rifà con un agente nuovo, come impone il protocollo.

---

## 1. I criteri, e l'esito di ciascuno

### 1.1 I sette del committente

| # | Criterio | Esito |
|---|---|---|
| 1 | Fedeltà ai cinque testi | **superato** |
| 2 | Nessuna invenzione progettuale | **superato** |
| 3 | Nessuna informazione esplicita persa | **superato** |
| 4 | Domande solo quando necessarie | **superato**, con due voci di rumore (R1) |
| 5 | Regime ricavato dalle potenze, non chiesto | **superato**, tutti e cinque |
| 6 | Diramazioni a N vie: N−1 raccordi; impianto 5 con tre circuiti | **superato**, conto esatto |
| 7 | Il seguito della catena li digerisce, in modo deterministico | **NON superato** → difetto 1 |

### 1.2 I miei, aggiunti prima di aprire le consegne

Fissati in `criteri-prima-di-guardare.md`, qui accanto, prima di guardare un solo
grafo.

| # | Criterio | Esito |
|---|---|---|
| M1 | Il file carica davvero | 5/5 |
| M2 | Voci di catalogo esistenti, nessuna ferramenta | 5/5 |
| M3 | Nessun attacco con due tubazioni | 5/5 |
| M4 | Verso out→in, nessun attacco inventato, nessuno stub toccato | 5/5 |
| M5 | Fluido dell'attacco = fluido della rete | 5/5 |
| M6 | Sigle tutte nulle (nei testi non ce n'è nessuna) | 5/5 |
| M7 | Sottosistemi, regole, fogli vuoti; versione 1.1.0 | 5/5 |
| M8 | Nessun attacco obbligatorio scoperto | 5/5 |
| M9 | Esclusioni esplicite dichiarate | 5/5 |
| M10 | Nomine di ferramenta dichiarate | 5/5 |
| M11 | Logica di regolazione dichiarata | 5/5 |
| M12 | Potenze, volumi, modello, qualifiche trascritti | 5/5 |
| M13 | Reversibilità dichiarata (impianti 2 e 5) | 2/2 |
| M14 | Nessun pezzo isolato ingiustificato | 5/5 |
| M15 | Voci leggibili, senza gergo di modello | 5/5 |
| M16 | Ogni pezzo e ogni tubo risale a una frase (riletto da me) | 5/5 |
| M17 | Confronto sui campi del contratto | fatto |
| M18 | Raccordi contati, non guardati a occhio | 5/5 |

Tutto questo è inchiodato in `tests/collaudo/test_collaudo_interprete.py`:
**91 prove verdi e 1 `xfail(strict=True)`**, il difetto.

---

## 2. La tabella di classificazione, impianto per impianto

Il confronto è quello del contratto (`CONSEGNA.md` §2): **reti** (dominio e fluido),
**componenti** (voce di catalogo), **tubazioni** (quale attacco con quale attacco, su
quale fluido). Sigle e sottosistemi restano fuori per costruzione.

L'identità delle tubazioni è stata verificata cercando una corrispondenza fra i pezzi
dei due grafi che mandi ogni tubo in un tubo con gli stessi attacchi e lo stesso
fluido: i nomi interni non contano, due file corretti li scelgono diversi.

### Impianto 1 — due pompe di calore, accumulo combinato

Reti, componenti e **tutte e 11 le tubazioni**: identici alla lettura manuale.

| Differenza | Esito | Nota |
|---|---|---|
| Sigle (`PDC-01`…) presenti a mano, assenti in camera pulita | fuori confronto | le istruzioni vietano di inventarle |
| Sottosistemi presenti a mano, vuoti in camera pulita | fuori confronto | appartengono a un pezzo successivo |
| Dati in `properties`: 12 kW, 200 litri, ECOcombi in camera pulita; niente a mano | **assunzione tacita della lettura manuale** | povertà del metro, già registrata da un altro collaudo |
| 10 voci dichiarate contro 2 | **assunzione tacita della lettura manuale** | il metro aveva chiuso in silenzio master/slave, il numero dei radiatori, la posizione del circolatore, l'esclusione del ricircolo |

### Impianto 2 — pompa di calore con deviatrice e bollitore

Reti, componenti e **tutte e 11 le tubazioni**: identici.

| Differenza | Esito | Nota |
|---|---|---|
| Sigle, sottosistemi | fuori confronto | — |
| `properties`: 15 kW, 100 litri | **assunzione tacita della lettura manuale** | — |
| 11 voci contro 2 | **assunzione tacita della lettura manuale** | la reversibilità, il numero dei fan-coil, la confluenza dei ritorni, l'esclusione del ricircolo erano taciuti |

### Impianto 3 — pompa di calore diretta su pavimento radiante

Reti, componenti e **tutte e 9 le tubazioni**: identici. Entrambe le letture disegnano
due circuiti radianti e chiudono i ritorni con una confluenza.

| Differenza | Esito | Nota |
|---|---|---|
| Sigle, sottosistemi | fuori confronto | — |
| `properties`: 8 kW, 50 litri, 200 litri | **assunzione tacita della lettura manuale** | — |
| 9 voci contro 2 | **assunzione tacita della lettura manuale** | l'esclusione del separatore, la separazione del boiler, i confini sanitari, il regime |

### Impianto 4 — ibrido pompa di calore + caldaia

Reti, componenti e **tutte e 15 le tubazioni**: identici. Entrambe leggono la caldaia
«combinata» con la voce base e disegnano la produzione sanitaria come la descrive il
testo (deviatrice + scambiatore a piastre).

| Differenza | Esito | Nota |
|---|---|---|
| Sigle, sottosistemi | fuori confronto | — |
| `properties`: 10 kW, 24 kW, 150 litri | **assunzione tacita della lettura manuale** | — |
| 12 voci contro 2 | **assunzione tacita della lettura manuale** | — |
| Due voci chiedono conferma di cose già decise dal testo e dal catalogo (a1, a3) | osservazione R1 | non è una scelta taciuta: è rumore, non un difetto |

### Impianto 5 — tre pompe di calore, tre circuiti secondari

Il testo dice che dal volume partono **tre** circuiti secondari e non nomina un
collettore. Il grafo li ha **tutti e tre**: batterie delle UTA, fan-coil, pavimento
radiante miscelato, ognuno con il proprio circolatore, più il ricircolo sanitario con
il suo. Tolta la valvola di ritegno (vedi sotto), la topologia coincide **arco per
arco** con la lettura manuale: 36 tubazioni su 36.

| Differenza | Esito | Nota |
|---|---|---|
| La lettura manuale porta una **valvola di ritegno** sul ricircolo sanitario, la camera pulita no | **assunzione tacita della lettura manuale** | è ferramenta (`non_return`), il testo non la nomina, e §5 la vieta alla prima stesura: qui il metro ha torto e il pezzo 1 lavora meglio |
| La camera pulita taglia il lato secondario in quattro reti (una per circuito più il tratto comune), la lettura manuale in una | **assunzione tacita della lettura manuale** | stessi fluidi, stessi pezzi, stessi tubi; la camera pulita lo dichiara (voce a16), il metro lo risolve in silenzio. **Ma ha una conseguenza fuori dal confronto: è la causa del difetto 1** |
| Sigle, sottosistemi, `properties` (35 kW ×3, 500 litri ×2), 16 voci contro 4 | fuori confronto / **assunzione tacita** | — |

### Riepilogo dei quattro esiti

| Esito | Quante | Respinge? |
|---|---|---|
| Detto dal testo e perso | **0** | — |
| Inventato | **0** | — |
| Assunzione tacita della lettura manuale | 12 | no |
| Ambiguità dichiarata da entrambe, risolta diversamente | 0 | no |
| *(fuori confronto per costruzione: sigle e sottosistemi)* | *10* | — |

Le dodici: `properties` vuote e voci dichiarate mancanti in tutti e cinque gli impianti
(due per impianto, dieci in tutto), più la valvola di ritegno e il raggruppamento delle
reti del quinto.

---

## 3. Il difetto

### DIFETTO 1 — il quinto grafo non attraversa il resto della catena

**Cosa si vede.** Il grafo carica. Il completatore lo digerisce e non lascia punti
aperti. Poi il passo che battezza le linee idrauliche si ferma:

```
NamingError: nessuna famiglia di linea per il fluido 'heating_water'
che parte da 'other' in verso 'return'
```

Sugli altri quattro impianti il documento esce. Sul quinto esce anche partendo dalla
lettura manuale. È il solo dei cinque che rompe la catena.

**Perché.** Il testo dice «dal volume tecnico partono **tre circuiti secondari
indipendenti**». Le istruzioni, §4.2, dicono che «una rete è un circuito che il testo
nomina o distingue». Preso alla lettera — ed è la lettura più fedele — questo fa tre
reti, una per circuito, più una per il tratto comune fra il volume e le tre partenze.
Ma ciascuno dei tre circuiti **comincia su un raccordo**, non su una macchina, e la
tabella delle famiglie di linea (`naming/lines.json`) conosce le linee di riscaldamento
solo quando la rete parte da un generatore o da una riserva. Da un raccordo non sa
partire, e si ferma.

**La prova che inchioda la causa.** Fondendo le quattro reti del lato secondario in una
sola — senza toccare **nessun pezzo e nessuna tubazione**, solo l'etichetta della rete
su 16 tubi — il documento esce, e i pezzi del grafo completato sono gli stessi uno per
uno. È la prova `test_il_difetto_si_chiude_fondendo_le_reti_secondarie`.

**Di chi è.** Non dell'agente. Il suo grafo è fedele al testo, coincide arco per arco
con la lettura manuale, e la scelta di raggruppamento è dichiarata apertamente nella
voce a16 («è una scelta di modello, non una frase del testo»). Il difetto è delle
**istruzioni**: §4.2 definisce cos'è una rete ma non dice mai **dove una rete può
cominciare**, né quanto finemente si taglia. Due letture ragionevoli producono due
grafi che il resto della catena tratta in modo diverso — e una delle due lo rompe.

**Non è un caso isolato, ed è il segnale che conta.** Due agenti in camere pulite
separate, che non si sono visti, hanno segnalato lo **stesso** buco senza suggerimenti:
il rapporto dell'impianto 2 (§4, «le istruzioni non danno un criterio per decidere se
un ramo che si stacca da un pezzo di deviazione sia una rete a sé») e quello
dell'impianto 5 (P3, «le istruzioni non dicono se si debba creare una rete in più,
allungarne una, o fonderle»). È la stessa firma che aveva fatto fermare il giro
interrotto.

**Come si ripara.** Due strade, una riga ciascuna:

1. §4.2 dice dove una rete comincia — su una macchina che genera, su una riserva o su
   un confine — e che i rami che si staccano da un raccordo restano nella rete da cui
   nascono; oppure
2. la tabella delle famiglie di linea impara a nominare una linea di riscaldamento che
   parte da un raccordo.

La prima è la correzione delle istruzioni, ed è quella che il collaudo indica: il grafo
di prima stesura non deve poter tagliare le reti in un modo che il resto della catena
non sa leggere. Fatta la correzione, la prova si rifà **da capo con un agente nuovo**,
come impone `CONSEGNA.md` §3.

**Come si riproduce.**

```
.venv/bin/python -m pytest tests/collaudo/test_collaudo_interprete.py -q
```

Il difetto è `test_il_documento_esce_per_tutti_e_cinque_gli_impianti`, marcato
`xfail(strict=True)` con il motivo scritto per esteso. La sua causa è inchiodata dalla
prova che segue, che passa.

---

## 4. Osservazioni, che non respingono

**R1 — due voci che chiedono conferma di cose già decise.** Nel quarto grafo, la voce
a1 chiede se sia corretto rappresentare la caldaia «combinata» con la voce base: ma
§4.1 lo decide già («comanda la descrizione, non l'aggettivo») e il catalogo non ha
un'altra voce. La voce a3 chiede se «configurato a quattro tubi» sia stato inteso bene:
il testo lo scrive. Nessuna delle due nasconde una scelta e nessuna delle due cambia il
grafo — costano solo tempo all'ingegnere che le legge. Non è la fattispecie che il
criterio 4 colpisce (una domanda che chiede **un dato** già scritto): nessun grafo
chiede una potenza, un volume o il regime. Ma il numero delle voci cresce senza un
criterio: 10, 11, 9, 12, 16 contro le 2÷4 della lettura manuale, e le istruzioni non
dicono mai quanto sia troppo.

**R2 — i confini sanitari, dichiarati in tre grafi su cinque.** L'allacciamento
dell'acquedotto e le utenze sono imposti da §4.3 («i circuiti sanitari entrano
dall'acquedotto, escono alle utenze»). I grafi 2, 3 e 5 lo dichiarano in una voce; l'1
e il 4 no. Nel 4 il testo li nomina tutti e due, quindi non serve; nell'1 il testo
nomina l'acquedotto e dice che «l'ACS viene prelevata in uscita», ma non nomina le
utenze. Non è né perdita né invenzione — è la trascrizione che §4.3 ordina — ma la
disparità mostra che le istruzioni non dicono se i confini vadano dichiarati.

**R3 — i nomi delle proprietà non hanno un vocabolario.** Tutti e cinque i rapporti lo
segnalano. I grafi hanno inventato `impiego`, `funzione`, `ruolo`, `qualifica`, `stato`,
`denominazione`, `regolazione`, `produzione_sanitaria`. Oggi non fa danno: nessuna
regola legge le proprietà per chiave (solo `layout/labels.py` le trasporta). Domani, se
qualcuno le leggerà, due esecuzioni della stessa istruzione produrranno chiavi diverse.

**R4 — l'ordine delle liste nel file segue l'ordine d'ingresso.** Rimescolando pezzi e
tubi nel file, il modello completato esce con le liste in un altro ordine — ma il
**contenuto** è identico (verificato su 20 rimescolamenti per ciascuno dei cinque
impianti) e il **documento finale è identico carattere per carattere** (impianti 1÷4;
il 5 non lo si può produrre). Vale allo stesso modo per le letture manuali, quindi non
riguarda l'interprete. L'esito è deterministico.

**R5 — le contraddizioni segnalate dai rapporti che NON hanno prodotto un grafo
sbagliato.** Per obbligo di metodo, ognuna è stata verificata:

| Segnalazione | Ha prodotto un pezzo perso o inventato? |
|---|---|
| «Un terminale rappresentativo» (§7) contro «gli attacchi obbligatori si collegano tutti» (§4.3), sul collettore a due uscite dell'impianto 3 | **no**: il testo dice «più circuiti», cioè almeno due; due è il minimo che il plurale consente, è dichiarato, e la lettura manuale fa lo stesso |
| Il collettore di catalogo copre la sola mandata e non i ritorni | **no**: il collettore resta (è nominato dal testo), i ritorni si chiudono con la confluenza, tutto dichiarato; identico al metro |
| Il regime quando le potenze ci sono per una macchina sola (impianto 3) | **no**: 8 kW, regime ricavato e dichiarato; l'altra lettura darebbe lo stesso esito |
| `carries_on_board` mai nominato dalle istruzioni | **no**: il circolatore a bordo non è stato disegnato e la cosa è dichiarata in tutti i grafi interessati |
| Le due uscite della deviatrice non hanno semantica | **no**: sono simmetriche, il grafo non cambia |
| L'ordine delle catene di raccordi non è prescritto | **no**: il conto N−1 è rispettato, i pezzi sono gli stessi |
| La derivazione è ammessa da §5 ma il suo braccio è uno stub vietato da §4.3 | **no**: nessun grafo usa derivazioni |
| Le due liste di §5 non coprono tutti i mestieri (`air_separation`, `gas_combustion`…) | **no**: nessun testo li nomina |
| `project_id` e `project_name` non normati | **no**: sono metadati del documento, fuori dal confronto |
| Accenti sì o no nel JSON | **no**: cosmetico |
| Il taglio delle reti (rapporti 2 e 5) | **SÌ** → difetto 1 |

Dieci segnalazioni su undici sono imprecisioni delle istruzioni che hanno comunque
prodotto un grafo fedele e dichiarato. Una sola ha rotto qualcosa, ed è quella che
respinge.

---

## 5. Cosa è stato fatto girare, e cosa non è stato toccato

**Prove eseguite** (tutte in `tests/collaudo/test_collaudo_interprete.py`, che gira con
`.venv/bin/python -m pytest tests/collaudo/test_collaudo_interprete.py`):

- caricamento dei cinque grafi;
- ferramenta, mestieri ammessi, un attacco una tubazione, verso, fluido, attacchi di
  servizio, attacchi obbligatori scoperti, forma del file;
- regime ricavato per tutti e cinque, e mai chiesto;
- dati del testo trascritti; esclusioni, nomine di ferramenta e regolazione dichiarate;
- conto dei raccordi N−1, impianto per impianto, con il motivo scritto;
- i tre circuiti secondari del quinto impianto, e i loro tre circolatori;
- ogni pezzo che non è raccordo né confine risale a una parola del testo;
- corrispondenza arco per arco con la lettura manuale (impianti 1÷4) e con le due
  differenze note (impianto 5);
- il completatore digera i cinque grafi e non lasci punti aperti;
- determinismo del completatore su 20 rimescolamenti, e del documento finale su 20
  rimescolamenti (impianti 1÷4);
- il difetto, e la prova che ne inchioda la causa.

**Non toccato, come impone il contratto:** le istruzioni, i cinque grafi della camera
pulita, le letture manuali, e ogni altro file del repository. L'unico file nuovo è la
prova; il verbale sta fuori dal repository.

**Stato della cartella del collaudo dopo l'aggiunta** (`.venv/bin/python -m pytest
tests/collaudo -q`): `6 failed, 274 passed, 12 xfailed`. Le 6 rosse sono, una per una,
quelle già note sull'artefatto pubblicato del quinto impianto
(`test_p4_indirizzo_dei_nodi` × 4 e `test_p5_regime_e_tratto_comune` × 2, tutte sul file
`docs/prodotto/grafi-di-prova/prova-5-*` non ancora rigenerato). I 12 `xfail` sono gli
11 dell'altro collaudo più il difetto 1 di questo. **Il file nuovo non aggiunge nessuna
rossa.**

**Attribuzioni tenute separate:** le sei prove rosse dell'artefatto pubblicato del
quinto impianto e gli undici `xfail` del collaudo delle correzioni del completatore non
riguardano l'interprete e non sono entrate in questo verbale, salvo dove il secondo
tocca il metro (le letture manuali non portano le potenze in `properties`) — e in quel
punto la differenza è stata classificata come povertà del metro, terzo esito, non come
difetto dell'interprete.
