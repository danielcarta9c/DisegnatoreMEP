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
- **1.4.1** — 5 ottobre 2026: **lo sfiato col suo rubinetto**, un simbolo solo, ovunque (I-210, I-211, D-210); lo sfiato
  senza rubinetto solo se il progettista lo dice. 104 file.
- **1.5.0** — 24 ottobre 2026: **il revisore esterno** (`REL-010`, D-212): la tavola la può guardare un altro agente
  che non conosce l'impianto, se il progettista lo sceglie alla domanda del passo 2; la soglia del PO in Rivedere; il
  pannello e il giunto di D-211. 104 file.
- **1.6.0** — 29 ottobre 2026: **l'aria-aria, l'elettrico e il comando** (`REL-012`), con **la distinta materiali**
  (`REL-013`) e **la pianta dei tracciati** (`REL-014`) su richiesta, dal kit del PO (I-224 … I-229, D-213 proposta).
  Le tavole idroniche della 1.5.0 non cambiano. 131 file.
- **1.7.0** — 30 ottobre 2026: **la distinta in un documento a parte, la tavola in A3, l'elettrico dopo l'idraulica**
  (`REL-015`, I-230 … I-234): sulla tavola solo apparecchiature e legenda, la distinta in PDF coi report Nove C, le
  scritte dell'acqua prima dei cavi, il collettore a coppia col ritorno continuo, la pompa di calore che regola da sé
  (proposta). 134 file.
- **1.7.1** — 30 ottobre 2026: **i circolatori comandati dalla pompa di calore** prendono alimentazione e comando
  dalla sua morsettiera, con un cavo solo; il quadro alimenta la macchina (I-236, D-215, lo standard dell'elettricista
  del PO). 134 file.
- **1.8.0** — 30 ottobre 2026: **i tre rilievi del collaudo della 1.7.0** (`REL-016`, I-237, I-239, D-216): la tavola
  aggrovigliata non si consegna, il collettore di zona da 3 a 12 vie, le domande della distinta al passo 2. 135 file.
- **1.8.1** — 3 novembre 2026: la terza via della deviatrice corre accanto al ritorno della serpentina, all'interasse
  delle autostrade: si sposta la deviatrice, non il bollitore (I-240). 135 file.

- **1.9.0** — 4 novembre 2026 (`REL-011`): le regole del corredo contro il manuale Shenling e la specifica Nove C, decise
  col PO punto per punto (D-217 … D-232) — ritegno su ogni generatore in parallelo, giunti antivibranti, valvole
  antigelo, vaso con riempimento e manometro fra le macchine e il defangatore, le domande su volano e vaso, il DN mai
  sotto l'attacco Shenling; il vaso dimensionato (`mep.py vaso`) e il livello del progetto (definitivo / esecutivo),
  con tarature e note di posa solo nell'esecutivo; il relè d'appoggio da 10 A fra la pompa di calore e i circolatori;
  la distinta rivista e la lista della spesa (`distinta --lista`). 140 file.
- **1.10.0** — 4 novembre 2026 (`REL-017`): i rilievi di una commessa reale (I-269 … I-277) — il **termostato ambiente
  a contatto** in serie sulla linea quadro → circolatore (TAC-nn, niente relè); la **tabella della tavola elettrica**
  con tutti i pezzi del foglio e le sole caratteristiche elettriche (alimentazione, potenza elettrica, corrente
  massima, cavo minimo); il **vaso sanitario** messo dalla regola fra gruppo di sicurezza e bollitore anche quando il
  bollitore non lo ha (`non_a_bordo`), e quello scritto a mano a monte del non ritorno fermato; le **note di posa del
  progettista** (`note_di_posa`, `note_tolte`); l'**avviso della prevalenza** della pompa a bordo sul giro primario;
  le lunghezze del progettista non più perse da `completa`; lo **scarico** senza freccia, la sigla del volano accanto
  al suo simbolo, i simboli della legenda che non si toccano. 141 file.
- **1.11.0** — 4 novembre 2026 (`REL-017`, I-279, I-281, D-233): **sulla tavola il tubo da comprare**, non l'Øi — il
  materiale delle tubazioni (`materiale_tubazioni`, multistrato di base), il tubo commerciale scelto per velocità
  («MS 32×3», «DN 25 (1")», «Cu 28×1») con la sua legenda, l'Øi solo nel foglio dei calcoli, il tubo del progettista
  che vince con un avviso, una scritta per tratta; la distinta con la stessa dicitura e il pollice degli accessori; la
  nota dell'isolamento sul tubo vero; l'attacco della Shenling non più un minimo ma la **riduzione all'attacco**, un
  pezzo con il suo simbolo dopo il giunto antivibrante; la prevalenza della pompa a bordo assunta 8 m se non data. 144 file.
- **1.12.0** — 5 novembre 2026 (`REL-018`, I-278): **le protezioni elettriche** — l'interruttore magnetotermico
  differenziale (QF-nn) sulla linea della pompa di calore, in tabella e in legenda; i dati elettrici delle Shenling dal
  manuale e dalla specifica Nove C («vale il maggiore»: 12 kW 230 V 1~, 30 A, 3G6, 2P C32 Idn 30 mA tipo B) scritti da
  `completa` dove il progettista non li dà; gli avvisi per protezione o cavo sotto il manuale e per la linea senza
  protezione; niente sezionatore locale di regola. 147 file.
- **1.12.1** — 5 novembre 2026 (D-234): le tre scelte delle protezioni — il 6 kW a C20, il differenziale separato con
  la corrente del magnetotermico (il «B40»), le linee di servizio protette solo se dichiarate. 147 file.
- **1.13.0** — 5 novembre 2026 (`REL-019`, I-284 … I-286): **il listino interno della minuteria** nella skill
  (`riferimenti/listino-minuteria.md`), dal foglio del PO: le 150 voci Tecnomat del 2 novembre e il riferimento online
  delle 18 voci mancanti, con forbice e mediana, fonte e link di ogni prezzo. Lo apre l'agente solo quando il progettista
  chiede un costo; il documento per l'installatore resta senza prezzi. Disegno e distinta invariati. 148 file.
- **1.14.0** — 5 novembre 2026 (`REL-020`, `REL-021`, I-287, D-236): **la distinta della parte idronica e il costo
  della minuteria** — la sezione I con il corredo di ogni voce idronica del catalogo (tubo della tavola, raccordi a
  pressare, valvolame del pollice del tubo, tee, guaina, collari), i tratti corti in centrale a 1 m, gli stacchi senza
  tubo; `distinta --costo` prezza col listino della minuteria tutto il materiale (idronico, elettrico, aria,
  frigorifero) in `interno/costo-minuteria.md`, che `consegna` non copia; la protezione chiesta solo sulle linee dal
  quadro. Collaudata con quattro agenti freschi (`docs/collaudi/REL-021/RAPPORTO.md`). Tavole invariate. 150 file.
- **1.15.0** — 6 novembre 2026 (`REL-022`, I-288, I-289, D-237): **la distinta dal contesto della chat** — i metri,
  l'isolamento e i gomiti dei tubi d'acqua li dice il progettista nella chat (blocco `distinta` del grafo, che `completa`
  conserva), non si misurano sul grafo; la pompa di calore a terra, su staffe solo se chieste; il differenziale domestico
  di tipo A; il listino rev. 04 con 27 voci nuove. Con `REL-023` (I-290 … I-292, D-238, D-239): **le giunzioni** —
  un nipplo fra due accessori, un raccordo a pressare fra tubo e accessorio —, **niente valvole antigelo di base**
  nelle case (con la nota sulla tavola), il circolatore fra le apparecchiature, il listino rev. 05 con i nippli. 150 file.
- **1.15.1** — 6 novembre 2026 (`REL-024`, I-295, I-296): **la prima della 2.0 di consolidamento** — la CI su GitHub
  Actions (prove su 3.11 e 3.12, ruff, mypy), mypy strict verde, pypdfium2 fra le dipendenze di sviluppo. Tavole,
  distinta e pianta identiche byte per byte alla 1.15.0. 150 file.
- **1.15.2** — 6 novembre 2026 (`REL-024`, fase 1): **il banco delle tavole come prova** (`scripts/banco.py`,
  `tests/test_il_banco.py`: 28 casi, a ogni PR) e **la skill senza rete** — un'installazione facoltativa non riuscita
  non si ritenta a ogni comando, pip con un limite d'attesa; un accessorio `compreso_in` (filtro a Y, pozzetto compresi
  con la PdC) non esce più in distinta (I-297). Tavole identiche alla 1.15.1. 150 file.
- **2.0.0** — 7 novembre 2026 (`REL-024`, I-299): **la versione da dare ai progettisti** — la 1.15.2 con il numero della
  2.0, tavole identiche. Il consolidamento che resta esce nelle 2.0.x, le funzioni nuove di I-297 nella 2.1. 150 file.
- **2.1.0** — 13 novembre 2026 (`REL-026`, I-300): **i rilievi d'uso della 2.0.0 su una commessa** — la base
  architettonica letta da un sub-agente e ridisegnata in una grafica sola, le scritte fuori pianta col richiamo, le
  lunghezze dalla pianta al grafo, il ventilconvettore canalizzato idronico e il plenum di mandata da 2 a 6 uscite,
  il vaso sanitario. Nel banco cambia la sola pianta del collaudo T3. 155 file.
