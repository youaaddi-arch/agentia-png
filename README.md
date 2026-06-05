# 🤖 Agentia PNG

Plateforme d'**agents IA** pour la direction d'entreprise, construite avec
[LangChain](https://python.langchain.com) et
[LangGraph](https://langchain-ai.github.io/langgraph/). Chaque agent incarne un
rôle métier et produit des livrables professionnels en français. Un graphe
LangGraph aiguille automatiquement la demande vers le bon responsable.

## 👥 Les agents

| Clé | Rôle |
|-----|------|
| `responsable_marketing` | Responsable Marketing — stratégie, campagnes, contenus, KPI |
| `responsable_marches_publics` | Responsable Marchés Publics — appels d'offres, mémoire technique, conformité |
| `responsable_commercial` | Responsable Commercial — prospection, négociation, propositions |
| `assistante_direction` | Assistant·e de Direction — courriers, comptes rendus, organisation |
| `responsable_administratif` | Responsable Administratif & Financier — facturation, conformité, reporting |
| `responsable_certification_rs` | Responsable Certification & RSE (RS) — Qualiopi, ISO, audits, RSE |

> 🪄 **Mode automatique** : vous n'êtes pas obligé de choisir l'agent. Décrivez
> simplement votre besoin et la plateforme sélectionne le bon responsable.

---

## 🚀 Démarrage ultra-simple (débutant)

### Étape 1 — Obtenir une clé API

Les agents ont besoin d'un « cerveau » (un modèle d'IA). Par défaut, la
plateforme utilise **Claude (Anthropic)**. Créez une clé sur
**https://console.anthropic.com/settings/keys**. Elle ressemble à
`sk-ant-...`. Gardez-la, on va la coller à l'étape 3.

> Vous préférez OpenAI ? Créez plutôt une clé sur
> https://platform.openai.com/api-keys et mettez dans `.env` :
> `OPENAI_API_KEY=sk-...` et `AGENTIA_MODEL=openai:gpt-4o-mini`.

### Étape 2 — Lancer la plateforme

Sur Mac ou Linux, dans un terminal, placez-vous dans le dossier du projet puis :

```bash
./run.sh
```

Ce script fait **tout** pour vous : il installe ce qu'il faut et ouvre
l'interface web dans votre navigateur. (La première fois peut prendre quelques
minutes.)

### Étape 3 — Coller votre clé

Au premier lancement, un fichier `.env` est créé. Ouvrez-le, et remplacez
`sk-ant-...` par votre vraie clé :

```
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
```

Relancez `./run.sh` — c'est prêt ! Décrivez votre besoin et cliquez sur
**Lancer**.

---

## 🧑‍💻 Utilisation avancée

### Installation manuelle

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseignez votre clé dans .env
```

### En ligne de commande

```bash
# Lister les agents
python -m agentia.main --liste

# Mode AUTO : la plateforme choisit le bon responsable
python -m agentia.main --sujet "Rédige un courrier de relance pour un client"

# Forcer un agent précis
python -m agentia.main --agent responsable_marketing \
  --sujet "Lancement d'une nouvelle offre SaaS" \
  --contexte "Cible PME, budget 20k€" \
  --objectif "Générer 100 leads qualifiés en 3 mois"

# Solliciter toute l'équipe sur un même sujet
python -m agentia.main --equipe \
  --sujet "Réponse à un marché public de formation Qualiopi"

# Mode interactif (sans argument) : on vous pose les questions
python -m agentia.main
```

### Interface web

```bash
streamlit run app.py
```

---

## 🔧 Configuration

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Claude (fournisseur par défaut) | — |
| `OPENAI_API_KEY` | Clé API OpenAI (si vous préférez GPT) | — |
| `AGENTIA_MODEL` | Modèle utilisé, au format `fournisseur:modele` | `anthropic:claude-sonnet-4-6` |

Exemples de `AGENTIA_MODEL` : `anthropic:claude-sonnet-4-6`,
`openai:gpt-4o-mini`. La plateforme s'appuie sur `init_chat_model` de LangChain,
qui détecte automatiquement le fournisseur.

## 🗂️ Structure du projet

```
agentia-png/
├── run.sh                       # Lanceur tout-en-un
├── app.py                       # Interface web Streamlit
├── pyproject.toml               # Packaging + config tests/lint
├── requirements.txt
├── .env.example
├── .github/workflows/ci.yml     # Intégration continue (lint + tests)
├── tests/                       # Tests automatiques (sans clé API)
└── src/agentia/
    ├── main.py                  # CLI
    ├── engine.py                # Moteur LangGraph (graphe d'agents)
    ├── config_loader.py         # Chargement config + routage automatique
    ├── config/
    │   ├── agents.yaml          # Définition des 6 agents
    │   └── tasks.yaml           # Tâches par défaut par agent
    └── tools/                   # Outils personnalisés (extensible)
```

## ✅ Qualité

```bash
ruff check src tests app.py   # lint
pytest -q                     # tests (ne nécessitent pas de clé API)
```

La CI GitHub exécute automatiquement ces vérifications sur chaque push.

## 🧩 Personnalisation

- **Modifier un agent** : éditez `src/agentia/config/agents.yaml`.
- **Modifier une tâche** : éditez `src/agentia/config/tasks.yaml`.
- **Ajuster le routage automatique** : éditez les mots-clés dans
  `src/agentia/config_loader.py`.
- **Ajouter un outil** (recherche web, accès CRM, veille marchés publics…) :
  créez-le dans `src/agentia/tools/` puis branchez-le sur les nœuds du graphe
  dans `engine.py`.

## 📄 Licence

Projet interne — Paris Nord Groupe.
