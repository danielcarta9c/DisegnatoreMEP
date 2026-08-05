# Le proprietà dei componenti

> **Cosa approvi qui.** L'elenco delle cose che ogni pezzo dell'impianto dichiara di sé.
> Non cosa è, ma **cosa è vero di lui**: si manutiene, sporca l'acqua, non si chiude mai.
>
> **Perché esiste.** Una regola deve poter dire *«tutto ciò che si manutiene vuole le
> proprie valvole»*. Se nessun pezzo dichiara di manutenersi, quella frase non è dicibile e
> resta solo la scorciatoia sbagliata — *«il volano vuole quattro valvole»* — che vale per
> un pezzo solo e va riscritta per il successivo. Questo elenco è ciò che rende generali le
> regole.

---

## L'elenco

| Proprietà | Che cosa dice del componente | Il ragionamento che permette | Chi ce l'ha, per esempio |
|---|---|---|---|
| **Si manutiene** | Si smonta o si sostituisce, e per farlo bisogna poter chiudere l'acqua attorno. | Tutto ciò che si manutiene vuole una valvola su **ogni** tubo che entra o esce: si isola quel pezzo senza svuotare l'impianto. | Pompa di calore, bollitore, volano, circolatore, filtro, defangatore |
| **Sporca il circuito** | Produce fanghi e ossidi che l'acqua si porta dietro tornando indietro. | Se in un circuito c'è qualcosa che lo sporca, la macchina delicata va protetta su ciò che le entra. | Radiatori, pannelli radianti |
| **Va protetto dai residui** | Ha organi che i fanghi e i residui di montaggio rovinano. | Filtro e defangatore vanno **prima** del pezzo da proteggere, sul tubo che ci entra. | Pompa di calore, caldaia, circolatore |
| **Produce aria** | Scalda l'acqua, e l'acqua scaldata libera l'aria che tiene disciolta. | L'aria si libera dove l'acqua è più calda: il separatore d'aria va sulla mandata, appena fuori dalla macchina. | Pompa di calore, caldaia |
| **Va protetto dalla sovrapressione** | Chiude dentro di sé un volume d'acqua che, scaldandosi, spinge. | A chi ha questa proprietà servono la valvola di sicurezza e un vaso che assorba la dilatazione. | Pompa di calore, caldaia, bollitore |
| **Contiene acqua da svuotare** | Ha dentro un volume di fluido che deve poter essere svuotato per conto proprio. | A chi ha questa proprietà serve un attacco di scarico, così si vuota quel solo serbatoio e non l'impianto. | Volano, bollitore |
| **Si intercetta normalmente** | Se lo si deve isolare, lo fa una valvola comune. | È il caso ordinario, e va detto lo stesso: chi non chiede niente di speciale lo dichiara invece di lasciarlo intendere. | Quasi tutti |
| **Non si intercetta mai** | Fra lui e ciò che serve non ci va **nulla** che si possa chiudere. | Impedisce che la regola delle valvole metta un rubinetto davanti a un organo di sicurezza: una valvola chiusa lì è un impianto che scoppia. | Valvola di sicurezza, attacco di scarico |
| **Si intercetta solo con valvola bloccabile** | Si isola soltanto con una valvola che si blocca aperta e non si chiude per distrazione. | Il vaso di espansione va potuto staccare per la verifica, ma non deve mai restare escluso per sbaglio. | Vaso di espansione, di riscaldamento e sanitario |
| **Sta in linea** | Il tubo ci passa dentro, o ci arriva: è sul percorso. | L'assemblatore lo mette **nella fila** dei pezzi lungo quel tubo. | Filtro, defangatore, circolatore, volano, bollitore |
| **Sta su uno stacco** | Pende dal tubo con una propria derivazione: non è un organo di passaggio. | Quel pezzo ha una sua piccola fila laterale, con i propri accessori: la sequenza dell'impianto diventa un albero e non una lista. | Vaso di espansione, valvola di sicurezza, gruppo di riempimento, scarico, manometro |

---

## Le due cose che nessun componente può tacere

Ogni pezzo, macchina o accessorio che sia, **deve** dire due cose:

1. **Come si lascia isolare** — normalmente, mai, o solo con valvola bloccabile.
2. **Come si attacca** — in linea sul tubo, oppure su uno stacco.

Non c'è un valore sottinteso per chi non lo scrive: un componente che tace **non entra in
catalogo**. È voluto. Un valore sottinteso sarebbe una scelta impiantistica presa dal
programma di nascosto, e i due casi che ci hai segnalato — la sicurezza che non si isola
mai, il vaso che si isola solo con valvola bloccabile — sono esattamente quelli che un
valore sottinteso avrebbe cancellato.

## Perché all'elenco ne abbiamo aggiunta una

Delle proprietà qui sopra, una non era nella richiesta: **«va protetto dai residui»**.
Serve perché *«sporca il circuito»* copre solo metà del ragionamento: dice che i fanghi
esistono, non dove va messo il filtro. Senza l'altra metà, la regola del defangatore
dovrebbe dire *«davanti alla pompa di calore»* — cioè nominare un pezzo, che è la cosa che
stiamo togliendo di mezzo. Con entrambe, la regola diventa: *dove qualcosa sporca l'acqua,
ciò che i residui rovinano va protetto su ciò che gli entra.*

Nient'altro è stato aggiunto. Una proprietà che nessun componente dichiara viene rifiutata
da un controllo automatico: l'elenco non può gonfiarsi di voci inutili.

## Una scelta che vale la pena dirti

**La valvola di intercettazione non dichiara di manutenersi.** Si sostituisce, certo, ma
non chiede altre due valvole per essere sostituita — e se lo chiedesse, quelle due ne
vorrebbero altre quattro, senza fine. «Si manutiene» qui vuol dire una cosa precisa: *per
smontarlo bisogna poter chiudere l'acqua attorno*. Con quel taglio, il filtro le sue valvole
le vuole e la valvola no.

Per lo stesso motivo un pezzo non può dichiarare insieme «si manutiene» e «non si
intercetta mai»: la prima chiede le valvole che la seconda vieta. Il catalogo rifiuta la
contraddizione invece di lasciarla passare e produrre una sequenza sbagliata.

## Come sappiamo che nessuna proprietà è un componente mascherato

È il rischio vero di tutto questo lavoro: chiamare *«è un vaso di espansione»* una
proprietà, e ritrovarsi con le stesse regole particolari di prima sotto un altro nome. Un
controllo automatico legge l'elenco e lo confronta con i nomi di tutti i componenti in
catalogo: se una proprietà coincide con uno di quei nomi, o lo contiene, il controllo
fallisce e il lavoro non passa.

---

## Cosa ti stiamo chiedendo

Di leggere le undici righe della tabella e dirci, per ciascuna: **è vera, è utile, e ne
manca una?** Le regole del prossimo passo si scriveranno solo su queste — se una proprietà
qui non c'è, quel ragionamento non si potrà scrivere.
