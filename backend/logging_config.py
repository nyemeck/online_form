"""
Configuration centralisee du systeme de logs.

Niveau configurable via la variable d'environnement LOG_LEVEL (defaut : INFO).
La sortie va vers stdout, captee par systemd/journald en production.

Niveaux disponibles : DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""

import logging
import os
import sys


def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Reduire la verbosite des bibliotheques bruyantes
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
