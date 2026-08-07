# Rapporto — Esempio 2, pompa di calore con deviazione tra climatizzazione e ACS

Consegna: `consegna/grafo.json` (valida, carica senza output), `consegna/rilettura.md`,
questo rapporto. Committente «Nove C», codice di commessa «PROVA», revisione 00,
data di emissione 2026-08-07.

---

## 1. Cosa ho capito dell'impianto

Una centrale piccola, a un solo generatore, che con una sola macchina serve due cose
diverse a turno.

**La generazione.** Una pompa di calore aria-acqua reversibile da 15 kW. È l'unica
macchina che genera calore, quindi la somma delle potenze di generazione è 15 kW: sotto i
35 kW, e il regime della centrale è `up_to_35_kw`. Il conto è aritmetica su un dato che
l'ingegnere ha già scritto, non un dimensionamento. La macchina è reversibile: d'estate
manda acqua refrigerata negli stessi tubi.

**La deviazione, che è il cuore dell'impianto.** Sulla mandata della pompa di calore c'è
una valvola a tre vie deviatrice — *devia*, non miscela: il testo dice «alternativamente
verso … oppure verso …», ed è il verbo a scegliere la voce di catalogo, non il numero
delle vie. Da lì il flusso va **o** al circuito di climatizzazione **o** al serpentino del
bollitore. Non contemporaneamente: è la stessa acqua di generazione che fa due lavori in
tempi diversi. La priorità al sanitario dice *quando*, e il *quando* non si disegna.

**Il lato climatizzazione.** Il ramo di climatizzazione entra in un volume tecnico da 100
litri «configurato a quattro tubi»: quattro attacchi di flusso, primario e secondario
separati. È il pezzo che disaccoppia la pompa di calore dai terminali — a catalogo la voce
dichiara insieme `thermal_storage` e `hydraulic_separation`, ed è per questo che quattro
attacchi contano: due li usa il primario, due il secondario. Dal secondario parte un
circuito con circolatore dedicato che alimenta i fan-coil e torna al volume. Quel circuito
lavora in riscaldamento e in raffrescamento, ma è **un** circuito, non due.

**Il lato sanitario.** Un bollitore con serpentino: il serpentino è attraversato
dall'acqua della pompa di calore e cede calore all'acqua del bollitore, che è tutt'altra
acqua — entra fredda dall'acquedotto in basso ed esce calda in alto. Sono due circuiti che
si toccano dentro lo stesso serbatoio senza mescolarsi, e il catalogo lo rende esplicito
con quattro attacchi di tre fluidi diversi (`coil_in`/`coil_out` acqua di riscaldamento,
`cold_in` acqua fredda, `dhw_out` acqua calda sanitaria). Il sanitario è un circuito
**aperto**: comincia all'acquedotto e finisce alle utenze. Il ricircolo è escluso per
iscritto.

**Il punto di topologia che il testo non nomina ma impone.** Il ritorno dal volume tecnico
e il ritorno dal serpentino del bollitore rientrano tutti e due sull'unico attacco di
ritorno della pompa di calore. Un attacco porta una tubazione sola: due tubazioni che si
incontrano in un punto vogliono un raccordo (§4.4, N=2 → N−1 = 1). Da qui il raccordo a T
di confluenza `rc-ritorni-primario`, che è l'unico componente del grafo che nessuna frase
del testo nomina, ed è dichiarato in a4.

**Quattro reti**, perché il fluido cambia dove una macchina lo cambia: `primario` e
`secondario` (acqua di riscaldamento), `acqua-fredda` (acqua fredda sanitaria) e `acs`
(acqua calda sanitaria).

**Cosa il testo nomina e il grafo non mostra**, perché è ferramenta del pezzo successivo
della catena: il carico automatico da acquedotto e lo scarico sul volume tecnico, e la
valvola miscelatrice sull'uscita sanitaria (mestiere `dhw_mixing`, esplicitamente nella
lista che non entra mai). Nessuna delle tre è andata persa: sono annotate in `assumptions`
proprio perché chi completa il grafo le rimetta al loro posto e l'ingegnere possa
verificarlo.

**In numeri:** 9 componenti, 11 tubazioni, 4 reti, 11 voci in `assumptions`, nessuna voce
di catalogo mancante (nessun tipo B), nessuna domanda di tipo C.

---

## 2. Le domande e le assunzioni, in chiaro

Sono le undici voci di `assumptions` nel JSON, tutte con `status: "proposed"`. Le divido
per quello che chiedono a chi legge, perché lo schema non ha un campo per distinguerle
(vedi §3, punto 3).

### 2a. Domande che aspettano una risposta dall'ingegnere (tipo A: il testo impone il collegamento, non dice con che pezzo)

| id | Domanda | Come ho chiuso il grafo nel frattempo |
|---|---|---|
| **a1** | Il testo non nomina un circolatore sul circuito primario. La circolazione è a bordo della pompa di calore, o c'è un circolatore esterno da disegnare? | Ho seguito la macchina di catalogo, che dichiara la circolazione a bordo. Nessun circolatore primario nel grafo. |
| **a2** | Il circuito secondario ha un «circolatore dedicato», ma il testo non dice su quale ramo sta. Mandata o ritorno? | Sulla **mandata** del secondario, subito a valle del volume tecnico: è la posizione convenzionale di disegno (§7), e per questo va dichiarata. |
| **a3** | «Fan-coil» è plurale e il numero non è detto. Quanti sono davvero, e vanno disegnati singolarmente? | Uno solo, rappresentativo dell'insieme (§7). |
| **a4** | Il ritorno dal volume tecnico e quello dal serpentino del bollitore rientrano sullo stesso attacco della pompa di calore: con che pezzo si uniscono? | Un raccordo a T di confluenza subito prima dell'attacco (§4.4). Se in centrale c'è invece un collettore o un separatore, va corretto. |
| **a10** | Il testo dice che l'acqua fredda entra in basso e l'ACS esce in alto, ma non nomina né l'allacciamento di acquedotto né le utenze. L'acqua fredda arriva da un punto già rappresentato altrove? | Ho disegnato le due voci di confine del catalogo: un circuito aperto deve avere un inizio e una fine (§4.3). |

### 2b. Annotazioni che non aspettano una risposta, ma servono a non perdere niente

| id | Cosa dice | Perché è lì |
|---|---|---|
| **a5** | La macchina è reversibile e i fan-coil lavorano anche in raffrescamento: negli stessi tubi d'estate corre acqua refrigerata. Le reti restano dichiarate `heating_water`. | La tabella dei fluidi non ha un fluido per il raffrescamento, e non se ne inventa uno (§4.2). |
| **a6** | La priorità sanitaria è regolazione, non topologia: sul grafo si vede la valvola deviatrice, non la priorità. | §4.5: la logica di regolazione non produce nodi né tubi, ma non deve sparire. |
| **a7** | Il carico automatico da acquedotto e lo scarico sul volume tecnico sono ferramenta di servizio: li aggiunge il pezzo che completa. | §5 e §7: l'accessorio nominato per dire *dove* sta un attacco resta fuori, ma la nomina si annota. |
| **a8** | La valvola miscelatrice sull'uscita sanitaria è ferramenta (`dhw_mixing`): l'ACS è disegnata dal bollitore direttamente alle utenze. | §5, dove la miscelatrice sanitaria è nominata per esteso nella lista che non entra mai. |
| **a9** | Il ricircolo ACS è escluso **per iscritto**: non è disegnato perché non c'è, non perché sia stato perso. | §4.5: le esclusioni esplicite sono informazione, e servono a chi legge dopo per non riaggiungerlo. |
| **a11** | Il ramo verso la climatizzazione e il ramo verso il bollitore condividono mandata e ritorno della pompa di calore, e sono tenuti in una rete sola (`primario`); il circuito dei fan-coil è una rete a sé. | Scelta di raggruppamento: non cambia né i pezzi né i tubi. Vedi §3, punto 2. |

### 2c. Domande di tipo C (la scelta è dell'ingegnere, e cambia il disegno)

**Nessuna.** Non ho trovato nel testo un punto in cui due letture ragionevoli producano
due grafi diversi ed entrambe siano corrette. Il testo è insolitamente esplicito sulla
topologia: dice dove sta la valvola («sulla mandata»), dove va ciascun ramo, cosa comprende
il circuito di climatizzazione, da dove parte il secondario, come il bollitore è collegato
alla pompa di calore, da dove entra l'acqua fredda e da dove esce l'ACS. Quello che tace
sono i **pezzi minimi** di chiusura, e quelli sono tipo A: ogni lettura ragionevole
produce lo stesso grafo a meno di un dettaglio.

### 2d. Voci di catalogo mancanti (tipo B)

**Nessuna.** Ogni mestiere che il testo nomina ha una voce in catalogo con gli attacchi
che servono a scrivere esattamente i collegamenti descritti: `heat_generation` →
`heat-pump-air-water`; `diversion` → `diverting-valve-3way`; `thermal_storage` +
`hydraulic_separation` a quattro attacchi → `buffer-four-port`; `circulation` →
`pump-circulator`; `emission` → `fan-coil`; `dhw_storage` con serpentino → `dhw-cylinder`;
`junction` → `tee-junction`; `boundary` → `cold-water-inlet` e `dhw-draw-off`.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questa è la parte che la prova misura. Ordino per quanto pesa.

### 1. `assumptions` fa due mestieri diversi, e non ha modo di distinguerli

§6 definisce `assumptions` come «ogni cosa che il testo **non** dice e che serve per
disegnare». Ma §4.5 e §5 mi ordinano di scriverci dentro anche l'esatto opposto: le cose
che il testo **dice** e che il grafo non mostra — la priorità sanitaria, la ferramenta
nominata, l'esclusione del ricircolo. Sono note di non-perdita, non domande.

Il risultato è che chi apre il JSON trova undici voci tutte `proposed` e tutte uguali, e
non ha modo di sapere che cinque aspettano una risposta (a1, a2, a3, a4, a10) e sei no
(a5–a9, a11). Lo schema non ha un campo per la distinzione. L'ho resa solo nel modo in cui
è scritto il testo di ogni voce — le domande finiscono con un punto interrogativo — e in
questo rapporto, alle sezioni 2a e 2b. È una convenzione mia, non delle istruzioni.

### 2. Nemmeno il tipo A/B/C ha un posto nel modello

§6 costruisce tutta la distinzione fra tipo A, tipo B e tipo C, dà il criterio per
separare A da C, e chiede di ripetere in chiaro nella risposta le sole domande di tipo C.
Ma il modello non ha un campo `tipo`, e `status` ammette solo `proposed`/`approved`/
`rejected`. La distinzione su cui il §6 costruisce tutto sopravvive solo in prosa. Chi
legge il JSON a valle non la vede.

### 3. Il perimetro delle reti non ha un criterio operativo

§4.2 dice: «Una rete è un circuito che il testo nomina o distingue». Preso alla lettera,
qui produce un risultato strano: il testo nomina «il circuito di climatizzazione», che è
un **ramo** del primario a valle della deviatrice, e lo distingue dal ramo che va al
bollitore. Sarebbero due reti — ma condividono la mandata della pompa di calore, il
raccordo di confluenza e il ritorno, e sono la stessa acqua nello stesso circuito.

Le istruzioni non danno un criterio per decidere se un ramo che si stacca da un pezzo di
deviazione sia una rete a sé o parte della rete da cui nasce. Ho tenuto un solo
`primario`, perché il fluido non cambia e il circuito si chiude su sé stesso, e l'ho
dichiarato in a11. La scelta non cambia né i componenti né le tubazioni, solo l'etichetta
`network_id` di tre tubi: per questo non l'ho trattata come tipo C. Ma è una scelta senza
appoggio nel testo delle istruzioni.

### 4. Quale uscita della valvola deviatrice va a quale ramo

`diverting-valve-3way` ha due uscite, `out_a` e `out_b`, identiche per fluido e per verso,
e il catalogo non dà loro alcuna semantica. Le istruzioni non dicono come assegnarle. Ho
messo la climatizzazione su `out_a` e il bollitore su `out_b`, seguendo l'ordine in cui il
testo li nomina. È un criterio inventato da me sul momento: qualunque agente potrebbe
scegliere l'opposto e il grafo sarebbe altrettanto valido, ma il disegno che ne esce
potrebbe non essere lo stesso.

### 5. `carries_on_board` è nel catalogo e non è mai nominato dalle istruzioni

La voce `heat-pump-air-water` dichiara `"carries_on_board": ["circulation"]`. Le istruzioni
parlano del circolatore integrato in due punti, e nessuno dei due è questo caso:

- §7 tratta il componente che **il testo** descrive come integrato («il circolatore
  integrato nella pompa di calore»). Qui il testo non lo descrive affatto.
- §6-tipo-A tratta il caso in cui il testo **nomina** un circolatore ma non dice se è a
  bordo o esterno. Qui il testo non nomina nessun circolatore primario.

Manca la regola per il terzo caso, che è il mio: il testo tace del tutto, e il catalogo
dichiara qualcosa. Non è scritto se `carries_on_board` vada letto come «la circolazione
c'è, è a bordo, non si disegna» oppure se il silenzio del testo debba diventare un buco
dichiarato. Ho fatto tutte e due: ho seguito il catalogo **e** ho dichiarato (a1), per
analogia con l'esempio del §6-tipo-A. Ma è un'analogia che ho tirato io, non una regola.

### 6. Lo stub `drain` del volano contro «lo scarico» del testo

Il `buffer-four-port` di catalogo porta già gli stub `vent`, `drain` e `probe`. Il testo
nomina «lo scarico» sul volume tecnico. §4.3 dice di non collegare niente agli stub; §5
dice di annotare la nomina degli accessori. Le due istruzioni non si contraddicono, ma
nessuna dice se lo stub già presente in catalogo «copra» la nomina del testo o se la
nomina resti comunque un dato da riportare. Ho fatto entrambe le cose: stub lasciato
libero e nota in a7. Se la risposta giusta fosse «lo stub basta, non annotare», a7 sarebbe
rumore.

### 7. «15 kW» di che potenza?

§4.6 dice: «Se il testo dà una potenza in una forma diversa (potenza resa, potenza
assorbita) trascrivila come sta e dichiara nell'assunzione quale hai sommato». Il mio testo
dice «una pompa di calore aria-acqua reversibile **da 15 kW**», senza qualificare: non è
«una forma diversa», è la forma nuda. Per una pompa di calore la potenza nuda è di per sé
ambigua (resa a che temperature? in che condizioni?).

Le istruzioni non dicono se la potenza nuda vada trattata come già chiara o come ambigua.
Ho trascritto «15 kW» così com'è e ricavato il regime senza aggiungere una dichiarazione,
perché §6 vieta esplicitamente di chiedere «qualunque cosa il testo abbia già scritto — a
partire dalle potenze». Fra i due, ho lasciato vincere il divieto.

### 8. Quali qualifiche finiscono in `properties`, e quante

§3 dice di trascrivere «le qualifiche che il testo usa», e non dà un limite. Nel mio testo
sono qualifiche anche «dedicato» (del circolatore), «tecnico» (del volume), «idronici» (dei
fan-coil), «alternativamente» (della deviazione). Ho trascritto solo quelle che qualificano
**la macchina** e non il circuito o l'azione: `potenza`, `tipo`, `volume`, `configurazione`,
`impiego`. È un criterio mio. Un altro agente potrebbe trascriverne il doppio o la metà, e
nessuna delle due letture violerebbe le istruzioni.

Nella stessa riga: **i nomi delle proprietà non hanno un vocabolario**. §3 dà cinque
esempi (`potenza`, `volume`, `modello`, `tipo`, `configurazione`) ma nessuna tabella
chiusa, e a differenza dei mestieri e dei fluidi non c'è un file di naming che li governi.
Ho inventato `impiego` per rendere «utilizzati sia in riscaldamento sia in raffrescamento».

### 9. Il `project_id` «dal titolo dell'impianto», quando l'impianto non ha un titolo

§3 dice di costruire il `project_id` dal titolo dell'impianto. Il testo che ho ricevuto ha
per intestazione «Esempio 2 – Pompa di calore con deviazione tra climatizzazione e ACS»:
metà è la numerazione di un esempio, non un titolo d'impianto. Ho scartato «Esempio 2» e
usato la sola parte descrittiva, ottenendo
`pompa-di-calore-deviazione-climatizzazione-acs`. Le istruzioni non dicono cosa fare
quando il testo non ha un titolo proprio, né se il titolo vada usato per intero.

### 10. Dove finisce la «trascrizione» e comincia l'«invenzione»

Non è un contrasto formale — le istruzioni lo risolvono da sole — ma vale segnarlo perché
è il punto in cui ho dovuto usare più giudizio. §1 dice: «nel grafo entra solo ciò che il
testo dice». §4.3 dice che il ritorno di un circuito chiuso «è trascrizione, non
invenzione». §4.4 impone i raccordi dove la topologia descritta fa incontrare due
tubazioni.

Il risultato è che il grafo contiene un componente (`rc-ritorni-primario`) e tre tubazioni
di ritorno (`p4`, `p5`, `p6`) che nessuna frase del testo nomina. Le istruzioni dicono che
è giusto così, e sono d'accordo. Ma il criterio per sapere **fino a dove** arriva questa
licenza — perché il raccordo di confluenza sì e un separatore idraulico no, perché il
ritorno sì e la valvola di intercettazione no — sta tutto nella lista dei mestieri del §5,
e funziona solo finché quella lista basta. È il perno su cui regge l'intero metodo, e
riposa su un elenco.

### 11. Minori, per completezza

- **Il grafo da solo non porta la sua tracciabilità.** §3 consente di lasciare `evidence`
  vuoto e di dare la traccia con la tabella di rilettura. L'ho fatto: `evidence` è vuoto
  ovunque. Ma vuol dire che il JSON, staccato da `rilettura.md`, non dice più da quale
  frase venga ciascun pezzo. `source_message_refs` copre solo le assunzioni, e l'ho usato.
- **Nessun criterio per gli `id` delle assunzioni.** Ho usato `a1`…`a11` in ordine di
  lettura del testo, come nell'esempio del §3.
- **Il §2 dice che il testo dell'ingegnere «te lo consegna chi lancia il lavoro»**, mentre
  qui è arrivato come file nella cartella di lavoro. Il §2 lo prevede («se i file ti
  arrivano copiati in un'altra cartella, valgono lo stesso»), quindi non è un problema:
  lo segno solo perché è un punto in cui le istruzioni e la realtà della prova non
  combaciavano alla lettera.

---

## 4. Isolamento

Ho lavorato solo dentro `camera-pulita/impianto-2/`. Non ho aperto, letto, cercato,
elencato né ispezionato alcun file fuori dalla cartella di lavoro: niente dentro
`/home/user/DisegnatoreMEP` — non i suoi esempi, non le sue prove, non la sua
documentazione, non il suo codice.

L'unica cosa eseguita fuori è il comando di validazione del §8, passo 7, che le istruzioni
del lavoro e il vincolo di isolamento permettono espressamente:

```
.venv/bin/python -c "from pathlib import Path; from disegnatore_mep.io.project_json import load_project; load_project(Path('.../consegna/grafo.json'))"
```

Nessun output: il file carica.

**Un episodio da dichiarare, per trasparenza.** Un mio comando che stampava l'intero
catalogo ha prodotto un output troppo grande, e l'ambiente l'ha salvato da sé in un file
di appoggio fuori dalla cartella di lavoro (`/root/.claude/projects/.../tool-results/`).
Era il risultato del mio stesso comando, non un file del repository — ma **non l'ho
letto**: ho rifatto il dump del catalogo a pezzi più piccoli, sempre e solo dai file
dentro `examples/layout/catalog/`. Nessuna infrazione, e la segno perché il confine
meritava di essere dichiarato invece che risolto in silenzio.

---

## 5. Verifiche fatte prima di consegnare

Il controllo finale del §9 è passato punto per punto; il dettaglio sta in
`rilettura.md`, sezione C. In sintesi: il JSON carica; i 9 `definition_id` esistono tutti
in catalogo e nessuno ha un mestiere della lista «ferramenta»; i 22 estremi delle 11
tubazioni usano solo attacchi dichiarati dal catalogo, nessun attacco porta due tubazioni,
nessuna tubazione tocca uno `stub`; ogni tubazione va da una porta `out` a una porta `in`
sullo stesso fluido, uguale a quello della sua rete; nessun attacco `required: true` è
rimasto libero; tutti i `tag` sono `null` perché l'ingegnere non ne ha scritto nessuno;
`subsystems`, `rule_applications` e `sheets` sono liste vuote.
