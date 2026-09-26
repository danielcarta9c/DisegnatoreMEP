# Rapporto del compositore A — camera 6a, 26 settembre 2026

> Conservato come l'agente l'ha scritto, in camera pulita, sul motore congelato a `967fc89`. La
> misura che vale è quella della sessione (`../RAPPORTO.md`), non questa. Il piano è `piano-6-a.json`,
> la tavola `../tavola-impianto-6.pdf`.

## La tavola esce: A2, 0 tratte cedute, 0 rilievi bloccanti

- Tavola: `camera-6a/tavola/prova-6-centrale-ibrida-solare-t1.svg`. Immagine: `camera-6a/lavoro/tavola-finale.png`.
- Piano consegnato: `camera-6a/piano.json`, con 43 pezzi, 14 note e una `regola` per ogni pezzo. Nessun organo in linea nel piano, tutte le coordinate multiple di 2,5.

**Ultima uscita del comando**:
- formato A2, 48 tratte, 0 cedute, 0 bloccanti; preflight senza rilievi;
- misura da `geometria.json`: 10 pieghe, 3 sormonti, ingombro del disegno 360 × 165 mm.

Rilievi rimasti:
- `HIGHWAY_IS_NOT_STRAIGHT` sulla catena volume → rip-mandata-secondario → fancoil: "2 di troppo";
- `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` fancoil–volume tecnico: terminale a 10 contro 15, caso noto di B11;
- `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` bollitore–collettore solare: serpentina a 10 contro 15, caso noto di B11.

Scelte principali, ciascuna misurata contro l'alternativa:
- **Collettori dei generatori (B3)**: mandata vicina alle macchine 3 sormonti, ritorno vicino 4. Tengo la mandata vicina.
- **Colonne del pettine (B12)**: ritorno vicino al volume 10 pieghe e 3 sormonti; mandata vicina 16 pieghe, 4 sormonti e tre rilievi in più. Tengo il ritorno vicino.
- **Raccordo di mandata del pettine**: giacitura scritta (rotazione 90) 10 pieghe; lasciata alla deduzione (0→180) 11 pieghe. Tengo quella scritta.
- **Collettore solare**: con il ritorno diritto la mandata scala accanto al bollitore e corre a 5 mm dal ritorno della serpentina (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE`). Con la mandata diritta il gradino di 5 mm cade sul ritorno, subito dopo il collettore. Tengo la mandata diritta.
- **Formato**: in A3 "the legend needs 252.5mm but its band is 235mm tall". A2 è il più piccolo.

## Cosa ho visto nella tavola

Assomiglia al lavoro di un disegnatore:
- a sinistra la generazione: PdC, sotto la caldaia (stessa x), in basso il collettore solare;
- il primario corre diritto dalla PdC al volume tecnico, a +5 e +20;
- deviatrice sulla mandata con la terza via verso la serpentina superiore del bollitore; le due verticali della serpentina corrono appaiate a 10 mm;
- a destra un pettine vero: il ritorno principale va diritto dai radiatori al volume, la mandata paga il gradino 15/10 alla testa della colonna;
- in basso il bollitore, servito dall'alto (serpentina), da sinistra (solare e acqua fredda) e con l'ACS che esce in alto verso miscelatrice e utenze.

I 3 sormonti sono quelli topologicamente inevitabili: ritorno PdC sulla verticale di mandata, terza via della deviatrice sul ritorno del volume, ritorno radiatori sulla colonna di mandata.

Dove non assomiglia:
- La **seconda valvola del separatore d'aria** il motore la mette subito prima della deviatrice, a circa 75 mm dal separatore. Dal piano non si cura: la lunghezza della tratta la impone il ritorno parallelo, più carico.
- Il **gruppo solare è spezzato**: circolatore e ritegno li posa il motore alla porta del bollitore; vaso, manometro e sicurezza stanno addosso al collettore, perché vicino al bollitore sotto il ritorno solare corre l'acqua fredda.
- **Mandata e ritorno solari hanno lo stesso colore (#c71585), anche in legenda**: le due voci non si distinguono. È una convenzione grafica, non la tocco.
- Il disegno è piccolo sul foglio A2, perché lo impone la legenda.

**La tavola mi sembra giusta dove due rilievi dicono di no:**
- `HIGHWAY_IS_NOT_STRAIGHT` conta come "di troppo" le L di testa e di piede della colonna, che B1 elenca fra le pieghe imposte. È anche incoerente: nella variante precedente segnalava la catena di ritorno e non quella di mandata, che aveva la stessa forma; ora il contrario. Spostando la posa il rilievo si sposta, non sparisce.
- `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` fancoil–volume misura un interasse di 37,5 mm fra le due colonne, dove la coppia in realtà gira insieme a L annidate.

## Cosa manca o è sbagliato nelle istruzioni

1. **A3 troppo piccolo segnalato in modo fuorviante.** Al primo tentativo il comando non ha detto "legend" né "bands". Ha detto "run se-2-a … the 6 straight steps the chain needs beyond the port … run into an obstacle", davanti a `radiatori.in`. L'ostacolo era la fascia della legenda, verticale a destra del foglio. Mi è costato circa 10 esecuzioni e 5 diagnosi su copie del grafo in `lavoro/` (il `grafo.json` è intatto). Il messaggio "legend" arriva solo quando il disegno si instrada. Servirebbero nelle istruzioni la forma dell'area utile per formato (legenda: fascia verticale larga 50 mm; cartiglio 36 mm in basso) e l'avviso che un "obstacle" vicino al bordo può voler dire "foglio piccolo".
2. **§4 "per un raccordo non scriverla" non regge sul pettine a colonne.** La deduzione mette la corsa del raccordo verso la linea principale, in orizzontale, e la mandata fa una Z. Il motore rispetta una giacitura scritta. Serve l'eccezione esplicita.
3. **Organi in linea attraverso una piega.** Il motore mette valvola e circolatore in fila dal raccordo lungo il percorso. Con la piega di fondo colonna a 20–22,5 mm dal raccordo il circolatore sta sull'orizzontale, a 25 mm cade sulla piega (`INLINE_ORGAN_BREAKS_THE_RUN`). §4bis dà solo lunghezze di rettilineo.
4. **Un organo isolato che sta in mezzo alla tratta** (il separatore d'aria) si vede le due valvole divise ai due capi. "A partire dalla porta del pezzo che isolano" non copre questo caso.
5. Non ci sono criteri per:
   - dove mettere il gruppo ACS (miscelatrice, confine AF, utenze), che contende al pettine lo spazio sotto la distribuzione;
   - lo scarico del volume, che pende 10 mm sotto e sbarra il passaggio alle linee che vanno sotto il volume;
   - dove vanno vaso, manometro e sicurezza di un circuito solare: vicino al collettore o vicino al circolatore.
6. Minori:
   - la lista "Girati dalla deduzione" non è completa: `der-vaso-solare` e i raccordi dei vasi e del riempimento sono a 180 in `geometria.json` ma non compaiono;
   - l'incarico dice che `catalogo/` non serve al pianificatore, ma §3 lo richiede per passare da `definition_id` a simbolo;
   - i percorsi citati in §3 (`examples/layout/catalog`, `assets/symbols`) non corrispondono a `catalogo/` e `simboli/` della camera.

**Domande sul grafo** (nelle note del piano, non le ho risolte): il bollitore ha `recirculation_in` libero e non c'è ricircolo ACS; il circuito solare non ha sfiato né intercettazioni, benché il catalogo abbia `air-vent-solar` e `valve-isolation-solar`; il `vent` del volume tecnico è libero. È voluto?

## Esecuzioni e file aperti

Circa 39 esecuzioni di `piano.sh`, poco sopra la quarantina indicata, più 6 chiamate dirette allo stesso modulo (1 `--help` e 5 diagnosi su copie del grafo in `lavoro/`, poi cancellate). `piano.sh` esegue il motore fuori dalla camera (`scratchpad/motore/src`, interprete del repository): l'ho solo eseguito, non ho aperto quei file.

File aperti:
- `ISTRUZIONI.md` e `CONSEGNA.md`, per intero;
- `grafo.json` (con Python);
- `simboli/*.json` dei simboli usati dal grafo, più `pressure-reducer.json`; `simboli/radiator.svg` e `simboli/fan-coil-ducted.svg`;
- `catalogo/*.json` dei `definition_id` del grafo, via script per leggere `symbol_id`; `catalogo/radiator.json` e `catalogo/fan-coil-ducted.json` per intero;
- `strumenti/piano.sh`, `strumenti/rasterize.sh`, `strumenti/to-pdf.sh`;
- le uscite `tavola/*.svg` e `tavola/geometria.json`;
- i miei file in `lavoro/`: il generatore del piano `genera.py`, il misuratore `misura.py`, `zoom.py` per ingrandire zone della tavola, e le prove.

`naming/` non l'ho aperto.
