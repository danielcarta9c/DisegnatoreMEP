"""Errore unico del pacchetto di layout.

Sottoclasse di `ValueError`, come `CatalogError` e `SymbolError`: i caricatori
e la CLI del progetto catturano `ValueError` e classificano di conseguenza.
"""


class LayoutError(ValueError):
    pass
