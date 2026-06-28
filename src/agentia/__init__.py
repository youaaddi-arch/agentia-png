"""Agentia PNG — Plateforme d'agents IA basée sur LangChain + LangGraph."""

__all__ = ["AgentiaPlatform"]
__version__ = "0.2.0"


def __getattr__(name):
    # Import paresseux : évite de charger LangChain/LangGraph (lourd) tant qu'on
    # n'instancie pas la plateforme. Permet d'utiliser config_loader/router sans
    # dépendance LLM (utile pour les tests).
    if name == "AgentiaPlatform":
        from agentia.engine import AgentiaPlatform

        return AgentiaPlatform
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
