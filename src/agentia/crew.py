"""Noyau de la plateforme Agentia : construction des agents et des tâches CrewAI.

Ce module charge la configuration des agents et des tâches depuis les fichiers
YAML, et expose une classe ``AgentiaCrew`` permettant :

* de récupérer un agent par sa clé (ex. ``responsable_marketing``),
* de faire traiter une demande par un seul agent,
* de lancer l'ensemble de l'équipe sur une demande (processus séquentiel).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

import yaml
from crewai import Agent, Crew, Process, Task

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

# Libellés lisibles pour l'interface en ligne de commande
LIBELLES: Dict[str, str] = {
    "responsable_marketing": "Responsable Marketing",
    "responsable_marches_publics": "Responsable Marchés Publics",
    "responsable_commercial": "Responsable Commercial",
    "assistante_direction": "Assistant·e de Direction",
    "responsable_administratif": "Responsable Administratif & Financier",
    "responsable_certification_rs": "Responsable Certification & RSE (RS)",
}


def _load_yaml(nom_fichier: str) -> dict:
    """Charge un fichier YAML du dossier de configuration."""
    chemin = CONFIG_DIR / nom_fichier
    with chemin.open("r", encoding="utf-8") as flux:
        return yaml.safe_load(flux)


class AgentiaCrew:
    """Équipe d'agents IA représentant les rôles métier de la direction."""

    def __init__(self, modele: str | None = None, verbose: bool = True) -> None:
        # Le modèle LLM peut être surchargé par variable d'environnement.
        self.modele = modele or os.getenv("AGENTIA_MODEL", "gpt-4o-mini")
        self.verbose = verbose
        self.config_agents = _load_yaml("agents.yaml")
        self.config_taches = _load_yaml("tasks.yaml")
        self._agents: Dict[str, Agent] = {}
        self._construire_agents()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def _construire_agents(self) -> None:
        for cle, conf in self.config_agents.items():
            self._agents[cle] = Agent(
                role=conf["role"].strip(),
                goal=conf["goal"].strip(),
                backstory=conf["backstory"].strip(),
                llm=self.modele,
                verbose=self.verbose,
                allow_delegation=False,
            )

    # ------------------------------------------------------------------
    # Accès
    # ------------------------------------------------------------------
    def agents_disponibles(self) -> Dict[str, str]:
        """Retourne {clé: libellé} des agents disponibles."""
        return {cle: LIBELLES.get(cle, cle) for cle in self._agents}

    def get_agent(self, cle: str) -> Agent:
        if cle not in self._agents:
            raise KeyError(
                f"Agent inconnu : '{cle}'. "
                f"Agents disponibles : {', '.join(self._agents)}"
            )
        return self._agents[cle]

    def _construire_tache(self, cle_agent: str, variables: dict) -> Task:
        cle_tache = AGENT_TO_TASK[cle_agent]
        conf = self.config_taches[cle_tache]
        return Task(
            description=conf["description"].format(**variables),
            expected_output=conf["expected_output"].strip(),
            agent=self.get_agent(cle_agent),
        )

    # ------------------------------------------------------------------
    # Exécution
    # ------------------------------------------------------------------
    def executer_agent(
        self,
        cle_agent: str,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ) -> str:
        """Fait traiter une demande par un seul agent."""
        variables = {"sujet": sujet, "contexte": contexte, "objectif": objectif}
        tache = self._construire_tache(cle_agent, variables)
        crew = Crew(
            agents=[self.get_agent(cle_agent)],
            tasks=[tache],
            process=Process.sequential,
            verbose=self.verbose,
        )
        return str(crew.kickoff())

    def executer_equipe(
        self,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ) -> str:
        """Fait traiter une même demande par toute l'équipe (séquentiel)."""
        variables = {"sujet": sujet, "contexte": contexte, "objectif": objectif}
        taches = [
            self._construire_tache(cle, variables) for cle in self._agents
        ]
        crew = Crew(
            agents=list(self._agents.values()),
            tasks=taches,
            process=Process.sequential,
            verbose=self.verbose,
        )
        return str(crew.kickoff())
