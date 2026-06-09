"""Tests de la configuration et du routage (sans dépendance à LangChain)."""

import sys
from pathlib import Path

# Permet d'importer le paquet ``agentia`` depuis src/ sans installation.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentia.config_loader import (  # noqa: E402
    AGENT_TO_TASK,
    CEO,
    EQUIPES,
    LIBELLES,
    PRESENTATION,
    RESPONSABLES,
    SPECIALISTES,
    charger_agents,
    charger_taches,
    organigramme,
    router,
    valider_configuration,
)

# 1 CEO + 6 responsables + 15 spécialistes = 22 agents.
RESPONSABLES_ATTENDUS = {
    "responsable_marketing",
    "responsable_marches_publics",
    "responsable_commercial",
    "assistante_direction",
    "responsable_administratif",
    "responsable_certification_rs",
}


def test_organigramme_complet():
    agents = charger_agents()
    # Tous les agents de l'organigramme existent bien dans agents.yaml.
    attendus = {CEO, *RESPONSABLES, *SPECIALISTES}
    assert set(agents) == attendus
    assert len(agents) == 22


def test_responsables_et_specialistes():
    assert set(RESPONSABLES) == RESPONSABLES_ATTENDUS
    # Chaque responsable a au moins un spécialiste dans sa sous-équipe.
    for _, equipe in EQUIPES:
        assert len(equipe) >= 1
    assert len(SPECIALISTES) == 15


def test_taches_definies():
    taches = charger_taches()
    # 1 (ceo) + 1 (générique) + 6 (responsables) = 8 tâches.
    assert len(taches) == 8
    # Toutes les tâches référencées par les agents existent réellement.
    assert set(AGENT_TO_TASK.values()) == set(taches)


def test_chaque_agent_a_une_tache():
    agents = charger_agents()
    for cle in agents:
        assert cle in AGENT_TO_TASK, f"Tâche non mappée pour : {cle}"


def test_libelles_complets():
    assert set(LIBELLES) == set(charger_agents())


def test_presentation_complete():
    # Chaque agent a une icône et une accroche pour les cartes de l'accueil.
    assert set(PRESENTATION) == set(charger_agents())
    for cle, infos in PRESENTATION.items():
        assert infos.get("icone"), f"icône manquante : {cle}"
        assert infos.get("accroche"), f"accroche manquante : {cle}"


def test_organigramme_structure():
    org = organigramme()
    assert org["ceo"] == CEO
    assert [e["responsable"] for e in org["equipes"]] == RESPONSABLES


def test_configuration_valide():
    # Ne doit lever aucune exception.
    valider_configuration()


# ---------------------------------------------------------------------------
# Routage : les demandes larges vont au responsable, les demandes précises
# au bon spécialiste.
# ---------------------------------------------------------------------------
def test_routage_marketing():
    assert router("Je veux lancer une campagne de communication") == \
        "responsable_marketing"


def test_routage_marches_publics():
    assert router("Réponse à un appel d'offres marché public BOAMP") == \
        "responsable_marches_publics"


def test_routage_commercial():
    assert router("Rédige un devis pour un prospect et négocie la vente") == \
        "responsable_commercial"


def test_routage_certification():
    assert router("Préparer l'audit de certification Qualiopi ISO 9001") == \
        "responsable_certification_rs"


def test_routage_administratif():
    assert router("Établir la facturation et le suivi de trésorerie") == \
        "responsable_administratif"


def test_routage_par_defaut_assistante():
    # Demande sans mot-clé identifiable -> assistant·e de direction.
    assert router("xyz quelque chose d'indéterminé") == "assistante_direction"


def test_routage_specialiste_community_manager():
    assert router("Rédige un post LinkedIn pour nos réseaux sociaux") == \
        "community_manager"


def test_routage_specialiste_google_ads():
    assert router("Crée une campagne Google Ads avec des annonces") == \
        "expert_google_ads"


def test_routage_specialiste_suivi_documents():
    assert router("Suivre la date de validité et l'échéance de nos documents") == \
        "suivi_documents"


def test_routage_ceo_strategie():
    assert router("Définis la vision et la stratégie, la feuille de route") == \
        CEO
