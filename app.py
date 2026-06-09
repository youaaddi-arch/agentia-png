"""Interface web Agentia PNG — page d'accueil + plateforme d'agents IA.

Design inspiré de CrewAI : fond sombre, accent corail, cartes d'agents.

Lancement :
    streamlit run app.py
"""

from __future__ import annotations

import os
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

# Sur Streamlit Community Cloud, les clés sont saisies dans « Secrets ».
# On les recopie dans les variables d'environnement pour que le moteur
# (init_chat_model) les trouve, exactement comme le ferait un fichier .env.
try:
    for _cle in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AGENTIA_MODEL"):
        if _cle in st.secrets and not os.getenv(_cle):
            os.environ[_cle] = str(st.secrets[_cle])
except Exception:  # noqa: BLE001 — aucun secret défini (ex. en local) : on ignore.
    pass

from agentia.config_loader import (
    LIBELLES,
    PRESENTATION,
    organigramme,
)
from agentia.engine import AgentiaPlatform

st.set_page_config(
    page_title="Agentia PNG — Vos agents IA",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Style (CSS) — inspiré de CrewAI
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      /* Cache le menu/footer Streamlit pour un rendu « produit » */
      #MainMenu, footer {visibility: hidden;}

      .block-container {padding-top: 2.2rem; max-width: 1150px;}

      /* ---- Hero ---- */
      .hero {text-align: center; padding: 18px 0 6px;}
      .hero .eyebrow {
        display:inline-block; letter-spacing:.18em; font-size:.72rem;
        text-transform:uppercase; color:#FF5A4C; font-weight:700;
        border:1px solid rgba(255,90,76,.35); border-radius:999px;
        padding:6px 14px; margin-bottom:18px; background:rgba(255,90,76,.07);
      }
      .hero h1 {
        font-size: 3.1rem; font-weight: 800; line-height:1.05; margin:0;
        background: linear-gradient(90deg,#FFFFFF 0%, #FFC9C2 60%, #FF5A4C 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      }
      .hero p.sub {
        color:#A7AEC0; font-size:1.12rem; max-width:660px;
        margin:16px auto 6px; line-height:1.6;
      }

      /* ---- Section title ---- */
      .section-title {
        font-size:1.35rem; font-weight:700; color:#fff;
        margin:30px 0 4px; display:flex; align-items:center; gap:10px;
      }
      .section-sub {color:#8b91a4; margin:0 0 14px; font-size:.95rem;}

      /* ---- Grille de cartes d'agents ---- */
      .agent-grid {
        display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
        gap:16px; margin: 6px 0 10px;
      }
      .agent-card {
        background: linear-gradient(180deg,#191B24 0%, #14161d 100%);
        border:1px solid #272a38; border-radius:16px; padding:22px 20px;
        transition: all .18s ease;
      }
      .agent-card:hover {
        border-color:#FF5A4C; transform:translateY(-4px);
        box-shadow:0 14px 34px rgba(255,90,76,.14);
      }
      .agent-card .icon {font-size:30px; line-height:1;}
      .agent-card .name {font-weight:700; font-size:1.05rem; color:#fff; margin:12px 0 6px;}
      .agent-card .desc {color:#9aa1b4; font-size:.9rem; line-height:1.55;}

      /* ---- Bandeau étapes ---- */
      .steps {display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:6px 0 8px;}
      .step {background:#14161d; border:1px solid #272a38; border-radius:12px; padding:14px 16px;}
      .step .n {color:#FF5A4C; font-weight:800; font-size:.8rem;}
      .step .t {color:#cfd3df; font-size:.9rem; margin-top:4px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def charger_plateforme() -> AgentiaPlatform:
    return AgentiaPlatform(verbose=False)


plateforme = charger_plateforme()
agents = plateforme.agents_disponibles()

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <span class="eyebrow">Paris Nord Groupe · Plateforme d'agents IA</span>
      <h1>Agentia</h1>
      <p class="sub">Votre direction augmentée par l'IA. Un CEO, six responsables
      et leurs spécialistes, prêts à rédiger, analyser et produire vos livrables
      professionnels — en français, en quelques secondes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Organigramme cliquable (CEO -> responsables -> spécialistes)
# ---------------------------------------------------------------------------
if "agent_selectionne" not in st.session_state:
    st.session_state.agent_selectionne = None

st.markdown(
    '<div class="section-title">👥 Votre équipe (organigramme)</div>'
    '<div class="section-sub">Cliquez sur un agent pour qu\'il traite votre '
    'demande — ou laissez le mode automatique choisir pour vous.</div>',
    unsafe_allow_html=True,
)


def bouton_agent(cle: str) -> None:
    """Affiche un agent sous forme de bouton cliquable qui le sélectionne."""
    pres = PRESENTATION.get(cle, {})
    libelle = LIBELLES.get(cle, cle)
    actif = st.session_state.agent_selectionne == cle
    if st.button(
        f"{pres.get('icone', '🤖')}  {libelle}",
        key=f"org_{cle}",
        use_container_width=True,
        help=pres.get("accroche", ""),
        type="primary" if actif else "secondary",
    ):
        st.session_state.agent_selectionne = cle
        st.rerun()


org = organigramme()

# Niveau 1 — CEO (centré)
col_g, col_c, col_d = st.columns([1, 1.4, 1])
with col_c:
    bouton_agent(org["ceo"])

st.markdown(
    '<div style="text-align:center;color:#5b6075;font-size:.85rem;'
    'margin:2px 0 10px;">▼ délègue à ses responsables ▼</div>',
    unsafe_allow_html=True,
)

# Niveaux 2 & 3 — chaque responsable et sa sous-équipe, par colonnes de 3
equipes = org["equipes"]
for debut in range(0, len(equipes), 3):
    colonnes = st.columns(3)
    for colonne, equipe in zip(colonnes, equipes[debut : debut + 3]):
        with colonne, st.container(border=True):
            bouton_agent(equipe["responsable"])
            st.markdown(
                '<div style="color:#5b6075;font-size:.72rem;'
                'margin:2px 0 4px 4px;">Sous-équipe :</div>',
                unsafe_allow_html=True,
            )
            for specialiste in equipe["specialistes"]:
                bouton_agent(specialiste)

# ---------------------------------------------------------------------------
# Comment ça marche
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">⚡ Comment ça marche</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="steps">
      <div class="step"><div class="n">ÉTAPE 1</div><div class="t">Décrivez votre besoin</div></div>
      <div class="step"><div class="n">ÉTAPE 2</div><div class="t">L'agent adapté est choisi</div></div>
      <div class="step"><div class="n">ÉTAPE 3</div><div class="t">Récupérez votre livrable</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Zone de travail
# ---------------------------------------------------------------------------
st.markdown('<div class="section-title">📝 Lancer une demande</div>', unsafe_allow_html=True)

with st.container(border=True):
    agent_clique = st.session_state.agent_selectionne
    cle_agent = None

    if agent_clique:
        # Un agent a été choisi en cliquant dans l'organigramme.
        pres = PRESENTATION.get(agent_clique, {})
        st.success(
            f"Agent sélectionné : {pres.get('icone', '🤖')} "
            f"**{LIBELLES.get(agent_clique, agent_clique)}** — il traitera votre demande."
        )
        if st.button("✖ Désélectionner (revenir au mode automatique)"):
            st.session_state.agent_selectionne = None
            st.rerun()
        mode = "Un agent"
        cle_agent = agent_clique
    else:
        mode = st.radio(
            "Mode de traitement",
            ["Automatique 🪄", "Un agent", "Toute l'équipe"],
            horizontal=True,
            help="« Automatique » choisit pour vous le responsable le plus adapté. "
            "Astuce : cliquez sur un agent dans l'organigramme ci-dessus.",
        )
        if mode == "Un agent":
            libelle = st.selectbox("Choisissez l'agent", list(agents.values()))
            cle_agent = next(c for c, lib in agents.items() if lib == libelle)

    sujet = st.text_area(
        "Votre demande",
        placeholder="Ex. : Rédige un mémoire technique pour un appel d'offres "
        "de formation Manager en TPE…",
        height=110,
    )
    col1, col2 = st.columns(2)
    with col1:
        contexte = st.text_input("Contexte (optionnel)", value="")
    with col2:
        objectif = st.text_input("Objectif (optionnel)", value="")

    lancer = st.button("🚀 Lancer", type="primary", use_container_width=True)

if lancer:
    if not sujet.strip():
        st.warning("Merci de saisir une demande.")
    else:
        ctx = contexte.strip() or "Aucun contexte particulier."
        obj = objectif.strip() or "Produire un livrable professionnel et exploitable."
        with st.spinner("Vos agents travaillent…"):
            try:
                if mode == "Toute l'équipe":
                    resultat = plateforme.executer_equipe(sujet, ctx, obj)
                elif mode == "Automatique 🪄":
                    choisi, resultat = plateforme.executer_auto(sujet, ctx, obj)
                    st.info(f"🤖 Agent choisi : **{agents.get(choisi, choisi)}**")
                else:
                    resultat = plateforme.executer_agent(cle_agent, sujet, ctx, obj)
                st.markdown("### ✅ Résultat")
                st.markdown(resultat)
                st.download_button(
                    "💾 Télécharger le résultat (Markdown)",
                    data=resultat,
                    file_name="agentia_resultat.md",
                    mime="text/markdown",
                )
            except Exception as exc:  # noqa: BLE001
                st.error(
                    f"Erreur : {exc}\n\n"
                    "Vérifiez que votre clé API est bien renseignée dans le "
                    "fichier .env (ANTHROPIC_API_KEY)."
                )

# ---------------------------------------------------------------------------
# Barre latérale
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🤖 Agentia")
    st.caption("Plateforme d'agents IA — LangChain + LangGraph")
    st.divider()
    st.markdown("**Votre équipe**")

    def _ligne(cle: str, decalage: bool = False) -> str:
        marge = "&nbsp;&nbsp;&nbsp;&nbsp;↳ " if decalage else ""
        icone = PRESENTATION.get(cle, {}).get("icone", "🤖")
        return f"{marge}{icone} {LIBELLES.get(cle, cle)}"

    st.markdown(_ligne(org["ceo"]), unsafe_allow_html=True)
    for equipe in org["equipes"]:
        st.markdown(_ligne(equipe["responsable"]), unsafe_allow_html=True)
        for specialiste in equipe["specialistes"]:
            st.markdown(_ligne(specialiste, decalage=True), unsafe_allow_html=True)
    st.divider()
    st.caption(
        "Configurez votre clé API dans le fichier `.env` "
        "(`ANTHROPIC_API_KEY`). Voir `.env.example`."
    )
