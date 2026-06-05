"""Tests de la configuration et du routage (sans dépendance à CrewAI)."""

import sys
from pathlib import Path

# Permet d'importer le paquet ``agentia`` depuis src/ sans installation.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentia.config_loader import (  # noqa: E402
    AGENT_TO_TASK,
    LIBELLES,
    charger_agents,
    charger_taches,
    router,
    valider_configuration,
)

AGENTS_ATTENDUS = {
    "responsable_marketing",
    "responsable_marches_publics",
    "responsable_commercial",
    "assistante_direction",
    "responsable_administratif",
    "responsable_certification_rs",
}


def test_six_agents_definis():
    agents = charger_agents()
    assert set(agents) == AGENTS_ATTENDUS
    assert len(agents) == 6


def test_six_taches_definies():
    taches = charger_taches()
    assert len(taches) == 6
    assert set(AGENT_TO_TASK.values()) == set(taches)


def test_libelles_complets():
    assert set(LIBELLES) == AGENTS_ATTENDUS


def test_configuration_valide():
    # Ne doit lever aucune exception.
    valider_configuration()


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
