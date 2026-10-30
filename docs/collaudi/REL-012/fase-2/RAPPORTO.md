# REL-012, fase 2, punto 3 — la M.02 del kit aria-aria rifatta dalla skill

**Data:** 29 ottobre 2026 · **Base:** `710475c` · **Stato:** sul ramo, da mostrare al PO.

## 1. Le tavole, per prime

| file | che cos'è |
|---|---|
| `tavola/caso-prova-aria-aria-t1.png` | la M.02 della skill, intera (PDF, SVG, DXF e rilievi accanto) |
| `confronto.png` | il kit a sinistra, la skill a destra, le due tavole intere alla stessa altezza |
| `confronto-schema.png` | lo schema, **alla stessa scala**, 340 × 182 mm attorno al disegno |
| `confronto-tratte.png` | la tabella delle tratte, alla stessa scala |

**La differenza che si vede subito: la skill fa un A1, il kit era un A2.** Le tabelle del motore
hanno il corpo delle scritte della tavola, 9 punti (I-159) con righe di 6,25 mm; il kit le
scriveva a 7 punti con righe di 3,4 mm. Con 9 punti il computo da solo vuole tre colonne di
zona alte 230 mm: sull'A2 non entra con nessuna misura delle zone (provate 175 × 135 e
200 × 200: «il titolo … non entra in una riga nella zona destra»; «… non entra nella zona
basso: restano 0 mm»). Il corpo delle tabelle è una convenzione grafica del PO (D-192, D-194,
I-159): **non l'ho toccato**, e la domanda è al §6.

**Quello che ho visto guardando, e i numeri non vedono:**

- lo **schema** è quello del kit pezzo per pezzo — stesso piano, 5 pieghe, 0 sormonti —, ma
  sull'A1 è piccolo rispetto al foglio: le tabelle pesano più del disegno;
- le **bocchette** portano la sigla e il locale su due righe, e la sigla di B1 sta sopra il
  simbolo, quella di B5 sotto («B1» + «Camera 13 m²»; il kit scriveva «B1 · Camera 13 m²» in
  una riga). È lo stesso modo dei termostati, anche sul kit; ma sulla colonna delle bocchette
  si legge meno ordinato;
- la **freccia dell'aria di mandata** sta a metà ramo, sotto la scritta «Ø200 · 270 m³/h · L 6
  m», e la punta tocca quasi le lettere: **anche sul kit è così** (ingrandimento a 400 dpi), non
  l'ho toccata;
- sulla tavola la scritta del tratto T13 dice «P1-P2 · L 3 m» (dato del progettista, dal kit) e
  la tabella delle tratte «L quot. 5»: la distinta applica il minimo di 5 m a tutto il bus, e
  lo segnala (`Verifica — T13`). **Sullo stesso foglio due numeri diversi per lo stesso
  tratto**: è la differenza in su E.9 di REL-013 (§4), che il PO non ha ancora deciso;
- nel computo **A.1 è il comando a filo**, non l'unità esterna come nel kit: l'ordine delle
  apparecchiature è quello della distinta;
- le **note della distinta** uscivano con una riga d'intestazione vuota fra il titolo e la
  prima nota. **Era un difetto del motore**, e l'ho corretto (§3).

## 2. Come è fatta, e come si rifà

```
bash docs/collaudi/REL-012/fase-2/rifai.sh     # 5,4 s
```

La strada di un agente, con la skill costruita da `scripts/costruisci-skill.py` in una cartella
temporanea: `fai-il-grafo.py` → `valida` → `completa` → `distinta` → `disegna --tabelle` →
`anteprima` → `confronto.py`.

- **Il grafo** (`grafo.json`) è `examples/distinta/AA-01/grafo-completo.json` (REL-013) con tre
  cambiamenti, detti in `fai-il-grafo.py`: i tre campi del tratto in testa alla tubazione,
  dove il motore li legge (nell'esempio stavano fra le `properties`, e la tavola usciva senza
  nessuna scritta Ø·L); l'etichetta delle bocchette senza la sigla, che altrimenti si
  scriveva due volte; il sifone senza sigla, come nel grafo del kit (§5, D2).
- **Il piano** (`piano.json`) è quello del kit pezzo per pezzo (gli id coincidono, nessuno da
  adattare), con `"formato": "A1"` e `"zone_tabelle": {"destra_mm": 230, "basso_mm": 230}` al
  posto del formato «A2T».
- **Le tabelle**: `distinta/tabelle-del-foglio.json` (tratte, computo, attività, note della
  distinta) e `note-di-progetto.json`, le nove note del kit che sono del progettista (§5, D7).

## 3. Che cosa è cambiato nel codice

| dove | che cosa | prova |
|---|---|---|
| `src/disegnatore_mep/skill.py` | `disegna --tabelle <file>` (ripetibile): legge il formato `disegnatore-mep/tabelle-del-foglio` versione 1, documentato in `FORMATO_DELLE_TABELLE`; ogni colonna larga almeno quanto la sua parola più lunga, il resto in proporzione ai pesi; una tabella con la sua `zona` va lì, le altre **a destra se ci stanno in una colonna, se no in basso**, dove la zona si divide in colonne; stampa dove ha messo ciascuna. Se il piano non ha zone o una tabella non entra, si ferma **prima di scrivere** (codice 1) e dice che cosa allargare | `tests/aria_elettrico/test_tabelle_dal_comando.py`, 15 prove |
| `src/disegnatore_mep/graphics/tabelle.py` | **difetto trovato sulla M.02**: una tabella con le intestazioni tutte vuote non ha più la riga dell'intestazione | `test_una_tabella_senza_intestazioni_non_ha_la_riga_vuota`, rossa prima della correzione (`assert 4 == 3`) |
| `tests/aria_elettrico/test_la_m02.py` | la M.02 rigenerata (valida, completa, distinta, disegna): zero bloccanti, zero cedute, le 18 scritte, le cinque tabelle, le sigle | 3 prove, 0,6 s |
| `skill/capire/ISTRUZIONI.md` §4.8 | l'aria-aria e le linee elettriche e di comando: voci, reti e fluidi, il verso anche dei cavi (`CONNECTION_WRITTEN_BACKWARDS`), i tre campi del tratto in testa come dati del progettista, il raccordo diretto, sigle ed etichette | `test_le_istruzioni_dicono_come_si_trascrive_l_aria_aria_e_l_elettrico` |
| `skill/comporre/ISTRUZIONI.md`, `docs/regole-del-piano.md` | `zone_tabelle` e `--tabelle` (D4); la posa del canalizzato (E1, E2, E3) dal kit | la costruzione della skill e `tests/test_le_release.py` |

## 4. Le misure

```
$ bash docs/collaudi/REL-012/fase-2/rifai.sh
Il grafo si legge: 19 pezzi, 22 tubazioni, 11 reti; regime della centrale: up_to_35_kw.
Le regole hanno aggiunto 0 accessori; … il grafo passa da 19 a 19 pezzi (+0).
Distinta: 80 voci in 9 sezioni, 18 tratte; regole cfc42a99c0fd0a1a.
Formato A1 · tratte 20 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 5 · sormonti 0 · avvisi e regole: nessuno

$ PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider          # sul commit di partenza
2301 passed, 15 skipped, 10 xfailed
$ PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider          # sul ramo
2320 passed, 15 skipped, 10 xfailed

$ ruff check src tests
All checks passed!

$ python3 scripts/costruisci-skill.py --out outputs/skilltmp
Skill: outputs/skilltmp/disegnatore-mep (115 file, 2165 kB)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.
$ PYTHONPATH=src python3 -m pytest -q -p no:cacheprovider tests/test_le_release.py tests/skill
44 passed
```

**Le tavole idroniche non cambiano.** Il banco `docs/collaudi/REL-011/banco.py` sul commit di
partenza (estratto con `git archive 710475c`) e sul ramo, stessi dati: **24 tavole su 24 con
lo stesso SVG, byte per byte** (impronta sha256 dell'SVG uguale, stessa riga di sintesi).

`mypy --strict` si ferma sugli stub di numpy anche sul `main` (HANDOFF): non è girato.

## 5. Le differenze dalla M.02 del kit, e perché

| | kit | skill | perché |
|---|---|---|---|
| D1 | A2, tabelle a 7 pt | **A1**, tabelle a 9 pt | il corpo delle tabelle del motore è quello della tavola (I-159, D-192); il computo non entra in un A2 (§1). **Domanda al PO** |
| D2 | sifone senza sigla, ripresa senza sigla | sifone senza sigla, **ripresa «RA-01»** | le sigle di ripresa e sifone le aveva messe REL-013 per la distinta; quella del sifone prendeva il posto del richiamo della scritta della condensa (`RUN_LABEL_OMITTED`, bloccante) e l'ho tolta — nella tabella delle tratte il sifone si legge «sifone»; quella della ripresa non disturba e resta |
| D3 | «B1 · Camera 13 m²» | «B1» e «Camera 13 m²» | la sigla è il `tag`, che la distinta usa per le tratte; l'etichetta porta il locale |
| D4 | frecce su refrigerante, cavi e bus | **senza** | voluto: i fluidi senza verso (fase 1, D-213 punto 6, decide il PO) |
| D5 | colori del kit per alimentazione, collegamento, bus | colori nuovi | voluto (fase 1) |
| D6 | legenda «Ø · L … da quotare (riserva compresa) … tabella delle tratte» | «Ø · L sezione e lunghezza, dato del progettista» | la riga di legenda della scritta del tratto è del motore (fase 1) |
| D7 | 11 «NOTE TECNICHE» | 5 «NOTE DELLA DISTINTA» + 9 «NOTE DI PROGETTO» | le note della distinta sono generali (REL-013 §4); le nove di progetto sono il testo del kit (note 3-11, e la prima frase della 4), che l'agente passa come secondo file di tabelle. Nella nota 8 i rimandi al computo sono quelli della distinta (Z.2, Z.3, Z.5; B.7) e non più del kit (Z.4-Z.6; B.2) |
| D8 | computo del kit, 62 voci | computo della distinta, 63 voci in A-Z | REL-013 §4: cinque voci contano di più (B.5, B.7, B.9, D.8, E.9), C.3 in due righe, testi generali, ordine diverso |
| D9 | G, 11 attività | G, 12 | REL-013 §4: le due DiCo in due righe |
| D10 | tratte T10 quadro-UE, T11 collegamento, T12 quadro-CZ | T10 QE-UE, T11 QE-CZ, T12 collegamento | REL-013 §4: le tratte in ordine di fluido |
| D11 | T13 L quot. 3 | T13 L quot. **5**, scritta sulla tavola «L 3 m» | REL-013 §4 (E.9): il minimo del bus su tutto il bus. **Sulla tavola due numeri per lo stesso tratto** (§1) |
| D12 | «Da - a»: «PLZ-01 - B1 Camera 13 m²», «ripresa - UI-01», «UI-01 - scarico bagno» | «PLZ-01 - B1», «RA-01 - UI-01», «UI-01 - sifone - scarico» | la distinta scrive le sigle dei capi del tratto |

Uguali: i pezzi (19), le sigle delle macchine, la tabella delle apparecchiature (5 righe, gli
stessi testi), tutte le 18 scritte Ø·L, «di fabbrica», le etichette di ripresa, scarico, quadro
e termostati, il cartiglio (titolo, M.02, rev. 00, Nove C, Ing. Daniel Carta, «Committente (dati
omessi)», AA-01), la posa e le misure dello schema (5 pieghe, 0 sormonti).

## 6. Da decidere col PO

1. **Il formato della M.02**: A1 con le tabelle a 9 punti, come le scritte della tavola, o le
   tabelle più piccole (il kit: 7 punti, sotto il minimo di 8 di I-159) per tenerla in A2.
2. **T13**: la scritta del progettista (3 m) e la lunghezza della distinta (5 m) sullo stesso
   foglio. Si decide con le cinque differenze di REL-013.
3. **Le frecce** sui fluidi senza verso (D-213 punto 6), viste qui sulla tavola.

## 7. Righe proposte per `skill/SKILL.md` (le integra il PO / la sessione)

Al passo 6, dopo il blocco del comando:

> Se la tavola porta tabelle — la distinta materiali, note del progettista — il piano lascia
> loro le zone (`zone_tabelle`, [riferimenti/comporre.md](riferimenti/comporre.md) §4) e il
> comando le riceve: `--tabelle $L/distinta/tabelle-del-foglio.json`, ripetibile per un
> secondo file nello stesso formato. Dice dove ha messo ciascuna; se non entrano si ferma
> prima di scrivere, e si allargano le zone o si prende il formato successivo.

Nella descrizione, quando la release lo dirà. Quella di oggi ha 194 caratteri, e «o di un
canalizzato aria-aria» in coda non ci sta (limite 200); riscritta, 189:

> Disegna in PDF e DXF lo schema funzionale di una centrale termica (pompe di calore, caldaie,
> accumuli, ACS) o di un canalizzato aria-aria. Da usare quando si chiede lo schema dell'impianto.

## 8. Quello che non ho fatto

- **Il corpo delle tabelle e il formato A2**: sono del PO (§6.1).
- **La riga di legenda «Ø · L»** del kit non c'è: la scritta della legenda è del motore.
- **`scripts/costruisci-skill.py` non porta `rules/distinta/` nella skill** (REL-013 §6.2,
  fuori dal mio perimetro): `rifai.sh` passa `--regole rules/distinta`.
- **Il campo `lunghezza_m` in testa non ammette 0**, e la distinta legge lo 0 come raccordo
  diretto: nel grafo il raccordo diretto tiene `"lunghezza_m": 0` fra le `properties`. Lo dicono
  le istruzioni di Capire; sarebbe più pulito un campo del modello che lo dica (modello fuori
  dal mio perimetro).
- `skill/scripts/mep.py` non è cambiato: `--tabelle` è un'opzione di `disegna`, e l'aiuto la
  stampa.
