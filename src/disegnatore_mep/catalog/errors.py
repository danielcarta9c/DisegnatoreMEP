"""Errore unico del pacchetto catalogo.

Vive in un modulo proprio, come `graphics/errors.py`, perche' il registro e la
vista risolta lo sollevano entrambi e il primo importa la seconda: definirlo in
uno dei due creerebbe un ciclo. Resta esportato da `registry` con il nome con
cui il resto del progetto lo importa.
"""


class CatalogError(ValueError):
    pass
