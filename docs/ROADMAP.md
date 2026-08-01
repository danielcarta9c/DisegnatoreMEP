# Roadmap — Disegnatore MEP

La roadmap definisce l'ordine delle fasi. Le attività operative immediate vivono in `PROJECT_STATE.md`.

## Fase 0 — Fondazione del progetto

- [x] Consolidare il contesto iniziale.
- [x] Definire la struttura di project management.
- [ ] Completare il brainstorming e approvare il design.
- [ ] Trasformare il design in un piano di implementazione verificabile.

## Fase 1 — Conoscenza tecnica e perimetro

- selezionare fonti normative, manuali e schemi autorevoli;
- codificare la gerarchia tra obblighi, buona pratica e convenzioni grafiche;
- definire il nucleo universale e i pacchetti di dominio idronico, aeraulico, refrigerante e gas;
- delimitare la libreria ampia dei componenti comuni senza introdurre schemi tipo rigidi;
- definire dati obbligatori, assunzioni consentite e casi bloccanti.

## Fase 2 — Modello e validazione

- definire il modello strutturato interno;
- definire componenti, porte, circuiti e relazioni;
- implementare regole necessarie, raccomandate e condizionate;
- produrre l'elenco delle integrazioni prima del disegno;
- validare coerenza e completezza topologica.

## Fase 3 — Linguaggio grafico

- creare simboli SVG originali;
- definire griglia, allineamenti, colori, spessori, testi e tag;
- integrare il cartiglio Nove C;
- implementare layout e instradamento deterministici;
- esportare SVG e PDF vettoriali.

## Fase 4 — Collaudo

- costruire casi validi, ambigui e non validi;
- confrontare gli elaborati con schemi professionali di riferimento;
- effettuare revisione tecnica dell'ingegnere;
- correggere regole e regressioni grafiche.

## Fase 5 — Prima release

- impacchettare la skill installabile;
- verificare installazione pulita e funzionamento;
- aggiornare `releases/latest/`;
- creare archivio numerato e manifesto della release.

## Fasi successive

- ampliare progressivamente componenti e regole meno frequenti senza modificare il nucleo;
- consolidare i pacchetti di dominio tramite casi reali misti;
- valutare integrazione CAD desktop soltanto dopo la maturità del motore vettoriale.
