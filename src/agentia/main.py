"""Point d'entrée en ligne de commande de la plateforme Agentia.

Exemples d'utilisation :

    # Lister les agents disponibles
    python -m agentia.main --liste

    # Faire traiter une demande par un agent précis
    python -m agentia.main --agent responsable_marketing \
        --sujet "Lancement d'une nouvelle offre SaaS" \
        --contexte "Cible PME, budget 20k€" \
        --objectif "Générer 100 leads qualifiés en 3 mois"

    # Mode interactif (questions/réponses)
    python -m agentia.main

    # Faire traiter une demande par toute l'équipe
    python -m agentia.main --equipe --sujet "Réponse à un marché public de formation"
"""

from __future__ import annotations

import argparse
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv est optionnel
    pass

from agentia.crew import AgentiaCrew


def _afficher_agents(crew: AgentiaCrew) -> None:
    print("\nAgents disponibles :\n")
    for cle, libelle in crew.agents_disponibles().items():
        print(f"  • {cle:32s} → {libelle}")
    print()


def _mode_interactif(crew: AgentiaCrew) -> None:
    _afficher_agents(crew)
    cle = input("Choisissez un agent (clé) ou 'equipe' pour toute l'équipe : ").strip()
    sujet = input("Sujet / demande : ").strip()
    contexte = input("Contexte (entrée pour ignorer) : ").strip() or \
        "Aucun contexte particulier."
    objectif = input("Objectif (entrée pour ignorer) : ").strip() or \
        "Produire un livrable professionnel et exploitable."

    print("\n⏳ Traitement en cours...\n")
    if cle == "equipe":
        resultat = crew.executer_equipe(sujet, contexte, objectif)
    else:
        resultat = crew.executer_agent(cle, sujet, contexte, objectif)
    print("\n===== RÉSULTAT =====\n")
    print(resultat)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Plateforme d'agents IA (CrewAI) — Agentia PNG",
    )
    parser.add_argument("--liste", action="store_true", help="Lister les agents")
    parser.add_argument("--agent", help="Clé de l'agent à solliciter")
    parser.add_argument("--equipe", action="store_true", help="Solliciter toute l'équipe")
    parser.add_argument("--sujet", help="Sujet / demande à traiter")
    parser.add_argument("--contexte", default="Aucun contexte particulier.")
    parser.add_argument(
        "--objectif",
        default="Produire un livrable professionnel et exploitable.",
    )
    parser.add_argument("--modele", help="Modèle LLM à utiliser (ex. gpt-4o-mini)")
    args = parser.parse_args(argv)

    crew = AgentiaCrew(modele=args.modele)

    if args.liste:
        _afficher_agents(crew)
        return 0

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
        parser.error("Précisez --agent <clé> ou --equipe.")

    print("\n===== RÉSULTAT =====\n")
    print(resultat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
