# Release — Disegnatore MEP

- `latest/` contiene esclusivamente l'ultima versione approvata e pronta da installare.
- `archive/` conserva i pacchetti ZIP numerati delle versioni pubblicate.

`latest/` non deve essere modificata manualmente durante lo sviluppo. Una release viene pubblicata soltanto dopo verifica dei test, controllo degli artefatti e approvazione.

Convenzione prevista: `DisegnatoreMEP-vMAJOR.MINOR.PATCH.zip`.

## Le release pubblicate

- **1.2.0** — 2 ottobre 2026: la prima, con cui si chiude `REL-005` (D-198). La versione del pacchetto Python, la
  riga in testa a `SKILL.md` e il nome dello ZIP dicono lo stesso numero, e una prova lo tiene su
  (`tests/test_le_release.py`).
- **1.2.1** — 2 ottobre 2026: la prima consegna della beta (I-187, D-199). Da qui la riga in testa a `SKILL.md`
  porta il numero per intero.
