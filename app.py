"""Interface web Agentia PNG — équipe d'agents IA par services.

Deux vues :
  • « Équipe »  : les 7 services et leurs agents (cartes cliquables).
  • « Fiche agent » (au clic) : conversation + historique, missions, et
    tâches récurrentes (avec ajout).

Lancement :
    streamlit run app.py
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

# Permet l'import du paquet ``agentia`` situé dans src/
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import streamlit.components.v1 as components

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Sur Streamlit Community Cloud, les clés sont saisies dans « Secrets ».
# On les recopie dans les variables d'environnement pour le moteur.
try:
    for _cle in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AGENTIA_MODEL"):
        if _cle in st.secrets and not os.getenv(_cle):
            os.environ[_cle] = str(st.secrets[_cle])
except Exception:  # noqa: BLE001 — aucun secret défini (ex. en local) : on ignore.
    pass

from agentia.config_loader import (
    COULEUR_AGENT,
    LIBELLES,
    MISSIONS,
    NOMS,
    PRESENTATION,
    TACHES_REC_DEFAUT,
    organigramme,
)
from agentia.engine import AgentiaPlatform

AVATAR_DIR = Path(__file__).parent / "assets" / "avatars"

st.set_page_config(page_title="Agentia — Vos agents IA", page_icon="🤖", layout="wide")

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      #MainMenu, footer {visibility: hidden;}
      .block-container {padding-top: 1.6rem; max-width: 1180px;}

      .hero {text-align:center; padding:6px 0 2px;}
      .hero .eyebrow {
        display:inline-block; letter-spacing:.18em; font-size:.7rem;
        text-transform:uppercase; color:#FF5A4C; font-weight:700;
        border:1px solid rgba(255,90,76,.35); border-radius:999px;
        padding:5px 13px; margin-bottom:12px; background:rgba(255,90,76,.07);
      }
      .hero h1 {
        font-size:2.7rem; font-weight:800; margin:0; line-height:1.05;
        background:linear-gradient(90deg,#1F2433 0%, #FF5A4C 100%);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      }
      .hero p.sub {color:#5b6275; font-size:1.05rem; max-width:680px; margin:12px auto 4px;}

      .service-header {
        color:#fff; font-weight:800; letter-spacing:.05em; font-size:1.05rem;
        text-align:center; padding:11px 16px; border-radius:12px; margin:26px 0 16px;
        box-shadow:0 6px 18px rgba(0,0,0,.35);
      }

      /* Carte d'agent (vue équipe) — teintée à la couleur de son service */
      .tcard {
        border-radius:16px; padding:16px 12px 10px;
        text-align:center; transition:all .18s ease; min-height:176px;
      }
      .tcard:hover {transform:translateY(-4px); box-shadow:0 14px 30px rgba(31,36,51,.18);}
      .tname {font-weight:700; color:#1F2433; font-size:1rem; margin-top:8px;}
      .trole {color:#6b7280; font-size:.8rem; line-height:1.35; margin-top:3px;}

      /* En-tête de fiche agent */
      .ahead {
        display:flex; align-items:center; gap:18px;
        background:#fff; border:1px solid #e6e9f0; border-radius:18px;
        padding:18px 22px; margin-bottom:8px; box-shadow:0 4px 16px rgba(31,36,51,.06);
      }
      .ahead .nm {font-size:1.7rem; font-weight:800; color:#1F2433; line-height:1.1;}
      .ahead .rl {color:#5b6275; font-size:1rem; margin-top:2px;}
      .badge {display:inline-block; color:#fff; font-size:.72rem; font-weight:700;
        padding:3px 10px; border-radius:999px; margin-top:8px;}

      .avatar, .avatar-anim {
        border-radius:50%; overflow:hidden; border:2px solid #FF5A4C;
        box-shadow:0 6px 16px rgba(0,0,0,.35); display:flex;
        align-items:center; justify-content:center; line-height:1;
      }
      .avatar-anim {display:block; animation:flotte 3.2s ease-in-out infinite;
        transition:transform .2s ease;}
      .avatar-anim:hover {transform:scale(1.12) rotate(-3deg);}
      @keyframes flotte {
        0%{transform:translateY(0)}50%{transform:translateY(-5px)}100%{transform:translateY(0)}
      }
      @media (prefers-reduced-motion: reduce){.avatar-anim{animation:none;}}

      .mission-item {
        background:#fff; border:1px solid #e6e9f0; border-left:3px solid #FF5A4C;
        border-radius:10px; padding:11px 14px; margin-bottom:8px; color:#1F2433;
        box-shadow:0 2px 8px rgba(31,36,51,.05);
      }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def charger_plateforme() -> AgentiaPlatform:
    return AgentiaPlatform(verbose=False)


plateforme = charger_plateforme()

# État de session
st.session_state.setdefault("agent_actif", None)
st.session_state.setdefault("historique", {})       # cle -> [{role, content}]
st.session_state.setdefault("taches_rec", {})       # cle -> [str]

org = organigramme()
COULEUR_SERVICE = {m: s["couleur"] for s in org for m in s["membres"]}
SERVICE_DE = {m: s for s in org for m in s["membres"]}


@st.cache_data(show_spinner=False)
def _avatar_b64(chemin: str, _signature: float) -> str:
    """Encode un visage en base64 (clé de cache = date de modif du fichier)."""
    return base64.b64encode(Path(chemin).read_bytes()).decode("ascii")


def avatar_html(cle: str, taille: int = 64) -> str:
    """Renvoie le HTML d'un avatar animé (image Pixar, ou pastille de secours)."""
    couleur = COULEUR_AGENT.get(cle, "#FF5A4C")
    fichier = AVATAR_DIR / f"{cle}.png"
    delai = (sum(map(ord, cle)) % 20) / 10
    if fichier.is_file():
        b64 = _avatar_b64(str(fichier), fichier.stat().st_mtime)
        return (
            f'<div class="avatar-anim" style="width:{taille}px;height:{taille}px;'
            f'border-color:{couleur};animation-delay:{delai}s;margin:0 auto;">'
            f'<img src="data:image/png;base64,{b64}" '
            f'style="width:100%;height:100%;border-radius:50%;"></div>'
        )
    icone = PRESENTATION.get(cle, {}).get("icone", "🤖")
    return (
        f'<div class="avatar" style="width:{taille}px;height:{taille}px;margin:0 auto;'
        f'font-size:{int(taille * 0.45)}px;border-color:{couleur};'
        f'background:radial-gradient(circle at 30% 25%,{couleur},#11131b);">{icone}</div>'
    )


def ouvrir(cle: str) -> None:
    st.session_state.agent_actif = cle
    st.rerun()


def lecteur_vocal(texte: str) -> None:
    """Bouton de lecture vocale (voix du navigateur, gratuite)."""
    contenu = json.dumps(texte[:6000])
    components.html(
        f"""
        <div style="font-family:sans-serif;">
          <button id="play" style="background:#FF5A4C;color:#fff;border:none;
            border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;">🔊 Écouter</button>
          <button id="stop" style="background:#272a38;color:#fff;border:none;
            border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;margin-left:6px;">⏹️ Stop</button>
          <script>
            document.getElementById('play').onclick = function() {{
              window.speechSynthesis.cancel();
              const u = new SpeechSynthesisUtterance({contenu});
              u.lang='fr-FR';
              const v=window.speechSynthesis.getVoices().find(x=>x.lang&&x.lang.toLowerCase().startsWith('fr'));
              if(v)u.voice=v; window.speechSynthesis.speak(u);
            }};
            document.getElementById('stop').onclick=function(){{window.speechSynthesis.cancel();}};
          </script>
        </div>""",
        height=52,
    )


# ===========================================================================
# BARRE LATÉRALE — navigation
# ===========================================================================
with st.sidebar:
    st.markdown("### 🤖 Agentia")
    if st.button("🏠 Accueil — toute l'équipe", use_container_width=True):
        st.session_state.agent_actif = None
        st.rerun()
    st.divider()
    for service in org:
        st.markdown(f"**{service['icone']} {service['nom']}**")
        for cle in service["membres"]:
            ic = PRESENTATION.get(cle, {}).get("icone", "🤖")
            if st.button(f"{ic} {NOMS[cle]}", key=f"nav_{cle}", use_container_width=True):
                ouvrir(cle)
    st.divider()
    st.caption("Clé API à configurer dans les Secrets (`ANTHROPIC_API_KEY`).")


# ===========================================================================
# VUE 1 — ÉQUIPE
# ===========================================================================
if st.session_state.agent_actif is None:
    st.markdown(
        """
        <div class="hero">
          <span class="eyebrow">Paris Nord Groupe · Plateforme d'agents IA</span>
          <h1>Agentia</h1>
          <p class="sub">Votre équipe augmentée par l'IA — 7 services, 18 agents.
          Cliquez sur un agent pour ouvrir sa fiche : lui parler, voir ses missions
          et gérer ses tâches récurrentes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for service in org:
        st.markdown(
            f'<div class="service-header" style="background:{service["couleur"]};">'
            f'{service["icone"]} {service["nom"].upper()}</div>',
            unsafe_allow_html=True,
        )
        membres = service["membres"]
        for colonne, cle in zip(st.columns(max(len(membres), 1)), membres):
            with colonne:
                coul = service["couleur"]
                st.markdown(
                    f'<div class="tcard" style="background:linear-gradient(180deg,'
                    f'{coul}2b 0%, #ffffff 62%);'
                    f'border:1px solid {coul}55;border-top:4px solid {coul};">'
                    f'{avatar_html(cle, 64)}'
                    f'<div class="tname">{NOMS[cle]}</div>'
                    f'<div class="trole">{LIBELLES[cle]}</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Ouvrir la fiche ›", key=f"open_{cle}", use_container_width=True):
                    ouvrir(cle)


# ===========================================================================
# VUE 2 — FICHE AGENT
# ===========================================================================
else:
    cle = st.session_state.agent_actif
    nom = NOMS.get(cle, cle)
    role = LIBELLES.get(cle, cle)
    service = SERVICE_DE.get(cle, {"nom": "", "couleur": "#FF5A4C", "icone": "🤖"})
    couleur = service["couleur"]

    if st.button("‹ Retour à l'équipe"):
        st.session_state.agent_actif = None
        st.rerun()

    # En-tête
    st.markdown(
        f'<div class="ahead" style="background:linear-gradient(180deg,{couleur}26 0%,'
        f' #ffffff 70%);border-color:{couleur}55;">{avatar_html(cle, 88)}'
        f'<div><div class="nm">{nom}</div><div class="rl">{role}</div>'
        f'<span class="badge" style="background:{couleur};">'
        f'{service["icone"]} {service["nom"]}</span></div></div>',
        unsafe_allow_html=True,
    )

    onglet_chat, onglet_miss, onglet_taches = st.tabs(
        ["💬 Conversation", "🎯 Missions", "🔁 Tâches récurrentes"]
    )

    # ---- Onglet Conversation + historique ----
    with onglet_chat:
        historique = st.session_state.historique.setdefault(cle, [])
        if not historique:
            st.caption(f"Posez votre première question à {nom}. L'historique apparaîtra ici.")
        for msg in historique:
            avatar = "🧑" if msg["role"] == "user" else PRESENTATION.get(cle, {}).get("icone", "🤖")
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])
        if historique and historique[-1]["role"] == "assistant":
            lecteur_vocal(historique[-1]["content"])

        with st.form(f"chat_{cle}", clear_on_submit=True):
            question = st.text_area(
                f"Écrivez à {nom}",
                placeholder="Ex. : Rédige un courrier de relance pour une facture impayée…",
                height=90,
            )
            envoye = st.form_submit_button("Envoyer ✉️", type="primary", use_container_width=True)
        col_a, col_b = st.columns([1, 4])
        with col_a:
            if st.button("🗑️ Effacer l'historique", use_container_width=True):
                st.session_state.historique[cle] = []
                st.rerun()

        if envoye and question.strip():
            historique.append({"role": "user", "content": question.strip()})
            with st.spinner(f"{nom} réfléchit…"):
                try:
                    reponse = plateforme.executer_agent(cle, question.strip())
                except Exception as exc:  # noqa: BLE001
                    reponse = (
                        f"⚠️ Erreur : {exc}\n\n"
                        "Vérifiez que la clé API est bien configurée (Secrets / `.env`)."
                    )
            historique.append({"role": "assistant", "content": reponse})
            st.rerun()

    # ---- Onglet Missions ----
    with onglet_miss:
        st.markdown(f"#### 🎯 Les missions de {nom}")
        for mission in MISSIONS.get(cle, []):
            st.markdown(f'<div class="mission-item">✓ {mission}</div>', unsafe_allow_html=True)
        st.caption(f"💬 Astuce : demandez n'importe laquelle de ces missions à {nom} dans l'onglet Conversation.")

    # ---- Onglet Tâches récurrentes ----
    with onglet_taches:
        taches = st.session_state.taches_rec.setdefault(
            cle, list(TACHES_REC_DEFAUT.get(cle, []))
        )
        st.markdown(f"#### 🔁 Tâches récurrentes de {nom}")
        if not taches:
            st.info("Aucune tâche récurrente pour l'instant. Ajoutez-en une ci-dessous.")
        for i, tache in enumerate(taches):
            c1, c2 = st.columns([9, 1])
            c1.markdown(f'<div class="mission-item">🔁 {tache}</div>', unsafe_allow_html=True)
            if c2.button("🗑️", key=f"deltask_{cle}_{i}"):
                taches.pop(i)
                st.rerun()

        st.markdown("**➕ Ajouter une tâche récurrente**")
        with st.form(f"addtask_{cle}", clear_on_submit=True):
            desc = st.text_input("Que doit-il faire ?", placeholder="Ex. : préparer le reporting")
            freq = st.selectbox(
                "Fréquence", ["Chaque jour", "Chaque semaine", "Chaque mois", "Chaque trimestre"]
            )
            ajoute = st.form_submit_button("➕ Ajouter la tâche", type="primary")
        if ajoute and desc.strip():
            taches.append(f"{freq} : {desc.strip()}")
            st.rerun()

        st.caption(
            "ℹ️ Ces tâches forment la « feuille de route » de l'agent (gardées pendant "
            "votre session). L'exécution automatique programmée viendra dans une "
            "prochaine étape."
        )
