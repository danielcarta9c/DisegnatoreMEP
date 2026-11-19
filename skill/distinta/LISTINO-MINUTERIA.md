# Listino della minuteria — riferimento interno Nove C

**Revisione 07, 18 novembre 2026** (REL-028: i prezzi Tecnomat Pro e 35 articoli Tecnomat nuovi, §1; le apparecchiature con un ID, il bollitore col serpentino, il rame «CONDY»).
**Revisione 06, 18 novembre 2026.** Riscrive in Markdown il file del PO
`listino_minuteria_pdc_rev02.xlsx` (2 novembre 2026); dalla revisione 05 il listino vive qui:
si aggiorna in questo file, non più nel foglio Excel. **La revisione 06 lo fa a più fornitori**
(`REL-027`, I-302 … I-304): ogni riga dice da chi viene il prezzo, una voce può avere il prezzo di
più fornitori, e la distinta con `--costo` dice **dove comprare**. Ci sono entrati gli ordini
Abbattista e il preventivo Idrosanitaria della commessa PR.MI.059 (§4 e §5).

## A che cosa serve, e a che cosa no

- **Serve** a Nove C: dà un prezzo di riferimento per confrontare i preventivi degli
  installatori e una prima idea del costo della minuteria, quando la lista dei materiali
  l'abbiamo già.
- **Non va nel documento della distinta per l'installatore.** Quel documento resta senza
  prezzi, «a corpo, quantità indicative, sopralluogo obbligatorio», come dicono le istruzioni della distinta. Il
  listino non si mostra all'installatore e non si cita in una tavola.
- **Non è un preventivo.** I prezzi al banco e online sono soggetti a variazione e a spedizione; quelli degli
  ingrossi (§4, §5) sono gli sconti di una commessa, e valgono per la data del documento.
- **Serve anche a fare gli ordini.** Con `--costo` la distinta dice, articolo per articolo, il fornitore che lo
  vende al prezzo più basso, e raccoglie gli articoli in un ordine per fornitore; dice anche quanto costa in più
  comprare da meno fornitori.
- **La skill non lo usa da sé.** Lo legge l'agente, quando il progettista chiede quanto costa
  la minuteria o dove comprarla. Una voce senza prezzo resta **DA PREZZARE**: non si stima.

## Come si legge

- **Netto** vuol dire **IVA esclusa**. Il prezzo con l'IVA è il netto × 1,22: sulle 150
  righe Tecnomat la colonna «IVA inclusa» del foglio era sempre così, ed è stata tolta.
- **Netto/UM** è il netto diviso per la confezione: euro al metro (m), al metro quadro (m²)
  o al pezzo (cad).
- **ID** è il codice del piano dei materiali: I idraulica, F frigorifero, A aeraulica,
  E elettrico, M le apparecchiature (macchine, accumuli, bollitori, circolatori, unità e comandi del clima: dal 18
  novembre 2026 il costo le prezza, D-241). Una lettera dopo il numero (I36a, I36b) distingue le misure della stessa voce.
- **Fornitore** è chi vende l'articolo a quel prezzo; la tabella «I fornitori» qui sotto dice da quali Nove C
  ordina. **Lo stesso ID può avere più righe, una per fornitore**: è la stessa voce della stessa misura.
- **La marca non conta, conta la prescrizione** (I-307): minuteria, volani, accessori. Il gomito a pressare da 32 è APE
  da Tecnomat, Tiemme da Abbattista, RM da Idrosanitaria, ed è la stessa voce. Quello che conta è che l'articolo
  rispetti quello che la voce prescrive: la misura, l'attacco, la pressione, il fondo scala, gli organi che la voce
  nomina (il disconnettore del gruppo di riempimento).
- **⚠ in testa alla nota è uno scostamento** dalla prescrizione: il fondo scala 0–12 al posto di 0–6, l'attacco 3/8"
  al posto di ½", il disconnettore che non c'è. Una riga così **non si sceglie da sé**: il conto prende il prezzo più
  basso fra quelle che rispettano la voce, e se quella con ⚠ costa meno lo dice con un avviso sul prezzo, perché il
  progettista decida. Se nessun fornitore ha un articolo che rispetta la voce, il conto prende quello con ⚠ e lo
  avvisa.
- **Il bollitore si confronta col serpentino** (I-315, I-321): una riga di bollitore dice nella nota la «superficie di
  scambio N m²» del serpentino; il conto la confronta col minimo della pompa di calore che lo scalda (dal manuale
  Shenling, §2.3), e una riga sotto il minimo, o che non la dice, è uno scostamento: non vince il confronto, e se è
  l'unica il conto la prende avvisando. Un serpentino da 0,8 m² costa meno, ma con la pompa di calore non funziona.
- **Le macchine si confrontano col modello** (pompa di calore, unità del clima, comandi): la marca conta, perché
  la garanzia e gli attacchi sono quelli della macchina scelta. Una macchina di un'altra marca è uno scostamento.
- **Mai un pezzo che fa un altro mestiere** sotto l'ID di una voce: il gruppo di sicurezza sull'acqua fredda del
  bollitore non diventa una valvola di sicurezza qualsiasi. Un articolo che fa un'altra cosa prende un altro ID, o
  «—».
- **ID «—»**: la riga è documentata, ma nessuna regola della distinta la usa ancora (un articolo che la lista non
  chiede, una misura che la regola non distingue). Il conto non la legge.
- **Tre gradi di affidabilità.** Gli ordini e i preventivi dei fornitori (§4, §5) e le fatture (§2ter) sono
  prezzi veri, alla data del documento. Le righe Tecnomat (§1) le hanno rilevate il PO e Claude insieme, col prezzo Tecnomat Pro il 18 novembre 2026,
  sul sito del negozio, con Claude in Chrome nel browser del PO (I-311). Le righe online (§2) vengono dal motore di ricerca: le pagine dei negozi non si
  aprivano dalla sessione, quindi **il prezzo non è stato letto sulla pagina del prodotto**.
  Valgono come ordine di grandezza, e prima di usarle per una trattativa si apre il link.

## Come si aggiorna

Si cambia la riga, e si scrive nel titolo del capitolo la data del nuovo rilievo. Una voce
nuova prende il primo ID libero della sua famiglia. Un prezzo senza fonte (negozio, codice o
link, data) non entra. Quando una voce del §3 trova un prezzo, si sposta nel §1 o nel §2.

**Un'offerta o un ordine nuovo di un fornitore** prende un capitolo suo, con il numero e la data del documento:
**ogni riga** del documento, con l'ID della voce se l'articolo è quella voce di quella misura, «—» se no. Lo
stesso ID **una volta sola per fornitore**: se un fornitore manda un prezzo nuovo per un articolo che ha già, si
cambia la sua riga (o si toglie quella vecchia) — due prezzi dello stesso fornitore per lo stesso ID fermano la
lettura. Un fornitore nuovo si aggiunge alla tabella qui sotto.

## I fornitori

| Fornitore | Si ordina | Come si paga | Da dove vengono i prezzi | Capitolo |
|---|---|---|---|---|
| Tecnomat | sì | al banco | il rilievo Tecnomat Pro sul sito con Claude in Chrome, nel browser del PO, negozio di Segrate (MI), 18 novembre 2026 (il primo, 2 novembre) | §1 |
| Abbattista | sì | RB 30/60 gg fine mese | due ordini della commessa PR.MI.059, 10 e 13 novembre 2026 | §4 |
| Idrosanitaria | sì | alla consegna | il preventivo della commessa PR.MI.059, 9 novembre 2026 (valido fino al 24 novembre) | §5 |
| Bricoman | no | — | le fatture all'installatore della commessa PR.BG.017, fine ottobre 2026 | §2ter |

«Si ordina: no» vuol dire che il prezzo è un riferimento: entra nel conto solo dove nessun fornitore da cui si
ordina ha quell'articolo, come i prezzi online (§2, §2bis). Il PO ha detto che oggi Nove C compra fra Abbattista,
Tecnomat e Idrosanitaria (I-304); se si comincia a ordinare da Bricoman, si scrive «sì».

## 1. Il rilievo Tecnomat Pro — 18 novembre 2026

Il rilievo con l'account **Tecnomat Pro** di Nove C, negozio di Segrate (MI), il 18 novembre 2026 (REL-028, I-313): il
PO e Claude in Chrome nel suo browser (il file è `docs/rilievi/tecnomat-pro-rilevato-2026-11-18.md`). Il prezzo netto è
il prezzo Pro IVA esclusa letto sulla scheda; «pubblico» nella nota è il prezzo al pubblico, dove la scheda lo
mostrava. Le righe del 2 novembre sono nella storia di git; dove il codice non c'era più, la nota dice «sostituisce».

### Idraulica - tubo multistrato

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I01 | Tubo multistrato PEX-AL-PEX nudo, rotolo | MULTISTRATO APE Ø 16x2 mm NUDO PEX-B ROTOLO 100 m | 10041924 | Tecnomat | Segrate (MI) | 100 m | 69,10 | 0,691 | m | alt: 25004262 rotolo 50 m netto 39,79 |
| I02 | Tubo multistrato PEX-AL-PEX nudo, rotolo | MULTISTRATO APE Ø 20x2 mm NUDO PEX-B ROTOLO 100 m | 10041925 | Tecnomat | Segrate (MI) | 100 m | 106,50 | 1,065 | m | alt: 25004263 rotolo 50 m netto 63,30 |
| I03 | Tubo multistrato PEX-AL-PEX nudo, rotolo o barra | MULTISTRATO APE Ø 26x3 mm NUDO PEX-B ROTOLO 50 m | 10041926 | Tecnomat | Segrate (MI) | 50 m | 113,53 | 2,271 | m | alt: 12086038 verga 2,5 m netto 7,87 |
| I04 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO SHARKBITE PERT/AL/PERT Ø 32 x 3 mm NUDO VERGA DA 3 m | 25115665 | Tecnomat | Segrate (MI) | 3 m | 10,92 | 3,64 | m | alt: 12086039 APE verga 2,5 m netto 11,20 |
| I05 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO APE PEX-B Ø 40 x 3,5 mm NUDO VERGA DA 2,5 m | 25019689 | Tecnomat | Segrate (MI) | 2.5 m | 13,15 | 5,26 | m |  |
| I06 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO APE PEX-B Ø 50 x 3,5 mm NUDO VERGA DA 2,5 m | 25019716 | Tecnomat | Segrate (MI) | 2.5 m | 20,07 | 8,028 | m | 63x3,5: 25019715 verga 2,5 m lordo 40,78 |
| I07 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 16x2 mm PEX-b/Al/PEX-b ROTOLO 100 m SPESSORE GUAINA 6 mm | 25105360 | Tecnomat | Segrate (MI) | 100 m | 69,26 | 0,693 | m | prezzo stock; alt 10067680 rotolo 50 m guaina 6 netto 39,18 |
| I08 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 20x2 mm PEX-b/Al/PEX-b ROTOLO 50 m SPESSORE GUAINA 9 mm | 10041922 | Tecnomat | Segrate (MI) | 50 m | 72,46 | 1,449 | m | alt: 10067681 SYSTEM guaina 6 mm 50 m netto 56,15 |
| I09 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 26x3 mm PEX-b/Al/PEX-b ROTOLO 50 m SPESSORE GUAINA 9 mm | 10041923 | Tecnomat | Segrate (MI) | 50 m | 130,90 | 2,618 | m | alt: 25004261 rotolo 25 m netto 86,39 |
| I10 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 32x3 mm PEX-b/Al/PEX-b ROTOLO 25 m SPESSORE GUAINA 9 mm | 10071536 | Tecnomat | Segrate (MI) | 25 m | 98,69 | 3,948 | m |  |

### Idraulica - raccordi multistrato

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I11 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø20 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000753 | Tecnomat | Segrate (MI) | 1 pz | 3,40 | 3,40 | cad |  |
| I12 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000739 | Tecnomat | Segrate (MI) | 1 pz | 4,86 | 4,86 | cad |  |
| I13 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø 32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000723 | Tecnomat | Segrate (MI) | 1 pz | 7,45 | 7,45 | cad |  |
| I14 | Gomito 90 a pressare | GOMITO 90° PRESSFIT APE APL Ø 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019740 | Tecnomat | Segrate (MI) | 1 pz | 11,65 | 11,65 | cad |  |
| I15 | Gomito 90 a pressare | GOMITO 90° PRESSFIT APE APL Ø 50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019717 | Tecnomat | Segrate (MI) | 1 pz | 21,08 | 21,08 | cad |  |
| I16 | Tee a pressare | TEE PRESSFIT APE APL Ø20 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000730 | Tecnomat | Segrate (MI) | 1 pz | 4,54 | 4,54 | cad |  |
| I17 | Tee a pressare | TEE PRESSFIT APE APL Ø26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000721 | Tecnomat | Segrate (MI) | 1 pz | 6,89 | 6,89 | cad | a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I18 | Tee a pressare | TEE PRESSFIT APE APL Ø 32x32x32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000725 | Tecnomat | Segrate (MI) | 1 pz | 11,02 | 11,02 | cad |  |
| I19 | Tee a pressare | TEE PRESSFIT APE APL F 1 x Ø 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019739 | Tecnomat | Segrate (MI) | 1 pz | 17,65 | 17,65 | cad | tee 40x40x40 non trovato: voce con derivazione F 1" |
| I20 | Tee a pressare | TEE PRESSFIT APE APL Ø 50X50X50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019752 | Tecnomat | Segrate (MI) | 1 pz | 26,22 | 26,22 | cad |  |
| I21 | Raccordo diritto a pressare filettato maschio | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 3/4'' x Ø 20 mm PROFILO PRESSATURA TH-H-U | 12092751 | Tecnomat | Segrate (MI) | 1 pz | 3,26 | 3,26 | cad | APE equivalente solo versione GAS |
| I22 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE M 3/4'' x Ø 26 mm PROFILO PRESSATURA TH-H PER TUBO MULTISTRATO | 10042037 | Tecnomat | Segrate (MI) | 1 pz | 4,01 | 4,01 | cad | attacco 3/4" (non 1"); alt F 1" x 26: 12086283 netto 4,70 |
| I23 | Raccordo diritto a pressare filettato maschio | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 1'' x Ø 32 mm PROFILO PRESSATURA TH-H-U | 12092754 | Tecnomat | Segrate (MI) | 1 pz | 6,43 | 6,43 | cad | attacco 1" (non 1"1/4) |
| I24 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE APL M 1"1/4 x Ø 40 mm PROFILO T H TUBO MULTISTRATO SPESS.3 | 25019707 | Tecnomat | Segrate (MI) | 1 pz | 10,64 | 10,64 | cad |  |
| I25 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE APL F 1"1/2 x Ø 50 mm PROFILO T H TUBO MULTISTRATO SPESS.4 | 25019734 | Tecnomat | Segrate (MI) | 1 pz | 13,65 | 13,65 | cad | versione femmina; maschio non trovato |
| I26a | Manicotto a pressare | MANICOTTO DRITTO A STRINGERE APE Ø 20x20 mm PER TUBO MULTISTRATO | 10041948 | Tecnomat | Segrate (MI) | 1 pz | 4,16 | 4,16 | cad | a stringere |
| I26b | Manicotto a pressare | MANICOTTO DRITTO A STRINGERE APE Ø 26x26 mm PER TUBO MULTISTRATO | 10041949 | Tecnomat | Segrate (MI) | 1 pz | 7,48 | 7,48 | cad | a stringere |
| I26c | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 32x32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000719 | Tecnomat | Segrate (MI) | 1 pz | 5,52 | 5,52 | cad |  |
| I26d | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 40 x 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019709 | Tecnomat | Segrate (MI) | 1 pz | 8,36 | 8,36 | cad |  |
| I26e | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 50 x 50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019736 | Tecnomat | Segrate (MI) | 1 pz | 9,48 | 9,48 | cad |  |
| I27a | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE APL Ø20x16 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000765 | Tecnomat | Segrate (MI) | 1 pz | 3,31 | 3,31 | cad | a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I27b | Riduzione a pressare | MANICOTTO PRESSFIT APE APL Ø 32x26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000726 | Tecnomat | Segrate (MI) | 1 pz | 5,55 | 5,55 | cad |  |
| I27c | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE Ø 40 x 32 mm PROFILO PRESSATURA TH-H MULTISTRATO | 25019723 | Tecnomat | Segrate (MI) | 1 pz | 9,60 | 9,60 | cad |  |
| I27d | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE Ø 50 x 40 mm PROFILO PRESSATURA TH-H MULTISTRATO | 25019750 | Tecnomat | Segrate (MI) | 1 pz | 15,59 | 15,59 | cad |  |

### Idraulica - tubo acciaio

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I28 | Tubo acciaio zincato filettabile, barra | TUBO ACCIAIO ZINCATO 1'' 3 m SENZA SALDATURA 1 FILETTO | 10054077 | Tecnomat | Segrate (MI) | 3 m | 22,66 | 7,553 | m | solo 1/2", 3/4" (16,84) e 1"; 1"1/4-2" da verificare |

### Idraulica - raccorderia filettata

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I29a | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA BERG MONTANA FIGURA 90 GOMITO FF 1"1/4 CONFORME USO ACQUA E GAS | 25018162 | Tecnomat | Segrate (MI) | 1 pz | 2,70 | 2,70 | cad | sostituisce 10035683 (non più a catalogo) |
| I29b | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA ATUSA FIGURA 130R TEE 1" x 3/4" x 3/4" | 25018534 | Tecnomat | Segrate (MI) | 1 pz | 2,93 | 2,93 | cad |  |
| I29c | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1"1/4 CONFORME USO ACQUA E GAS | 25018210 | Tecnomat | Segrate (MI) | 1 pz | 1,95 | 1,95 | cad | sostituisce 10035767 (non più a catalogo) |
| I30a | Raccordo a tre pezzi (bocchettone) ottone | BOCCHETTONE OTTONE GIALLO BANNINGER DRITTO 3 PEZZI 3/4'' TENUTA O-RING SOLO ACQUA | 10024324 | Tecnomat | Segrate (MI) | 1 pz | 3,93 | 3,93 | cad |  |
| I30b | Raccordo a tre pezzi (bocchettone) ottone | BOCCHETTONE DRITTO 3 PEZZI PATTARONI OTTONE GIALLO MF 1" TENUTA O-RING ACQUA - GAS | 25018743 | Tecnomat | Segrate (MI) | 1 pz | 6,55 | 6,55 | cad | sostituisce 10024325 (non più a catalogo) |

### Idraulica - valvolame

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I31 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA ENOLGAS SERIE ATOMIC CON LEVA FF 3/4 PN25 | 25017140 | Tecnomat | Segrate (MI) | 1 pz | 5,16 | 5,16 | cad |  |
| I32 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' | 12080447 | Tecnomat | Segrate (MI) | 1 pz | 6,30 | 6,30 | cad |  |
| I33 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' 1/4 PN16 | 12080448 | Tecnomat | Segrate (MI) | 1 pz | 14,87 | 14,87 | cad |  |
| I34 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' 1/2 PN16 | 12080450 | Tecnomat | Segrate (MI) | 1 pz | 18,24 | 18,24 | cad |  |
| I35 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA SERIE BASIC LEVA FF 2" PN50 | 25017115 | Tecnomat | Segrate (MI) | 1 pz | 34,27 | 34,27 | cad |  |
| I36a | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 3/4'' OTTONE TENUTA IN POLIMERO 12 BAR | 25086992 | Tecnomat | Segrate (MI) | 1 pz | 5,59 | 5,59 | cad |  |
| I36b | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1'' OTTONE TENUTA IN POLIMERO 12 BAR | 25086996 | Tecnomat | Segrate (MI) | 1 pz | 7,09 | 7,09 | cad |  |
| I36c | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1''1/4 OTTONE TENUTA IN POLIMERO 10 BAR | 25086987 | Tecnomat | Segrate (MI) | 1 pz | 10,53 | 10,53 | cad |  |
| I36d | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1''1/2 OTTONE TENUTA IN POLIMERO 10 BAR | 25087010 | Tecnomat | Segrate (MI) | 1 pz | 15,57 | 15,57 | cad |  |
| I37a | Filtro a Y ottone | FILTRO A Y FARG 610 Ø 3/4'' PER ACQUA PN 25 MAGLIA FILTRANTE 500 MICRON | 25068146 | Tecnomat | Segrate (MI) | 1 pz | 7,50 | 7,50 | cad |  |
| I37b | Filtro a Y ottone | FILTRO A Y FARG 610 Ø 1'' PER ACQUA PN 25 MAGLIA FILTRANTE 500 MICRON | 25068170 | Tecnomat | Segrate (MI) | 1 pz | 10,11 | 10,11 | cad | 1"1/4 e 1"1/2 non trovati |

### Idraulica - accessori

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I38a | Defangatore magnetico | FILTRO DEFANGATORE MAGNETICO AQUAFILTRA COMPACT OTTONE 3 VIE FF 3/4 500 MICRON | 25012605 | Tecnomat | Segrate (MI) | 1 pz | 33,20 | 33,20 | cad |  |
| I38b | Defangatore magnetico | FILTRO DEFANGATORE MAGNETICO RBM MP2 1'' 800 µ 11000 GAUSS | 25050370 | Tecnomat | Segrate (MI) | 1 pz | 104,92 | 104,92 | cad |  |
| I43a | Valvola automatica di sfogo aria | VALVOLA SFOGO ARIA AUTOMATICA ITAP 362 M 1/2'' ATTACCO VERTICALE OTTONE | 25087007 | Tecnomat | Segrate (MI) | 1 pz | 4,80 | 4,80 | cad |  |
| I43b | Valvola automatica di sfogo aria | VALVOLA SFOGO ARIA AUTOMATICA ITAP 362 M 3/8'' ATTACCO VERTICALE OTTONE | 25087005 | Tecnomat | Segrate (MI) | 1 pz | 4,22 | 4,22 | cad |  |
| — | Manometro radiale/assiale 0-6 bar | MANOMETRO PRESSIONE 0-12 bar | 10047624 | Tecnomat | Segrate (MI) | 1 pz | 5,33 | 5,33 | cad | ⚠ fondo scala 0–12 bar: la voce chiede 0–6 (I-308); 0–6 non trovato; il rilievo Pro ha trovato un articolo più vicino alla voce (riga I44 qui sotto): questo resta documentato |
| I45 | Termometro a immersione con pozzetto | TERMOMETRO BIMETALLICO FERRARI Ø 80 mm 0 - 120° ATTACCO POSTERIORE POZZETTO | 10046531 | Tecnomat | Segrate (MI) | 1 pz | 6,89 | 6,89 | cad |  |
| I46 | Rubinetto di scarico portagomma | RUBINETTO SCARICO CALDAIA 1/2'' CON PORTAGOMMA | 10012741 | Tecnomat | Segrate (MI) | 1 pz | 3,73 | 3,73 | cad |  |
| — | Gruppo di riempimento automatico | GRUPPO DI RIEMPIMENTO ''FILLER'' 1/2'' | 10034051 | Tecnomat | Segrate (MI) | 1 pz | 24,61 | 24,61 | cad | ⚠ senza disconnettore nel titolo: la voce lo chiede (I-309); alt: 25005259 Honeywell V06F con riduttore netto 48,51; il rilievo Pro ha trovato un articolo più vicino alla voce (riga I47 qui sotto): questo resta documentato |
| I48 | Riduttore di pressione | RIDUTTORE DI PRESSIONE HONEYWELL D04FM TARABILE 1,5 - 6 bar CON FILTRO | 10071827 | Tecnomat | Segrate (MI) | 1 pz | 25,61 | 25,61 | cad | misura attacco da verificare sulla scheda |
| I49a | Tubo flessibile inox / giunto antivibrante | FLESSIBILE ANTIVIBRANTE ACCIAIO INOX MF 1"1/4 A/F LUNGHEZZA 50 cm | 25051084 | Tecnomat | Segrate (MI) | 1 pz | 16,15 | 16,15 | cad |  |
| I49b | Tubo flessibile inox / giunto antivibrante | FLESSIBILE ANTIVIBRANTE ACCIAIO INOX MF 1'' A/F LUNGHEZZA 40 CM PORTATA L/MIN 490 | 12092616 | Tecnomat | Segrate (MI) | 1 pz | 9,59 | 9,59 | cad | ⚠ sostituisce 25017314 (giunto in gomma FF 1" non più a catalogo): flessibile inox MF 1" L 40 cm, non giunto in gomma FF |

### Idraulica - sicurezza

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I40a | Valvola di sicurezza 3 bar | VALVOLA SICUREZZA RBM 1/2'' MF 3 bar PED97/23/CE | 10034052 | Tecnomat | Segrate (MI) | 1 pz | 13,07 | 13,07 | cad |  |
| I40b | Valvola di sicurezza 3 bar | VALVOLA SICUREZZA RBM 3/4'' MF 3 BAR CON MANOMETRO - PN10 | 10046860 | Tecnomat | Segrate (MI) | 1 pz | 14,61 | 14,61 | cad |  |
| I41a | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 8 l Ø 200 mm | 10011741 | Tecnomat | Segrate (MI) | 1 pz | 22,46 | 22,46 | cad |  |
| I41b | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO SANITARIO 12 L Ø 270 MM ATTACCO VERTICALE | 10011742 | Tecnomat | Segrate (MI) | 1 pz | 26,64 | 26,64 | cad | sostituisce 25050885 (non più a catalogo); stesso articolo di I40 |
| I41c | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 25 l Ø 290 mm | 25111039 | Tecnomat | Segrate (MI) | 1 pz | 32,87 | 32,87 | cad | 18/35/50 l da verificare |
| I41d | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 18 l Ø 270 mm | 10011743 | Tecnomat | Segrate (MI) | 1 pz | 29,84 | 29,84 | cad | 24/35/50 l non trovati; a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I42 | Vaso di espansione sanitario | VASO ESPANSIONE AQUAFILL RISCALDAMENTO SANITARIO 12 l Ø 270 mm | 10011742 | Tecnomat | Segrate (MI) | 1 pz | 26,64 | 26,64 | cad | stesso articolo riscaldamento e sanitario |

### Idraulica - circolazione

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I50 | Circolatore elettronico | CIRCOLATORE ELETTRONICO MATRA HOT 25-6 INTERASSE 130 mm CON BOCCHETTONI | 25060502 | Tecnomat | Segrate (MI) | 1 pz | 92,21 | 92,21 | cad | 32-60 non trovato; alt DAB EVOSTA2 40-70 (25130043) netto 105,12 |

### Idraulica - regolazione

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I51 | Valvola deviatrice 3 vie motorizzata | VALVOLA DEVIATRICE 3 VIE GIACOMINI R279B Ø 1'' ATTUATORE K270 220V | 25109732 | Tecnomat | Segrate (MI) | 1 pz | 88,93 | 88,93 | cad |  |
| I52a | Valvola miscelatrice termostatica sanitaria | MISCELATORE TERMOSTATICO GIACOMINI DR156X004 F/F 3/4'' USO SANITARIO E SOLARE | 12102799 | Tecnomat | Segrate (MI) | 1 pz | 46,30 | 46,30 | cad |  |
| I52b | Valvola miscelatrice termostatica sanitaria | MISCELATORE TERMOSTATICO GIACOMINI DR156X005 F/F 1 USO SANITARIO E SOLARE | 12102800 | Tecnomat | Segrate (MI) | 1 pz | 50,16 | 50,16 | cad |  |

### Idraulica - trattamento

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I53 | Dosatore di polifosfati | DOSATORE POLIFOSFATI 1/2'' CON BYBASS ATTACCHI RUOTABILI E CARTUCCIA | 25084336 | Tecnomat | Segrate (MI) | 1 pz | 17,87 | 17,87 | cad |  |
| I54 | Glicole propilenico / antigelo impianti | ANTIGELO FACOT ALIGEL A BASE DI GLICOLE MONOPROPILENICO | 25052255 | Tecnomat | Segrate (MI) | 1 pz | 42,21 | 42,21 | cad | formato confezione da verificare sulla scheda |
| I55a | Additivo inibitore / pulitore per impianti | DECAPANTE FACOT FERRONEX PER IMPIANTI TERMICI NUOVI O RECENTI 1 l | 10016379 | Tecnomat | Segrate (MI) | 1 pz | 10,82 | 10,82 | cad | pulitore/decapante; dosaggio da scheda tecnica |
| I55b | Additivo inibitore / pulitore per impianti | FILMANTE FACOT FILMAX + THERMAKIL PER IMPIANTI TERMICI ALTA E BASSA TEMPERATURA E ANTIALGHE 1 l | 10016381 | Tecnomat | Segrate (MI) | 1 pz | 12,70 | 12,70 | cad |  |

### Idraulica - isolamento

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I56 | Guaina isolante elastomerica sp. 9-13 mm | TUBO ISOLANTE IT-FLEX C1 Ø 22 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040200 | Tecnomat | Segrate (MI) | 2 m | 4,71 | 2,355 | m | lunghezza barra non nel titolo: assunta 2 m, da verificare; Ø18: 10040199 netto 4,39 |
| I57 | Guaina isolante elastomerica sp. 13-19 mm | TUBO ISOLANTE IT-FLEX C1 Ø 28 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040201 | Tecnomat | Segrate (MI) | 2 m | 5,58 | 2,79 | m | lunghezza barra assunta 2 m |
| I58 | Guaina isolante elastomerica sp. 13-19 mm | TUBO ISOLANTE IT-FLEX C1 Ø35 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 25091418 | Tecnomat | Segrate (MI) | 2 m | 6,99 | 3,495 | m | lunghezza barra assunta 2 m |
| I59 | Guaina isolante elastomerica sp. 19 mm | TUBO ISOLANTE IT-FLEX C1 Ø 42 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040204 | Tecnomat | Segrate (MI) | 2 m | 7,98 | 3,99 | m | lunghezza barra assunta 2 m; Ø48: 10040205 netto 8,99 |
| I61 | Nastro adesivo per isolante / colla | NASTRO ADESIVO IN ALLUMINIO ISOCELL FLEX ALU AA H 50 mm x 50 m | 25075683 | Tecnomat | Segrate (MI) | 1 pz | 5,57 | 5,57 | cad | rotolo 50 m |

### Idraulica - fissaggi

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I63 | Collare pesante con gommino e barra filettata M8 | COLLARI PER TUBI FRIULSIDER CON ASOLA Ø 1'' 2 PEZZI TASSELLO NYLON | 10062009 | Tecnomat | Segrate (MI) | 2 pz | 2,21 | 1,105 | cad | confezione da 2 pezzi (1/2" 10062007, 3/4" 10062008 netto 1,48) |
| I64 | Barra filettata M8 / M10 zincata | BARRA FILETTATA M8x1 m ACCIAIO ZINCATO BIANCO | 10066672 | Tecnomat | Segrate (MI) | 1 pz | 1,07 | 1,07 | cad | barra 1 m |
| I65 | Binario / profilo asolato zincato | PROFILO GRIP PF1 32x20x2,5 mm 2 m ACCIAIO DX51 DZ200 INTERASSE ASOLE 35 | 25013666 | Tecnomat | Segrate (MI) | 1 pz | 12,46 | 12,46 | cad | barra 2 m; Pro; pubblico 13,12 |
| I66 | Tassello ad espansione / chimico | TASSELLO IN ACCIAIO FISCHER FAZ II 12/10 Ø 12 mm 1 PEZZO PER CALCESTRUZZO | 12087276 | Tecnomat | Segrate (MI) | 1 pz | 1,75 | 1,75 | cad | M10; M8 non trovato; Pro; pubblico 1,84 |

### Idraulica - sigillanti

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I67a | Teflon / canapa / pasta sigillante / filo sigillante | CANAPA A FILO CON CONTENITORE 80 g | 10069812 | Tecnomat | Segrate (MI) | 1 pz | 3,07 | 3,07 | cad |  |
| I67b | Teflon / canapa / pasta sigillante / filo sigillante | SIGILLANTE GAS E LIQUIDI PTFE FAREN 35S77 75 ml | 10062154 | Tecnomat | Segrate (MI) | 1 pz | 8,16 | 8,16 | cad |  |

### Idraulica - condensa

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I69 | Sifone ispezionabile condensa | SIFONE SCARICO CONDENSA IDROSTILE IN PP MORSETTO Ø 46x32 mm | 12104501 | Tecnomat | Segrate (MI) | 1 pz | 4,88 | 4,88 | cad |  |
| I70a | Tubo flessibile condensa / tubo cristal | TUBO RETEX Ø 16 mm ATOSSICO TRASPARENTE VENDITA AL METRO | 10063143 | Tecnomat | Segrate (MI) | 1 m | 1,89 | 1,89 | m |  |
| I70b | Tubo flessibile condensa / tubo cristal | TUBO RETEX Ø 19 mm ATOSSICO TRASPARENTE VENDITA AL METRO | 10063144 | Tecnomat | Segrate (MI) | 1 m | 2,79 | 2,79 | m |  |

### Idraulica - supporti macchina

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I71a | Basamento antivibrante in gomma per unità esterna | GOMMA ANTIVIBRANTE 100x100x5 mm NERO 4 PEZZI | 25013860 | Tecnomat | Segrate (MI) | 4 pz | 6,48 | 1,62 | cad | 4 pz |
| I72a | Staffe a muro per unità esterna | STAFFE UNIVERSALI CLOCK 420x400x780 mm PORTATA 120 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062345 | Tecnomat | Segrate (MI) | 1 pz | 11,89 | 11,89 | cad | coppia di staffe |
| I72b | Staffe a muro per unità esterna | STAFFE UNIVERSALI CLOCK 465x400x780 mm PORTATA 160 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062346 | Tecnomat | Segrate (MI) | 1 pz | 16,31 | 16,31 | cad | coppia di staffe |

### Frigorifero - linee

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| F01a | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 1/4''x 1 mm GUAINA - vendita al ml | 25022912 | Tecnomat | Segrate (MI) | 1 m | 4,16 | 4,16 | m | linea liquido; "coppia" = 2 tubi (liquido+gas) |
| F01b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 3/8''x 1 mm GUAINA - vendita al ml | 25022913 | Tecnomat | Segrate (MI) | 1 m | 6,52 | 6,52 | m |  |
| F02b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 1/2''x 1 mm GUAINA - vendita al ml | 25022914 | Tecnomat | Segrate (MI) | 1 m | 8,43 | 8,43 | m |  |
| F03b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 5/8''x 1 mm GUAINA 9 mm - vendita al ml | 25022931 | Tecnomat | Segrate (MI) | 1 m | 10,80 | 10,80 | m | 3/4" non trovato |
| F06 | Nastro di finitura per linee frigorifere | NASTRO ADESIVO PVC ISOLANTE ALTEZZA 5 cm LUNGHEZZA 20 m NERO | 10016397 | Tecnomat | Segrate (MI) | 1 pz | 2,75 | 2,75 | cad | rotolo 20 m |

### Frigorifero - condensa

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| F10a | Pompa scarico condensa | POMPA DI SCARICO CONDENSA TECOM DPC40 PORTATA MASSIMA 40 l PREVALENZA MAX 20 m | 25011135 | Tecnomat | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad |  |

### Frigorifero - supporti

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| F11a | Staffe a muro per unità esterna split | STAFFE UNIVERSALI CLOCK 420x400x780 mm PORTATA 120 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062345 | Tecnomat | Segrate (MI) | 1 pz | 11,89 | 11,89 | cad | coppia di staffe |
| F11b | Staffe a muro per unità esterna split | STAFFE UNIVERSALI CLOCK 465x400x780 mm PORTATA 160 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062346 | Tecnomat | Segrate (MI) | 1 pz | 16,31 | 16,31 | cad | coppia di staffe |

### Aeraulica - canali

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| A02a | Tubo flessibile non isolato alluminio | TUBO FLESSIBILE Ø 150 mm ESTENSIBILE IN ALLUMINIO NATURALE L 850 - 3000 mm SPESSORE 0,12 mm | 10042850 | Tecnomat | Segrate (MI) | 1 pz | 16,19 | 16,19 | cad | non isolato; Ø160 non trovato; estensione max 3 m (€/m indicativo = prezzo/3) |

### Aeraulica - accessori

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| A07a | Nastro alluminio / fascette stringitubo | NASTRO ADESIVO IN ALLUMINIO ISOCELL FLEX ALU AA H 50 mm x 50 m SPESSORE 30 µm | 25075683 | Tecnomat | Segrate (MI) | 1 pz | 5,57 | 5,57 | cad | rotolo 50 m |
| A07b | Nastro alluminio / fascette stringitubo | FASCETTE STRINGITUBO ACCIAIO INOX AISI 304 Ø 44-56 mm 2 PEZZI | 10055474 | Tecnomat | Segrate (MI) | 2 pz | 3,40 | 1,70 | cad | 2 pz |

### Elettrico - cavi

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E01 | Cavo FG16OR16 0,6/1 kV | CAVO TRIPOLARE FG16(O)R16 0,6/1 kV SEZIONE 3G2,5 mmq COLORE GRIGIO MATASSA 50m | 10073623 | Tecnomat | Segrate (MI) | 50 m | 64,75 | 1,295 | m | matassa 50 m; alt 100 m 10073624 netto 127,05 |
| E04 | Cavo FG16OR16 0,6/1 kV | CAVO PENTAPOLARE FG16(O)R16 0,6/1 kV SEZIONE 5G2,5 mmq COLORE GRIGIO MATASSA 100m | 10073630 | Tecnomat | Segrate (MI) | 100 m | 220,49 | 2,205 | m |  |
| E06 | Cavo FG16OR16 0,6/1 kV | CAVO PENTAPOLARE FG16(O)R16 0,6/1 kV SEZIONE 5G6 mmq COLORE GRIGIO MATASSA 50m | 25060082 | Tecnomat | Segrate (MI) | 50 m | 253,28 | 5,066 | m |  |
| E07 | Cordina FS17 450/750 V | CAVO UNIPOLARE FS17 CPR 450/750 SEZIONE 1x4 mmq COLORE NERO MATASSA 100 m | 10073509 | Tecnomat | Segrate (MI) | 100 m | 60,57 | 0,606 | m | altri colori stesso prezzo |
| E08 | Cordina FS17 450/750 V | CAVO UNIPOLARE FS17 CPR 450/750 SEZIONE 1x6 mmq COLORE NERO MATASSA 100 m | 10073514 | Tecnomat | Segrate (MI) | 100 m | 83,61 | 0,836 | m | altri colori stesso prezzo |
| E09a | Cavo segnale / bus schermato | CAVO FRO-H2HP-OB 2x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014566 | Tecnomat | Segrate (MI) | 100 m | 69,67 | 0,697 | m |  |
| E09b | Cavo segnale / bus schermato | CAVO FRO-H2HP-OB 4x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014575 | Tecnomat | Segrate (MI) | 100 m | 97,54 | 0,975 | m |  |
| E10 | Cavo FROR (comandi) | CAVO FROR 4x0,50 mmq CAVO ANTIFIAMMA CPR GRIGIO MATASSA 100 m | 12097160 | Tecnomat | Segrate (MI) | 100 m | 97,54 | 0,975 | m | 1,5 mmq non trovato (0,50 mmq) |

### Elettrico - vie cavi

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E11a | Tubo corrugato flessibile | TUBO CORRUGATO SEMPLE' ELEKTRIK Ø 25 mm COLORE NERO MATASSA 50 m | 25062264 | Tecnomat | Segrate (MI) | 50 m | 21,11 | 0,422 | m |  |
| E11b | Tubo corrugato flessibile | TUBO CORRUGATO GEWISS NERO Ø 32 mm MATASSA 50 m | 12103297 | Tecnomat | Segrate (MI) | 50 m | 38,88 | 0,778 | m | Pro; pubblico 41,81 |
| E12a | Tubo rigido PVC con raccordi | TUBO RIGIDO GRIGIO GEWISS Ø 25 mm LUNGHEZZA 3 m | 10044194 | Tecnomat | Segrate (MI) | 3 m | 3,61 | 1,203 | m | Pro; pubblico 4,01 |
| E12b | Tubo rigido PVC con raccordi | TUBO RIGIDO GRIGIO GEWISS Ø 32 mm LUNGHEZZA 3 m | 10044196 | Tecnomat | Segrate (MI) | 3 m | 5,24 | 1,747 | m | Pro; pubblico 5,82 |
| E13a | Canala portacavi PVC con accessori | CANALE UFFICIO ARNOCANALI A 2 SCOMPARTI IN PVC 60x40mm LUNGHEZZA 2m GRIGIO | 12102678 | Tecnomat | Segrate (MI) | 2 m | 7,01 | 3,505 | m | barra 2 m |
| E14a | Guaina spiralata / raccordi guaina IP65 | 2 RACCORDI TUBO-GUAINA Ø 25 mm PVC IP67 BM | 25037261 | Tecnomat | Segrate (MI) | 2 pz | 1,35 | 0,675 | cad | confezione da 2 pezzi |
| E14b | Guaina spiralata / raccordi guaina IP65 | 2 RACCORDI TUBO-GUAINA Ø 32 mm PVC IP67 BM | 25037266 | Tecnomat | Segrate (MI) | 2 pz | 1,93 | 0,965 | cad | confezione da 2 pezzi |

### Elettrico - protezioni

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E15a | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO ABB DIFFERENZIALE 2P PROTETTI 16A 4,5 kA CURVA C 0,03A | 10072117 | Tecnomat | Segrate (MI) | 1 pz | 31,07 | 31,07 | cad | Pro; pubblico 32,70 |
| E16a | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 20A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008032 | Tecnomat | Segrate (MI) | 1 pz | 15,49 | 15,49 | cad | Pro; pubblico 17,21 |
| E16b | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 25A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008046 | Tecnomat | Segrate (MI) | 1 pz | 15,49 | 15,49 | cad | Pro; pubblico 17,21 |
| E17 | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 32A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008050 | Tecnomat | Segrate (MI) | 1 pz | 15,49 | 15,49 | cad | Pro; pubblico 17,21 · a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| E18a | Interruttore magnetotermico differenziale 4P 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO TECNOLINE DIFFERENZIALE 4P 16A TIPO A 30mA 10KA 5 MODULI | 25116915 | Tecnomat | Segrate (MI) | 1 pz | 61,48 | 61,48 | cad |  |
| E18b | Interruttore magnetotermico differenziale 4P 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO TECNOLINE DIFFERENZIALE 4P 20A TIPO A 30mA 10KA 415V 5 MODULI | 25116931 | Tecnomat | Segrate (MI) | 1 pz | 61,48 | 61,48 | cad | 25 e 32 A 30 mA non trovati |
| E19a | Interruttore magnetotermico 1P+N | INTERRUTTORE MAGNETOTERMICO CHINT 10A 1P+N CURVA C 4,5KA 1 MODULO | 25008045 | Tecnomat | Segrate (MI) | 1 pz | 4,06 | 4,06 | cad | Pro; pubblico 4,51 |
| E19b | Interruttore magnetotermico 1P+N | INTERRUTTORE MAGNETOTERMICO CHINT 16A 1P+N CURVA C 4,5KA 1 MODULO | 25008041 | Tecnomat | Segrate (MI) | 1 pz | 4,06 | 4,06 | cad | 20/25/32 A da verificare; Pro; pubblico 4,51 |
| E20 | Interruttore magnetotermico 4P | INTERRUTTORE MAGNETOTERMICO TECNOLINE 4P 32A 10KA 415V 4 MODULI | 25116927 | Tecnomat | Segrate (MI) | 1 pz | 16,56 | 16,56 | cad | ⚠ sostituisce 25062710 (AEG, 97,54): curva non dichiarata in scheda (la variante D è a codice separato 25127507), da verificare C |
| E21a | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO CHINT 2P 25A 30mA TIPO AC 2 MODULI | 25008031 | Tecnomat | Segrate (MI) | 1 pz | 14,68 | 14,68 | cad | tipo AC (no A); Pro; pubblico 16,31 |
| E21b | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO TECNOLINE 2P 40A 30mA 230/240VAC TIPO A 2 MODULI | 25127450 | Tecnomat | Segrate (MI) | 1 pz | 14,34 | 14,34 | cad | a Segrate su ordinazione |
| E21c | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO TECNOLINE 4P 40A 30mA 400/415VAC TIPO A 4 MODULI | 25127438 | Tecnomat | Segrate (MI) | 1 pz | 24,51 | 24,51 | cad | a Segrate su ordinazione |
| E21d | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO ABB 4P 25A | 25007415 | Tecnomat | Segrate (MI) | 1 pz | 77,87 | 77,87 | cad | alt 4P 25A (30mA non esplicitato) |
| E22a | Scaricatore di sovratensioni | SCARICATORE DI SOVRATENSIONE FINDER 2P 230V SPD TIPO II 1P+N | 25003353 | Tecnomat | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad |  |
| E22b | Scaricatore di sovratensioni | SCARICATORE DI SOVRATENSIONE FINDER 4P 230/400V TRIFASE CON INDICATORE DI GUASTO | 25003355 | Tecnomat | Segrate (MI) | 1 pz | 97,54 | 97,54 | cad |  |

### Elettrico - sezionamento

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E23a | Sezionatore / interruttore rotativo in cassetta IP65 bordo macchina | SEZIONATORI DI MANOVRA 32A 4 poli IN CASSETTA CON MANIGLIA GIALLO/ROSSA | 12085434 | Tecnomat | Segrate (MI) | 1 pz | 23,24 | 23,24 | cad | IP non dichiarato |

### Elettrico - quadri

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E24a | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 8 MODULI IP65 | 10040848 | Tecnomat | Segrate (MI) | 1 pz | 9,14 | 9,14 | cad |  |
| E24b | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 12 MODULI IP65 | 10040850 | Tecnomat | Segrate (MI) | 1 pz | 16,48 | 16,48 | cad |  |
| E24c | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 24 MODULI IP65 | 10040851 | Tecnomat | Segrate (MI) | 1 pz | 27,79 | 27,79 | cad |  |
| E25a | Centralino da incasso | CENTRALINO SARTEL INCASSO 8 MODULI CON PORTELLO BIANCO IP40 | 25011885 | Tecnomat | Segrate (MI) | 1 pz | 7,79 | 7,79 | cad |  |
| E25b | Centralino da incasso | CENTRALINO SARTEL INCASSO 12 MODULI CON PORTELLO BIANCO IP40 | 25011888 | Tecnomat | Segrate (MI) | 1 pz | 10,70 | 10,70 | cad |  |
| E26a | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 100x100x50 mm PARETI LISCE IP55 | 25011797 | Tecnomat | Segrate (MI) | 1 pz | 5,33 | 5,33 | cad |  |
| E26b | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 150x110x70 mm PARETI LISCE IP55 | 25011789 | Tecnomat | Segrate (MI) | 1 pz | 7,79 | 7,79 | cad |  |
| E26c | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 190x140x70 mm PARETI LISCE IP55 | 25011795 | Tecnomat | Segrate (MI) | 1 pz | 14,34 | 14,34 | cad |  |

### Elettrico - accessori

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E27a | Pressacavo IP68 | PRESSACAVO CON DADO PG21 IP68 5 PEZZI DOPPIA GUARNIZIONE | 12099464 | Tecnomat | Segrate (MI) | 5 pz | 3,77 | 0,754 | cad | PG21 ~ M25; conf. 5 pz |
| E27b | Pressacavo IP68 | PRESSACAVO CON DADO PG16 IP68 5 PEZZI DOPPIA GUARNIZIONE | 12099463 | Tecnomat | Segrate (MI) | 5 pz | 1,97 | 0,394 | cad | PG16 ~ M20; conf. 5 pz |
| E28a | Morsetti a leva / morsettiera / capicorda | 5 CONNETTORI A LEVE CABLO 2X4 MM² 2 VIE 600V 32A | 10074717 | Tecnomat | Segrate (MI) | 5 pz | 1,64 | 0,328 | cad | conf. 5 pz |
| E28b | Morsetti a leva / morsettiera / capicorda | 5 CONNETTORI A LEVE CABLO 3 VIE 600V 32A | 10073777 | Tecnomat | Segrate (MI) | 5 pz | 1,93 | 0,386 | cad | conf. 5 pz |

### Elettrico - comando

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| E30a | Termostato / cronotermostato ambiente | CRONOTERMOSTATO BPT SETTIMANALE WIFI 220V/240V DA PARETE | 25079387 | Tecnomat | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad | wifi |
| E30b | Termostato / cronotermostato ambiente | TERMOSTATO AMBIENTE ARISTON CUBE ROOM A FILO 3319116 | 25012760 | Tecnomat | Segrate (MI) | 1 pz | 54,30 | 54,30 | cad | filo; Pro; pubblico 56,56 |


### Le voci trovate col rilievo Pro (la parte B)

Gli articoli della distinta che Tecnomat non aveva nel rilievo del 2 novembre, cercati per voce. Una nota che comincia
con ⚠ è uno scostamento. I «non trovato» (27) non entrano: sono nel file del rilievo.

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| A07c | Fascetta stringitubo inox 60–270 mm | FASCETTA STRINGITUBO Ø20 cm INOX (collare di fissaggio Ø200) | 25097787 | Tecnomat | Segrate (MI) | 1 pz | 2,34 | 2,34 | cad |  |
| A08c | Collare di fissaggio isolato Ø200 | FASCETTA STRINGITUBO Ø20 cm INOX (collare di fissaggio Ø200) | 25097787 | Tecnomat | Segrate (MI) | 1 pz | 2,34 | 2,34 | cad | stesso articolo di A07c |
| E33 | Interruttore magnetotermico differenziale 1P+N C10 30 mA tipo A, C10 | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 10A 30 mA CLASSE A | 25008049 | Tecnomat | Segrate (MI) | 1 pz | 15,49 | 15,49 | cad | Pro; pubblico 17,21 · curva non indicata nel titolo |
| E35a | Cavo FG16OR16 0,6/1 kV, 3G1,5 | CAVO FG16(O)R16 0,6/1 kV SEZIONE 3G1,5 mmq COLORE GRIGIO MATASSA 100 m | 10073622 | Tecnomat | Segrate (MI) | 100 m | 97,54 | 0,975 | m | alternativa matassa 50 m (10073621) 56,56 = 1,131 €/m |
| E35c | Cavo FG16OR16 0,6/1 kV, 4G1,5 | CAVO FG16(O)R16 0,6/1 kV SEZIONE 4G1,5 mmq COLORE GRIGIO MATASSA 100 m | 10073627 | Tecnomat | Segrate (MI) | 100 m | 110,66 | 1,107 | m |  |
| E36 | Cavo schermato per sonde FR2OH2R16 / FROHH2R, 2×0,75 | CAVO FRO-H2HP-OB 2x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014566 | Tecnomat | Segrate (MI) | 100 m | 69,67 | 0,697 | m | ⚠ sezione 2×0,50 (la voce: 2×0,75) |
| E37 | Scatola da incasso 503, 3 moduli | SCATOLA INCASSO KML 3 MODULI | 12085813 | Tecnomat | Segrate (MI) | 1 pz | 0,25 | 0,25 | cad |  |
| I44 | Manometro radiale/assiale 0-6 bar | MANOMETRO POSTERIORE FERRARI 0-6 BAR ATTACCO 1/4" | 25004117 | Tecnomat | Segrate (MI) | 1 pz | 3,81 | 3,81 | cad | ⚠ attacco posteriore ¼" (la voce: radiale ½") |
| I47 | Gruppo di riempimento automatico | DISCONNETTORE CILLIT HFB 1/2"-3/4" CON RIDUTTORE (gruppo di riempimento) | 25036575 | Tecnomat | Segrate (MI) | 1 pz | 254,57 | 254,57 | cad | Pro; pubblico 270,82 · su ordinazione · alternativa senza disconnettore: Honeywell V06F 25005259 a 48,51 (non conforme) |
| I68a | Tubo di scarico condensa Ø32 / Ø40 con raccordi, Ø32 PP (HT) barra 2 m | TUBO COES Ø32 mm 1 BICCHIERE HTEM L2000 mm IN PP GRIGIO | 10009262 | Tecnomat | Segrate (MI) | 2 m | 3,57 | 1,785 | m |  |
| I68d | Tubo di scarico condensa Ø32 / Ø40 con raccordi, curva Ø32 87°/45° | CURVA COES Ø32 mm HTB 87,5° IN PP GRIGIO | 10009270 | Tecnomat | Segrate (MI) | 1 pz | 0,75 | 0,75 | cad |  |
| I68f | Tubo di scarico condensa Ø32 / Ø40 con raccordi, manicotto Ø32 | MANICOTTO SCORREVOLE 2 BICCHIERI Ø 32 mm | 10045956 | Tecnomat | Segrate (MI) | 1 pz | 1,15 | 1,15 | cad |  |
| I74 | Gruppo di sicurezza sanitario per bollitore, ¾" | GRUPPO DI SICUREZZA UNIVAL 3/4" TARATURA 7 BAR | 10059049 | Tecnomat | Segrate (MI) | 1 pz | 20,30 | 20,30 | cad | ⚠ taratura 7 bar (la voce: 6 bar) |
| I78a | Riduzione filettata in ottone M × F, 1¼" × 1" | RIDUZIONE OTTONE MF 1"1/4 x 1" | 25018599 | Tecnomat | Segrate (MI) | 1 pz | 3,15 | 3,15 | cad |  |
| I81c | Raccordo diritto a pressare M × multistrato, ½" × 16 | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 1/2'' x Ø 16 mm | 12092747 | Tecnomat | Segrate (MI) | 1 pz | 2,10 | 2,10 | cad |  |
| I82 | Guaina elastomerica sp. 32 mm, tubo Ø35 | TUBO ISOLANTE IT-FLEX C1 Ø35 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 25091418 | Tecnomat | Segrate (MI) | 2 m | 6,99 | 3,495 | m | ⚠ spessore 19 mm (la voce: 32 mm o 30) |
| I83b | Nipplo in ottone | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 3/4" CONFORME USO ACQUA E GAS | 25018205 | Tecnomat | Segrate (MI) | 1 pz | 0,95 | 0,95 | cad |  |
| I83c | Nipplo in ottone | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1" CONFORME USO ACQUA E GAS | 25018203 | Tecnomat | Segrate (MI) | 1 pz | 1,19 | 1,19 | cad |  |
| I83e | Nipplo ridotto 1¼" × 1" | RACCORDO GHISA BERG MONTANA FIGURA 245 NIPPLE RIDOTTO 1"1/4 X 1" CONFORME USO ACQUA E GAS | 25018245 | Tecnomat | Segrate (MI) | 1 pz | 2,29 | 2,29 | cad |  |
| I84a | Guaina isolante elastomerica sp. 9 mm per tubo 26 | TUBO ISOLANTE POLAR 10 Ø 27 mm SPESSORE 10 mm BARRA 2 m | 10017684 | Tecnomat | Segrate (MI) | 2 m | 2,22 | 1,11 | m | ⚠ foro 27, spessore 10 (la voce: foro 28, spessore 9) |
| I84b | Guaina isolante elastomerica sp. 9 mm per tubo 32 | TUBO ISOLANTE POLAR 10 Ø 34 mm SPESSORE 10 mm BARRA 2 m | 10017686 | Tecnomat | Segrate (MI) | 2 m | 2,45 | 1,225 | m | ⚠ foro 34, spessore 10 (la voce: foro 35, spessore 9) |
| I84c | Guaina isolante elastomerica sp. 32 mm per tubo 26 | TUBO ISOLANTE IT-FLEX C1 Ø 28 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040201 | Tecnomat | Segrate (MI) | 2 m | 5,58 | 2,79 | m | ⚠ spessore 19 mm (la voce: 32 mm o 30) |
| I85 | Collante per tubo di scarico condensa rigido | COLLA TANGIT PER PVC-U 125 g | 10027398 | Tecnomat | Segrate (MI) | 1 pz | 7,30 | 7,30 | cad |  |
| I86 | Braga 45° Ø40/32 in PP | BRAGA COES Ø40x32 mm RIDOTTA HTEA 45° IN PP GRIGIO | 10009291 | Tecnomat | Segrate (MI) | 1 pz | 2,42 | 2,42 | cad |  |
| I87 | Clip di fissaggio per tubo condensa rigido | COLLARE DI FISSAGGIO TUBI SCARICO Ø32 - 40 - 50 mm | 10021502 | Tecnomat | Segrate (MI) | 1 pz | 1,60 | 1,60 | cad | confezione non indicata in scheda: assunto 1 pz |
| E34 | Relè modulare su guida DIN, bobina 230 V, contatto 20 A | CONTATTORE 230 V 20 A ABB | 10026879 | Tecnomat | Segrate (MI) | 1 pz | 23,77 | 23,77 | cad | ⚠ contattore, non relè modulare (la voce); la scheda non indica il montaggio su guida DIN |
| I68c | Tubo di scarico condensa Ø32 / Ø40 con raccordi, Ø40 PVC arancio barra 2 m | TUBO Ø 40 mm 3 m ARANCIO | 10035941 | Tecnomat | Segrate (MI) | 3 m | 5,41 | 1,803 | m | alternativa barra 1 m (10035932) 2,01 €/m |
| I68e | Tubo di scarico condensa Ø32 / Ø40 con raccordi, curva Ø40 87°/45° | CURVA 87° Ø 40 mm PVC ARANCIO | 10035540 | Tecnomat | Segrate (MI) | 1 pz | 0,37 | 0,37 | cad |  |
| I68g | Tubo di scarico condensa Ø32 / Ø40 con raccordi, manicotto Ø40 | GIUNTO DI RIPARAZIONE Ø 40 mm PVC ARANCIO | 12082231 | Tecnomat | Segrate (MI) | 1 pz | 5,16 | 5,16 | cad | ⚠ giunto di riparazione, non manicotto semplice |
| I75 | Valvola a sfera FF a passaggio totale, ½" | VALVOLA A SFERA PER ACQUA ENOLGAS SERIE ATOMIC CON LEVA FF 1/2 PN25 | 25017114 | Tecnomat | Segrate (MI) | 1 pz | 3,57 | 3,57 | cad | passaggio totale non verificato in scheda |
| I78b | Riduzione filettata in ottone M × F, 1" × ¾" | RIDUZIONE OTTONE MF 1" x 3/4" | 25018605 | Tecnomat | Segrate (MI) | 1 pz | 1,70 | 1,70 | cad |  |
| I81a | Gomito a pressare multistrato, 16×2 | RACCORDO PRESSFIT APE APL GOMITO Ø 16 x Ø 16 mm PRESSATURA TH-H-U TUBO | 25000740 | Tecnomat | Segrate (MI) | 1 pz | 2,65 | 2,65 | cad |  |
| I81b | Manicotto a pressare multistrato, 16×2 | RACCORDO PRESS FIT GIACOMINI MULTISTRATO MANICOTTO Ø 16x16 mm PROFILO PRESSATURA TH-H-U | 12092781 | Tecnomat | Segrate (MI) | 1 pz | 3,34 | 3,34 | cad |  |
| I83a | Nipplo in ottone | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1/2" CONFORME USO ACQUA E GAS | 25018214 | Tecnomat | Segrate (MI) | 1 pz | 0,78 | 0,78 | cad |  |
| I83d | Nipplo ridotto in ottone | RACCORDO GHISA BERG MONTANA FIGURA 245 NIPPLE RIDOTTO 1" X 3/4" CONFORME USO ACQUA E GAS | 25018251 | Tecnomat | Segrate (MI) | 1 pz | 1,48 | 1,48 | cad |  |

## 2. Il riferimento online — 5 novembre 2026

Le 18 voci che il rilievo Tecnomat non aveva trovato. I riscontri sono 167, presi da
rivenditori italiani con un prezzo pubblico. Ogni riga ha il suo link.

- **Da dove vengono i prezzi.** Dai riassunti del motore di ricerca: nessuna pagina è stata
  aperta, e il riassunto non ha data. Due ricerche di controllo su sei hanno ritrovato lo
  stesso prezzo (cavo 3G6 su RS e Leroy Merlin); il Caleffi 551007 è coerente con i prezzi
  americani dello stesso codice; le altre tre non hanno ritrovato la riga.
- **IVA.** Dove il negozio non dice se l'IVA è compresa, la si presume compresa, perché a un
  privato il prezzo si espone IVA inclusa. Queste righe sono scritte «non detta».
- **Forbice e mediana.** Il riepilogo dà, per voce e misura (con il suo **codice**, che le regole della distinta usano: l'ID, più una lettera quando la voce ha più misure), il netto per unità più basso,
  la mediana e il più alto dei riscontri. La mediana è il riferimento da usare. Una riga
  segnata «fuori forbice» non entra nel conto.
- **Misure vicine.** Dove la misura del piano non c'era, si danno quelle vicine, ed è scritto
  nella colonna Misura (I60).

### Riepilogo

| Codice | ID | Voce | Misura | Riscontri | Netto/UM min € | Mediana € | Max € | UM |
|---|---|---|---|--:|--:|--:|--:|---|
| I39a | I39 | Separatore d'aria (disaeratore) | 1" | 3 | 84,11 | 96,83 | 126,93 | cad |
| I39b | I39 | Separatore d'aria (disaeratore) | 1"1/4 | 3 | 95,08 | 167,58 | 168,82 | cad |
| I60a | I60 | Guaina isolante elastomerica sp. 19 mm per tubo 50-54 | sp. 19, tubo Ø42 (sotto) | 1 | 3,30 | 3,30 | 3,30 | m |
| I60b | I60 | Guaina isolante elastomerica sp. 19 mm per tubo 50-54 | sp. 19, tubo Ø60 (sopra) | 1 | 4,49 | 4,49 | 4,49 | m |
| I60c | I60 | Guaina isolante elastomerica sp. 19 mm per tubo 50-54 | sp. 13, tubo Ø54 | 1 | 2,06 | 2,06 | 2,06 | m |
| I62a | I62 | Finitura esterna dell'isolante (PVC, alluminio, nastro UV) | benda PVC Isogenopak h 100 mm | 1 | 1,71 | 1,71 | 1,71 | m |
| I62b | I62 | Finitura esterna dell'isolante (PVC, alluminio, nastro UV) | nastro PVC per clima | 1 | 0,14 | 0,14 | 0,14 | m |
| I62c | I62 | Finitura esterna dell'isolante (PVC, alluminio, nastro UV) | foglio alluminio/poliestere UV autoadesivo | 1 | 15,16 | 15,16 | 15,16 | m |
| I62d | I62 | Finitura esterna dell'isolante (PVC, alluminio, nastro UV) | lamierino alluminio 0,5 mm | 1 | 12,21 | 12,21 | 12,21 | m² |
| I62e | I62 | Finitura esterna dell'isolante (PVC, alluminio, nastro UV) | curva 90° PUR + PVC | 1 | 6,45 | 6,45 | 6,45 | cad |
| I68a | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | Ø32 PP (HT) barra 2 m | 4 | 1,73 | 1,94 | 2,10 | m |
| I68b | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | Ø40 PP (HT) barra 2 m | 3 | 1,68 | 1,72 | 2,21 | m |
| I68c | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | Ø40 PVC arancio barra 2 m | 2 | 1,91 | 2,28 | 2,66 | m |
| I68d | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | curva Ø32 87°/45° | 1 | 0,78 | 0,78 | 0,78 | cad |
| I68e | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | curva Ø40 87°/45° | 2 | 0,47 | 0,64 | 0,81 | cad |
| I68f | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | manicotto Ø32 | 1 | 1,48 | 1,48 | 1,48 | cad |
| I68g | I68 | Tubo di scarico condensa Ø32 / Ø40 con raccordi | manicotto Ø40 | 1 | 1,39 | 1,39 | 1,39 | cad |
| F07a | F07 | Canalina copritubo per condizionatori | 60x45 | 5 | 2,03 | 2,46 | 3,24 | m |
| F07b | F07 | Canalina copritubo per condizionatori | 80x60 | 5 | 2,58 | 3,44 | 4,27 | m |
| F08a | F08 | Curve e raccordi della canalina copritubo | 60x45 curva piana | 3 | 2,75 | 3,28 | 4,43 | cad |
| F08b | F08 | Curve e raccordi della canalina copritubo | 60x45 angolo interno/esterno | 4 | 1,47 | 2,00 | 2,30 | cad |
| F08c | F08 | Curve e raccordi della canalina copritubo | 60x45 passaggio a muro | 2 | 1,84 | 2,19 | 2,54 | cad |
| F08d | F08 | Curve e raccordi della canalina copritubo | 60x45 tappo terminale | 2 | 1,57 | 1,74 | 1,92 | cad |
| F08e | F08 | Curve e raccordi della canalina copritubo | 80x60 curva piana | 3 | 1,80 | 3,50 | 3,69 | cad |
| F08f | F08 | Curve e raccordi della canalina copritubo | 80x60 angolo interno/esterno | 4 | 2,20 | 2,41 | 3,24 | cad |
| F08g | F08 | Curve e raccordi della canalina copritubo | 80x60 giunto | 1 | 1,80 | 1,80 | 1,80 | cad |
| F08h | F08 | Curve e raccordi della canalina copritubo | 80x60 passaggio a muro | 2 | 1,80 | 1,90 | 1,99 | cad |
| F08i | F08 | Curve e raccordi della canalina copritubo | 80x60 tappo terminale | 2 | 1,39 | 2,01 | 2,62 | cad |
| F09a | F09 | Dadi a cartella e giunzioni per rame | dado a cartella 1/4" | 3 | 0,49 | 0,57 | 0,73 | cad |
| F09b | F09 | Dadi a cartella e giunzioni per rame | dado a cartella 3/8" | 2 | 0,90 | 0,98 | 1,06 | cad |
| F09c | F09 | Dadi a cartella e giunzioni per rame | dado a cartella 1/2" | 2 | 1,06 | 1,12 | 1,19 | cad |
| F09d | F09 | Dadi a cartella e giunzioni per rame | dado a cartella 5/8" | 2 | 1,20 | 1,23 | 1,27 | cad |
| F09e | F09 | Dadi a cartella e giunzioni per rame | giunto a doppia cartella 1/4" | 3 | 0,70 | 1,07 | 1,14 | cad |
| F09f | F09 | Dadi a cartella e giunzioni per rame | giunto a doppia cartella 3/8" | 2 | 1,55 | 1,77 | 2,00 | cad |
| F09g | F09 | Dadi a cartella e giunzioni per rame | giunto a doppia cartella 1/2" | 2 | 1,96 | 2,17 | 2,38 | cad |
| F09h | F09 | Dadi a cartella e giunzioni per rame | giunto a doppia cartella 5/8" | 3 | 2,87 | 3,58 | 5,67 | cad |
| F09i | F09 | Dadi a cartella e giunzioni per rame | manicotto a brasare 1/4" | 2 | 0,28 | 0,75 | 1,23 | cad |
| F09j | F09 | Dadi a cartella e giunzioni per rame | manicotto a brasare 3/8" | 1 | 2,20 | 2,20 | 2,20 | cad |
| A01a | A01 | Tubo flessibile isolato per aria, rotolo 10 m | Ø125 | 4 | 3,24 | 5,95 | 11,30 | m |
| A01b | A01 | Tubo flessibile isolato per aria, rotolo 10 m | Ø160 | 4 | 5,09 | 7,33 | 7,72 | m |
| A01c | A01 | Tubo flessibile isolato per aria, rotolo 10 m | Ø200 | 3 | 4,46 | 8,84 | 9,20 | m |
| A03a | A03 | Canale spiroidale zincato e raccordi | spiroidale Ø125 | 1 | 9,36 | 9,36 | 9,36 | m |
| A03b | A03 | Canale spiroidale zincato e raccordi | spiroidale Ø160 | 2 | 10,04 | 11,01 | 11,98 | m |
| A03c | A03 | Canale spiroidale zincato e raccordi | spiroidale Ø200 | 3 | 12,29 | 13,23 | 15,98 | m |
| A03d | A03 | Canale spiroidale zincato e raccordi | curva 90° Ø125 | 2 | 7,25 | 7,41 | 7,57 | cad |
| A03e | A03 | Canale spiroidale zincato e raccordi | curva 90° Ø160 | 2 | 10,93 | 10,96 | 11,00 | cad |
| A03f | A03 | Canale spiroidale zincato e raccordi | curva 90° Ø200 | 2 | 15,03 | 15,15 | 15,26 | cad |
| A03g | A03 | Canale spiroidale zincato e raccordi | tee 90° Ø160 | 1 | 16,86 | 16,86 | 16,86 | cad |
| A03h | A03 | Canale spiroidale zincato e raccordi | riduzione 160/125 | 2 | 6,23 | 7,79 | 9,35 | cad |
| A03i | A03 | Canale spiroidale zincato e raccordi | riduzione 200/160 | 2 | 8,03 | 8,77 | 9,51 | cad |
| A04a | A04 | Bocchetta di mandata a doppio filare di alette | 300x100 | 3 | 12,10 | 18,85 | 31,97 | cad |
| A04b | A04 | Bocchetta di mandata a doppio filare di alette | 400x150 | 4 | 23,77 | 24,57 | 43,44 | cad |
| A05a | A05 | Griglia di ripresa con filtro | 400x200 | 4 | 34,10 | 46,88 | 76,72 | cad |
| A05b | A05 | Griglia di ripresa con filtro | 600x300 | 3 | 48,38 | 60,86 | 80,13 | cad |
| A06a | A06 | Plenum porta-bocchetta | 300x100 | 4 | 18,55 | 21,95 | 32,99 | cad |
| A06b | A06 | Plenum porta-bocchetta | 400x150 | 4 | 28,00 | 30,69 | 31,50 | cad |
| A08a | A08 | Pendini e sospensioni | barra filettata M8 1 m | 2 | 1,07 | 1,10 | 1,14 | cad |
| A08b | A08 | Pendini e sospensioni | sospensione a cavetto 3 m | 2 | 7,68 | 8,54 | 9,39 | cad |
| E02 | E02 | Cavo FG16OR16 0,6/1 kV 3G4 | 3G4 | 5 | 1,88 | 2,28 | 2,44 | m |
| E03 | E03 | Cavo FG16OR16 0,6/1 kV 3G6 | 3G6 | 6 | 2,93 | 3,32 | 5,21 | m |
| E05 | E05 | Cavo FG16OR16 0,6/1 kV 5G4 | 5G4 | 5 | 3,46 | 3,77 | 3,85 | m |
| E29a | E29 | Fascette, collari e graffette per cavi | fascette 4,8x300 nere | 3 | 0,030 | 0,038 | 0,045 | cad |
| E29b | E29 | Fascette, collari e graffette per cavi | fascette 4,8x300 nere UV | 1 | 0,099 | 0,099 | 0,099 | cad |
| E29c | E29 | Fascette, collari e graffette per cavi | fascette 4,8x350 nere | 1 | 0,040 | 0,040 | 0,040 | cad |
| E29d | E29 | Fascette, collari e graffette per cavi | collare fissatubo Ø20 | 2 | 0,093 | 0,12 | 0,16 | cad |
| E29e | E29 | Fascette, collari e graffette per cavi | collare fissatubo Ø25 | 2 | 0,11 | 0,14 | 0,16 | cad |
| E29f | E29 | Fascette, collari e graffette per cavi | clip a scatto Ø25 | 2 | 0,069 | 0,085 | 0,10 | cad |
| E29g | E29 | Fascette, collari e graffette per cavi | graffetta a chiodo 12-14 mm | 2 | 0,020 | 0,038 | 0,057 | cad |

### Il dettaglio, voce per voce

### I39 — Separatore d'aria (disaeratore)

Famiglia: Idraulica - accessori.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 1" | Amazon.it | Caleffi Discal 551006 disaeratore 1" | 1 pz | 118,13 | inclusa | 96,83 | 96,83 | cad | altre offerte da 122,18 | [link](https://www.amazon.it/DEGASATORE-1-551006-CALEFFI-103872/dp/B009L4F2NQ) |
| 1" | Leroy Merlin (marketplace) | Caleffi Discal 551006 1" attacchi F | 1 pz | 154,85 | inclusa | 126,93 | 126,93 | cad | venditore Officina Idraulica | [link](https://www.leroymerlin.it/prodotti/caleffi-discal-dirtmag-p.html) |
| 1" | Amazon.it | FAR 2250 disaeratore 1" (senza coibentazione) | 1 pz | 102,62 | inclusa | 84,11 | 84,11 | cad | equivalente, non Caleffi | [link](https://www.amazon.it/2250-mis-Disaeratore-impianti-termici/dp/B01MV6HL17) |
| 1"1/4 | Leroy Merlin | Caleffi Discal 551007 1"1/4 attacchi F | 1 pz | 205,96 | inclusa | 168,82 | 168,82 | cad |  | [link](https://www.leroymerlin.it/prodotti/551007-1-1-4-discal-disaeratore-attacchi-filettati-f-caleffi-92595433.html) |
| 1"1/4 | ManoMano | Caleffi Discal 551007 1"1/4 | 1 pz | 204,45 | inclusa | 167,58 | 167,58 | cad | altri riassunti 177,88 e 158,70 | [link](https://www.manomano.it/p/551007-1-1-4-discal-disaeratore-attacchi-filettati-f-caleffi-35855260) |
| 1"1/4 | eBay.it | FAR 2251 1"1/4 disaeratore con coibentazione | 1 pz | 116,00 | non detta (presunta inclusa) | 95,08 | 95,08 | cad | equivalente, non Caleffi | [link](https://www.ebay.it/itm/2251-114-1-1-4-Disaeratore-per-impianti-termici-completo-di-coibentazione-FAR-/301030056196) |

### I60 — Guaina isolante elastomerica sp. 19 mm per tubo 50-54

Famiglia: Idraulica - isolamento.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| sp. 19, tubo Ø42 (sotto) | Leroy Merlin | IT-FLEX C1 sp. 19 Ø int. 42 EVM042, a metro | 1 m | 4,02 | inclusa | 3,30 | 3,30 | m | misura vicina, non 54 | [link](https://www.leroymerlin.it/prodotti/tubo-isolante-guaina-it-flex-c1-spessore-19-mm-interno-42-mm-prezzo-e-unita-di-vendita-a-metro-acquisto-min-2-metri-e-multipli-evm042-94552098.html) |
| sp. 19, tubo Ø60 (sopra) | Leroy Merlin | IT-FLEX C1 sp. 19 Ø int. 60 EVM060N, a metro | 1 m | 5,48 | inclusa | 4,49 | 4,49 | m | misura vicina, non 54 | [link](https://www.leroymerlin.it/prodotti/tubo-isolante-guaina-it-flex-c1-spessore-19-mm-interno-60-mm-prezzo-e-unita-di-vendita-a-metro-acquisto-min-2-metri-e-multipli-evm060n-94551933.html) |
| sp. 13, tubo Ø54 | Leroy Merlin (marketplace) | IT-FLEX C1 sp. 13 Ø int. 54 EVH054N, a metro | 1 m | 2,51 | inclusa | 2,06 | 2,06 | m | spessore 13, non 19; promozione | [link](https://www.leroymerlin.it/prodotti/edilizia/prodotti-per-isolamento/isolamento-termico/guaina-isolante-2-m-p.html) |

### I62 — Finitura esterna dell'isolante (PVC, alluminio, nastro UV)

Famiglia: Idraulica - isolamento.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| benda PVC Isogenopak h 100 mm | Leroy Merlin | Benda PVC Isogenopak bianca-grigia, rotolo 25 m | 25 m | 52,29 | inclusa | 42,86 | 1,71 | m | €/m di benda, non di tubo | [link](https://www.leroymerlin.it/prodotti/benda-in-pvc-isogenopak-per-copertura-tubazioni-di-impianti-di-condizionamento-riscaldamento-bianca-grigia-92357561.html) |
| nastro PVC per clima | eBay.it | Benda nastro PVC fascia isolante panna 25 m | 25 m | 4,20 | non detta (presunta inclusa) | 3,44 | 0,14 | m | UV non dichiarata | [link](https://www.ebay.it/itm/165480384697) |
| foglio alluminio/poliestere UV autoadesivo | Amazon.it | Isolpak CLAD 7 strati, bianco, fascia 600 mm | 1 m | 18,50 | inclusa | 15,16 | 15,16 | m | fascia 0,6 m: ~25 €/m² | [link](https://www.amazon.it/Isolpak-CLAD-autoadesiva-poliestere-resistente/dp/B0CNS2HLQ6) |
| lamierino alluminio 0,5 mm | eBay.it | Lastra alluminio 99,5 per coibentazione 0,5x1000, al m² | 1 m² | 14,90 | non detta (presunta inclusa) | 12,21 | 12,21 | m² | al m² | [link](https://www.ebay.it/itm/166555009601) |
| curva 90° PUR + PVC | Amazon.it | Curva PUR con rivestimento PVC 90° SCP-PURB4840 | 1 pz | 7,87 | inclusa | 6,45 | 6,45 | cad | per rame 22 con isolamento 20 | [link](https://www.amazon.it/Tubo-curvo-rivestimento-gradi-SCP-PURB4840/dp/B0BR82GJ3R) |

### I68 — Tubo di scarico condensa Ø32 / Ø40 con raccordi

Famiglia: Idraulica - condensa.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| Ø32 PP (HT) barra 2 m | Tecnomat | Gabbaplast HTEM 1 bicchiere Ø32 L 2000 (25040992) | 2 m | 4,23 | inclusa | 3,47 | 1,73 | m |  | [link](https://www.tecnomat.it/it/tubo-gplast-1-bic-htem-o32mm-l2000mm-gr-25040992/) |
| Ø32 PP (HT) barra 2 m | Tecnomat | Gabbaplast HTDM 2 bicchieri Ø32 L 2000 (25040982) | 2 m | 5,13 | inclusa | 4,20 | 2,10 | m |  | [link](https://www.tecnomat.it/it/tubo-gplast-2-bic-htdm-o32mm-l2000mm-gr-25040982/) |
| Ø32 PP (HT) barra 2 m | OBI | Tubo HTEM 1 bicchiere Ø32 x 200 cm | 2 m | 4,69 | inclusa | 3,84 | 1,92 | m |  | [link](https://www.obi-italia.it/p/2464162/tubo-htem-con-1-bicchiere-32-mm-x-200-cm) |
| Ø32 PP (HT) barra 2 m | Leroy Merlin | Tubo HTDM 2 bicchieri Ø32 L 200 PP | 2 m | 4,80 | inclusa | 3,93 | 1,97 | m |  | [link](https://www.leroymerlin.it/prodotti/tubo-per-scarico-2-bicchieri-htdm-32-mm-x-l200-cm-in-polipropilene-31047226.html) |
| Ø40 PP (HT) barra 2 m | Tecnomat | Gabbaplast HTDM 2 bicchieri Ø40 L 2000 (25040979) | 2 m | 4,09 | inclusa | 3,35 | 1,68 | m |  | [link](https://www.tecnomat.it/it/tubo-gplast-2-bic-htdm-o40mm-l2000mm-gr-25040979/) |
| Ø40 PP (HT) barra 2 m | OBI | Tubo HTEM 1 bicchiere Ø40 x 200 cm | 2 m | 4,19 | inclusa | 3,43 | 1,72 | m |  | [link](https://www.obi-italia.it/p/1518208/tubo-htem-con-1-bicchiere-40-mm-x-200-cm) |
| Ø40 PP (HT) barra 2 m | Bricocenter | Tubo 2 bicchieri Ø40 L 200 HTDM | 2 m | 5,40 | inclusa | 4,43 | 2,21 | m | pagina di categoria | [link](https://www.bricocenter.it/prodotti/default/idraulica-e-riscaldamento/impianti-per-scarico-acqua/tubi-e-raccordi-polipropilene.html) |
| Ø40 PVC arancio barra 2 m | Tecnomat | Tubo Ø40 2 m arancio (25008796) | 2 m | 4,65 | inclusa | 3,81 | 1,91 | m |  | [link](https://www.tecnomat.it/it/tubo-o-40-mm-2-m-arancio-25008796/) |
| Ø40 PVC arancio barra 2 m | Bricocenter | Tubo PVC arancio 2 m Ø40 | 2 m | 6,50 | inclusa | 5,33 | 2,66 | m |  | [link](https://www.bricocenter.it/prodotti/default/430640006-tubo-pvc-arancio-2mt-d-40.html) |
| curva Ø32 87°/45° | OBI | Curva HTB Ø32 87° (45° stesso prezzo) | 1 pz | 0,95 | inclusa | 0,78 | 0,78 | cad |  | [link](https://www.obi-italia.it/curve-ht/curva-htb-32-mm-87-/p/2464238) |
| curva Ø40 87°/45° | OBI | Curva HTB Ø40 87° | 1 pz | 0,99 | inclusa | 0,81 | 0,81 | cad |  | [link](https://www.obi-italia.it/p/1352277/curva-htb-40-mm-87-) |
| curva Ø40 87°/45° | ManoMano | Curva 87,5° PP Ø40 Bampi BBO040087 | 1 pz | 0,57 | inclusa | 0,47 | 0,47 | cad |  | [link](https://www.manomano.it/p/curva-40-mm-87-in-polipropilene-ad-innesto-bampi-50955721) |
| manicotto Ø32 | OBI | Manicotto HTU Ø32 | 1 pz | 1,80 | inclusa | 1,48 | 1,48 | cad |  | [link](https://www.obi-italia.it/tubi-di-scarico-ht/manicotto-htu-32-mm/p/2464246) |
| manicotto Ø40 | OBI | Manicotto HTU Ø40 | 1 pz | 1,69 | inclusa | 1,39 | 1,39 | cad |  | [link](https://obi-italia.it/raccordi-ht/manicotto-htu-40-mm/p/1352038) |

### F07 — Canalina copritubo per condizionatori

Famiglia: Frigorifero - linee.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 60x45 | Tecnomat | Canalina bianca 60x45 per condizionatori | 2 m | 5,10 | non detta (presunta inclusa) | 4,18 | 2,09 | m | dalla pagina di categoria | [link](https://www.tecnomat.it/am/it/canaline-per-condizionatori) |
| 60x45 | Progetto Casa | Canalina PVC 60x45 Tecnosystemi | 2 m | 6,00 | inclusa | 4,92 | 2,46 | m |  | [link](https://www.progettocasastore.com/canaline-tecnosystemi/1226-canalina-in-pvc-60x45-mt-2-xxxx-p-3rip-8052967011812.html) |
| 60x45 | OBI | Canale condizionamento 60x45 avorio, art. 3353943 | 2 m | 4,95 | inclusa | 4,06 | 2,03 | m | avorio | [link](https://www.obi-italia.it/cavi-per-locali-umidi/canale-per-impianti-condizionamento-60x45-mm-avorio-2-m/p/3353943) |
| 60x45 | ElettroClimaShop | Canalsplit 1101-0106-01 60x45 avorio | 2 m | 7,90 | inclusa | 6,48 | 3,24 | m | avorio | [link](https://www.elettroclimashop.com/canalina-condizionatore-60x45cm-avorio-lunghezza-2metri-gia-canalsplit-1101-0106-01) |
| 60x45 | Paritec | Canalina clima 60x45 bianca | 2 m | 7,50 | non detta (presunta inclusa) | 6,15 | 3,07 | m |  | [link](https://www.paritec.it/it/canalina-clima-60x45-bianca-2-mt) |
| 60x45 | Leroy Merlin | Canale PVC condizionamento 60x45 (87497384) | 2 m | 15,65 | inclusa | 12,83 | 6,41 | m | fuori forbice | [link](https://www.leroymerlin.it/prodotti/canale-bianco-portacavi-pvc-condizionamento-60x45mm-barra-2-metri-87497384.html) |
| 80x60 | Tecnomat | Canale clima Olan 80x60 bianco (25067823) | 2 m | 6,30 | non detta (presunta inclusa) | 5,16 | 2,58 | m | prezzo di listino; scontato 5,16, altra ricerca 7,30 | [link](https://www.tecnomat.it/it/canale-clima-olan-80x60-2-m-bianco-25067823/) |
| 80x60 | OBI | Canalina condizionamento 80x60 bianco, art. 5656038 | 2 m | 8,39 | inclusa | 6,88 | 3,44 | m |  | [link](https://www.obi-italia.it/p/5656038/canalina-per-impianti-di-condizionamento-bianco-puro-80x60-mm) |
| 80x60 | Bricocenter | Canale clima a U 80x60 bianco (420004270) | 2 m | 8,40 | non detta (presunta inclusa) | 6,89 | 3,44 | m | non ritrovato al ricontrollo | [link](https://www.bricocenter.it/prodotti/default/420004270-canale-clima-a-u-80x60-mm-bianco.html) |
| 80x60 | Climamarket | Canalina GIA 80x60 bianca | 2 m | 8,35 | non detta (presunta inclusa) | 6,84 | 3,42 | m |  | [link](https://www.climamarket.it/products/canalina-gia-80x60mm-con-coperchio-bianca-da-2-mt) |
| 80x60 | DasIdrotecnica | Elettrocanali EC9008060 80x60 | 2 m | 10,41 | non detta (presunta inclusa) | 8,53 | 4,27 | m |  | [link](https://www.dasidrotecnica.com/vendita/canalina-condizionamento-80x60-2-metri) |

### F08 — Curve e raccordi della canalina copritubo

Famiglia: Frigorifero - linee.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 60x45 curva piana | Tecnogas | Curva piana ART-ECO 60x45 | 1 pz | 2,75 | esclusa | 2,75 | 2,75 | cad |  | [link](https://www.tecnogas.net/prodotto/curva-piana-4/) |
| 60x45 curva piana | ShopClima | Curva piana regolabile 0622PR | 1 pz | 4,00 | non detta (presunta inclusa) | 3,28 | 3,28 | cad |  | [link](https://www.shopclima.it/en/curva-piana-regolabile-per-canaline-installazione-climatizzatori-60x45-mm.html) |
| 60x45 curva piana | Arbo | Curva piana Nexto CSCP60 | 1 pz | 4,43 | esclusa | 4,43 | 4,43 | cad |  | [link](https://arbo.it/curva-piana-x-canal-60-x-45-nexto-cscp60/) |
| 60x45 angolo interno/esterno | Electrolight | Angolo interno 60x45 FAEG FG18111 | 1 pz | 1,79 | inclusa | 1,47 | 1,47 | cad |  | [link](https://www.electrolight.it/it/prod/angolo-interno-per-canalina-60-x-45-1816) |
| 60x45 angolo interno/esterno | Del Piano Elettrico | Angolo esterno 60x45 Elettrocanali EC9206045 | 1 pz | 2,68 | non detta (presunta inclusa) | 2,20 | 2,20 | cad |  | [link](https://www.delpianoelettrico.com/it/accessori-per-canale-portacavi-/3874-angolo-esterno-per-canale-climatizzatori-60x45-ec9206045-8053676579761.html) |
| 60x45 angolo interno/esterno | ShopClima | Angolo interno 0605AI 60x45 | 1 pz | 2,80 | non detta (presunta inclusa) | 2,30 | 2,30 | cad |  | [link](https://www.shopclima.it/it/angolo-interno-per-canaline-installazione-climatizzatori-60x45-mm.html) |
| 60x45 angolo interno/esterno | Bricofer | Angolo interno 60x45 | 1 pz | 2,20 | non detta (presunta inclusa) | 1,80 | 1,80 | cad |  | [link](https://www.bricofer.it/idraulica-riscaldamento-e-climatizzazione/angolo-interno-per-canale-condizionamento-dim-60x45-mm-9104693/) |
| 60x45 passaggio a muro | ShopClima | Passaggio a muro 60x45 | 1 pz | 3,10 | non detta (presunta inclusa) | 2,54 | 2,54 | cad |  | [link](https://www.shopclima.it/it/passaggio-a-muro-per-canaline-installazione-climatizzatori-60x45-mm.html) |
| 60x45 passaggio a muro | Del Piano Elettrico | Elettrocanali EC9706045 passaggio muro 60x45 | 1 pz | 2,24 | non detta (presunta inclusa) | 1,84 | 1,84 | cad | URL della versione 80x60 | [link](https://www.delpianoelettrico.com/it/accessori-per-canale-portacavi-/4146-passaggio-a-muro-terminale-curvo-canale-bianco-80x60-elettrocanali--8032793870333.html) |
| 60x45 tappo terminale | Electrolight | Tappo terminale 60x45 | 1 pz | 1,91 | inclusa | 1,57 | 1,57 | cad |  | [link](https://www.electrolight.it/it/prod/tappo-terminale-per-canalina-60-x-45-1813) |
| 60x45 tappo terminale | AM Termoidraulica | Tappo terminale 60x45 Groppalli | 1 pz | 2,34 | inclusa | 1,92 | 1,92 | cad |  | [link](https://www.am-termoidraulica.it/climatizzatori-e-accessori/accessori-climatizzazione-e-tubo-rame/tappo-terminale-per-canalina-60-x-45.1.53.91.gp.2602.uw) |
| 80x60 curva piana | ShopClima | Curva piana 0807CP 80x60 | 1 pz | 4,50 | non detta (presunta inclusa) | 3,69 | 3,69 | cad |  | [link](https://www.shopclima.it/en/curva-piana-per-canaline-installazione-climatizzatori-80x60-mm.html) |
| 80x60 curva piana | Tecno Frasca | Curva piana 80x60 | 1 pz | 4,27 | non detta (presunta inclusa) | 3,50 | 3,50 | cad |  | [link](https://www.tecnofrasca.it/curva-piana-per-canalina-climatizzatore-80x60.html) |
| 80x60 curva piana | Bestdigit | Vecamco curva piana 9805-115-08 80x60 | 10 pz | 21,99 | inclusa | 18,02 | 1,80 | cad |  | [link](https://bestdigit.it/en/products/vecamco-curva-piana-per-canalina-condizionatore-9805-115-08-80x60-mm-bianca-pvc-conf-10-pz) |
| 80x60 angolo interno/esterno | OBI | Angolo esterno 80x60, art. 5487095 | 1 pz | 3,95 | inclusa | 3,24 | 3,24 | cad |  | [link](https://www.obi-italia.it/p/5487095/angolo-esterno-per-canalina-80x60-cm) |
| 80x60 angolo interno/esterno | Eurotronic | Angolo esterno 80x60 GIA 0806AE.1 | 1 pz | 2,68 | inclusa | 2,20 | 2,20 | cad |  | [link](https://eurotronic.it/80x60-mm-mono-dual-split/10048-raccordo-angolo-esterno-per-canalina-80x60mm-1-pz.html) |
| 80x60 angolo interno/esterno | Cappadonna | Angolo interno 80x60 ARN NSI6080.3 | 1 pz | 3,04 | non detta (presunta inclusa) | 2,49 | 2,49 | cad |  | [link](https://shop.cappadonna.it/prodotto/angolo-interno-80x60mm-bianco-arn-nsi6080-3/) |
| 80x60 angolo interno/esterno | Emmeffeci | Angolo interno 80x60 Ferrari 100960 | 1 pz | 2,83 | non detta (presunta inclusa) | 2,32 | 2,32 | cad |  | [link](https://shop.emmeffeci.it/accessori-climatizzazione/784-angolo-interno-80x60-per-canlina-in-pvc-per-climatizzatori-climatizzatore-tecnogas-8058699000971.html) |
| 80x60 giunto | D'Alessandris | Giunto per canalina 80x60 | 1 pz | 2,20 | inclusa | 1,80 | 1,80 | cad | scontato | [link](https://www.dalessandris.it/giunto-per-canalina-80mm-x-60mm/) |
| 80x60 passaggio a muro | Tecnomat | Passaggio muro dritto per canale clima 80x60 | 1 pz | 2,20 | non detta (presunta inclusa) | 1,80 | 1,80 | cad | curvo 2,50; pagina di categoria | [link](https://www.tecnomat.it/it/c/riscaldamento-e-climatizzazione/condizionatori-ventilatori-e-deumidificatori/installazione-condizionatori/canaline-curve-e-altri-accessori-per-posa/) |
| 80x60 passaggio a muro | Elettrotecnica Meridionale | Passaggio a muro lineare 80x60 | 1 pz | 2,43 | inclusa | 1,99 | 1,99 | cad |  | [link](https://elettrotecnicameridionale.com/it/tubi-cavidotti-e-canaline/549-passaggio-a-muro-lineare-80x60-impianto-condizionamento.html) |
| 80x60 tappo terminale | LaTermoWeb | Tappo terminale 80x60 | 1 pz | 1,70 | inclusa | 1,39 | 1,39 | cad |  | [link](https://www.latermoweb.com/shop/condizionamento-e-accessori/561-tappo-terminale-per-canala-canalina-80x60-per-tubi-condizionatore.html) |
| 80x60 tappo terminale | ShopClima | Tappo terminale 80x60 | 1 pz | 3,20 | non detta (presunta inclusa) | 2,62 | 2,62 | cad |  | [link](https://www.shopclima.it/it/tappo-terminale-per-canaline-installazione-climatizzatori-80x60-mm.html) |

### F09 — Dadi a cartella e giunzioni per rame

Famiglia: Frigorifero - linee.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| dado a cartella 1/4" | HelloBagno | Dado ottone 1/4" Rinaldi e Pettinaroli | 1 pz | 0,60 | non detta (presunta inclusa) | 0,49 | 0,49 | cad |  | [link](https://www.hellobagno.it/clima/condizionamento/rame-per-refrigerazione-e-raccordi/dado-in-ottone/) |
| dado a cartella 1/4" | Edilgavis | Dado per giunto ottone 1/4" 9898061 | 1 pz | 0,70 | non detta (presunta inclusa) | 0,57 | 0,57 | cad |  | [link](https://www.edilgavis.it/2944-n-d-dado-per-giunto-ottone-1-4.html) |
| dado a cartella 1/4" | Gasfrigo | 10 dadi a cartella 1/4" SAE | 10 pz | 8,90 | inclusa | 7,30 | 0,73 | cad |  | [link](https://www.gasfrigo.it/95-raccorderia-e-minuteria) |
| dado a cartella 3/8" | Esuberi Idraulici | Dado ottone porta cartella 3/8 | 1 pz | 1,10 | non detta (presunta inclusa) | 0,90 | 0,90 | cad | rimanenze | [link](https://esuberi-idraulici.it/index.php?controller=category&id_category=29) |
| dado a cartella 3/8" | Gasfrigo | 10 bocchettoni 3/8" SAE (3311507) | 10 pz | 12,90 | inclusa | 10,57 | 1,06 | cad |  | [link](https://www.gasfrigo.it/raccorderia-e-minuteria/345-10-bocchettoni-ottone-3-8-sae-climatizzazione.html) |
| dado a cartella 1/2" | HelloBagno | Dado ottone 1/2" | 1 pz | 1,45 | non detta (presunta inclusa) | 1,19 | 1,19 | cad |  | [link](https://www.hellobagno.it/clima/condizionamento/rame-per-refrigerazione-e-raccordi/dado-in-ottone/) |
| dado a cartella 1/2" | Gasfrigo | 10 bocchettoni 1/2" SAE | 10 pz | 12,90 | inclusa | 10,57 | 1,06 | cad |  | [link](https://www.gasfrigo.it/raccorderia-e-minuteria/346-10-bocchettoni-ottone-1-2-sae-climatizzazione.html) |
| dado a cartella 5/8" | HelloBagno | Dado ottone 5/8" | 1 pz | 1,55 | non detta (presunta inclusa) | 1,27 | 1,27 | cad |  | [link](https://www.hellobagno.it/clima/condizionamento/rame-per-refrigerazione-e-raccordi/dado-in-ottone/) |
| dado a cartella 5/8" | Esuberi Idraulici | Dado ottone porta cartella 5/8 | 1 pz | 1,46 | non detta (presunta inclusa) | 1,20 | 1,20 | cad | rimanenze | [link](https://www.esuberi-idraulici.it/index.php?id_product=1007&controller=product) |
| giunto a doppia cartella 1/4" | Fornitura Idraulica | Giunto doppia cartella 1/4 | 1 pz | 0,85 | inclusa | 0,70 | 0,70 | cad | prezzo speciale | [link](https://www.fornituraidraulica.com/riscaldamento/climatizzazione/raccordi-per-condizionatori/giunto-doppia-cartella-14-condizionatori) |
| giunto a doppia cartella 1/4" | Ricambi Caldaie Roma | Raccordo doppio 1/4" SAE RCC001 | 1 pz | 1,30 | inclusa | 1,07 | 1,07 | cad |  | [link](https://ricambicaldaieroma.it/condizionamento/7735-raccordo-doppio-1-4-sae-maschio-rcc001.html) |
| giunto a doppia cartella 1/4" | Gasfrigo | 10 nipples doppia cartella 1/4" SAE | 10 pz | 13,90 | non detta (presunta inclusa) | 11,39 | 1,14 | cad |  | [link](https://www.gasfrigo.it/95-raccorderia-e-minuteria) |
| giunto a doppia cartella 3/8" | Caldaie Condizionatori | Giunto a doppia cartella 3/8 | 1 pz | 2,44 | inclusa | 2,00 | 2,00 | cad |  | [link](https://www.caldaiecondizionatori.com/shop/climatizzazione/4391-giunto-a-doppia-cartella-3-8-8033408050928.html) |
| giunto a doppia cartella 3/8" | Gasfrigo | 10 nipples doppia cartella 3/8" SAE | 10 pz | 18,90 | non detta (presunta inclusa) | 15,49 | 1,55 | cad |  | [link](https://www.gasfrigo.it/95-raccorderia-e-minuteria) |
| giunto a doppia cartella 1/2" | Gasfrigo | 10 nipples doppia cartella 1/2" SAE | 10 pz | 23,90 | non detta (presunta inclusa) | 19,59 | 1,96 | cad |  | [link](https://www.gasfrigo.it/95-raccorderia-e-minuteria) |
| giunto a doppia cartella 1/2" | Amazon.it | Giunto doppia cartella 1/2 | 1 pz | 2,90 | inclusa | 2,38 | 2,38 | cad | spedizione +5,50 € | [link](https://www.amazon.it/GIUNTO-DOPPIA-CARTELLA-1-2/dp/B08XY8VLMV) |
| giunto a doppia cartella 5/8" | Fornitura Idraulica | Giunto doppia cartella 5/8 | 1 pz | 4,37 | inclusa | 3,58 | 3,58 | cad | prezzo speciale | [link](https://www.fornituraidraulica.com/riscaldamento/climatizzazione/raccordi-per-condizionatori) |
| giunto a doppia cartella 5/8" | PromoClima | Wigam giunto doppia cartella 5/8" 05108012001 | 1 pz | 3,50 | non detta (presunta inclusa) | 2,87 | 2,87 | cad |  | [link](https://www.promoclima.it/wigam-giunto-a-doppia-cartella-5-8-codice-05108012001.html) |
| giunto a doppia cartella 5/8" | ePrice | Wigam giunto doppia cartella 5/8 | 1 pz | 6,92 | non detta (presunta inclusa) | 5,67 | 5,67 | cad |  | [link](https://www.eprice.it/raccordi-e-connettori-WIGAM/d-51496296) |
| manicotto a brasare 1/4" | Arbo | Manicotto rame a saldare FF 1/4 Banninger | 1 pz | 1,23 | esclusa | 1,23 | 1,23 | cad |  | [link](https://arbo.it/manicotto-rame-saldare-ff-d-1-4-9600002000000/) |
| manicotto a brasare 1/4" | Termoidraulica Ingrosso Roma | Manicotto rame frigo 1/4 BRL | 1 pz | 0,34 | inclusa | 0,28 | 0,28 | cad |  | [link](https://www.termoidraulicaingrossoroma.it/Raccorderie-Bronzo-Rame/8921-MANICOTTO-RAME-PER-SALDAT.html) |
| manicotto a brasare 3/8" | Arbo | Manicotto rame a saldare FF 3/8 | 1 pz | 2,69 | non detta (presunta inclusa) | 2,20 | 2,20 | cad |  | [link](https://arbo.it/manicotto-rame-saldare-ff-d-3-8-9600003000000/) |

### A01 — Tubo flessibile isolato per aria, rotolo 10 m

Famiglia: Aeraulica - canali.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| Ø125 | Sterr | Tubo alluminio coibentato IAL125_10, isolante 25 mm | 10 m | 39,58 | non detta (presunta inclusa) | 32,44 | 3,24 | m | scontato | [link](https://sterr.it/products/tubo-flessibile-in-alluminio-coibentato-10-m-x-125-mm-5-ial125_10) |
| Ø125 | Idrotop | Tubo flessibile Ø127 doppia parete coibentato, fibra di vetro 25 mm | 10 m | 82,29 | inclusa | 67,45 | 6,75 | m | Ø127; promozione | [link](https://www.idrotop.com/ventilazione/tubi-flessibili-ventilazione/tubo-flessibile-diam-127-in-alluminio-a-doppia-parete-tubo-flex-10-mt/) |
| Ø125 | Idrovip | Tecnosystemi tubo flessibile termico-fonico Ø127 doppia parete | 10 m | 63,00 | non detta (presunta inclusa) | 51,64 | 5,16 | m | Ø127; pagina di categoria | [link](https://idrovip.it/categoria-prodotto/trattamento-aria/plenum-tubi-flessibili-ed-accessori-per-canalizzati) |
| Ø125 | Tavolla | Irsap TFI-AFO DN125 isolato afonico (DPLTUB012501C0) | 10 m | 137,88 | inclusa | 113,02 | 11,30 | m | afonico, fascia alta | [link](https://www.tavolla.com/irsap-dpltub012501c0-tfi-afo-tubo-flessibile-isolato-afonico-dn125-rotolo-da-10-m-/) |
| Ø160 | Brunori | Tubo alluminio isolato lana di vetro DN160 | 10 m | 92,80 | non detta (presunta inclusa) | 76,07 | 7,61 | m |  | [link](https://www.brunorigroup.com/distribuzione-aria/tubazioni-flessibili/2504-tubo-flessibile-alluminio-isolato-lana-di-vetro-classe-0-vmc-10-metri-dn-160-detail.html) |
| Ø160 | Idrotop | Tubo flessibile Ø160 doppia parete coibentato | 10 m | 94,13 | inclusa | 77,16 | 7,72 | m | promozione | [link](https://www.idrotop.com/ventilazione/tubi-flessibili-ventilazione/tubo-flessibile-diam-160-in-alluminio-a-doppia-parete-tubo-flex-10-mt/) |
| Ø160 | Ventilclima | Tubo alluminio doppia parete coibentato Ø160 | 10 m | 62,15 | non detta (presunta inclusa) | 50,94 | 5,09 | m | promozione; pagina di categoria | [link](https://www.ventilclima.it/29-tubi-flessibili) |
| Ø160 | Grecifer | Tubo aria coibentato alluminio Ø160 Vecam-Co, fibra di vetro 25 mm | 10 m | 86,10 | non detta (presunta inclusa) | 70,57 | 7,06 | m |  | [link](http://www.grecifer.it/portale/catalog/ENG/articolo/2052-termoidraulica/yfqqywsrtk-tubo-aria-coibentato-allummm160-mt10.html) |
| Ø200 | Sterr | Tubo alluminio coibentato IAL200_10, isolante 25 mm | 10 m | 54,45 | non detta (presunta inclusa) | 44,63 | 4,46 | m | scontato | [link](https://sterr.it/products/tubo-flessibile-in-alluminio-coibentato-10-m-x-200-mm-8-ial200_10) |
| Ø200 | Idrotop | Tubo flessibile Ø204 doppia parete coibentato | 10 m | 112,24 | inclusa | 92,00 | 9,20 | m | Ø204; promozione | [link](https://www.idrotop.com/ventilazione/tubi-flessibili-ventilazione/tubo-flessibile-in-alluminio-a-doppia-parete-tubo-flex-diam-204-10-m-/) |
| Ø200 | Brunori | Tubo alluminio isolato lana di vetro DN203 | 10 m | 107,90 | non detta (presunta inclusa) | 88,44 | 8,84 | m | Ø203; pagina elenco | [link](https://www.brunorigroup.com/distribuzione-aria/tubazioni-flessibili) |

### A03 — Canale spiroidale zincato e raccordi

Famiglia: Aeraulica - canali.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| spiroidale Ø125 | Steam Condotte | Tubazione spiroidale zincata sp. 5/10 Ø125 | 3 m | 34,26 | non detta (presunta inclusa) | 28,08 | 9,36 | m |  | [link](https://www.steamcondotte.it/prodotti/tubazione-spiroidale-acciaio-zincato-spessore-diametro-lunghezza-3000-5980) |
| spiroidale Ø160 | Steam Condotte | Tubazione spiroidale zincata sp. 5/10 Ø160 | 3 m | 43,83 | non detta (presunta inclusa) | 35,93 | 11,98 | m |  | [link](https://www.steamcondotte.it/prodotti/tubazione-spiroidale-acciaio-zincato-spessore-diametro-lunghezza-3000-7337) |
| spiroidale Ø160 | Amazon.it | Tubo ventilazione acciaio zincato Ø160 K-TECH-PRO | 1 m | 12,25 | inclusa | 10,04 | 10,04 | m |  | [link](https://www.amazon.it/Tubo-ventilazione-acciaio-zincato-lunghezza/dp/B07V6KYTDL) |
| spiroidale Ø200 | Siderea | Tubo spiro Ø200 (17100705) | 1 m | 12,29 | esclusa | 12,29 | 12,29 | m | trasporto da 12 € + IVA | [link](https://www.sidereasrl2002.com/it/home-page/17-aria-canalizzazioni/171-canalizzazioni-in-lamiera-zincata-e-accessori/tubazioni-spiroidali-e-accessori/tubo-spiro-diam-mm-200.1.1.165.gp.3957.uw) |
| spiroidale Ø200 | Tavolla | Irsap TLZ condotto spiroidale DN200 (DLZTUB02000300) | 3 m | 58,50 | inclusa | 47,95 | 15,98 | m |  | [link](https://www.tavolla.com/irsap-dlztub02000300-tlz-condotto-circolare-spiroidale-in-lamiera-zincata-dn200-lunghezza-3-m/) |
| spiroidale Ø200 | Ventigo | Tubo spiro Ø200 zincato 0,5 mm (75010200) | 1,5 m | 24,22 | non detta (presunta inclusa) | 19,85 | 13,23 | m |  | [link](https://www.ventigo.it/it_IT/p/tubo-spiro-o-200-mm-lunghezza-15-metri-zincato/1966/) |
| curva 90° Ø125 | Soluzione Aria | Curva stampata 90° EPDM S0290125 | 1 pz | 8,85 | non detta (presunta inclusa) | 7,25 | 7,25 | cad |  | [link](https://www.soluzionearia.shop/it/prodotti/canali-spiroidali/00f032-1/72/curva-stampata-a-90-.html) |
| curva 90° Ø125 | Ventigo | Curva spiro 90° Ø125 (75060004) | 1 pz | 9,24 | non detta (presunta inclusa) | 7,57 | 7,57 | cad |  | [link](https://www.ventigo.it/it_IT/p/curva-tonda-spiro-90deg-o-160-mm-per-tubo-spiro/7143/) |
| curva 90° Ø160 | Soluzione Aria | Curva stampata 90° EPDM S0290160 | 1 pz | 13,42 | non detta (presunta inclusa) | 11,00 | 11,00 | cad |  | [link](https://www.soluzionearia.shop/it/prodotti/canali-spiroidali/00f032-1/72/curva-stampata-a-90-.html) |
| curva 90° Ø160 | Ventigo | Curva spiro 90° Ø160 (75060007) | 1 pz | 13,33 | non detta (presunta inclusa) | 10,93 | 10,93 | cad |  | [link](https://www.ventigo.it/it_IT/p/curva-tonda-spiro-90deg-o-160-mm-per-tubo-spiro/7143/) |
| curva 90° Ø200 | Soluzione Aria | Curva stampata 90° EPDM S0290200 | 1 pz | 18,62 | non detta (presunta inclusa) | 15,26 | 15,26 | cad |  | [link](https://www.soluzionearia.shop/it/prodotti/canali-spiroidali/00f032-1/72/curva-stampata-a-90-.html) |
| curva 90° Ø200 | Ventigo | Curva spiro 90° Ø200 (75060009) | 1 pz | 18,34 | non detta (presunta inclusa) | 15,03 | 15,03 | cad |  | [link](https://www.ventigo.it/it_IT/p/curva-tonda-spiro-90deg-o-160-mm-per-tubo-spiro/7143/) |
| tee 90° Ø160 | Ventigo | Raccordo a T Ø160-Ø160 90° (75120011) | 1 pz | 20,57 | non detta (presunta inclusa) | 16,86 | 16,86 | cad |  | [link](https://www.ventigo.it/it_IT/p/raccordo-a-t-o-160-mm-o-160-mm-per-tubo-spiro-90deg/7205/) |
| riduzione 160/125 | Ventigo | Riduttore Econox Ø160/Ø125 (75090013) | 1 pz | 7,60 | non detta (presunta inclusa) | 6,23 | 6,23 | cad |  | [link](https://www.ventigo.it/it_IT/p/riduttore-da-o-160-mm-o-125-mm-per-tubo-spiro/7665/) |
| riduzione 160/125 | Ecoclima | RC riduzione concentrica 160/125 | 1 pz | 11,41 | non detta (presunta inclusa) | 9,35 | 9,35 | cad | listino poco leggibile | [link](https://www.ecoclima.com/catalogo-generale/tubo-spiro-e-raccordi~558/raccordi~559/rc-riduzioni-concentriche~583.html) |
| riduzione 200/160 | Ventigo | Riduttore Econox Ø200/Ø160 (75090016) | 1 pz | 9,80 | non detta (presunta inclusa) | 8,03 | 8,03 | cad |  | [link](https://www.ventigo.it/it_IT/p/riduttore-da-o-200-mm-o-160-mm-per-tubo-spiro/7254/) |
| riduzione 200/160 | Brunori | Riduzione acciaio zincato DN200/160 | 1 pz | 11,60 | non detta (presunta inclusa) | 9,51 | 9,51 | cad |  | [link](https://www.brunorigroup.com/distribuzione-aria/riduzioni-eccentriche/1364-riduzione-eccentrica-acciaio-zincato-dn-200-160-detail) |

### A04 — Bocchetta di mandata a doppio filare di alette

Famiglia: Aeraulica - terminali.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 300x100 | Climacal | Bocchetta mandata alluminio doppio filare 300x100 DAV300X100 | 1 pz | 23,00 | non detta (presunta inclusa) | 18,85 | 18,85 | cad | bianca 25,00 | [link](https://climacal.it/products/bocchetta-di-mandata-in-alluminio-300-x-100-mm) |
| 300x100 | Idrotop | Bocchetta alluminio alette orientabili 300x100 | 1 pz | 14,76 | non detta (presunta inclusa) | 12,10 | 12,10 | cad | promozione | [link](https://www.idrotop.com/ventilazione/griglie-di-mandata/bocchette-griglie-300x100mm-in-alluminio-con-alette-orientabili/) |
| 300x100 | Ingrossoclima | Bocchetta mandata alluminio + serranda 300x100 BO111030 | 1 pz | 39,00 | non detta (presunta inclusa) | 31,97 | 31,97 | cad | con serranda | [link](https://www.ingrossoclima.it/prid_BO111030.html) |
| 400x150 | Climacal | Bocchetta mandata alluminio doppio filare 400x150 DAV400X150 | 1 pz | 29,00 | non detta (presunta inclusa) | 23,77 | 23,77 | cad | non ritrovata al ricontrollo | [link](https://climacal.it/products/bocchetta-di-mandata-in-alluminio-400-x-150-mm) |
| 400x150 | Steam Condotte | Bocchetta mandata alluminio doppio filare 400x150 BMM400150 | 1 pz | 30,06 | non detta (presunta inclusa) | 24,64 | 24,64 | cad |  | [link](https://www.steamcondotte.it/prodotti/bocchetta-mandata-alluminio-doppio-filare-dimensione-400x150-fissaggio-clips-8964) |
| 400x150 | Idrotop | Bocchetta alluminio doppio filare 400x150 | 1 pz | 29,89 | non detta (presunta inclusa) | 24,50 | 24,50 | cad |  | [link](https://www.idrotop.com/ventilazione/griglie-di-mandata/bocchette-griglie-400x150mm-in-alluminio-con-alette-orientabili-singolarmente/) |
| 400x150 | Ingrossoclima | Bocchetta mandata alluminio + serranda 400x150 BO111540 | 1 pz | 53,00 | non detta (presunta inclusa) | 43,44 | 43,44 | cad | con serranda | [link](https://www.ingrossoclima.it/prid_BO111540.html) |

### A05 — Griglia di ripresa con filtro

Famiglia: Aeraulica - terminali.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 400x200 | Comid | Griglia di ripresa con filtro 400x200 | 1 pz | 65,20 | inclusa | 53,44 | 53,44 | cad |  | [link](https://www.comid.it/it/griglie/22372-griglia-di-ripresa-400x200-con-filtro.html) |
| 400x200 | Brunori | Griglia ripresa alluminio portafiltro 400x200 Europair, G3 | 1 pz | 93,60 | inclusa | 76,72 | 76,72 | cad |  | [link](https://www.brunorigroup.com/diffusione-aria/67-griglie-bianche/1121-griglia-ripresa-aria-calda-fredda-alluminio-portafiltro-400x200-bianca-detail.html) |
| 400x200 | Climadiscount | Griglia ripresa portafiltro Europair 400x200 naturale | 1 pz | 49,18 | non detta (presunta inclusa) | 40,31 | 40,31 | cad | RAL 9016 53,28 | [link](https://www.climadiscount.it/categoria-prodotto/impianti-canalizzati/griglia-di-ripresa-portafiltro/) |
| 400x200 | Etaweb | France Air GL20ZFR42 griglia portafiltro 400x200 | 1 pz | 41,60 | inclusa | 34,10 | 34,10 | cad | non disponibile | [link](https://etaweb.eu/accessori/3683-griglia-di-ripresa-porta-filtro-alluminio-gl20zfr-france-air-400x200-2111525836833.html) |
| 600x300 | Steam Condotte | Bocchetta ripresa con filtro 600x300 BRMF600300 | 1 pz | 74,25 | non detta (presunta inclusa) | 60,86 | 60,86 | cad |  | [link](https://www.steamcondotte.it/prodotti/bocchetta-ripresa-allsingolofilare-con-filtro-600x300-mm-BRMF600300-1070) |
| 600x300 | Climadiscount | Griglia ripresa portafiltro Europair 600x300 | 1 pz | 59,02 | non detta (presunta inclusa) | 48,38 | 48,38 | cad | altra scheda 42,00 | [link](https://www.climadiscount.it/prodotto/griglia-di-ripresa-in-alluminio-600x300/) |
| 600x300 | ManoMano | Griglia ripresa portafiltro alette fisse 600x300 | 1 pz | 97,76 | non detta (presunta inclusa) | 80,13 | 80,13 | cad |  | [link](https://www.manomano.it/p/griglia-di-ripresa-portafiltro-ad-alette-fisse-all-anodizzato-mm-600-x-300-53990926) |

### A06 — Plenum porta-bocchetta

Famiglia: Aeraulica - terminali.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 300x100 | Steam Condotte | Plenum porta-bocchetta zincato 300x100 PPB300100 | 1 pz | 23,16 | non detta (presunta inclusa) | 18,98 | 18,98 | cad | attacco non detto; non isolato | [link](https://www.steamcondotte.it/ecommerce-prodotti/componenti-aeraulici/24) |
| 300x100 | Energyduegi | Plenum 300x100 isolato esternamente, attacco posteriore | 1 pz | 30,40 | inclusa | 24,92 | 24,92 | cad | attacco Ø100 | [link](https://www.energyduegi.com/accessori-per-canalizzato/1982-plenum-per-griglia-in-lamiera-per-bocchette-di-mandata-con-isolamento-esternoattacco-posteriore-dimensioni-300x100-mm.html) |
| 300x100 | iClima Roma | Plenum porta bocchetta 300x100 att. Ø100 VEP3010 | 1 pz | 22,63 | inclusa | 18,55 | 18,55 | cad | attacco Ø100; altra pagina 32,03 | [link](https://www.iclimaroma.it/it/home-page/aeraulica/plenum/plenum-porta-bocchette/products.1.34.203.sp.uw) |
| 300x100 | Idrotop | Plenum 300x100 att. Ø100 zincato | 1 pz | 40,25 | non detta (presunta inclusa) | 32,99 | 32,99 | cad | attacco Ø100; promozione | [link](https://www.idrotop.com/ventilazione/plenum-per-griglie/plenum-per-bocchette-300x100mm-d100-x-nova-a-in-lamiera-zincata-/) |
| 400x150 | Steam Condotte | Plenum porta-bocchetta rivestito 400x150 PPBI400150 | 1 pz | 38,43 | non detta (presunta inclusa) | 31,50 | 31,50 | cad | attacco non detto | [link](https://www.steamcondotte.it/prodotti/plenum-porta-bocchetta-acciaio-zincato-rivestito-dimensione-400x150-3202) |
| 400x150 | Termoidraulica Ingrosso Roma | Plenum Ecoclima 400x150 uscita 160 | 1 pz | 36,88 | non detta (presunta inclusa) | 30,23 | 30,23 | cad | attacco Ø160 dal nome | [link](https://www.termoidraulicaingrossoroma.it/Accessori-Condizionamento/13815-PLENUM-X-BOCCHETTA-DI-MANDATA-X-CANALIZZATO-400-X-150-US-160-H-25.html) |
| 400x150 | iClima Roma | Plenum porta bocchetta 400x150 att. Ø150 | 1 pz | 34,16 | inclusa | 28,00 | 28,00 | cad | attacco Ø150 | [link](https://www.iclimaroma.it/it/home-page/aeraulica/plenum-/plenum-porta-bocchette/plenum-porta-bocchetta-400-x-150-att-d-150-altezza-10cm.1.34.203.gp.3227.uw) |
| 400x150 | Energyduegi | Plenum 400x150 isolato esternamente | 1 pz | 38,00 | inclusa | 31,15 | 31,15 | cad | attacco Ø100 | [link](https://www.energyduegi.com/accessori-per-canalizzato/1985-plenum-per-griglia-in-lamiera-per-bocchette-di-mandata-con-isolamento-esternoattacco-posteriore-dimensioni-400x150-mm.html) |

### A08 — Pendini e sospensioni

Famiglia: Aeraulica - accessori.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| barra filettata M8 1 m | Leroy Merlin | Barra filettata Suki M8 1000 mm zincata | 1 pz | 1,30 | inclusa | 1,07 | 1,07 | cad | in listino c'è già I64 Tecnomat | [link](https://www.leroymerlin.it/prodotti/barra-filettata-suki-in-acciaio-m8-l-1000-mm-35736862.html) |
| barra filettata M8 1 m | Wovar | Barra filettata zincata M8 1 m DIN 975 4.8 | 1 pz | 1,39 | inclusa | 1,14 | 1,14 | cad |  | [link](https://www.wovar.it/barra-filettata-zincata-m8-x-1m-4-8/) |
| sospensione a cavetto 3 m | RS Components | Gripple HF01-3M kit sospensione 3 m | 10 pz | 76,83 | esclusa | 76,83 | 7,68 | cad |  | [link](https://it.rs-online.com/web/p/corde/4915029) |
| sospensione a cavetto 3 m | RS Components | Gripple HF02-3M kit sospensione 3 m, 45 kg | 10 pz | 93,90 | esclusa | 93,90 | 9,39 | cad |  | [link](https://it.rs-online.com/web/p/corde/4915057) |

### E02 — Cavo FG16OR16 0,6/1 kV 3G4

Famiglia: Elettrico - cavi.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 3G4 | Stock Elettrico | Cavo FG16OR16 3G4 CPR, al metro | 1 m | 2,84 | inclusa | 2,33 | 2,33 | m |  | [link](https://www.stockelettrico.it/products/15518-Cavo-Elettrico-FG16OR16-3G4-Cavo-CPR-FG16OR16-3G4mm2-con-gialloverde-AL-METRO/) |
| 3G4 | Emmebistore | Cavo FG16OR16 3G4 grigio, al metro | 1 m | 2,76 | inclusa | 2,26 | 2,26 | m |  | [link](https://www.emmebistore.com/cavi-elettrici-fg16or-fg16om-e-ftg18/cavo-fg16or16-3g4-mmq-guaina-grigia-con-giallo-verde-13368.html) |
| 3G4 | Elettroonline | Cavo FG16OR16 3G4, matassa 100 m | 100 m | 298,00 | inclusa | 244,26 | 2,44 | m | 2,98 €/m | [link](https://www.elettroonline.it/prodotto/cavo-multipolare-cavo-energia-fg16or16-06-1kv-3g4mm%C2%B2-matassa-da-100m/) |
| 3G4 | OBI | Cavo FG16OR16 3G4 grigio, art. 5834098 | 100 m | 229,00 | inclusa | 187,70 | 1,88 | m |  | [link](https://www.obi-italia.it/p/5834098/cavo-unipolare-in-hepr-fg16or16-3g4-da-100-m-grigio) |
| 3G4 | OBI | Cavo FG16OR16 3G4 grigio, art. 5854658 | 50 m | 139,00 | inclusa | 113,93 | 2,28 | m | non disponibile | [link](https://www.obi-italia.it/p/5854658/cavo-fg16or16-3g4-da-50-m-grigio) |

### E03 — Cavo FG16OR16 0,6/1 kV 3G6

Famiglia: Elettrico - cavi.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 3G6 | Leroy Merlin | Cavo FG16OR16 3x6 Electraline, vendita al metro (ref. 93831910) | 1 m | 5,40 | inclusa | 4,43 | 4,43 | m | un'altra scheda dice 6,00 | [link](https://www.leroymerlin.it/prodotti/cavo-elettrico-flessibile-fg16or16-3-x-6-mm2-l-60-m-electraline-grigio-vendita-al-metro-93831910.html) |
| 3G6 | Stock Elettrico | Cavo FG16OR16 3G6 CPR, al metro | 1 m | 4,14 | inclusa | 3,39 | 3,39 | m |  | [link](https://www.stockelettrico.it/products/15519-Cavo-Elettrico-FG16OR16-3G6-Cavo-CPR-FG16OR16-3G6mm2-con-giallo-verde-AL-METRO/) |
| 3G6 | Emmebistore | Cavo FG16OR16 3G6 grigio, al metro | 1 m | 3,96 | inclusa | 3,25 | 3,25 | m |  | [link](https://www.emmebistore.com/cavi-elettrici-fg16or-fg16om-e-ftg18/cavo-fg16or16-3g6-mmq-guaina-grigia-con-giallo-verde-13370.html) |
| 3G6 | Sovatem | Cavo FG16OR16 3G6 Garofoli, al metro | 1 m | 3,77 | inclusa | 3,09 | 3,09 | m | taglio +2,50 € | [link](https://www.sovatem.it/negozio/impiantistica/cavi-e-filo-unipolare/cavo-multipolare-fg16or16-3g6-mmq-conduttori-flessibili-grigio/) |
| 3G6 | OBI | Cavo FG16OR16 3G6 grigio, art. 5854609 | 50 m | 179,00 | inclusa | 146,72 | 2,93 | m | non disponibile | [link](https://www.obi-italia.it/p/5854609/cavo-fg16or16-3g6-da-50-m-grigio) |
| 3G6 | RS Components | Prysmian FG16OR16 3G6, bobina 50 m (RS 216-1681) | 50 m | 260,74 | esclusa | 260,74 | 5,21 | m | ricontrollato dalla sessione | [link](https://it.rs-online.com/web/p/cavi-di-potenza/2161681) |

### E05 — Cavo FG16OR16 0,6/1 kV 5G4

Famiglia: Elettrico - cavi.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| 5G4 | Elettroonline | Cavo FG16OR16 5G4, matassa 100 m | 100 m | 467,00 | inclusa | 382,79 | 3,83 | m | 4,67 €/m | [link](https://www.elettroonline.it/prodotto/cavo-multipolare-cavo-energia-fg16or16-06-1kv-5g4mm%C2%B2-matassa-da-100m/) |
| 5G4 | Stock Elettrico | Cavo FG16OR16 5G4 CPR, al metro | 1 m | 4,60 | inclusa | 3,77 | 3,77 | m |  | [link](https://www.stockelettrico.it/products/15534-Cavo-Elettrico-FG16OR16-5G4-Cavo-CPR-FG16OR16-5G4mm2-con-giallo-verde-AL-METRO/) |
| 5G4 | Emmebistore | Cavo FG16OR16 5G4 grigio, al metro | 1 m | 4,38 | inclusa | 3,59 | 3,59 | m |  | [link](https://www.emmebistore.com/cavi-elettrici-fg16or-fg16om-e-ftg18/cavo-fg16or16-5g4-mmq-guaina-grigia-con-giallo-verde-13383.html) |
| 5G4 | Sovatem | Cavo FG16OR16 5G4 Garofoli, al metro | 1 m | 4,22 | inclusa | 3,46 | 3,46 | m | taglio +2,50 € | [link](https://www.sovatem.it/negozio/impiantistica/cavi-e-filo-unipolare/cavo-multipolare-fg16or16-5g4-mmq-conduttori-flessibili-grigio/) |
| 5G4 | Elettronew | Cavo FG16OR16 5G4 (FG16R5G4M), minimo 100 m | 1 m | 4,70 | inclusa | 3,85 | 3,85 | m |  | [link](https://www.elettronew.com/en/fg16or-unipolar-and-multipolar-double-insulation-cables/fg16or16-double-insulated-flameproof-cable-5g-4mmq-yellow-green-fg16r5g4m-42418.html) |

### E29 — Fascette, collari e graffette per cavi

Famiglia: Elettrico - accessori.

| Misura | Negozio | Articolo | Confezione | Prezzo mostrato € | IVA | Netto conf. € | Netto/UM € | UM | Note | Fonte |
|---|---|---|---|--:|---|--:|--:|---|---|---|
| fascette 4,8x300 nere | Leroy Merlin | Fascetta 11GDB3048 300x4,8 (ref. 35442505) | 100 pz | 3,65 | inclusa | 2,99 | 0,030 | cad | colore e UV non detti | [link](https://www.leroymerlin.it/catalogo/fascetta-a-collare-11gdb3048-300-x-4.8-mm-100-pezzi-35442505-p) |
| fascette 4,8x300 nere | Cfadda | Fascette nere 4,8x300 | 100 pz | 5,49 | inclusa | 4,50 | 0,045 | cad |  | [link](https://www.cfadda.com/prodotti/elettricita/cavi-canalette-e-corrugati/morsetti-fascette-e-nastri-isolanti/fascette-nere-4-8-x-300-mm-C001012099) |
| fascette 4,8x300 nere | Faritaly Shop | 100 fascette nere nylon 4,8x300 | 100 pz | 3,80 | esclusa | 3,80 | 0,038 | cad |  | [link](https://www.faritalyshop.com/palificazione/581-100-fascette-nere-nylon-48-x-300-mm-colore-nero.html) |
| fascette 4,8x300 nere UV | RS Components | RS PRO fascette nylon UV 300x4,8 nere (RS 656-044) | 100 pz | 9,95 | esclusa | 9,95 | 0,099 | cad | resistenti UV | [link](https://it.rs-online.com/web/p/fascette/0656044) |
| fascette 4,8x350 nere | Tecnomat | Fascette Tecnoline 350x4,8 nere (25066364) | 100 pz | 4,90 | inclusa | 4,02 | 0,040 | cad | 350 mm, non 300 | [link](https://www.tecnomat.it/it/m-100-fascette-suprema-350x4-8mm-pvc-nro-25066364/) |
| collare fissatubo Ø20 | Voltair | Collare fissatubo Ø20 ECCFC20 | 100 pz | 11,34 | inclusa | 9,30 | 0,093 | cad |  | [link](https://www.voltair.it/it/clips-fissatubo-a-collare-dim-20-21954.html) |
| collare fissatubo Ø20 | D'Alessandris | Gewiss clip a collare Ø20 GW50602 | 1 pz | 0,19 | inclusa | 0,16 | 0,16 | cad | scontato 40% | [link](https://www.dalessandris.it/gewiss-clip-collare-per-tubo-da-20-mm-gw50602/) |
| collare fissatubo Ø25 | Voltair | Collare fissatubo Ø25 Elettrocanali ECCFC25 | 100 pz | 12,97 | inclusa | 10,63 | 0,11 | cad | scontato | [link](https://www.voltair.it/it/clips-fissatubo-a-collare-dim-25-29116.html) |
| collare fissatubo Ø25 | Stock Elettrico | PM CFC25G clip a collare Ø25 | 1 pz | 0,20 | inclusa | 0,16 | 0,16 | cad |  | [link](https://www.stockelettrico.it/products/3799-PM-CFC25G-Clips-fissatubo-a-collare-per-tubo-diametro-25-mm/) |
| clip a scatto Ø25 | Tecnomat | 100 clips fissatubo Sartel a scatto Ø25 (25077159) | 100 pz | 12,40 | inclusa | 10,16 | 0,10 | cad | a scatto, non a collare | [link](https://www.tecnomat.it/it/clips-fissatubo-a-scatto-o25-100-pezzi-25077159/) |
| clip a scatto Ø25 | Comcavi | Elettrocanali ECCF25 clip a scatto Ø25 | 100 pz | 8,38 | inclusa | 6,87 | 0,069 | cad |  | [link](https://www.comcavi.shop/prodotto/elettrocanali-eccf25-clip-fissatubo-a-scatto-d25-100pz/) |
| graffetta a chiodo 12-14 mm | J69 Store | Graffette fermacavo con chiodo 14 mm | 100 pz | 2,49 | inclusa | 2,04 | 0,020 | cad | spedizione +5,50 € | [link](https://www.j69store.com/graffette-ferma-fissa-passa-cavo-14-mm-confezione-da-100-pezzi) |
| graffetta a chiodo 12-14 mm | Amazon.it | Graffette con chiodo 14 mm | 100 pz | 6,90 | inclusa | 5,66 | 0,057 | cad |  | [link](https://www.amazon.it/GRAFFETTE-CHIODI-FERMA-FISSA-CONFEZIONE/dp/B06ZYGCX45) |

## 2bis. Il riferimento online — 6 novembre 2026

Le voci che la distinta conta e che il listino non aveva, trovate dopo i collaudi della 1.14.0. Come nel §2: i prezzi
vengono dai riassunti del motore di ricerca, netti IVA esclusa (IVA presunta inclusa dove il negozio non la dice),
con il link di ogni riscontro; il riferimento è la mediana. I siti con protezione anti-robot (Tecnomat, Leroy Merlin,
ManoMano, RS) non si aprono dalla sessione: i loro prezzi qui sono quelli che il motore di ricerca riporta.

- **Interruttore tipo B.** Il combinato tipo B economico (E31a) sta sui 85–90 €; il differenziale puro tipo B di
  marca (E31b) sui 270–390 €, da abbinare a un magnetotermico (E32). Il «B» di molti titoli è la **curva**, non il tipo
  del differenziale: non vale per la pompa di calore.
- **Valvola antigelo.** La Caleffi 108 da 1" sta sui 75–85 €; equivalenti Giacomini, BRV o ICMA sui 37–66 €.

### Riepilogo (6 novembre 2026)

| Codice | ID | Voce | Misura | Riscontri | Netto/UM min € | Mediana € | Max € | UM |
|---|---|---|---|--:|--:|--:|--:|---|
| I73a | I73 | Valvola antigelo per pompa di calore | 1" | 5 | 62,30 | 77,38 | 84,21 | cad |
| I73b | I73 | Valvola antigelo per pompa di calore | 1¼" | 4 | 54,92 | 86,95 | 114,66 | cad |
| I74 | I74 | Gruppo di sicurezza sanitario per bollitore | ¾" | 4 | 25,09 | 44,63 | 49,35 | cad |
| I75 | I75 | Valvola a sfera FF a passaggio totale | ½" | 4 | 3,24 | 5,80 | 8,84 | cad |
| I76 | I76 | Pozzetto portasonda in ottone | ½" | 4 | 4,92 | 12,66 | 14,66 | cad |
| I77 | I77 | Rubinetto portamanometro a tre vie | ½" | 2 | 14,35 | 17,93 | 21,50 | cad |
| I78a | I78 | Riduzione filettata in ottone M × F | 1¼" × 1" | 2 | 2,30 | 2,64 | 2,98 | cad |
| I78b | I78 | Riduzione filettata in ottone M × F | 1" × ¾" | 2 | 1,52 | 3,41 | 5,30 | cad |
| I79 | I79 | Circolatore per ricircolo sanitario | Rp ½" | 6 | 85,40 | 133,35 | 138,75 | cad |
| I80a | I80 | Valvola miscelatrice a tre vie con servomotore 230 V | ¾" | 2 | 176,24 | 180,17 | 184,10 | cad |
| I80b | I80 | Valvola miscelatrice a tre vie con servomotore 230 V | 1" | 3 | 179,04 | 181,00 | 223,39 | cad |
| I41e | I41 | Vaso di espansione per riscaldamento | 35 l | 6 | 53,63 | 68,85 | 89,46 | cad |
| I41f | I41 | Vaso di espansione per riscaldamento | 50 l | 3 | 80,33 | 89,34 | 90,57 | cad |
| I81a | I81 | Gomito a pressare multistrato | 16×2 | 2 | 3,25 | 3,47 | 3,69 | cad |
| I81b | I81 | Manicotto a pressare multistrato | 16×2 | 3 | 2,38 | 2,45 | 2,85 | cad |
| I81c | I81 | Raccordo diritto a pressare M × multistrato | ½" × 16 | 3 | 2,67 | 6,65 | 11,39 | cad |
| I82 | I82 | Guaina elastomerica sp. 32 mm | tubo Ø35 | 3 | 7,20 | 7,85 | 7,85 | m |
| E31a | E31 | Interruttore magnetotermico differenziale tipo B, 1P+N 30 mA | C16–C32 | 2 | 85,30 | 87,73 | 90,16 | cad |
| E31b | E31 | Differenziale puro tipo B 2P 30 mA (da abbinare a un magnetotermico) | 25–40 A | 4 | 271,67 | 302,64 | 390,66 | cad |
| E32 | E32 | Interruttore magnetotermico 1P+N 4,5 kA | C20–C32 | 6 | 5,48 | 6,39 | 7,30 | cad |
| E33 | E33 | Interruttore magnetotermico differenziale 1P+N C10 30 mA tipo A | C10 | 5 | 17,13 | 18,61 | 26,32 | cad |
| E34 | E34 | Relè modulare su guida DIN, bobina 230 V | contatto 20 A | 4 | 8,79 | 19,45 | 26,30 | cad |
| E35a | E35 | Cavo FG16OR16 0,6/1 kV | 3G1,5 | 5 | 0,80 | 0,99 | 1,77 | m |
| E35b | E35 | Cavo FG16OR16 0,6/1 kV | 2×1,5 | 3 | 0,64 | 0,78 | 0,91 | m |
| E35c | E35 | Cavo FG16OR16 0,6/1 kV | 4G1,5 | 4 | 1,24 | 1,30 | 2,05 | m |
| E36 | E36 | Cavo schermato per sonde FR2OH2R16 / FROHH2R | 2×0,75 | 4 | 0,65 | 0,78 | 1,49 | m |
| E37 | E37 | Scatola da incasso 503 | 3 moduli | 4 | 0,25 | 0,26 | 0,26 | cad |

### Il dettaglio (6 novembre 2026)

| Codice | Negozio | Articolo | Netto/UM € | Note | Fonte |
|---|---|---|--:|---|---|
| I73a | ManoMano | Caleffi 108601 iStop | 77,38 |  | [link](https://www.manomano.it/p/valvola-antigelo-con-corpo-in-ottone-caleffi-108-1-40239508) |
| I73a | Leroy Merlin (Maligi Home) | Caleffi 108601 | 72,45 | marketplace | [link](https://www.leroymerlin.it/prodotti/108601-valvola-antigelo-corpo-in-ottone-1-caleffi-83928823.html) |
| I73a | Amazon.it | Caleffi 108601 | 84,21 | spedizione 8,99 € | [link](https://www.amazon.it/108601-Valvola-antigelo-ottone-CALEFFI/dp/B07GDSNLMX) |
| I73a | Amazon.it | Caleffi 108601 | 79,86 |  | [link](https://www.amazon.it/Caleffi-108601-anti-gelo-circuiti-aerotermica/dp/B00OXUD9OM) |
| I73a | ManoMano | Giacomini R148HPY005 | 62,30 | pagina di categoria; IVA non detta | [link](https://www.manomano.it/cat/valvole+giacomini?page=2) |
| I73b | Rubinetteria Shop | Giacomini R148HPY006 | 65,57 |  | [link](https://www.rubinetteriashop.com/en/heat-pump-system-components/11898-antifreeze-valve-protection-for-heat-pumps-114-gas-connection-giacomini-r148hpy006.html) |
| I73b | eBay.it | BRV Bonetti 05791 | 54,92 | IVA non detta | [link](https://www.ebay.it/itm/357622672577) |
| I73b | new-heating.com | Caleffi iStop 108 1¼" | 108,34 | estero | [link](https://new-heating.com/en/caleffi-istop-classic-frost-protection-valve-type.html) |
| I73b | panpower.eu | Caleffi 108 iStop 1¼" DN32 | 114,66 | estero | [link](https://panpower.eu/en/accessories-for-heat-pumps/7042-caleffi-108-istop-1-14-dn32.html) |
| I74 | ManoMano | Caleffi 526153, 7 bar | 40,71 |  | [link](https://www.manomano.it/p/5261-gr-sic-boiler-1-inox-ccurva-526161-45800733?model_id=4722815) |
| I74 | Amazon.it | Caleffi 526153 | 48,55 | spedizione 8,04 € | [link](https://www.amazon.it/526153-sicurezza-scaldacqua-accumulo-CALEFFI/dp/B07GSGK71L) |
| I74 | Rubinetteria Shop | Caleffi 526153 | 49,35 |  | [link](https://www.rubinetteriashop.com/en/components-for-sanitary-systems/2033-safety-group-for-storage-water-heater-caleffi-526153-526163.html) |
| I74 | Amazon.it | Thermador GS20C = Caleffi 526151, curvo | 25,09 | spedizione 10,90 € | [link](https://www.amazon.it/Thermador-GS20C-Caleffi-526151-Sicurezza/dp/B009L4J8P4) |
| I75 | Rubinetteria Shop | Giacomini R850 | 3,24 |  | [link](https://www.rubinetteriashop.com/en/ball-valves/8958-ball-valve-female-female-connections-giacomini-r850.html) |
| I75 | ManoMano | Bugatti FF farfalla PN50 | 4,27 | pagina di categoria | [link](https://www.manomano.it/cat/valvola+a+sfera+a+passaggio+totale) |
| I75 | Amazon.it | RB FF farfalla DN15 | 7,34 |  | [link](https://www.amazon.it/VALVOLA-SFERA-PASSAGGIO-TOTALE-FARFALLA/dp/B08XZ4NT99) |
| I75 | ManoMano | Tiemme Tornado DN15 | 8,84 | pagina di categoria | [link](https://www.manomano.it/cat/valvola+a+sfera+a+passaggio+totale) |
| I76 | Amazon.it | Best Solar L 120 | 4,92 |  | [link](https://www.amazon.it/Best-Solar-Pozzetto-sonda-Lunghezza/dp/B09SZPBX2W) |
| I76 | ManoMano | Comisa L 100 | 12,38 | pagina di categoria | [link](https://www.manomano.it/cat/pozzetto+sonda) |
| I76 | Leroy Merlin | portasonda ottone L 130 | 12,95 |  | [link](https://www.leroymerlin.it/prodotti/portasonda-in-ottone-attacco-1-2-pozzetto-per-termostato-l-130mm-guarnizione-88350554.html) |
| I76 | Fausto Ricambi | pozzetto ottone ½" | 14,66 | spedizione 7,52 € | [link](https://www.faustoricambi.it/thermometers-pozzetto-ottone-1-2-per-termometro-in-vetro-10-a-120-c-a-bulbo.2.14.305.gp.12909.uw) |
| I77 | Amazon.it | Giacomini R228IY003 | 21,50 | un solo riscontro esatto | [link](https://www.amazon.it/R228I-Rubinetto-manometro-R228IY003-GIACOMINI/dp/B07Z8DZ78W) |
| I77 | Amazon.it | Rastelli 424 portamanometro | 14,35 | tre vie non dichiarato | [link](https://www.amazon.it/424-Rubinetto-portamanometro-ottone-RASTELLI/dp/B07NK5QJFC) |
| I78a | Tecnomat | Banninger esagonale M/F | 2,30 |  | [link](https://www.tecnomat.it/it/riduz-esag-ottone-banninger-m-f-1-1-4x1-10016609/) |
| I78a | ManoMano | Rain M-F ottone | 2,98 | saldo | [link](https://www.manomano.it/p/riduttore-m-f-ottone-1-14-x-1-34872732) |
| I78b | Tecnomat | Banninger esagonale M/F | 1,52 |  | [link](https://www.tecnomat.it/it/rriduz-esag-ott-banninger-m-f-1-x3-4-10013658/) |
| I78b | ManoMano | Wolfpack M 1" × F ¾" | 5,30 | pagina di categoria | [link](https://www.manomano.it/cat/riduttore+maschio+femmina) |
| I79 | ManoMano | Wilo Star-Z 15 Nova | 138,75 |  | [link](https://www.manomano.it/p/circolatore-domestico-star-z-15-nova-wilo-4132760-6094842) |
| I79 | Leroy Merlin | Wilo Star-Z 15 Nova | 137,09 |  | [link](https://www.leroymerlin.it/prodotti/star-z-15-nova-wilo-4132760-14397627.html) |
| I79 | Amazon.it | Grundfos Comfort UP15-14 B PM | 132,80 |  | [link](https://www.amazon.it/Grundfos-97916771-Up-efficienza-circolazione-potabile/dp/B01L4OZ8XO) |
| I79 | ManoMano | Grundfos Comfort 15-14 B PM | 133,90 |  | [link](https://www.manomano.it/p/circolante-grundfos-simple-acqua-chaudel-sanitario-up15-14-bx-pm-ref-97916772-29023254?model_id=3423221) |
| I79 | ManoMano | DAB Evosta 2 11/85 SAN R | 85,40 |  | [link](https://www.manomano.it/p/circolatore-dab-evosta-2-1185-san-r-12-60187267-84784383) |
| I79 | Amazon.it | DAB Evosta 2 11/85 R | 109,84 |  | [link](https://www.amazon.it/dab-pumps-EVOSTA-SAN-circolazione/dp/B083TBGQXP) |
| I80a | Rubinetteria Shop + ManoMano | Caleffi 610 ¾" + servomotore 637042 | 176,24 | somma di valvola e servomotore | [link](https://www.rubinetteriashop.com/en/mixing-valves/7000-sector-threaded-three-way-mixing-valve-caleffi-610.html) |
| I80a | Amazon.it | Esbe VRG131 DN20 + ARA661 | 184,10 | somma di valvola e servomotore | [link](https://www.amazon.it/VALVOLA-MISCELATRICE-ROTATIVA-FILETTO-ART-11600800/dp/B01M6ZU10L) |
| I80b | Leroy Merlin + ManoMano | Caleffi 610 1" + servomotore 637042 | 179,04 | somma | [link](https://www.leroymerlin.it/prodotti/valvola-miscelatrice-a-tre-vie-filettata-a-settore-caleffi-610-1-91565602.html) |
| I80b | ManoMano + Amazon.it | Esbe VRG131 DN25 + ARA661 | 181,00 | somma | [link](https://www.manomano.it/p/valvola-miscelatrice-miscelatore-esbe-vrg-131-3-4-3-vie-f-12754077) |
| I80b | Amazon.it | kit Esbe VRG131 DN25 + ARA661 | 223,39 | kit | [link](https://www.amazon.it/VRG131-ARA661-riscaldamento-mixer-metter%C3%B2-Motor/dp/B00JFYKYCG) |
| I41e | ManoMano | Elbi ERCE 35 | 53,63 | pagina di categoria | [link](https://www.manomano.it/cat/vaso+espansione+35+litri) |
| I41e | ManoMano | Desivero 35 l | 65,57 |  | [link](https://www.manomano.it/p/vaso-espansione-storm-lt35-senza-basamento-codice-prod-st06548-49280672) |
| I41e | Amazon.it | Cosmo 35 l | 66,63 |  | [link](https://www.amazon.it/riscaldamento-espansione-35-LTR-vordruck-pressione/dp/B01D1XX3VA) |
| I41e | ManoMano | Zilmet Cal-Pro 35 | 71,07 | pagina di categoria | [link](https://www.manomano.it/cat/vaso+espansione+35+litri) |
| I41e | Leroy Merlin | Zilmet Cal-Pro 35 | 81,48 | pagina di marca | [link](https://www.leroymerlin.it/prodotti/stufe-climatizzatori-e-idraulica/impianti-per-carico-acqua-e-gas/valvole-e-accessori-idraulici/zilmet-p.html) |
| I41e | ManoMano | Caleffi 556035 | 89,46 |  | [link](https://www.manomano.it/p/556035-vaso-despansione-saldato-per-impianti-di-riscaldamento-35-litri-caleffi-6302443) |
| I41f | Amazon.it | Zilmet Zilflex H 50 | 80,33 |  | [link](https://www.amazon.it/zilflex-50-vaso-espansione-vordruck-50-litri/dp/B00TFCX9CA) |
| I41f | Amazon.it | Elbi ERCE-50 | 89,34 |  | [link](https://www.amazon.it/Elbi-A102L34-Espansione-Riscaldamento-Erce-50/dp/B00WWGQX2O) |
| I41f | Leroy Merlin | Zilmet Cal-Pro 50 | 90,57 | pagina di marca | [link](https://www.leroymerlin.it/prodotti/stufe-climatizzatori-e-idraulica/impianti-per-carico-acqua-e-gas/valvole-e-accessori-idraulici/zilmet-p.html) |
| I81a | Tecnomat | APE pressfit Ø16 | 3,25 |  | [link](https://www.tecnomat.it/it/gomito-pressfit-ape-o16mm-pex-10042067/) |
| I81a | Amazon.it | gomito a pressare 16×16 | 3,69 |  | [link](https://www.amazon.it/GOMITO-PRESSARE-TUBO-MULTISTRATO-16/dp/B01G3WYU68) |
| I81b | ManoMano | Noyon & Thiébault Ø16 | 2,38 | pagina di categoria | [link](https://www.manomano.it/cat/raccordi+multistrato+a+pressare+16) |
| I81b | Tecnomat | APE pressfit 16×16 | 2,45 | pagina di marca | [link](https://www.tecnomat.it/it/marche/index/display/brands/5229/?page=5) |
| I81b | Amazon.it | Booparts 16-16, 4 pezzi | 2,85 |  | [link](https://www.amazon.it/BOOPARTS-raccordo-multistrato-manicotto-idraulico/dp/B0CNWG3RCW) |
| I81c | ManoMano | Dakiviva 16 × ½" M | 2,67 |  | [link](https://www.manomano.it/p/raccordo-dritto-maschio-a-pressare-per-multistrato-diametro-16x34-64565700?model_id=67892911) |
| I81c | Amazon.it | Tiemme 16 × ½" M | 6,65 | versione gas | [link](https://www.amazon.it/Raccordo-Pressare-Maschio-Multistrato-Tiemme/dp/B07TZKLN9N) |
| I81c | Leroy Merlin | NT Ø16 × M½" | 11,39 |  | [link](https://www.leroymerlin.it/prodotti/raccordo-multistrato-a-pressare-16-maschio-1-2-nt-68628630.html) |
| I82 | Leroy Merlin (Officina Idraulica) | IT-FLEX C1 EVT035 | 7,85 | pagina di categoria | [link](https://www.leroymerlin.it/prodotti/edilizia/prodotti-per-isolamento/isolamento-termico/guaina-isolante-2-m-p.html) |
| I82 | ManoMano | IT-FLEX C1 EVT035, tubo da 2 m | 7,85 | 19,16 € il tubo da 2 m | [link](https://www.manomano.it/p/tubo-isolante-guaina-it-flex-c1-spessore-32-mm-o-interno-35-mm-prezzo-al-metro-venduto-tassativamente-in-tubo-da-2-metri-e-multipli-evt035-87432145) |
| I82 | ManoMano | IT-FLEX C1 EVT035 | 7,20 |  | [link](https://www.manomano.it/p/tubo-isolante-guaina-it-flex-c1-spessore-32-mm-o-interno-35-mm-prezzo-al-metro-venduto-tassativamente-in-tubo-da-2-metri-e-multipli-evt035-87432145) |
| E31a | Amazon.it | A2ZWORLD RCBO classe B C16 | 90,16 | marca sconosciuta; solo C16 | [link](https://www.amazon.it/A2ZWORLD-Interruttore-Differenziale-Occupa-Moduli/dp/B0DP34LLGT) |
| E31a | Westbase Direct (UK) | Live Electrical RKB125C-030, C25 tipo B | 85,30 | 72,47 £ IVA esclusa; estero | [link](https://westbasedirect.com/products/live-electrical-rkb125c-030-25a-1p-n-c-curve-6ka-30ma-type-b-bi-directional-rcbo) |
| E31b | Emmebistore | Siemens 5SV3322-4 2P 25 A | 390,66 |  | [link](https://www.emmebistore.com/interruttori-differenziali-puri-bipolari-e-quadripolari-siemens/interruttore-differenziale-tipo-b-2-poli-25a-30ma-230vac-siemens-5sv33224-4001869548876-56649.html) |
| E31b | Stock Elettrico | ABB B274802 blocco 2P 25 A per S200 | 309,42 |  | [link](https://www.stockelettrico.it/products/19560-ABB-B274802-Blocco-Differenziale-2P-25A-30mA-Tipo-B/?id=19560) |
| E31b | Emmebistore | ABB B274802 | 295,86 | prezzo dubbio | [link](https://www.emmebistore.com/blocchi-differenziali-abb/blocco-differenziale-2p-25a-30ma-tipo-b-per-serie-s-200-abb-b274802-8012542748021-59771.html) |
| E31b | Amazon.it | TURHAN RCCB tipo B 2P 40 A | 271,67 | marca sconosciuta | [link](https://www.amazon.it/Interruttore-differenziale-corrente-63Amp-100mA/dp/B0CSW5VPZK) |
| E32 | Tecnomat | Schneider 1P+N C20 1M | 5,98 |  | [link](https://www.tecnomat.it/it/int-magn-schneider-1p-n-20a-4-5ka-c-1m-25016596/) |
| E32 | Tecnomat | Bticino 1P+N C20 1M | 6,80 |  | [link](https://www.tecnomat.it/it/magn-bticino-1p-n-20a-4-5ka-c-1m-25101115/) |
| E32 | Tecnomat | Schneider 1P+N C25 1M | 5,98 |  | [link](https://www.tecnomat.it/it/int-magn-schneider-1p-n-25a-4-5ka-c-1m-25016575/) |
| E32 | Leroy Merlin | Bticino FC881C25 | 6,80 |  | [link](https://www.leroymerlin.it/prodotti/interruttore-magnetotermico-bticino-1p-n-25a-4-5ka-1m-230-v-fc881c25-32987185.html) |
| E32 | Leroy Merlin | Schneider DomA47 C32 1M | 7,30 |  | [link](https://www.leroymerlin.it/prodotti/interruttore-magnetotermico-schneider-32a-1-modulo-82796906.html) |
| E32 | ManoMano | Chint EB 1P+N 32 A | 5,48 | pagina di categoria | [link](https://www.manomano.it/cat/magnetotermico+chint+32a) |
| E33 | Bricohome | Chint NB1L1 203333 | 17,13 |  | [link](https://bricohomeferramenta.it/products/interruttore-magnetotermici-differenziali-nb1l1-4-5-ka) |
| E33 | Amazon.it | Chint 203333 | 17,21 |  | [link](https://www.amazon.it/Chint-Magnetotermici-Differenziali-NB1L-230Vac-10A-30mA/dp/B09BBP1SBY) |
| E33 | ManoMano | Chint 203333 | 18,81 |  | [link](https://www.manomano.it/p/abb-sace-spa-ds91lc10ac30-ds901l-c10-30ma-ac-interrdiffer45ka-1p-1139998) |
| E33 | eBay.it | Chint 203333 | 18,61 |  | [link](https://www.ebay.it/itm/406399773512) |
| E33 | Voltair | Chint NB1L1 C10 tipo A | 26,32 |  | [link](https://www.voltair.it/it/nb1l1-int-mtd-1p-n-10a-30ma-45ka-c-tipo-a-2mod-37505.html) |
| E34 | RS Italia | Finder 22.21.8.230.4000 | 23,32 | prezzo indicativo | [link](https://it.rs-online.com/web/p/rele-di-potenza/0159789) |
| E34 | Amazon.it | Finder 22.21.8.230.4000 | 26,30 |  | [link](https://www.amazon.it/stores/Finder/page/5D7311CB-3EF3-406D-9F41-D5803A9D0EBF) |
| E34 | ManoMano | Finder 22.22.8.230.4000 2NA | 15,57 |  | [link](https://www.manomano.it/p/finder-222282304000-rele-industriale-tensione-nom-230-v-ac-corrente-di-commut-max-20-a-2-na-1-pz-38591627) |
| E34 | Klinkmann | Chint NCH8-20/11 | 8,79 | estero | [link](https://store.klinkmann.com/?p=7393) |
| E35a | Stock Elettrico | FG16OR16-3G1.5 al metro | 0,99 |  | [link](https://www.stockelettrico.it/products/15513-Cavo-Elettrico-FG16OR16-3G15-Cavo-CPR-FG16OR16-3G15mm2-con-giallo-verde-AL-METRO/) |
| E35a | Stock Elettrico | FG16OR16-3G1.5 matassa 100 m | 0,80 |  | [link](https://www.stockelettrico.it/products/15514-Cavo-Elettrico-FG16OR16-3G15M-Cavo-CPR-FG16OR16-3G15mm2-con-giallo-verde-100mt/) |
| E35a | Tecnomat | FG16(O)R16 3G1,5 matassa 100 m | 0,98 |  | [link](https://www.tecnomat.it/it/cavo-trip-fg16-o-r16-0-6-1kv-3g1-5-100m-10073622/) |
| E35a | ManoMano | FG16OR16 3G1,5 al metro | 1,19 |  | [link](https://www.manomano.it/p/al-metro-cavo-fg16or16-multipolare-3-conduttori-con-giallo-verde-con-1-5-mmq-di-sezione-fg7-3gx15-fg16or16-3gx15-10925940) |
| E35a | RS Italia | Prysmian FG16OR16 3G1.5 100 m | 1,77 |  | [link](https://it.rs-online.com/web/p/cavi-di-potenza/2161677) |
| E35b | Stock Elettrico | FG16OR16 2×1,5 a taglio | 0,64 |  | [link](https://www.stockelettrico.it/products/15507-CAVO-CPR-FG16OR16-2X15-A-TAGLIO/) |
| E35b | Elettronew | FG16OR16 2×1,5 | 0,78 | pagina di categoria | [link](https://www.elettronew.com/en/prodotti/categoria/fg16or-unipolar-and-multipolar-double-insulation-cables-2037.html) |
| E35b | ManoMano | FG16OR16 2×1,5 al metro | 0,91 |  | [link](https://www.manomano.it/p/al-metro-cavo-fg16or16-multipolare-fg16-2-conduttori-da-1-5mmq-senza-giallo-verde-fg7-2x15-fg16or16-2x15-10925950) |
| E35c | Stock Elettrico | FG16OR16-4G1.5 al metro | 1,24 |  | [link](https://www.stockelettrico.it/products/15520-Cavo-Elettrico-FG16OR16-4G15-Cavo-CPR-FG16OR16-4G15mm2-con-giallo-verde-AL-METRO/) |
| E35c | Elettronew | FG16OR16 4×1,5 | 1,30 |  | [link](https://www.elettronew.com/en/fg16or-unipolar-and-multipolar-double-insulation-cables/double-insulated-flameproof-cable-fg16or16-4x15mmq-06-1-kv-grey-fg16r4x15m-42415.html) |
| E35c | Emmebistore | FG16OR16 4G1,5 | 1,30 | pagina di categoria | [link](https://www.emmebistore.com/cavi-elettrici-fg16or-fg16om-e-ftg18-4528) |
| E35c | Leroy Merlin | FG16OR16 4×1,5 | 2,05 | pagina di categoria | [link](https://www.leroymerlin.it/prodotti/elettricita-automazioni-e-fotovoltaico/fili-e-cavi/cavi-elettrici-e-fili/cavi-multipolari/cavo-fg16or16-p.html) |
| E36 | Stock Elettrico | Specialcavi FR2OH2R16 2×0,75, 100 m | 0,67 |  | [link](https://www.stockelettrico.it/products/15485-Specialcavi-Baldassari-CFZ07502M100-Cavo-Schermato-CPR-CONTROLFLEX-FR2OH2R16-2x075mm2/) |
| E36 | Emmebistore | FR2OH2R16 2×0,75 al metro | 0,65 | taglio 3,50 € | [link](https://www.emmebistore.com/cavi-schermati/cavo-fror-schermato-antifiamma-2x075-frohh2r-19771.html) |
| E36 | Elettronew | FROHH2R 2×0,75 | 0,89 | minimo 100 m | [link](https://www.elettronew.com/en/shielded-cables/fror-shielded-flameproof-cable-frohh2r-2x075-sq-mm-33042.html) |
| E36 | Amazon.it | FR2OHH2R 2×0,75, 10 m | 1,49 |  | [link](https://www.amazon.it/ELETTRO-CAVI-SCHERMATO-ANTIFIAMMA-FLESSIBILE/dp/B07G1BH38J) |
| E37 | Stock Elettrico | BTicino 503E | 0,25 |  | [link](https://www.stockelettrico.it/products/1432-BTicino-503E-Scatola-da-Incasso-3-Moduli-per-Serie-Civili-Universale/) |
| E37 | Emmebistore | BTicino 503E | 0,26 |  | [link](https://www.emmebistore.com/bticino-light/scatola-da-incasso-in-resina-3-moduli-serie-civili-bticino-503e-8012199051260-49614.html) |
| E37 | Tecnomat | BTicino 503, 15 pezzi | 0,26 |  | [link](https://www.tecnomat.it/it/15-scatole-deriv-inc-3m-mod-503-bticino-10041379/) |
| E37 | Leroy Merlin | BTicino S503EFA, 15 pezzi | 0,26 |  | [link](https://www.leroymerlin.it/prodotti/scatola-da-incasso-3-moduli-s503efa-bticino-15-pezzi-85112878.html) |

## 2ter. I prezzi d'acquisto dell'installatore — 28 ottobre 2026

**Fatture Bricoman all'installatore della commessa PR.BG.017** (27 ottobre – 2 novembre 2026), lette dalla
cartella della commessa il 6 novembre 2026. Sono prezzi netti pagati al banco da un professionista, quindi
affidabili come prezzo; le quantità di quella commessa non sono un riferimento (il PO: «non mi fido tantissimo»).
I nippli entrano con la regola delle giunzioni (`REL-023`): un nipplo fra due pezzi filettati che si toccano.

| ID | Voce | Articolo | Codice | Fornitore | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I83a | Nipplo in ottone | NIPPLE OTTONE CROMATO 1/2'' | 5054826528304 | Bricoman | Bricoman | 1 pz | 1,02 | 1,02 | cad |  |
| I83b | Nipplo in ottone | NIPPLE OTTONE CROMATO 3/4'' | 5054826528403 | Bricoman | Bricoman | 1 pz | 1,52 | 1,52 | cad |  |
| I83c | Nipplo in ottone | NIPPLE OTTONE GIALLO BANNINGER M1'' | 5052740322701 | Bricoman | Bricoman | 1 pz | 2,13 | 2,13 | cad | in ghisa (280, 1") 1,15 € |
| I83d | Nipplo ridotto in ottone | NIPPLE OTT.GIALLO RID.BANNINGER 1x3/4'' | 5052740310104 | Bricoman | Bricoman | 1 pz | 2,21 | 2,21 | cad | in ghisa (245, 1"×¾") 1,41 € |

## 3. Ancora da prezzare

**Le voci che la distinta conta e il listino non ha.** Dopo il §2bis restano: il combinato tipo B di marca nelle taglie
C20, C25 e C32 (il prezzo pubblico italiano non c'è; c'è il combinato economico, E31a); il plenum di ripresa con filtro
(Idrosanitaria ne ha dato uno per la Daikin FBA71A9, «prezzo indicativo», §5), la canalina coprilinee 110×75
(Idrosanitaria ha offerto la serie D100), il manicotto del flessibile, i sostegni dei flessibili diversi dal Ø200, il
collare delle linee frigorifere. Con il §5 hanno trovato un prezzo la guaina sp. 32 per il tubo da 28 (I84c), le
fascette (A07c) e il sostegno del flessibile Ø200 (A08c).

Quello che manca, dopo il §1 e il §2:

- **I60, guaina sp. 19 per tubo 54 esatto.** IT-FLEX e Armaflex esistono, ma senza prezzo
  pubblico (Würth lo mostra solo ai clienti registrati). Il riferimento sta fra il Ø42
  (3,30 €/m) e il Ø60 (4,49 €/m) di Leroy Merlin.
- **I62, coppelle in lamierino e curve PVC per tubi isolati da 26 a 54 mm.** Si trovano
  solo il foglio e il nastro al metro quadro. Il prezzario della Regione Friuli Venezia
  Giulia 2025 dà la finitura posata (fornitura e posa, IVA esclusa): PVC 22,24 €/m²
  (voce 58.1.IN6.01), alluminio da 0,6 mm 39,88 €/m² (voce 58.1.IH4.01).
- **I68, PVC rigido Ø32.** Non si trova a un prezzo credibile: a Ø32 c'è il PP grigio (HT).
- **A03, tee per Ø125 e Ø200;** **A06, plenum con attacco Ø125 o Ø200 esatto** (si trovano
  Ø100, Ø150 e Ø160).
- **A08, kit di sospensione per l'unità interna canalizzata** (barra con antivibranti).
  La barra M8 da 1 m c'è già nel §1 (I64, Tecnomat).
- **F09, manicotto a brasare 1/2" e 5/8".**
- **E05 da Tecnomat.** L'articolo esiste (cod. 10073631, matassa 100 m), ma il prezzo non è
  uscito.
- **Le misure che le note del §1 danno come non trovate**: tee 40×40×40 (I19), raccordo
  maschio (I25), le misure da 1"1/4 a 2" di I28, 1"1/4 e 1"1/2 di I30b e del filtro a Y
  (I37b), manometro 0–6 bar (I44), vasi da 24/35/50 l (I41d), circolatore 32-60 (I50),
  tassello M8 (I66), rame 3/4" (F03b), tubo flessibile Ø160 (A02a), cavo FROR 1,5 mm²
  (E10), differenziali 4P 25 e 32 A (E18b), magnetotermici 1P+N 16/25 A (E20).
- **Le righe del §1 da verificare sulla scheda**: I28, I41c, I48, I54, E19b; la lunghezza
  della barra delle guaine I56–I59, assunta 2 m. Leroy Merlin vende la stessa linea IT-FLEX
  a metro, a multipli di 2 m.
- **F04/F05, tubo di rame ricotto con guaina.** Non è da prezzare: è coperto da F01–F03,
  il rame rivestito a metro.

## 4. Abbattista — ordini del 10 e del 13 novembre 2026

**Gli ordini OC-STD-0185611 del 10 novembre 2026** (offerta 212119 del 9 novembre: circolatore, volano, valvola di
zona, bollitore) **e OC-STD-0188404 del 13 novembre 2026** (offerta 214224 dell'11 novembre: il circuito idraulico),
commessa PR.MI.059, filiale di Milano. Pagamento RB 30/60 gg fine mese. **Tutte le 46 righe**, nell'ordine del
documento (colonna Rif.: documento e riga).

- **Il prezzo**: il listino Abbattista con gli sconti in cascata (50+20, 50+25, 50+30; sul tubo 50+15+3); il netto è
  quello dell'ordine, IVA esclusa. Canapa e nastro anticondensa sono senza sconto.
- **Il tubo**: Abbattista ha offerto il multistrato **rivestito blu, guaina 6 mm**, in rotoli, al posto del tubo nudo
  con la guaina che la lista chiedeva (19 e 30 mm sul 32, 9 e 30 mm sul 26): le righe sono sui codici del tubo
  preisolato (I07, I09, I10), non su quelli del nudo, e la guaina non c'è.
- **Gli articoli uguali**: la valvola di zona, lo sfogo aria, il defangatore e il gruppo di sicurezza sono gli stessi
  articoli Caleffi dell'offerta Idrosanitaria (stesso codice), e così il volano Cordivari: il confronto è diretto.

### Il materiale

| ID | Voce | Articolo | Codice | Fornitore | Rif. | Confezione | Listino € | Sconti % | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|---|--:|--:|---|---|
| I51 | Valvola deviatrice 3 vie motorizzata | VAL.ZONA MOTOR.CF.6443 1 644366 | 48972151 | Abbattista | OC 0185611 r. 3 | 1 pz | 390,73 | 50+20 | 156,29 | 156,290 | cad | Caleffi 6443 1" (644366), lo stesso articolo dell'offerta Idrosanitaria |
| I09 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVEST.BLU MM26/06 — MT.50 KAITMRB26/06 26G11711AHEC70F | 23660274 | Abbattista | OC 0188404 r. 1 | rotolo 50 m | 278,79 | 50+15+3 | 114,93 | 2,299 | m | rivestito blu, guaina 6 mm (il §1: 9 mm); offerto al posto del tubo nudo con la guaina della lista |
| I07 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVEST.BLU MM16/06 — MT.50 KAITMRB16/06 26G11111AHAA70F | 15604398 | Abbattista | OC 0188404 r. 2 | rotolo 50 m | 110,84 | 50+15+3 | 45,70 | 0,914 | m | rivestito blu, guaina 6 mm; offerto al posto del tubo nudo |
| I10 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVEST.BLU MM32/06 — MT.25 KAITMRB32/06 26G11311AHFC60F | 69113897 | Abbattista | OC 0188404 r. 3 | rotolo 25 m | 204,89 | 50+15+3 | 84,47 | 3,379 | m | rivestito blu, guaina 6 mm (il §1: 9 mm); offerto al posto del tubo nudo con la guaina della lista |
| I13 | Gomito 90 a pressare | RACC.CURVO 32X32 PRESS.TIEMME 1653 — 1650013 | 67027245 | Abbattista | OC 0188404 r. 4 | 1 pz | 26,26 | 50+25 | 9,85 | 9,848 | cad |  |
| I43a | Valvola automatica di sfogo aria | VAL.SFOGO ARIA AUT.CF.5020 1/2 GIALLA — 502040 | 41082752 | Abbattista | OC 0188404 r. 5 | 1 pz | 33,92 | 50+20 | 13,57 | 13,570 | cad | Caleffi 5020 (502040), lo stesso articolo dell'offerta Idrosanitaria |
| I38b | Defangatore magnetico | DEFANG.C/MAGNETE ORIENT.CF.545306 D.1 | 34297572 | Abbattista | OC 0188404 r. 6 | 1 pz | 223,08 | 50+20 | 89,23 | 89,230 | cad | Caleffi 545306, lo stesso articolo dell'offerta Idrosanitaria |
| I46 | Rubinetto di scarico portagomma | RUBIN.PORTAGOMMA 1/2 TIEMME LEVA NERA — 2500043 | 47637767 | Abbattista | OC 0188404 r. 7 | 1 pz | 14,36 | 50+25 | 5,38 | 5,385 | cad |  |
| I41a | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESP.SANIT/RISC.VAREM EXTRA LT.8 — LC CE R1008223S4000000 | 32063341 | Abbattista | OC 0188404 r. 8 | 1 pz | 61,70 | 50+25 | 23,14 | 23,140 | cad | sanitario e riscaldamento |
| I41c | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESP.SANIT.VAREM LT.24 AT.3/4" — C/CONTROFLAN.AVVITATA S2024263S40000000 | 46192715 | Abbattista | OC 0188404 r. 9 | 1 pz | 96,29 | 50+25 | 36,11 | 36,110 | cad | 24 l, sanitario, con controflangia: offerto per il vaso del riscaldamento da 24 l (il codice è la taglia da 25 l) |
| I44 | Manometro radiale/assiale 0-6 bar | MAN.RAD.3/8 ISPESL D.80 6BAR FERR. — 110512/6 | 23838345 | Abbattista | OC 0188404 r. 10 | 1 pz | 21,00 | 50+30 | 7,35 | 7,350 | cad | ⚠ attacco 3/8" (la voce: ½"); ISPESL; con serpentina e rubinetto a parte (righe 11 e 12) |
| — | Serpentina in rame 3/8" per manometro | SERPENTINA RAME 3/8 FERR.110556 | 34982850 | Abbattista | OC 0188404 r. 11 | 1 pz | 28,31 | 50+30 | 9,91 | 9,910 | cad | il kit ISPESL del manometro; la lista non la chiede |
| I77 | Rubinetto portamanometro a tre vie, ½" | RUB.PORTAMANOMETRO PN16 FERR.110553 3/8 | 36256339 | Abbattista | OC 0188404 r. 12 | 1 pz | 39,10 | 50+30 | 13,69 | 13,690 | cad | ⚠ attacco 3/8" (la voce: ½") |
| I18 | Tee a pressare | RACC.T PRESS.TIEMME 1657 32X32X32 — 1650058 | 99816767 | Abbattista | OC 0188404 r. 13 | 1 pz | 42,98 | 50+25 | 16,12 | 16,116 | cad |  |
| I17 | Tee a pressare | RACC.T PRESS.TIEMME 1657 26X26X26 — 1650018 | 89921759 | Abbattista | OC 0188404 r. 14 | 1 pz | 26,08 | 50+25 | 9,78 | 9,780 | cad |  |
| I32 | Valvola a sfera a passaggio totale ottone | VAL.SFERA FF ACQUA 1 TIEMME 2310 — 2310001 C/LEVA ROSSA | 84135919 | Abbattista | OC 0188404 r. 15 | 1 pz | 27,04 | 50+25 | 10,14 | 10,140 | cad |  |
| I31 | Valvola a sfera a passaggio totale ottone | VAL.SFERA FF ACQUA 3/4 TIEMME 2310 — 2310008 C/LEVA ROSSA | 74240912 | Abbattista | OC 0188404 r. 16 | 1 pz | 17,01 | 50+25 | 6,38 | 6,380 | cad |  |
| I40a | Valvola di sicurezza 3 bar | VAL.SIC.ISPESL CF.527 3 ATE 1/2 527430 | 92415435 | Abbattista | OC 0188404 r. 17 | 1 pz | 122,36 | 50+20 | 48,95 | 48,950 | cad | Caleffi 527, ISPESL |
| — | Imbuto di scarico ½" con ritegno | IMBUTO SCAR.CF.5521 1/2 552140 | 94621714 | Abbattista | OC 0188404 r. 18 | 1 pz | 56,89 | 50+20 | 22,76 | 22,760 | cad | per lo scarico convogliato della sicurezza; la lista non lo conta a parte |
| — | Raccordo diritto a pressare M 1" × 26 | RACC.DIR.M.PRESS.TIEMME 1650 26X1 — 1650027 | 83018140 | Abbattista | OC 0188404 r. 19 | 1 pz | 12,84 | 50+25 | 4,82 | 4,817 | cad | offerto per i raccordi «all'attacco» del 26, che la regola prezza col ¾" (I22) |
| I22 | Raccordo diritto a pressare filettato maschio | RACC.DIR.M PRESS.TIEMME 1650 26X3/4 — 1650007 | 95193952 | Abbattista | OC 0188404 r. 20 | 1 pz | 9,85 | 50+25 | 3,69 | 3,693 | cad |  |
| I81c | Raccordo diritto a pressare M × multistrato, ½" × 16 | RACC.DIR.M PRESS.TIEMME 1650 16X1/2 — 1650009 | 68636050 | Abbattista | OC 0188404 r. 21 | 1 pz | 4,84 | 50+25 | 1,81 | 1,810 | cad | offerto per il raccordo «all'attacco» del 16 («quotato ½" M») |
| — | Raccordo diritto a pressare M 3/8" × 16 | TIEMME RACC.DIR.M.16X3/8M PRESS.1650262 | 04756113 | Abbattista | OC 0188404 r. 22 | 1 pz | 6,12 | 50+25 | 2,29 | 2,290 | cad | la regola prezza il 16 col ½" (I81c) |
| I23 | Raccordo diritto a pressare filettato maschio | RACC.DIR.M PRESS.TIEMME 1650 32X1 — 1650032 | 05088968 | Abbattista | OC 0188404 r. 23 | 1 pz | 15,06 | 50+25 | 5,65 | 5,646 | cad |  |
| — | Raccordo diritto a pressare M 1" × 32 | RACC.DIR.M PRESS.TIEMME 1650 32X1 — 1650032 | 05088968 | Abbattista | OC 0188404 r. 24 | 1 pz | 15,06 | 50+25 | 5,64 | 5,645 | cad | come la riga 23: i due raccordi «all'attacco» del 32 |
| — | Collare con gommino ¾" | COLLARE RIV.GOMMA GIA 082209 STO1G 3/4 | 36190648 | Abbattista | OC 0188404 r. 25 | 1 pz | 5,71 | 50+25 | 2,14 | 2,142 | cad | la regola dei collari ha un codice solo, I63 (1") |
| — | Collare con gommino 3/8" | COLLARE RIV.GOMMA STO1G 3/8 GIA 082009 | 23388081 | Abbattista | OC 0188404 r. 26 | 1 pz | 5,34 | 50+25 | 2,00 | 2,005 | cad | la regola dei collari ha un codice solo, I63 (1") |
| I63 | Collare pesante con gommino e barra filettata M8 | COLLARE RIV.GOMMA GIA 082309 STO1G 1 | 01814945 | Abbattista | OC 0188404 r. 27 | 1 pz | 6,25 | 50+25 | 2,34 | 2,342 | cad | il collare; il fissaggio è a parte (riga 28) |
| — | Supporto rapido di fissaggio per collari (2 pezzi) | SUPP.RAPIDO FISS.GIA 146400 10TF 2PZ. | 19211046 | Abbattista | OC 0188404 r. 28 | 1 pz | 3,20 | 50+25 | 1,20 | 1,199 | cad | il fissaggio dei collari: 14 confezioni per 27 collari |
| I49a | Tubo flessibile inox / giunto antivibrante | GIUNTO IN GOMMA ANTIVIBRANTE BOCCH.11/4 — MCVGGAB11/4 | 76800301 | Abbattista | OC 0188404 r. 29 | 1 pz | 32,94 | 50+20 | 13,18 | 13,175 | cad | giunto in gomma con bocchettone |
| I83c | Nipplo in ottone | NIPPLE GHISA ZINCATO FIG 280 1" — GEONGZ2801 | 82014246 | Abbattista | OC 0188404 r. 30 | 1 pz | 5,64 | 50+20 | 2,26 | 2,257 | cad | in ghisa zincata fig. 280 (il §2ter: in ottone) |
| I83e | Nipplo ridotto 1¼" × 1" | NIPPLE GHISA ZINCATO FIG.245 11/4-1 — GEONGZ24511/4-1 | 39080875 | Abbattista | OC 0188404 r. 31 | 1 pz | 11,22 | 50+20 | 4,49 | 4,490 | cad | in ghisa zincata fig. 245 |
| I83b | Nipplo in ottone | NIPPLE GHISA ZINCATO FIG 280 3/4 — GEONGZ2803/4 | 72119238 | Abbattista | OC 0188404 r. 32 | 1 pz | 3,92 | 50+20 | 1,57 | 1,570 | cad | in ghisa zincata fig. 280 (il §2ter: in ottone) |
| I67a | Teflon / canapa / pasta sigillante / filo sigillante | CANAPA EXTRA 4 FACOT CANEXK025 — CANEXK025 | 02923656 | Abbattista | OC 0188404 r. 33 | 0,25 kg | 7,50 | — | 7,50 | 7,500 | cad | canapa, 0,25 kg a 30 €/kg, senza sconto |
| I67b | Teflon / canapa / pasta sigillante / filo sigillante | KOLGAS-UNI 400GR.FACOT KOLGUNI0400 | 33424924 | Abbattista | OC 0188404 r. 34 | 1 pz | 14,54 | 50+20 | 5,81 | 5,810 | cad | pasta sigillante, 400 g |
| I61 | Nastro adesivo per isolante / colla | NASTRO ANTICOND.H50MM L10M SP.3MM — 850NS020100 | 88838050 | Abbattista | OC 0188404 r. 35 | rotolo 10 m | 4,91 | — | 4,91 | 24,550 | cad | nastro anticondensa in gomma 3 mm, senza sconto; il codice è il rotolo da 50 m: 5 rotoli da 10 m |
| I55a | Additivo inibitore / pulitore per impianti | CONDIZ.CALD.CILLIT HS23RS PLUS KG.1 — 10145AC LAVAGGIO ALTA T. | 38021657 | Abbattista | OC 0188404 r. 36 | 1 pz | 47,70 | 50+20 | 19,08 | 19,080 | cad | lavaggio, 1 kg |
| I55b | Additivo inibitore / pulitore per impianti | CONDIZ.CALD.CILLIT HS COMBI KG1 10135 — ALTA TEMPERATURA PROTET | 67193034 | Abbattista | OC 0188404 r. 37 | 1 pz | 75,60 | 50+20 | 30,24 | 30,240 | cad | protettivo, 1 kg |
| I74 | Gruppo di sicurezza sanitario per bollitore, ¾" | GR.SIC.BOLL.CF.5261 1/2 526142 | 43273068 | Abbattista | OC 0188404 r. 38 | 1 pz | 71,02 | 50+20 | 28,41 | 28,410 | cad | Caleffi 5261 ½" (526142), lo stesso articolo dell'offerta Idrosanitaria |
| I47 | Gruppo di riempimento automatico | VAL.CAR.CALEFFI.553 C/MANOM.1/2 553640 — RIEMPIMENTO AUTOM | 42291019 | Abbattista | OC 0188404 r. 39 | 1 pz | 168,96 | 50+20 | 67,59 | 67,590 | cad | ⚠ il disconnettore non è nel titolo: la voce lo chiede (I-309); Caleffi 553 con manometro |
| I78a | Riduzione filettata in ottone M × F, 1¼" × 1" | RIDUZIONE GHISA ZINCATA FIG.241 11/4-1 — GEORGZ24111/4-1 | 45357738 | Abbattista | OC 0188404 r. 40 | 1 pz | 5,17 | 50+20 | 2,07 | 2,070 | cad | in ghisa zincata fig. 241 |
| — | Staffa per vaso di espansione ¾" | STAFFA VASO DI ESPANSIONE 3/4" 075510 — GIA | 69816916 | Abbattista | OC 0188404 r. 41 | 1 pz | 38,70 | 50+25 | 14,52 | 14,515 | cad | la voce del vaso la comprende («con attacco e staffa») |
| I75 | Valvola a sfera FF a passaggio totale, ½" | VAL.SFERA FF ACQUA 1/2 TIEMME 2320 — 2310010 C/FARF.ROSSA | 88290332 | Abbattista | OC 0188404 r. 42 | 1 pz | 11,94 | 50+25 | 4,48 | 4,480 | cad | con farfalla |

### Le apparecchiature

Dal 18 novembre 2026 il costo prezza anche le apparecchiature (D-241, I-314): la lista prezzata è l'analisi CAPEX, e
deve essere completa. Il PO compra da Abbattista gli accessori più costosi (I-304).

| ID | Voce | Articolo | Codice | Fornitore | Rif. | Confezione | Listino € | Sconti % | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|---|--:|--:|---|---|
| M30a | Circolatore DAB Evosta 2 40-70/130 | POMPA EVOSTA 2 40-70/130 (1")1X230 50/60 — Y25 60231853 | 85801171 | Abbattista | OC 0185611 r. 1 | 1 pz | 241,29 | 50+20 | 96,52 | 96,520 | cad |  |
| M20b | Volano termico a quattro attacchi, 80 l | UP GBF 80 VOLANO TERMICO SEPARATORE IDRA — 3070160920018 | 68432687 | Abbattista | OC 0185611 r. 2 | 1 pz | 448,21 | 50+20 | 179,29 | 179,290 | cad | stesso articolo Cordivari dell'offerta Idrosanitaria (3070160920018) |
| M10b | Bollitore ACS 200 l a serpentino | BOLLY 1 XL WB 200 BOLLITORE VERTICALE CO — 3104162330011 | 79861453 | Abbattista | OC 0185611 r. 4 | 1 pz | 1.566,31 | 50+20 | 626,52 | 626,520 | cad | superficie di scambio 2 m² (scheda Cordivari BOLLY 1 XL 02.2026, codice 3104162330011, I-328; acciaio rivestito Polywarm®, attacchi primario 1¼" F); modello diverso da quello dell'offerta Idrosanitaria |

## 5. Idrosanitaria — preventivo del 9 novembre 2026

**Il preventivo XC/STD/2704331 del 9 novembre 2026**, valido fino al 24 novembre 2026, commessa PR.MI.059, sede di
Magnago. Pagamento alla consegna. Il preventivo è «indicativo, da rivedere in fase d'ordine». **Tutte le 81 righe**,
nell'ordine del documento; il totale merce è 10.835,01 € più 8,75 € di contributo RAEE (sulle macchine).

- **Il prezzo**: il prezzo unitario del preventivo, già netto, IVA esclusa.
- **Il tubo**: nudo, in barre da 5 m, con la guaina a parte (spessore × foro: «9X28» è la guaina da 9 mm per il tubo
  da 26).
- **I raccordi «all'attacco»**: per i raccordi diritti a pressare filettati che la lista chiamava «all'attacco» (senza
  il pollice), Idrosanitaria ha offerto **manicotti** tubo-tubo (righe 40, 42, 47): le righe sono sui codici dei
  manicotti, che è quello che sono.
- **Il rame «CONDY»**: è il rame rivestito (righe 50 e 51, F01b e F03b): il preventivo non ha isolante per il rame, e il PO ha detto che allora è il preisolato (I-316).

### Il materiale

| ID | Voce | Articolo | Codice | Fornitore | Rif. | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| I71a | Basamento antivibrante in gomma per unità esterna | PIEDINO ANTIVIBRANTE PAV 1000KG | 11105340N | Idrosanitaria | XC 2704331 r. 6 | 1 pz | 2,60 | 2,603 | cad | piedino antivibrante, portata 1000 kg |
| I03 | Tubo multistrato PEX-AL-PEX nudo, rotolo o barra | TUBO 26X3 AL.0,35 NUDO BARRE 5MT PEX-AL-PEX | R999Y174 | Idrosanitaria | XC 2704331 r. 7 | barra 5 m | 2,01 | 2,011 | m | barre da 5 m |
| I84a | Guaina isolante elastomerica sp. 9 mm per tubo 26 | ISOLANTE GOMMA ST 9X28 MM | 09028005508 | Idrosanitaria | XC 2704331 r. 8 | 1 m | 0,51 | 0,513 | m | spessore 9 mm, foro 28 mm |
| — | Collare con gommino ¾" M8 | COLLARE OTER PES.C/GUARN. P+T 3/4" M8 833 | 83305 | Idrosanitaria | XC 2704331 r. 9 | 1 pz | 1,44 | 1,442 | cad | la regola dei collari ha un codice solo, I63 (1") |
| I01 | Tubo multistrato PEX-AL-PEX nudo, rotolo | TUBO 16X2 AL.0,2 NUDO BARRE 5MT PEX-AL-PEX | R999Y125 | Idrosanitaria | XC 2704331 r. 10 | barra 5 m | 0,76 | 0,760 | m | barre da 5 m |
| — | Collare isofonico 3/8" | COLLARE ISOFONICO ZINCATO C/T 3/8 | 83303 | Idrosanitaria | XC 2704331 r. 11 | 1 pz | 1,29 | 1,294 | cad | la regola dei collari ha un codice solo, I63 (1") |
| I84c | Guaina isolante elastomerica sp. 32 mm per tubo 26 | ISOLANTE GOMMA ST 32X28 MM | 32028005508 | Idrosanitaria | XC 2704331 r. 12 | 1 m | 3,50 | 3,505 | m | spessore 32 mm, foro 28 mm: per la guaina da 30 mm della lista |
| I04 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO 32X3 AL.0,4 NUDO BARRE 5MT PX-AL-PEX | R999Y184 | Idrosanitaria | XC 2704331 r. 13 | barra 5 m | 3,21 | 3,211 | m | barre da 5 m |
| I58 | Guaina isolante elastomerica sp. 13-19 mm | ISOLANTE GOMMA ST 19X35 MM | 19035005508 | Idrosanitaria | XC 2704331 r. 14 | 1 m | 1,65 | 1,654 | m | spessore 19 mm, foro 35 mm |
| I63 | Collare pesante con gommino e barra filettata M8 | COLLARE OTER PES.C/GUARN. P+T 1" M8 833 | 83306 | Idrosanitaria | XC 2704331 r. 15 | 1 pz | 1,68 | 1,681 | cad | collare pesante con guarnizione, M8 |
| I82 | Guaina elastomerica sp. 32 mm, tubo Ø35 | ISOLANTE GOMMA ST 32X35 MM | 32035005508 | Idrosanitaria | XC 2704331 r. 16 | 1 m | 3,94 | 3,945 | m | spessore 32 mm, foro 35 mm |
| I13 | Gomito 90 a pressare | RM122 GOMITO 90° 32 | RM122Y011 | Idrosanitaria | XC 2704331 r. 17 | 1 pz | 7,20 | 7,200 | cad |  |
| I61 | Nastro adesivo per isolante / colla | NASTRO IN GOMMA ADES.H.50 SP.3 L.10M | 850NS020100 | Idrosanitaria | XC 2704331 r. 18 | rotolo 10 m | 3,07 | 15,340 | cad | nastro in gomma adesivo 3 mm, rotolo 10 m; il codice è il rotolo da 50 m: 5 rotoli |
| I67a | Teflon / canapa / pasta sigillante / filo sigillante | CANAPA GR.250 | 00505 | Idrosanitaria | XC 2704331 r. 19 | 1 pz | 3,94 | 3,944 | cad | canapa 250 g |
| I67b | Teflon / canapa / pasta sigillante / filo sigillante | MASTICE EXTRA GAS KG.0,460 | 00201 | Idrosanitaria | XC 2704331 r. 20 | 1 pz | 2,63 | 2,632 | cad | mastice 0,46 kg |
| I43a | Valvola automatica di sfogo aria | VALV.AUTOM.SFOGO ARIA 1/2" 2,5BARMINICAL | 502040 | Idrosanitaria | XC 2704331 r. 21 | 1 pz | 11,16 | 11,158 | cad | Caleffi Minical (502040), lo stesso articolo dell'ordine Abbattista |
| I51 | Valvola deviatrice 3 vie motorizzata | VALV.DEVIAT.1" 3 VIE MOTOR.C/MICRO 220 | 644366 | Idrosanitaria | XC 2704331 r. 22 | 1 pz | 143,33 | 143,326 | cad | Caleffi 644366, lo stesso articolo dell'ordine Abbattista |
| I74 | Gruppo di sicurezza sanitario per bollitore, ¾" | GRUPPO SICUREZZA BOILER 1/2 DIR. | 526142 | Idrosanitaria | XC 2704331 r. 23 | 1 pz | 26,05 | 26,051 | cad | Caleffi 526142, lo stesso articolo dell'ordine Abbattista |
| I38b | Defangatore magnetico | DEFANGATORE MAGNETICO VERTICALE 1" F | 545306 | Idrosanitaria | XC 2704331 r. 24 | 1 pz | 81,83 | 81,832 | cad | Caleffi 545306, lo stesso articolo dell'ordine Abbattista |
| I46 | Rubinetto di scarico portagomma | RUBINETTO SCARICO CALDAIA 1/2 | 538400 | Idrosanitaria | XC 2704331 r. 25 | 1 pz | 6,25 | 6,246 | cad |  |
| I41a | Vaso di espansione chiuso a membrana per riscaldamento | SERBATOIO RISC/SANIT. DP 8LT BCO | A2C2L16 V0020 | Idrosanitaria | XC 2704331 r. 26 | 1 pz | 20,05 | 20,053 | cad | riscaldamento e sanitario |
| I41c | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE RISC. ER 24 CE | A102L27 00270 | Idrosanitaria | XC 2704331 r. 27 | 1 pz | 23,66 | 23,663 | cad | 24 l, riscaldamento (il codice è la taglia da 25 l) |
| I47 | Gruppo di riempimento automatico | GRUPPO DI CARICAMENTO C/DISCONNETTORE 1/2" | 580011 | Idrosanitaria | XC 2704331 r. 28 | 1 pz | 153,01 | 153,011 | cad | con disconnettore |
| I49a | Tubo flessibile inox / giunto antivibrante | ZKT GIUNTO ELASTICO FIL. 1"1/4 PN10 GHISA/EPDM | 149B12570C | Idrosanitaria | XC 2704331 r. 29 | 1 pz | 16,27 | 16,271 | cad | giunto elastico filettato ghisa/EPDM |
| I55a | Additivo inibitore / pulitore per impianti | X800 PULITORE IMPIANTI 1LT | X800L-12X1L-EXPB | Idrosanitaria | XC 2704331 r. 30 | 1 pz | 24,81 | 24,807 | cad |  |
| I55b | Additivo inibitore / pulitore per impianti | PROTETTIVO FILMANTE UNIV. | K375Y021 | Idrosanitaria | XC 2704331 r. 31 | 1 pz | 19,70 | 19,705 | cad |  |
| I78a | Riduzione filettata in ottone M × F, 1¼" × 1" | F241 RIDUZ.MF GH.ZINC.11/4-1" | 770241231 | Idrosanitaria | XC 2704331 r. 32 | 1 pz | 1,44 | 1,438 | cad | in ghisa zincata fig. 241 |
| I44 | Manometro radiale/assiale 0-6 bar | MANOMETRO ATT.RAD.G1/2B M1-ABS 100/R-0-6BAR | PA5206BD03 | Idrosanitaria | XC 2704331 r. 33 | 1 pz | 9,84 | 9,842 | cad | 0–6 bar, attacco radiale ½" |
| I18 | Tee a pressare | RM150 TEE 32X32X32 | RM150Y011 | Idrosanitaria | XC 2704331 r. 34 | 1 pz | 11,11 | 11,105 | cad |  |
| I17 | Tee a pressare | RM150 TEE 26X26X26 | RM150Y009 | Idrosanitaria | XC 2704331 r. 35 | 1 pz | 7,27 | 7,274 | cad |  |
| I77 | Rubinetto portamanometro a tre vie, ½" | 403RF RUBINETTO PORTAMANOMETRO 1/2" WATTS | 403R12 | Idrosanitaria | XC 2704331 r. 36 | 1 pz | 8,95 | 8,951 | cad |  |
| I32 | Valvola a sfera a passaggio totale ottone | 0801 VALV.SFERA ASTER 1" FF LEVA ALLUM. C/LEVA ALLUMINIO | 0801N406 | Idrosanitaria | XC 2704331 r. 37 | 1 pz | 8,12 | 8,120 | cad |  |
| I31 | Valvola a sfera a passaggio totale ottone | 0801 VALV.SFERA ASTER 3/4" FF LEVA ALLUM. | 0801N405 | Idrosanitaria | XC 2704331 r. 38 | 1 pz | 5,62 | 5,620 | cad |  |
| I40a | Valvola di sicurezza 3 bar | VST VALVOLA DI SICUREZZA 1/2" 3 BAR CERTIF.INAIL | 0212130 | Idrosanitaria | XC 2704331 r. 39 | 1 pz | 27,14 | 27,135 | cad | certificata INAIL |
| I26b | Manicotto a pressare | RM102 MANICOTTO 26X3 | RM102Y009 | Idrosanitaria | XC 2704331 r. 40 | 1 pz | 4,24 | 4,242 | cad | manicotto: offerto per i raccordi «all'attacco» del 26 della lista, che sono filettati |
| I22 | Raccordo diritto a pressare filettato maschio | RM107 RACCORDO FIL.M. 26X3/4" | RM107Y049 | Idrosanitaria | XC 2704331 r. 41 | 1 pz | 3,01 | 3,011 | cad |  |
| I81b | Manicotto a pressare multistrato, 16×2 | RM102 MANICOTTO 16X2 | RM102Y003 | Idrosanitaria | XC 2704331 r. 42 | 1 pz | 2,14 | 2,137 | cad | manicotto: offerto per il raccordo «all'attacco» del 16 della lista, che è filettato |
| — | Raccordo diritto a pressare M 3/8" × 16 | RM107 RACCORDO FIL.M. 16X3/8" | RM107Y023 | Idrosanitaria | XC 2704331 r. 43 | 1 pz | 1,62 | 1,621 | cad | la regola prezza il 16 col ½" (I81c) |
| I23 | Raccordo diritto a pressare filettato maschio | RM107 RACCORDO FIL.M. 32X1" | RM107Y059 | Idrosanitaria | XC 2704331 r. 44 | 1 pz | 4,74 | 4,737 | cad |  |
| I83c | Nipplo in ottone | F280 NIPPLO GHISA ZINC.1" | 770280206 | Idrosanitaria | XC 2704331 r. 45 | 1 pz | 1,57 | 1,567 | cad | in ghisa zincata fig. 280 (il §2ter: in ottone) |
| I83e | Nipplo ridotto 1¼" × 1" | F245 NIPPLO GH.ZINC.11/4-1" | 770245227 | Idrosanitaria | XC 2704331 r. 46 | 1 pz | 3,12 | 3,119 | cad | in ghisa zincata fig. 245 |
| I26c | Manicotto a pressare | RM102 MANICOTTO 32X3 | RM102Y011 | Idrosanitaria | XC 2704331 r. 47 | 1 pz | 6,07 | 6,074 | cad | manicotto: offerto per i raccordi «all'attacco» del 32 della lista, che sono filettati |
| I83b | Nipplo in ottone | F280 NIPPLO GHISA ZINC.3/4" | 770280205 | Idrosanitaria | XC 2704331 r. 48 | 1 pz | 1,09 | 1,089 | cad | in ghisa zincata fig. 280 (il §2ter: in ottone) |
| A01c | Tubo flessibile isolato per aria, rotolo 10 m, Ø200 | TUBO FLEX ISOLATO PER CANALIZZATO D203 PREZZO AL MT | TES203 | Idrosanitaria | XC 2704331 r. 49 | 1 m | 6,90 | 6,897 | m | Ø203, al metro |
| F01b | Coppia tubi rame preisolati | TUBO RAME 3/8"X0.8 ROTOLO 50M CONDY | RBMEM009520800 | Idrosanitaria | XC 2704331 r. 50 | 1 m | 4,34 | 4,344 | m | rivestito: nel preventivo non c'è isolante per il rame (gli isolanti sono 9×28, 32×28, 19×35, 32×35, 9×35), quindi «CONDY» è il preisolato (I-316); 3/8" × 0,8 |
| F03b | Coppia tubi rame preisolati | TUBO RAME 5/8"X1.0 ROTOLO 50M CONDY | RBMEM015871000 | Idrosanitaria | XC 2704331 r. 51 | 1 m | 9,50 | 9,504 | m | rivestito: nel preventivo non c'è isolante per il rame, quindi «CONDY» è il preisolato (I-316); 5/8" × 1,0 |
| — | Piedino antivibrante, portata 1000 kg | PIEDINO ANTIVIBRANTE PAV 1000KG | 11105340N | Idrosanitaria | XC 2704331 r. 57 | 1 pz | 2,60 | 2,603 | cad | come la riga 6 (I71a), per l'unità esterna |
| I64 | Barra filettata M8 / M10 zincata | BARRA FILETTATA MA 8 X 1000MM ZINCATA DIN 975 | 647V00000801 | Idrosanitaria | XC 2704331 r. 58 | 1 pz | 0,71 | 0,709 | cad |  |
| — | Barra filettata M10, 1 m | BARRA FILETTATA MA10 X 1000MM ZINCATA DIN 975 | 647V00001001 | Idrosanitaria | XC 2704331 r. 59 | 1 pz | 1,15 | 1,153 | cad | le regole prezzano la M10 con la M8 (I64) |
| — | Dado esagonale M8 | DADI ESAG. M 8 6S CL8 ZINC.UNI 5588 | 688V00000008 | Idrosanitaria | XC 2704331 r. 60 | 1 pz | 0,01 | 0,009 | cad |  |
| — | Dado esagonale M10 | DADI ESAG. M10 6S CL8 ZINC.UNI 5588 | 688V00000010 | Idrosanitaria | XC 2704331 r. 61 | 1 pz | 0,02 | 0,019 | cad | «quantita' dadi da confermare» |
| A06c | Plenum porta-bocchetta 400×200, attacco Ø200 | PORTABOCCHETTA PLP 400X200 1X200 POSTERIORE | PLP-U-400X200-1B-P | Idrosanitaria | XC 2704331 r. 62 | 1 pz | 30,81 | 30,808 | cad | ⚠ attacco posteriore (la voce: laterale) |
| A07c | Fascetta stringitubo inox 60–270 mm | FASCETTE STRINGITUBO ACC.INOX 60-270 | FSI60-270 | Idrosanitaria | XC 2704331 r. 63 | 1 pz | 1,82 | 1,819 | cad | per il flessibile fino a Ø250 |
| A07a | Nastro alluminio / fascette stringitubo | NASTRO ADESIVO IN ALLUMINIO | KK-43 | Idrosanitaria | XC 2704331 r. 64 | 1 pz | 16,75 | 16,749 | cad |  |
| A08c | Collare di fissaggio isolato Ø200 | COLLARE FISSAGGIO ISOLATO D200 | AIR-RS2SNE-200 | Idrosanitaria | XC 2704331 r. 65 | 1 pz | 3,60 | 3,600 | cad | il sostegno del flessibile Ø200; 5 offerti contro 21 della lista |
| — | Derivazione a Y 250-200-150 | DERIVAZ.MULTIPLA A Y 250-200-150 MM | 11161803 | Idrosanitaria | XC 2704331 r. 66 | 1 pz | 87,72 | 87,717 | cad | non è la derivazione 1×Ø200 > 2×Ø200 della lista |
| F06 | Nastro di finitura per linee frigorifere | NASTRO IN GOMMA ADES.H.50 SP.3 L.10M | 850NS020100 | Idrosanitaria | XC 2704331 r. 67 | 1 pz | 3,07 | 3,068 | cad | nastro in gomma adesivo 3 mm, rotolo 10 m |
| — | Plenum di ripresa chiuso per Daikin FBA71A9 | PLENUM DI RIPRESA CHIUSO DAIKIN FBA71A9 | PLR-DAI091-C | Idrosanitaria | XC 2704331 r. 68 | 1 pz | 102,32 | 102,316 | cad | «prezzo indicativo da rivedere in fase esecutiva con disegno esecutivo» |
| — | Giunto antivibrante in tela 70/100/70, rotolo 25 m | GIUNTO ANTIVIBRANTE 70/100/70 - CONF. 25 M | CC8 | Idrosanitaria | XC 2704331 r. 69 | 1 pz | 80,91 | 80,908 | cad | il rotolo, per un giunto della lista |
| — | Canalina coprilinee D100, barra 2 m | T-100 CANALINA C/BOLLA 2MT D100 (PREZZO AL MT) | B-N11120010 | Idrosanitaria | XC 2704331 r. 70 | 1 m | 8,64 | 8,640 | m | «modello da confermare»; la lista chiede la 110×75 |
| — | Curva piana della canalina D100 | CP-100 CURVA PIANA D100 | N11120100 | Idrosanitaria | XC 2704331 r. 71 | 1 pz | 11,42 | 11,418 | cad |  |
| — | Terminale a muro della canalina D100 | TERMINALE A MURO FLANGIATO QUADRO TM100 NEW LINE (3 PZ) | SCD100283 | Idrosanitaria | XC 2704331 r. 72 | 1 pz | 17,58 | 17,584 | cad |  |
| — | Manicotto della canalina D100 | MG-100 MANICOTTO DI GIUNZIONE D100 | N11121100 | Idrosanitaria | XC 2704331 r. 73 | 1 pz | 3,86 | 3,860 | cad |  |
| I68a | Tubo di scarico condensa Ø32 / Ø40 con raccordi, Ø32 PP (HT) barra 2 m | TCR-32 TUBO SCAR CON RIGIDO 2MTAL MT | SCD300034 | Idrosanitaria | XC 2704331 r. 74 | barra 2 m | 2,38 | 2,382 | m | tubo rigido per condensa TCR-32, barra 2 m |
| I87 | Clip di fissaggio per tubo condensa rigido | CLIP FISS.BIANCO TUBO SC.COND.RIGID | 11126396 | Idrosanitaria | XC 2704331 r. 75 | 1 pz | 0,40 | 0,403 | cad |  |
| I84b | Guaina isolante elastomerica sp. 9 mm per tubo 32 | ISOLANTE GOMMA ST 9X35 MM | 09035005508 | Idrosanitaria | XC 2704331 r. 76 | 1 m | 0,59 | 0,586 | m | spessore 9 mm, foro 35 mm |
| I86 | Braga 45° Ø40/32 in PP | PP-TECH BRAGA DM 40/32 45 HTEA | BEA040345 | Idrosanitaria | XC 2704331 r. 77 | 1 pz | 1,16 | 1,162 | cad | l'innesto sullo scarico esistente |
| I68d | Tubo di scarico condensa Ø32 / Ø40 con raccordi, curva Ø32 87°/45° | TCR32 CA 90 CURVA AD ANGOLO | 11126392 | Idrosanitaria | XC 2704331 r. 78 | 1 pz | 3,69 | 3,694 | cad | curva TCR32 90° |
| I68f | Tubo di scarico condensa Ø32 / Ø40 con raccordi, manicotto Ø32 | TCR32 MG MANICOTTO DI GIUNZIONE | 11126393 | Idrosanitaria | XC 2704331 r. 79 | 1 pz | 2,60 | 2,603 | cad | manicotto TCR32 |
| I69 | Sifone ispezionabile condensa | SIFONE A SECCO ORIZ. ANTIODORED.32 | SCD300006 | Idrosanitaria | XC 2704331 r. 80 | 1 pz | 13,33 | 13,328 | cad | sifone a secco antiodore, Ø32 |
| I85 | Collante per tubo di scarico condensa rigido | COLLA PER TUBO SCARICO CONDENSA RIGIDO | 11126315 | Idrosanitaria | XC 2704331 r. 81 | 1 pz | 13,65 | 13,652 | cad |  |

### Le apparecchiature e la climatizzazione

Dal 18 novembre 2026 il costo le prezza (D-241, I-314).

| ID | Voce | Articolo | Codice | Fornitore | Rif. | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|--:|--:|---|---|
| M10b | Bollitore ACS 200 l a serpentino | Cordivari BOLLY 1 XL WB 200 | 3104162330011 | Idrosanitaria | XC 2704331 r. 1, corretta (comunicata dal PO il 18 novembre 2026) | 1 pz | 546,00 | 546,000 | cad | superficie di scambio 2 m² (scheda Cordivari BOLLY 1 XL 02.2026, I-328); il preventivo corretto da Idrosanitaria al posto del Bolly 1 ST da 0,8 m² (I-334); il codice è quello della scheda, assunto |
| — | Bollitore ACS 200 l a serpentino | BOL. BOLLY1 ST FB WB 200 V003 | 3104162330042 | Idrosanitaria | XC 2704331 r. 1 | 1 pz | 461,40 | 461,396 | cad | superficie di scambio 0,8 m² (scheda Cordivari letta dal motore di ricerca, I-315: da confermare); «modello da confermare»; modello diverso da quello di Abbattista; sostituito dalla correzione del preventivo (riga sotto, I-334): resta documentato |
| M01c | Pompa di calore aria-acqua monoblocco R290, Shenling ThermaX 12 kW | U.E. PDC MONOBLOCCO TRI 12KW R290 | AW12NMXGHA | Idrosanitaria | XC 2704331 r. 2 | 1 pz | 3.103,60 | 3.103,600 | cad | ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa (il codice AW12NMXGHA nelle schede dei rivenditori, REL-028) |
| — | Box elettronico della pompa di calore | BOX ELETTRONICO POMPA DI CALORE MONOBLOCCO R290 | ATW-A03N | Idrosanitaria | XC 2704331 r. 3 | 1 pz | 461,20 | 461,200 | cad | va con la pompa di calore della riga 2 (non verificato); nessuna regola lo usa |
| M30a | Circolatore DAB Evosta 2 40-70/130 | EVOSTA2 40-70/130 1" CIRC.EL.SING.MONOF. | 60231853 | Idrosanitaria | XC 2704331 r. 4 | 1 pz | 93,60 | 93,600 | cad |  |
| M20b | Volano termico a quattro attacchi, 80 l | BOL. VB 80LT C/4 ATT. C/COPERT.V003 | 3070160920018 | Idrosanitaria | XC 2704331 r. 5 | 1 pz | 156,49 | 156,492 | cad | lo stesso articolo Cordivari dell'ordine Abbattista (UP GBF 80) |
| M44a | Comando a filo Daikin BRC1H52W7 | COMANDO FILO BT BIANCO | BRC1H52W7 | Idrosanitaria | XC 2704331 r. 52 | 1 pz | 119,12 | 119,116 | cad |  |
| M42a | Plenum motorizzato di zona Airzone 4×200 | AIRZONE EASYZONE 25 WI-FI MEDIUM IB8 DAIKIN 4X200 | AZC25DAIBS07M4 | Idrosanitaria | XC 2704331 r. 53 | 1 pz | 993,61 | 993,611 | cad |  |
| M43a | Termostato di zona Airzone Think radio | TERMOSTATO THINK RADIO BIANCO | AZCE6THINKRB | Idrosanitaria | XC 2704331 r. 54 | 1 pz | 170,16 | 170,158 | cad |  |
| M41a | Unità esterna Daikin RZASG71MV1, 7,1 kW | U.E. MONO ADVANCE 7,1KW R32 MONOFASE | RZASG71MV1 | Idrosanitaria | XC 2704331 r. 55 | 1 pz | 1.017,27 | 1.017,275 | cad |  |
| M40a | Unità interna canalizzata Daikin FBA71A9, 7 kW | U.I.CANALIZ.M/PREV S/COM 7,0KW R32/R410 | FBA71A9 | Idrosanitaria | XC 2704331 r. 56 | 1 pz | 835,78 | 835,783 | cad |  |
