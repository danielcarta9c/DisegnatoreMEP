# REL-028, punto 2 — Due liste complete, il bollitore col serpentino, il rame «CONDY», il pollice all'attacco, le quantità nette — rapporto

**18 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md`, punto 2 (I-314 … I-320), con le indicazioni del PO arrivate
in sessione dalla sessione precedente (I-325 … I-328) e la correzione del PO (I-329); poi **il punto 1**, il rilievo
Tecnomat Pro, che il PO ha portato in sessione (§2bis). Ramo `claude/rel-028-punto-2`. **La release è la 2.2.0**: il PO
ha detto «dammi la skill aggiornata e fondi su main» senza un numero, e la sessione ha preso quello proposto dal
pacchetto.

## 1. Prima di tutto: le tavole

**Nessuno schema funzionale cambia**: sui 30 casi del banco tutti gli SVG di schema sono identici. **Cambia una tavola:
la pianta del collaudo T3** (`collaudo-t3-rel012`), perché la sua tabella delle tratte scrive la «L quot.», che ora
è netta (2e). Prima e dopo: `pianta-t3/pianta-prima.png`, `pianta-t3/pianta-dopo.png`, e la sola tabella affiancata in
`pianta-t3/tabella-prima-e-dopo.png`. Cambiano i numeri della colonna «L quot.» (T01 7 → 6, T10 22 → 19, …), due
asterischi in più (T08 condensa 10*, T11 cavo 13*: ora vince il minimo) e la nota (`L quot. = L + 1 m per eccesso a
0,5 m`, senza il ×1,15).

**Una tavola dimostrativa, fuori dal banco**: il T1 del banco (Shenling 12 kW, volano, bollitore 200 l) con la
superficie del serpentino dichiarata sul bollitore — `tavola-bollitore/tavola-t1-serpentino.png` (e `.pdf`, il grafo
accanto). Nella tabella delle apparecchiature: «BOL-01 · Bollitore ACS · 200 l · serpentino 2,5 m² · Cordivari». Il
resto della tavola è quello di sempre.

Nel banco cambiano anche quattro distinte (`t1-rel023`, `plenum-di-mandata-rel026`, `plenum-motorizzato-rel026`:
`distinta.json` e `tabelle-del-foglio.json`) per le quantità nette, le voci nuove del bollitore e del raccordo
all'attacco, e l'impronta delle regole. Registrate:

```
$ python3 scripts/banco.py --registra
t1-rel023: CAMBIATO  ~ distinta/distinta.json  ~ distinta/tabelle-del-foglio.json
collaudo-t3-rel012: CAMBIATO  ~ pianta/pianta.svg  ~ pianta/pianta.tracciati.json
plenum-di-mandata-rel026: CAMBIATO  ~ distinta/distinta.json  ~ distinta/tabelle-del-foglio.json
plenum-motorizzato-rel026: CAMBIATO  ~ distinta/distinta.json  ~ distinta/tabelle-del-foglio.json
Impronte scritte: tests/banco/impronte.json (30 casi)
```

## 2. La misura su PR.MI.059 (col listino Tecnomat Pro e i minimi Shenling)

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
apparecchiature: 8 voci, prezzate 8, totale 6780.87 €
  P-A.1 Pompa di calore aria-acqua: Shenling ThermaX R290 12 kW      3103.60 €
      Idrosanitaria    3103.60 €  ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa
  P-A.2 Bollitore ACS — 200 l, a serpentino maggiorato …, non minore di 2,5 m²   461.40 €
      Idrosanitaria     461.40 €, serpentino 0.8 m²  ⚠ serpentino 0,8 m², sotto il minimo di 2,5 m²
      Abbattista        626.52 €, serpentino 2 m²  ⚠ serpentino 2 m², sotto il minimo di 2,5 m²
  P-A.3 Volano termico a quattro attacchi, 80 l                        156.49 €  (Idrosanitaria; Abbattista 179.29)
  P-A.4 Pompa di circolazione: DAB Evosta 2 40-70/130                   93.60 €  (Idrosanitaria; Abbattista 96.52)
  C-A.1 … C-A.4 (Daikin, Airzone, comando)                            2965.78 €  (Idrosanitaria)
voci 99, prezzate 90, da prezzare 9; totale 8742.55 €
ordine: 8689.87 € + senza fornitore 52.68 €
un fornitore solo (articoli in comune: 24):
  Idrosanitaria  ha 61 ( 8698.03 €), non ha 13 ( 236.99 € altrove): totale  8935.02 €; sugli articoli in comune   913.47 €
  Tecnomat       ha 57 ( 1834.68 €), non ha 17 (7156.14 € altrove): totale  8990.82 €; sugli articoli in comune   846.60 €
  Abbattista     ha 29 ( 2079.45 €), non ha 45 (7197.17 € altrove): totale  9276.62 €; sugli articoli in comune  1145.09 €
  Idrosanitaria: 34 articoli, 7973.17 €
  Tecnomat: 38 articoli, 686.73 €
  Abbattista: 2 articoli, 29.97 €
avviso M01c: Idrosanitaria 3103.60 € ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa
avviso M10b: Idrosanitaria 461.40 € ⚠ serpentino 0,8 m², sotto il minimo di 2,5 m²
avviso I74: Tecnomat 20.30 € ⚠ taratura 7 bar (la voce: 6 bar)
avviso I82: Tecnomat 3.50 € ⚠ spessore 19 mm (la voce: 32 mm o 30)
avviso E36: Tecnomat 0.70 € ⚠ sezione 2×0,50 (la voce: 2×0,75)
avviso I44: Tecnomat 3.81 € ⚠ attacco posteriore ¼" (la voce: radiale ½")
avviso I84c: Tecnomat 2.79 € ⚠ spessore 19 mm (la voce: 32 mm o 30)
… (e gli avvisi di REL-027: A06c, I47 Abbattista, I44 Abbattista)
```

**In parole.**

- **La lista prezzata completa** è 8.742,55 € netti su 90 voci: 6.780,87 € di apparecchiature e 1.961,68 € di
  minuteria (era 2.065,98 € in REL-027: −24,31 € per il rame «CONDY», −80 € col listino Tecnomat Pro). Gli articoli
  senza un fornitore scendono da 137,55 a 52,68 €.
- **Un fornitore solo**: ora Tecnomat ha 57 articoli su 74 (erano 38); il più economico per tutto resta Idrosanitaria
  (8.935,02 €), Tecnomat a 55,80 € in più; sugli articoli che hanno tutti Tecnomat costa meno (846,60 € contro 913,47).
- **Il bollitore**: col minimo del manuale Shenling per la 12 kW, 2,5 m² smaltato (I-329), **nessuno dei due bollitori
  delle offerte va bene**: il Bolly 1 XL WB 200 di Abbattista ha 2 m², il Bolly 1 ST di Idrosanitaria 0,8 m². Il conto
  prende il meno caro (461,40 €) e lo avvisa: **il numero del CAPEX qui è quello di un bollitore che non va bene**.
  Se il progettista accetta il Bolly 1 XL da 2 m² (I-329: «sappiamo che rende bene»), lo scrive sul bollitore e il
  conto prende quello di Abbattista, 626,52 € (la prova `test_il_progettista_accetta_un_serpentino_piu_piccolo`).
- **La pompa di calore del preventivo Idrosanitaria non è una Shenling.** Il codice AW12NMXGHA, nelle schede dei
  rivenditori, è una **Haier GT R290 12 kW trifase** ([groupsumi](https://groupsumi.it/en/climate-control/aerothermal-energy/monobloc-air-to-water-heat-pump/haier-gt-r290-12-kw-monobloc-air-source-heat-pump-three-phase-aw12nmxgha));
  non ho trovato la scheda di Haier. Il conto la prende perché non c'è altro prezzo per la Shenling 12 kW, e la avvisa.
- I termostati di zona Airzone non sono nella misura: la lista non dice quanti sono.

## 2bis. Il punto 1: il rilievo Tecnomat Pro

Il file del PO (`docs/rilievi/tecnomat-pro-rilevato-2026-11-18.md`, rev. 03, negozio di Segrate, account Pro): parte A,
150 righe su 150 col prezzo Pro (5 codici non più a catalogo sostituiti, E20 sostituito per risparmio con ⚠ sulla
curva, I49b sostituito con ⚠: flessibile inox al posto del giunto in gomma); parte B, 35 articoli trovati (9 con ⚠),
27 non trovati (non entrano). Nel listino: il §1 è «Il rilievo Tecnomat Pro — 18 novembre 2026»; le note «Pro;
pubblico …» restano; una sezione nuova con le 35 righe della parte B. **Due ID avevano già una riga Tecnomat con ⚠**
(I44 manometro 0–12, I47 Filler senza disconnettore): la riga della parte B è più vicina alla voce (0–6 bar, il
gruppo col disconnettore) e prende l'ID; quella vecchia resta documentata senza ID. Tecnomat ha ora 183 prezzi.

```
$ python3 -m pytest tests/distinta/test_i_fornitori.py -q
16 passed
```

(la prova nuova `test_il_rilievo_tecnomat_pro_e_tutto_nel_listino` rilegge il file del rilievo e trova ogni riga nel
listino, col codice, il prezzo Pro, Segrate e la data.)

## 3. I criteri, con il comando e l'output

**2a — due liste, tutte e due complete** (D-241, I-314). `distinta --costo` prezza anche le apparecchiature, comprese
quelle fornite da Nove C (nota «fornita da Nove C»), dal listino — ID della famiglia M, scelti sui dati del pezzo con
`prezzo_apparecchiatura` del corredo — o DA PREZZARE col perché; fuori restano quelle del Committente. `distinta
--lista` scrive «fornita da Nove C: non si quota» sulle voci di Nove C; `--lista --senza-nove-c` le toglie e lo dice.

```
$ python3 -m pytest tests/distinta/test_rel028_due_liste_e_bollitore.py -q
14 passed
```

(le prove: la lista prezzata con le apparecchiature di Nove C; una macchina senza codice è DA PREZZARE; le voci del
Committente fuori; la lista per il fornitore con la nota, e senza con `--senza-nove-c`; il comando con l'opzione, e
l'errore se manca `--lista`). La regola è scritta come decisione del PO: **D-241**, con la frase di I-314.

**2b — il bollitore col serpentino** (D-243, I-315, I-321, I-323, I-329). Il dato `superficie_scambio_m2` nel modello e
nelle istruzioni di Capire; la tabella delle apparecchiature lo scrive («200 l · serpentino 2,5 m²»); la voce della
lista dice «a serpentino maggiorato per pompa di calore, superficie di scambio non minore di X m²», con X dal manuale
Shenling §2.3 (2,0 m² 6–9 kW, 2,5 m² 12–15 kW, smaltata; 1,4 e 1,6 m² inox). **Di base la specifica della macchina**
(I-329); un serpentino più piccolo lo accetta il progettista, scrivendo il minimo sul bollitore
(`superficie_minima_scambio_m2`); per una pompa di calore non Shenling, o un serpentino né smaltato né inox, è una
domanda. Nel listino la riga del bollitore dice la sua superficie; sotto il minimo è
uno scostamento ⚠ nel confronto. Il serpentino sotto il minimo e il tubo pompa di calore – bollitore oltre 5 m sono
avvisi. Prove nello stesso file (inox e taglie; la domanda per la Haier; il bollitore senza pompa di calore non
cambia; gli avvisi; la tabella; il listino e il confronto: con la 12 kW vince Abbattista, con la 15 kW sono sotto
tutti e due; il progettista che accetta il Bolly da 2 m²). La tavola: §1.

**2c — il rame «CONDY»** (I-316). Le righe 50 e 51 del §5 del listino prendono F01b e F03b, con la nota della
deduzione (nel preventivo non c'è isolante per il rame). Su PR.MI.059 il rame si compra ora da Idrosanitaria
(4,34 e 9,50 €/m contro 6,52 e 10,80 di Tecnomat).

**2d — il raccordo all'attacco** (I-317, I-322, I-327). Il testo è «Raccordo diritto a pressare M {attacco} × tubo …,
all'attacco»; il pollice viene dal pezzo (`attacco`, dalla scheda), dal manuale Shenling (1" / 1¼"), o dalla scheda
del Bolly 1 XL di Cordivari porta per porta (I-328: primario 1¼", ACS e acqua fredda secondo la taglia). Senza, la voce
è DA DEFINIRE e `--domande` chiede il pollice dell'attacco di quel pezzo: mai il pollice del tubo.

```
$ python3 -m pytest tests/distinta/test_le_giunzioni.py -q -k pollice
1 passed
```

Sul caso della centrale (`test_il_corredo_idronico_e_il_costo.py`) il raccordo all'attacco senza dati diventa una
domanda; sul T1 del banco le domande nuove sono gli attacchi di bollitore, collettore e reti esistenti. **Su PR.MI.059
non si può provare sul grafo** (non è nel repository): le tre voci «all'attacco» della lista (P-I.33, P-I.35, P-I.40)
con la 2.2 uscirebbero col pollice del bollitore se il grafo dice «Cordivari Bolly 1 XL», o come domanda.

**2e — le quantità nette** (D-242, I-320). Il fattore della regola delle lunghezze è 1: niente ×1,15. Restano il metro
per tratto delle linee aria, frigo ed elettriche, il mezzo metro per eccesso e i minimi (proposta, §5). I documenti lo
dicono («indicative e nette»).

```
$ python3 -m pytest tests/distinta/test_regole_e_lunghezze.py -q -k nette
1 passed
```

Le prove vecchie che contavano le quantità maggiorate sono aggiornate ai numeri netti, ciascuna con la ragione scritta
(il caso AA-01 ha un elenco `NETTE` con le tre voci che ora stanno sotto il kit: B.1, E.5, E.8).

## 4. Le prove di sempre

```
$ python3 -m pytest -q
3191 passed, 15 skipped, 11 xfailed in 337.20s   (skip e xfail: gli stessi di REL-027; il diff delle prove non ne aggiunge)

$ ruff check src tests
All checks passed!

$ mypy
Success: no issues found in 133 source files

$ python3 scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (157 file, 3774 kB); ZIP sha256 469792ace3da33f6 → releases/latest/DisegnatoreMEP-v2.2.0.zip
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.

$ python3 -m pytest tests/test_le_release.py tests/test_package.py tests/skill -q
50 passed
```

La release è in `releases/latest/DisegnatoreMEP-v2.2.0.zip` (e in `releases/archive/`).

## 5. Che cosa decide il PO, e che cosa ho scelto io

- **I 2 m² per la 12 kW** (I-326, arrivati dalla sessione precedente): **ritirati dal PO** (I-329), valgono i valori
  del manuale Shenling; l'eccezione la decide il progettista. La scheda del Bolly 1 XL (I-328) l'ha trascritta l'altra
  sessione: non l'ho letta dal PDF (www.cordivari.it non si apre da qui).
- **Quali attacchi del bollitore restano liberi** in un impianto tipo (ricircolo, resistenza, il secondo pozzetto, lo
  scarico): serve per contare i tappi e le riduzioni (I-327). Non l'ho fatto.
- **Le quantità nette, fin dove**: ho tolto solo il ×1,15 (la disposizione). Restano il metro per tratto e i minimi
  delle linee: se il PO li vuole togliere, è una riga.
- **La Haier nel preventivo Idrosanitaria**: è da dire al fornitore.
- **Scelte della sessione**: gli ID della famiglia M nel listino; il prezzo delle macchine per modello (la marca conta);
  la scritta «serpentino 2,5 m²» in tabella; il raccordo all'attacco prezzato col codice del raccordo del tubo; la
  serpentina «smaltata» quando il grafo non dice il materiale.
- Resta da sapere **in quale conversazione è stata fatta la lista di PR.MI.059** (pacchetto, punto 2).
