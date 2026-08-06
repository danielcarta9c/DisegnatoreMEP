"""Le prove del collaudo importano i propri attrezzi per nome piano.

Con l'import a moduli isolati del progetto la cartella non sta sul percorso:
ce la mette questo file, prima che le prove vengano raccolte.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
