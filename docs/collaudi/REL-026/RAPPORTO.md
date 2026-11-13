# REL-026 — La 2.1.0: i rilievi d'uso della 2.0.0 su una commessa. Rapporto

**13 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md` (I-300). Ramo `claude/magical-wright-ffrf86`, PR #95.
**Stato: in attesa che il PO guardi le tavole. Non è fuso.**

Il lavoro esecutivo l'hanno fatto quattro agenti della sessione (D-152), uno per blocco, ciascuno nel suo albero di
lavoro; la sessione ha scritto il pacchetto, unito i rami, rieseguito le misure e guardato le tavole. Quello che gli
agenti hanno riferito sta nei rapporti dei blocchi; **quello che è scritto qui è stato rieseguito dalla sessione** sul
ramo unito, salvo dove è detto il contrario.

| blocco | che cosa | rapporto |
|---|---|---|
| A | catalogo, schema, vaso | `blocco-a/RAPPORTO.md` |
| B | la pianta, prima parte | `blocco-b/RAPPORTO.md` |
| C-1, C-2 | le scritte fuori pianta | `blocco-c-scritte/RAPPORTO.md` |
| C-3 | la base architettonica | `blocco-c-base/RAPPORTO.md` |

## 1. Le tavole, per prime (D-146)

**Le tavole escono da tutti i casi.** Nessun caso di prova è rimasto senza tavola.

| che cosa guardare | dove |
|---|---|
| la base architettonica: origine, base standard, sovrapposizione, impianto sopra | `blocco-c-base/anonimo/1-origine.png` … `4-impianto.png` |
| le scritte fuori pianta: prima tre fogli, dopo uno | `blocco-c-scritte/fitta/prima/`, `…/fitta/dopo/centrale-fitta.png` |
| lo stesso sull'appartamento e sul T3 | `blocco-c-scritte/appartamento/`, `…/t3/`, `…/t3-esempio/` |
| i simboli nuovi | `blocco-a/simboli-nuovi.png` |
| tre ventilconvettori con plenum a 2, 3, 6 uscite | `blocco-a/plenum-di-mandata/tavola/` |
| il plenum motorizzato col ventilconvettore idronico | `blocco-a/plenum-motorizzato/tavola/` |
| il confronto che non cambia il foglio: prima A1, dopo A3 | `blocco-b/discordanze/prima/discordanze.png`, `finale/discordanze/discordanze.png` |
| le lunghezze dalla pianta al grafo | `blocco-b/lunghezze/` |

Le cartelle `blocco-b/` sono la fotografia del blocco B alla sua consegna (i dettagli si aprivano ancora da soli); le
cartelle `blocco-c-*/` e `finale/` sono rifatte **col codice unito** (`rifai_le_tavole.py` in ciascuna).

### Quello che alla sessione sembra sbagliato, anche con i controlli a posto

- **I richiami lunghi.** Un pezzo in mezzo alla pianta (un termostato, la centrale di zona) esce con un richiamo di
  8–12 cm che taglia un locale intero: `blocco-c-scritte/appartamento/dopo/` (TZ-03, TZ-04, CZ-01),
  `finale/discordanze/` (TZ-01 e T55, due linee parallele lungo tutto il disimpegno). Si legge, ma è pesante. Nel caso
  fitto il vecchio dettaglio a 1:20 si leggeva meglio: si può ancora chiedere in `dettagli`.
- **Un richiamo sopra una scritta**: nell'appartamento TZ-04 passa sopra la scritta di T16. Il controllo lo conta
  (`richiami_fuori_sopra_scritte_o_pezzi`) e non ferma la consegna.
- **Il ritorno «col dente»** a ogni confluenza dei ventilconvettori nello schema (i raccordi a T non si specchiano).
- **I plenum a 2 e 3 uscite** si leggono «rettangolo dentro rettangolo»; l'ingresso dei plenum pari sta 1,25 mm fuori
  dal centro, sulla griglia.
- **Le sigle numerate dal basso** (PL-01 è l'ultimo in fondo alla tavola).
- **La tavola della sola base** porta la colonna dell'impianto vuota; **il contorno dei muri** a 1:20 si vede appena.

## 2. Che cosa ha cambiato l'unione dei blocchi

I due rami del blocco C toccavano gli stessi file. Conflitti in `pianta/tavola.py` (il blocco delle scritte fuori e il
ciclo dei nomi dei locali) e in `tests/pianta/conftest.py`, risolti tenendo le due cose.

**Un difetto è nato dall'unione, e l'ha visto una prova, poi la tavola**: con i richiami delle scritte fuori che
attraversano i locali, il nome di un locale non trovava più posto per la scritta intera e perdeva i mq («Camera 3»,
«Disimpegno»). Corretto: prima di rinunciare ai mq il nome va **su due righe**, il nome sopra, zona e mq sotto
(`scritte.posa_dentro_su_due_righe`). Ordine dei tentativi: una riga a 9 pt, due righe a 9 pt, una riga a 8 pt, due
righe a 8 pt, il nome solo. È una scelta grafica: **da confermare dal PO** (§6).

Durante l'unione una corsa della suite ha dato 9 falliti: la sessione stava cambiando i file mentre girava. Rifatta a
file fermi, 0 falliti (§3).

## 3. I criteri, ciascuno col suo comando

*Bozza: le misure sull'ultima testa del ramo si scrivono qui alla chiusura, ciascuna col suo comando e il suo output.*

## 4. Che cosa non è stato fatto o verificato

- **La misura dei 72 avvisi di `pianta --grafo` sulla commessa** (B-5): grafo e pianta di BD.RM.260 non sono arrivati
  in sessione. Il comportamento è provato su un caso anonimo con 49 discordanze (`finale/discordanze/`).
- **La fotografia di un catastale stampato**: l'immagine era solo nella conversazione, non su disco. Non provata.
- **Gli aiuti deterministici sul PDF vettoriale** (leggere i tratti): non fatti. Due «catastali vettoriali» su due
  sono immagini a 1 bit dentro il PDF.
- **Il DXF non è stato aperto in AutoCAD**; della resa dei PDF è provato solo pypdfium2.
- **Il PDF della distinta** non esce in sessione (serve la skill `nove-c-report` accanto): il contenuto è in Markdown.
- **I tempi**: la suite passa da 248 a circa 355 secondi; la pianta dell'appartamento, senza PNG, da 2,2 a 5,5 s (le
  prove di spostamento della pianta per le scritte fuori).

## 5. La prova in camera pulita della lettura della base (C-3)

*Bozza: la prova è in corso (quattro agenti con le sole istruzioni della skill); gli esiti si scrivono qui.*

## 6. Che cosa decide il PO

Niente di quanto segue è stato deciso dalla sessione: è implementato come **proposta**, perché si veda sulla tavola.

**Simboli e schema** — la forma del ventilconvettore canalizzato idronico e dei plenum di mandata, la sigla PL;
l'ingresso dei plenum pari sulla griglia (1,25 mm fuori centro) o al centro esatto; il nome «Ventilconvettore
canalizzato», oggi uguale per `fan-coil-ducted` e `fan-coil-ducted-air`; il corredo di distinta dei pezzi nuovi (oggi
DA DEFINIRE, sezione X); la distinta che dice «unità interna» anche per il ventilconvettore; le porte
`consenso_in`/`consenso` tenute facoltative; la porta `p1p2` del `zone-controller`, obbligatoria, nell'esempio collegata
al `bus` del ventilconvettore.

**Vaso sanitario** — la precarica uguale alla pressione di rete; il margine fino a 5 bar (taratura − 0,5); la serie
delle taglie e la scelta della taglia (sull'esempio di Caleffi il comando sceglie 80 l, Caleffi propone 60); l'acqua
fredda a 10 °C.

**Base architettonica** — i colori (muri `#dcdcdc` col contorno `#a8a8a8`, finestre `#d6ecfa`/`#74b3e0`, porte
`#a0a0a0`, nomi `#8a8a8a`); un grigio solo per perimetrali e tramezze; il contorno dei muri a 1:20; i gradini delle
scale; il nome su due righe, poi a 8 pt, poi senza mq; la portafinestra come finestra; i balconi col solo contorno; lo
sfondo fuori dalla tavola quando la base è ridisegnata; l'estrattore dei tratti dal PDF vettoriale.

**Scritte e pianta** — l'ordine dei ripieghi (accanto, richiamo corto, numero in legenda, e solo alla fine fuori); le
righe sopra e sotto oltre alle colonne ai lati; la pianta spostata dal centro del foglio prima di cambiare formato; i
richiami lunghi; «T05/T06» con la barra; il richiamo sopra una scritta permesso come ultima risorsa; un dettaglio
chiesto che si tiene le scritte del suo nodo; le lunghezze nel grafo al millimetro; le tubazioni della centrale «non
in pianta» nel confronto; l'A2 → A3 del T3 con le forature spente.
