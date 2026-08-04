# Architettura - Disegnatore MEP

## Fonte di verità

Il `ProjectModel` JSON è la fonte tecnica canonica. Elaborati grafici e distinte sono derivati.

## Moduli P0

- `model/`: entità e metadati indipendenti dal dominio.
- `catalog/`: definizioni versionate dei componenti e delle porte.
- `domains/`: compatibilità e validatori specifici per dominio.
- `validation/`: diagnostiche bloccanti e report strutturati.
- `io/`: round-trip JSON, canonicalizzazione e fingerprint.
- `cli.py`: interfaccia stabile per validazione, schema e foglio dei simboli.

## Modulo grafico

- `graphics/standard.py`: tutte le grandezze in millimetri di carta, istanza unica `A3_LANDSCAPE`. Unica autorita' sulle grandezze della carta.
- `graphics/symbol.py`: manifesto geometrico del simbolo. Porte sul perimetro con faccia coerente.
- `graphics/registry.py`: caricamento e validazione della libreria di simboli. La verifica incrociata con il catalogo vive in `catalog/registry.py`, che confronta gli insiemi di porte quando riceve un `SymbolRegistry`.
- `graphics/composite.py`: compositi assemblati da primitive e pubblicati come simbolo unico.
- `graphics/svg.py`: emettitore SVG a misura reale e foglio di riscontro A3.
- `graphics/errors.py`: `SymbolError`, unico errore del pacchetto, sollevato da manifesto, registro e compilatore dei compositi.

- `graphics/frame.py`: il telaio della tavola — squadratura, intestazione, riserva del cartiglio, fascia della legenda, area di disegno. Misure prese dal cartiglio Nove C (D-053).
- `graphics/sheet.py`: il renderer della tavola. `graphics/svg.py` resta il banco di prova della libreria, non la tavola.

La geometria vive nel simbolo, la semantica nella definizione di componente: si uniscono per
identificativo di porta (D-043), e `catalog/resolved.py` e' la vista che le tiene insieme.
Dettagli in `docs/GRAPHIC_STANDARD.md`.

## Modulo di layout

- `layout/grid.py`: nodi di griglia e il controllo che ogni porta di simbolo vi cada sopra (D-054).
- `layout/trunks.py`: ricompone le tratte che gli accessori in linea hanno spezzato nel modello.
- `layout/partition.py`: divisione in tavole e rimandi accoppiati (D-020, D-028).
- `layout/place.py`: posizionamento a fasce funzionali (D-041), dal piano di impaginazione (D-042).
- `layout/route.py`: instradamento ortogonale; l'incrocio costa meno del giro (D-041).
- `layout/inline.py`: gli accessori posati sulla tratta, che interrompono la linea (D-027).
- `layout/labels.py` e `layout/legend.py`: tag di valore e legenda dai soli simboli usati (D-052).
- `layout/geometry.py`: il modello geometrico derivato, con `drawing_fingerprint`.
- `layout/compose.py`: la catena completa, nell'ordine della specifica §10.1.
- `validation/geometry.py`: i controlli geometrici della specifica §12.2.

Il modello tecnico canonico **non contiene coordinate**: la geometria e' derivata e
rigenerabile (D-026).

## Librerie di simboli

- `assets/symbols/`: i dodici simboli pubblicati, generati da `examples/graphics/build_symbols.py`.
- `examples/foundation/symbols/`: gli otto simboli delle fixture, generati da `examples/foundation/build_fixtures.py`.

Entrambe si rigenerano identiche.

## Confini

Il nucleo non interpreta conversazioni, non applica best practice impiantistiche e non disegna. Fornisce i contratti verificati usati dai piani successivi.

## Comandi

Preparazione dell'ambiente, primo comando in una sessione cloud:

```bash
bash scripts/setup-env.sh
```

Uso del nucleo:

```bash
.venv/bin/python -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
.venv/bin/python -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog --symbols examples/foundation/symbols
.venv/bin/python -m disegnatore_mep fingerprint examples/foundation/valid-mixed-project.json
.venv/bin/python -m disegnatore_mep export-schema schemas/project.schema.json
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
.venv/bin/python -m disegnatore_mep draw examples/layout/heat-pump-dhw-buffer-two-zones.json \
  --catalog examples/layout/catalog --symbols assets/symbols --out outputs/
```

Su Windows in locale l'interprete è `.venv/Scripts/python.exe`.
