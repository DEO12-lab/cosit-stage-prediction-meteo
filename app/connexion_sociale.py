"""
app/connexion_sociale.py
--------------------------
Connexion avec un compte Google ou GitHub (utilisateur simple, jamais
administrateur : les droits admin passent uniquement par auth.py).

- Google : utilise la connexion OpenID Connect intégrée à Streamlit
  (st.login / st.user, Streamlit >= 1.42 + package Authlib).
- GitHub : flux OAuth « authorization code » codé ici (GitHub n'est pas
  un fournisseur OpenID Connect standard, donc st.login ne le gère pas).

Réglages à mettre dans .streamlit/secrets.toml : voir secrets.toml.exemple.
"""

import hashlib
import hmac
import json
import secrets
import time
import urllib.parse
import urllib.request

import streamlit as st

from notifications import lire_secret

_DUREE_ETAT_SECONDES = 600


class ErreurConnexionSociale(Exception):
    """Erreur à afficher telle quelle à l'utilisateur."""


# ------------------------------- Google ------------------------------------

def google_configure() -> bool:
    if not (hasattr(st, "login") and hasattr(st, "user")):
        return False
    try:
        return bool(st.secrets["auth"]["google"]["client_id"])
    except Exception:
        return False


def google_lancer() -> None:
    try:
        st.login("google")
    except Exception:
        st.error("La connexion Google est mal configurée (voir secrets.toml.exemple).")


def google_utilisateur() -> tuple[str, str] | None:
    """(nom, e-mail) si l'utilisateur vient de se connecter via Google."""
    utilisateur = getattr(st, "user", None)
    if utilisateur is None or not getattr(utilisateur, "is_logged_in", False):
        return None
    email = getattr(utilisateur, "email", None)
    if not email or getattr(utilisateur, "email_verified", True) is False:
        return None
    return (getattr(utilisateur, "name", None) or email), email


# ------------------------------- GitHub ------------------------------------

def _github_reglages() -> tuple[str | None, str | None, str | None]:
    return (
        lire_secret("github", "client_id"),
        lire_secret("github", "client_secret"),
        lire_secret("github", "redirect_uri"),
    )


def github_configure() -> bool:
    return all(_github_reglages())


def _signer(message: str) -> str:
    _, secret, _ = _github_reglages()
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def github_url_autorisation() -> str:
    """URL vers laquelle envoyer l'utilisateur. Le paramètre `state` est signé
    (HMAC) et daté : Streamlit perd la session pendant la redirection, on ne
    peut donc pas le mémoriser côté serveur, mais on peut le vérifier au retour."""
    client_id, _, redirect_uri = _github_reglages()
    base = f"{secrets.token_urlsafe(12)}.{int(time.time())}"
    etat = f"gh.{base}.{_signer(base)}"
    return "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": etat,
        }
    )


def _etat_valide(etat: str) -> bool:
    parties = etat.split(".")
    if len(parties) != 4 or parties[0] != "gh":
        return False
    base = f"{parties[1]}.{parties[2]}"
    if not hmac.compare_digest(parties[3], _signer(base)):
        return False
    try:
        return 0 <= time.time() - int(parties[2]) <= _DUREE_ETAT_SECONDES
    except ValueError:
        return False


def _requete_json(url: str, donnees: dict | None = None, entetes: dict | None = None):
    corps = urllib.parse.urlencode(donnees).encode() if donnees else None
    requete = urllib.request.Request(
        url,
        data=corps,
        headers={"Accept": "application/json", "User-Agent": "MeteoHub", **(entetes or {})},
    )
    with urllib.request.urlopen(requete, timeout=15) as reponse:
        return json.loads(reponse.read().decode())


def github_retour() -> tuple[str, str] | None:
    """À appeler en haut de la page Connexion : si l'URL contient le retour de
    GitHub (?code=...&state=gh....), échange le code et retourne (nom, e-mail).
    Retourne None s'il n'y a rien à traiter ; lève ErreurConnexionSociale en
    cas d'échec."""
    code = st.query_params.get("code")
    etat = st.query_params.get("state")
    if not code or not etat or not etat.startswith("gh."):
        return None

    st.query_params.clear()  # un code GitHub ne sert qu'une fois
    if not github_configure():
        raise ErreurConnexionSociale("La connexion GitHub n'est pas configurée.")
    if not _etat_valide(etat):
        raise ErreurConnexionSociale("Connexion GitHub expirée ou invalide. Réessaie.")

    client_id, client_secret, redirect_uri = _github_reglages()
    try:
        jeton = _requete_json(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
            },
        ).get("access_token")
        if not jeton:
            raise ErreurConnexionSociale("GitHub a refusé la connexion. Réessaie.")

        entetes = {"Authorization": f"Bearer {jeton}"}
        profil = _requete_json("https://api.github.com/user", entetes=entetes)
        courriels = _requete_json("https://api.github.com/user/emails", entetes=entetes)
    except ErreurConnexionSociale:
        raise
    except Exception:
        raise ErreurConnexionSociale("Impossible de joindre GitHub. Réessaie dans un instant.")

    # Seul un e-mail principal ET vérifié est accepté.
    email = next(
        (c["email"] for c in courriels if c.get("primary") and c.get("verified")), None
    )
    if not email:
        raise ErreurConnexionSociale("Aucune adresse e-mail vérifiée sur ce compte GitHub.")
    return (profil.get("name") or profil.get("login") or email), email
