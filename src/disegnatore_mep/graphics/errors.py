"""Errore unico del pacchetto grafico.

Vive in un modulo proprio perche' non appartiene a nessuno dei tre che lo
sollevano: il manifesto (`symbol.py`), il registro (`registry.py`) e il
compilatore dei compositi (`composite.py`). Sottoclasse di `ValueError`, come
`CatalogError`, cosi' che la CLI la intercetti con l'unica voce `ValueError`.
"""


class SymbolError(ValueError):
    pass
