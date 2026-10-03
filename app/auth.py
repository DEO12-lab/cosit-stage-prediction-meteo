"""
app/auth.py
------------
Authentification par e-mail + mot de passe : inscription, connexion,
gestion de la session (st.session_state).

⚠️ LIMITE À CONNAÎTRE : le mot de passe est haché avec PBKDF2-SHA256
(bibliothèque standard de Python, sans dépendance à installer), salé
individuellement par utilisateur — c'est correct pour un projet de
stage. Il manque toutefois ce qu'un vrai système de production aurait
en plus : limitation du nombre d'essais, expiration de session côté
serveur, HTTPS obligatoire, etc.
"""

import hashlib
import hmac
import re
import secrets

import streamlit as st

from database import email_deja_utilise, inscrire_utilisateur, obtenir_utilisateur_par_email

_MOTIF_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ITERATIONS_PBKDF2 = 200_000


def email_valide(email: str) -> bool:
    return bool(_MOTIF_EMAIL.match((email or "").strip()))


def _hacher_mot_de_passe(mot_de_passe: str, sel: str | None = None) -> tuple[str, str]:
    """Retourne (sel, empreinte). Génère un nouveau sel aléatoire si aucun
    n'est fourni (cas de l'inscription) ; réutilise celui du compte sinon
    (cas de la vérification à la connexion)."""
    sel = sel or secrets.token_hex(16)
    empreinte = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), sel.encode(), _ITERATIONS_PBKDF2
    ).hex()
    return sel, empreinte


def inscrire(email: str, nom: str, prenom: str, telephone: str, mot_de_passe: str):
    """Crée le compte. Retourne (succès: bool, message: str)."""
    if not (email and nom and prenom and mot_de_passe):
        return False, "Tous les champs marqués d'un * sont obligatoires."
    if not email_valide(email):
        return False, "Adresse e-mail invalide."
    if len(mot_de_passe) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."
    if email_deja_utilise(email):
        return False, "Un compte existe déjà avec cet e-mail. Connecte-toi plutôt."

    sel, empreinte = _hacher_mot_de_passe(mot_de_passe)
    inscrire_utilisateur(email, nom, prenom, telephone, sel, empreinte)
    return True, "Compte créé avec succès. Tu es maintenant connecté(e)."


def connecter(email: str, mot_de_passe: str):
    """Vérifie l'e-mail et le mot de passe. Retourne (succès: bool, message: str,
    utilisateur: dict | None)."""
    if not (email and mot_de_passe):
        return False, "Renseigne ton e-mail et ton mot de passe.", None

    utilisateur = obtenir_utilisateur_par_email(email)
    if not utilisateur or not utilisateur.get("mot_de_passe_hash"):
        return False, "E-mail ou mot de passe incorrect.", None

    _, empreinte_saisie = _hacher_mot_de_passe(mot_de_passe, utilisateur["sel"])
    if not hmac.compare_digest(empreinte_saisie, utilisateur["mot_de_passe_hash"]):
        return False, "E-mail ou mot de passe incorrect.", None

    return True, f"Bon retour, {utilisateur['prenom']} !", utilisateur


def ouvrir_session(utilisateur: dict) -> None:
    """Mémorise l'utilisateur connecté pour le reste de la session."""
    st.session_state["utilisateur"] = {
        "nom": utilisateur["nom"],
        "prenom": utilisateur["prenom"],
        "email": utilisateur["email"],
        "telephone": utilisateur.get("telephone", ""),
        "date_inscription": utilisateur.get("date_inscription", ""),
    }


def utilisateur_connecte() -> dict | None:
    return st.session_state.get("utilisateur")


def deconnecter() -> None:
    st.session_state.pop("utilisateur", None)
