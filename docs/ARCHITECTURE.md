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
- `graphics/registry.py`: caricamento della libreria e verifica incrociata con il catalogo.
- `graphics/composite.py`: compositi assemblati da primitive e pubblicati come simbolo unico.
- `graphics/svg.py`: emettitore SVG a misura reale e foglio di riscontro A3.

La geometria vive nel simbolo, la semantica nella definizione di componente: si uniscono per
identificativo di porta (D-043). Dettagli in `docs/GRAPHIC_STANDARD.md`.

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
.venv/bin/python -m disegnatore_mep fingerprint examples/foundation/valid-mixed-project.json
.venv/bin/python -m disegnatore_mep export-schema schemas/project.schema.json
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
```

Su Windows in locale l'interprete è `.venv/Scripts/python.exe`.
