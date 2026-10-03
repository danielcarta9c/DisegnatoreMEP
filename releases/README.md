# Release — Disegnatore MEP

- `latest/` contiene esclusivamente l'ultima versione approvata e pronta da installare.
- `archive/` conserva i pacchetti ZIP numerati delle versioni pubblicate.

`latest/` non deve essere modificata manualmente durante lo sviluppo. Una release viene pubblicata soltanto dopo verifica dei test, controllo degli artefatti e approvazione.

Convenzione prevista: `DisegnatoreMEP-vMAJOR.MINOR.PATCH.zip`.

## Prima di pubblicare: la skill si deve caricare (I-189, D-200)

Uno ZIP va in `latest/` e in `archive/` **solo** se l'ha costruito `scripts/costruisci-skill.py` e se
`tests/test_le_release.py` passa. Tutti e due chiamano gli stessi controlli (`controlla_lo_zip`, `controlla`):

| limite | fonte |
|---|---|
| al massimo **200 file** nello ZIP | il caricamento su claude.ai: «Zip contains too many files (maximum 200)» (I-188, I-189) |
| la skill in **una cartella sola** alla radice dello ZIP, nessuna voce di cartella | centro d'aiuto di claude.ai, «Creating custom Skills» |
| **sotto i 30 MB**, decompressa | guida delle Skills per l'API |
| un solo `SKILL.md`, frontespizio YAML con i soli campi `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` | validatore di `skill-creator` |
| `name` in minuscole, cifre e trattini, fino a 64 caratteri, senza «anthropic» e «claude» | «Skill authoring best practices»; specifica |
| `description` fino a **200 caratteri** (claude.ai; la specifica ne ammette 1024) | centro d'aiuto di claude.ai |
| `compatibility` fino a 500 caratteri | validatore di `skill-creator` |
| corpo di `SKILL.md` sotto le 500 righe; i riferimenti a un livello, con l'indice oltre le 100 righe | «Skill authoring best practices» |

Simboli, catalogo e regole stanno nella skill in un file ciascuno (`dati/<nome>.json`): da soli erano 183 file.
Il comando della skill li riapre da sé.

## Le release pubblicate

- **1.2.0** — 2 ottobre 2026: la prima, con cui si chiude `REL-005` (D-198). La versione del pacchetto Python, la
  riga in testa a `SKILL.md` e il nome dello ZIP dicono lo stesso numero, e una prova lo tiene su
  (`tests/test_le_release.py`).
- **1.2.1** — 2 ottobre 2026: la prima consegna della beta (I-187, D-199). Da qui la riga in testa a `SKILL.md`
  porta il numero per intero.
- **1.2.2** — 3 ottobre 2026: **la prima che si carica su claude.ai** (104 file). La 1.2.0 e la 1.2.1, con 287 e 284
  file, si fermavano al caricamento (I-188, I-189, D-200).
- **1.3.0** — 3 ottobre 2026: **la tavola del costruito**, dal primo caso reale (`REL-009`, D-205): togliere,
  spostare e collocare gli accessori, il bordo della singola macchina, l'esistente, le voci del costruito con il
  simbolo. 104 file.
- **1.4.0** — 3 ottobre 2026: **la tavola del caso reale rifatta** (`REL-009`, punti 6 e 7; D-206 … D-209): prima
  le autostrade, il collettore che si raccorda dritto, i colori della distribuzione, le pompe in parallelo con lo
  stesso verso, e il disegna più veloce con le stesse tavole. 104 file.
