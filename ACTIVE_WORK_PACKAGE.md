# REL-001, seconda parte — La skill che si carica, e che funziona dove si carica

> **▶ Attivo dal 2 ottobre 2026** (I-171), **prima di `REL-005`**, che resta il prossimo e aspetta scritto in
> `docs/plans/pacchetti/REL-005.md`. Il PO ha caricato lo ZIP di `REL-001` su claude.ai e il caricamento si è
> fermato: «Zip contains too many files (maximum 200)». Il PO: «la skill nn si riesce a caricare. La skill deve
> essere perfettametne funzionante e perfettamente e facilmente installabile. devi seguire tutte le linee guida
> di anthropic sia quelle obbligatorie sia le best practice.»

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO** dal 2 ottobre 2026 (I-171).
**Base:** `main` dopo la fusione di `REL-001` (PR #66).
**Ramo:** quello che l'ambiente della sessione assegna, ripartito da `main`.
**Release:** la prima release (**D-183**): è il difetto della consegna di `REL-001`.
**Approvazione della fusione:** **del PO**, e si dà guardando la tavola e caricando la skill (D-146, D-147).

---

## Dove siamo — misurato il 2 ottobre 2026

- **Lo ZIP di `REL-001` ha 287 file.** Il caricamento su claude.ai ne accetta al massimo 200 (il messaggio
  del caricamento; lo stesso limite è segnalato da altri progetti). La guida di Anthropic e il validatore di
  `skill-creator` non lo controllano, e la costruzione non lo controllava.
- **Da dove vengono**: 89 moduli del motore, di cui la skill ne importa 84; 94 file di simboli (un manifesto
  e un disegno per simbolo), 73 voci di catalogo, 16 file di regole; il resto sono le istruzioni, il
  comando, i nomi, lo schema e il cartiglio.
- **I limiti scritti da Anthropic**, letti il 2 ottobre 2026: la cartella della skill dentro lo ZIP, un solo
  `SKILL.md` con il frontespizio YAML (`name` fino a 64 caratteri, minuscole, cifre e trattini, senza
  «anthropic» e «claude»; `description` fino a 1024 caratteri, senza parentesi angolari); tutto sotto i 30 MB;
  i campi che `skill-creator` ammette sono `name`, `description`, `license`, `allowed-tools`, `metadata`,
  `compatibility`. L'articolo del centro d'aiuto di claude.ai («Creating custom Skills», 22 luglio 2026) dà
  alla descrizione 200 caratteri.
- **L'ambiente di claude.ai**: per le organizzazioni la rete del codice è, se non la si cambia, «solo i
  gestori di pacchetti» (PyPI compreso); può essere spenta. La skill vuole pydantic, e lo installa da PyPI
  alla prima chiamata.

## Le cose da fare

1. **Lo ZIP sotto i 200 file, con margine.** Simboli, catalogo e regole — 183 file che legge solo il comando
   — stanno ciascuno **in un file solo**, leggibile, e il comando li riapre da sé in una cartella temporanea.
   Il motore resta com'è, le istruzioni pure. Chi compone legge un manifesto o una voce di catalogo con un
   comando: `mep.py simbolo <id>`, `mep.py catalogo <id>`.
2. **I controlli della costruzione** coprono il caricamento: i file dello ZIP, la misura, un solo `SKILL.md`,
   il frontespizio con i soli campi ammessi e le loro misure, la descrizione dentro i 200 caratteri del
   centro d'aiuto. Se uno non passa, la costruzione si ferma.
3. **Il frontespizio**: la descrizione dentro i 200 caratteri, con che cosa fa e quando si usa; `license` e
   `compatibility` — che cosa vuole l'ambiente: l'esecuzione del codice, Python 3.11, pydantic da PyPI.
4. **La prova**: la skill costruita disegna le tavole dei collaudi byte per byte come il repository; poi la
   prova in camera pulita dal testo al PDF, con lo ZIP nuovo.

## Perimetro

**Dentro:** `scripts/costruisci-skill.py`, `src/disegnatore_mep/skill.py`, `skill/`, `tests/skill/`,
`docs/collaudi/REL-001/`, i documenti di passaggio.

**Fuori:** il motore del disegno, le regole, i simboli, il catalogo nel contenuto; le istruzioni di Capire,
Comporre e Rivedere fuori dai percorsi.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: la tavola dell'impianto 7 uscita dalla skill nuova in camera pulita, al PO.
1. **Lo ZIP si carica**: al massimo 200 file — con margine —, sotto i 30 MB, un solo `SKILL.md`, il
   frontespizio dentro le regole della guida, di `skill-creator` e del centro d'aiuto; la costruzione lo
   controlla e una prova lo tiene su. **Il caricamento vero lo fa il PO.**
2. **La skill funziona come prima**: dalla skill costruita, fuori dal repository, le tavole dei collaudi
   escono identiche byte per byte a quelle del repository; ogni comando gira.
3. **Le istruzioni cambiano nei soli percorsi**: un file che non c'è più diventa il comando che lo legge.
4. **La prova in camera pulita**: dal testo al PDF, zero cedute e zero bloccanti, con lo ZIP nuovo.
5. **La suite**: nessuna rossa nuova rispetto alle 46 di `main`; zero `skip` e zero `xfail` nuovi; `ruff` e
   `mypy` verdi.

## Consegna

Una PR verso `main`, fusa solo dopo che il PO ha caricato la skill e ha detto di sì. Rapporto in
`docs/collaudi/REL-001/RAPPORTO-SECONDA-PARTE.md`, con la tavola in testa.
