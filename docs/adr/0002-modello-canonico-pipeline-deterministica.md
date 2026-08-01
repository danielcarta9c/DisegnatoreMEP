# ADR 0002 - Modello canonico e pipeline deterministica

**Stato:** accettato - agosto 2026

## Contesto

Il disegno libero dell'AI produce coordinate instabili, componenti flottanti e connessioni graficamente scorrette. SVG e PDF non sono sorgenti affidabili per aggiornare un progetto.

## Decisione

Mantenere un modello tecnico canonico con identificativi stabili. Derivare da esso un modello geometrico e generare SVG/PDF mediante una pipeline deterministica. Le modifiche persistenti rientrano nel modello o in override espliciti.

## Motivazione

La separazione consente validazione, rigenerazione, confronto fra revisioni, distinta affidabile e test automatici. Evita che correzioni manuali sugli elaborati vadano perse o rendano il progetto non riproducibile.

## Conseguenze

Ogni renderer deve rispettare lo stesso contratto. Occorre versionare modello, libreria e regole. Gli elaborati restano vettoriali ed eventualmente modificabili, ma non costituiscono la fonte di verità.

## Quando rivedere

Se il prodotto dovrà supportare editing CAD bidirezionale o importare modifiche manuali da DWG/DXF/SVG nel modello canonico.
