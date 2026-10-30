# REL-011 — Le regole del corredo contro il manuale Shenling

> **Attivo dal 30 ottobre 2026**, dopo la 1.7.0 (`REL-015`, PR #81, I-235). Era in coda dal 29 ottobre (I-228): il PO
> aveva portato il kit aria-aria, e prima sono venuti `REL-012` e `REL-015`. Il pacchetto resta com'era scritto.
> **Prima di cominciare**, le domande lasciate aperte dalla 1.7.0 (`docs/plans/pacchetti/REL-015.md`): i rilievi D1, D3,
> D4 del collaudo (i circolatori li ha decisi il PO: I-236, D-215, nella 1.7.1) — se entrano qui o in un pacchetto a parte lo dice il PO.

> **▶ Il pacchetto attivo, per l'ordine del PO** — «il manuale shenling pensavo piu' di usarlo non per il revisore ma
> proprio per verificare nella skill le regole dell'agente "capire" o composizione. non ricordo dove avevamo messo le
> regole che dicono vaso d'espansione se ci va quanto grande ecc. quel pezzo li dico. pero' facciamo una cosa alla
> volta. prima l'agente revisore esterno.» (I-218). Il revisore esterno è nella 1.5.0 (I-223). Scritto il 25 ottobre
> 2026, sulla 1.5.0.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **DA COMINCIARE**.
**Base:** `main` dopo la PR #79 (la 1.5.0).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147).

---

## Perché

Le regole che dicono **se un accessorio ci va** — il vaso d'espansione, la valvola di sicurezza, lo sfiato, il ritegno —
sono di **Completare**, in `rules/hydronic/` (un file per regola, 16 in tutto), non di Capire né di Comporre. Il PO
vuole verificarle sul manuale della marca che usa di più. Il manuale Shenling ThermaX R290 6–15 kW è già stato letto e
ricontrollato sulle pagine 40–43 e 51–53 (`docs/collaudi/REL-010/RAPPORTO.md` §2): il vaso non è a bordo, la valvola di
sicurezza sì (3 bar), il volume minimo dell'impianto è 40 l, in cascata vuole un ritegno sull'uscita di ogni unità e un
tampone che cresce con il numero delle unità.

**Una cosa da dire al PO per prima:** la skill decide **se** un accessorio si disegna, non **quanto è grande**. La
taglia del vaso è del progettista («Non progetti», `SKILL.md`); se il PO vuole che la tavola la scriva, è un dato da
chiedere, non un calcolo.

## Le cose da fare, in quest'ordine

### 1. Dove stanno le regole

Una tabella per il PO: le regole di `rules/hydronic/` che il manuale tocca — `expansion-on-closed-circuit`,
`expansion-on-the-stored-volume-feed`, `safety-relief-where-heat-enters-the-water`, `air-release-where-the-water-is-hottest`,
`air-vent-on-the-stored-volume`, `dhw-check-on-cold-inlet`, `isolate-what-is-serviced` e le altre — con, per ciascuna,
**quando** scatta e **che cosa** mette, in parole sue.

### 2. Il confronto

Regola per regola: che cosa dice la skill, che cosa dice il manuale Shenling (con la pagina), che cosa dice la §2.4 della
*Specifica tecnica di installazione* Nove C. Dove sono d'accordo, dove no, che cosa manca — il ritegno su ogni unità in
cascata, il volume minimo, il tampone. **Il contenuto MEP è del PO**: la sessione mostra il confronto e propone; il PO
decide che cosa cambia.

### 3. Il dubbio del PO sul vaso

«Ho anche un dubbio sul vaso di espansione» (I-220, sul caso rifatto). Si chiede al PO qual è, con la tavola in mano.

### 4. Le correzioni

Quelle che il PO decide: le regole, le prove, il banco di regressione, e **le tavole che cambiano, al PO, prima dei
numeri**.

### 5. La release

Con `scripts/costruisci-skill.py`, e `tests/test_le_release.py` verde (D-200).

## Da decidere col PO — rimasti da `REL-010` e `REL-009`

- **la soglia** (I-223): la tavola del caso rifatto, con le colonne della cascata lontane, si consegna o va ricomposta?
  Con la soglia tre revisori su tre dicono «si consegna»; al primo giro il PO aveva dato giusto «va ricomposta»
  (`docs/collaudi/REL-010/RAPPORTO.md` §5). La domanda è anche sulla pagina della prova;
- **quattro difetti del disegno** visti dai revisori esterni: i tre simboli in testa alla legenda che si toccano, la
  miscelatrice termostatica e il rubinetto portamanometro quasi uguali, la barra di ritorno del collettore di zona
  spezzata, la freccia sullo scarico dell'acqua fredda;
- **il segno della commutatrice** (I-221): una «c» sopra, o un simbolo leggermente diverso;
- **i difetti del prodotto** della taratura e della prova (`docs/plans/pacchetti/REL-010.md`, «Quello che la taratura ha
  riportato sul prodotto»): in quale pacchetto;
- gli esempi del revisore: gli schemi tipologici A, B, C della specifica tecnica;
- da `REL-009`, punto 9: la distanza della valvola di sicurezza sopra il suo raccordo; B3 contro B1 nell'ordine dei
  collettori primari; la quota del primo raccordo della zona vicina; da dove arriva la fredda del bollitore. E il
  **limite d'intervento** facoltativo (I-195, D-202).

## Perimetro

**Dentro:** `rules/hydronic/**`, `skill/**`, `src/**`, `tests/**`, `docs/collaudi/REL-011/`, `releases/`, il registro,
il registro delle decisioni (come proposte), `HANDOFF.md`, questo file.

**Fuori:** i manuali dei costruttori e la specifica tecnica Nove C nel repository — si citano con la pagina, non si
copiano (il repository è pubblico); i dati del cliente, in qualunque file; un contenuto MEP o una convenzione grafica
decisi dalla sessione.

## Criteri di accettazione — per ogni PR

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: quelle che la PR cambia, prima e dopo, al PO.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff check src tests` verde; `mypy` verde dove
   l'ambiente lo lascia girare.
2. **La regressione**: il banco di `REL-009` (`docs/collaudi/REL-009/la-1.4-sulle-tavole-agli-atti/banco.py`, più le
   tre prove pulite) fra `main` e il ramo, ogni tavola cambiata spiegata.
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza.
4. **Gli input del PO nel registro** il giorno in cui arrivano.
5. **Nessun dato di cliente nel diff**, e nessuna pagina dei manuali: il comando di ricerca e il suo output vuoto.
6. **La release**: `tests/test_le_release.py` verde — la skill si carica (D-200).
