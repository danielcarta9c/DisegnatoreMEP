# Le sicurezze una per generatore — 24 settembre 2026, sera

> ⏳ **Da guardare al PO**: le tavole 1 e 4, accanto a quelle approvate la mattina
> ([`../../DRAW-017/prova-camera-pulita-2026-09-24/`](../../DRAW-017/prova-camera-pulita-2026-09-24/)).

**Che cos'è.** Le tavole dopo **D-182**, la strada A del PO: una valvola di sicurezza per ogni
generatore, attaccata alla sua uscita e prima dei suoi rubinetti, a qualunque potenza, e nessuna
sulla mandata comune. I grafi completi sono quelli che `rules --apply-all --out` scrive oggi; **i
piani non si correggono a mano** (D-155).

- **Impianti 1 e 4**: i grafi cambiano — esce la sicurezza comune, entra una sicurezza per
  macchina —, e le tavole si ricompongono. **Due agenti per impianto**, avviati da zero in camere
  pulite indipendenti, con lo stesso mandato del 23 settembre
  ([`mandato.md`](../../DRAW-016/prova-camera-pulita-2026-09-23/mandato.md)), le istruzioni di
  `skill/comporre/` e il motore congelato a `6312902`. **Si tiene per ciascun impianto la tavola
  che il metro e l'occhio preferiscono, e l'altra resta agli atti** (`*-altro-agente.*`).
- **Impianti 2, 3 e 5**: cambia solo la motivazione scritta nel grafo — una macchina sola sul 2 e
  sul 3, sopra i 35 kW sul 5, dove le sicurezze per macchina c'erano già. I piani sono quelli di
  `DRAW-017`, **copiati e non toccati**, e sui grafi nuovi danno **SVG identici** a quelli
  approvati: le loro tavole restano quelle di `DRAW-017`.

**Ogni agente dichiara i file che ha aperto: nessuno è uscito dalla propria cartella.** Uno
ricorda che il `CLAUDE.md` del repository gli è arrivato nel contesto all'avvio, senza aprirlo.

## Le tavole

| impianto | tavola | piano | grafo |
|---|---|---|---|
| 1 | [`tavola-completo-1.pdf`](tavola-completo-1.pdf) | `piano-completo-1.json` | `grafo-completo-1.json` |
| 4 | [`tavola-completo-4.pdf`](tavola-completo-4.pdf) | `piano-completo-4.json` | `grafo-completo-4.json` |
| 1, altro agente | [`tavola-completo-1-altro-agente.pdf`](tavola-completo-1-altro-agente.pdf) | `piano-completo-1-altro-agente.json` | `grafo-completo-1.json` |
| 4, altro agente | [`tavola-completo-4-altro-agente.pdf`](tavola-completo-4-altro-agente.pdf) | `piano-completo-4-altro-agente.json` | `grafo-completo-4.json` |
| 2, 3, 5 | quelle di [`DRAW-017`](../../DRAW-017/prova-camera-pulita-2026-09-24/) | `piano-completo-{2,3,5}.json` | `grafo-completo-{2,3,5}.json` |

Per rifarle: `disegnatore-mep piano grafo-completo-N.json --piano piano-completo-N.json
--catalog examples/layout/catalog --symbols assets/symbols --naming naming --out <cartella>`, e
`scripts/to-pdf.sh` sull'SVG.

## La misura, contro le tavole approvate la mattina

**La misura è quella della sessione** (D-152), rieseguita con
[`../../DRAW-017/misura-tavole.py`](../../DRAW-017/misura-tavole.py), non quella che gli agenti
dichiarano:

```
tavola                   formato tratte cedute blocc regole avvisi piegate pieghe incroci
impianto-1               A3          25      0     0      1      1       3      4       1
impianto-2               A3          25      0     0      1      1       4      5       1
impianto-3               A3          24      0     0      1      1       3      3       2
impianto-4               A3          27      0     0      2      2       5      6       2
impianto-5               A2          56      0     0      1      1       8      9       5
1-altro-agente           A3          25      0     0      1      1       3      4       1
4-altro-agente           A3          27      0     0      2      2       5      6       2
```

**Uguali alle tavole approvate**, riga per riga, salvo le tratte: **due in più sull'1 e sul 4**, gli
stacchi delle due sicurezze nuove. I rilievi sono gli stessi: sull'1 la coppia che si apre davanti
al radiatore, il caso noto del terminale (D-167); sul 4 quella e la coppia della caldaia fra le due
verticali dei collettori (15 e 65 mm).

**La scelta, guardando**: sull'1 le due composizioni sono quasi identiche, e si tiene la prima;
sul 4 si tiene la prima, che mette lo scambiatore vicino alla deviatrice — nella seconda le due
linee verso lo scambiatore corrono lunghe e vuote fino a sotto il volano, e l'agente stesso lo
dice «una scelta di gusto».

**Dove stanno le sicurezze, guardate sulla tavola**: su ciascuna macchina, un raccordo subito
all'uscita, la valvola sul suo stacco verso l'alto, e il rubinetto della macchina dopo — sulla
pompa di calore e sulla caldaia del 4, sulle due pompe di calore dell'1. Nessuna sulla mandata
comune.

## Quello che gli agenti hanno visto, e i numeri non dicono

- **Sfiato e scarico dell'accumulo e del volano escono rossi**, e lo scarico ha la freccia: lo
  dicono tutti e quattro, ed era così anche nelle tavole approvate.
- **L'attacco della sonda** dell'accumulo e del volano è disegnato come un moncone, e a occhio
  sembra un tubo tagliato (tre agenti su quattro).
- **Il rapporto «Girati dalla deduzione»** non elenca i raccordi del vaso e del gruppo di
  riempimento, che la posa gira di 180°: tutti e quattro.
- **`scripts/rasterize.sh` taglia il fondo del foglio**: un agente ha trovato la finestra che lo
  fa uscire intero (`--window-size=1588,1400` sull'A3).

## Domande per il progettista

Il grafo gli agenti non l'hanno toccato; le hanno scritte come domande. Sono contenuto MEP: al PO.

- **Impianto 1**: due pompe di calore in parallelo sui collettori comuni, **senza un ritegno su
  ciascun ramo** — è previsto, o sta dentro le macchine? (due agenti)
- **Impianto 1**: il circolatore del secondario **non ha un filtro davanti** — è voluto?
- **Impianto 1**: il lato sanitario del serpentino non ha sicurezza, espansione o ritegno — è
  voluto?
- **Impianto 4**: nella produzione sanitaria le due tre vie **separano l'anello caldaia–scambiatore
  dal tronco**: il vaso di espansione sul ritorno del tronco lo protegge ancora?
- **Impianto 4**: la caldaia non ha un circolatore nel grafo, e il catalogo non dice che ce l'ha a
  bordo (lo dice della pompa di calore): **chi fa circolare il suo anello**, in particolare verso
  lo scambiatore?

## Che cosa chiedono alle istruzioni del pianificatore

Lavoro di un pacchetto successivo, insieme a quello che chiedevano gli agenti di `DRAW-017`:

1. la tabella delle misure dei pezzi non dice dove stanno **sfiato, scarico e sonda
   dell'accumulo combinato** (lo sfiato è a +17,5, non a +12,5 come sul volano a quattro
   attacchi), né le misure di tre vie, raccordi, sicurezza, gruppo di riempimento e confine di
   rete;
2. i **rettilinei minimi** vanno aggiornati: valvola e defangatore fra un raccordo e un collettore
   vogliono 30 mm, non 20–25; valvola, circolatore e valvola 40 mm;
3. **da quale capo il motore mette gli organi in linea** non si ricava, ed è quello che decide dove
   una linea ne può incrociare un'altra; serve una regola scritta, e una distanza per le linee di
   traverso;
4. **un terzo caso noto di B11**: il generatore in basso in una pila entra dal fondo delle due
   verticali dei collettori, e la coppia si apre fra le due verticali;
5. **quale generatore va sopra** quando uno dei due porta le tre vie di un'utenza;
6. i **percorsi** nelle istruzioni sono quelli del repository, non quelli della camera; e il
   mandato dice che il catalogo non serve al pianificatore, mentre le istruzioni lo usano;
7. il messaggio del motore sull'A4 consiglia di dividere l'impianto su più fogli, mentre D3 dice di
   prendere il formato successivo; e A1 parla di tre fasce dove il motore ne conta quattro.
