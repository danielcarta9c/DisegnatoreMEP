# «Ti faccio vedere come andava fatto» — 21 settembre 2026

**Sono la fonte più precisa che abbiamo su come si tira una coppia mandata/ritorno**, perché
il PO non ha descritto a parole: ha **ridisegnato sopra le nostre tavole**, due volte, e le due
correzioni sono la stessa.

> «Tavola 1 va quasi bene. Tavola 5… **ti faccio vedere come andava fatto**. Due cose che ho
> notato: la **valvola a tre vie** la metti sempre con uscita terza verso il basso, guarda che
> **puoi ruotarla**. I **simboli dei terminali** vanno modificati: con uscita dall'altro lato
> **si spreca spazio**, meglio metterli sempre con **ingresso e uscita su un lato solo** come
> ho fatto io. Ti aiuta così a capire come vanno fatti? Riesci a tirare fuori una regola?»

| file | che cosa ci ha segnato |
|---|---|
| `tavola-5-come-andava-fatta.webp` | **Cancella con una X verde** il collettore di mandata lontano dalle pompe e **ripassa in rosso spesso** quello che va **addosso alle macchine**: i due collettori stanno su **una colonna stretta accanto alla cascata**, non a duecento millimetri l'uno dall'altro. **Tratteggia in rosso** le linee da togliere. A destra **ridisegna in blu e rosso spesso** i tre secondari: **due colonne adiacenti** — mandata e ritorno — e da quelle **una coppia di orizzontali per ogni utenza**, mandata sopra e ritorno sotto, che arrivano al terminale **dallo stesso lato**. Cancella in verde i giri che i ritorni facevano attorno ai terminali. |
| `tavola-4-come-andava-fatta.webp` | La stessa cosa sulla tratta caldaia → scambiatore: **due orizzontali adiacenti** che corrono insieme, mandata sopra e ritorno sotto, e **due verticali vicine e dritte** che salgono al primario. Tratteggia in rosso le linee che facevano il giro largo. |

## La regola che ne esce, ed è una sola

> **La coppia mandata/ritorno è un oggetto solo — un binario a due corsie — e si ramifica a
> pettine.** Due colonne **adiacenti** portano il fluido, e da quelle si stacca **una coppia di
> orizzontali per ogni utenza**: mandata sopra, ritorno sotto, **affiancate per tutta la
> corsa**, fino al terminale, che si prende **da un lato solo**.

È **B12** in `docs/regole-del-piano.md`, ed è anche la «composizione a corsie» che la ricerca
del 4 agosto 2026 §2.2 aveva trovato sulle tavole vere e che non eravamo ancora riusciti a
comporre.

## E le due cose che ha notato sono i due impedimenti a quella forma

Non sono due osservazioni sparse: sono **le due ragioni per cui il pettine non ci veniva**.

1. **Un terminale con le porte su facce opposte rompe il binario.** `in` a sinistra e `out` a
   destra costringono il ritorno a **uscire dall'altro lato e girare attorno**: la coppia si
   apre, e si spreca la fascia a destra del terminale. Con tutt'e due le porte **sullo stesso
   lato** il pettine si chiude da solo. → **D-167**.
2. **Una tre vie con la terza via sempre verso il basso costringe la diramazione a scendere**,
   anche quando il pezzo da servire sta altrove. La valvola **si può ruotare**, e la rotazione
   va **scelta**, non subita. → **D-168**.

## Come si usano, e come no

**Sì**: per la **forma** — come corre una coppia, dove sta un collettore, come si prende un
terminale, come si ramifica una dorsale.

**No**: per le **quote**. Sono ripassi a penna su uno schermo: gli spessori e le distanze non
sono misure. Vale lo stesso avvertimento delle tavole del 20 settembre.
