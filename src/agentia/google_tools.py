"""Outils Google (Drive + Gmail) pour les agents Agentia.

Ce module donne aux agents un accès RÉEL au Drive et à Gmail de l'utilisateur.

Authentification : OAuth « utilisateur » via un jeton de rafraîchissement
(refresh token). Trois variables d'environnement / secrets sont attendues :

    GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET
    GOOGLE_REFRESH_TOKEN

Si elles sont absentes, ``google_actif()`` renvoie False et les agents
fonctionnent normalement (sans accès Google).

Sécurité : par défaut on reste en LECTURE pour le Drive, et on se limite à la
CRÉATION DE BROUILLONS pour Gmail (aucun envoi automatique).
"""

from __future__ import annotations

import base64
import os
import re
from email.mime.text import MIMEText

# Mots vides ignorés lors de la recherche (on ne garde que les mots utiles).
_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "mon", "ma", "mes",
    "dans", "sur", "et", "ou", "ce", "cette", "fichier", "fichiers", "document",
    "documents", "tableau", "tableaux", "piece", "pieces", "pièce", "pièces",
    "drive", "trouve", "trouver", "cherche", "chercher", "moi", "svp", "stp",
    "plait", "envoie", "envoyer", "mail", "email", "par", "les", "tout", "toutes",
}


def _mots_cles(requete: str) -> list[str]:
    """Extrait les mots utiles d'une demande (ignore les mots vides)."""
    mots = re.findall(r"[A-Za-z0-9À-ÿ_.-]{2,}", requete)
    cles = [m for m in mots if m.lower() not in _STOPWORDS]
    return cles or mots

# Lecture du Drive + rédaction de brouillons Gmail (pas d'envoi auto).
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

_CLES = ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN")


def google_actif() -> bool:
    """Renvoie True si les identifiants Google sont configurés."""
    return all(os.getenv(c) for c in _CLES)


def _credentials():
    from google.oauth2.credentials import Credentials

    return Credentials(
        token=None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )


def _service(api: str, version: str):
    from googleapiclient.discovery import build

    return build(api, version, credentials=_credentials(), cache_discovery=False)


def rechercher_drive(requete: str, maximum: int = 20) -> str:
    """Cherche des fichiers dans le Drive par MOT-CLÉ (pas la phrase entière).

    On extrait les mots utiles de la demande et on cherche les fichiers dont le
    nom contient ces mots. Ainsi « les pièces BPU » trouve tout ce qui contient
    « BPU ».
    """
    cles = _mots_cles(requete)
    conditions = " and ".join(
        f"name contains '{m.replace(chr(39), chr(92) + chr(39))}'" for m in cles
    )
    requete_drive = f"({conditions}) and trashed = false" if conditions else "trashed = false"
    try:
        service = _service("drive", "v3")
        reponse = (
            service.files()
            .list(
                q=requete_drive,
                pageSize=maximum,
                fields="files(id,name,mimeType,webViewLink,modifiedTime)",
                orderBy="modifiedTime desc",
            )
            .execute()
        )
    except Exception as exc:  # noqa: BLE001
        return f"Erreur lors de la recherche Drive : {exc}"

    fichiers = reponse.get("files", [])
    mots = ", ".join(cles) if cles else requete
    if not fichiers:
        return (
            f"Aucun fichier trouvé contenant « {mots} ». "
            "Essayez un autre mot-clé ou vérifiez l'orthographe du nom."
        )
    lignes = [
        f"- {f['name']} : {f.get('webViewLink', '(lien indisponible)')}"
        for f in fichiers
    ]
    return f"{len(fichiers)} fichier(s) contenant « {mots} » :\n" + "\n".join(lignes)


def creer_brouillon_email(destinataire: str, sujet: str, message: str) -> str:
    """Crée un BROUILLON Gmail (n'envoie rien) et renvoie une confirmation."""
    try:
        service = _service("gmail", "v1")
        mime = MIMEText(message)
        mime["to"] = destinataire
        mime["subject"] = sujet
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
        service.users().drafts().create(
            userId="me", body={"message": {"raw": raw}}
        ).execute()
    except Exception as exc:  # noqa: BLE001
        return f"Erreur lors de la création du brouillon : {exc}"
    return (
        f"✅ Brouillon préparé pour {destinataire} (sujet : « {sujet} »). "
        "Il vous attend dans vos brouillons Gmail — à vous de l'envoyer."
    )


def rechercher_emails(requete: str, maximum: int = 8) -> str:
    """Cherche des emails (objet + expéditeur) et renvoie un résumé lisible."""
    try:
        service = _service("gmail", "v1")
        liste = (
            service.users()
            .messages()
            .list(userId="me", q=requete, maxResults=maximum)
            .execute()
        )
        ids = [m["id"] for m in liste.get("messages", [])]
        resultats = []
        for mid in ids:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=mid,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
            entetes = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            resultats.append(
                f"- {entetes.get('Subject', '(sans objet)')} "
                f"— de {entetes.get('From', '?')} ({entetes.get('Date', '')})"
            )
    except Exception as exc:  # noqa: BLE001
        return f"Erreur lors de la recherche d'emails : {exc}"
    if not resultats:
        return f"Aucun email trouvé pour « {requete} »."
    return f"{len(resultats)} email(s) pour « {requete} » :\n" + "\n".join(resultats)
