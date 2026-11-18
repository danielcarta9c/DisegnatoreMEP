# REL-028, punto 2 — Due liste complete, il bollitore col serpentino, il rame «CONDY», il pollice all'attacco, le quantità nette — rapporto

**18 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md`, punto 2 (I-314 … I-320), con le indicazioni del PO arrivate
in sessione dalla sessione precedente (I-325 … I-328). Ramo `claude/rel-028-punto-2`. Il punto 1 (il rilievo Tecnomat
Pro) non è in questo lavoro: aspetta il file del PO.

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

## 2. La misura su PR.MI.059

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
apparecchiature: 8 voci, prezzate 8, totale 6946.00 €
  P-A.1 Pompa di calore aria-acqua: Shenling ThermaX R290 12 kW      3103.60 €
      Idrosanitaria    3103.60 €  ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa
  P-A.2 Bollitore ACS — 200 l, a serpentino maggiorato …, non minore di 2 m²   626.52 €
      Idrosanitaria     461.40 €, serpentino 0.8 m²  ⚠ serpentino 0,8 m², sotto il minimo di 2 m²
      Abbattista        626.52 €, serpentino 2 m²
  P-A.3 Volano termico a quattro attacchi, 80 l                        156.49 €  (Idrosanitaria; Abbattista 179.29)
  P-A.4 Pompa di circolazione: DAB Evosta 2 40-70/130                   93.60 €  (Idrosanitaria; Abbattista 96.52)
  C-A.1 Unità esterna: Daikin RZASG71MV1                              1017.27 €
  C-A.2 Unità interna canalizzata: Daikin FBA71A9                      835.78 €
  C-A.3 Plenum motorizzato di zona: Airzone Easyzone 4×200             993.61 €
  C-A.4 Comando a filo dell'unità: Daikin BRC1H52W7                    119.12 €
voci 99, prezzate 90, da prezzare 9; totale 8987.67 €
ordine: 8850.12 € + senza fornitore 137.55 €
…
avviso M01c: Idrosanitaria 3103.60 € ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa
avviso M10b: Idrosanitaria 461.40 € ⚠ serpentino 0,8 m², sotto il minimo di 2 m²
```

(l'output intero è nel file `pr-mi-059/costo-minuteria.md` di REL-027, rifatto.)

**In parole.**

- **La lista prezzata completa** è 8.987,67 € netti su 90 voci: 6.946,00 € di apparecchiature e 2.041,67 € di
  minuteria (era 2.065,98 € in REL-027: −24,31 € per il rame «CONDY» di Idrosanitaria, 2c). Le 9 voci DA PREZZARE
  sono le stesse di REL-027 (137,55 € di riferimento).
- **Il bollitore**: col minimo di 2 m² per la 12 kW (I-326) il Bolly 1 XL WB 200 di Abbattista (2 m², dalla scheda
  Cordivari) rispetta la voce, e il conto lo sceglie anche se costa 165,12 € in più; il Bolly 1 ST WB 200 di
  Idrosanitaria (0,8 m²) è uno scostamento, e diventa un avviso. Con i 2,5 m² del manuale sarebbero stati sotto tutti e due.
- **La pompa di calore del preventivo Idrosanitaria non è una Shenling.** Il codice AW12NMXGHA, nelle schede dei
  rivenditori, è una **Haier GT R290 12 kW trifase** ([groupsumi](https://groupsumi.it/en/climate-control/aerothermal-energy/monobloc-air-to-water-heat-pump/haier-gt-r290-12-kw-monobloc-air-source-heat-pump-three-phase-aw12nmxgha));
  non ho trovato la scheda di Haier. Nel listino è uno scostamento: il conto la prende perché non c'è altro prezzo per la
  Shenling 12 kW, e la avvisa. **Il CAPEX della pompa di calore è quindi quello di un'altra macchina.**
- I termostati di zona Airzone non sono nella misura: la lista non dice quanti sono.

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

**2b — il bollitore col serpentino** (D-243, I-315, I-321, I-323, I-326). Il dato `superficie_scambio_m2` nel modello e
nelle istruzioni di Capire; la tabella delle apparecchiature lo scrive («200 l · serpentino 2,5 m²»); la voce della
lista dice «a serpentino maggiorato per pompa di calore, superficie di scambio non minore di X m²», con X dal manuale
Shenling §2.3 (2,0 m² 6–9 kW, 2,5 m² 15 kW, smaltata; 1,4 e 1,6 m² inox) e **2,0 m² per la 12 kW, disposizione del
PO (I-326)**; per una pompa di calore non Shenling, o un serpentino né smaltato né inox fuori dalla 12 kW, è una
domanda (`superficie_minima_scambio_m2`). Nel listino la riga del bollitore dice la sua superficie; sotto il minimo è
uno scostamento ⚠ nel confronto. Il serpentino sotto il minimo e il tubo pompa di calore – bollitore oltre 5 m sono
avvisi. Prove nello stesso file (inox e taglie; la domanda per la Haier; il bollitore senza pompa di calore non
cambia; gli avvisi; la tabella; il listino e il confronto: con la 12 kW vince Abbattista, con la 15 kW sono sotto
tutti e due). La tavola: §1.

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
SUITE_FINALE

$ ruff check src tests
All checks passed!

$ mypy
Success: no issues found in 133 source files

$ python3 scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (157 file, 3765 kB)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.

$ python3 -m pytest tests/test_le_release.py tests/test_package.py tests/skill -q
50 passed
```

La release non è ancora in `releases/`: **il numero lo decide il PO** (la proposta è 2.2.0).

## 5. Che cosa decide il PO, e che cosa ho scelto io

- **Conferma delle indicazioni arrivate dalla sessione precedente** (I-325 … I-328): i 2 m² per la 12 kW e la scheda del
  Bolly 1 XL non li ho letti dal PO né dal PDF (www.cordivari.it non si apre da qui): li ha trascritti l'altra sessione.
- **Quali attacchi del bollitore restano liberi** in un impianto tipo (ricircolo, resistenza, il secondo pozzetto, lo
  scarico): serve per contare i tappi e le riduzioni (I-327). Non l'ho fatto.
- **Le quantità nette, fin dove**: ho tolto solo il ×1,15 (la disposizione). Restano il metro per tratto e i minimi
  delle linee: se il PO li vuole togliere, è una riga.
- **La Haier nel preventivo Idrosanitaria**: è da dire al fornitore.
- **Scelte della sessione**: gli ID della famiglia M nel listino; il prezzo delle macchine per modello (la marca conta);
  la scritta «serpentino 2,5 m²» in tabella; il raccordo all'attacco prezzato col codice del raccordo del tubo; la
  serpentina «smaltata» quando il grafo non dice il materiale.
- Resta da sapere **in quale conversazione è stata fatta la lista di PR.MI.059** (pacchetto, punto 2).
