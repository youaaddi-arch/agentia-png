"""Agentia PNG — Plateforme d'agents IA basée sur CrewAI."""

__all__ = ["AgentiaCrew"]
__version__ = "0.1.0"


def __getattr__(name):
    # Import paresseux : évite de charger CrewAI (lourd) tant qu'on n'instancie
    # pas réellement l'équipe. Permet d'utiliser config_loader/router sans LLM.
    if name == "AgentiaCrew":
        from agentia.crew import AgentiaCrew

        return AgentiaCrew
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
