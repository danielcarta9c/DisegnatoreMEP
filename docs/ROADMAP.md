# Roadmap — Disegnatore MEP

La roadmap definisce l'ordine delle fasi. Le attività operative immediate vivono in `PROJECT_STATE.md`.

## Fase 0 — Fondazione del progetto

- [x] Consolidare il contesto iniziale.
- [x] Definire la struttura di project management.
- [x] Completare il brainstorming e approvare il design concettuale.
- [x] Eseguire la revisione end-to-end CAD e software.
- [x] Far approvare al PM la specifica scritta.
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
- introdurre identificativi stabili, provenienza e versioni;
- implementare regole necessarie, raccomandate e condizionate;
- produrre l'elenco delle integrazioni prima del disegno;
- validare coerenza e completezza topologica con controlli specifici per dominio;
- generare la distinta quantitativa dal modello.

## Fase 3 — Linguaggio grafico

- creare simboli SVG originali;
- definire griglia, allineamenti, colori, spessori, testi e tag;
- integrare il cartiglio Nove C;
- partizionare semanticamente i sistemi complessi prima del layout;
- implementare layout e instradamento deterministici;
- esportare SVG e PDF vettoriali con manifest di riproducibilità.

## Fase 4 — Collaudo

- costruire casi validi, ambigui e non validi;
- confrontare gli elaborati con schemi professionali di riferimento;
- verificare invarianti generali e combinazioni miste fra domini;
- eseguire controlli visivi e prove di stampa A3;
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

## Futuro remoto — progetto generale

Questi filoni sono intenzionalmente esclusi dalla skill attuale, ma restano nella visione del progetto:

- generazione di tavole planimetriche degli impianti;
- generazione di schemi elettrici e di regolazione esecutivi completi;
- eventuale modello coordinato capace di collegare schema funzionale, planimetria ed elaborati elettrici.

Non devono introdurre requisiti prematuri nell'implementazione corrente. Saranno rivalutati soltanto dopo la maturità e l'uso reale del disegnatore di schemi termotecnici.
