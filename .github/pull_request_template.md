<!--
  Compilato dal DEV. Giudicato dal PM.
  Una PR senza questo modulo compilato non è revisionabile.
  Il DEV non fonde e non chiude questa PR: l'accettazione è del PM.
-->

## Work Package

- **Identificatore:** <AREA-NNN>
- **Titolo:** <titolo del pacchetto>
- **Ramo:** <nome del ramo dedicato>
- **SHA iniziale:** <SHA di partenza>
- **SHA finale:** <SHA della testa del ramo>

## Input del PO collegati

<!-- Righe di docs/input-pm/REGISTRO.md a cui questo lavoro si riferisce.
     Elencare anche quelle solo toccate. Nessuna riga viene chiusa qui: la chiusura è del PO. -->

- <riga / identificatore> — <stato: resta aperta / se ne propone la chiusura, con la prova>
- Nessuno.

## Decisioni collegate

<!-- D-NNN o ADR. Indicare lo stato secondo docs/governance/DECISION_POLICY.md.
     Il DEV non marca nulla come approvato. -->

- <D-NNN> — <stato attuale> — <in che rapporto sta con questo lavoro>
- Nessuna.

## File modificati

<!-- Elenco completo, che deve coincidere con il diff e con il perimetro del pacchetto. -->

- `<percorso>` — <cosa cambia, in una riga>

## Verifiche eseguite

<!-- Cosa è stato eseguito e cosa è stato osservato. Non «funziona»: il comando e l'esito. -->

- <verifica> — <esito>

### Criteri di accettazione

<!-- Copiati dal pacchetto, uno per uno, con la prova accanto. Non si riscrivono. -->

- [ ] <criterio> — <prova>

## Difetti noti

<!-- Quello che non funziona, quello che è rimasto fuori, quello che è stato scoperto fuori
     perimetro e lasciato dov'è. Vuoto solo se davvero non c'è nulla. -->

- <difetto o limite>
- Nessuno.

## Ambiguità e punti aperti

<!-- Ciò che richiede una decisione del PO o del PM. Riportato, non risolto. -->

- <punto aperto> — <a chi spetta: PO / PM>
- Nessuno.

## Dichiarazione di assenza di modifiche fuori scope

- [ ] **Nessun file fuori dal perimetro del pacchetto è stato modificato.** Il diff di
      questa PR contiene esclusivamente i file elencati sopra.
- [ ] Nessuna decisione esistente è stata rinumerata, riscritta o cambiata di stato.
- [ ] Nessun input del PO è stato chiuso.
- [ ] Nessun merge su `main` è stato eseguito, e questa PR non è stata fusa dal DEV.
- [ ] Nessun ramo esistente è stato fuso, cancellato o riscritto.
