# Rapporto del compositore B — camera 6b, 26 settembre 2026

> Conservato come l'agente l'ha scritto, in camera pulita, sul motore congelato a `967fc89`. La
> misura che vale è quella della sessione (`../RAPPORTO.md`), non questa. Il piano è `piano-6-b.json`,
> la tavola `tavola-impianto-6-seconda-composizione.pdf`.

## Rapporto — camera-6b (centrale ibrida PdC + caldaia modulare + solare)

**La tavola esce.** Il file è `camera-6b/tavola/prova-6-centrale-ibrida-solare-t1.svg`, l'immagine `camera-6b/lavoro/t11.png`. Il piano consegnato è `camera-6b/piano.json`: formato A2, 43 pezzi, 11 note, una `regola` su ogni pezzo.

### Che cosa si vede nella tavola
- **Primario:** la PdC sta sopra la caldaia, alla stessa x. Il volume tecnico è allo stesso y della PdC, quindi mandata (y=5) e ritorno (y=20) sono rette da un capo all'altro. I due collettori sono verticali corte accanto ai generatori.
- **Deviatrice e bollitore:** la deviatrice è sulla mandata e la sua terza via scende al serpentino superiore. La coppia del serpentino arriva su due verticali adiacenti ed entra a L annidate, con la mandata sopra.
- **Bollitore:** è sotto il volume, alla stessa x. Da sinistra gli arrivano, dall'alto in basso, la coppia del primario, la coppia solare e l'AF, senza incroci fra loro.
- **Solare:** il collettore è nella fascia di generazione e la mandata solare è retta. Il ritorno scala di 5 mm, un gradino imposto (collettore a interasse 15, serpentino a 10).
- **Secondario:** le rotaie partono dal volume. Il fancoil sta sopra, girato (90 + specchio), su due montanti adiacenti; il radiatore è diritto in fondo alle rotaie.
- **Numeri della posa:** 9 pieghe e 3 sormonti, tutti imposti. Due sono noti: la terza via che scavalca il ritorno e il ritorno PdC che attraversa il collettore di mandata. Il terzo è l'unico sormonto del pettine, che cade sul tronco dove non ci sono organi.

**Assomiglia al lavoro di un disegnatore?** Nello scheletro sì. Dove no:
- le due verticali del serpentino sono lunghe (circa 90 mm) e resta un vuoto sotto la caldaia. È il prezzo di avere l'ACS che esce dall'alto del bollitore e deve passare sotto lo scarico del volume;
- la seconda valvola del separatore d'aria finisce addosso alla deviatrice, a 60 mm dal separatore;
- il gruppo solare è spezzato in due. Circolatore e ritegno stanno sul bollitore; sicurezza, manometro e vaso stanno 50 mm più a sinistra, perché più a destra cadrebbero sulla linea AF;
- un terminale è girato.

### Ultima uscita del comando
- Formato A2. A3 non si può usare: la legenda chiede 252,5 mm e la fascia ne ha 235.
- 84 tubazioni del grafo, disegnate in 48 spezzate, di cui 7 piegate.
- **0 tratte cedute, 0 rilievi bloccanti.** Preflight senza rilievi.
- Rilievi:
  - `HIGHWAY_IS_NOT_STRAIGHT` su se-4 (radiatori → rc-ritorno-secondario, «2 di troppo»);
  - `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` bollitore–collettore solare: è il caso noto del serpentino, 10 contro 15 (B11).
- Ho usato circa 16 esecuzioni.

### Che cosa non ho sistemato, e perché
1. **Il rilievo su se-4 dice di no, ma secondo me la tavola ha ragione.** È il gradino del terminale (10 contro 15), che §5 B1 dà per imposto. Il motore lo riconosce come imposto solo se la catena terminale→volume passa per il passante del raccordo **secondo le porte del grafo**, mentre §3 dice che il passante lo decide la posa. L'ho misurato in tre pose:
   - gradino vicino al radiatore: il rilievo c'è;
   - raccordo a y=15, gradino sul tronco verso il volume: il rilievo resta;
   - utenze scambiate, radiatore sdraiato sopra: il rilievo sparisce, con gli stessi numeri (9 pieghe, 3 sormonti).

   Ho tenuto la versione che si legge meglio, cioè il radiatore diritto.
2. **Il pettine di B12 applicato alla lettera non funziona qui.** Con le utenze impilate a destra, il motore posa «valvola + circolatore» **dal capo del raccordo**, quindi sulla verticale. Il ritorno dell'utenza alta deve attraversarla proprio lì, e il motore lo fa girare: nella prima tavola c'era uno zig-zag, con 2 pieghe di troppo e interassi 7,5/10/15. Topologicamente un sormonto è inevitabile. L'unico che cade su tratti liberi è quello del ritorno sul tronco di mandata, e l'ho ottenuto prendendo un'utenza da sopra, su montanti adiacenti.
3. **Il motore spezza le file di organi fra i due capi della tratta.** Succede alla valvola del separatore d'aria e alla valvola del circolatore lato terminale. Il piano non può impedirlo.
4. **Il gradino su una tratta diretta lo mette il motore dove vuole.** Con la mandata solare a gradino l'ha messo a 12,5 mm dal bollitore, a 5 mm dal ritorno del serpentino (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE`). Ho risolto rendendo retta la mandata.
5. **Difetto del motore o della convenzione:** andata e ritorno del fluido solare hanno lo stesso colore (#c71585) e lo stesso tratto. Nella tavola li distinguono solo le frecce, e la legenda porta due voci identiche.
6. **L'elenco «Girati dalla deduzione» è incompleto.** `der-vaso-solare`, `tee-filling-unit…` e `tee-expansion-…` risultano a 180° in `geometria.json` ma non sono elencati. La tavola è giusta, il rapporto trae in inganno.

### Che cosa manca o è sbagliato nelle istruzioni
- **B12 ignora i circolatori sui rami** (vedi punti 2 e 3). Va detto che il sormonto del pettine deve cadere su un tratto senza organi, e che una tre vie o un terminale si possono prendere da sopra girandoli (per il fancoil: 90 + specchio → attacchi in basso, mandata a destra).
- **§4bis descrive l'ancoraggio degli organi in modo impreciso.** Dice «dalla porta del pezzo che isolano», ma il comportamento reale è: valvola a monte e circolatore dal raccordo, valvola a valle dal terminale.
- **Rettilinei misurati qui, più lunghi di quelli di §4bis:**
  - valvola + circolatore + valvola: 37,5 mm (32,5 non basta);
  - defangatore con due valvole: più di 27,5 mm (40 va);
  - gruppo di sicurezza sanitario fra due raccordi: 30 mm da centro a centro (25 non basta);
  - una valvola fra due raccordi: 22,5 mm da centro a centro (17,5 non basta).
- **B1 e il motore non concordano sul gradino 10/15 del terminale** (vedi punto 1).
- **A1 non nomina il collettore solare** fra i generatori, anche se il catalogo lo dichiara tale. B11 potrebbe citare fra i casi noti il serpentino solare del bollitore a due serpentini.
- **Manca un avvertimento:** con il bollitore sotto il volume, lo scarico del volume e l'uscita ACS in alto si contendono lo stesso spazio. È questo che fissa la quota del bollitore.
- **Serve una soglia pratica per la legenda:** con circa 26 simboli la legenda obbliga ad A2, qualunque sia la dimensione del disegno. Me ne sono accorto solo dopo un'esecuzione.

### Domande sul grafo (non l'ho toccato)
- F4 vuole il carico automatico «sul volume tecnico», ma il completamento ha messo il gruppo di riempimento sul ritorno primario verso i generatori. È voluto?
- Resta aperta la domanda del grafo `a-gruppo-solare-mancanti`: sul circuito solare non ci sono valvole d'intercettazione, sfiato, carico e scarico.

### File aperti
- In `camera-6b`:
  - `ISTRUZIONI.md` e `CONSEGNA.md`, per intero;
  - `grafo.json`, letto con script;
  - `strumenti/piano.sh`, `rasterize.sh`, `to-pdf.sh`;
  - `naming/lines.json`;
  - i manifesti in `simboli/` dei pezzi presenti, più gli SVG di `fan-coil-ducted` e `radiator`;
  - `catalogo/` delle macchine; tutti i `simboli/*.json` e `catalogo/*.json` letti da script per ricavare `symbol_id` e `inline_gap_mm`;
  - le uscite del comando (`tavola/*.svg`, `tavola/geometria.json`);
  - i miei file in `lavoro/`.
- `piano.sh` esegue il motore in `…/scratchpad/motore/src` e la venv in `/home/user/DisegnatoreMEP/.venv`: l'ho solo lanciato tramite lo script, senza aprire quei file.
- Nient'altro letto o modificato fuori da `camera-6b`.
