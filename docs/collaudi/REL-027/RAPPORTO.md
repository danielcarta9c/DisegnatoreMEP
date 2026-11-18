# REL-027 — Il listino a più fornitori, e dove comprare — rapporto

**18 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md` (I-302 … I-305). Ramo `claude/peaceful-brown-lnxll7`.

## 1. Prima di tutto: nessuna tavola

**Il pacchetto non tocca il disegno, e non esce nessuna tavola nuova.** Il banco resta identico (§2, criterio 6).
Quello che il PO guarda al posto delle tavole è **il costo della minuteria con «Dove comprare» sulla sua commessa**:
`docs/collaudi/REL-027/pr-mi-059/costo-minuteria.md` (§3).

## 2. I criteri, con il comando e l'output

**Criterio 1 — tutte le righe dei tre documenti, col fornitore.** In sessione, l'estrazione dai PDF (che non entrano
nel repository) dà 4 + 42 righe Abbattista e 81 Idrosanitaria, e i totali tornano con quelli dei documenti:

```
Counter({('Idrosanitaria', 'XC/STD/2704331'): 81, ('Abbattista', 'OC-STD-0188404'): 42, ('Abbattista', 'OC-STD-0185611'): 4})
{'OC-STD-0185611': 1058.62, 'OC-STD-0188404': 1547.12, 'XC/STD/2704331': 10835.01}
```

(Idrosanitaria: 10.835,01 € è il «Tot. Merce» del preventivo; con 8,75 € di RAEE l'imponibile è 10.843,76 €, come sul
documento.) Nel listino, ogni riga c'è una volta, col suo fornitore e il suo Rif.:

```
$ python3 -m pytest tests/distinta/test_i_fornitori.py -q -k ogni_riga
1 passed
```

Il listino rev. 06 si legge — 259 codici, 338 prezzi:

```
06, 18 novembre 2026 259 codici; 338 prezzi
Counter({'Tecnomat': 150, 'riferimento online': 95, 'Idrosanitaria': 55, 'Abbattista': 34, 'Bricoman': 4})
{'Tecnomat': True, 'Abbattista': True, 'Idrosanitaria': True, 'Bricoman': False}
```

Abbattista 34 = 46 righe − 3 apparecchiature − 9 senza ID; Idrosanitaria 55 = 81 − 10 apparecchiature − 16 senza ID.

**Criteri 2, 3 e 4 — più prezzi per codice, il più basso fra chi si ordina, «Dove comprare».**

```
$ python3 -m pytest tests/distinta/test_i_fornitori.py -q
..........                                                               [100%]
10 passed
```

Le prove: due fornitori, due prezzi; lo stesso codice due volte dallo stesso fornitore ferma il listino
(«I01 ha due prezzi da Alfa»); un fornitore che la tabella non ha lo ferma; una riga «—» non si legge; un fornitore
che non si ordina vale solo dove nessun altro ha l'articolo; l'ordine va al più economico, somma le quantità per
articolo, e le combinazioni confrontano sugli stessi articoli; sulla distinta di prova del repository il totale degli
ordini più gli articoli senza fornitore è il totale del costo; `distinta --costo` scrive «Dove comprare» nel Markdown e
l'ordine nel JSON (versione 2).

**Criterio 5 — la misura su PR.MI.059**: §3. **Criterio 8 — un fornitore solo e `--fornitori`**: §3bis. **Criterio 9 — gli scostamenti come avvisi**: §4.

**Criterio 6 — nessuna tavola cambia** e **criterio 7 — suite, ruff, mypy, release**: §6.

## 3. La misura su PR.MI.059

Il grafo della commessa non c'è: le voci vengono dalla lista materiali rev. 01 che la skill ha scritto
(`pr-mi-059/voci.json`, 91 voci, con i codici che le regole danno a ciascuna, senza dati del committente). Le quantità
sono **quelle nette della lista**, non maggiorate: la frase sul +15% che il file del costo scrive di suo, qui, non vale.
I numeri sono quelli con le disposizioni del PO di §4 (la marca non conta, gli scostamenti sono avvisi).

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
voci 91, prezzate 82, da prezzare 9; totale 2065.98 €
ordine: 1928.43 € + senza fornitore 137.55 €
un fornitore solo (articoli in comune: 20):
  Tecnomat       ha 38 ( 1346.30 €), non ha 23 ( 732.06 € altrove): totale  2078.36 €; sugli articoli in comune   825.74 €
  Idrosanitaria  ha 51 ( 1820.22 €), non ha 10 ( 288.17 € altrove): totale  2108.39 €; sugli articoli in comune   886.05 €
  Abbattista     ha 26 ( 1177.12 €), non ha 35 (1137.23 € altrove): totale  2314.35 €; sugli articoli in comune  1105.62 €
  Idrosanitaria: 32 articoli, 1251.88 €
  Tecnomat: 27 articoli, 646.58 €
  Abbattista: 2 articoli, 29.97 €
  Idrosanitaria                            scoperti 10    1820.22 €  + 179.96 €
  Tecnomat                                 scoperti 23    1346.30 €  + 149.93 €
  Abbattista                               scoperti 35    1177.12 €  + 385.92 €
  Idrosanitaria + Tecnomat                 scoperti  1    1930.76 €  +   5.95 €
  Abbattista + Idrosanitaria               scoperti  9    1810.20 €  + 166.32 €
  Abbattista + Tecnomat                    scoperti 17    1375.28 €  + 121.82 €
  Abbattista + Idrosanitaria + Tecnomat    scoperti  0    1928.43 €  +   0.00 €
solo la pompa di calore: 1228.50 € in 3 ordini
  Idrosanitaria: 20 articoli, 775.37 €
  Tecnomat: 19 articoli, 423.16 €
  Abbattista: 2 articoli, 29.97 €
  Idrosanitaria                            scoperti  5    1300.15 €  + 156.08 €
  Tecnomat                                 scoperti 12    1112.18 €  + 146.32 €
  Abbattista                               scoperti 15    1177.12 €  + 385.92 €
  Idrosanitaria + Tecnomat                 scoperti  1    1230.83 €  +   5.95 €
  Abbattista + Idrosanitaria               scoperti  4    1290.13 €  + 142.44 €
  Abbattista + Tecnomat                    scoperti  6    1141.16 €  + 118.21 €
  Abbattista + Idrosanitaria + Tecnomat    scoperti  0    1228.50 €  +   0.00 €
articoli in comune Abbattista-Idrosanitaria: 28; meno caro Abbattista 5, Idrosanitaria 23; alle quantità della lista Abbattista 1262.13 €, Idrosanitaria 1111.32 €
avviso A06c: Idrosanitaria 30.81 € ⚠ attacco posteriore (la voce: laterale)
avviso I47: Tecnomat 24.61 € ⚠ senza disconnettore nel titolo: la voce lo chiede (I-309)
avviso I47: Abbattista 67.59 € ⚠ il disconnettore non è nel titolo: la voce lo chiede (I-309)
avviso I44: Tecnomat 5.33 € ⚠ fondo scala 0–12 bar: la voce chiede 0–6 (I-308)
avviso I44: Abbattista 7.35 € ⚠ attacco 3/8" (la voce: ½")
circuito idraulico della pompa di calore (P-S, P-I): 42 voci; ordine diviso 1174.33 € + senza fornitore 0.00 €
  Idrosanitaria: 20 articoli, 775.37 €
  Tecnomat: 16 articoli, 368.99 €
  Abbattista: 2 articoli, 29.97 €
  Idrosanitaria                            scoperti  2    1300.15 €  + 156.08 €
  Tecnomat                                 scoperti 12    1058.01 €  + 146.32 €
  Abbattista                               scoperti 12    1177.12 €  + 385.92 €
  Idrosanitaria + Tecnomat                 scoperti  1    1176.66 €  +   5.95 €
  Abbattista + Idrosanitaria               scoperti  1    1290.13 €  + 142.44 €
  Abbattista + Tecnomat                    scoperti  6    1086.99 €  + 118.21 €
  Abbattista + Idrosanitaria + Tecnomat    scoperti  0    1174.33 €  +   0.00 €
```

**Che cosa dice, in parole.**

- **L'ordine diviso**: 1.928,43 € in tre ordini — Idrosanitaria 32 articoli (1.251,88 €), Tecnomat 27 (646,58 €),
  Abbattista 2 (29,97 €: i giunti antivibranti 1¼" e il raccordo 16 × ½"). Due ordini, Idrosanitaria più Tecnomat,
  costano 5,95 € in più di tre.
- **Un fornitore solo** (§3bis): Tecnomat 2.078,36 €, ma 23 articoli li deve comprare altrove; Idrosanitaria
  2.108,39 €, e altrove ne compra solo 10.
- **Abbattista contro Idrosanitaria**, sui 28 articoli che hanno tutti e due: Idrosanitaria costa meno su 23, alle
  quantità della lista 1.111,32 € contro 1.262,13 € (−12%). Anche sugli articoli costosi che il PO compra da Abbattista
  (§5 del listino): volano Cordivari UP GBF 80, stesso codice, 156,49 € contro 179,29 €; valvola di zona Caleffi 6443,
  stesso codice, 143,33 € contro 156,29 €; circolatore Evosta 2 40-70/130, 93,60 € contro 96,52 €.
- **Gli avvisi sul prezzo**: il gruppo di riempimento senza disconnettore (Tecnomat 24,61 €, Abbattista 67,59 €,
  contro 153,01 € di quello con disconnettore di Idrosanitaria) e il manometro (Tecnomat 0–12 a 5,33 €, Abbattista
  da 3/8" a 7,35 €, contro il 0–6 da ½" di Idrosanitaria a 9,84 €): 132,91 € di risparmio possibile, se lo
  scostamento va bene. Il porta-bocchetta 400×200 c'è solo con l'attacco posteriore: preso, e avvisato.
- **Le offerte vere, sullo stesso perimetro** (il circuito idraulico della pompa di calore con la valvola di zona):
  Abbattista 1.703,41 € (l'ordine del 13 novembre, 1.547,12 €, più la valvola di zona dell'ordine del 10, 156,29 €),
  Idrosanitaria 1.327,85 € (righe 6–48 del preventivo). Le offerte comprano confezioni intere (barre, rotoli) e qualche
  pezzo che la lista non chiede (§5, punto 7); il conto della skill è il consumo, 1.174,33 €. Non sono la stessa
  misura, e non le metto in fila come se lo fossero.

## 3bis. Un fornitore solo (I-306, criterio 8)

Il PO, visto il funzionamento: «in base al cantiere posso magari dividere l'ordine in più fornitori o scegliere un solo
fornitore per tutta la minuteria e la skill mi dice quale è il fornitore più economico per il totale prezzo». In
«Dove comprare» c'è ora **«Un fornitore solo»**: per ogni fornitore il totale della minuteria comprata da lui, sullo
stesso paniere (quello che non ha, dal più economico degli altri), e il conto sugli articoli che hanno tutti. E
`distinta --costo --fornitori <nomi>` manda l'ordine soltanto ai fornitori scelti.

Su PR.MI.059 (l'output è in §3): il più economico come fornitore unico è **Tecnomat**, 2.078,36 €, sui 20 articoli
che hanno tutti 825,74 € contro 886,05 € di Idrosanitaria e 1.105,62 € di Abbattista. **Ma Tecnomat non ha 23 articoli**
(i 732,06 € che andrebbero comprati altrove: i porta-bocchetta, il flessibile coi collari e le fascette, le guaine da 9 e da 32 mm, la condensa, il gruppo di riempimento col disconnettore, il gruppo di sicurezza del bollitore, i nippli in ghisa),
mentre a Idrosanitaria ne mancano 10: per un ordine solo davvero, oggi, è Idrosanitaria quella che copre la commessa,
a 30,03 € in più di Tecnomat sul totale. Il listino Tecnomat è il rilievo del 2 novembre: completarlo cambierebbe il
conto.

## 4. Il prezzo più basso e la prescrizione (I-307 … I-310)

**Il rilievo.** Il conto confronta le righe che hanno lo stesso ID, e la prima versione prendeva il prezzo più basso
anche quando l'articolo non rispettava la voce: il gruppo di riempimento «Filler» di Tecnomat (24,61 €, senza
disconnettore nel titolo) contro 67,59 € e 153,01 €; il manometro 0–12 bar contro il 0–6 della voce.

**La disposizione del PO** (18 novembre 2026): «la marca non mi interessa … mi interessa solo che rispettino le
prescrizioni. queste la skill puo' anche evidenziarle se ci sono lievi sconstamenti … mi mette un alert sul prezzo,
certo se ho messo un gruppo di sicurezza su AF verso il boiler ACS non è che la skill decide di cambiarlo con una cosa
che fa un mestiere diverso» (I-307); «Il manometro da 0-12 bar … tanto vale mettere quello da 6» (I-308); «lo scopo
principale è risparmiare sulla minuteria. Non voglio comprare cose che sono utili ma non necessarie» (I-310).

**Come è fatta.** Nel listino una nota che comincia con ⚠ è uno scostamento dalla voce; il conto sceglie il più
economico fra gli articoli che la rispettano, e quello con ⚠ che costa meno diventa un avviso col risparmio; senza un
articolo conforme si prende quello con ⚠, avvisato. La marca non è uno scostamento: la deviatrice Giacomini di
Tecnomat (92,95 €) vale la Caleffi 6443 (143,33 €, 156,29 €), la valvola di sicurezza RBM vale la Caleffi. Le righe
segnate, dai titoli degli articoli:

| ID | Fornitore | Lo scostamento |
|---|---|---|
| I47 gruppo di riempimento con disconnettore | Tecnomat, Abbattista | il disconnettore non è nel titolo |
| I44 manometro 0–6 bar ½" | Tecnomat | fondo scala 0–12 (I-308) |
| I44 manometro 0–6 bar ½" | Abbattista | attacco 3/8" |
| I77 rubinetto portamanometro ½" | Abbattista | attacco 3/8" |
| A06c porta-bocchetta 400×200, attacco laterale | Idrosanitaria | attacco posteriore |

**Il disconnettore (I-309), per il PO.** Il disconnettore (tipo BA, a zona di pressione ridotta controllabile) sta
sulla linea di riempimento e impedisce che l'acqua dell'impianto torni nell'acquedotto. Le schede dei produttori lo
legano alla EN 1717: l'acqua di riscaldamento **con inibitori** è un fluido di categoria 4, e contro la categoria 4 ci
vuole il BA (Resideo NK300S; Kemper FG 3650G); Caleffi consiglia sempre il gruppo di riempimento col disconnettore
(Caleffi 01061, 01125). In questa commessa la lista mette il filmante-inibitore (P-I.24): un gruppo senza disconnettore
non rispetta la voce. **Non ho letto il testo della EN 1717**, né verificato se in Italia sia un obbligo per ogni
impianto: sono schede di produttori. Il risparmio del Filler (128,40 €) resta un avviso.

**Che cosa non ho fatto**: classificare righe dove il titolo non basta (il nastro in alluminio contro quello in gomma
per le giunte, il sifone «a secco» contro «ispezionabile»): restano conformi finché il PO non dice altro.

## 5. Come ha lavorato la skill sulla lista (I-305)

Due fornitori hanno letto la stessa lista; dove l'hanno letta in modo diverso, la lista non era chiara, o loro hanno
deviato.

1. **La lista non viene da `main`.** Dice «quantità nette, senza maggiorazioni né scorte» — è `REL-025`, la 2.2, non
   ancora fatta — e la voce «Piedini antivibranti per pompa di calore a terra» non è nelle regole del repository (che
   dicono «Basamento a terra per l'unità esterna con supporti antivibranti»). La sessione che l'ha scritta lavorava su
   una copia cambiata, come per BD.RM.260 (I-300): **quelle modifiche, se servono, vanno riportate nel repository**,
   o si perdono.
2. **«Raccordo diritto a pressare M × tubo …, all'attacco»** senza il pollice: Idrosanitaria l'ha letto come un
   **manicotto** tubo-tubo (righe 40, 42, 47: il pezzo sbagliato), Abbattista ha dovuto supporre il pollice («quotato
   M 32×1», «quotato ½" M»). La voce dovrebbe dire il pollice dell'attacco. Proposta, non fatta: tocca il testo della
   distinta.
3. **Tubo nudo e guaina**: Abbattista ha offerto il multistrato **rivestito con guaina da 6 mm** al posto del nudo con
   la guaina da 19 e 30 mm della lista. La lista era chiara: è l'offerta che non la rispetta, e va detto al fornitore.
4. **Il manometro**: Abbattista ha messo il kit ISPESL da 3/8" (manometro, serpentina, rubinetto); la lista chiede ½".
   E ha aggiunto l'**imbuto di scarico** Caleffi 5521 per la sicurezza «con scarico convogliato», che la lista non
   conta a parte. Se l'imbuto va contato è contenuto MEP: decide il PO.
5. **La climatizzazione** (solo Idrosanitaria): canalina D100 al posto della 110×75, derivazione a Y 250-200-150 al
   posto di 1×Ø200 > 2×Ø200, 5 collari Ø200 contro 21 sostegni, il giunto antivibrante in tela in rotolo da 25 m,
   il plenum di ripresa «indicativo».
6. **Le quantità**: i fornitori arrotondano alla confezione (barre da 5 m: 10 m per 8, 30 per 28, 5 per 3; rotoli da
   50 e 25 m). Normale; il conto della skill lo dice nella colonna Confezione.
7. **L'utile che non serve (I-310)**: Abbattista ha messo nell'ordine quattro articoli che la lista non chiede —
   l'imbuto di scarico (22,76 €), la serpentina del manometro (9,91 €), due staffe per i vasi (29,03 €, la voce del
   vaso le comprende già), 14 supporti rapidi per i collari (16,79 €): 78,49 €. L'ordine della skill conta solo gli
   articoli della distinta, e non li aggiunge.

## 6. Le prove di sempre

**Criterio 6 — nessuna tavola cambia.** Il banco, prima di registrare:

```
$ python3 -m pytest -q   (prima esecuzione, sul ramo)
FAILED tests/test_il_banco.py::test_la_tavola_e_quella_registrata[t1-rel023]
FAILED tests/test_il_banco.py::test_la_tavola_e_quella_registrata[plenum-di-mandata-rel026]
FAILED tests/test_il_banco.py::test_la_tavola_e_quella_registrata[plenum-motorizzato-rel026]
3 failed, 3166 passed, 15 skipped, 11 xfailed in 410.81s
```

In tutti e tre il solo file cambiato è `distinta/distinta.json` (`~ distinta/distinta.json: cambiato`): **nessun SVG,
nessuna tavola**. Rifatti i tre casi su `main` (una copia di lavoro di `origin/main`: «3 uguali, 0 cambiati») e sul
ramo, la differenza è **una riga per file**, l'impronta delle regole della distinta, che cambia perché le regole sono
cambiate (§7):

```
<   "impronta": "13d6f4ef01e2a96a"
>   "impronta": "f86a5832c1d1821c"
```

(e la stessa impronta nella testa di `distinta-calcoli.md`, che il banco non impronta). Il documento per
l'installatore è identico. Registrate le tre impronte (`python3 scripts/banco.py --registra --caso …`), il banco:

```
$ python3 -m pytest tests/test_il_banco.py -q
31 passed in 28.67s
```

**Criterio 7.**

```
$ python3 -m pytest -q   (stato finale)
3174 passed, 15 skipped, 11 xfailed in 554.44s

$ ruff check src tests
All checks passed!

$ mypy
Success: no issues found in 132 source files

$ python3 scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (156 file, 3733 kB)
ZIP:   …/outputs/skill/disegnatore-mep.zip (1163 kB, sha256 80245662bb72d28f)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.

$ python3 -m pytest tests/test_le_release.py tests/test_package.py tests/skill -q
50 passed in 13.33s
```

Skip e xfail: 15 e 11, gli stessi della prima esecuzione; il diff delle prove non aggiunge nessun `skip` né `xfail`
(`git diff origin/main -- tests | grep -E "^\+.*(skip|xfail)"`: vuoto). Le prove nuove sono 15
(`tests/distinta/test_i_fornitori.py`); due prove vecchie cambiano perché il dato è cambiato apposta: la revisione del
listino (05 → 06) e il prezzo del tubo da 32, che ora si legge per fornitore
(`test_il_corredo_idronico_e_il_costo.py`); il codice del nipplo ridotto (I78a → I83e, `test_le_giunzioni.py`).

Dati personali nel diff: cercati il nome e l'indirizzo del committente, i nomi e i telefoni degli addetti, l'email del
PO — nessuno.

## 7. Le scelte della sessione, e che cosa decide il PO

- **I PDF non entrano nel repository** (dati personali, repository pubblico): entrano le righe di prezzo. Con il
  listino pubblico, **gli sconti di Abbattista sono leggibili da chiunque**: se non va bene, è una decisione del PO.
- **Il prezzo che il conto usa** è il più basso fra i fornitori da cui si ordina; Bricoman è «si ordina: no» (prezzi
  dalle fatture di un installatore): se il PO vuole, si cambia una parola nel listino.
- **Gli ID nuovi** (I83e, I84a–c, I85, I86, I87, A06c, A07c, A08c) solo dove una regola li usa; le regole cambiano
  **solo il prezzo**, non che cosa la distinta conta. Il nipplo ridotto 1¼" × 1" passa dalla riduzione M × F (I78a,
  un ripiego) al nipplo vero (I83e); il collare del tubo della condensa dal collare del multistrato (I63) alla clip
  (I87). La prova del nipplo ridotto è aggiornata per questo (`tests/distinta/test_le_giunzioni.py`).
- **Il numero 2.1.1**: proposta; `REL-025` resta la 2.2.
- **Decide il PO**: le apparecchiature nel consiglio (oggi fuori, D-235); il rame «CONDY» (rivestito o no); le righe
  del §1 che non sono la voce (§4); il pollice nei raccordi «all'attacco»; l'imbuto di scarico.
