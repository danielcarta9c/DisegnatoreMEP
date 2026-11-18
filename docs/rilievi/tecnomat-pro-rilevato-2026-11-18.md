# RILIEVO TECNOMAT PRO — 18 novembre 2026 — negozio Segrate (MI)

> **Rilievo completo** con l'account Tecnomat Pro di Nove C (prezzi IVA esclusa, letti sulla scheda prodotto, «TOT … IVA escl.»).
> **Parte A**: 150 righe su 150 lette per codice; 5 codici non più a catalogo sostituiti e 1 (E20) sostituito per risparmio (nota «sostituisce»).
> **Parte B**: 35 articoli trovati (9 con ⚠), 27 «non trovato».
> **Alternative economiche (Parte A)**: ricerca fatta famiglia per famiglia (valvole a sfera, ritegni, filtri, defangatori, circolatore, multistrato nudo e raccordi press, cavi, rame, guaine, protezioni, termostati, pompa condensa, glicole, deviatrice). Nella quasi totalità i codici già in elenco sono i più economici a parità di misura e specifica; unica sostituzione conveniente **E20** (magnetotermico 4P 32A: da 97,54 a 16,56, ⚠ curva da verificare). Non verificate: multistrato preisolato, tee/riduzioni press, raccordi ghisa, valvole di sicurezza, vasi (salvo 12 l), miscelatori, filler e riduttore, polifosfati e additivi, staffe, sigillanti, nastri, centralini e scatole.
> **Limiti**: il prezzo al pubblico («pubblico») è annotato solo dove la scheda lo mostrava nella lettura.
> Negozio: tutte le letture a Segrate (MI); dove la riga diceva Pero, il prezzo è comunque quello letto a Segrate.

# Tecnomat Pro — il rilievo da fare con Claude in Chrome

**Preparato il 18 novembre 2026** (`REL-028`; I-304, I-311). Nove C ha l'abbonamento **Tecnomat Pro**: i prezzi
che vediamo da professionisti possono essere più bassi di quelli del rilievo del 2 novembre. Questo file serve a una
conversazione con **Claude in Chrome** nel browser del PO, sul sito Tecnomat, per due cose:

- **Parte A — da verificare**: le **150** righe Tecnomat che il listino ha già (il rilievo del 2 novembre), da
  ricontrollare col prezzo Pro. Si cercano **per codice Tecnomat**.
- **Parte B — da trovare**: i **62** articoli che la distinta usa e che da Tecnomat non abbiamo (o abbiamo in una
  versione che non va bene). Si cercano **per voce**. Prima la B1: le 30 voci della commessa PR.MI.059.

---

## Istruzioni per la sessione Chrome

**Prima di cominciare**

1. Il PO entra su tecnomat.it con l'**account Tecnomat Pro** di Nove C. Il login lo fa il PO: Claude non scrive né
   legge password.
2. Si sceglie il **negozio di Segrate (MI)**, come il 2 novembre. Se un articolo a Segrate non c'è, si guarda Pero
   (MI) e lo si scrive nella colonna Negozio.
3. Se il sito chiede una verifica («non sono un robot» o simili), Claude si ferma e la fa il PO.

**Come si riempie una riga**

- **Netto** è il prezzo **IVA esclusa**, quello che vediamo da Pro. Se la pagina mostra solo il prezzo IVA inclusa,
  si divide per 1,22 e lo si scrive nella nota («da IVA inclusa»).
- Se la pagina mostra **più prezzi** (al pubblico e Pro, o prezzi per quantità), nella colonna si mette il prezzo Pro
  per la confezione singola, e gli altri si scrivono nella nota (per esempio «pubblico 7,45 · da 10 pz 6,90»).
- **Confezione**: come la vende il negozio (1 pz, 2 pz, rotolo 50 m, barra 3 m, matassa 100 m).
- **Netto/UM**: il netto diviso per i pezzi o i metri della confezione. Per esempio un rotolo da 50 m a 100,00 € fa
  2,00 €/m; una confezione da 2 collari a 2,21 € fa 1,105 €/pz. UM è «m», «cad» o «m²».
- Se l'articolo **non c'è**, si scrive «non trovato» nella nota e si lasciano vuoti i prezzi. **Non si stima mai un
  prezzo.**

**Che cosa si cerca**

- **La marca non conta, conta la prescrizione** (I-307): la misura, l'attacco, la pressione, il fondo scala, gli
  organi che la voce nomina (per esempio il disconnettore del gruppo di riempimento). Un articolo di qualunque marca che
  rispetta la voce va bene.
- Se ci sono più articoli che vanno bene, si prende **il più economico** al netto per unità.
- Se si trova solo un articolo che **non rispetta del tutto** la voce (un'altra misura, un altro attacco, un organo
  che manca), lo si scrive lo stesso, con la nota che **comincia con ⚠** e dice che cosa non torna (per esempio «⚠
  attacco 3/8" (la voce: ½")»).
- **Mai un articolo che fa un altro mestiere**: se non c'è niente che faccia la stessa cosa, si scrive «non trovato».
- **Parte A**: se il codice di oggi non c'è più, o se c'è un articolo **più economico che rispetta la voce**, si
  scrive quello nuovo nella riga (articolo, codice, prezzi) e nella nota «sostituisce <codice vecchio>».
- **Non si cambiano gli ID**, e non si aggiungono righe: una riga per ID.

**Alla fine**

- In testa al file si scrive la **data del rilievo** e il negozio.
- Si restituisce **il file intero**, in Markdown, con le colonne riempite: il PO lo riporta alla sessione di Claude Code
  sul repository.

## Per la sessione che lo importa (Claude Code, repository DisegnatoreMEP)

- **Parte A**: le righe Tecnomat del §1 del listino prendono i prezzi Pro. Il capitolo dice la data del nuovo rilievo
  e «Tecnomat Pro»; le note «sostituisce» cambiano articolo e codice; i prezzi del 2 novembre restano nella storia di
  git. Le note con ⚠ entrano come scostamenti.
- **Parte B**: righe nuove con fornitore «Tecnomat», negozio, codice e data, sull'ID della riga; ⚠ dove la nota lo
  dice; «non trovato» non entra.
- Poi: le prove del listino, la misura di PR.MI.059 (`docs/collaudi/REL-027/pr-mi-059/misura.py`) mostrata al PO, la
  suite, il banco, la release con `scripts/costruisci-skill.py`.

---

## Parte A — da verificare col prezzo Pro (150 righe)

Le righe del rilievo del 2 novembre, per famiglia. «Oggi» è quello che il listino ha adesso. Si cerca per **codice
Tecnomat**. Le righe con ⚠ nella nota di oggi sono articoli che non rispettano la voce: si verifica il prezzo, e
l'articolo giusto si cerca nella parte B.


### A · Idraulica - tubo multistrato

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I01 | Tubo multistrato PEX-AL-PEX nudo, rotolo | MULTISTRATO APE Ø 16x2 mm NUDO PEX-B ROTOLO 100 m | 10041924 | Segrate (MI) | 100 m | 69,10 | 0,69 | m | 69,10 | 0,691 |  |
| I02 | Tubo multistrato PEX-AL-PEX nudo, rotolo | MULTISTRATO APE Ø 20x2 mm NUDO PEX-B ROTOLO 100 m | 10041925 | Segrate (MI) | 100 m | 106,50 | 1,06 | m | 106,50 | 1,065 |  |
| I03 | Tubo multistrato PEX-AL-PEX nudo, rotolo o barra | MULTISTRATO APE Ø 26x3 mm NUDO PEX-B ROTOLO 50 m | 10041926 | Segrate (MI) | 50 m | 113,53 | 2,27 | m | 113,53 | 2,271 |  |
| I04 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO SHARKBITE PERT/AL/PERT Ø 32 x 3 mm NUDO VERGA DA 3 m | 25115665 | Segrate (MI) | 3 m | 10,92 | 3,64 | m | 10,92 | 3,64 |  |
| I05 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO APE PEX-B Ø 40 x 3,5 mm NUDO VERGA DA 2,5 m | 25019689 | Segrate (MI) | 2.5 m | 13,15 | 5,26 | m | 13,15 | 5,26 |  |
| I06 | Tubo multistrato PEX-AL-PEX nudo, barra | TUBO MULTISTRATO APE PEX-B Ø 50 x 3,5 mm NUDO VERGA DA 2,5 m | 25019716 | Segrate (MI) | 2.5 m | 20,07 | 8,03 | m | 20,07 | 8,028 |  |
| I07 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 16x2 mm PEX-b/Al/PEX-b ROTOLO 100 m SPESSORE GUAINA 6 mm | 25105360 | Segrate (MI) | 100 m | 69,26 | 0,69 | m | 69,26 | 0,693 |  |
| I08 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 20x2 mm PEX-b/Al/PEX-b ROTOLO 50 m SPESSORE GUAINA 9 mm | 10041922 | Segrate (MI) | 50 m | 72,46 | 1,45 | m | 72,46 | 1,449 |  |
| I09 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 26x3 mm PEX-b/Al/PEX-b ROTOLO 50 m SPESSORE GUAINA 9 mm | 10041923 | Segrate (MI) | 50 m | 130,90 | 2,62 | m | 130,90 | 2,618 |  |
| I10 | Tubo multistrato preisolato | TUBO MULTISTRATO RIVESTITO APE Ø 32x3 mm PEX-b/Al/PEX-b ROTOLO 25 m SPESSORE GUAINA 9 mm | 10071536 | Segrate (MI) | 25 m | 98,69 | 3,95 | m | 98,69 | 3,948 |  |

### A · Idraulica - raccordi multistrato

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I11 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø20 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000753 | Segrate (MI) | 1 pz | 3,40 | 3,40 | cad | 3,40 | 3,40 |  |
| I12 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000739 | Segrate (MI) | 1 pz | 4,86 | 4,86 | cad | 4,86 | 4,86 |  |
| I13 | Gomito 90 a pressare | GOMITO PRESSFIT APE APL Ø 32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000723 | Segrate (MI) | 1 pz | 7,45 | 7,45 | cad | 7,45 | 7,45 |  |
| I14 | Gomito 90 a pressare | GOMITO 90° PRESSFIT APE APL Ø 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019740 | Segrate (MI) | 1 pz | 11,65 | 11,65 | cad | 11,65 | 11,65 |  |
| I15 | Gomito 90 a pressare | GOMITO 90° PRESSFIT APE APL Ø 50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019717 | Segrate (MI) | 1 pz | 21,08 | 21,08 | cad | 21,08 | 21,08 |  |
| I16 | Tee a pressare | TEE PRESSFIT APE APL Ø20 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000730 | Segrate (MI) | 1 pz | 4,54 | 4,54 | cad | 4,54 | 4,54 |  |
| I17 | Tee a pressare | TEE PRESSFIT APE APL Ø26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000721 | Segrate (MI) | 1 pz | 6,89 | 6,89 | cad | 6,89 | 6,89 | a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I18 | Tee a pressare | TEE PRESSFIT APE APL Ø 32x32x32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000725 | Segrate (MI) | 1 pz | 11,02 | 11,02 | cad | 11,02 | 11,02 |  |
| I19 | Tee a pressare | TEE PRESSFIT APE APL F 1 x Ø 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019739 | Segrate (MI) | 1 pz | 17,65 | 17,65 | cad | 17,65 | 17,65 |  |
| I20 | Tee a pressare | TEE PRESSFIT APE APL Ø 50X50X50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019752 | Segrate (MI) | 1 pz | 26,22 | 26,22 | cad | 26,22 | 26,22 |  |
| I21 | Raccordo diritto a pressare filettato maschio | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 3/4'' x Ø 20 mm PROFILO PRESSATURA TH-H-U | 12092751 | Segrate (MI) | 1 pz | 3,26 | 3,26 | cad | 3,26 | 3,26 |  |
| I22 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE M 3/4'' x Ø 26 mm PROFILO PRESSATURA TH-H PER TUBO MULTISTRATO | 10042037 | Segrate (MI) | 1 pz | 4,01 | 4,01 | cad | 4,01 | 4,01 |  |
| I23 | Raccordo diritto a pressare filettato maschio | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 1'' x Ø 32 mm PROFILO PRESSATURA TH-H-U | 12092754 | Segrate (MI) | 1 pz | 6,43 | 6,43 | cad | 6,43 | 6,43 |  |
| I24 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE APL M 1"1/4 x Ø 40 mm PROFILO T H TUBO MULTISTRATO SPESS.3 | 25019707 | Segrate (MI) | 1 pz | 10,64 | 10,64 | cad | 10,64 | 10,64 |  |
| I25 | Raccordo diritto a pressare filettato maschio | RACCORDO DRITTO PRESSFIT APE APL F 1"1/2 x Ø 50 mm PROFILO T H TUBO MULTISTRATO SPESS.4 | 25019734 | Segrate (MI) | 1 pz | 13,65 | 13,65 | cad | 13,65 | 13,65 |  |
| I26a | Manicotto a pressare | MANICOTTO DRITTO A STRINGERE APE Ø 20x20 mm PER TUBO MULTISTRATO | 10041948 | Segrate (MI) | 1 pz | 4,16 | 4,16 | cad | 4,16 | 4,16 |  |
| I26b | Manicotto a pressare | MANICOTTO DRITTO A STRINGERE APE Ø 26x26 mm PER TUBO MULTISTRATO | 10041949 | Segrate (MI) | 1 pz | 7,48 | 7,48 | cad | 7,48 | 7,48 |  |
| I26c | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 32x32 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000719 | Segrate (MI) | 1 pz | 5,52 | 5,52 | cad | 5,52 | 5,52 |  |
| I26d | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 40 x 40 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.3.5 | 25019709 | Segrate (MI) | 1 pz | 8,36 | 8,36 | cad | 8,36 | 8,36 |  |
| I26e | Manicotto a pressare | MANICOTTO PRESSFIT APE APL Ø 50 x 50 mm PROFILO PRESSATURA TH-H TUBO MULTISTRATO SPESS.4 | 25019736 | Segrate (MI) | 1 pz | 9,48 | 9,48 | cad | 9,48 | 9,48 |  |
| I27a | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE APL Ø20x16 mm PRESSATURA TH-H-U TUBO MULTISTRATO | 25000765 | Segrate (MI) | 1 pz | 3,31 | 3,31 | cad | 3,31 | 3,31 | a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I27b | Riduzione a pressare | MANICOTTO PRESSFIT APE APL Ø 32x26 mm PRESSATURA TH-H TUBO MULTISTRATO | 25000726 | Segrate (MI) | 1 pz | 5,55 | 5,55 | cad | 5,55 | 5,55 |  |
| I27c | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE Ø 40 x 32 mm PROFILO PRESSATURA TH-H MULTISTRATO | 25019723 | Segrate (MI) | 1 pz | 9,60 | 9,60 | cad | 9,60 | 9,60 |  |
| I27d | Riduzione a pressare | MANICOTTO RIDOTTO PRESSFIT APE Ø 50 x 40 mm PROFILO PRESSATURA TH-H MULTISTRATO | 25019750 | Segrate (MI) | 1 pz | 15,59 | 15,59 | cad | 15,59 | 15,59 |  |

### A · Idraulica - tubo acciaio

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I28 | Tubo acciaio zincato filettabile, barra | TUBO ACCIAIO ZINCATO 1'' 3 m SENZA SALDATURA 1 FILETTO | 10054077 | Segrate (MI) | 3 m | 22,66 | 7,55 | m | 22,66 | 7,553 |  |

### A · Idraulica - raccorderia filettata

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I29a | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA BERG MONTANA FIGURA 90 GOMITO FF 1"1/4 CONFORME USO ACQUA E GAS | 25018162 | Segrate (MI) | 1 pz | 2,59 | 2,59 | cad | 2,70 | 2,70 | sostituisce 10035683 (non più a catalogo) |
| I29b | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA ATUSA FIGURA 130R TEE 1" x 3/4" x 3/4" | 25018534 | Segrate (MI) | 1 pz | 2,93 | 2,93 | cad | 2,93 | 2,93 |  |
| I29c | Nipplo / gomito / tee / riduzione in ghisa malleabile zincata | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1"1/4 CONFORME USO ACQUA E GAS | 25018210 | Segrate (MI) | 1 pz | 1,89 | 1,89 | cad | 1,95 | 1,95 | sostituisce 10035767 (non più a catalogo) |
| I30a | Raccordo a tre pezzi (bocchettone) ottone | BOCCHETTONE OTTONE GIALLO BANNINGER DRITTO 3 PEZZI 3/4'' TENUTA O-RING SOLO ACQUA | 10024324 | Segrate (MI) | 1 pz | 3,70 | 3,70 | cad | 3,93 | 3,93 |  |
| I30b | Raccordo a tre pezzi (bocchettone) ottone | BOCCHETTONE DRITTO 3 PEZZI PATTARONI OTTONE GIALLO MF 1" TENUTA O-RING ACQUA - GAS | 25018743 | Segrate (MI) | 1 pz | 6,17 | 6,17 | cad | 6,55 | 6,55 | sostituisce 10024325 (non più a catalogo) |

### A · Idraulica - valvolame

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I31 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA ENOLGAS SERIE ATOMIC CON LEVA FF 3/4 PN25 | 25017140 | Segrate (MI) | 1 pz | 5,16 | 5,16 | cad | 5,16 | 5,16 |  |
| I32 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' | 12080447 | Segrate (MI) | 1 pz | 6,30 | 6,30 | cad | 6,30 | 6,30 |  |
| I33 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' 1/4 PN16 | 12080448 | Segrate (MI) | 1 pz | 14,87 | 14,87 | cad | 14,87 | 14,87 |  |
| I34 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA BUCCHI FF 1'' 1/2 PN16 | 12080450 | Segrate (MI) | 1 pz | 18,24 | 18,24 | cad | 18,24 | 18,24 |  |
| I35 | Valvola a sfera a passaggio totale ottone | VALVOLA A SFERA SERIE BASIC LEVA FF 2" PN50 | 25017115 | Segrate (MI) | 1 pz | 34,27 | 34,27 | cad | 34,27 | 34,27 |  |
| I36a | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 3/4'' OTTONE TENUTA IN POLIMERO 12 BAR | 25086992 | Segrate (MI) | 1 pz | 5,59 | 5,59 | cad | 5,59 | 5,59 |  |
| I36b | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1'' OTTONE TENUTA IN POLIMERO 12 BAR | 25086996 | Segrate (MI) | 1 pz | 7,09 | 7,09 | cad | 7,09 | 7,09 |  |
| I36c | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1''1/4 OTTONE TENUTA IN POLIMERO 10 BAR | 25086987 | Segrate (MI) | 1 pz | 10,53 | 10,53 | cad | 10,53 | 10,53 |  |
| I36d | Valvola di ritegno a molla | VALVOLA DI RITEGNO ITAP YORK FF 1''1/2 OTTONE TENUTA IN POLIMERO 10 BAR | 25087010 | Segrate (MI) | 1 pz | 15,57 | 15,57 | cad | 15,57 | 15,57 |  |
| I37a | Filtro a Y ottone | FILTRO A Y FARG 610 Ø 3/4'' PER ACQUA PN 25 MAGLIA FILTRANTE 500 MICRON | 25068146 | Segrate (MI) | 1 pz | 7,50 | 7,50 | cad | 7,50 | 7,50 |  |
| I37b | Filtro a Y ottone | FILTRO A Y FARG 610 Ø 1'' PER ACQUA PN 25 MAGLIA FILTRANTE 500 MICRON | 25068170 | Segrate (MI) | 1 pz | 10,11 | 10,11 | cad | 10,11 | 10,11 |  |

### A · Idraulica - accessori

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I38a | Defangatore magnetico | FILTRO DEFANGATORE MAGNETICO AQUAFILTRA COMPACT OTTONE 3 VIE FF 3/4 500 MICRON | 25012605 | Segrate (MI) | 1 pz | 33,20 | 33,20 | cad | 33,20 | 33,20 |  |
| I38b | Defangatore magnetico | FILTRO DEFANGATORE MAGNETICO RBM MP2 1'' 800 µ 11000 GAUSS | 25050370 | Segrate (MI) | 1 pz | 104,92 | 104,92 | cad | 104,92 | 104,92 |  |
| I43a | Valvola automatica di sfogo aria | VALVOLA SFOGO ARIA AUTOMATICA ITAP 362 M 1/2'' ATTACCO VERTICALE OTTONE | 25087007 | Segrate (MI) | 1 pz | 4,80 | 4,80 | cad | 4,80 | 4,80 |  |
| I43b | Valvola automatica di sfogo aria | VALVOLA SFOGO ARIA AUTOMATICA ITAP 362 M 3/8'' ATTACCO VERTICALE OTTONE | 25087005 | Segrate (MI) | 1 pz | 4,22 | 4,22 | cad | 4,22 | 4,22 |  |
| I44 | Manometro radiale/assiale 0-6 bar | MANOMETRO PRESSIONE 0-12 bar | 10047624 | Segrate (MI) | 1 pz | 5,33 | 5,33 | cad | 5,33 | 5,33 |  |
| I45 | Termometro a immersione con pozzetto | TERMOMETRO BIMETALLICO FERRARI Ø 80 mm 0 - 120° ATTACCO POSTERIORE POZZETTO | 10046531 | Segrate (MI) | 1 pz | 6,89 | 6,89 | cad | 6,89 | 6,89 |  |
| I46 | Rubinetto di scarico portagomma | RUBINETTO SCARICO CALDAIA 1/2'' CON PORTAGOMMA | 10012741 | Segrate (MI) | 1 pz | 3,73 | 3,73 | cad | 3,73 | 3,73 |  |
| I47 | Gruppo di riempimento automatico | GRUPPO DI RIEMPIMENTO ''FILLER'' 1/2'' | 10034051 | Segrate (MI) | 1 pz | 24,61 | 24,61 | cad | 24,61 | 24,61 |  |
| I48 | Riduttore di pressione | RIDUTTORE DI PRESSIONE HONEYWELL D04FM TARABILE 1,5 - 6 bar CON FILTRO | 10071827 | Segrate (MI) | 1 pz | 25,61 | 25,61 | cad | 25,61 | 25,61 |  |
| I49a | Tubo flessibile inox / giunto antivibrante | FLESSIBILE ANTIVIBRANTE ACCIAIO INOX MF 1"1/4 A/F LUNGHEZZA 50 cm | 25051084 | Segrate (MI) | 1 pz | 16,15 | 16,15 | cad | 16,15 | 16,15 |  |
| I49b | Tubo flessibile inox / giunto antivibrante | FLESSIBILE ANTIVIBRANTE ACCIAIO INOX MF 1'' A/F LUNGHEZZA 40 CM PORTATA L/MIN 490 | 12092616 | Segrate (MI) | 1 pz | 7,83 | 7,83 | cad | 9,59 | 9,59 | ⚠ sostituisce 25017314 (giunto in gomma FF 1" non più a catalogo): flessibile inox MF 1" L 40 cm, non giunto in gomma FF |

### A · Idraulica - sicurezza

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I40a | Valvola di sicurezza 3 bar | VALVOLA SICUREZZA RBM 1/2'' MF 3 bar PED97/23/CE | 10034052 | Segrate (MI) | 1 pz | 13,07 | 13,07 | cad | 13,07 | 13,07 |  |
| I40b | Valvola di sicurezza 3 bar | VALVOLA SICUREZZA RBM 3/4'' MF 3 BAR CON MANOMETRO - PN10 | 10046860 | Segrate (MI) | 1 pz | 14,61 | 14,61 | cad | 14,61 | 14,61 |  |
| I41a | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 8 l Ø 200 mm | 10011741 | Segrate (MI) | 1 pz | 22,46 | 22,46 | cad | 22,46 | 22,46 |  |
| I41b | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO SANITARIO 12 L Ø 270 MM ATTACCO VERTICALE | 10011742 | Segrate (MI) | 1 pz | 23,36 | 23,36 | cad | 26,64 | 26,64 | sostituisce 25050885 (non più a catalogo); stesso articolo di I40 |
| I41c | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 25 l Ø 290 mm | 25111039 | Segrate (MI) | 1 pz | 32,87 | 32,87 | cad | 32,87 | 32,87 |  |
| I41d | Vaso di espansione chiuso a membrana per riscaldamento | VASO ESPANSIONE AQUAFILL RISCALDAMENTO E SANITARIO 18 l Ø 270 mm | 10011743 | Segrate (MI) | 1 pz | 29,84 | 29,84 | cad | 29,84 | 29,84 | a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| I42 | Vaso di espansione sanitario | VASO ESPANSIONE AQUAFILL RISCALDAMENTO SANITARIO 12 l Ø 270 mm | 10011742 | Segrate (MI) | 1 pz | 26,64 | 26,64 | cad | 26,64 | 26,64 |  |

### A · Idraulica - circolazione

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I50 | Circolatore elettronico | CIRCOLATORE ELETTRONICO MATRA HOT 25-6 INTERASSE 130 mm CON BOCCHETTONI | 25060502 | Segrate (MI) | 1 pz | 92,21 | 92,21 | cad | 92,21 | 92,21 |  |

### A · Idraulica - regolazione

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I51 | Valvola deviatrice 3 vie motorizzata | VALVOLA DEVIATRICE 3 VIE GIACOMINI R279B Ø 1'' ATTUATORE K270 220V | 25109732 | Segrate (MI) | 1 pz | 92,95 | 92,95 | cad | 88,93 | 88,93 |  |
| I52a | Valvola miscelatrice termostatica sanitaria | MISCELATORE TERMOSTATICO GIACOMINI DR156X004 F/F 3/4'' USO SANITARIO E SOLARE | 12102799 | Segrate (MI) | 1 pz | 49,78 | 49,78 | cad | 46,30 | 46,30 |  |
| I52b | Valvola miscelatrice termostatica sanitaria | MISCELATORE TERMOSTATICO GIACOMINI DR156X005 F/F 1 USO SANITARIO E SOLARE | 12102800 | Segrate (MI) | 1 pz | 53,91 | 53,91 | cad | 50,16 | 50,16 |  |

### A · Idraulica - trattamento

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I53 | Dosatore di polifosfati | DOSATORE POLIFOSFATI 1/2'' CON BYBASS ATTACCHI RUOTABILI E CARTUCCIA | 25084336 | Segrate (MI) | 1 pz | 17,87 | 17,87 | cad | 17,87 | 17,87 |  |
| I54 | Glicole propilenico / antigelo impianti | ANTIGELO FACOT ALIGEL A BASE DI GLICOLE MONOPROPILENICO | 25052255 | Segrate (MI) | 1 pz | 42,21 | 42,21 | cad | 42,21 | 42,21 |  |
| I55a | Additivo inibitore / pulitore per impianti | DECAPANTE FACOT FERRONEX PER IMPIANTI TERMICI NUOVI O RECENTI 1 l | 10016379 | Segrate (MI) | 1 pz | 10,82 | 10,82 | cad | 10,82 | 10,82 |  |
| I55b | Additivo inibitore / pulitore per impianti | FILMANTE FACOT FILMAX + THERMAKIL PER IMPIANTI TERMICI ALTA E BASSA TEMPERATURA E ANTIALGHE 1 l | 10016381 | Segrate (MI) | 1 pz | 12,70 | 12,70 | cad | 12,70 | 12,70 |  |

### A · Idraulica - isolamento

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I56 | Guaina isolante elastomerica sp. 9-13 mm | TUBO ISOLANTE IT-FLEX C1 Ø 22 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040200 | Segrate (MI) | 2 m | 4,71 | 2,35 | m | 4,71 | 2,355 |  |
| I57 | Guaina isolante elastomerica sp. 13-19 mm | TUBO ISOLANTE IT-FLEX C1 Ø 28 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040201 | Segrate (MI) | 2 m | 5,58 | 2,79 | m | 5,58 | 2,79 |  |
| I58 | Guaina isolante elastomerica sp. 13-19 mm | TUBO ISOLANTE IT-FLEX C1 Ø35 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 25091418 | Segrate (MI) | 2 m | 6,99 | 3,50 | m | 6,99 | 3,495 |  |
| I59 | Guaina isolante elastomerica sp. 19 mm | TUBO ISOLANTE IT-FLEX C1 Ø 42 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040204 | Segrate (MI) | 2 m | 7,98 | 3,99 | m | 7,98 | 3,99 |  |
| I61 | Nastro adesivo per isolante / colla | NASTRO ADESIVO IN ALLUMINIO ISOCELL FLEX ALU AA H 50 mm x 50 m | 25075683 | Segrate (MI) | 1 pz | 5,57 | 5,57 | cad | 5,57 | 5,57 |  |

### A · Idraulica - fissaggi

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I63 | Collare pesante con gommino e barra filettata M8 | COLLARI PER TUBI FRIULSIDER CON ASOLA Ø 1'' 2 PEZZI TASSELLO NYLON | 10062009 | Segrate (MI) | 2 pz | 2,21 | 1,10 | cad | 2,21 | 1,105 |  |
| I64 | Barra filettata M8 / M10 zincata | BARRA FILETTATA M8x1 m ACCIAIO ZINCATO BIANCO | 10066672 | Segrate (MI) | 1 pz | 1,07 | 1,07 | cad | 1,07 | 1,07 |  |
| I65 | Binario / profilo asolato zincato | PROFILO GRIP PF1 32x20x2,5 mm 2 m ACCIAIO DX51 DZ200 INTERASSE ASOLE 35 | 25013666 | Segrate (MI) | 1 pz | 13,11 | 13,11 | cad | 12,46 | 12,46 | Pro; pubblico 13,12 |
| I66 | Tassello ad espansione / chimico | TASSELLO IN ACCIAIO FISCHER FAZ II 12/10 Ø 12 mm 1 PEZZO PER CALCESTRUZZO | 12087276 | Segrate (MI) | 1 pz | 1,84 | 1,84 | cad | 1,75 | 1,75 | Pro; pubblico 1,84 |

### A · Idraulica - sigillanti

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I67a | Teflon / canapa / pasta sigillante / filo sigillante | CANAPA A FILO CON CONTENITORE 80 g | 10069812 | Segrate (MI) | 1 pz | 3,07 | 3,07 | cad | 3,07 | 3,07 |  |
| I67b | Teflon / canapa / pasta sigillante / filo sigillante | SIGILLANTE GAS E LIQUIDI PTFE FAREN 35S77 75 ml | 10062154 | Segrate (MI) | 1 pz | 8,16 | 8,16 | cad | 8,16 | 8,16 |  |

### A · Idraulica - condensa

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I69 | Sifone ispezionabile condensa | SIFONE SCARICO CONDENSA IDROSTILE IN PP MORSETTO Ø 46x32 mm | 12104501 | Segrate (MI) | 1 pz | 4,88 | 4,88 | cad | 4,88 | 4,88 |  |
| I70a | Tubo flessibile condensa / tubo cristal | TUBO RETEX Ø 16 mm ATOSSICO TRASPARENTE VENDITA AL METRO | 10063143 | Segrate (MI) | 1 m | 1,89 | 1,89 | m | 1,89 | 1,89 |  |
| I70b | Tubo flessibile condensa / tubo cristal | TUBO RETEX Ø 19 mm ATOSSICO TRASPARENTE VENDITA AL METRO | 10063144 | Segrate (MI) | 1 m | 2,79 | 2,79 | m | 2,79 | 2,79 |  |

### A · Idraulica - supporti macchina

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| I71a | Basamento antivibrante in gomma per unità esterna | GOMMA ANTIVIBRANTE 100x100x5 mm NERO 4 PEZZI | 25013860 | Segrate (MI) | 4 pz | 6,48 | 1,62 | cad | 6,48 | 1,62 |  |
| I72a | Staffe a muro per unità esterna | STAFFE UNIVERSALI CLOCK 420x400x780 mm PORTATA 120 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062345 | Segrate (MI) | 1 pz | 11,89 | 11,89 | cad | 11,89 | 11,89 |  |
| I72b | Staffe a muro per unità esterna | STAFFE UNIVERSALI CLOCK 465x400x780 mm PORTATA 160 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062346 | Segrate (MI) | 1 pz | 16,31 | 16,31 | cad | 16,31 | 16,31 |  |

### A · Frigorifero - linee

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| F01a | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 1/4''x 1 mm GUAINA - vendita al ml | 25022912 | Segrate (MI) | 1 m | 4,16 | 4,16 | m | 4,16 | 4,16 |  |
| F01b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 3/8''x 1 mm GUAINA - vendita al ml | 25022913 | Segrate (MI) | 1 m | 6,52 | 6,52 | m | 6,52 | 6,52 |  |
| F02b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 1/2''x 1 mm GUAINA - vendita al ml | 25022914 | Segrate (MI) | 1 m | 8,43 | 8,43 | m | 8,43 | 8,43 |  |
| F03b | Coppia tubi rame preisolati | TUBO RAME RIVESTITO CLIMA ZETAESSE CUPEX GEL SILVER Ø 5/8''x 1 mm GUAINA 9 mm - vendita al ml | 25022931 | Segrate (MI) | 1 m | 10,80 | 10,80 | m | 10,80 | 10,80 |  |
| F06 | Nastro di finitura per linee frigorifere | NASTRO ADESIVO PVC ISOLANTE ALTEZZA 5 cm LUNGHEZZA 20 m NERO | 10016397 | Segrate (MI) | 1 pz | 2,75 | 2,75 | cad | 2,75 | 2,75 |  |

### A · Frigorifero - condensa

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| F10a | Pompa scarico condensa | POMPA DI SCARICO CONDENSA TECOM DPC40 PORTATA MASSIMA 40 l PREVALENZA MAX 20 m | 25011135 | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad | 56,56 | 56,56 |  |

### A · Frigorifero - supporti

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| F11a | Staffe a muro per unità esterna split | STAFFE UNIVERSALI CLOCK 420x400x780 mm PORTATA 120 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062345 | Segrate (MI) | 1 pz | 11,89 | 11,89 | cad | 11,89 | 11,89 |  |
| F11b | Staffe a muro per unità esterna split | STAFFE UNIVERSALI CLOCK 465x400x780 mm PORTATA 160 kg FORNITA CON GOMMINI ANTIVIBRANTI IN PVC | 10062346 | Segrate (MI) | 1 pz | 16,31 | 16,31 | cad | 16,31 | 16,31 |  |

### A · Aeraulica - canali

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| A02a | Tubo flessibile non isolato alluminio | TUBO FLESSIBILE Ø 150 mm ESTENSIBILE IN ALLUMINIO NATURALE L 850 - 3000 mm SPESSORE 0,12 mm | 10042850 | Segrate (MI) | 1 pz | 16,19 | 16,19 | cad | 16,19 | 16,19 |  |

### A · Aeraulica - accessori

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| A07a | Nastro alluminio / fascette stringitubo | NASTRO ADESIVO IN ALLUMINIO ISOCELL FLEX ALU AA H 50 mm x 50 m SPESSORE 30 µm | 25075683 | Segrate (MI) | 1 pz | 5,57 | 5,57 | cad | 5,57 | 5,57 |  |
| A07b | Nastro alluminio / fascette stringitubo | FASCETTE STRINGITUBO ACCIAIO INOX AISI 304 Ø 44-56 mm 2 PEZZI | 10055474 | Segrate (MI) | 2 pz | 3,40 | 1,70 | cad | 3,40 | 1,70 |  |

### A · Elettrico - cavi

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E01 | Cavo FG16OR16 0,6/1 kV | CAVO TRIPOLARE FG16(O)R16 0,6/1 kV SEZIONE 3G2,5 mmq COLORE GRIGIO MATASSA 50m | 10073623 | Segrate (MI) | 50 m | 64,75 | 1,29 | m | 64,75 | 1,295 |  |
| E04 | Cavo FG16OR16 0,6/1 kV | CAVO PENTAPOLARE FG16(O)R16 0,6/1 kV SEZIONE 5G2,5 mmq COLORE GRIGIO MATASSA 100m | 10073630 | Segrate (MI) | 100 m | 220,49 | 2,20 | m | 220,49 | 2,205 |  |
| E06 | Cavo FG16OR16 0,6/1 kV | CAVO PENTAPOLARE FG16(O)R16 0,6/1 kV SEZIONE 5G6 mmq COLORE GRIGIO MATASSA 50m | 25060082 | Segrate (MI) | 50 m | 253,28 | 5,07 | m | 253,28 | 5,066 |  |
| E07 | Cordina FS17 450/750 V | CAVO UNIPOLARE FS17 CPR 450/750 SEZIONE 1x4 mmq COLORE NERO MATASSA 100 m | 10073509 | Segrate (MI) | 100 m | 60,57 | 0,61 | m | 60,57 | 0,606 |  |
| E08 | Cordina FS17 450/750 V | CAVO UNIPOLARE FS17 CPR 450/750 SEZIONE 1x6 mmq COLORE NERO MATASSA 100 m | 10073514 | Segrate (MI) | 100 m | 83,61 | 0,84 | m | 83,61 | 0,836 |  |
| E09a | Cavo segnale / bus schermato | CAVO FRO-H2HP-OB 2x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014566 | Segrate (MI) | 100 m | 57,79 | 0,58 | m | 69,67 | 0,697 |  |
| E09b | Cavo segnale / bus schermato | CAVO FRO-H2HP-OB 4x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014575 | Segrate (MI) | 100 m | 84,43 | 0,84 | m | 97,54 | 0,975 |  |
| E10 | Cavo FROR (comandi) | CAVO FROR 4x0,50 mmq CAVO ANTIFIAMMA CPR GRIGIO MATASSA 100 m | 12097160 | Segrate (MI) | 100 m | 97,54 | 0,98 | m | 97,54 | 0,975 |  |

### A · Elettrico - vie cavi

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E11a | Tubo corrugato flessibile | TUBO CORRUGATO SEMPLE' ELEKTRIK Ø 25 mm COLORE NERO MATASSA 50 m | 25062264 | Segrate (MI) | 50 m | 21,11 | 0,42 | m | 21,11 | 0,422 |  |
| E11b | Tubo corrugato flessibile | TUBO CORRUGATO GEWISS NERO Ø 32 mm MATASSA 50 m | 12103297 | Segrate (MI) | 50 m | 48,36 | 0,97 | m | 38,88 | 0,778 | Pro; pubblico 41,81 |
| E12a | Tubo rigido PVC con raccordi | TUBO RIGIDO GRIGIO GEWISS Ø 25 mm LUNGHEZZA 3 m | 10044194 | Segrate (MI) | 3 m | 4,02 | 1,34 | m | 3,61 | 1,203 | Pro; pubblico 4,01 |
| E12b | Tubo rigido PVC con raccordi | TUBO RIGIDO GRIGIO GEWISS Ø 32 mm LUNGHEZZA 3 m | 10044196 | Segrate (MI) | 3 m | 5,82 | 1,94 | m | 5,24 | 1,747 | Pro; pubblico 5,82 |
| E13a | Canala portacavi PVC con accessori | CANALE UFFICIO ARNOCANALI A 2 SCOMPARTI IN PVC 60x40mm LUNGHEZZA 2m GRIGIO | 12102678 | Segrate (MI) | 2 m | 7,01 | 3,50 | m | 7,01 | 3,505 |  |
| E14a | Guaina spiralata / raccordi guaina IP65 | 2 RACCORDI TUBO-GUAINA Ø 25 mm PVC IP67 BM | 25037261 | Segrate (MI) | 2 pz | 1,35 | 0,68 | cad | 1,35 | 0,675 |  |
| E14b | Guaina spiralata / raccordi guaina IP65 | 2 RACCORDI TUBO-GUAINA Ø 32 mm PVC IP67 BM | 25037266 | Segrate (MI) | 2 pz | 1,93 | 0,96 | cad | 1,93 | 0,965 |  |

### A · Elettrico - protezioni

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E15a | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO ABB DIFFERENZIALE 2P PROTETTI 16A 4,5 kA CURVA C 0,03A | 10072117 | Segrate (MI) | 1 pz | 32,70 | 32,70 | cad | 31,07 | 31,07 | Pro; pubblico 32,70 |
| E16a | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 20A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008032 | Segrate (MI) | 1 pz | 18,44 | 18,44 | cad | 15,49 | 15,49 | Pro; pubblico 17,21 |
| E16b | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 25A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008046 | Segrate (MI) | 1 pz | 18,44 | 18,44 | cad | 15,49 | 15,49 | Pro; pubblico 17,21 |
| E17 | Interruttore magnetotermico differenziale 1P+N 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 32A 4,5KA 30mA 2 MODULI 230V CLASSE A | 25008050 | Segrate (MI) | 1 pz | 18,44 | 18,44 | cad | 15,49 | 15,49 | Pro; pubblico 17,21 · a Segrate «disponibile a breve» (prezzo comunque mostrato) |
| E18a | Interruttore magnetotermico differenziale 4P 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO TECNOLINE DIFFERENZIALE 4P 16A TIPO A 30mA 10KA 5 MODULI | 25116915 | Segrate (MI) | 1 pz | 61,48 | 61,48 | cad | 61,48 | 61,48 |  |
| E18b | Interruttore magnetotermico differenziale 4P 30 mA tipo A | INTERRUTTORE MAGNETOTERMICO TECNOLINE DIFFERENZIALE 4P 20A TIPO A 30mA 10KA 415V 5 MODULI | 25116931 | Segrate (MI) | 1 pz | 61,48 | 61,48 | cad | 61,48 | 61,48 |  |
| E19a | Interruttore magnetotermico 1P+N | INTERRUTTORE MAGNETOTERMICO CHINT 10A 1P+N CURVA C 4,5KA 1 MODULO | 25008045 | Segrate (MI) | 1 pz | 4,84 | 4,84 | cad | 4,06 | 4,06 | Pro; pubblico 4,51 |
| E19b | Interruttore magnetotermico 1P+N | INTERRUTTORE MAGNETOTERMICO CHINT 16A 1P+N CURVA C 4,5KA 1 MODULO | 25008041 | Segrate (MI) | 1 pz | 4,84 | 4,84 | cad | 4,06 | 4,06 | Pro; pubblico 4,51 |
| E20 | Interruttore magnetotermico 4P | INTERRUTTORE MAGNETOTERMICO TECNOLINE 4P 32A 10KA 415V 4 MODULI | 25116927 | Segrate (MI) | 1 pz | 97,54 | 97,54 | cad | 16,56 | 16,56 | ⚠ sostituisce 25062710 (AEG, 97,54): curva non dichiarata in scheda (la variante D è a codice separato 25127507), da verificare C |
| E21a | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO CHINT 2P 25A 30mA TIPO AC 2 MODULI | 25008031 | Segrate (MI) | 1 pz | 16,31 | 16,31 | cad | 14,68 | 14,68 | Pro; pubblico 16,31 |
| E21b | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO TECNOLINE 2P 40A 30mA 230/240VAC TIPO A 2 MODULI | 25127450 | Segrate (MI) | 1 pz | 14,34 | 14,34 | cad | 14,34 | 14,34 | a Segrate su ordinazione |
| E21c | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO TECNOLINE 4P 40A 30mA 400/415VAC TIPO A 4 MODULI | 25127438 | Segrate (MI) | 1 pz | 24,51 | 24,51 | cad | 24,51 | 24,51 | a Segrate su ordinazione |
| E21d | Interruttore differenziale puro 2P / 4P 30 mA tipo A | DIFFERENZIALE PURO ABB 4P 25A | 25007415 | Segrate (MI) | 1 pz | 77,87 | 77,87 | cad | 77,87 | 77,87 |  |
| E22a | Scaricatore di sovratensioni | SCARICATORE DI SOVRATENSIONE FINDER 2P 230V SPD TIPO II 1P+N | 25003353 | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad | 56,56 | 56,56 |  |
| E22b | Scaricatore di sovratensioni | SCARICATORE DI SOVRATENSIONE FINDER 4P 230/400V TRIFASE CON INDICATORE DI GUASTO | 25003355 | Segrate (MI) | 1 pz | 97,54 | 97,54 | cad | 97,54 | 97,54 |  |

### A · Elettrico - sezionamento

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E23a | Sezionatore / interruttore rotativo in cassetta IP65 bordo macchina | SEZIONATORI DI MANOVRA 32A 4 poli IN CASSETTA CON MANIGLIA GIALLO/ROSSA | 12085434 | Segrate (MI) | 1 pz | 23,24 | 23,24 | cad | 23,24 | 23,24 |  |

### A · Elettrico - quadri

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E24a | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 8 MODULI IP65 | 10040848 | Segrate (MI) | 1 pz | 9,14 | 9,14 | cad | 9,14 | 9,14 |  |
| E24b | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 12 MODULI IP65 | 10040850 | Segrate (MI) | 1 pz | 16,48 | 16,48 | cad | 16,48 | 16,48 |  |
| E24c | Centralino da parete IP65 con portella | CENTRALINO SARTEL DA PARETE STAGNO 24 MODULI IP65 | 10040851 | Segrate (MI) | 1 pz | 27,79 | 27,79 | cad | 27,79 | 27,79 |  |
| E25a | Centralino da incasso | CENTRALINO SARTEL INCASSO 8 MODULI CON PORTELLO BIANCO IP40 | 25011885 | Segrate (MI) | 1 pz | 7,79 | 7,79 | cad | 7,79 | 7,79 |  |
| E25b | Centralino da incasso | CENTRALINO SARTEL INCASSO 12 MODULI CON PORTELLO BIANCO IP40 | 25011888 | Segrate (MI) | 1 pz | 10,70 | 10,70 | cad | 10,70 | 10,70 |  |
| E26a | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 100x100x50 mm PARETI LISCE IP55 | 25011797 | Segrate (MI) | 1 pz | 5,33 | 5,33 | cad | 5,33 | 5,33 |  |
| E26b | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 150x110x70 mm PARETI LISCE IP55 | 25011789 | Segrate (MI) | 1 pz | 7,79 | 7,79 | cad | 7,79 | 7,79 |  |
| E26c | Scatola di derivazione IP55/IP65 | SCATOLA GEWISS DI DERIVAZIONE ESTERNA 190x140x70 mm PARETI LISCE IP55 | 25011795 | Segrate (MI) | 1 pz | 14,34 | 14,34 | cad | 14,34 | 14,34 |  |

### A · Elettrico - accessori

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E27a | Pressacavo IP68 | PRESSACAVO CON DADO PG21 IP68 5 PEZZI DOPPIA GUARNIZIONE | 12099464 | Segrate (MI) | 5 pz | 3,77 | 0,75 | cad | 3,77 | 0,754 |  |
| E27b | Pressacavo IP68 | PRESSACAVO CON DADO PG16 IP68 5 PEZZI DOPPIA GUARNIZIONE | 12099463 | Segrate (MI) | 5 pz | 1,97 | 0,39 | cad | 1,97 | 0,394 |  |
| E28a | Morsetti a leva / morsettiera / capicorda | 5 CONNETTORI A LEVE CABLO 2X4 MM² 2 VIE 600V 32A | 10074717 | Segrate (MI) | 5 pz | 1,64 | 0,33 | cad | 1,64 | 0,328 |  |
| E28b | Morsetti a leva / morsettiera / capicorda | 5 CONNETTORI A LEVE CABLO 3 VIE 600V 32A | 10073777 | Segrate (MI) | 5 pz | 1,93 | 0,39 | cad | 1,93 | 0,386 |  |

### A · Elettrico - comando

| ID | Voce | Articolo (oggi) | Codice Tecnomat | Negozio | Confezione | Netto conf. € oggi | Netto/UM € oggi | UM | Netto conf. € Pro | Netto/UM € Pro | Note |
|---|---|---|---|---|---|--:|--:|---|--:|--:|---|
| E30a | Termostato / cronotermostato ambiente | CRONOTERMOSTATO BPT SETTIMANALE WIFI 220V/240V DA PARETE | 25079387 | Segrate (MI) | 1 pz | 56,56 | 56,56 | cad | 56,56 | 56,56 |  |
| E30b | Termostato / cronotermostato ambiente | TERMOSTATO AMBIENTE ARISTON CUBE ROOM A FILO 3319116 | 25012760 | Segrate (MI) | 1 pz | 64,75 | 64,75 | cad | 54,30 | 54,30 | Pro; pubblico 56,56 |

---

## Parte B — da trovare (62 articoli)

Si cerca **per voce**, con quello che la colonna «Che cosa deve rispettare» dice. «Oggi» è il prezzo che il conto usa
adesso, e di chi è (un altro fornitore, o un riferimento online): è l'ordine di grandezza da battere.

### B1 · Le 30 voci della commessa PR.MI.059 (prima queste)

| ID | Voce | Che cosa deve rispettare | Oggi (il prezzo che il conto usa) | Articolo | Codice Tecnomat | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|---|--:|--:|---|---|
| A01c | Tubo flessibile isolato per aria, rotolo 10 m, Ø200 | condotto flessibile coibentato Ø200 (isolamento 25 mm, barriera vapore), al metro o rotolo 10 m | Idrosanitaria 6,90 €/m |  |  |  |  |  |  |  | non trovato (a catalogo solo flessibili isolati Ø80 25072442 e Ø100 25072441) |
| A06c | Plenum porta-bocchetta 400×200, attacco Ø200 | plenum porta-bocchetta 400×200, attacco Ø200 **laterale**, coibentato | Idrosanitaria 30,81 €/cad |  |  |  |  |  |  |  | non trovato |
| A07c | Fascetta stringitubo inox 60–270 mm | fascetta stringitubo inox per Ø200 (anima e mantello) | Idrosanitaria 1,82 €/cad | FASCETTA STRINGITUBO Ø20 cm INOX (collare di fissaggio Ø200) | 25097787 | Segrate (MI) | 1 pz | 2,34 | 2,34 | cad |  |
| A08c | Collare di fissaggio isolato Ø200 | collare o fascia di sostegno per flessibile Ø200 | Idrosanitaria 3,60 €/cad | FASCETTA STRINGITUBO Ø20 cm INOX (collare di fissaggio Ø200) | 25097787 | Segrate (MI) | 1 pz | 2,34 | 2,34 | cad | stesso articolo di A07c |
| E02 | Cavo FG16OR16 0,6/1 kV 3G4, 3G4 | cavo FG16OR16 0,6/1 kV 3G4, al metro | riferimento online 2,28 €/m |  |  |  |  |  |  |  | non trovato |
| E03 | Cavo FG16OR16 0,6/1 kV 3G6, 3G6 | cavo FG16OR16 0,6/1 kV 3G6, al metro | riferimento online 3,32 €/m |  |  |  |  |  |  |  | non trovato |
| E33 | Interruttore magnetotermico differenziale 1P+N C10 30 mA tipo A, C10 | magnetotermico differenziale 1P+N C10, 30 mA, **tipo A** | riferimento online 18,61 €/cad | INTERRUTTORE MAGNETOTERMICO CHINT DIFFERENZIALE 1P+N 10A 30 mA CLASSE A | 25008049 | Segrate (MI) | 1 pz | 15,49 | 15,49 | cad | Pro; pubblico 17,21 · curva non indicata nel titolo |
| E35a | Cavo FG16OR16 0,6/1 kV, 3G1,5 | cavo FG16OR16 0,6/1 kV 3G1,5, al metro | riferimento online 0,99 €/m | CAVO FG16(O)R16 0,6/1 kV SEZIONE 3G1,5 mmq COLORE GRIGIO MATASSA 100 m | 10073622 | Segrate (MI) | 100 m | 97,54 | 0,975 | m | alternativa matassa 50 m (10073621) 56,56 = 1,131 €/m |
| E35c | Cavo FG16OR16 0,6/1 kV, 4G1,5 | cavo FG16OR16 0,6/1 kV 4G1,5, al metro | riferimento online 1,30 €/m | CAVO FG16(O)R16 0,6/1 kV SEZIONE 4G1,5 mmq COLORE GRIGIO MATASSA 100 m | 10073627 | Segrate (MI) | 100 m | 110,66 | 1,107 | m |  |
| E36 | Cavo schermato per sonde FR2OH2R16 / FROHH2R, 2×0,75 | cavo schermato 2×0,75 per sonde e bus, al metro | riferimento online 0,78 €/m | CAVO FRO-H2HP-OB 2x0,50 mmq SCHERMATO CPR CCA-S3-D1-A3 MATASSA DA 100 m | 25014566 | Segrate (MI) | 100 m | 69,67 | 0,697 | m | ⚠ sezione 2×0,50 (la voce: 2×0,75) |
| E37 | Scatola da incasso 503, 3 moduli | scatola da incasso 503 | riferimento online 0,26 €/cad | SCATOLA INCASSO KML 3 MODULI | 12085813 | Segrate (MI) | 1 pz | 0,25 | 0,25 | cad |  |
| I44 | Manometro radiale/assiale 0-6 bar | fondo scala 0–6 bar, attacco radiale ½" (il 0–12 della parte A non va) | Idrosanitaria 9,84 €/cad | MANOMETRO POSTERIORE FERRARI 0-6 BAR ATTACCO 1/4" | 25004117 | Segrate (MI) | 1 pz | 3,81 | 3,81 | cad | ⚠ attacco posteriore ¼" (la voce: radiale ½") |
| I47 | Gruppo di riempimento automatico | gruppo di riempimento ½" **con disconnettore** (il Filler della parte A non ce l'ha) | Idrosanitaria 153,01 €/cad | DISCONNETTORE CILLIT HFB 1/2"-3/4" CON RIDUTTORE (gruppo di riempimento) | 25036575 | Segrate (MI) | 1 pz | 254,57 | 254,57 | cad | Pro; pubblico 270,82 · su ordinazione · alternativa senza disconnettore: Honeywell V06F 25005259 a 48,51 (non conforme) |
| I68a | Tubo di scarico condensa Ø32 / Ø40 con raccordi, Ø32 PP (HT) barra 2 m | tubo rigido per scarico condensa Ø32 (PVC o PP) | Idrosanitaria 2,38 €/m | TUBO COES Ø32 mm 1 BICCHIERE HTEM L2000 mm IN PP GRIGIO | 10009262 | Segrate (MI) | 2 m | 3,57 | 1,785 | m |  |
| I68d | Tubo di scarico condensa Ø32 / Ø40 con raccordi, curva Ø32 87°/45° | curva 87°–90° Ø32 | Idrosanitaria 3,69 €/cad | CURVA COES Ø32 mm HTB 87,5° IN PP GRIGIO | 10009270 | Segrate (MI) | 1 pz | 0,75 | 0,75 | cad |  |
| I68f | Tubo di scarico condensa Ø32 / Ø40 con raccordi, manicotto Ø32 | manicotto Ø32 | Idrosanitaria 2,60 €/cad | MANICOTTO SCORREVOLE 2 BICCHIERI Ø 32 mm | 10045956 | Segrate (MI) | 1 pz | 1,15 | 1,15 | cad |  |
| I74 | Gruppo di sicurezza sanitario per bollitore, ¾" | gruppo di sicurezza per bollitore: ritegno, valvola 6 bar, intercettazione | Idrosanitaria 26,05 €/cad | GRUPPO DI SICUREZZA UNIVAL 3/4" TARATURA 7 BAR | 10059049 | Segrate (MI) | 1 pz | 20,30 | 20,30 | cad | ⚠ taratura 7 bar (la voce: 6 bar) |
| I77 | Rubinetto portamanometro a tre vie, ½" | rubinetto portamanometro a tre vie, attacco ½" | Idrosanitaria 8,95 €/cad |  |  |  |  |  |  |  | non trovato |
| I78a | Riduzione filettata in ottone M × F, 1¼" × 1" | riduzione 1¼" M × 1" F | Idrosanitaria 1,44 €/cad | RIDUZIONE OTTONE MF 1"1/4 x 1" | 25018599 | Segrate (MI) | 1 pz | 3,15 | 3,15 | cad |  |
| I81c | Raccordo diritto a pressare M × multistrato, ½" × 16 | raccordo diritto a pressare M ½" × multistrato 16 | Abbattista 1,81 €/cad | RACCORDO PRESS FIT GIACOMINI MULTISTRATO DRITTO M 1/2'' x Ø 16 mm | 12092747 | Segrate (MI) | 1 pz | 2,10 | 2,10 | cad |  |
| I82 | Guaina elastomerica sp. 32 mm, tubo Ø35 | guaina elastomerica, spessore 32 mm (o 30), foro 35 (multistrato 32) | Idrosanitaria 3,94 €/m | TUBO ISOLANTE IT-FLEX C1 Ø35 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 25091418 | Segrate (MI) | 2 m | 6,99 | 3,495 | m | ⚠ spessore 19 mm (la voce: 32 mm o 30) |
| I83b | Nipplo in ottone | nipplo ¾" M × M (ottone o ghisa zincata) | Idrosanitaria 1,09 €/cad | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 3/4" CONFORME USO ACQUA E GAS | 25018205 | Segrate (MI) | 1 pz | 0,95 | 0,95 | cad |  |
| I83c | Nipplo in ottone | nipplo 1" M × M (ottone o ghisa zincata) | Idrosanitaria 1,57 €/cad | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1" CONFORME USO ACQUA E GAS | 25018203 | Segrate (MI) | 1 pz | 1,19 | 1,19 | cad |  |
| I83e | Nipplo ridotto 1¼" × 1" | nipplo ridotto 1¼" × 1" M × M | Idrosanitaria 3,12 €/cad | RACCORDO GHISA BERG MONTANA FIGURA 245 NIPPLE RIDOTTO 1"1/4 X 1" CONFORME USO ACQUA E GAS | 25018245 | Segrate (MI) | 1 pz | 2,29 | 2,29 | cad |  |
| I84a | Guaina isolante elastomerica sp. 9 mm per tubo 26 | guaina elastomerica, spessore 9 mm, foro 28 (tubo multistrato 26) | Idrosanitaria 0,51 €/m | TUBO ISOLANTE POLAR 10 Ø 27 mm SPESSORE 10 mm BARRA 2 m | 10017684 | Segrate (MI) | 2 m | 2,22 | 1,11 | m | ⚠ foro 27, spessore 10 (la voce: foro 28, spessore 9) |
| I84b | Guaina isolante elastomerica sp. 9 mm per tubo 32 | guaina elastomerica, spessore 9 mm, foro 35 (multistrato 32 e tubo condensa 32) | Idrosanitaria 0,59 €/m | TUBO ISOLANTE POLAR 10 Ø 34 mm SPESSORE 10 mm BARRA 2 m | 10017686 | Segrate (MI) | 2 m | 2,45 | 1,225 | m | ⚠ foro 34, spessore 10 (la voce: foro 35, spessore 9) |
| I84c | Guaina isolante elastomerica sp. 32 mm per tubo 26 | guaina elastomerica, spessore 32 mm (o 30), foro 28 (multistrato 26) | Idrosanitaria 3,50 €/m | TUBO ISOLANTE IT-FLEX C1 Ø 28 SPESSORE 19 mm ELASTOMERICO CLASSE 1 | 10040201 | Segrate (MI) | 2 m | 5,58 | 2,79 | m | ⚠ spessore 19 mm (la voce: 32 mm o 30) |
| I85 | Collante per tubo di scarico condensa rigido | collante per PVC o tubo condensa rigido | Idrosanitaria 13,65 €/cad | COLLA TANGIT PER PVC-U 125 g | 10027398 | Segrate (MI) | 1 pz | 7,30 | 7,30 | cad |  |
| I86 | Braga 45° Ø40/32 in PP | braga 45° Ø40 con innesto Ø32 | Idrosanitaria 1,16 €/cad | BRAGA COES Ø40x32 mm RIDOTTA HTEA 45° IN PP GRIGIO | 10009291 | Segrate (MI) | 1 pz | 2,42 | 2,42 | cad |  |
| I87 | Clip di fissaggio per tubo condensa rigido | clip o collare per tubo condensa Ø32 | Idrosanitaria 0,40 €/cad | COLLARE DI FISSAGGIO TUBI SCARICO Ø32 - 40 - 50 mm | 10021502 | Segrate (MI) | 1 pz | 1,60 | 1,60 | cad | confezione non indicata in scheda: assunto 1 pz |

### B2 · Le altre 32 voci della distinta

| ID | Voce | Che cosa deve rispettare | Oggi (il prezzo che il conto usa) | Articolo | Codice Tecnomat | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |
|---|---|---|---|---|---|---|---|--:|--:|---|---|
| A01a | Tubo flessibile isolato per aria, rotolo 10 m, Ø125 | condotto flessibile coibentato Ø125, rotolo 10 m | riferimento online 5,95 €/m |  |  |  |  |  |  |  | non trovato |
| A01b | Tubo flessibile isolato per aria, rotolo 10 m, Ø160 | condotto flessibile coibentato Ø160, rotolo 10 m | riferimento online 7,33 €/m |  |  |  |  |  |  |  | non trovato |
| A04a | Bocchetta di mandata a doppio filare di alette, 300x100 | bocchetta di mandata 300×100 a doppio filare di alette, con serranda | riferimento online 18,85 €/cad |  |  |  |  |  |  |  | non trovato |
| A04b | Bocchetta di mandata a doppio filare di alette, 400x150 | bocchetta di mandata 400×150 a doppio filare di alette, con serranda | riferimento online 24,57 €/cad |  |  |  |  |  |  |  | non trovato |
| A05a | Griglia di ripresa con filtro, 400x200 | griglia di ripresa 400×200 | riferimento online 46,88 €/cad |  |  |  |  |  |  |  | non trovato |
| A05b | Griglia di ripresa con filtro, 600x300 | griglia di ripresa 600×300 | riferimento online 60,86 €/cad |  |  |  |  |  |  |  | non trovato |
| A06a | Plenum porta-bocchetta, 300x100 | plenum porta-bocchetta 300×100, coibentato | riferimento online 21,95 €/cad |  |  |  |  |  |  |  | non trovato |
| A06b | Plenum porta-bocchetta, 400x150 | plenum porta-bocchetta 400×150, coibentato | riferimento online 30,69 €/cad |  |  |  |  |  |  |  | non trovato |
| E05 | Cavo FG16OR16 0,6/1 kV 5G4, 5G4 | cavo FG16OR16 0,6/1 kV 5G4, al metro | riferimento online 3,77 €/m |  |  |  |  |  |  |  | non trovato |
| E31a | Interruttore magnetotermico differenziale tipo B, 1P+N 30 mA, C16–C32 | magnetotermico differenziale 1P+N, 30 mA, **tipo B**, C16–C32 | riferimento online 87,73 €/cad |  |  |  |  |  |  |  | non trovato |
| E34 | Relè modulare su guida DIN, bobina 230 V, contatto 20 A | relè modulare su guida DIN, bobina 230 V, contatto 16–20 A | riferimento online 19,45 €/cad | CONTATTORE 230 V 20 A ABB | 10026879 | Segrate (MI) | 1 pz | 23,77 | 23,77 | cad | ⚠ contattore, non relè modulare (la voce); la scheda non indica il montaggio su guida DIN |
| E35b | Cavo FG16OR16 0,6/1 kV, 2×1,5 | cavo FG16OR16 0,6/1 kV 2×1,5, al metro | riferimento online 0,78 €/m |  |  |  |  |  |  |  | non trovato |
| F09i | Dadi a cartella e giunzioni per rame, manicotto a brasare 1/4" | manicotto a brasare per rame 1/4" | riferimento online 0,75 €/cad |  |  |  |  |  |  |  | non trovato |
| F09j | Dadi a cartella e giunzioni per rame, manicotto a brasare 3/8" | manicotto a brasare per rame 3/8" | riferimento online 2,20 €/cad |  |  |  |  |  |  |  | non trovato |
| I39a | Separatore d'aria (disaeratore), 1" | separatore d'aria (disaeratore) 1" | riferimento online 96,83 €/cad |  |  |  |  |  |  |  | non trovato |
| I39b | Separatore d'aria (disaeratore), 1"1/4 | separatore d'aria (disaeratore) 1¼" | riferimento online 167,58 €/cad |  |  |  |  |  |  |  | non trovato |
| I41e | Vaso di espansione per riscaldamento, 35 l | vaso di espansione riscaldamento 35 l | riferimento online 68,85 €/cad |  |  |  |  |  |  |  | non trovato (a catalogo solo il 50 l Aquasystem sanitario/autoclave 25050944, non per riscaldamento) |
| I41f | Vaso di espansione per riscaldamento, 50 l | vaso di espansione riscaldamento 50 l | riferimento online 89,34 €/cad |  |  |  |  |  |  |  | non trovato (a catalogo solo il 50 l Aquasystem sanitario/autoclave 25050944, non per riscaldamento) |
| I68c | Tubo di scarico condensa Ø32 / Ø40 con raccordi, Ø40 PVC arancio barra 2 m | tubo per scarico condensa Ø40 | riferimento online 2,28 €/m | TUBO Ø 40 mm 3 m ARANCIO | 10035941 | Segrate (MI) | 3 m | 5,41 | 1,803 | m | alternativa barra 1 m (10035932) 2,01 €/m |
| I68e | Tubo di scarico condensa Ø32 / Ø40 con raccordi, curva Ø40 87°/45° | curva 87°–90° Ø40 | riferimento online 0,64 €/cad | CURVA 87° Ø 40 mm PVC ARANCIO | 10035540 | Segrate (MI) | 1 pz | 0,37 | 0,37 | cad |  |
| I68g | Tubo di scarico condensa Ø32 / Ø40 con raccordi, manicotto Ø40 | manicotto Ø40 | riferimento online 1,39 €/cad | GIUNTO DI RIPARAZIONE Ø 40 mm PVC ARANCIO | 12082231 | Segrate (MI) | 1 pz | 5,16 | 5,16 | cad | ⚠ giunto di riparazione, non manicotto semplice |
| I73a | Valvola antigelo per pompa di calore, 1" | valvola antigelo per pompa di calore 1" | riferimento online 77,38 €/cad |  |  |  |  |  |  |  | non trovato |
| I73b | Valvola antigelo per pompa di calore, 1¼" | valvola antigelo per pompa di calore 1¼" | riferimento online 86,95 €/cad |  |  |  |  |  |  |  | non trovato |
| I75 | Valvola a sfera FF a passaggio totale, ½" | valvola a sfera ½" FF a passaggio totale, con leva | Abbattista 4,48 €/cad | VALVOLA A SFERA PER ACQUA ENOLGAS SERIE ATOMIC CON LEVA FF 1/2 PN25 | 25017114 | Segrate (MI) | 1 pz | 3,57 | 3,57 | cad | passaggio totale non verificato in scheda |
| I76 | Pozzetto portasonda in ottone, ½" | pozzetto portasonda ½" in ottone | riferimento online 12,66 €/cad |  |  |  |  |  |  |  | non trovato |
| I78b | Riduzione filettata in ottone M × F, 1" × ¾" | riduzione 1" M × ¾" F | riferimento online 3,41 €/cad | RIDUZIONE OTTONE MF 1" x 3/4" | 25018605 | Segrate (MI) | 1 pz | 1,70 | 1,70 | cad |  |
| I80a | Valvola miscelatrice a tre vie con servomotore 230 V, ¾" | valvola miscelatrice a tre vie ¾" con servomotore 230 V | riferimento online 180,17 €/cad |  |  |  |  |  |  |  | non trovato |
| I80b | Valvola miscelatrice a tre vie con servomotore 230 V, 1" | valvola miscelatrice a tre vie 1" con servomotore 230 V | riferimento online 181,00 €/cad |  |  |  |  |  |  |  | non trovato |
| I81a | Gomito a pressare multistrato, 16×2 | gomito a pressare multistrato 16×2 | riferimento online 3,47 €/cad | RACCORDO PRESSFIT APE APL GOMITO Ø 16 x Ø 16 mm PRESSATURA TH-H-U TUBO | 25000740 | Segrate (MI) | 1 pz | 2,65 | 2,65 | cad |  |
| I81b | Manicotto a pressare multistrato, 16×2 | manicotto a pressare multistrato 16×2 | Idrosanitaria 2,14 €/cad | RACCORDO PRESS FIT GIACOMINI MULTISTRATO MANICOTTO Ø 16x16 mm PROFILO PRESSATURA TH-H-U | 12092781 | Segrate (MI) | 1 pz | 3,34 | 3,34 | cad |  |
| I83a | Nipplo in ottone | nipplo ½" M × M | Bricoman 1,02 €/cad | RACCORDO GHISA BERG MONTANA FIGURA 280 NIPPLE 1/2" CONFORME USO ACQUA E GAS | 25018214 | Segrate (MI) | 1 pz | 0,78 | 0,78 | cad |  |
| I83d | Nipplo ridotto in ottone | nipplo ridotto 1" × ¾" M × M | Bricoman 2,21 €/cad | RACCORDO GHISA BERG MONTANA FIGURA 245 NIPPLE RIDOTTO 1" X 3/4" CONFORME USO ACQUA E GAS | 25018251 | Segrate (MI) | 1 pz | 1,48 | 1,48 | cad |  |
