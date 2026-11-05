# REL-018 — Le protezioni elettriche sulla tavola dell'elettrico

> **Scritto il 4 novembre 2026**, dopo la fusione della 1.11.0 (`REL-017`, PR #86, I-282). Il PO, sulla tavola uscita
> in sessione per una commessa: «è uscita senza le protezioni elettriche (che interruttori ecc... ) non so mi sembra ci
> siamo persi qualcosa rispetto al lavoro fatto sulla parte aria» (I-278). Verificato: il catalogo non ha mai avuto le
> protezioni; l'aria-aria porta quadro, sezionatore e la scritta del cavo come dato del progettista.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **CONSEGNATO** (5 novembre 2026) — fuso con la PR #87, la 1.12.1 (I-283, D-234). **Il pacchetto successivo non è scelto**: si chiede al PO (le candidate sono in `HANDOFF.md`).
**Base:** `main` dopo la PR #86 (la 1.11.0).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147).

## Le fonti (OneDrive del PO, non nel repository: si citano con la pagina)

- Manuale ThermaX R290 6-15 kW, §7.4 p. 55: corrente massima e cablaggio per taglia (6 kW 16 A 4 mm²; 9 kW 20,5 A
  4 mm²; 12 e 15 kW monofase 30 A 6 mm²; 12 e 15 kW trifase 14 A 2,5 mm²); p. 5 e 51: sezionamento onnipolare,
  differenziale 30 mA ad alta velocità, compatibile con l'inverter, alimentazione dedicata.
- Specifica tecnica di installazione PdC Shenling Nove C Rev. 01, §3.2–3.4: magnetotermico differenziale bipolare,
  curva C, Idn 30 mA, tipo B, ad alta velocità, nel quadro, con targhetta; niente sezionatore locale come regola;
  tabella §3.3 (9 kW C25/B25 3G4; 12 kW C25/B25 3G4; 15 kW C32/B40 3G6) con «se targa o manuale chiedono valori
  maggiori vale il maggiore»; linee di servizio 3G1,5.

## Le cose da fare

1. **Il pezzo**: interruttore magnetotermico differenziale, passante sulla linea all'uscita del quadro, sigla QF-nn,
   in tabella (poli, curva e In, Idn, tipo) e in legenda, solo sulla tavola dell'elettrico. Simbolo: **proposta della
   sessione**, da giudicare sulla tavola (il PO, alla domanda «simbolo QF-nn o scritta?», ha detto «vai avanti»).
2. **I valori per le Shenling** quando il progettista non li dà: la tabella §3.3 con la regola «vale il maggiore» del
   manuale — il 12 kW monofase va a **C32, differenziale tipo B 40 A, 3G6** (manuale 30 A e 6 mm²; assunzione detta al
   PO e non corretta). Gli stessi dati riempiono la tabella dell'elettrico della macchina (alimentazione, corrente
   massima, cavo minimo). 6 kW e trifase: fuori dalla specifica, si propongono dal manuale e si dichiarano.
3. **Gli avvisi**: una protezione o un cavo dichiarati sotto il manuale (la corrente massima, la sezione) sono un
   avviso di `completa` (il caso della commessa da 15 kW protetta C25).
4. **Il sezionatore locale**: di regola no (specifica §3.2); Capire lo mette solo se il testo lo chiede.
5. **La distinta**: la voce dell'interruttore (la P15 della specifica) con la sua dicitura.
6. Le istruzioni di Capire e Comporre; le prove; la villetta di riferimento con QF-01 sulla linea della PdC.

## Fuori

- Il calcolo generale di cavi e protezioni per macchine qualsiasi (portata del cavo, caduta di tensione): **I-248**.
- Le protezioni delle linee di servizio (circolatori, valvole): solo se il progettista le dichiara; la regola è da
  chiedere al PO.

## Criteri di accettazione

Le tavole per prime; suite a 0 failed senza skip o xfail nuovi; `ruff check src tests` verde; il banco di `REL-011`
fra `main` e il ramo; nessun dato di cliente nel diff; `tests/test_le_release.py` verde se c'è una release.
