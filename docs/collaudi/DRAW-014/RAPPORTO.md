# RAPPORTO DI CONSEGNA — DRAW-014

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «Tutte e cinque le tavole escono»
**Disposizioni di riferimento:** **D-147** (agente unico), **D-148** (oltre l'A3 si va),
**D-149** (il riempimento esce dagli obiettivi), **D-150** (la tratta persa non uccide la tavola)
**Ruolo:** l'agente unico (D-147)
**Data:** 2026-09-19

---

## 0. LE TAVOLE (D-146)

*(da completare con i cinque PDF e il loro percorso)*

| Impianto | Formato | Tratte cedute | Pieghe | Attrav. | Margine | Riempimento |
|---|---|---|---|---|---|---|
| 1 — due PdC con accumulo combinato | A3 | 0/21 | 8 | 2 | 25,0 mm | 38 % |
| 2 — PdC con deviatrice e ACS | A3 | 0/23 | 5 | 1 | 25,0 mm | 67 % |
| 3 — PdC diretta a pavimento | *(in corso)* | | | | | |
| 4 — ibrido PdC + caldaia | **A2** | **0/25** | 18 | 8 | 25,0 mm | 30 % |
| 5 — cascata di tre PdC | **A1** | **7/54** | 50 | 22 | 12,5 mm | 31 % |

**Le tavole 4 e 5 non erano mai uscite** in tutta la storia del progetto.

---

## 1. Le tre cose da guardare per prime, e due non sono buone

### 1.1 La tavola 4 esce **pulita**, e bastava il foglio

Zero tratte cedute: non è degradata, è **risolta**. Il ripiego di D-150 non si è nemmeno
acceso. È stato sufficiente il formato più grande, che è esattamente ciò che il PO aveva
ipotizzato — «tanto lo scopo sarà esportare un dxf che viene ri-finito in autocad».

Resta un **rilievo bloccante vero**, che non c'entra col formato: la tratta `p11-a, p11-b`
supera di 25 mm la propria porta di arrivo e ci torna indietro. La tavola esce marcata
«verifica» per quello. **È una causa da curare**, non un effetto del ripiego.

### 1.2 La tavola 5 è degradata: 7 tratte su 54

Escono tratteggiate fitte e il preflight le nomina una per una con un rilievo bloccante.
Vanno guardate sapendo che **quelle sette linee non evitano niente** e che i loro accessori
in linea possono mancare.

**Un'ipotesi che ho fatto e che era sbagliata.** Avevo pensato a una valanga: una tratta
ceduta occupa celle, e le successive cadono per colpa sua. Ho corretto il meccanismo — la
spezzata di ripiego non entra più fra le celle occupate né fra i tratti percorsi — e
**le sette sono rimaste sette**. Sono indipendenti. La correzione resta perché è giusta in
sé (una linea che è una finzione non deve vincolare quelle vere), ma **non ha cambiato nulla
di misurato**, e va scritto invece che lasciato credere.

### 1.3 La tavola 1 **peggiora**, e la causa è la disposizione del PO

Da **4 pieghe e 1 attraversamento a 8 e 2**. Misurato con un A/B netto — stesso impianto,
stessa via di composizione (`le fasi`), solo la chiave di costo cambiata:

```
senza riempimento (oggi)     pieghe=  8 attrav=  2  via: le fasi
con riempimento (PR #44)     pieghe=  4 attrav=  1  via: le fasi
```

**Il meccanismo, e non è quello che sembra.** Pieghe e attraversamenti stanno **prima** del
riempimento nella chiave: una mossa che li peggiora non può vincere, né prima né adesso.
Quindi il riempimento non ha mai *comprato* una piega. Faceva un'altra cosa: **da spareggio
fra mosse di pari costo**, e quello spareggio — per caso, non per progetto — spingeva la
ricerca greedy verso un minimo migliore. Era una stampella, non un criterio.

**Non l'ho rimessa.** Il PO ha giudicato il disegno e non il numero, e il disegno è quello
che ha in mano. Se guardando il PDF la tavola 1 gli sembra peggiore, la strada è uno
spareggio **neutro** che recuperi il 4/1 senza rimettere il riempimento come obiettivo — non
il ritorno di D-140.

---

## 2. Perché le tre tavole non uscivano — la misura, prima del codice

Fatta il 19 settembre **prima di toccare qualunque riga**. Tutt'e tre morivano per **una
sola tratta**, e tutt'e tre contro il **bordo destro dell'area A3**:

| Impianto | Messaggio del motore | Che cos'è in millimetri |
|---|---|---|
| 3 | `give the run a longer straight length` | non c'è rettilineo |
| 4 | `no route from (134, 80) to (144, 80)` | la destinazione è a **x 370** su una griglia che finisce a **x 360**: è fuori dal foglio |
| 5 | `run into an obstacle at (140, 65)` | «l'ostacolo» è **x 360,0 mm**, cioè il bordo stesso |

Provati **direttamente su A2**, saltando la scala:

| | esito su A2 | |
|---|---|---|
| 4 | **OK**, 195 s | il foglio era tutto il problema |
| 5 | FAIL | ostacolo **vero**: un pezzo a due passi dove ne servono cinque |
| 3 | FAIL, 1099 s | stacco di **5 mm** con un accessorio in linea che ne chiede **7,5** |

Cioè: il formato ha chiuso l'impianto 4 e ha **cambiato natura** al difetto degli altri due,
da «non c'è foglio» a un difetto vero e locale. Sono quelli le cause da curare.

### 2.1 La causa della tavola 3, trovata e **non** curata qui

Lo stiramento che esiste apposta per «far entrare il corredo dove non ci sta» è offerto
**solo alle autostrade** (`improve.py`, `_stretch_moves`: `if self.hierarchy[...] is not
Level.AUTOSTRADA: continue`). La tratta che fallisce è lo stacco di un vaso d'espansione,
che autostrada non è: la mossa che la salverebbe non le viene mai proposta.

**Non l'ho toccato in questo giro**, ed è una scelta che dichiaro: estendere lo stiramento
cambia la posa anche delle tavole che oggi funzionano, e con un giro di misura che costa
decine di minuti non potevo separare quell'effetto dal resto. È la prima voce del lavoro
successivo.

---

## 3. Che cosa è cambiato nel motore

| File | Che cosa |
|---|---|
| `graphics/standard.py`, `graphics/frame.py` | **A2 e A1** entrano fra i formati ordinari (D-148) |
| `layout/route.py` | `_last_resort`, la spezzata di ripiego; `route_sheet` impara `tolerant` |
| `layout/inline.py` | `last_resort`, **separato** da `tolerant` |
| `layout/compose.py` | il ripiego scatta solo a vie **e** formati finiti; la dilatazione è ritirata |
| `layout/improve.py` | il riempimento e la copertura escono dalla chiave; `beats` torna una riga; `CostKey` a otto voci |
| `layout/geometry.py` | `RoutedTrunk.unresolved` |
| `validation/preflight.py` | `RUN_UNRESOLVED`, bloccante e **primo** dell'elenco; i messaggi del riempimento dicono che è una misura |
| `graphics/sheet.py` | il tratteggio fitto della tratta ceduta |
| `cli.py` | una tavola già dichiarata incompleta non si misura come una completa |
| `scripts/tavole-dei-cinque.sh` | **nuovo**: i cinque impianti in parallelo, con l'esito su una riga |

---

## 4. I due confini che tengono onesto il ripiego

Sono la parte pericolosa di D-150, e `tests/layout/test_ripiego_dichiarato.py` li difende.

1. **Non anticipa la scala dei formati.** Se scattasse prima, *ogni* foglio riuscirebbe e
   l'impianto finirebbe sull'A4 degradato invece che sul primo che lo regge davvero. La prova
   verifica l'ordine esatto delle chiamate: quattro formati provati sul serio, e **poi** il
   ripiego sul più grande.
2. **Non entra nel ciclo di miglioramento.** Il ciclo usa l'errore per scegliere una posa
   migliore; con il ripiego acceso accetterebbe come buone proprio le pose da scartare. I due
   interruttori — `tolerant` e `last_resort` — restano separati, e una prova legge l'albero
   sintattico di `improve.py` per accertarsi che il ciclo non accenda il secondo.

**Un difetto trovato da una prova, non a mano:** `_last_resort` degenerava su due porte che
si guardano a un passo, restituendo `(a, b, a, b)` — una spezzata che si ripercorre. Corretto.

---

## 5. La suite

*(da completare)*

---

## 6. Quello che questo giro **non** chiude

- **Le cause vere delle tavole 3 e 5**, e il rilievo bloccante della 4. Il PO ha scelto
  «prima degrada, poi curo le cause» (I-081): la prima metà si chiude qui.
- **Il formato definitivo.** D-148 è dichiarata momentanea dal PO stesso.
- **Il tempo di un giro.** La suite gira in decine di minuti e una tavola che scala fino
  all'A1 può costarne altrettanti — e la scala paga **tutti** i tentativi falliti prima di
  quello buono, che sono i più cari perché un instradamento che fallisce esplora la griglia
  intera. Con un'ora a giro una sessione ci sta dentro una volta sola, ed è metà della
  lentezza di questo progetto.
