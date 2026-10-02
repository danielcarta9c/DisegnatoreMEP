# La prima prova del PO su claude.ai — pompa di calore, deviatrice, pavimento, bollitore, volano

**2 ottobre 2026** · `REL-005`, punto 0.1 · input **I-171 … I-174**

Il PO ha caricato la skill e l'ha provata su un impianto suo: pompa di calore aria-acqua, valvola
deviatrice fra pavimento radiante e serpentina del bollitore ACS, volano termico a due attacchi in
serie sul ritorno. La tavola si è composta e disegnata, e il PO l'ha respinta: «Non va bene».

**Il suo DXF non è in questa cartella**: porta nome e indirizzo del cliente, e il repository è
pubblico. Grafo e posa qui accanto sono **ricostruiti dal DXF**, pezzo per pezzo e coordinata per
coordinata, senza i dati del cliente; la tavola A rifà la sua.

## Le tavole

| | grafo | piano | che cosa mostra |
|---|---|---|---|
| **A** | `grafo-com-era.json` | `piano-A-com-era.json` | la tavola del PO, rifatta, con il colore della serpentina corretto |
| **B** | `grafo-proposta-po.json` | `piano-B-proposta-po.json` | la disposizione del PO: deviatrice dritta sulla mandata, terza via in basso verso il bollitore |
| **C** | `grafo-proposta-po.json` | `piano-C-volano-abbassato.json` | come B, con il volano 10 mm più in basso |
| **D** | `grafo-proposta-po.json` | `piano-D-volano-coricato.json` | **la cura scelta dal PO** (D-196): la disposizione di B con il volano a due attacchi coricato e lo sfiato piccolo |

A, B e C sono disegnate con i simboli **di prima** — sono le tavole che il PO ha visto
rispondendo —; D con quelli nuovi.

Si rifanno così, dalla cartella della skill costruita (`python scripts/costruisci-skill.py`):

```bash
python3 scripts/mep.py completa <grafo> --out /tmp/po1/grafo-completo.json
python3 scripts/mep.py disegna /tmp/po1/grafo-completo.json --piano <piano> --out /tmp/po1/<A|B|C>
```

| | tratte cedute | bloccanti | pieghe | sormonti | rilievi delle regole |
|---|---|---|---|---|---|
| A | 0 | 0 | 6 | 1 | autostrada non dritta ×2 |
| B | 0 | 0 | 9 | 1 | autostrada non dritta ×2, **sali-scendi della mandata** |
| C | 0 | 0 | 9 | 1 | autostrada non dritta ×3 — la mandata no |
| **D** | 0 | 0 | **5** | 1 | autostrada non dritta ×1: il ritorno del pannello, che ha interasse 10 contro il 15 della pompa |

## Che cosa è successo, misurato

**Lo sfiato del volano sta sulla quota della mandata (I-172).** La pompa di calore ha la mandata a
+5 e il ritorno a +20 dal proprio cielo. Il volano a due attacchi ha gli attacchi a +5: per stare
sul ritorno il suo cielo sta 10 mm sotto la mandata, e lo sfiato è alto 10 mm. Nel DXF del PO lo
sfiato occupa da y=126 a y=136, e la mandata corre a y=136. Il compositore è uscito dalla mandata
10 mm prima del volano. Sulla disposizione del PO (B) la mandata lo scavalca con un sali-scendi di
2,5 mm per 137,5 mm; con il volano 10 mm più in basso (C) è dritta da un capo all'altro, e il
ritorno fa un gradino per parte al volano. Le istruzioni di Comporre (§2.1) dicono di posare il
volano «15 mm più in basso della pompa»: è esattamente la posizione in cui lo sfiato tocca.

**La deviatrice poteva girare, il grafo no (I-173).** Il piano l'aveva girata (270°: ingresso da
sotto, via dritta in alto verso il bollitore, terza via a destra verso il pavimento). Ma Capire ha
collegato la **via dritta** al bollitore e la **terza via** al pavimento: con quel grafo nessuna
delle otto giaciture dà «dritta verso il pavimento, terza via in basso verso l'ACS», e il grafo
approvato il compositore non lo tocca. Con le due uscite scambiate la disposizione del PO si
compone (B, C).

**Il ritorno della serpentina era rosso (I-174): difetto del motore.** Il volano in serie sul
ritorno ferma la camminata che risale dalla pompa di calore, e la tratta dalla serpentina al
raccordo restava indecisa; la regola che la decide cambiava ruolo solo ai terminali, e la tratta
ereditava la mandata che entra nel bollitore. Corretto in `layout/flow.py`: chi scambia calore con
un fluido che non è quello della rete — la serpentina — restituisce ritorno. La prova
`test_il_ritorno_della_serpentina_e_ritorno_anche_col_volano_in_serie` è rossa senza la correzione.

## La cura, scelta dal PO (I-175 … I-178, D-196)

- **«Prova 2 è quello corretto»**: su una deviatrice fra riscaldamento e ACS la via dritta va al
  riscaldamento e la terza all'ACS — una riga di Capire (§7).
- **Lo sfiato più piccolo**: `air-vent` 5 × 5 invece di 5 × 10, lo stesso segno, su tutte le tavole.
- **Il volano a due attacchi coricato e in linea, alto la metà**: `buffer-two-port` 25 × 10, attacchi
  in asse a +5. La metà esatta, 22,5 × 12,5, non sta sulla griglia da 2,5 mm (un lato con una porta
  centrata vuole un numero pari di passi); 25 × 10 tiene la larghezza di prima. Sul ritorno della
  pompa di calore il cielo dello sfiato resta 5 mm sotto la mandata: la tavola D ha mandata e
  ritorno dritti.
- **Le sette tavole di prova approvate**, rifatte con i simboli nuovi, sono in `tavole-di-prova/`,
  con i piani adattati agli appesi (`tavole_di_prova.py`): lo sfiato sale di 5 mm, così il suo
  attacco resta dov'era; sull'impianto 3 sfiato e scarico tornano addosso al volano coricato. Il
  piano dell'impianto 3 aveva messo lo sfiato **sopra la mandata**, con lo stacco che la
  attraversava («A4 cede a B1 … incrocio imposto»): era lo stesso difetto della prova del PO, e con
  il volano coricato l'incrocio sparisce.

## Quello che resta al PO

- lo scarico del volano resta rosso su tutte le tavole: è la regola vigente — uno stacco che
  pende da una macchina prende il colore base del fluido —, ma su un volano in serie sul ritorno
  il volume è ritorno.
