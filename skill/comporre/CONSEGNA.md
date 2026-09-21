# Comporre — che cosa consegna, e come si giudica

## Che cosa consegna

**Un file `piano.json`** nella forma di `ISTRUZIONI.md` §4, e nient'altro. Si esegue così:

```
disegnatore-mep piano <grafo-completo.json> --piano <piano.json> \
  --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
  --geometry <geometria.json> --out <cartella>
```

Se il comando non produce la tavola, **il piano non è consegnato**.

## Come si giudica, in quest'ordine

1. **Esce una tavola?** È il cancello: un piano che non si instrada non si discute, si
   rifà. Il messaggio d'errore dice quale tratta non trova strada.
2. **Nessuna tratta ceduta, nessun rilievo bloccante.** Sono nel rapporto che il comando
   stampa.
3. **Le autostrade sono rette?** Copri con una mano il corredo e guarda solo le linee grosse
   fra le macchine. **Questo è il criterio del pacchetto**, e non è un numero: è se la tavola
   assomiglia al lavoro di un disegnatore.
4. **Il confronto col bersaglio.** I cinque piani scritti a mano sono il metro: rilievi,
   tratte cedute, pieghe, incroci, impianto per impianto. **Se il piano dell'agente fa peggio
   si dice di quanto e su cosa** — non è un fallimento, è la misura da cui si migliorano le
   istruzioni.
5. **Le note dicono perché.** Un piano senza `note` e senza `regola` non è correggibile da chi
   lo rivede: può solo essere spostato. **Si scarta.**

## Quello che questo pezzo non chiude

- Non decide contenuti MEP, non cambia convenzioni grafiche, non tara soglie.
- **Non sceglie la forma delle linee**: quella la sceglie l'instradatore. Il piano può solo
  liberare il posto.
- Non giudica la propria tavola: quello è il pezzo 5, l'occhio del revisore.
