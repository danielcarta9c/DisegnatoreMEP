"""L'elettrico della tavola: le protezioni delle linee e i dati elettrici delle macchine che
il manuale del costruttore da' (REL-018, I-278).

- `protezione`: l'interruttore magnetotermico differenziale della linea, i suoi dati e come
  si scrivono; la sezione di un cavo letta dal testo del progettista;
- `costruttori`: i dati del manuale Shenling e della specifica Nove C per la linea della
  pompa di calore, che `completa` scrive dove il progettista non li ha dati, e gli avvisi
  quando quelli dati stanno sotto il manuale.

La skill non dimensiona cavi e protezioni di una macchina qualsiasi (I-248): qui ci sono i
numeri di un costruttore, letti dal suo manuale.
"""
