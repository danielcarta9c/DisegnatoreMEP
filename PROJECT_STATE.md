# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale | Nessun remote configurato |
| Sviluppo | Locale Windows | Cartella sincronizzata con OneDrive |
| Release | Non disponibile | `releases/latest/` sarà popolata dopo la prima versione verificata |

## Now — in corso

- [ ] ❓ Revisione del PM sulla specifica `docs/specs/2026-08-01-disegnatore-mep-design.md`.

## Next — backlog ordinato

1. Ottenere l'approvazione finale della specifica scritta.
2. Preparare il piano di implementazione.
3. Costruire e validare il registro delle fonti tecniche e normative.
4. Implementare nucleo topologico, contratti dei domini e validatori di base.
5. Costruire la libreria ampia dei simboli e il sistema grafico A3.
6. Implementare layout, rendering SVG/PDF e controlli geometrici.
7. Costruire la matrice di casi, regressioni e prove di stampa.
8. Generare la prima release installabile.

## Domande aperte

- ❓ Il PM approva la specifica scritta dopo la revisione end-to-end?

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `0bb4ef8` | Design concettuale completato, verificato end-to-end e formalizzato |
| `fa7157c` | Bootstrap della struttura di project management e avvio del repository Git locale |
