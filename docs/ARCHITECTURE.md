# Architettura - Disegnatore MEP

## Fonte di verità

Il `ProjectModel` JSON è la fonte tecnica canonica. Elaborati grafici e distinte sono derivati.

## Moduli P0

- `model/`: entità e metadati indipendenti dal dominio.
- `catalog/`: definizioni versionate dei componenti e delle porte.
- `domains/`: compatibilità e validatori specifici per dominio.
- `validation/`: diagnostiche bloccanti e report strutturati.
- `io/`: round-trip JSON, canonicalizzazione e fingerprint.
- `cli.py`: interfaccia stabile per validazione e schema.

## Confini

P0 non interpreta conversazioni, non applica best practice impiantistiche e non disegna. Fornisce i contratti verificati usati dai piani successivi.

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
```

Su Windows in locale l'interprete è `.venv/Scripts/python.exe`.
