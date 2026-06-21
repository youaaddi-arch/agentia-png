"""Moteur de la plateforme Agentia basé sur LangChain + LangGraph.

L'orchestration est un graphe d'états LangGraph :

    [routage] --(choisit l'agent)--> [agent_xxx] --> FIN

* Le nœud « routage » sélectionne l'agent (automatiquement via mots-clés, ou
  selon l'agent imposé par l'utilisateur).
* Chaque agent est un nœud qui appelle le LLM avec son prompt système (rôle,
  objectif, histoire) et la tâche à réaliser.

La classe ``AgentiaPlatform`` expose la même interface que précédemment
(``executer_agent``, ``executer_auto``, ``executer_equipe``…), si bien que le
CLI et l'interface web n'ont pas besoin de changer.
"""

from __future__ import annotations

import os
from typing import Dict, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph

from agentia.config_loader import (
    AGENT_TO_TASK,
    LEADS,
    LIBELLES,
    charger_agents,
    charger_taches,
    router,
)

# Modèle par défaut : Claude Sonnet (bon rapport qualité/coût). Surchargable
# par la variable d'environnement AGENTIA_MODEL, au format "fournisseur:modele"
# (ex. "openai:gpt-4o-mini", "anthropic:claude-sonnet-4-6").
MODELE_DEFAUT = "anthropic:claude-sonnet-4-6"


class EtatAgent(TypedDict, total=False):
    """État circulant dans le graphe LangGraph."""

    sujet: str
    contexte: str
    objectif: str
    agent: str
    resultat: str


class AgentiaPlatform:
    """Plateforme d'agents IA (LangGraph) pour les rôles métier de la direction."""

    def __init__(self, modele: str | None = None, verbose: bool = True) -> None:
        self.modele = modele or os.getenv("AGENTIA_MODEL", MODELE_DEFAUT)
        self.verbose = verbose
        self.config_agents = charger_agents()
        self.config_taches = charger_taches()
        # On construit l'objet LLM dès l'init : c'est peu coûteux et la clé API
        # n'est requise qu'au moment de l'invocation (pas de la construction).
        # NB : on évite une @property ici car LangGraph introspecte les closures
        # des nœuds au moment de compile() et déclencherait le getter.
        self.llm = init_chat_model(self.modele, temperature=0.3)
        self._graphe = self._construire_graphe()

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------
    def _prompt_systeme(self, cle_agent: str) -> str:
        conf = self.config_agents[cle_agent]
        return (
            f"Tu es {conf['role'].strip()}.\n\n"
            f"Objectif : {conf['goal'].strip()}\n\n"
            f"{conf['backstory'].strip()}\n\n"
            "Réponds toujours en français, de façon structurée et professionnelle, "
            "au format Markdown."
        )

    def _prompt_tache(self, cle_agent: str, state: EtatAgent) -> str:
        conf = self.config_taches[AGENT_TO_TASK[cle_agent]]
        description = conf["description"].format(
            sujet=state.get("sujet", ""),
            contexte=state.get("contexte", "Aucun contexte particulier."),
            objectif=state.get("objectif", "Produire un livrable exploitable."),
        )
        return (
            f"{description}\n\n"
            f"Format attendu : {conf['expected_output'].strip()}"
        )

    # ------------------------------------------------------------------
    # Construction du graphe
    # ------------------------------------------------------------------
    def _faire_noeud_agent(self, cle_agent: str):
        def noeud(state: EtatAgent) -> EtatAgent:
            messages = [
                SystemMessage(content=self._prompt_systeme(cle_agent)),
                HumanMessage(content=self._prompt_tache(cle_agent, state)),
            ]
            reponse = self.llm.invoke(messages)
            return {"agent": cle_agent, "resultat": reponse.content}

        return noeud

    def _noeud_routage(self, state: EtatAgent) -> EtatAgent:
        # Si l'agent est déjà imposé, on le garde ; sinon on route par mots-clés.
        if state.get("agent"):
            return {}
        return {"agent": router(state.get("sujet", ""))}

    def _construire_graphe(self):
        graphe = StateGraph(EtatAgent)
        graphe.add_node("routage", self._noeud_routage)
        for cle in self.config_agents:
            graphe.add_node(cle, self._faire_noeud_agent(cle))

        graphe.set_entry_point("routage")
        graphe.add_conditional_edges(
            "routage",
            lambda state: state["agent"],
            {cle: cle for cle in self.config_agents},
        )
        for cle in self.config_agents:
            graphe.add_edge(cle, END)
        return graphe.compile()

    # ------------------------------------------------------------------
    # Accès
    # ------------------------------------------------------------------
    def agents_disponibles(self) -> Dict[str, str]:
        return {cle: LIBELLES.get(cle, cle) for cle in self.config_agents}

    def choisir_agent(self, demande: str) -> str:
        return router(demande)

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
        if cle_agent not in self.config_agents:
            raise KeyError(
                f"Agent inconnu : '{cle_agent}'. "
                f"Agents disponibles : {', '.join(self.config_agents)}"
            )
        etat: EtatAgent = {
            "sujet": sujet,
            "contexte": contexte,
            "objectif": objectif,
            "agent": cle_agent,
        }
        resultat = self._graphe.invoke(etat)
        return str(resultat["resultat"])

    def executer_auto(
        self,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ) -> tuple[str, str]:
        etat: EtatAgent = {
            "sujet": sujet,
            "contexte": contexte,
            "objectif": objectif,
            "agent": "",
        }
        resultat = self._graphe.invoke(etat)
        return str(resultat["agent"]), str(resultat["resultat"])

    def executer_equipe(
        self,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ) -> str:
        """Fait traiter la demande par le lead de chaque service, puis assemble.

        On ne mobilise qu'un agent « lead » par service (7) : faire répondre
        tous les membres multiplierait inutilement les appels au LLM.
        """
        morceaux: list[str] = []
        for cle in LEADS:
            sortie = self.executer_agent(cle, sujet, contexte, objectif)
            morceaux.append(f"## {LIBELLES.get(cle, cle)}\n\n{sortie}")
        return "\n\n---\n\n".join(morceaux)
