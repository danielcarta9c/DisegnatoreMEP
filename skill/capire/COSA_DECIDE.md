# Le quattro cose che l'interprete deve capire, o chiedere

> **A cosa serve questo file.** Le regole degli accessori cambiano esito in base a
> pochi dati d'ingresso. Se l'interprete li legge bene, il resto della catena non ha
> bisogno di chiedere niente. Se uno di questi gli resta oscuro, **quella è la domanda
> da fare all'ingegnere** — e non ce ne sono altre.
>
> **Come è stato fatto questo elenco.** Contando le condizioni delle diciassette
> regole, una per una, non a memoria. Se domani una regola cambia condizione, questo
> file va rifatto allo stesso modo.

---

## Quante regole dipendono da cosa

| Cosa decide | Quante regole la leggono |
|---|---|
| Che macchina è ciascun pezzo (e cosa dichiara di sé) | 17 su 17 |
| Che acqua porta ogni circuito | 9 |
| Il regime della centrale | 5 |
| Come i circuiti toccano una riserva | 6 |

---

## 1 · Che macchina è ciascun pezzo

È il dato più pesante: la scelta della macchina porta con sé tutto il resto. Fra due
macchine che sembrano simili cambia l'esito, e sono differenze che il testo dice.

**Le domande a cui il testo deve rispondere:**

- **Produce calore?** Un generatore riceve filtro, e — sopra i 35 kW — sicurezza e
  termometro. Un accumulo no.
- **Produce anche l'acqua calda sanitaria, da solo?** È il caso che citi tu. Una pompa
  di calore per il solo riscaldamento e un boiler in pompa di calore sono due macchine
  diverse: il secondo genera **e** accumula sanitario, e riceve il corredo della
  riserva (gruppo di sicurezza, ritegno, vaso) sulla propria alimentazione fredda.
- **Tiene una riserva d'acqua, e di quale acqua?** Il volano tiene acqua di
  riscaldamento, il bollitore acqua sanitaria. Da questo dipende dove va lo scarico —
  e metterlo sul circuito sbagliato è l'errore che abbiamo già fatto.
- **Da dove si riempie la riserva?** Il bollitore dall'acqua fredda: è da lì che si
  svuota. Il volano dal circuito, e non dichiara niente.
- **Cosa porta a bordo di fabbrica?** Le monoblocco hanno il circolatore dentro il
  mantello. Ciò che è a bordo non si disegna.

**Se il testo non lo dice:** è una domanda. «La caldaia produce anche il sanitario o
solo il riscaldamento?» è una domanda legittima; «che marca è» non lo è.

## 2 · Che acqua porta ogni circuito

Nove regole guardano il fluido: riscaldamento, acqua fredda sanitaria, acqua calda
sanitaria. **C'è o non c'è il sanitario** è la differenza più grossa: senza, tutto il
corredo sanitario non esiste.

**Se il testo non lo dice:** normalmente lo dice, perché descrive i circuiti. Se
descrive un circuito e non si capisce che acqua porta, è una domanda.

## 3 · Il regime della centrale

Sotto o sopra i 35 kW. Cinque regole cambiano: sicurezza e termometro per ogni
macchina o sul solo serbatoio, separatore d'aria o semplice sfogo.

**Si legge dalle potenze che il testo dichiara**, sommandole. Non è dimensionare: il
dato è dell'ingegnere, la soglia ha radice normativa, il conto è aritmetica.

**Se il testo le potenze non le dà:** allora è una domanda. Senza risposta vale il
corredo minimo, e va detto.

## 4 · Come i circuiti toccano una riserva

Sei regole distinguono il circuito che **attraversa** un serbatoio da quello che ne
**riempie** la riserva. Un serpentino passa dentro il bollitore a scaldare, ma non è
la sua acqua; l'ingresso freddo sì.

**Si legge dai collegamenti che il testo descrive**, non è una scelta.

---

## Cosa non si chiede mai

- Dove va un accessorio: lo sanno le regole.
- Quanti pezzi, che taglie, che diametri, che tarature: sono dell'ingegnere, e se non
  li ha detti non compaiono sulla tavola.
- Quello che sta scritto in un catalogo di un costruttore: si va a leggerlo.
- Come si chiude un collegamento quando c'è un solo modo di chiuderlo: si chiude e si
  dichiara l'assunzione.

## Quando una cosa non decisa va chiesta, e quando basta dichiararla

Si **chiede** quando valgono tutte e tre:

1. il testo davvero non lo dice;
2. le due strade sono **entrambe corrette** — nessuna è l'errore;
3. la scelta **cambia il disegno**.

Altrimenti si sceglie la strada convenzionale e si **dichiara**, così l'ingegnere la
vede e la corregge in un colpo solo con tutto il resto.
