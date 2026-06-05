"""Interface web Streamlit pour la plateforme Agentia PNG.

Lancement :
    streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permet l'import du paquet ``agentia`` situé dans src/
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from agentia.engine import AgentiaPlatform

st.set_page_config(page_title="Agentia PNG", page_icon="🤖", layout="centered")

st.title("🤖 Agentia PNG")
st.caption("Plateforme d'agents IA pour la direction — propulsée par LangChain + LangGraph")


@st.cache_resource(show_spinner=False)
def charger_crew() -> AgentiaPlatform:
    return AgentiaPlatform(verbose=False)


crew = charger_crew()
agents = crew.agents_disponibles()

mode = st.radio(
    "Mode de traitement",
    ["Automatique 🪄", "Un agent", "Toute l'équipe"],
    horizontal=True,
    help="« Automatique » choisit pour vous le responsable le plus adapté.",
)

cle_agent = None
if mode == "Un agent":
    libelle = st.selectbox("Choisissez l'agent", list(agents.values()))
    cle_agent = next(c for c, lib in agents.items() if lib == libelle)

sujet = st.text_area("Sujet / demande", placeholder="Décrivez votre besoin…")
contexte = st.text_area("Contexte (optionnel)", value="")
objectif = st.text_input("Objectif (optionnel)", value="")

if st.button("🚀 Lancer", type="primary"):
    if not sujet.strip():
        st.warning("Merci de saisir un sujet.")
    else:
        ctx = contexte.strip() or "Aucun contexte particulier."
        obj = objectif.strip() or "Produire un livrable professionnel et exploitable."
        with st.spinner("Les agents travaillent…"):
            try:
                if mode == "Toute l'équipe":
                    resultat = crew.executer_equipe(sujet, ctx, obj)
                elif mode == "Automatique 🪄":
                    choisi, resultat = crew.executer_auto(sujet, ctx, obj)
                    st.info(f"🤖 Agent choisi : **{agents.get(choisi, choisi)}**")
                else:
                    resultat = crew.executer_agent(cle_agent, sujet, ctx, obj)
                st.markdown("### Résultat")
                st.markdown(resultat)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Erreur : {exc}")

with st.sidebar:
    st.header("Agents")
    for libelle in agents.values():
        st.markdown(f"- {libelle}")
    st.divider()
    st.caption(
        "Configurez votre clé API LLM dans un fichier `.env` "
        "(voir `.env.example`)."
    )
