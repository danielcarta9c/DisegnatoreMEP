# REL-016, D3 — Il collettore di zona a più vie

**Il rilievo** (collaudo della 1.7.0, `../../REL-015/collaudo-1.7.0/RAPPORTO.md`, D3): il catalogo
aveva il collettore con ritorno a due vie e basta; il «collettore a pavimento a 6 vie» della
villetta del collaudo non si disegnava, e la tavola portava un pannello rappresentativo con la
scritta «impianto a pavimento (collettore a 6 vie)».

**La tavola:** `tavola/villetta-pdc-aria-acqua-idraulica-t1.png` (PDF accanto). Si rifà con
`bash docs/collaudi/REL-016/d3/rifai.sh`.

## Che cosa c'è

- **Le voci:** `zone-manifold-pair-3` … `zone-manifold-pair-12`, «Collettore di zona con ritorno a
  tre … dodici vie», una per numero come il plenum di zona da 2 a 6 uscite. Porte `in`, `out` a
  sinistra; sotto `out_1 … out_N` e `ret_1 … ret_N`, tutte obbligatorie; i passaggi di quello a
  due (`in` con tutte le mandate, tutti i ritorni con `out`). Catalogo da
  `examples/layout/build_layout_fixtures.py`, simboli da `examples/graphics/build_symbols.py`.
- **Quello a due vie resta `zone-manifold-pair`**, senza numero: manifesto, corpo e voce sono i
  file della 1.7.0 all'ultimo byte (la prova ne tiene l'impronta).
- `capire.md`: la voce dice le vie, un terminale per via; `comporre.md`: la riga della tabella
  delle porte e la posa dei terminali sotto le vie.

## Il simbolo — una proposta, che il PO approva sulla tavola

**Com'è fatto:** lo stesso disegno del collettore a due vie della 1.7.0 (I-231), allungato: due
barre continue, la mandata sopra e il ritorno sotto, e per ogni via la sua coppia di attacchi in
basso a **10 mm** (come gli attacchi dei terminali, I-205), **una coppia ogni 20 mm**. La discesa
della mandata passa dietro la barra del ritorno, interrotta. Alto 15, largo **20 mm per via**: 120
a sei vie, 240 a dodici.

**Le alternative considerate:**

1. **Le coppie più strette** (mandata e ritorno alternati a 5 mm, o una coppia ogni 15): il
   collettore sarebbe più corto, ma i terminali larghi 15 non starebbero più sotto la loro coppia
   — tornano le pieghe che il PO ha tolto in REL-009 («paghiamo inutilmente un sacco di curve»,
   I-205). Scartata.
2. **Due collettori separati**, mandata e ritorno come due pezzi, come sono davvero a pavimento:
   due voci al posto di una, il circuito che passa per due pezzi, e un disegno diverso da quello a
   due vie già approvato. Scartata.
3. **Una voce sola con il numero delle vie come proprietà**: il motore ha simboli a manifesto
   fisso, e il plenum ha già fissato la strada di una voce per numero. Scartata.
4. **Il segno compatto senza terminali** (il collettore con la scritta «6 circuiti»): è il
   pannello rappresentativo di prima con un altro nome. Scartato.

## La tavola esce in A2, non in A3 — da guardare

Il collettore a sei vie con i suoi pannelli è largo 120 mm, e porta la posa della villetta da
~305 a **405 mm**; l'area del disegno dell'A3 ne ha **350**. La skill dice di prendere il foglio
successivo invece di comprimere (comporre, D3, D-170), e la tavola è in **A2**: pulita, ma con
molto bianco. Ho provato a tenerla in A3 (collettore abbassato a destra del volano, circolatore
sulla discesa, primario stretto di 30 mm): si instrada con 0 bloccanti, ma il collettore tocca
la legenda (`DRAWING_TOUCHES_THE_BORDER`), mandata e ritorno si incrociano accanto al circolatore,
e 13 pieghe contro 7 (`alternativa-a3.png`, dal piano `alternativa-a3-piano.json`). Non è una
tavola migliore. **Se il PO vuole la villetta in A3, il
collettore a 20 mm per via è il vincolo**: a dodici vie (240 mm) occupa da solo due terzi
dell'area di un A3.

## Le misure

- `rifai.sh`: `Formato A2 · tratte 39 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 ·
  sormonti 1`; gli avvisi sono quelli del piano buono del collaudo, più
  `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` fra collettore e volano (interasse 10 contro 15 mm: lo
  aveva anche il pannello rappresentativo).
- Il banco di REL-011 fra la 1.7.1 e il ramo: **24 identiche su 24**.
- Le prove: `tests/catalog/test_il_collettore_a_piu_vie.py`, 33 prove; sul commit di partenza 32
  rosse — passa solo quella che tiene l'impronta del collettore a due vie, che è una guardia.

## Quello che a occhio non torna

- Il collettore **non ha una sigla** sulla tavola né una riga nella tabella delle apparecchiature
  — come quello a due vie e come i pannelli: è il comportamento di sempre, non di questo lavoro.
- Le valvole delle vie stanno **sfalsate** (quella della mandata più in basso di quella del
  ritorno): le posa il motore, come sul collettore a due vie.
