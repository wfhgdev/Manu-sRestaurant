#!/usr/bin/env bash
# Levanta la API en modo desarrollo.
# Uso (desde la raíz del proyecto, en Git Bash / Linux / macOS):  bash run.sh

# Activa el entorno virtual si existe (.venv o env; Windows o Linux/macOS)
for venv in .venv env; do
  if [ -f "$venv/Scripts/activate" ]; then source "$venv/Scripts/activate"; break; fi
  if [ -f "$venv/bin/activate" ]; then source "$venv/bin/activate"; break; fi
done

uvicorn app.main:app --reload
