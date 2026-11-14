# REL-026 — Blocco B, la pianta (prima parte): rapporto

**Scritto il 13 novembre 2026** dall'agente esecutivo del blocco B (D-152). Base: `d9c8f2e` (il pacchetto
REL-026 sopra la 2.0.0). Quello che segue non è una misura per l'orchestratore finché non l'ha rieseguito.

> Il worktree dell'agente era nato su `54262a1` (la 1.15.0), che non ha REL-026: il ramo dell'agente, ancora
> senza lavoro, è stato portato su `d9c8f2e` prima di cominciare. Nessun altro ramo è stato toccato.

## 1. Le tavole, per prime

Tutte le tavole escono, da ogni caso. Si rifanno con
`.venv/bin/python docs/collaudi/REL-026/blocco-b/rifai_le_tavole.py` (il «prima» gira sulle sorgenti della
base estratte con `git archive`); formato, scala e avvisi di ognuna sono in `misure.txt`.

| cartella | che cosa guardare |
|---|---|
| `t3/prima/pianta.png` → `t3/dopo/pianta.png` | il collaudo T3 del banco: **spariscono F1…F5, l'elenco FORATURE e la voce in legenda; la tavola passa da A2 ad A3** (la colonna è più corta). Il disegno è lo stesso |
| `t3/dopo-forature-accese/` | con `"forature": true`: **i quattro PNG sono identici a quelli della base, byte per byte** (`misure.txt`) |
| `t3/*/pianta-dettaglio-B.png` | spariscono F2 e F5; la colonna dice «Tratte, lunghezze e avvisi» |
| `sagome/senza-sagome/` → `sagome/con-sagome/` | il caso anonimo: senza sagome le tramezze chiare entrano nei muri scuri e la gamba verticale della tramezza a L sporge sopra quella orizzontale (si vede bene nel **dettaglio A**, 1:20); con le sagome gli angoli sono puliti. C'è anche il DXF |
| `discordanze/prima/discordanze.png` → `discordanze/dopo/discordanze.png` | il T3 con 49 discordanze, con distinta e grafo: **prima A1**, con il disegno piccolo e una colonna di 49 avvisi; **dopo A3**, come senza confronto (`discordanze/dopo-senza-confronto/`), con quattro righe di riassunto |
| `lunghezze/giro-1/`, `lunghezze/giro-2/` | la pianta di B-4 al primo giro e dopo aver spostato TA-01 di un metro (T01 da 2,8 a 3,8 m) |
| `lunghezze/schema-prima/` → `lunghezze/schema/` | lo schema rifatto dal grafo aggiornato: le lunghezze dei rami, dei bus e della linea dell'unità esterna sono quelle misurate in pianta |

### Quello che le tavole hanno mostrato e i numeri no

1. **Due lunghezze sulla stessa tratta** (corretto). Alla prima stesura B-4 scriveva una misura per tronco: lo
   schema rifatto aveva sulla linea quadro – sezionatore – unità esterna «3G4 · L 10,19 m» e «3G4 · L 0,44
   m». La distinta sommava giusto (10,63 m) e tutte le prove passavano. La convenzione è una lunghezza per
   tratta, sulla prima tubazione, come la scrive il progettista e come `completa` la tiene quando spezza una
   tubazione: ora è così (commit `1217bb1`), con la prova che lo schema ha una scritta sola.
2. **La colonna del dettaglio nominava le forature spente** (corretto, `99023da`): «Tratte, lunghezze,
   forature e avvisi: tavola pianta».
3. **Lo schema scrive le misure al millimetro**: «L 3,465 m», «L 5,105 m», «L 2,365 m». È voluto (§3,
   B-4), ma a vedersi è strano: **da decidere dal PO** (§7).
4. **Con le sagome le tramezze perdono il grigio chiaro**: una sagoma non dice il tipo del muro, e prende il
   grigio del perimetrale (come nella copia di BD.RM.260). Lo standard della base lo fissa C-3.
5. **Il T3 e l'appartamento dell'esempio passano da A2 ad A3**: senza l'elenco delle forature la colonna ci
   sta. A3 si legge bene (guardato); è un cambio visibile da approvare.
6. Già noto, non di questo blocco: i riquadri di dettaglio automatici del T3 (B, C) sono fogli A3 quasi vuoti
   (C-1 li toglie).

## 2. Voce per voce

### B-1 — il nome corto dei fluidi idronici

**Fatto** (`ace3820`). «Acqua risc.», «ACS», «AFS» nella colonna «Fluido» della tabella delle tratte. La
copia della commessa usava la chiave `domestic_cold_water`, che non esiste: l'acqua fredda è `cold_water`.
`chilled_water` non è un fluido della pianta e non è nella tabella. La prova misura il nome di ogni fluido della
pianta contro lo spazio fra le colonne «Fluido» e «Da» (26 mm): prima della correzione «Acqua di
riscaldamento» misurava 29,3 mm, «Acqua calda sanitaria» 27,0, «Acqua fredda sanitaria» 28,2.

Prova: `tests/pianta/test_rilievi_bd_rm_260.py::test_il_nome_del_fluido_sta_nella_sua_colonna` (13 fluidi). Il
caso delle sagome è idronico e lo mostra sulla tavola. Nessuna tavola del banco cambia per B-1 (il T3 è
aria-aria).

### B-2 — `sagome_muri`

**Fatto** (`c494106`). Campo facoltativo della pianta: un poligono per muro, in metri, almeno tre punti (una L è
un poligono solo). Se c'è, il retino si disegna sulle sagome; i `muri` restano per l'instradamento e per gli
ingombri delle scritte e dei controlli. Nel riquadro di dettaglio le sagome si ritagliano sulla zona; nel DXF
sono HATCH sul layer `A-WALL`. **`muri_visibili` non entra**, e una prova lo verifica (il campo è rifiutato).
`schemas/pianta.schema.json` rigenerato dal modello (lo controlla `test_lo_schema_dichiarato_e_quello_del_modello`);
`skill/pianta/ISTRUZIONI.md` §4 ha la riga, con le aperture come buchi della sagoma.

Il disegno della base sta in due funzioni, `retino_dei_muri` e `disegno_delle_aperture` (`pianta/tavola.py`),
pronte per C-3; colori e stile non sono cambiati (senza sagome le tavole del banco sono identiche).

Caso anonimo: `examples/pianta/casi/sagome-muri.json` — appartamento a L, portante 45 cm, perimetrali 30,
tramezze 10 e 15, una tramezza a L, porte e finestre, dettaglio A sull'angolo della L; aggiunto ai casi di
`tests/pianta/conftest.py`, quindi passa anche per le prove comuni (niente diagonali, niente scritte su linee,
niente bloccanti).

Prove: `test_con_le_sagome_il_retino_sta_sulle_sagome` (17 aree, vertici uguali alle sagome),
`test_senza_le_sagome_il_retino_e_quello_di_sempre` (percorsi e misure identici con e senza sagome),
`test_con_le_sagome_gli_ingombri_restano_i_muri`, `test_nel_dettaglio_le_sagome_si_ritagliano`,
`test_nel_dxf_le_sagome_sono_campiture_sul_layer_dei_muri` (17 HATCH su `A-WALL`), `test_una_sagoma_vuole_tre_punti`,
`test_muri_visibili_non_c_e`.

**Aperto**: un muro ad anello va spezzato in più sagome (un poligono non ha buchi); le sagome non si
confrontano con i muri (una sagoma lontana dal suo muro passa senza avviso).

### B-3 — le forature spente di base

**Fatto** (`44fb2b4`, `99023da`). Campo `forature` della pianta, `false` di base. Spente: niente F1/F2 sulla
tavola e nei dettagli, niente voce in legenda, niente elenco FORATURE né «Fori per i pezzi a parete», niente
rilievo `fori_fuori_dalle_aperture`, e nei dati `forature: []`, `fori_dei_pezzi: []`, niente
`attraversamenti_di_parete`/`fori_nel_perimetrale` per tratta e niente `per_il_grafo`; il riassunto dice
«Forature: spente, come di base». Accese: tutto come prima — **i PNG del T3 sono identici alla base**.
Il costo della foratura nell'instradamento e i passaggi nei muri non cambiano: le prove confrontano percorsi e
lunghezze a forature spente e accese, e il muro senza aperture si fora come prima.

Prove: `test_di_base_le_forature_non_si_scrivono`, `test_accese_le_forature_tornano_come_prima`,
`test_il_riassunto_dice_che_le_forature_sono_spente`; adattate, col perché scritto nella prova:
`test_collaudo_t3.py::test_i_tracciati_dicono_gli_attraversamenti_per_il_grafo` (ora a forature accese),
`test_instradamento.py::test_un_muro_senza_aperture_si_fora_e_lo_dice`, `test_tavola.py::test_il_comando_della_skill`,
`test_tavola.py::test_le_lunghezze_sono_quelle_del_percorso_disegnato`, `test_tavola.py::test_la_tavola_esce_a_1_50_con_tutti_i_file`
(l'appartamento da A2 ad A3).

**Il conteggio in distinta** — vedi §7, punto 1: la pianta non chiede più di riportare le forature; la
distinta, senza `attraversamenti`, continua ad assumerne una per ramo con la sua regola.

### B-4 — le lunghezze dalla pianta al grafo

**Fatto** (`9017507`, `1217bb1`). Con `--grafo`, dopo aver scritto le tavole, la pianta scrive nel file del
grafo le lunghezze misurate (`pianta/nel_grafo.py`), e dice in console e in `.tracciati.json` (`grafo`) che
cosa è cambiato: tratta, tubazione, prima, dopo. Rilanciata senza cambi non riscrive niente e lo dice.
`--grafo-in-sola-lettura` fa solo il confronto (opzione di `mep.py pianta`, in `src/disegnatore_mep/skill.py`:
`skill/scripts/mep.py` passa di lì senza modifiche).

**La forma della provenienza** — un dato solo, sulla tubazione, fra le `properties`:
`"lunghezza_dalla_pianta_m": <il numero che la pianta ha scritto>`. La `lunghezza_m` è della pianta se il dato
c'è ed è uguale a lei (entro mezzo millimetro); altrimenti è del progettista e non si sovrascrive. Così:

- **retrocompatibile**: un grafo senza il dato si legge come «del progettista» (il T3 del repository: la pianta
  non scrive niente); nessun campo nuovo nel modello `ConnectionModel`, `schemas/project.schema.json` invariato;
- **una correzione a mano resta** anche se il progettista dimentica di togliere il segno (il numero non è più
  quello del segno).

L'unità è la tratta: se il progettista ne ha dato la lunghezza — nella pianta o su una qualunque tubazione —
non si scrive niente, e la console elenca dove la pianta misura altro. Se no, la misura della tratta intera va
sulla prima tubazione (con un organo in linea, il tronco che parte da `da`), le altre restano senza lunghezza.
Solo `lunghezza_m` e il segno (e `attraversamenti`/`attraversamenti_dalla_pianta` a forature accese, con la
stessa regola): mai collegamenti né altri campi — la prova toglie i campi scritti e ritrova il grafo di prima,
campo per campo. Il file conserva rientro, separatori, accenti e ordine delle chiavi: dei grafi in
`docs/collaudi/` ed `examples/`, i 64 scritti da programma (compatti, o con rientro 1 o 2) si riscrivono
identici, e così il grafo completo che scrive oggi `completa` (provato sul T1 di REL-023); 4 scritti a mano con
oggetti su una riga no (il riassunto lo dice, `formato_conservato: false`).

La misura scritta non torna indietro come L prog.: il confronto la riconosce dal segno nel grafo, e la distinta
fatta da quel grafo scrive `"lunghezza_dalla_pianta": true` sulle sue tratte (solo quando è vero: le distinte di
prima sono identiche, il banco lo conferma), così anche `pianta --distinta` senza grafo non la prende.

Il numero scritto è `Lunghezza.misurata_m`, al millimetro: la distinta rifatta quota lo stesso numero della
pianta, tratta per tratta (misurato, sotto).

**Prova di accettazione** (T3 anonimo: pianta senza `lunghezza_m`, nove tubazioni del grafo senza lunghezza;
`misure.txt` e `tests/pianta/test_rilievi_bd_rm_260.py`, sezione B-4):

```
== giro 1: pianta --grafo
Grafo grafo-completo.json: scritte le lunghezze di 9 tratte
  - T01: — → 2,8 m (ramo-matrimoniale)
  ...
  - T10: — → 10,63 m (alim-quadro-sezionatore)
Lunghezze del progettista, lasciate come sono (la pianta misura altro): T06 9 m (misura 8,635 m); T07 9 m (misura 9,035 m); T08 8 m (misura 1,775 m); T09 8 m (misura 8,325 m); T11 10 m (misura 8,235 m); T15 2 m (misura 0,125 m)
== giro 1 rilanciato uguale
Grafo grafo-completo.json: nessuna lunghezza cambiata, il file non si riscrive
== giro 2: TA-01 spostata di un metro verso ovest
Grafo grafo-completo.json: scritte le lunghezze di 1 tratta
  - T01: 2,8 m → 3,8 m (ramo-matrimoniale)
```

1. grafo aggiornato — `test_1_la_pianta_scrive_nel_grafo_le_lunghezze_misurate`, `test_1_solo_le_lunghezze_mai_la_connettivita`
   (e il modello lo valida), `test_1_rilanciata_senza_cambi_non_scrive_niente`;
2. pezzo spostato, elenco dei cambi — `test_2_spostato_un_pezzo_l_elenco_dice_che_cosa_e_cambiato`;
3. schema e distinta rifatti portano i numeri nuovi — `test_3_schema_e_distinta_rifatti_portano_i_numeri_nuovi`: per le
   nove tratte `lunghezza_stimata_m` della distinta = misura della pianta e `lunghezza_da_quotare_m` uguale
   (in `lunghezze/`, dopo il giro 2: T01 misura 3,8 m, da quotare 6 m nella distinta e nella pianta; T10
   10,63 → 13,5 e 13,5; T12 3,465 → 5,5 e 5,5; le tratte del progettista restano sue: T07 9 m → 12 e 12), lo
   schema scrive le misure e una sola scritta «3G4 · L 10,63 m»; `test_3_con_la_sola_distinta_la_misura_non_e_l_prog`;
4. lunghezza data a mano resta e si segnala — `test_1_le_lunghezze_del_progettista_restano_e_si_segnalano`
   (frigo, cavo UI-UE, condensa: nemmeno la tubazione senza lunghezza della condensa si tocca),
   `test_4_una_lunghezza_corretta_a_mano_resta` (corretta nel grafo col segno vecchio, e data nella pianta).

Inoltre `test_in_sola_lettura_il_grafo_non_si_scrive`, `test_un_grafo_senza_provenienza_non_si_sovrascrive`,
`test_a_forature_accese_si_scrivono_anche_gli_attraversamenti`, `test_a_forature_spente_gli_attraversamenti_non_si_scrivono`,
`test_una_tratta_ha_una_lunghezza_sola`, `test_la_provenienza_di_una_lunghezza`,
`test_la_misura_scritta_non_diventa_la_lunghezza_del_progettista`. Rotta di proposito la regola della
provenienza, quattro di queste prove vanno rosse (controllato, poi ripristinato).

Il banco lancia la pianta con `--grafo-in-sola-lettura`, per non toccare i file del repository
(`scripts/banco.py`). Istruzioni: `skill/pianta/ISTRUZIONI.md` §2 e §4 «Le lunghezze nel grafo»; `skill/SKILL.md`
una riga e il comando con `--grafo` (460 righe su 500).

### B-5 — il confronto non cambia il foglio

**Fatto** (`a11abd3`). **La causa, riprodotta**: l'elenco degli avvisi del confronto si impaginava per intero
nella colonna, e la colonna che non entrava portava la tavola al formato dopo. Sul T3 con 49 discordanze (numeri
di tratta che la distinta non ha, tratte della distinta non in pianta, sigle diverse, lunghezze diverse dal
grafo), sulla base:

```
senza confronto A3 · con --grafo A2 (19 avvisi) · con --distinta A2 (30) · con tutti e due A1 (49)
```

Ora sulla tavola le discordanze sono una riga — quante, di che tipo, dove leggere il resto —, i bloccanti con i
numeri di tratta; per esteso stanno in console e in `.tracciati.json` (`confronto.avvisi`, e
`confronto.avvisi_per_tipo`). Lo stesso caso esce **A3 in tutti e quattro i modi**. Anche l'avviso «L prog.
presa dalla distinta o dal grafo» è raggruppato per fonte.

Prove: `test_con_o_senza_il_confronto_il_foglio_e_lo_stesso`, `test_sulla_tavola_le_discordanze_sono_riassunte`,
`test_per_esteso_nei_dati_e_in_console`, `test_i_bloccanti_si_riassumono_coi_numeri_di_tratta`.

**«Con B-4 gran parte degli avvisi deve sparire da sola»: verificato solo in parte.** Sul caso di B-4, dopo lo
spostamento di TA-01, la pratica della 2.0.0 (misure ricopiate a mano nel grafo) dà 3 avvisi, fra cui «Misura
oltre il 15 % di L prog.: T01 3,8 m su 2,8», con T01 quotato 4,5 m sul dato vecchio; con B-4 gli avvisi sono
ancora 3, ma quello sul dato vecchio non c'è più, il grafo ha 3,8 m e la tavola quota 6 m sulla misura. **Il
numero degli avvisi non cala** su questo caso. I 72 della commessa non si possono scomporre senza i suoi file;
su un impianto idronico è probabile che molti siano «tubazione del grafo non in pianta» per le tubazioni della
centrale, che B-4 non tocca e B-5 riassume (§7, punto 6).

## 3. I controlli

```
$ .venv/bin/python -m pytest -q -p no:cacheprovider
2971 passed, 15 skipped, 11 xfailed in 260.22s (0:04:20)
$ .venv/bin/python -m ruff check src tests scripts skill/scripts
All checks passed!
$ .venv/bin/python -m mypy
Success: no issues found in 128 source files
$ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_il_banco.py tests/test_le_release.py
35 passed in 24.57s
```

Base: `2922 passed, 15 skipped, 11 xfailed`. Le 49 in più sono le prove nuove: 43 in `test_rilievi_bd_rm_260.py`
e 6 del caso delle sagome nelle prove parametrizzate sui casi della pianta; skip e xfail sono gli stessi.

## 4. Il banco

```
$ .venv/bin/python scripts/banco.py
... 27 uguali, 1 cambiati, su 28
collaudo-t3-rel012: CAMBIATO
  ~ pianta/pianta-dettaglio-A.svg, pianta-dettaglio-B.svg, pianta-dettaglio-C.svg, pianta.svg, pianta.tracciati.json
```

Perché, uscita per uscita:

- `pianta.svg` — B-3: niente F1…F5, niente voce «Foratura» in legenda, niente sezione FORATURE; la colonna più
  corta porta la tavola da A2 ad A3 (`t3/prima` → `t3/dopo`);
- `pianta-dettaglio-A/B/C.svg` — B-3: niente F nei dettagli, niente voce in legenda, «Tratte, lunghezze e avvisi»;
- `pianta.tracciati.json` — B-3 (`forature_accese`, niente forature né `per_il_grafo`), B-5 (`avvisi_per_tipo`),
  B-4 (la sezione `grafo`: nessuna lunghezza da scrivere, tutte del progettista).

B-1 e B-2 non cambiano il banco (il T3 è aria-aria e non ha sagome). Impronte registrate con
`scripts/banco.py --caso collaudo-t3-rel012 --registra`.

## 5. I file toccati

`src/disegnatore_mep/pianta/{modello,tavola,comando,confronto}.py`, `src/disegnatore_mep/pianta/nel_grafo.py` (nuovo),
`src/disegnatore_mep/skill.py` (l'opzione), `src/disegnatore_mep/distinta/uscite.py` (il segno sulle tratte),
`schemas/pianta.schema.json`, `skill/pianta/ISTRUZIONI.md`, `skill/SKILL.md`, `scripts/banco.py`,
`examples/pianta/casi/sagome-muri.json`, `tests/pianta/*`, `tests/banco/impronte.json`, questa cartella. Nulla del
blocco A.

## 6. Nessun dato di cliente

I casi sono anonimi (il T3 e l'appartamento del repository, il caso delle sagome inventato); BD.RM.260 compare
solo come riferimento nei commenti e nelle prove.

## 7. Da decidere dal PO

1. **Le forature in distinta (B-3).** Spente, la pianta non porta più `attraversamenti` al grafo; ma la
   distinta, quando il grafo non li dà, ne assume uno per ramo (`attraversamenti_se_mancano`, «regola Nove C:
   una parete per ramo»), e la voce «foratura» resta. «Niente conteggio in distinta» alla lettera vorrebbe
   togliere anche quella: è un contenuto della distinta e non l'ho toccato. Scelta conservativa: la distinta
   com'è.
2. **La precisione delle lunghezze scritte (B-4).** Al millimetro, come le misura la pianta: pianta e distinta
   quotano lo stesso numero, ma lo schema scrive «L 3,465 m». Arrotondarle al centimetro o al decimetro è
   possibile, a patto che la pianta quoti sullo stesso numero arrotondato (cambia di poco qualche quota).
3. **Una lunghezza del progettista scritta solo nella pianta (B-4).** Se il tracciato ha `lunghezza_m` e il
   grafo no, la pianta non la copia nel grafo (scrive solo misure) e la elenca fra quelle del progettista; la
   distinta resta senza. Copiarla sarebbe comodo, ma è un dato del progettista che passa da un file all'altro.
4. **Dove vanno le lunghezze (B-4).** Nel grafo completo, come fa `vaso`: rilanciando `completa` si perdono, e
   va rilanciata la pianta (scritto nelle istruzioni). In alternativa si scriverebbero nel grafo di prima
   stesura, ma lì le tubazioni non sono ancora spezzate dagli accessori.
5. **Il formato del T3 e dell'esempio (B-3)**: A2 → A3, e il riassunto delle discordanze (B-5): la forma del
   testo è una proposta.
6. **Le tubazioni del grafo «non in pianta» (B-5)**: su un impianto idronico la centrale ha molte tubazioni
   corte che la pianta non disegna, e ognuna è un avviso. Proposta: non contarle quando nessuno dei due capi è
   in pianta. Non fatto: cambia il controllo, non il formato.

## 8. Quello che non è stato fatto o verificato

- **La misura sulla commessa** (i 72 avvisi di `pianta --grafo`, il retino sulle sagome di BD.RM.260): i file non
  sono in questa sessione; va fatta in sessione sui file del PO.
- Il rapporto del pacchetto (`docs/collaudi/REL-026/RAPPORTO.md`), la versione e la release: dell'orchestratore.
- La CI non è girata (niente push, per disposizione).
- Con `pianta --distinta` senza `--grafo`, dopo B-4, l'avviso dice ancora «Da riportare nel grafo» per le misure
  che nel grafo ci sono già: senza il grafo la pianta non sa se la misura di adesso è quella scritta.
- La CLI del repository (`python -m disegnatore_mep pianta`) non ha mai avuto `--distinta`/`--grafo`, e non li ha
  ora: il confronto e la scrittura passano dal comando della skill.
- `sagome_muri` non ha ancora un esempio nella skill (`dati/esempi/`): c'è il caso in `examples/pianta/casi/`.
