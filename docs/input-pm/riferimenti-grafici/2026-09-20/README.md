# Le due tavole che il PO ha segnato a penna — 20 settembre 2026

**Sono la fonte più diretta che abbiamo su come devono venire le autostrade**, perché non
descrivono un impianto: **correggono il nostro**. Il PO le ha mandate fermando lo sviluppo,
con questo messaggio:

> «Le tavole fanno schifo. Guardale per favore, ti sembrano tavole come dovrebbero essere?
> **Sposta le macchine in modo che le linee delle autostrade vengano con pochissime curve,
> poi attacchi il resto delle valvole piccole e strade secondarie. Ma il disegno nasce dalle
> linee delle autostrade.** Le macchine o cose in parallelo si disegnano come ti ho già
> fatto vedere. Perché non si riesce a fare sta cosa. Stai lì a ottimizzare le cose inutili a
> calcolare non so quale parametro… ma la cosa più facile e più importante non la facciamo.
> **LE AUTOSTRADE CON POCHE CURVE e pochi sormonti.**»

| file | che cosa ci ha segnato |
|---|---|
| `tavola-5-segnata-dal-po.png` | Ripassa in **rosso spesso** le tre mandate delle pompe e la verticale del collettore, in **blu spesso** i tre ritorni e la loro verticale. Sta indicando **la forma che vuole**: stacchi orizzontali corti, **una** verticale per circuito accanto alle macchine, e poi i due tronchi dritti. |
| `tavola-4-segnata-dal-po.png` | Ripassa in rosso la mandata della caldaia e in blu il suo ritorno, e **scarabocchia con forza il nodo** dove le due incontrano la deviatrice e la commutatrice. A destra traccia un **rettangolo rosso** sulla zona dello scambiatore: la forma pulita che quella linea doveva avere. |

## Che cosa ne è uscito, e dove sta scritto

- **Il metodo**, in testa a `docs/regole-del-piano.md` — «L'ordine in cui si compone — prima
  le autostrade»: si leggono le **porte** delle macchine, si posano le macchine su quelle
  quote, il collettore è **una verticale corta accanto alle macchine**, e solo alla fine si
  appendono valvole e strade secondarie.
- **Il nodo dell'impianto 4** che ha scarabocchiato: era la commutatrice 30 mm fuori dalla
  quota della propria porta sulla caldaia. Corretta, la linea allo scambiatore è passata **da
  3 pieghe a 1**.
- **L'impianto 5**: il tronco del ritorno primario stava 20 mm sotto la quota di
  `volano.primary_out` e risaliva con una verticale di 120 mm. Rimesso sulla quota, è **una
  retta sola** dal volano fino a PDC-3.

## Come si usano, e come no

**Sì**: per la **forma** — quali linee sono autostrade, come si impila un parallelo, dove sta
il collettore, quali sormonti sono accettabili.

**No**: per le **quote**. Sono ripassi a penna su uno schermo: gli spessori e le distanze non
sono misure. Vale lo stesso avvertimento del `schizzo-informale-po.png` del 3 settembre.
