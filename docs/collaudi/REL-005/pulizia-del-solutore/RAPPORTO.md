# La pulizia del solutore — `REL-005`, punto 0.3 e punto 2

**2 ottobre 2026** · input **I-180** · decisione **D-197** (proposta)

Il PO: «Il vecchio solutore se non serve più certo va tolto. O viene ancora usato nella skill?» —
e, avuta la risposta, «Si ok procediamo a questa pulizia».

## Le tavole, per prime: non cambia niente

Le uscite che la pulizia non deve toccare sono **55 file**:
- le sette tavole di prova approvate;
- i cinque impianti di prova per la via del piano e per quella senza piano (`draw`);
- la tavola D della prova del PO, dalla skill costruita.

Si generano prima e dopo, con lo stesso script, e si confrontano byte per byte:

```
$ docs/collaudi/REL-005/pulizia-del-solutore/uscite.sh <prima>   # su main, 3365228
$ docs/collaudi/REL-005/pulizia-del-solutore/uscite.sh <dopo>    # sul ramo
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <prima> <dopo>
file: 55 prima, 55 dopo
IDENTICI
```

Le uscite sono deterministiche: due esecuzioni dello stesso codice danno file identici, a parte il
percorso della cartella scritto nei log, che lo script toglie prima di confrontare.

## Che cosa la skill usava, misurato

Il comando della skill non carica `improve.py` né `dilate.py`:

```
$ python3 -c "import sys, disegnatore_mep.skill; print(sorted(m for m in sys.modules if m.endswith(('.improve','.dilate'))))"
[]
```

E una prova sorvegliava già la via del piano, `draw` e la CLI intera. Però i due file
**viaggiavano nello ZIP**: 150 kB e 16 kB di codice che nessuno chiamava.

## Che cosa è uscito

| | prima | dopo |
|---|---|---|
| `layout/improve.py` | 3146 righe | tolto |
| `layout/dilate.py` | 374 righe | tolto |
| `layout/spine.py` | 1700 righe | 385: resta la semina, `carry_the_rest`, che l'esecutore usa |
| `layout/hierarchy.py::weight_of` | la scala 1 / 4 / 16 | tolta: la usava solo il costo del solutore |
| lo ZIP della skill | 822 kB, 287 file | 760 kB, 285 file |

Quello che resta del solutore lo dice `spine.py` in testa: che cosa ospitava, quando è morto
(D-151), quando è stato tolto (I-180), e che il codice sta nella storia di git. L'ultimo `main` che
lo porta è `3365228`. `tests/layout/test_il_solutore_e_fuori.py` sorveglia che non torni.

## La suite

| | `main` (`3365228`) | ramo |
|---|---|---|
| rosse | **46** | **0** |
| passate | 2036 | 1967 |
| `skip` | 24 | 15 |
| `xfail` | 12 | 10 |
| tempo | 15 min | 4 min 38 s |

`ruff check src tests` e `mypy src` verdi. Nessuno `skip` e nessuno `xfail` nuovi: quelli che
mancano sono usciti con le prove del solutore.

### Le prove tolte: 102, elencate in `prove-tolte.txt`

- **96 toccavano codice tolto.** Lo strumento che lo misura segue, per ogni prova, gli aiuti di
  modulo che usa, e dice se arriva a un nome del solutore: `Improver`, `improve_sheet`, `SheetCost`,
  `lay_the_spine`, `dilate_sheet`… Cinque file interi:
  - `test_traslazione_di_blocco`, `test_riempimento_del_foglio`, `test_assi_per_stato_idraulico`,
    `test_allineamento_del_tronco`;
  - `test_costo_per_gerarchia`, insieme a `weight_of`.

  Il resto sta dentro file misti.
- **6 misuravano la qualità della composizione senza piano**, che D-151 ha tolto al motore («il
  motore garantisce che la tavola sia valida e che i difetti siano nominati; il bello lo porta il
  piano», architettura §8):
  - la posa di partenza con ogni stacco al minimo;
  - la tavola 1 senza piano nei costi di `DRAW-005`;
  - i raccordi che non prendono una colonna nella posa senza piano;
  - il costo che non cambia rinominando, doppione di
    `test_i_nomi_non_muovono_la_geometria.py`, che passa;
  - i due `xfail` che aspettavano «che la composizione compatti».

Una prova è **sostituita**: `test_i_tre_moduli_dichiarano_di_essere_morti` diventa
`test_i_moduli_del_solutore_non_ci_sono_piu`.

### Le prove portate sul piano: tutte quelle che difendevano il motore

Le rosse che difendevano il **motore** cadevano tutte per lo stesso motivo: componevano **senza
piano**, e da D-167 quella via non instrada più il ritorno di un terminale con i due attacchi sullo
stesso lato. Ora eseguono un piano, come fa la skill.

- **I piani approvati** di `DRAW-018` per gli impianti 1 e 2:
  - le cinque prove di accettazione della tavola 1;
  - i tre accessori appesi;
  - le due tratte annidate;
  - due misure di asse e attraversamenti (`test_assi_sulle_tavole_dal_piano.py`).
- **Due piani nuovi**, in `tests/layout/piani/`, per le configurazioni «una / due macchine con
  accumulo combinato». Sono il piano approvato dell'impianto 1 tradotto sui nomi della prova: lo
  stesso impianto con altri nomi. Escono a zero tratte cedute, zero bloccanti e zero rilievi. Li
  usano:
  - i rami di servizio (8);
  - gli stacchi minimi (2);
  - la catena macchina (2);
  - la consegna (1).
- **Che non passino a vuoto**:
  - sulle tavole dal piano ci sono i rami statici, d'ingresso e di scarico che le prove misurano;
  - la prova riscritta sugli stacchi cade se si allontana di 20 mm una valvola di sicurezza.
- **Una prova riscritta**: «sulla tavola composta nessuno stacco è più lungo del minimo» misurava a
  mano il minimo di I-046 (due passi) e parlava del «ciclo». Ora chiede il controllo **A4** del
  motore, `organi_di_servizio_lontani`, con il minimo vigente: dieci millimetri per uno stacco vuoto
  (D-145, D-062). ⚠ Un mio errore, preso in tempo: avevo avvicinato al minimo di I-046 sfiato,
  scarico e gruppo di riempimento nei piani nuovi. Il piano approvato era giusto, e li ho rimessi.
- **Un'attesa superata**: `test_entering_means_respecting_the_minimum_distances` chiedeva la frase
  «does not fit on any ordinary sheet format». Da D-150 la scala dei formati, finita a vuoto,
  ricompone col ripiego, e il rifiuto nomina la misura senza quella frase. Resta l'attesa vera: il
  rifiuto nomina una misura.

I file del solutore che conservano prove vive hanno cambiato nome, e la riga `# categoria` dice
che cosa difendono adesso:
- `test_improve` → `test_caso_completo_senza_piano`;
- `test_costo_peso` → `test_la_via_senza_piano_e_deterministica`;
- `test_assi_dorsali_tee` → `test_i_nomi_non_muovono_la_geometria`;
- `test_posa_a_fasi` → `test_assi_sulle_tavole_dal_piano`.

## Il rilievo che la pulizia ha portato a galla

⚠ **Sulla tavola 1 dal piano due valvole che isolano stanno a 10 mm dal proprio attacco**:
- quella dell'acqua calda sull'uscita dell'accumulo;
- quella sulle utenze.

D-120 le vuole fra 2,5 e 5 mm. La prova che lo misura guardava solo la tavola senza piano, dove
reggeva; portata sul piano, è caduta. Correggerlo vuol dire cambiare la posa degli organi in linea,
e quindi le tavole approvate: non è una pulizia. La prova resta sulla via senza piano
(`_tavola_1_senza_piano`), e il rilievo è il **primo punto del debug**.

## Che cosa non è più eseguibile, e lo si sa

Gli strumenti di sessione di alcuni collaudi passati importano il solutore, e contro il codice di
oggi non girano più:
- `docs/collaudi/DRAW-002 … DRAW-013/metriche.py`, `criteri.py`, `allungo.py`, `tavola4.py`;
- `DRAW-009/le-due-sovrapposizioni.py`.

Sono documenti agli atti dei loro pacchetti: si rieseguono sul commit del loro tempo.
