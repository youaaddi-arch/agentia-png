#!/usr/bin/env bash
# Lanceur tout-en-un de la plateforme Agentia PNG.
# Crée l'environnement, installe les dépendances et lance la plateforme.
#
# Usage :
#   ./run.sh            -> lance l'interface web (recommandé)
#   ./run.sh cli        -> lance le mode ligne de commande interactif
set -euo pipefail

cd "$(dirname "$0")"

# 1. Environnement virtuel
if [ ! -d ".venv" ]; then
  echo "📦 Création de l'environnement virtuel..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

# 2. Dépendances
echo "📥 Installation des dépendances (peut prendre quelques minutes la 1re fois)..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 3. Fichier .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Fichier .env créé. Ouvrez-le et renseignez votre clé API (ANTHROPIC_API_KEY)."
fi

# 4. Lancement
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"
if [ "${1:-web}" = "cli" ]; then
  python -m agentia.main
else
  echo "🌐 Ouverture de l'interface web..."
  streamlit run app.py
fi
