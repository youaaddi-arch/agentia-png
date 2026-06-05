"""Chargement et validation de la configuration des agents.

Ce module ne dépend PAS de LangChain : il ne fait que lire les fichiers YAML et
exposer les constantes. Cela permet de le tester sans installer de LLM, et de
router une demande vers le bon agent sans appeler d'API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml

CONFIG_DIR = Path(__file__).parent / "config"

# Correspondance agent -> tâche par défaut (définie dans tasks.yaml)
AGENT_TO_TASK: Dict[str, str] = {
    "responsable_marketing": "tache_marketing",
    "responsable_marches_publics": "tache_marches_publics",
    "responsable_commercial": "tache_commercial",
    "assistante_direction": "tache_assistance_direction",
    "responsable_administratif": "tache_administrative",
    "responsable_certification_rs": "tache_certification_rs",
}

# Libellés lisibles pour l'interface
LIBELLES: Dict[str, str] = {
    "responsable_marketing": "Responsable Marketing",
    "responsable_marches_publics": "Responsable Marchés Publics",
    "responsable_commercial": "Responsable Commercial",
    "assistante_direction": "Assistant·e de Direction",
    "responsable_administratif": "Responsable Administratif & Financier",
    "responsable_certification_rs": "Responsable Certification & RSE (RS)",
}

# Mots-clés permettant de router automatiquement une demande vers un agent.
# Le routage choisit l'agent dont les mots-clés apparaissent le plus dans la
# demande. C'est volontairement simple et déterministe (aucun appel LLM).
MOTS_CLES: Dict[str, list[str]] = {
    "responsable_marketing": [
        "marketing", "campagne", "communication", "publicité", "publicite",
        "réseaux sociaux", "reseaux sociaux", "seo", "contenu", "marque",
        "notoriété", "notoriete", "lead", "newsletter", "emailing", "site web",
    ],
    "responsable_marches_publics": [
        "marché public", "marche public", "marchés publics", "marches publics",
        "appel d'offre", "appel d'offres", "appel d offre", "boamp", "ccap",
        "cctp", "dce", "dc1", "dc2", "dpgf", "mémoire technique",
        "memoire technique", "consultation", "soumission", "candidature",
    ],
    "responsable_commercial": [
        "commercial", "vente", "vendre", "prospection", "client", "prospect",
        "devis", "négociation", "negociation", "offre commerciale", "crm",
        "pipeline", "chiffre d'affaires", "ca", "closing", "argumentaire",
    ],
    "assistante_direction": [
        "agenda", "réunion", "reunion", "compte rendu", "compte-rendu",
        "courrier", "lettre", "ordre du jour", "rendez-vous", "rdv",
        "organisation", "secrétariat", "secretariat", "note", "synthèse",
        "synthese", "planning",
    ],
    "responsable_administratif": [
        "administratif", "facture", "facturation", "comptabilité",
        "comptabilite", "trésorerie", "tresorerie", "contrat", "paie",
        "rh", "budget", "dépense", "depense", "rgpd", "fiscal", "social",
        "reporting", "tableau de bord",
    ],
    "responsable_certification_rs": [
        "certification", "qualiopi", "iso", "audit", "rse", "rs", "norme",
        "qualité", "qualite", "référentiel", "referentiel", "conformité",
        "conformite", "label", "26000", "9001", "14001", "45001",
        "responsabilité sociétale", "responsabilite societale", "développement durable",
        "developpement durable",
    ],
}


def load_yaml(nom_fichier: str) -> dict:
    """Charge un fichier YAML du dossier de configuration."""
    chemin = CONFIG_DIR / nom_fichier
    with chemin.open("r", encoding="utf-8") as flux:
        return yaml.safe_load(flux)


def charger_agents() -> dict:
    return load_yaml("agents.yaml")


def charger_taches() -> dict:
    return load_yaml("tasks.yaml")


def router(demande: str) -> str:
    """Choisit automatiquement l'agent le plus pertinent pour une demande.

    Routage par comptage de mots-clés (déterministe, sans appel LLM).
    En cas d'égalité ou d'absence de correspondance, renvoie l'assistant·e de
    direction (rôle généraliste par défaut).
    """
    texte = demande.lower()
    scores: Dict[str, int] = {}
    for agent, mots in MOTS_CLES.items():
        scores[agent] = sum(1 for mot in mots if mot in texte)
    meilleur = max(scores, key=lambda a: scores[a])
    if scores[meilleur] == 0:
        return "assistante_direction"
    return meilleur


def valider_configuration() -> None:
    """Vérifie la cohérence des fichiers de configuration.

    Lève une AssertionError si une incohérence est détectée.
    """
    agents = charger_agents()
    taches = charger_taches()

    # Toutes les clés du mapping existent dans agents.yaml
    for agent in AGENT_TO_TASK:
        assert agent in agents, f"Agent manquant dans agents.yaml : {agent}"
        assert agent in LIBELLES, f"Libellé manquant pour : {agent}"
        assert agent in MOTS_CLES, f"Mots-clés manquants pour : {agent}"

    # Toutes les tâches référencées existent dans tasks.yaml
    for agent, tache in AGENT_TO_TASK.items():
        assert tache in taches, f"Tâche manquante dans tasks.yaml : {tache}"

    # Chaque agent a les champs requis
    for cle, conf in agents.items():
        for champ in ("role", "goal", "backstory"):
            assert conf.get(champ), f"Champ '{champ}' manquant pour {cle}"

    # Chaque tâche a une description formatable et un expected_output
    for cle, conf in taches.items():
        assert conf.get("expected_output"), f"expected_output manquant : {cle}"
        conf["description"].format(sujet="x", contexte="y", objectif="z")
