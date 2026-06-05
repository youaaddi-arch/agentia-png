# 🤖 Agentia PNG

Plateforme d'**agents IA** pour la direction d'entreprise, construite avec
[CrewAI](https://github.com/crewAIInc/crewAI). Chaque agent incarne un rôle
métier et produit des livrables professionnels en français.

## 👥 Les agents

| Clé | Rôle |
|-----|------|
| `responsable_marketing` | Responsable Marketing — stratégie, campagnes, contenus, KPI |
| `responsable_marches_publics` | Responsable Marchés Publics — appels d'offres, mémoire technique, conformité |
| `responsable_commercial` | Responsable Commercial — prospection, négociation, propositions |
| `assistante_direction` | Assistant·e de Direction — courriers, comptes rendus, organisation |
| `responsable_administratif` | Responsable Administratif & Financier — facturation, conformité, reporting |
| `responsable_certification_rs` | Responsable Certification & RSE (RS) — Qualiopi, ISO, audits, RSE |

## 📦 Installation

```bash
# 1. Cloner puis créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer la clé API
cp .env.example .env
# puis éditez .env et renseignez OPENAI_API_KEY (ou un autre fournisseur)
```

## 🚀 Utilisation

### En ligne de commande

```bash
# Lister les agents
python -m agentia.main --liste

# Solliciter un agent précis
python -m agentia.main \
  --agent responsable_marketing \
  --sujet "Lancement d'une nouvelle offre SaaS" \
  --contexte "Cible PME, budget 20k€" \
  --objectif "Générer 100 leads qualifiés en 3 mois"

# Solliciter toute l'équipe sur un même sujet
python -m agentia.main --equipe \
  --sujet "Réponse à un marché public de formation Qualiopi"

# Mode interactif (sans argument)
python -m agentia.main
```

> Astuce : exécutez les commandes depuis le dossier `src/`, ou installez le
> paquet en mode édition avec `pip install -e .` pour exposer la commande
> `agentia` et résoudre les imports.

### Interface web (optionnelle)

```bash
streamlit run app.py
```

## 🔧 Configuration

| Variable | Description | Défaut |
|----------|-------------|--------|
| `OPENAI_API_KEY` | Clé API du LLM | — |
| `AGENTIA_MODEL` | Modèle utilisé par les agents | `gpt-4o-mini` |

Pour utiliser un autre fournisseur (Anthropic, Groq…), définissez la clé
correspondante et le modèle, par ex. `AGENTIA_MODEL=anthropic/claude-sonnet-4-6`.

## 🗂️ Structure du projet

```
agentia-png/
├── app.py                       # Interface web Streamlit
├── pyproject.toml               # Packaging
├── requirements.txt
├── .env.example
└── src/agentia/
    ├── main.py                  # CLI
    ├── crew.py                  # Construction des agents/tâches CrewAI
    ├── config/
    │   ├── agents.yaml          # Définition des 6 agents
    │   └── tasks.yaml           # Tâches par défaut par agent
    └── tools/                   # Outils personnalisés (extensible)
```

## 🧩 Personnalisation

- **Modifier un agent** : éditez `src/agentia/config/agents.yaml`.
- **Modifier une tâche** : éditez `src/agentia/config/tasks.yaml`.
- **Ajouter un outil** (recherche web, accès CRM, veille marchés publics…) :
  créez-le dans `src/agentia/tools/` puis rattachez-le aux agents dans
  `crew.py`.

## 📄 Licence

Projet interne — Paris Nord Groupe.
