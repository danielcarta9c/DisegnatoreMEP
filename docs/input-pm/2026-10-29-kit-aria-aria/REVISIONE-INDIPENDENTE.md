# La revisione indipendente della rev. 0 e cosa ne è stato fatto

Il revisore è un agente lanciato dalla sessione **senza** il contesto della sessione. Gli sono stati dati la tavola
M.02 della rev. 0, l'Excel, `dim.json`, il catastale e l'offerta al cliente (il perimetro dei lavori). Il compito: un
elenco di rilievi per gravità, «in dubbio per eccesso», per un installatore che fa il prezzo chiavi in mano. Il testo
qui sotto è il suo, solo compattato. Accanto a ogni rilievo, l'esito nella rev. consegnata.

## 1. Errori tecnici e affermazioni non giustificate

| # | gravità | rilievo | esito |
|---|---|---|---|
| 1 | alta | I disimpegni del catastale sono **due**, separati da una tramezza con porta a x ≈ 5,45 m (pilastri e spallette, varco ~0,9 m): il plenum cadeva nel varco. UI, plenum e ripresa vanno nel disimpegno est; servono l'attraversamento della tramezza per B1, B3, il bus e la condensa, e il controsoffitto in tutti e due i disimpegni. | **applicato**: blocco nel disimpegno est, uscite verso ovest, B5 nella veletta del soggiorno, fori della tramezza a computo (F.3), controsoffitto dei due disimpegni (Z.1) |
| 2 | alta | Plenum senza codice; il kit Easyzone 5 × Ø200 per FBA60-71 è ~1425×250×454 mm, più largo della UI e quasi largo quanto il disimpegno: i rami che tornano indietro non gli passano accanto. | **applicato**: codice indicativo (AZEZ8DAIBS07M5 con gateway AZX6GTCDA1) e ingombro in tabella; orientamento delle uscite verso i rami, niente ritorni a fianco del plenum |
| 3 | media | La velocità minima della UI (~750 m³/h) supera la zona più piccola; la nota non decideva niente e contraddiceva l'offerta («le stanze non occupate restano chiuse»). | **applicato**: Z4 zona di sfogo con apertura minima, camere chiuse (nota 6, G.7). La frase dell'offerta è stata segnalata al PO |
| 4 | media | Ripresa 800×200: 1,9 m/s lordi, ~3 m/s reali con griglia e filtro; e due filtri (plenum e griglia). | **applicato**: 1000×250 (1,2 m/s lordi), un solo filtro nel plenum di ripresa, griglia senza filtro (Z.5) |
| 5 | media | Bocchette 400×150 con attacco Ø200: plenum più alto della bocchetta, 1,9 m/s su Aeff 0,04; il plenum «da ordinare sulle bocchette scelte» non si può prezzare. | **applicato**: bocchette 400×200, Aeff ≥ 0,055; plenum porta-bocchetta per 400×200 con attacco laterale o dall'alto (B.2); velette ≥ 30 cm (Z.3) |
| 6 | media | «Ø32 (VP20)» e «Ø32 equivalente VP20 (Øe 26)» si contraddicono; manca il raccordo. | **applicato**: PVC Ø32 + raccordo di adattamento VP20/Ø32 (D.2) |
| 7 | bassa | Protezione UE: rif. RXM60R MCA 15,9 A, fusibile massimo 16 A → MTD 1P+N C16, 30 mA, tipo A o F, 6 kA; verificare la targa della RXM60A. | **applicato** (E.2, con la verifica in nota) |
| 8 | bassa | Prevalenza: mancano i transiti e la parzializzazione del ramo corto; ~70 Pa. | **applicato**: budget 70 Pa con i transiti; regolazione automatica e misura delle portate in G.7 |
| 9 | bassa | Madoka e gateway sullo stesso P1-P2: ruoli da impostare; due uscite su una zona da verificare con Airzone. | **applicato** in G.7; la verifica con Airzone resta aperta |

## 2. Voci mancanti o sottostimate

| # | gravità | rilievo | esito |
|---|---|---|---|
| 10 | alta | Prezzo unitario × quantità = contratto a misura: ogni metro in più è un extra. Serve «a corpo, fisso e invariabile, quantità indicative, sopralluogo obbligatorio», una sezione per le voci aggiunte, i prezzi delle varianti. | **applicato**: intestazione dell'Excel, sezione H, sezione V |
| 11 | alta | Assistenze murarie: le aperture sono comprese (l'offerta esclude solo chiusure e ripristini) e mancavano. | **applicato**: sezione F (carotaggio, forature interne, 7 fori nelle tramezze, foro condensa, tracce) |
| 12 | media | MT dell'Airzone nascosto in una voce a metro; spazio nel quadro non verificato. | **applicato**: E.4 a sé, E.6 aggiornamento dello schema, centralino aggiuntivo come variante V.5 |
| 13 | media | Cantiere: POS e oneri della sicurezza, mezzi, trasporto e custodia delle macchine di Nove C, protezioni, pulizia e smaltimenti. | **applicato**: G.9-G.11 |
| 14 | media | Prove fra i due accessi: azoto prima della chiusura del controsoffitto con circuito in pressione e manometro fino al secondo accesso, verbale; prova della condensa; terzo accesso. | **applicato**: G.3, G.5, V.4 |
| 15 | media | App e Webserver: nessuna voce ferma. | **applicato**: kit con Wi-Fi integrato in A.3; il «se non compresa» è sparito |
| 16 | media | Due DiCo (lettera a e lettera c) e collaudo con portate misurate e verbale. | **applicato**: G.7, G.8 |
| 17 | media | I tratti di flessibile non stanno in 3 confezioni senza giunte; fascette ≥ 32 con le curve. | **applicato**: 4 confezioni (pezzi interi), 36 fascette |
| 18 | bassa | Scarico condensa della UE; canalina 4 m con accessori a numero; R32 a 0,2 kg; tasselli sul laterocemento; staffe UE nella sezione giusta. | **applicato**: C.5, C.6, C.8, C.9, C.10, B.10 |

## 3. Lunghezze

| # | gravità | rilievo | esito |
|---|---|---|---|
| 19 | media | Col plenum nel disimpegno est B1 e B3 crescono e attraversano una tramezza; quotare ~7,5 m sui rami peggiori, ~31 m in tutto. | **applicato in parte**: percorsi rifatti sul nuovo blocco (uscite verso ovest, niente ritorni di 180°), B1 e B3 6 m con +0,5 m per l'architrave, totale 26 m quotati, 40 m acquistati |
| 20 | media | Linee frigo: 8 m solo verso NE o NO; sul fronte SE 10-12 m. | **applicato**: 12 m da quotare, variante al metro (V.1) |
| 21 | media | Condensa dal disimpegno est al bagno ≥ 3 m in controsoffitto: quotare 10 m. | **applicato**: 10 m |
| 22 | bassa | Quadro presunto all'ingresso, da confermare. | **applicato** in nota 8 e in pianta |

## 4. Incoerenze

| # | gravità | rilievo | esito |
|---|---|---|---|
| 23 | media | La regola «+1 m e +15%» non era applicata ovunque. | **applicato**: regola unica nel codice (`da_quotare`), con i minimi dichiarati |
| 24 | media | Le portate sommano 1310 m³/h contro i 1080 della UI. | **applicato**: nota 4, portate massime non contemporanee |
| 25 | bassa | Codici delle tratte (E-1) e del computo (E.1) si confondevano; quadro e sezionatore senza sigla. | **applicato**: tratte T01-T18, sigle QE-01 e SZ-01 |
| 26 | bassa | «o derivazione dal circuito più vicino» contraddice l'esclusione dell'offerta. | **applicato**: solo linea dedicata |
| 27 | bassa | Offerta a 4 serrande, tavola a 5. | segnalato al PO (impatto di costo sul plenum) |
| 28 | bassa | Griglie di transito anche per il soggiorno e la porta fra i disimpegni. | **applicato**: Z.6, n 5 con le Aeff |
| 29 | bassa | Formule nell'Excel contro la regola «solo valori». | **applicato**: nessuna formula |

## 5. Leggibilità

| # | gravità | rilievo | esito |
|---|---|---|---|
| 30 | media | Manca una pianta: l'installatore non verifica le lunghezze che quota. | **applicato**: tavola M.03 a 1:50 sul catastale |
| 31 | bassa | Dimensioni e pesi delle macchine, codice e ingombro del plenum, «Unita'» con l'apostrofo, etichetta di B4 ambigua. | **applicato** |

Fonti citate dal revisore: datasheet FBA-A9 / RXM-R
(<https://oceanairuk.com/cdn/shop/files/FBA-A9_RXM-R_Datasheet_102B.pdf>) e scheda Easyzone 5 uscite per FBA60-71
(<https://climaled.fr/en/airzone-easyzone-ducted-medium-motorised-plenum-cmv-daikin-fba60-71-5-outlets-azez8daibs07m5>).
