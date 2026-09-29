"""
app/notifications.py
----------------------
Envoi d'e-mails via Gmail (SMTP) et lecture des réglages sensibles.

Les identifiants ne sont JAMAIS écrits dans le code : ils viennent de
.streamlit/secrets.toml (voir secrets.toml.exemple) ou de variables
d'environnement (EMAIL_ADRESSE, EMAIL_MOT_DE_PASSE_APPLICATION, ...).

Gmail n'accepte pas le mot de passe normal du compte pour SMTP : il faut
activer la validation en 2 étapes puis créer un « mot de passe
d'application » (compte Google > Sécurité > Mots de passe des applications).
"""

import os
import smtplib
import ssl
from email.message import EmailMessage

import streamlit as st


def lire_secret(section: str, cle: str, defaut: str | None = None) -> str | None:
    """Lit [section] cle dans st.secrets, sinon la variable d'environnement
    SECTION_CLE, sinon la valeur par défaut."""
    try:
        valeur = st.secrets[section][cle]
        if valeur:
            return str(valeur)
    except Exception:
        pass
    return os.environ.get(f"{section}_{cle}".upper(), defaut)


def email_configure() -> bool:
    return bool(
        lire_secret("email", "adresse")
        and lire_secret("email", "mot_de_passe_application")
    )


def envoyer_email(
    destinataire: str, sujet: str, texte: str, html: str | None = None
) -> tuple[bool, str]:
    """Envoie un e-mail. Retourne (succès, message d'erreur lisible)."""
    adresse = lire_secret("email", "adresse")
    mot_de_passe = lire_secret("email", "mot_de_passe_application")
    if not adresse or not mot_de_passe:
        return False, "L'envoi d'e-mails n'est pas encore configuré (voir secrets.toml.exemple)."

    try:
        message = EmailMessage()
        message["From"] = f"MétéoHub <{adresse}>"
        message["To"] = destinataire
        message["Subject"] = sujet
        message.set_content(texte)
        if html:
            message.add_alternative(html, subtype="html")

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=20
        ) as serveur:
            serveur.login(adresse, mot_de_passe.replace(" ", ""))
            serveur.send_message(message)
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, "Gmail a refusé les identifiants (vérifie le mot de passe d'application)."
    except Exception as erreur:
        return False, f"Échec de l'envoi de l'e-mail ({type(erreur).__name__})."
