# I comandi della camera — impianto 7 con la skill della seconda parte, opus

Uscita di `python docs/collaudi/REL-001/comandi_della_camera.py <trascrizione> <camera>`, eseguito il 2 ottobre 2026; il percorso della camera e' scritto <camera>, quello della sessione <sessione>.

## I comandi della skill

1. `ambiente` — uscita 0 — Pronto.
2. `catalogo` — uscita 0 — attacchi: in (in, heating_water), out_1 (out, heating_water), out_2 (out, heating_water)
3. `catalogo` — uscita 0 — }
4. `catalogo` — uscita ? — {'id': 'c', 'domain': 'hydronic', 'medium': 'heating_water', 'flow': 'out', 'required': True}
5. `valida` — uscita 0 — - a-miscelatrice-acs: Il testo prevede la valvola miscelatrice termostatica sull'uscita dell'acqua calda sanitaria: e' un accessorio, la aggiunge il completamen
6. `completa` — uscita 0 — - a-miscelatrice-acs: Il testo prevede la valvola miscelatrice termostatica sull'uscita dell'acqua calda sanitaria: e' un accessorio, la aggiunge il completamen
7. `valida` — uscita 0 — Grafo da leggere, per l'approvazione del progettista: <camera>/lav
8. `pezzi` — uscita 0 — valve-isolation-volano-secondary-out — Valvola di intercettazione · simbolo valve-isolation 5 x 5 · rotazioni 0, 90, 180, 270
9. `disegna` — uscita 0 — }
10. `disegna` — uscita 2 — Formato A3 · tratte 45 · tratte cedute 0 · rilievi bloccanti 1 · pieghe 7 · sormonti 3 · avvisi e regole: DIAMETER_TAG_MISSING x2, DRAWING_OVER_THE_EQUIPMENT_TA
11. `anteprima` — uscita 0 — -rw-r--r-- 1 root root 363202 Oct  2 08:19 centrale-condominiale-pdc-cascata-caldaia-t1.svg
12. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
13. `anteprima` — uscita 0 — Anteprima: <camera>/lavoro/tavola/centrale-condominiale-pdc-cascat
14. `anteprima` — uscita 0 — Anteprima: <camera>/lavoro/tavola/zoom-sinistra.png (con pypdfium2
15. `anteprima` — uscita 0 — Anteprima: <camera>/lavoro/tavola/zoom-destra.png (con pypdfium2, 
16. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 4 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
17. `consegna` — uscita 0 — -rw-r--r-- 1 root root 112905 Oct  2 08:21 zoom-sinistra.png
18. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
19. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
20. `consegna` — uscita 0 — -rw-r--r-- 1 root root 363626 Oct  2 08:24 centrale-condominiale-pdc-cascata-caldaia-t1.svg

## I file aperti

- Read: <camera>/skill/disegnatore-mep/SKILL.md
- Read: <camera>/skill/disegnatore-mep/riferimenti/capire.md
- Read: <camera>/skill/disegnatore-mep/riferimenti/comporre.md
- Read: <camera>/skill/disegnatore-mep/riferimenti/rivedere.md
- Read: <camera>/lavoro/tavola/centrale-condominiale-pdc-cascata-caldaia-t1.png
- Read: <camera>/lavoro/tavola/centrale-condominiale-pdc-cascata-caldaia-t1.png
- Read: <camera>/lavoro/tavola/zoom-sinistra.png
- Read: <camera>/lavoro/tavola/zoom-destra.png
- Read: <camera>/lavoro/tavola/centrale-condominiale-pdc-cascata-caldaia-t1.png

## Fuori dalla camera

- (nel comando) /Area
