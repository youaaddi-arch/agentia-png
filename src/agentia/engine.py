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
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
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

    def stream_agent(
        self,
        cle_agent: str,
        sujet: str,
        contexte: str = "Aucun contexte particulier.",
        objectif: str = "Produire un livrable professionnel et exploitable.",
    ):
        """Génère la réponse d'un agent au fil de l'eau (streaming).

        Renvoie un itérateur de morceaux de texte, pour un affichage progressif
        (perçu comme bien plus rapide). Utilisé par l'interface de conversation.
        """
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
        messages = [
            SystemMessage(content=self._prompt_systeme(cle_agent)),
            HumanMessage(content=self._prompt_tache(cle_agent, etat)),
        ]
        for morceau in self.llm.stream(messages):
            texte = getattr(morceau, "content", "")
            if texte:
                yield texte

    # ------------------------------------------------------------------
    # Agents AVEC outils (accès réel au Drive / Gmail)
    # ------------------------------------------------------------------
    def _outils_google(self):
        from langchain_core.tools import tool

        from agentia import google_tools as g

        @tool
        def chercher_dans_drive(requete: str) -> str:
            """Cherche des fichiers dans le Google Drive de l'utilisateur.
            Passe le MOT-CLÉ du document (ex. 'BPU', 'convention'), pas la phrase
            entière. Renvoie les noms et les liens des fichiers trouvés."""
            return g.rechercher_drive(requete)

        @tool
        def envoyer_email(destinataire: str, sujet: str, message: str) -> str:
            """ENVOIE réellement un email. À utiliser quand l'utilisateur demande
            de s'envoyer quelque chose à lui-même (« envoie-moi »). Mets
            destinataire='moi' pour utiliser son adresse. Le message peut contenir
            les liens des fichiers Drive trouvés."""
            return g.envoyer_email(destinataire, sujet, message)

        @tool
        def preparer_brouillon_email(destinataire: str, sujet: str, message: str) -> str:
            """Prépare un BROUILLON Gmail (n'envoie pas). À utiliser pour un
            destinataire EXTERNE (client, collègue), par sécurité."""
            return g.creer_brouillon_email(destinataire, sujet, message)

        return [chercher_dans_drive, envoyer_email, preparer_brouillon_email]

    def repondre_avec_outils(self, cle_agent: str, message: str) -> str:
        """Fait répondre un agent en lui donnant accès au Drive et à Gmail.

        Boucle d'appel d'outils : le modèle peut décider d'appeler un outil
        (chercher dans le Drive, préparer un brouillon…), on l'exécute, puis on
        lui renvoie le résultat jusqu'à la réponse finale.
        """
        outils = self._outils_google()
        dispatch = {o.name: o for o in outils}
        llm = self.llm.bind_tools(outils)

        from agentia.google_tools import adresse_proprietaire

        email_proprio = adresse_proprietaire()
        info_email = (
            f"\n- L'adresse email de l'utilisateur est {email_proprio}. Quand il "
            "dit « envoie-moi » ou « à moi-même », utilise CETTE adresse comme "
            "destinataire, sans la redemander."
            if email_proprio
            else ""
        )
        consigne = (
            "\n\nTu disposes d'OUTILS réels connectés au Drive et à Gmail de "
            "l'utilisateur : utilise-les pour agir concrètement plutôt que de "
            "donner des conseils généraux. N'invente JAMAIS de fichier ni de "
            "résultat : appuie-toi uniquement sur ce que renvoient les outils.\n"
            "- Pour chercher un fichier, passe le MOT-CLÉ (ex. 'BPU'), pas la "
            "phrase entière. Si l'utilisateur fait une petite faute de frappe "
            "(ex. 'PBU' au lieu de 'BPU'), tente aussi la variante la plus "
            "probable.\n"
            "- Pour les emails : quand l'utilisateur dit « envoie-moi » / « à "
            "moi-même », ENVOIE réellement le message à sa propre adresse avec "
            "l'outil envoyer_email (destinataire='moi'), sans redemander. Pour un "
            "destinataire EXTERNE (client, collègue), prépare un BROUILLON. "
            "Inclus toujours les liens des fichiers Drive trouvés dans le message."
            + info_email
        )
        messages = [
            SystemMessage(content=self._prompt_systeme(cle_agent) + consigne),
            HumanMessage(content=message),
        ]
        reponse = None
        for _ in range(6):  # garde-fou anti-boucle
            reponse = llm.invoke(messages)
            messages.append(reponse)
            appels = getattr(reponse, "tool_calls", None)
            if not appels:
                break
            for appel in appels:
                outil = dispatch.get(appel["name"])
                sortie = outil.invoke(appel["args"]) if outil else "Outil inconnu."
                messages.append(
                    ToolMessage(content=str(sortie), tool_call_id=appel["id"])
                )
        return str(getattr(reponse, "content", "") or "(réponse vide)")

    def predrafter_reponses(self, maximum: int = 10) -> str:
        """Pré-rédige (en brouillon) une réponse à chaque email reçu (hors no-reply).

        Lit la boîte de réception, génère une réponse pour chaque expéditeur réel,
        et crée un brouillon de réponse rattaché à la conversation. N'envoie rien.
        """
        from agentia import google_tools as g

        emails = g.lister_emails_a_traiter(maximum)
        if isinstance(emails, str):
            return emails  # message d'erreur (ex. autorisation lecture manquante)
        if not emails:
            return "Aucun email à traiter (boîte vide, ou uniquement des no-reply)."

        prompt_systeme = self._prompt_systeme("assistante_direction")
        prepares, erreurs = [], []
        for mail in emails:
            consigne = (
                "Rédige UNIQUEMENT le corps d'une réponse professionnelle, "
                "courtoise et concise (en français) à l'email ci-dessous. Ne mets "
                "ni objet ni en-tête, seulement le texte de la réponse, prêt à "
                "relire et envoyer.\n\n"
                f"Expéditeur : {mail['from_name']} <{mail['from_email']}>\n"
                f"Objet : {mail['subject']}\n"
                f"Aperçu reçu : {mail['snippet']}"
            )
            try:
                texte = self.llm.invoke(
                    [
                        SystemMessage(content=prompt_systeme),
                        HumanMessage(content=consigne),
                    ]
                ).content
            except Exception as exc:  # noqa: BLE001
                return f"Erreur lors de la génération des réponses : {exc}"
            sujet = mail["subject"]
            if not sujet.lower().startswith("re:"):
                sujet = f"Re: {sujet}"
            statut = g.creer_brouillon_reponse(
                mail["threadId"], mail["from_email"], sujet, str(texte), mail.get("message_id")
            )
            etiquette = f"{mail['from_name'] or mail['from_email']} — {mail['subject']}"
            (prepares if statut == "ok" else erreurs).append(etiquette)

        lignes = [f"✅ {len(prepares)} brouillon(s) de réponse préparé(s) :"]
        lignes += [f"- {p}" for p in prepares]
        if erreurs:
            lignes.append(f"\n⚠️ {len(erreurs)} non traité(s) :")
            lignes += [f"- {e}" for e in erreurs]
        lignes.append("\nIls vous attendent dans vos brouillons Gmail — à relire et envoyer.")
        return "\n".join(lignes)

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
