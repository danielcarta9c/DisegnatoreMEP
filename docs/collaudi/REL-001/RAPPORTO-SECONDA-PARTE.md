# REL-001, seconda parte — la skill che si carica: rapporto

**Pacchetto:** `REL-001`, seconda parte (`ACTIVE_WORK_PACKAGE.md`; I-171) · **Ramo:** `claude/admiring-allen-u00wec`,
ripartito da `main` · **Base:** `main` a `65b0a97` (PR #66, `REL-001`) · **Avviato dal PO:** il 2 ottobre 2026 ·
**Codice finale:** ⟦SHA⟧

> **Esito — in attesa del PO.** La fusione aspetta che il PO carichi la skill su claude.ai, guardi la tavola e
> dica di sì.

> **Le tavole, per prime**
>
> ⟦TAVOLE⟧

## 1. Che cosa è cambiato, per chi carica la skill

Il 2 ottobre il caricamento su claude.ai si è fermato: «Zip contains too many files (maximum 200)». Lo ZIP
di `REL-001` aveva **287 file**. **Adesso ne ha 107**, pesa 752 kB, e la skill fa le stesse cose:

- **simboli, catalogo e regole** — 183 file che legge solo il comando — stanno **in un file ciascuno**,
  leggibile; il comando li riapre da sé, una volta, in una cartella temporanea;
- chi compone una tavola legge una voce di catalogo o il manifesto di un simbolo con il comando:
  `mep.py catalogo <id>`, `mep.py simbolo <id>`; le istruzioni di Capire e di Comporre nominano il comando
  dove prima nominavano il file;
- **la descrizione** della skill sta nei 200 caratteri che il centro d'aiuto di claude.ai indica, e il
  frontespizio dice la licenza e che cosa vuole l'ambiente (`compatibility`);
- **la costruzione controlla il caricamento**: oltre 200 file, oltre 30 MB, una voce di cartella, un secondo
  `SKILL.md`, un campo che il validatore non ammette, una descrizione troppo lunga — si ferma e lo dice;
- **il lanciatore** installa pydantic anche dove il Python di sistema è protetto (Ubuntu 24.04, PEP 668).

## 2. I criteri, uno per uno

⟦CRITERI⟧

## 3. Le linee guida di Anthropic, voce per voce

### 3.1 Quelle obbligatorie — senza, il caricamento si ferma

| regola | fonte | nella skill | la prova |
|---|---|---|---|
| al massimo **200 file** nello ZIP | il messaggio del caricamento su claude.ai (I-171) | **107** | la costruzione si ferma oltre 200; `test_lo_zip_sta_nei_limiti_del_caricamento`, `test_troppi_file_fermano_la_costruzione` |
| **la cartella della skill** alla radice dello ZIP, **nessuna voce di cartella** | centro d'aiuto, «Creating custom Skills»; guida delle Skills per l'API | tutte le voci in `disegnatore-mep/`, nessuna di cartella | la costruzione rilegge lo ZIP e lo controlla |
| **un solo `SKILL.md`** | `skill-creator` (`quick_validate`): «the Skills API and claude.ai reject multiple on upload» | uno | `quick_validate` → «Skill is valid!» |
| frontespizio **YAML** con `name` e `description` | centro d'aiuto; specifica | sì | `quick_validate` legge il frontespizio con YAML |
| `name`: al massimo 64 caratteri, minuscole, cifre e trattini, senza «anthropic» e «claude» | guida «Skill authoring best practices»; specifica | `disegnatore-mep` | `controlla` e `quick_validate` |
| `description`: non vuota, al massimo 1024 caratteri, senza tag | guida; specifica | 194 caratteri | `controlla` e `quick_validate` |
| `description` al massimo **200 caratteri** | centro d'aiuto di claude.ai, «Creating custom Skills» (22 luglio 2026) | 194 | `controlla`; le tue skill già caricate ne hanno 690–939, quindi oggi il limite non è applicato: lo si rispetta lo stesso |
| solo i campi `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` | `skill-creator` (`quick_validate`) | `name`, `description`, `license`, `compatibility` | `quick_validate`. Il centro d'aiuto cita anche un campo `dependencies`, che `skill-creator` rifiuta: le librerie stanno in `compatibility` e nel corpo |
| `compatibility` al massimo 500 caratteri | `skill-creator` | 296 | `controlla` |
| **sotto i 30 MB**, e ogni file sotto i 30 MB | guida delle Skills per l'API; centro d'aiuto, «Create and edit files» | 2,1 MB in tutto, il file più grande 211 kB | `controlla` |

### 3.2 Le buone pratiche — la lista della guida

La lista «Checklist for effective Skills» è quella del rapporto della prima parte (§3, criterio 7), voce per
voce; qui cambia solo dove la skill è cambiata.

| voce | | che cosa cambia |
|---|---|---|
| La descrizione è specifica e porta le parole chiave | sì | più corta: schema funzionale, centrale termica, pompe di calore, caldaie, accumuli, ACS, PDF, DXF, tavola |
| Dice che cosa fa e quando usarla | sì | «Disegna in PDF e DXF lo schema funzionale … Da usare quando chiede lo schema o la tavola dell'impianto.» |
| I dettagli stanno in file a parte, a un livello | sì | i riferimenti sono gli stessi; i dati si leggono col comando, non si aprono |
| Gli script risolvono invece di rimandare | sì | il comando riapre da sé i dati; `catalogo <id>` e `simbolo <id>` |
| Le librerie sono dette e verificate | sì | in `compatibility` e in «Prima di cominciare»; `ambiente` le verifica e le installa, anche su un Python protetto |
| Provata con Haiku, Sonnet e Opus | sì | §2, criterio 4; `SKILL.md` dice ad Haiku di avvisare il progettista |
| Il parere del gruppo | **aperto** | il caricamento e la prova tua (§4) |

## 4. Come si carica

⟦CARICAMENTO⟧

## 5. Che cosa resta aperto

⟦APERTO⟧
