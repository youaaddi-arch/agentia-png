"""Tests de la configuration et du routage (sans dépendance à LangChain)."""

import sys
from pathlib import Path

# Permet d'importer le paquet ``agentia`` depuis src/ sans installation.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentia.config_loader import (  # noqa: E402
    AGENT_TO_TASK,
    AGENTS,
    LEADS,
    LIBELLES,
    NOMS,
    PRESENTATION,
    SERVICES,
    charger_agents,
    charger_taches,
    organigramme,
    router,
    valider_configuration,
)


def test_sept_services():
    assert len(SERVICES) == 7
    # Chaque service a un nom, une icône, une couleur et au moins un membre.
    for s in SERVICES:
        assert s["nom"] and s["icone"] and s["couleur"]
        assert len(s["membres"]) >= 1


def test_dix_huit_agents():
    agents = charger_agents()
    assert set(AGENTS) == set(agents)
    assert len(AGENTS) == 18
    # Pas de doublon dans l'ordre d'affichage.
    assert len(AGENTS) == len(set(AGENTS))


def test_un_lead_par_service():
    assert len(LEADS) == len(SERVICES)
    assert LEADS == [s["membres"][0] for s in SERVICES]


def test_metadonnees_completes():
    for cle in AGENTS:
        assert cle in NOMS and NOMS[cle].strip()
        assert cle in LIBELLES and LIBELLES[cle].strip()
        assert cle in PRESENTATION
        assert PRESENTATION[cle].get("icone")
        assert PRESENTATION[cle].get("accroche")
        assert cle in AGENT_TO_TASK


def test_taches_existantes():
    taches = charger_taches()
    assert set(AGENT_TO_TASK.values()) <= set(taches)


def test_avatars_presents():
    base = Path(__file__).parent.parent / "assets" / "avatars"
    for cle in AGENTS:
        assert (base / f"{cle}.png").is_file(), f"avatar manquant : {cle}"


def test_organigramme_structure():
    org = organigramme()
    assert [s["nom"] for s in org] == [s["nom"] for s in SERVICES]


def test_configuration_valide():
    valider_configuration()


# ---------------------------------------------------------------------------
# Routage
# ---------------------------------------------------------------------------
def test_routage_marketing():
    assert router("Je veux lancer une campagne de communication") == \
        "responsable_marketing"


def test_routage_appels_offres():
    assert router("Analyse cet appel d'offres marché public, critères CCTP") == \
        "analyste_ao"


def test_routage_commercial():
    assert router("Prépare un argumentaire de vente et la négociation") == \
        "ingenieur_commercial"


def test_routage_qualite():
    assert router("Préparer la certification Qualiopi et les procédures ISO") == \
        "responsable_qualite"


def test_routage_finance():
    assert router("Établir le budget et le suivi de trésorerie") == \
        "responsable_financier"


def test_routage_rh():
    assert router("Rédige un contrat de travail et le bulletin de paie") == \
        "responsable_rh"


def test_routage_sourcing():
    assert router("Lance un recrutement en alternance, rédige l'offre d'emploi") == \
        "charge_sourcing"


def test_routage_par_defaut_assistante():
    assert router("xyz quelque chose d'indéterminé") == "assistante_direction"
