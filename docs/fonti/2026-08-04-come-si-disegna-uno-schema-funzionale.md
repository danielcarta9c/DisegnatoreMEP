# Come si disegna davvero uno schema funzionale — e cosa sbaglia il nostro

**Data:** 4 agosto 2026 · **Stato:** prima acquisizione di fonti, richiesta dal PM

Il PM ha chiesto dall'inizio del progetto di studiare come si disegna uno schema
termotecnico, guardando la rete e la documentazione dei produttori. Non era mai stato
fatto: il registro fonti porta ISO 5457, 7200, 14617 e ASHRAE 134 come «da acquisire e
valutare» dal primo commit, la fase grafica ha inventato `CONV-GRAFICA-001` **proprio
perché** mancavano (D-047), e il motore di layout è stato costruito sopra quella
convenzione inventata senza mai confrontarla con una tavola reale.

Questo documento è la prima acquisizione. Le fonti sono citate e sintetizzate, non
riprodotte: nessun simbolo e nessun disegno viene copiato (regole in `README.md` di
questa cartella, D-007, D-015).

## 1. La norma italiana che mancava

**UNI 9511 — «Disegni tecnici. Rappresentazione delle installazioni»**, in quattro parti,
armonizza i segni grafici degli impianti civili: riscaldamento, condizionamento,
idrosanitario, gas. Copre tubazioni, valvolame, raccorderia, strumenti di regolazione e
controllo.

È **la** norma di riferimento per la pratica italiana, ed è quella che il progetto non
aveva. ISO 14617 resta valida come regola generale sui diagrammi, ma la simbologia che un
termotecnico italiano si aspetta è quella di UNI 9511.

## 2. Cosa mostra una tavola vera

Analizzate due tavole pubbliche di progetto — uno schema funzionale di centrale termica
condominiale a Treviso e uno di centrale scolastica in provincia di Ravenna — più il
materiale formativo Caleffi su pompe di calore aria-acqua e sistemi ibridi.

### 2.1 Il formato

| Tavola | Foglio |
|---|---|
| Centrale termica condominiale | 1189 × 841 mm (A0) |
| Centrale termica scolastica | 610 × 2500 mm (striscia) |

Nessuna delle due è A3, e da questa misura era stata dedotta una proposta: riaprire
ADR 0003 verso i formati grandi.

**La proposta è ritirata.** Il PM l'ha respinta il 4 agosto 2026: «Formato A3 oppure A4
se il disegno è proprio piccolo. Non voglio A0 o strisce.» Registrata come D-058.

La deduzione era sbagliata nel metodo, non solo nell'esito: due tavole trovate in rete
dicono cosa fa chi le ha disegnate, non cosa deve fare uno studio che stampa in ufficio e
consegna elaborati che il cliente possa maneggiare. Il vincolo di formato è una scelta di
prodotto già presa (D-019) e non si riapre misurando esempi altrui. Quello che le due
tavole insegnano davvero sta nei paragrafi seguenti — corsie, codifica delle linee,
composizione — e vale identico su una A3.

### 2.2 La composizione è a corsie, non a colonne

Misurata la geometria vettoriale della tavola condominiale: 33 843 segmenti, il 74%
ortogonali — il restante 26% sono gli interni dei simboli, non le tubazioni.

I tratti orizzontali lunghi si concentrano su poche quote ripetute (y ≈ 187, 266, 280,
334, 375, 388 mm), ciascuna con cinque-otto tratti. Sono le **corsie**: mandata e ritorno
corrono come dorsali orizzontali attraverso il foglio, e i componenti pendono da quelle con
stacchi verticali.

Il nostro motore non fa nulla di simile: dispone i componenti in quattro pile verticali e
instrada ogni tratta per conto proprio con un A*, punto a punto. Il risultato è
geometricamente valido e non somiglia a uno schema.

### 2.3 Mandata e ritorno sono linee diverse

La legenda tubazioni della tavola reale distingue, con tratti e colori propri:

- riscaldamento andata / riscaldamento ritorno
- condizionamento andata / condizionamento ritorno
- acqua calda sanitaria / acqua fredda sanitaria / ricircolo ACS
- linea gas
- linee di regolazione

Il nostro codice associa colore e tratto al **fluido**, quindi mandata e ritorno dello
stesso circuito sono indistinguibili. Peggio: poche ore fa ho «corretto» la legenda
accorpando le righe per fluido, che va esattamente nella direzione sbagliata.

### 2.4 La tavola porta i diametri, non solo i nomi

Sulla tavola reale compaiono, sulle tubazioni e accanto ai componenti: `DN65`, `3"`, `4"`,
`1"`, `3/4"`, `De 22`, `Øint > 18 mm`; tarature (`5,0 bar`, `2,1 bar`, `f.s. 16 bar`);
vincoli di posa (`< 1 m`, `> 0,5 m`).

I nostri tag portano litri e portata. **Il grosso dell'informazione di uno schema sta sulle
tubazioni**, e noi non ce ne mettiamo nessuna.

### 2.5 Le sigle sono mnemoniche funzionali

Sulle tavole reali: `VS` valvola di sicurezza, `VIC` valvola intercettazione combustibile,
`VST`, `PS` pressostato, `TS` termostato di sicurezza, `TI`, `M` manometro, `T` termometro,
`FLU` flussostato, `PSM` pressostato di minima, `MT`, `GM`, `SCAMB` scambiatore, `VEp` vaso
di espansione, `CVrisc`, `UCrisc`.

Le nostre — `PDC-01`, `VOL-01`, `BOL-01` — sono progressivi inventati per il caso di prova.
Plausibili, ma la convenzione reale è una sigla funzionale per tipo, numerata solo quando
il componente si ripete.

### 2.6 La libreria è largamente incompleta

La legenda generale della tavola reale elenca **oltre cinquanta simboli**. La nostra ne ha
venti, e ne copre forse sei. Mancano famiglie intere:

| Famiglia | Simboli che mancano |
|---|---|
| Strumenti | manometro e termometro ad attacco radiale e posteriore, pozzetto di prova, sonda temperatura, sonda temperatura esterna, sonda pressione, termostato di regolazione e di blocco, pressostato di minima e di blocco, flussostato, contatore, misuratore di portata |
| Valvolame | valvola a sfera, a farfalla, a tre vie, di taratura, di bilanciamento con flussometro, unidirezionale, a galleggiante, di by-pass differenziale (sfioro), autoflow |
| Sicurezze | valvola di sicurezza, disconnettore idraulico, giunto antivibrante, allarme acustico e ottico |
| Regolazione | servocomando, apparecchio regolatore e registratore, programmatore orario, linee di regolazione, bus Modbus/M-Bus/ethernet |
| Trattamento acqua | filtro autopulente, dosatore polifosfati, gruppo automatico di riempimento, degasatore |
| Gas | riduttore e stabilizzatore di pressione, filtro gas, presa di pressione, giunto antivibrante per gas |
| Idraulica | scambiatore a piastre, compensatore/separatore idraulico, vaso di espansione aperto |

Nota: il nostro `buffer-four-port` chiama «volano» quello che le fonti distinguono in
**separatore idraulico**, **compensatore idraulico** e **accumulo inerziale**: tre
componenti con funzioni diverse.

### 2.7 La regolazione si disegna

La tavola reale porta le linee di regolazione come rete propria, con sonde, termostati,
servocomandi e i bus di comunicazione. Il nostro modello ha `Domain.CONTROL` e non l'ha mai
usato.

### 2.8 La tavola porta tabelle

Oltre alla legenda: «TABELLA CARATTERISTICHE POMPE» con portata, prevalenza, marca e
modello per ciascuna pompa; «TABELLA SPESSORI MINIMI DI ISOLAMENTO TERMICO». I dati
tecnici stanno in tabella, non appesi a ogni simbolo.

## 3. Cosa resta valido di quanto costruito

Non è tutto da buttare, e vale la pena separare le due cose.

**Regge la meccanica:** griglia e allineamento, invarianza di scala, tratte ricomposte
dagli accessori in linea, interruzione della linea sotto un componente in linea,
partizione multi-tavola con rimandi accoppiati, validazione geometrica, riproducibilità.
Sono le fondamenta e continuano a servire.

**Non regge il linguaggio grafico:** i simboli, la loro semantica, la codifica delle linee,
cosa si scrive sulla tavola, e soprattutto **la regola di composizione**. Su questo il
progetto ha inventato invece di studiare, e si vede.

## 4. Cosa cambia, in ordine

1. **Acquisire UNI 9511** e derivarne la simbologia. È una decisione di prodotto perché la
   norma è a pagamento e va comprata.
2. **Rifare la libreria** sulla simbologia normata, coprendo le famiglie di §2.6.
3. **Codificare le linee per servizio, non per fluido**: mandata e ritorno separati.
4. **Portare i diametri sulla tavola**: il modello deve trasportarli e il layout scriverli
   sulle tubazioni.
5. **Cambiare la regola di composizione**: corsie orizzontali di mandata e ritorno con
   stacchi verticali, al posto delle pile verticali.
6. **Riaprire il formato ordinario** (ADR 0003): per una centrale termica reale l'A3 è
   stretto.

## Fonti

| ID | Fonte | Uso |
|---|---|---|
| SRC-007 | UNI 9511 (4 parti), «Disegni tecnici. Rappresentazione delle installazioni» | Simbologia italiana degli impianti. **Da acquistare** |
| SRC-008 | [Caleffi — Quaderni e Tabelle](https://www.caleffi.com/it-it/formazione/quaderni-e-tabelle) e [Componenti e schemi per impianti a pompa di calore aria-acqua](https://www.caleffi.com/sites/default/files/media/external-file/25%20-%20Componenti%20e%20schemi%20per%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf) | Casi di studio e prescrizioni di prodotto (D-015) |
| SRC-009 | [Schema funzionale centrale termica, Condominio Tower House, Treviso — Divisione Energia srl](https://www.divisionenergia.it/wp-content/uploads/2025/02/Cond.TH_schema-ct-as-built.pdf) | Caso di studio: legenda, corsie, diametri, sigle |
| SRC-010 | [Schema funzionale centrale termica, Liceo «G. Ballardini» — Provincia di Ravenna](https://presadmin.provincia.ra.it/content/download/88849/1115730/file/SM04%20-%20BALLARDINI%20Stato%20Modificato%20Schema%20funzionale%20Centrale%20Termica.pdf) | Caso di studio: colori tubazioni, sigle, tabelle |
| SRC-011 | [Segni grafici nella rappresentazione dei componenti — CT Energia](https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf) | Materiale didattico sulla rappresentazione degli impianti fluidotermici |

Le tavole SRC-009 e SRC-010 sono documenti pubblici di gara e di progetto: sono state
**lette e misurate**, non riprodotte. Nessun loro contenuto grafico entra nel progetto.
