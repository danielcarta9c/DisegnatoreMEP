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

**Criterio 5 — la misura su PR.MI.059**: §3.

**Criterio 6 — nessuna tavola cambia** e **criterio 7 — suite, ruff, mypy, release**: §6.

## 3. La misura su PR.MI.059

Il grafo della commessa non c'è: le voci vengono dalla lista materiali rev. 01 che la skill ha scritto
(`pr-mi-059/voci.json`, 91 voci, con i codici che le regole danno a ciascuna, senza dati del committente). Le quantità
sono **quelle nette della lista**, non maggiorate: la frase sul +15% che il file del costo scrive di suo, qui, non vale.

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
voci 91, prezzate 82, da prezzare 9; totale 1933.07 €
ordine: 1795.52 € + senza fornitore 137.55 €
  Idrosanitaria: 30 articoli, 1089.03 €
  Tecnomat: 29 articoli, 676.52 €
  Abbattista: 2 articoli, 29.97 €
  Idrosanitaria                            scoperti 10    1820.22 €  + 312.87 €
  Tecnomat                                 scoperti 21    1376.24 €  + 149.93 €
  Abbattista                               scoperti 32    1265.75 €  + 435.66 €
  Idrosanitaria + Tecnomat                 scoperti  1    1797.85 €  +   5.95 €
  Abbattista + Idrosanitaria               scoperti  9    1722.28 €  + 211.32 €
  Abbattista + Tecnomat                    scoperti 14    1418.91 €  + 126.56 €
  Abbattista + Idrosanitaria + Tecnomat    scoperti  0    1795.52 €  +   0.00 €
…
articoli in comune Abbattista-Idrosanitaria: 28; meno caro Abbattista 5, Idrosanitaria 23; alle quantità della lista Abbattista 1262.13 €, Idrosanitaria 1111.32 €
circuito idraulico della pompa di calore (P-S, P-I): 42 voci; ordine diviso 1041.42 € + senza fornitore 0.00 €
  Idrosanitaria: 18 articoli, 612.52 €
  Tecnomat: 18 articoli, 398.93 €
  Abbattista: 2 articoli, 29.97 €
  …
  Idrosanitaria + Tecnomat                 scoperti  1    1043.75 €  +   5.95 €
```

**Che cosa dice, in parole.**

- Su questa commessa **«Dove comprare» manda quasi tutto a Idrosanitaria e Tecnomat**: Abbattista vince due articoli
  (i giunti antivibranti 1¼" e il raccordo 16 × ½"), 29,97 €. Due ordini, Idrosanitaria più Tecnomat, costano 5,95 €
  in più di tre.
- **Abbattista contro Idrosanitaria**, sui 28 articoli che hanno tutti e due: Idrosanitaria costa meno su 23, alle
  quantità della lista 1.111,32 € contro 1.262,13 € (−12%). Anche sugli articoli costosi che il PO compra da Abbattista
  (§5 del listino): volano Cordivari UP GBF 80, stesso codice, 156,49 € contro 179,29 €; valvola di zona Caleffi 6443,
  stesso codice, 143,33 € contro 156,29 €; circolatore Evosta 2 40-70/130, 93,60 € contro 96,52 €.
- **Le offerte vere, sullo stesso perimetro** (il circuito idraulico della pompa di calore con la valvola di zona):
  Abbattista 1.703,41 € (l'ordine del 13 novembre, 1.547,12 €, più la valvola di zona dell'ordine del 10, 156,29 €),
  Idrosanitaria 1.327,85 € (righe 6–48 del preventivo). Le offerte comprano confezioni intere (barre, rotoli) e qualche
  pezzo che la lista non chiede (imbuto, serpentina, staffe dei vasi da Abbattista); il conto della skill è il consumo,
  1.041,42 €. Non sono la stessa misura, e non le metto in fila come se lo fossero.

## 4. Il rilievo più utile: il prezzo più basso non è sempre lo stesso articolo

**I numeri dicono che Tecnomat vince 29 articoli; ma per alcuni l'articolo Tecnomat del §1 non è la voce.** Il conto
confronta le righe che hanno lo stesso ID, e l'ID dice «la stessa voce della stessa misura»: se l'articolo sotto l'ID
non lo è, il prezzo più basso è falso. Su questa commessa:

| Voce | Tecnomat (vince) | Gli altri | Che cosa non torna |
|---|--:|---|---|
| I47 gruppo di riempimento con disconnettore | 24,61 € «Filler» | Abbattista 67,59 · Idrosanitaria 153,01 | il Filler non ha il disconnettore nel titolo; la voce lo chiede |
| I44 manometro 0–6 bar | 5,33 € (0–12 bar) | Abbattista 7,35 · Idrosanitaria 9,84 | il fondo scala (la nota del §1 lo dice) |
| I40a valvola di sicurezza ½" 3 bar | 13,07 € RBM | Idrosanitaria 27,14 (INAIL) · Abbattista 48,95 (ISPESL) | la certificazione, da verificare |
| I61 nastro per le giunte dell'isolamento | 5,57 € alluminio | Idrosanitaria 15,34 · Abbattista 24,55 (gomma 3 mm) | i fornitori hanno offerto il nastro anticondensa in gomma |
| I51 valvola deviatrice 1" | 92,95 € Giacomini | Idrosanitaria 143,33 · Abbattista 156,29 (Caleffi 6443) | marche diverse: equivalenti? |

Non ho cambiato le righe del §1: sono il rilievo del PO, e l'equivalenza di due articoli è un giudizio suo. **Domanda
per il PO**: le righe che non sono la voce si spostano su «—» (non entrano nel conto), o restano con la nota?

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
3169 passed, 15 skipped, 11 xfailed in 399.15s

$ ruff check src tests
All checks passed!

$ mypy
Success: no issues found in 132 source files

$ python3 scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (156 file, 3720 kB)
ZIP:   …/outputs/skill/disegnatore-mep.zip (1159 kB, sha256 89de7b4e66051d0e)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.

$ python3 -m pytest tests/test_le_release.py tests/test_package.py tests/skill -q
50 passed in 13.33s
```

Skip e xfail: 15 e 11, gli stessi della prima esecuzione; il diff delle prove non aggiunge nessun `skip` né `xfail`
(`git diff origin/main -- tests | grep -E "^\+.*(skip|xfail)"`: vuoto). Le prove nuove sono 10
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
