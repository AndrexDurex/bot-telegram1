#!/usr/bin/env python
"""
Punto de entrada para ejecutar el BioAgent bot.
Uso: python main.py
"""
from bioagent.startup import prepare_credentials

# Restaurar credenciales desde HF Secrets (no-op en local)
prepare_credentials()

from bioagent.bot import run

if __name__ == "__main__":
    run()

