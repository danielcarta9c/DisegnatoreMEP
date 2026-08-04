# Decisioni rimandate e note di sviluppo futuro

> Questo file esiste perché una decisione rimandata che non viene scritta è una decisione
> persa. Non è un backlog di priorità — quello è in `PROJECT_STATE.md` — ed è
> deliberatamente più lungo: qui ci sta anche ciò che nessuno farà presto.
>
> **Regola:** ogni volta che si dice «per ora no» o «lo vediamo dopo», la riga finisce qui,
> con il perché e con cosa la sbloccherebbe. Chi la esegue la cancella da qui.

---

## 1. Famiglie di accessori oltre il primo pacchetto di regole

Il primo pacchetto copre sette famiglie — sicurezza, intercettazione, protezione, aria,
riempimento e scarico, misura e acqua calda sanitaria — che bastano a completare il caso di
accettazione D-011. Non bastano a un impianto reale appena si esce da quel perimetro.

**Idronico, oltre l'MVP**

- valvole di bilanciamento, statiche e dinamiche;
- valvole di zona ed elettrotermiche;
- contabilizzazione del calore, che su una tavola condominiale c'è sempre;
- disconnettore sul gruppo di riempimento;
- addolcitore e dosatore di condizionante (le soglie di UNI 8065 sono in SRC-014);
- neutralizzatore di condensa per i generatori a condensazione.

**L'acqua calda sanitaria è rientrata nell'MVP** il 4 agosto 2026, per decisione del PM:
il caso di accettazione ha un bollitore, e lasciarne fuori gli accessori avrebbe prodotto
un impianto completo su metà tavola. Gruppo di sicurezza sull'ingresso acqua fredda, vaso
sanitario, miscelatrice termostatica e ricircolo sono nel Task 8 del piano P1.

**Aeraulico — l'esempio del PM.** Bastano ventilconvettori canalizzati perché servano
serranda di taratura, serranda tagliafuoco, silenziatore, batteria di post-riscaldamento,
filtro aria con la sua classe, plenum, griglie e diffusori, giunto antivibrante sul canale.
Una UTA ne aggiunge altrettanti: recuperatore, umidificatore, sezioni ventilanti.

**Espansione diretta e VRV.** Giunti di derivazione refrigerante, valvole di espansione,
distinzione fra linea liquido e linea gas.

**Gas.** Filtro gas, giunto antivibrante, elettrovalvola di intercettazione, pressostato di
minima e di massima, rilevatore di fughe.

**Regolazione.** Sonde di temperatura e pressione, valvola miscelatrice motorizzata a tre
vie, centralina climatica, termostati ambiente. Oggi `Domain.CONTROL` esiste nel modello e
non è usato da nessuna parte.

**Cosa lo sblocca:** ciascuna famiglia è indipendente dalle altre e si aggiunge senza
toccare il motore, purché il motore resti quello che P1 costruisce — regole come dato, non
come codice. Se aggiungere una famiglia richiede di modificare il motore, il motore è
sbagliato.

---

## 2. Come si migliorano le regole dopo P1

Il PM lo ha posto come requisito: le regole devono restare **migliorabili dandogli in pasto
documenti, normativa nuova o un manuale specifico**. Ne discendono tre vincoli per P1, che
il piano deve rispettare e non rimandare:

- una regola è **dato versionato**, non codice: si cambia senza toccare il motore;
- ogni regola porta la propria **fonte** e la propria **motivazione**, così che confrontarla
  con un documento nuovo sia possibile;
- cambiare una regola **incrementa la sua versione** e resta tracciabile a valle nel
  `RuleApplicationModel` di ogni progetto già disegnato (D-039).

Quello che resta rimandato è il **flusso**: come si dà in pasto un documento e come se ne
ricavano regole candidate da approvare. È lavoro della skill (P6), non del motore.

---

## 3. Fonti che si potrebbero acquisire, e non bloccano nulla

- **UNI 10412-1:2006** (SRC-013) — copre i dispositivi di sicurezza degli impianti con
  generatori elettrici, quindi il caso a pompa di calore che la Raccolta R esclude. Finché
  non c'è, quelle regole restano su buona pratica documentata, dichiarata come tale.
- **UNI 8065:2019** (SRC-014) — le sue prescrizioni sono già disponibili con soglie puntuali
  in guide di settore. Acquistarla servirebbe solo a salire di livello nella gerarchia.
- **ISO 14617** (SRC-003, SRC-004) — simbologia internazionale, utile il giorno in cui il
  prodotto uscisse dall'Italia.

Nessuna di queste è un prerequisito: D-066 fissa che non si acquistano norme che non
sbloccano nulla.

---

## 4. Rimandato dalla fase di layout

- **I diametri DN non stanno sulla tavola** perché il modello non li porta. Su una tavola
  reale ci sono sempre. Richiede un campo nel modello tecnico e un testo lungo la linea.
- **La fascia di regolazione tratteggiata sopra il disegno** non esiste: `Domain.CONTROL` è
  dichiarato e inutilizzato. È anche una delle due cose che riempirebbero l'altezza del
  foglio, oggi mezzo vuoto.
- **Una tratta che attraversa un confine di tavola non viene disegnata** su nessuna delle
  due: compaiono i rimandi accoppiati, non il tratto che li raggiunge. Spetta al rendering,
  che possiede i rimandi.
- **La rotazione di un componente posato è sempre 0.** Gli accessori in linea ruotano già
  seguendo la giacitura della propria tratta; un componente posato non viene mai orientato
  verso la fascia adiacente. È un grado di libertà in più per la regola di D-060.
- **La corsia di mandata non è garantita sopra quella di ritorno** dove due tratte devono
  scavalcare lo stesso ostacolo. Imporlo costerebbe pieghe. La convenzione resta garantita
  sui simboli e dai colori (D-057).
- **Il preflight grafico non esiste come validatore** (D-063): le misure vivono in
  `tests/layout/test_objective.py`, su una sola fixture e solo in sviluppo.
- **Il cold eye review e il ciclo di revisione non esistono** (D-063, D-064): sono lavoro
  della skill.

---

## 5. Rimandato dalla libreria dei simboli

- **La libreria va rifatta su SRC-015**, le tavole dei segni grafici UNI 9511. I venti
  simboli attuali seguono la convenzione interna `CONV-GRAFICA-001` e coprono meno di un
  ottavo di quelli che una tavola reale usa.
- **`buffer-four-port` confonde tre componenti diversi** — separatore idraulico,
  compensatore e accumulo inerziale — che Caleffi distingue e che su una tavola si
  disegnano diversamente (SRC-008).
- **Nessun test presidia che il corpo di un simbolo resti dentro il proprio riquadro** e
  raggiunga le porte dichiarate.
- **Nessun test protegge i due generatori di simboli dalla deriva** rispetto ai file che
  hanno prodotto.

---

## 6. Rimandato dal nucleo

- **`RuleApplicationModel` è un campo senza produttore**: esiste nel modello, nessun codice
  lo scrive. Lo chiude P1.
- **Il contratto `DomainPack` è minimo** — un solo metodo, che verifica la compatibilità di
  due porte. Va allargato **prima** che i quattro pacchetti di dominio procedano in
  parallelo, altrimenti divergono (W3).
- **La rappresentazione dei dati mancanti** e il percorso di migrazione dello schema sono
  descritti in `docs/P0_REVIEW_FINDINGS.md` §3.2 e non ancora implementati.
