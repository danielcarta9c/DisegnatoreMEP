class RuleError(Exception):
    """Errore del pacchetto delle regole.

    Ha il proprio tipo, come il catalogo e il layout: un pacchetto che importa
    l'errore di un altro lega due parti che devono restare indipendenti.
    """
