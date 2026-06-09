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

# =====================================================================
# Organigramme (hiérarchie de l'équipe, façon CrewAI)
#   CEO -> Responsables -> Spécialistes
# C'est la source de vérité de l'organisation : l'interface et les tests
# en dérivent la liste des agents et leur niveau.
# =====================================================================
CEO: str = "directeur_general"

# Chaque responsable et la liste de ses spécialistes (sous-équipe).
EQUIPES: list[tuple[str, list[str]]] = [
    ("responsable_marketing", [
        "community_manager", "webmaster_seo", "expert_google_ads",
    ]),
    ("responsable_marches_publics", [
        "veilleur_appels_offres", "redacteur_memoire_technique",
        "monteur_dossier_ao",
    ]),
    ("responsable_commercial", [
        "charge_prospection", "redacteur_propositions",
    ]),
    ("assistante_direction", [
        "gestionnaire_emails", "gestionnaire_drive", "redacteur_comptes_rendus",
    ]),
    ("responsable_administratif", [
        "suivi_documents", "facturation_tresorerie",
    ]),
    ("responsable_certification_rs", [
        "preparateur_audits", "redacteur_procedures",
    ]),
]

# Listes pratiques dérivées de l'organigramme.
RESPONSABLES: list[str] = [resp for resp, _ in EQUIPES]
SPECIALISTES: list[str] = [spe for _, equipe in EQUIPES for spe in equipe]

# Correspondance agent -> tâche par défaut (définie dans tasks.yaml).
# Le CEO et les responsables ont une tâche dédiée ; les spécialistes
# partagent « tache_generique ».
AGENT_TO_TASK: Dict[str, str] = {
    CEO: "tache_ceo",
    "responsable_marketing": "tache_marketing",
    "responsable_marches_publics": "tache_marches_publics",
    "responsable_commercial": "tache_commercial",
    "assistante_direction": "tache_assistance_direction",
    "responsable_administratif": "tache_administrative",
    "responsable_certification_rs": "tache_certification_rs",
    **{spe: "tache_generique" for spe in SPECIALISTES},
}

# Libellés lisibles pour l'interface
LIBELLES: Dict[str, str] = {
    CEO: "Directeur·rice Général·e (CEO)",
    "responsable_marketing": "Responsable Marketing",
    "responsable_marches_publics": "Responsable Marchés Publics",
    "responsable_commercial": "Responsable Commercial",
    "assistante_direction": "Assistant·e de Direction",
    "responsable_administratif": "Responsable Administratif & Financier",
    "responsable_certification_rs": "Responsable Certification & RSE (RS)",
    # Spécialistes
    "community_manager": "Community Manager",
    "webmaster_seo": "Webmaster & SEO",
    "expert_google_ads": "Expert Google Ads (SEA)",
    "veilleur_appels_offres": "Veilleur d'appels d'offres",
    "redacteur_memoire_technique": "Rédacteur mémoire technique",
    "monteur_dossier_ao": "Monteur de dossier administratif",
    "charge_prospection": "Chargé·e de prospection",
    "redacteur_propositions": "Rédacteur propositions commerciales",
    "gestionnaire_emails": "Gestionnaire d'emails",
    "gestionnaire_drive": "Gestionnaire Drive & documents",
    "redacteur_comptes_rendus": "Rédacteur de comptes rendus",
    "suivi_documents": "Suivi des documents (échéances)",
    "facturation_tresorerie": "Facturation & trésorerie",
    "preparateur_audits": "Préparateur d'audits (Qualiopi)",
    "redacteur_procedures": "Rédacteur de procédures",
}

# Présentation visuelle de chaque agent (icône + accroche) pour l'interface.
PRESENTATION: Dict[str, dict] = {
    "responsable_marketing": {
        "icone": "📣",
        "accroche": "Stratégie, campagnes multicanal, contenus & notoriété.",
    },
    "responsable_marches_publics": {
        "icone": "📑",
        "accroche": "Appels d'offres, mémoires techniques & conformité.",
    },
    "responsable_commercial": {
        "icone": "💼",
        "accroche": "Prospection, négociation & propositions commerciales.",
    },
    "assistante_direction": {
        "icone": "🗂️",
        "accroche": "Courriers, comptes rendus, agendas & organisation.",
    },
    "responsable_administratif": {
        "icone": "📊",
        "accroche": "Facturation, finances, RH & conformité.",
    },
    "responsable_certification_rs": {
        "icone": "✅",
        "accroche": "Qualiopi, ISO, audits & responsabilité sociétale.",
    },
    # ---- Direction ----
    CEO: {
        "icone": "👑",
        "accroche": "Vision, stratégie, arbitrages & coordination de l'équipe.",
    },
    # ---- Spécialistes Marketing ----
    "community_manager": {
        "icone": "📱",
        "accroche": "Réseaux sociaux : LinkedIn, Facebook, Instagram, TikTok.",
    },
    "webmaster_seo": {
        "icone": "🌐",
        "accroche": "Site internet, blog & référencement Google (SEO).",
    },
    "expert_google_ads": {
        "icone": "🎯",
        "accroche": "Campagnes Google Ads & publicité payante (SEA).",
    },
    # ---- Spécialistes Marchés Publics ----
    "veilleur_appels_offres": {
        "icone": "🔭",
        "accroche": "Veille BOAMP/PLACE & repérage des opportunités.",
    },
    "redacteur_memoire_technique": {
        "icone": "📝",
        "accroche": "Rédaction de mémoires techniques gagnants.",
    },
    "monteur_dossier_ao": {
        "icone": "🗃️",
        "accroche": "Pièces administratives : DC1, DC2, DUME, DPGF.",
    },
    # ---- Spécialistes Commercial ----
    "charge_prospection": {
        "icone": "🧲",
        "accroche": "Idées commerciales, cibles & prises de contact.",
    },
    "redacteur_propositions": {
        "icone": "📄",
        "accroche": "Propositions commerciales & devis convaincants.",
    },
    # ---- Spécialistes Assistance de Direction ----
    "gestionnaire_emails": {
        "icone": "✉️",
        "accroche": "Tri, priorisation & rédaction d'emails.",
    },
    "gestionnaire_drive": {
        "icone": "📁",
        "accroche": "Classement & organisation des fichiers (Drive).",
    },
    "redacteur_comptes_rendus": {
        "icone": "🗒️",
        "accroche": "Comptes rendus, relevés de décisions & PV.",
    },
    # ---- Spécialistes Administratif & Financier ----
    "suivi_documents": {
        "icone": "⏰",
        "accroche": "Dates de validité, échéances & alertes documentaires.",
    },
    "facturation_tresorerie": {
        "icone": "💶",
        "accroche": "Factures, relances d'impayés & trésorerie.",
    },
    # ---- Spécialistes Certification & RSE ----
    "preparateur_audits": {
        "icone": "🔎",
        "accroche": "Préparation d'audits, audit blanc & écarts.",
    },
    "redacteur_procedures": {
        "icone": "📚",
        "accroche": "Procédures, modes opératoires & documentation qualité.",
    },
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
    # -----------------------------------------------------------------
    # CEO + spécialistes : mots-clés PRÉCIS (placés après les responsables
    # pour qu'un responsable gagne en cas d'égalité ; un spécialiste n'est
    # choisi que lorsqu'une demande emploie son vocabulaire spécifique).
    # -----------------------------------------------------------------
    CEO: [
        "stratégie", "strategie", "stratégique", "strategique", "vision",
        "arbitrage", "priorité", "priorite", "feuille de route", "business plan",
        "direction générale", "direction generale", "pilotage", "cap",
    ],
    # --- Marketing ---
    "community_manager": [
        "réseaux sociaux", "reseaux sociaux", "linkedin", "facebook",
        "instagram", "tiktok", "post", "publication", "community manager",
    ],
    "webmaster_seo": [
        "site internet", "blog", "référencement", "referencement",
        "article de blog", "page web", "balise", "backlink",
    ],
    "expert_google_ads": [
        "google ads", "adwords", "sea", "sem", "campagne payante",
        "publicité en ligne", "publicite en ligne", "annonce", "roas",
    ],
    # --- Marchés publics ---
    "veilleur_appels_offres": [
        "veille", "surveillance", "place", "profil acheteur",
        "détection", "detection", "alerte marché", "alerte marche",
    ],
    "redacteur_memoire_technique": [
        "note méthodologique", "note methodologique", "rédiger le mémoire",
        "rediger le memoire", "trame de mémoire", "trame de memoire",
    ],
    "monteur_dossier_ao": [
        "dume", "pièces administratives", "pieces administratives",
        "attestation fiscale", "dossier de candidature", "kbis",
    ],
    # --- Commercial ---
    "charge_prospection": [
        "prospection", "cold email", "prise de contact", "idée commerciale",
        "idee commerciale", "nouveaux clients", "cibles", "fichier prospects",
    ],
    "redacteur_propositions": [
        "proposition commerciale", "offre commerciale", "plaquette",
        "rédiger une offre", "rediger une offre", "devis commercial",
    ],
    # --- Assistance de direction ---
    "gestionnaire_emails": [
        "email", "e-mail", "mail", "boîte mail", "boite mail", "messagerie",
        "répondre au mail", "repondre au mail", "tri des mails",
    ],
    "gestionnaire_drive": [
        "drive", "google drive", "classement", "arborescence",
        "ranger les fichiers", "nommage", "dossier de fichiers",
    ],
    "redacteur_comptes_rendus": [
        "relevé de décisions", "releve de decisions", "procès-verbal",
        "proces-verbal", "pv de réunion", "pv de reunion", "cr de réunion",
        "cr de reunion",
    ],
    # --- Administratif & financier ---
    "suivi_documents": [
        "date de validité", "date de validite", "échéance", "echeance",
        "expiration", "renouvellement", "suivi documentaire", "alerte document",
    ],
    "facturation_tresorerie": [
        "relance impayé", "relance impaye", "encaissement", "tva",
        "émettre une facture", "emettre une facture", "suivi des paiements",
    ],
    # --- Certification & RSE ---
    "preparateur_audits": [
        "préparation audit", "preparation audit", "audit blanc",
        "revue documentaire", "préparer l'audit", "preparer l'audit",
        "écarts", "ecarts",
    ],
    "redacteur_procedures": [
        "procédure", "procedure", "mode opératoire", "mode operatoire",
        "processus qualité", "processus qualite", "documentation qualité",
        "documentation qualite",
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


def organigramme() -> dict:
    """Renvoie l'organigramme prêt pour l'affichage.

    Structure :
        {
          "ceo": "directeur_general",
          "equipes": [
            {"responsable": "responsable_marketing",
             "specialistes": ["community_manager", ...]},
            ...
          ],
        }
    """
    return {
        "ceo": CEO,
        "equipes": [
            {"responsable": resp, "specialistes": list(equipe)}
            for resp, equipe in EQUIPES
        ],
    }


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
