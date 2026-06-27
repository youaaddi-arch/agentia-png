"""Chargement et validation de la configuration des agents.

Ce module ne dépend PAS de LangChain : il ne fait que lire les fichiers YAML et
exposer les constantes. Cela permet de le tester sans installer de LLM, et de
router une demande vers le bon agent sans appeler d'API.

L'équipe est organisée par SERVICES (7 services, 18 agents).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml

CONFIG_DIR = Path(__file__).parent / "config"

# =====================================================================
# Organisation par services (source de vérité de l'équipe)
# Chaque service : un identifiant, un nom, une icône, une couleur, et la
# liste de ses membres (le 1er membre est le « lead » du service).
# =====================================================================
SERVICES: list[dict] = [
    {
        "id": "direction",
        "nom": "Direction Générale",
        "icone": "👑",
        "couleur": "#E8B500",
        "membres": ["conseiller_strategie", "assistante_direction"],
    },
    {
        "id": "rh",
        "nom": "Ressources Humaines",
        "icone": "👥",
        "couleur": "#EC4899",
        "membres": ["responsable_rh"],
    },
    {
        "id": "marketing",
        "nom": "Marketing",
        "icone": "📣",
        "couleur": "#FF5A4C",
        "membres": [
            "responsable_marketing", "expert_google_ads",
            "webmaster_seo", "community_manager",
        ],
    },
    {
        "id": "commercial",
        "nom": "Commercial",
        "icone": "💼",
        "couleur": "#22C55E",
        "membres": ["ingenieur_commercial", "charge_prospection", "charge_sourcing"],
    },
    {
        "id": "appels_offres",
        "nom": "Appels d'Offres",
        "icone": "🎯",
        "couleur": "#3B82F6",
        "membres": [
            "veilleur_appels_offres", "analyste_ao",
            "redacteur_memoire_technique", "gestionnaire_ao",
        ],
    },
    {
        "id": "administratif",
        "nom": "Administratif & Financier",
        "icone": "💶",
        "couleur": "#14B8A6",
        "membres": ["responsable_financier", "gestionnaire_comptable"],
    },
    {
        "id": "qualite",
        "nom": "Qualité & Certification",
        "icone": "✅",
        "couleur": "#F97316",
        "membres": ["responsable_qualite", "auditeur_qualiopi"],
    },
]

# Listes pratiques dérivées de l'organisation.
AGENTS: list[str] = [m for s in SERVICES for m in s["membres"]]
LEADS: list[str] = [s["membres"][0] for s in SERVICES]
# Couleur de chaque agent = couleur de son service.
COULEUR_AGENT: Dict[str, str] = {
    m: s["couleur"] for s in SERVICES for m in s["membres"]
}

# Prénom de chaque membre.
NOMS: Dict[str, str] = {
    "conseiller_strategie": "Yousra",
    "assistante_direction": "Aïcha",
    "responsable_rh": "Chloé",
    "charge_sourcing": "Sarah",
    "responsable_marketing": "Karim",
    "expert_google_ads": "Emma",
    "webmaster_seo": "Hugo",
    "community_manager": "Léa",
    "ingenieur_commercial": "Yanis",
    "charge_prospection": "Léo",
    "veilleur_appels_offres": "Nadia",
    "analyste_ao": "Mehdi",
    "redacteur_memoire_technique": "Thomas",
    "gestionnaire_ao": "Camille",
    "responsable_financier": "Antoine",
    "gestionnaire_comptable": "Fatima",
    "responsable_qualite": "Aminata",
    "auditeur_qualiopi": "Anas",
}

# Intitulé de poste (libellé lisible) de chaque membre.
LIBELLES: Dict[str, str] = {
    "conseiller_strategie": "Conseillère en Stratégie",
    "assistante_direction": "Assistante de Direction",
    "responsable_rh": "Responsable RH & Paie",
    "charge_sourcing": "Chargée de Sourcing & Alternance",
    "responsable_marketing": "Responsable Marketing",
    "expert_google_ads": "Chargée de Publicité / Google Ads",
    "webmaster_seo": "Gestionnaire de Site Web & SEO",
    "community_manager": "Community Manager / Réseaux Sociaux",
    "ingenieur_commercial": "Ingénieur Commercial / Négociation",
    "charge_prospection": "Chargé de Prospection & Devis",
    "veilleur_appels_offres": "Chargée de Veille Appels d'Offres",
    "analyste_ao": "Analyste Appels d'Offres",
    "redacteur_memoire_technique": "Rédacteur Mémoire Technique",
    "gestionnaire_ao": "Gestionnaire Administratif Appels d'Offres",
    "responsable_financier": "Responsable Financier / Contrôleur de Gestion",
    "gestionnaire_comptable": "Gestionnaire Comptable & Administrative",
    "responsable_qualite": "Responsable Qualité & RSE",
    "auditeur_qualiopi": "Auditeur Interne & Référent Qualiopi",
}

# Correspondance agent -> tâche par défaut (définie dans tasks.yaml).
# Les profils « transverses » utilisent une tâche dédiée ; les autres la
# tâche générique (leur expertise est portée par leur fiche dans agents.yaml).
AGENT_TO_TASK: Dict[str, str] = {
    "conseiller_strategie": "tache_ceo",
    "assistante_direction": "tache_assistance_direction",
    "responsable_marketing": "tache_marketing",
    "ingenieur_commercial": "tache_commercial",
    "analyste_ao": "tache_marches_publics",
    "responsable_financier": "tache_administrative",
    "responsable_qualite": "tache_certification_rs",
}
# Tous les autres agents -> tâche générique.
for _cle in AGENTS:
    AGENT_TO_TASK.setdefault(_cle, "tache_generique")

# Icône + accroche de chaque membre (pour les cartes de l'interface).
PRESENTATION: Dict[str, dict] = {
    "conseiller_strategie": {"icone": "👑", "accroche": "Vision, stratégie & arbitrages."},
    "assistante_direction": {"icone": "🗂️", "accroche": "Courriers, comptes rendus & organisation."},
    "responsable_rh": {"icone": "🧑‍💼", "accroche": "Contrats, paie & droit social."},
    "charge_sourcing": {"icone": "📋", "accroche": "Recrutement, sourcing & alternance."},
    "responsable_marketing": {"icone": "📣", "accroche": "Stratégie, campagnes & contenus."},
    "expert_google_ads": {"icone": "🎯", "accroche": "Google Ads & publicité en ligne."},
    "webmaster_seo": {"icone": "🌐", "accroche": "Site web, blog & référencement (SEO)."},
    "community_manager": {"icone": "📱", "accroche": "Réseaux sociaux & community management."},
    "ingenieur_commercial": {"icone": "💼", "accroche": "Vente, négociation & closing."},
    "charge_prospection": {"icone": "🧲", "accroche": "Prospection & devis."},
    "veilleur_appels_offres": {"icone": "🔭", "accroche": "Veille BOAMP/PLACE & opportunités."},
    "analyste_ao": {"icone": "📑", "accroche": "Analyse des dossiers & critères."},
    "redacteur_memoire_technique": {"icone": "📝", "accroche": "Mémoires techniques gagnants."},
    "gestionnaire_ao": {"icone": "🗃️", "accroche": "Pièces administratives (DC1, DC2, DUME)."},
    "responsable_financier": {"icone": "📊", "accroche": "Budget, trésorerie & contrôle de gestion."},
    "gestionnaire_comptable": {"icone": "💶", "accroche": "Facturation, comptabilité & relances."},
    "responsable_qualite": {"icone": "✅", "accroche": "Qualiopi, ISO & RSE."},
    "auditeur_qualiopi": {"icone": "🔎", "accroche": "Audits internes & conformité Qualiopi."},
}

# Mots-clés de routage automatique (comptage déterministe, sans appel LLM).
# Le 1er membre d'un service (lead) est placé avant ses collègues : en cas
# d'égalité de score, c'est lui qui est choisi.
MOTS_CLES: Dict[str, list[str]] = {
    # --- Direction ---
    "conseiller_strategie": [
        "stratégie", "strategie", "vision", "arbitrage", "priorité", "priorite",
        "feuille de route", "business plan", "pilotage", "cap", "objectifs",
    ],
    "assistante_direction": [
        "agenda", "réunion", "reunion", "compte rendu", "compte-rendu",
        "courrier", "lettre", "ordre du jour", "note", "synthèse", "synthese",
        "organisation", "planning", "secrétariat", "secretariat",
    ],
    # --- Ressources humaines ---
    "responsable_rh": [
        "rh", "ressources humaines", "paie", "salaire", "bulletin", "contrat de travail",
        "embauche", "droit du travail", "congés", "conges", "personnel", "social rh",
    ],
    "charge_sourcing": [
        "recrutement", "sourcing", "alternance", "apprentissage", "candidat",
        "offre d'emploi", "cv", "entretien", "stage", "opco",
    ],
    # --- Marketing ---
    "responsable_marketing": [
        "marketing", "campagne", "communication", "marque", "notoriété",
        "notoriete", "lead", "newsletter", "emailing", "contenu", "positionnement",
    ],
    "expert_google_ads": [
        "google ads", "adwords", "sea", "sem", "campagne payante", "publicité",
        "publicite", "annonce", "roas", "display",
    ],
    "webmaster_seo": [
        "site internet", "site web", "blog", "seo", "référencement",
        "referencement", "article de blog", "page web", "backlink",
    ],
    "community_manager": [
        "réseaux sociaux", "reseaux sociaux", "linkedin", "facebook",
        "instagram", "tiktok", "post", "publication", "community",
    ],
    # --- Commercial ---
    "ingenieur_commercial": [
        "commercial", "vente", "vendre", "négociation", "negociation",
        "closing", "argumentaire", "offre commerciale", "client", "crm", "pipeline",
    ],
    "charge_prospection": [
        "prospection", "prospect", "devis", "cold email", "prise de contact",
        "lead", "nouveaux clients", "cibles",
    ],
    # --- Appels d'offres ---
    "veilleur_appels_offres": [
        "veille", "surveillance", "boamp", "place", "profil acheteur",
        "détection", "detection", "opportunité marché", "opportunite marche",
    ],
    "analyste_ao": [
        "appel d'offre", "appel d'offres", "marché public", "marche public",
        "marchés publics", "marches publics", "ccap", "cctp", "rc", "consultation",
        "critères d'attribution", "criteres d'attribution",
    ],
    "redacteur_memoire_technique": [
        "mémoire technique", "memoire technique", "note méthodologique",
        "note methodologique", "trame de mémoire", "trame de memoire",
    ],
    "gestionnaire_ao": [
        "dc1", "dc2", "dpgf", "dume", "pièces administratives",
        "pieces administratives", "dossier de candidature", "attestation",
    ],
    # --- Administratif & financier ---
    "responsable_financier": [
        "finance", "financier", "budget", "trésorerie", "tresorerie",
        "contrôle de gestion", "controle de gestion", "reporting",
        "tableau de bord", "rentabilité", "rentabilite",
    ],
    "gestionnaire_comptable": [
        "comptabilité", "comptabilite", "facture", "facturation", "relance",
        "impayé", "impaye", "encaissement", "tva", "paiement",
    ],
    # --- Qualité & certification ---
    "responsable_qualite": [
        "qualité", "qualite", "qualiopi", "iso", "rse", "norme", "référentiel",
        "referentiel", "procédure", "procedure", "26000", "9001",
        "responsabilité sociétale", "responsabilite societale",
    ],
    "auditeur_qualiopi": [
        "audit", "audit interne", "audit blanc", "écart", "ecart",
        "revue documentaire", "conformité", "conformite", "preuve",
    ],
}


# Missions principales de chaque agent (affichées sur sa fiche).
MISSIONS: Dict[str, list[str]] = {
    "conseiller_strategie": [
        "Définir les priorités et la feuille de route",
        "Arbitrer les décisions importantes",
        "Synthétiser la situation pour la direction",
    ],
    "assistante_direction": [
        "Rédiger courriers, comptes rendus et notes",
        "Organiser agendas et réunions",
        "Retrouver documents et emails (Drive / Gmail)",
    ],
    "responsable_rh": [
        "Rédiger contrats et éléments de paie",
        "Gérer l'administration du personnel",
        "Veiller à la conformité sociale",
    ],
    "charge_sourcing": [
        "Rédiger des offres d'emploi et d'alternance",
        "Sourcer et présélectionner des candidats",
        "Suivre les contrats d'alternance",
    ],
    "responsable_marketing": [
        "Définir la stratégie marketing",
        "Piloter les campagnes multicanal",
        "Suivre les KPI et la notoriété",
    ],
    "expert_google_ads": [
        "Créer et optimiser les campagnes Google Ads",
        "Gérer le budget publicitaire",
        "Suivre le retour sur investissement (ROAS)",
    ],
    "webmaster_seo": [
        "Gérer le site internet et le blog",
        "Optimiser le référencement (SEO)",
        "Rédiger des articles optimisés",
    ],
    "community_manager": [
        "Animer les réseaux sociaux",
        "Construire le calendrier éditorial",
        "Rédiger des posts engageants",
    ],
    "ingenieur_commercial": [
        "Qualifier les besoins clients",
        "Négocier et conclure les ventes",
        "Rédiger les propositions commerciales",
    ],
    "charge_prospection": [
        "Identifier de nouveaux prospects",
        "Rédiger des accroches de prospection",
        "Préparer les devis",
    ],
    "veilleur_appels_offres": [
        "Surveiller BOAMP / PLACE",
        "Repérer les opportunités pertinentes",
        "Synthétiser les consultations",
    ],
    "analyste_ao": [
        "Analyser les dossiers de consultation",
        "Étudier les critères d'attribution",
        "Définir la stratégie de réponse",
    ],
    "redacteur_memoire_technique": [
        "Rédiger les mémoires techniques",
        "Aligner la réponse sur les critères",
        "Valoriser la méthodologie",
    ],
    "gestionnaire_ao": [
        "Constituer les pièces administratives",
        "Vérifier la complétude (DC1, DC2, DUME)",
        "Préparer les check-lists",
    ],
    "responsable_financier": [
        "Élaborer le budget et le suivi de trésorerie",
        "Produire les tableaux de bord",
        "Contrôler la rentabilité",
    ],
    "gestionnaire_comptable": [
        "Émettre et suivre les factures",
        "Relancer les impayés",
        "Tenir la comptabilité courante",
    ],
    "responsable_qualite": [
        "Piloter la démarche Qualiopi / ISO",
        "Rédiger procédures et indicateurs",
        "Déployer la politique RSE",
    ],
    "auditeur_qualiopi": [
        "Préparer et mener les audits internes",
        "Identifier les écarts",
        "Bâtir les plans d'action correctifs",
    ],
}

# Tâche récurrente suggérée par défaut pour chaque agent (modifiable par l'utilisateur).
TACHES_REC_DEFAUT: Dict[str, list[str]] = {
    "conseiller_strategie": ["Chaque mois : point stratégique et priorités"],
    "assistante_direction": [
        "Chaque lundi : préparer l'agenda de la semaine",
        "Chaque jour : pré-rédiger en brouillon une réponse à tous les mails reçus (sauf no-reply)",
    ],
    "responsable_rh": ["Chaque mois : vérifier les échéances RH et contrats"],
    "charge_sourcing": ["Chaque semaine : relancer les candidats en cours"],
    "responsable_marketing": ["Chaque mois : bilan des actions marketing"],
    "expert_google_ads": ["Chaque semaine : optimiser les campagnes Google Ads"],
    "webmaster_seo": ["Chaque mois : un article de blog optimisé SEO"],
    "community_manager": ["Chaque semaine : 3 idées de posts réseaux sociaux"],
    "ingenieur_commercial": ["Chaque semaine : point sur le pipeline commercial"],
    "charge_prospection": ["Chaque semaine : 10 nouveaux prospects à contacter"],
    "veilleur_appels_offres": ["Chaque lundi : synthèse des nouveaux appels d'offres"],
    "analyste_ao": ["À chaque appel d'offres : analyse des critères"],
    "redacteur_memoire_technique": ["À chaque réponse : trame de mémoire technique"],
    "gestionnaire_ao": ["À chaque dossier : check-list des pièces administratives"],
    "responsable_financier": ["Chaque mois : tableau de bord financier"],
    "gestionnaire_comptable": ["Chaque mois : relance des factures impayées"],
    "responsable_qualite": ["Chaque trimestre : revue documentaire Qualiopi"],
    "auditeur_qualiopi": ["Chaque trimestre : audit interne blanc"],
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


def organigramme() -> list[dict]:
    """Renvoie l'organisation par services, prête pour l'affichage.

    Chaque service : ``{"nom", "icone", "couleur", "membres": [...]}``.
    """
    return [
        {
            "nom": s["nom"],
            "icone": s["icone"],
            "couleur": s["couleur"],
            "membres": list(s["membres"]),
        }
        for s in SERVICES
    ]


def router(demande: str) -> str:
    """Choisit automatiquement l'agent le plus pertinent pour une demande.

    Routage par comptage de mots-clés (déterministe, sans appel LLM).
    En cas d'absence de correspondance, renvoie l'assistante de direction
    (rôle généraliste par défaut).
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

    # L'organisation et agents.yaml décrivent exactement les mêmes agents.
    assert set(AGENTS) == set(agents), "SERVICES et agents.yaml divergent"

    # Chaque agent a ses métadonnées et une tâche existante.
    for cle in AGENTS:
        assert cle in LIBELLES, f"Libellé manquant pour : {cle}"
        assert cle in NOMS, f"Nom manquant pour : {cle}"
        assert cle in PRESENTATION, f"Présentation manquante pour : {cle}"
        assert cle in MOTS_CLES, f"Mots-clés manquants pour : {cle}"
        assert cle in AGENT_TO_TASK, f"Tâche non mappée pour : {cle}"
        assert AGENT_TO_TASK[cle] in taches, f"Tâche inexistante pour : {cle}"

    # Chaque agent a les champs requis.
    for cle, conf in agents.items():
        for champ in ("role", "goal", "backstory"):
            assert conf.get(champ), f"Champ '{champ}' manquant pour {cle}"

    # Chaque tâche a une description formatable et un expected_output.
    for cle, conf in taches.items():
        assert conf.get("expected_output"), f"expected_output manquant : {cle}"
        conf["description"].format(sujet="x", contexte="y", objectif="z")
