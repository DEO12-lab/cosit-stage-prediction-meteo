"""
app/auth.py
------------
Contrôle d'accès simple : détermine si la personne qui vient de se
connecter est administrateur (liste des utilisateurs) ou un utilisateur
normal (ne voit que ses propres prédictions dans l'historique).

Fonctionnement des droits administrateur :
- une adresse e-mail doit être AUTORISÉE à devenir administrateur, soit
  parce qu'elle figure dans EMAILS_ADMINISTRATEURS ci-dessous, soit parce
  qu'un administrateur l'a autorisée (demande par e-mail ou bouton rouge de
  la page Utilisateurs → table « administrateurs » de la base) ;
- ET le mot de passe administrateur doit être saisi à la connexion.
  Autoriser quelqu'un ne lui donne donc pas le mot de passe : l'administrateur
  qui l'autorise doit le lui communiquer.

⚠️ LIMITE IMPORTANTE À CONNAÎTRE :
Ceci N'EST PAS un vrai système d'authentification sécurisé — le mot de
passe est stocké en clair dans le code, sans hachage, et n'importe qui
ayant accès au code source (ou au dépôt GitHub) peut le lire. C'est
suffisant pour répondre à la demande de ton tuteur dans le cadre d'un
projet de stage (séparer "voit tout" / "voit seulement ses données"),
mais ce n'est pas adapté à une vraie mise en production avec des
données sensibles. Pour ça, il faudrait un vrai système d'authentification
(mots de passe hachés en base, sessions expirables, HTTPS...).
"""

import hmac
import re
from html import escape

import streamlit as st

from database import (
    ajouter_administrateur,
    annuler_demande,
    approuver_demande,
    ajouter_utilisateur,
    creer_demande_admin,
    lire_demande,
    recuperer_emails_administrateurs,
)
from notifications import email_configure, envoyer_email, lire_secret

# Adresses e-mail autorisées à devenir administrateur (à adapter).
EMAILS_ADMINISTRATEURS = {
    "adogoundeogracias@gmail.com",
}

# Mot de passe partagé exigé en plus de l'e-mail pour obtenir les droits
# administrateur. CHANGE CETTE VALEUR avant de partager le projet.
MOT_DE_PASSE_ADMIN = "2027cositAdmin@.gmail"

# Chemin (dans l'URL de l'application) de la page Connexion : c'est elle qui
# reçoit le lien « authorize » envoyé par e-mail. Adapte-le si l'URL de ta
# page de connexion est différente (ex. "connexion").
CHEMIN_PAGE_CONNEXION = "connexion"

_MOTIF_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email_valide(email: str) -> bool:
    return bool(_MOTIF_EMAIL.match((email or "").strip()))


def emails_administrateurs() -> set[str]:
    """Tous les e-mails autorisés à devenir administrateur (liste fixe + base)."""
    fixes = {e.strip().lower() for e in EMAILS_ADMINISTRATEURS}
    return fixes | recuperer_emails_administrateurs()


def est_email_administrateur(email: str) -> bool:
    return (email or "").strip().lower() in emails_administrateurs()


def est_administrateur(email: str, mot_de_passe: str) -> bool:
    """Retourne True seulement si l'e-mail est autorisé ET que le mot de
    passe administrateur correspond (les deux sont nécessaires, pour qu'il
    ne suffise pas de connaître/deviner un e-mail admin)."""
    if not email or not mot_de_passe:
        return False
    return est_email_administrateur(email) and hmac.compare_digest(
        mot_de_passe.encode(), MOT_DE_PASSE_ADMIN.encode()
    )


def ouvrir_session(nom: str, email: str, telephone: str = "", est_admin: bool = False):
    """Enregistre l'utilisateur (une seule fois par e-mail) et mémorise la
    session. Utilisé par la connexion classique et par Google / GitHub."""
    ajouter_utilisateur(nom, email, telephone)
    st.session_state["utilisateur_connecte"] = nom
    st.session_state["email_connecte"] = email
    st.session_state["est_admin"] = est_admin



# Demande pour devenir administrateur (e-mail Gmail « authorize »)


def _url_autorisation(jeton: str) -> str:
    base = (lire_secret("app", "url", "http://localhost:8501") or "").rstrip("/")
    return f"{base}/{CHEMIN_PAGE_CONNEXION}?autoriser={jeton}"


def demander_droits_administrateur(
    nom: str, email: str, email_admin: str
) -> tuple[bool, str]:
    """Envoie à l'administrateur indiqué un e-mail contenant le message
    « authorize » (lien de confirmation). Retourne (succès, message).

    Le message renvoyé est volontairement identique que l'adresse soit celle
    d'un administrateur ou non : on ne révèle pas quelles adresses sont admin."""
    if not email_valide(email_admin):
        return False, "L'adresse e-mail de l'administrateur n'est pas valide."
    if email_admin.strip().lower() == email.strip().lower():
        return False, "Indique l'e-mail d'un AUTRE administrateur que toi."
    if est_email_administrateur(email):
        return True, "Ton adresse est déjà autorisée à devenir administrateur."
    if not email_configure():
        return False, (
            "La demande n'a pas pu être envoyée : l'envoi d'e-mails n'est pas "
            "encore configuré sur ce serveur."
        )

    neutre = (
        "Demande envoyée : si cette adresse est bien celle d'un administrateur, "
        "il recevra ton message par e-mail. Vérifie qu'elle est correcte."
    )
    if not est_email_administrateur(email_admin):
        return True, neutre  # aucun envoi, mais on ne le dit pas

    jeton = creer_demande_admin(nom, email, email_admin)
    if jeton is None:
        return True, neutre  # même demande déjà en attente

    lien = _url_autorisation(jeton)
    texte = (
        f"Bonjour,\n\n{nom} ({email}) demande à devenir administrateur de MétéoHub "
        f"et t'a indiqué comme administrateur.\n\n"
        f"authorize\n{lien}\n\n"
        f"Ouvre ce lien puis confirme pour l'autoriser. Il est valable 48 h. "
        f"Si tu ne connais pas cette personne, ignore simplement ce message."
    )
    html = (
        f"<p>Bonjour,</p>"
        f"<p><strong>{escape(nom)}</strong> ({escape(email)}) demande à devenir "
        f"administrateur de MétéoHub et t'a indiqué comme administrateur.</p>"
        f'<p><a href="{escape(lien, quote=True)}" style="display:inline-block;'
        f"padding:12px 28px;background:#d32f2f;color:#ffffff;border-radius:8px;"
        f'text-decoration:none;font-weight:bold;">authorize</a></p>'
        f"<p style='color:#666;font-size:13px'>Le lien est valable 48 h. "
        f"Si tu ne connais pas cette personne, ignore ce message.</p>"
    )
    ok, erreur = envoyer_email(
        email_admin.strip(), "Demande d'autorisation administrateur — MétéoHub", texte, html
    )
    if not ok:
        annuler_demande(jeton)  # permet de réessayer tout de suite
        return False, erreur
    return True, neutre


def _notifier_autorisation(nom: str, email: str) -> None:
    """Prévient la personne autorisée (sans conséquence si l'envoi échoue)."""
    if not email_configure():
        return
    envoyer_email(
        email,
        "Tu as été autorisé(e) à devenir administrateur — MétéoHub",
        f"Bonjour {nom},\n\nUn administrateur t'a autorisé(e) à devenir administrateur "
        f"de MétéoHub. Pour te connecter en tant qu'administrateur, utilise ton e-mail "
        f"et le mot de passe administrateur (demande-le à la personne qui t'a autorisé(e)).",
    )


def autoriser_administrateur(email: str, nom: str = "", par: str | None = None) -> None:
    """Autorise directement cet e-mail (bouton rouge de la page Utilisateurs)."""
    ajouter_administrateur(email, par)
    _notifier_autorisation(nom or email, email)


def traiter_lien_autorisation() -> None:
    """À appeler en haut de la page Connexion. Si l'URL contient ?autoriser=...
    (lien du message « authorize »), affiche la demande et un bouton de
    confirmation. L'autorisation n'est donnée qu'au CLIC : ouvrir le lien (ou
    un antivirus/scanner de liens qui le visite) ne suffit pas."""
    resultat = st.session_state.pop("resultat_autorisation", None)
    if resultat:
        st.success(resultat)
        return

    jeton = st.query_params.get("autoriser")
    if not jeton:
        return

    demande = lire_demande(jeton)
    if demande is None:
        st.error("Ce lien d'autorisation est invalide, expiré ou déjà utilisé.")
        return

    with st.container(key="boite_autorisation"):
        st.markdown(
            f"<div class='carte-utilisateur-nom'>Demande d'autorisation</div>"
            f"<div class='carte-utilisateur-ligne'><strong>{escape(demande['nom'])}</strong> "
            f"({escape(demande['email_demandeur'])}) demande à devenir administrateur.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Autoriser", key="autoriser_confirmation", type="primary"):
            approuvee = approuver_demande(jeton)
            if approuvee is None:
                st.session_state["resultat_autorisation"] = (
                    "Cette demande a déjà été traitée ou a expiré."
                )
            else:
                _notifier_autorisation(approuvee["nom"], approuvee["email_demandeur"])
                st.session_state["resultat_autorisation"] = (
                    f"✅ {approuvee['nom']} est maintenant autorisé(e) à devenir "
                    f"administrateur. Communique-lui le mot de passe administrateur."
                )
            st.query_params.clear()
            st.rerun()
