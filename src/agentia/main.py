"""Point d'entrée en ligne de commande de la plateforme Agentia.

Exemples d'utilisation :

    # Lister les agents disponibles
    python -m agentia.main --liste

    # Mode AUTO : la plateforme choisit toute seule le bon responsable
    python -m agentia.main --sujet "Rédige un courrier pour un client"

    # Forcer un agent précis
    python -m agentia.main --agent responsable_marketing \
        --sujet "Lancement d'une nouvelle offre SaaS"

    # Faire traiter une demande par toute l'équipe
    python -m agentia.main --equipe --sujet "Réponse à un marché public"

    # Mode interactif (sans argument) : on vous pose les questions
    python -m agentia.main
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv est optionnel
    pass

from agentia.config_loader import LIBELLES


def _verifier_cle_api() -> None:
    """Avertit clairement si aucune clé API LLM n'est configurée."""
    cles = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY")
    if not any(os.getenv(c) for c in cles):
        print(
            "\n⚠️  Aucune clé API détectée.\n"
            "   Copiez le fichier .env.example en .env et renseignez votre clé\n"
            "   (ex. OPENAI_API_KEY=sk-...). Sans clé, les agents ne peuvent pas\n"
            "   réfléchir.\n",
            file=sys.stderr,
        )


def _afficher_agents(crew) -> None:
    print("\nAgents disponibles :\n")
    for cle, libelle in crew.agents_disponibles().items():
        print(f"  • {cle:32s} → {libelle}")
    print()


def _mode_interactif(crew) -> None:
    _afficher_agents(crew)
    print("Tapez 'auto' pour laisser la plateforme choisir, 'equipe' pour")
    print("solliciter toute l'équipe, ou la clé d'un agent ci-dessus.\n")
    cle = input("Choix [auto] : ").strip() or "auto"
    sujet = input("Sujet / demande : ").strip()
    contexte = input("Contexte (entrée pour ignorer) : ").strip() or \
        "Aucun contexte particulier."
    objectif = input("Objectif (entrée pour ignorer) : ").strip() or \
        "Produire un livrable professionnel et exploitable."

    print("\n⏳ Traitement en cours...\n")
    if cle == "equipe":
        resultat = crew.executer_equipe(sujet, contexte, objectif)
    elif cle == "auto":
        choisi, resultat = crew.executer_auto(sujet, contexte, objectif)
        print(f"🤖 Agent choisi automatiquement : {LIBELLES.get(choisi, choisi)}\n")
    else:
        resultat = crew.executer_agent(cle, sujet, contexte, objectif)
    print("\n===== RÉSULTAT =====\n")
    print(resultat)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plateforme d'agents IA (LangGraph) — Agentia PNG",
    )
    parser.add_argument("--liste", action="store_true", help="Lister les agents")
    parser.add_argument("--agent", help="Clé de l'agent à solliciter (sinon : auto)")
    parser.add_argument("--equipe", action="store_true", help="Solliciter toute l'équipe")
    parser.add_argument("--sujet", help="Sujet / demande à traiter")
    parser.add_argument("--contexte", default="Aucun contexte particulier.")
    parser.add_argument(
        "--objectif",
        default="Produire un livrable professionnel et exploitable.",
    )
    parser.add_argument("--modele", help="Modèle LLM à utiliser (ex. gpt-4o-mini)")
    args = parser.parse_args(argv)

    # Import tardif : évite de charger LangChain juste pour --liste / l'aide.
    from agentia.engine import AgentiaPlatform

    crew = AgentiaPlatform(modele=args.modele)

    if args.liste:
        _afficher_agents(crew)
        return 0

    _verifier_cle_api()

    # Aucun argument d'action -> mode interactif
    if not args.sujet and not args.agent and not args.equipe:
        _mode_interactif(crew)
        return 0

    if not args.sujet:
        parser.error("--sujet est requis pour traiter une demande.")

    if args.equipe:
        resultat = crew.executer_equipe(args.sujet, args.contexte, args.objectif)
    elif args.agent:
        resultat = crew.executer_agent(
            args.agent, args.sujet, args.contexte, args.objectif
        )
    else:
        # Mode AUTO par défaut : la plateforme choisit le bon agent.
        choisi, resultat = crew.executer_auto(
            args.sujet, args.contexte, args.objectif
        )
        print(f"🤖 Agent choisi automatiquement : {LIBELLES.get(choisi, choisi)}")

    print("\n===== RÉSULTAT =====\n")
    print(resultat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
