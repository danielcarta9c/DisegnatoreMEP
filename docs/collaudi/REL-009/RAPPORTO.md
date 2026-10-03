# REL-009 — la 1.3: il rapporto

Una sezione per ogni gruppo di punti, la più recente in alto. Il caso è il primo impianto reale (I-191),
ricostruito anonimo in `caso-reale-1/`: il documento della sessione di disegno porta i dati del cliente e non è
nel repository.

## 1. R1 — togliere, e «a bordo» per singola macchina (I-192)

**3 ottobre 2026** · decisione **D-201** (proposta)

### Le tavole, per prime: non cambia niente

Il punto 1 cambia il grafo completo, non il disegno. Le uscite di regressione, su `main` (`1dc2d80`) e sul ramo:

```
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <main> <ramo>
file: 54 prima, 54 dopo
IDENTICI
```

La tavola del caso non c'è ancora: si fa al punto 5, quando la skill sa disegnare l'esistente.

### Sul caso, con le scelte T1–T5 del progettista

```
                                  1.2.2        con il punto 1
pezzi del grafo completo          207          149
accessori delle regole            114           64
tolti dal progettista               —           42
punti aperti                        0            0
```

I 42 tolti, ciascuno con il motivo:
- **T1**: le 32 intercettazioni su ingresso e uscita di ventilconvettori e pannelli;
- **T3**: i due separatori d'aria;
- **T4**: i due defangatori;
- **T5**: vaso, riempimento e manometro sul ritorno dei due primari, 6 pezzi.

Con loro se ne vanno i pezzi che ne pendevano: le intercettazioni dei separatori, la valvola bloccata aperta dei
vasi, il rubinetto portamanometro. Rilanciare le regole sul grafo completo non propone niente.

**T2**, le valvole di sicurezza delle sei pompe: dichiarate a bordo, le regole le posano lo stesso. La sicurezza
di ogni generatore la vuole anche col bordo (D-182), e `completa` lo dice; se sul costruito non ci sono, si
tolgono con «togli», e il motivo.

### Come si scrive

- `accessori_tolti`, nel grafo di prima stesura: `{"pezzo": "air-separator-tj-pr-3-b", "motivo": "…"}`. Il nome è
  quello che `completa` scrive accanto a ogni accessorio: è derivato dai dati — voce, pezzo, attacco — e non cambia
  da un rilancio all'altro.
- `a_bordo`, sulla singola macchina: le funzioni che porta dentro, coi nomi del catalogo (`"a_bordo":
  ["filtration"]`). Le regole lo leggono come il bordo del catalogo.
- `completa` riporta:
  - i tolti per famiglia, con il motivo;
  - le voci che non tolgono niente;
  - i pezzi dichiarati a bordo che la regola posa lo stesso.

  Un nome di funzione sconosciuto nel bordo ferma la validazione.
- Capire §3 e `SKILL.md` passo 4 dicono quando si scrivono. «Spostare» è togliere da una parte e dichiarare
  dall'altra: la seconda metà è il punto 2.

### Le prove

`tests/rules/test_accessori_tolti.py` (9 prove, sul caso) e una prova sull'uscita di `completa`. Senza il filtro
del motore le due prove centrali cadono.

```
$ python3 -m pytest -q
1991 passed, 15 skipped, 10 xfailed in 249.55s
```

`ruff check src tests` e `mypy src` verdi. I grafi agli atti restano identici byte per byte: un campo vuoto non
si scrive.
