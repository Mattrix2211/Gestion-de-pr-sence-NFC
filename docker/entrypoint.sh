#!/usr/bin/env bash
set -euo pipefail

# Démarrer pcscd en arrière-plan (si présent)
if command -v pcscd >/dev/null 2>&1; then
  # -f (foreground) mais on l'envoie en arrière-plan pour garder les logs dans stdout
  pcscd -f -d 2>/dev/null &
fi

# Migrations DB
python manage.py migrate --noinput

# Lancer serveur Django
python manage.py runserver 0.0.0.0:8000
