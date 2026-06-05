"""Noyau de la plateforme Agentia : construction des agents et des tâches CrewAI.

Ce module charge la configuration des agents et des tâches depuis les fichiers
YAML, et expose une classe ``AgentiaCrew`` permettant :

* de récupérer un agent par sa clé (ex. ``responsable_marketing``),
* de laisser la plateforme choisir automatiquement le bon agent (routage),
* de faire traiter une demande par un seul agent,
* de lancer l'ensemble de l'équipe sur une demande (processus séquentiel).
"""

from __future__ import annotations

import os
from typing import Dict

from crewai import Agent, Crew, Process, Task

from agentia.config_loader import (
    AGENT_TO_TASK,
    LIBELLES,
    charger_agents,
    charger_taches,
    router,
)


class AgentiaCrew:
    """Équipe d'agents IA représentant les rôles métier de la direction."""

    def __init__(self, modele: str | None = None, verbose: bool = True) -> None:
        # Le modèle LLM peut être surchargé par variable d'environnement.
        self.modele = modele or os.getenv("AGENTIA_MODEL", "gpt-4o-mini")
        self.verbose = verbose
        self.config_agents = charger_agents()
        self.config_taches = charger_taches()
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

    def choisir_agent(self, demande: str) -> str:
        """Sélectionne automatiquement l'agent le plus pertinent."""
        return router(demande)

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

    def executer_auto(
        self,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ) -> tuple[str, str]:
        """Choisit l'agent automatiquement puis traite la demande.

        Retourne un tuple (clé_agent_choisi, résultat).
        """
        cle_agent = self.choisir_agent(sujet)
        resultat = self.executer_agent(cle_agent, sujet, contexte, objectif)
        return cle_agent, resultat

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
