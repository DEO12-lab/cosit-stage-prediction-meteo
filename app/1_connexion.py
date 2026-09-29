"""
app/1_connexion.py
----------------------
Formulaire de connexion / inscription : les informations saisies
(nom, e-mail, téléphone) sont enregistrées dans la base SQLite.
Le nom, l'e-mail et le statut (administrateur ou non) sont mémorisés
dans la session pour contrôler l'accès aux autres pages (Utilisateurs
réservée aux admins, Historique limité à ses propres prédictions).

Trois façons d'entrer :
- le formulaire classique (avec, en option, une demande pour devenir
  administrateur adressée par e-mail à un administrateur connu) ;
- « Continuer avec Google » ;
- « Continuer avec GitHub » (ces deux-là donnent un compte utilisateur simple).
"""

import sys
from html import escape
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from ui_helpers import afficher_barre_titre
from auth import (
    demander_droits_administrateur,
    est_administrateur,
    ouvrir_session,
    traiter_lien_autorisation,
)
from connexion_sociale import (
    ErreurConnexionSociale,
    github_configure,
    github_retour,
    github_url_autorisation,
    google_configure,
    google_lancer,
    google_utilisateur,
)

afficher_barre_titre("Connexion")

# Lien « authorize » reçu par e-mail par un administrateur (?autoriser=...)
traiter_lien_autorisation()

# --- Retours des connexions Google / GitHub (comptes utilisateur simples) ---
try:
    retour_github = github_retour()
except ErreurConnexionSociale as erreur:
    retour_github = None
    st.error(str(erreur))
if retour_github:
    nom_gh, email_gh = retour_github
    ouvrir_session(nom_gh, email_gh)
    st.success(f"Bienvenue, {nom_gh} ! Connecté(e) avec GitHub.")

compte_google = google_utilisateur()
# Traité une seule fois par session, pour ne pas écraser une connexion faite
# ensuite avec le formulaire.
if compte_google and st.session_state.get("google_traite") != compte_google[1]:
    nom_g, email_g = compte_google
    ouvrir_session(nom_g, email_g)
    st.session_state["google_traite"] = email_g
    st.success(f"Bienvenue, {nom_g} ! Connecté(e) avec Google.")

st.write("Renseigne tes informations pour accéder à l'application.")

# --- Boîte : connexion avec Google / GitHub (utilisateur simple) ---
with st.container(key="boite_oauth"):
    st.markdown(
        "<div class='boite-titre'>⚡ Plus rapide : connecte-toi avec ton compte</div>"
        "<div class='boite-texte'>Au lieu de remplir le formulaire, utilise ton compte "
        "Google ou GitHub. Tu accèdes à l'application comme utilisateur simple.</div>",
        unsafe_allow_html=True,
    )
    col_google, col_github = st.columns(2)
    with col_google:
        if st.button(
            "Continuer avec Google",
            key="btn_google",
            disabled=not google_configure(),
            use_container_width=True,
        ):
            google_lancer()
    with col_github:
        if github_configure():
            st.markdown(
                f'<a class="btn-oauth btn-oauth-github" target="_self" '
                f'href="{escape(github_url_autorisation(), quote=True)}">'
                f"Continuer avec GitHub</a>",
                unsafe_allow_html=True,
            )
        else:
            st.button(
                "Continuer avec GitHub",
                key="btn_github_inactif",
                disabled=True,
                use_container_width=True,
            )
    if not (google_configure() and github_configure()):
        st.caption(
            "Un bouton grisé signifie que ce fournisseur n'est pas encore "
            "configuré (voir secrets.toml.exemple)."
        )

with st.form("formulaire_connexion"):
    nom = st.text_input("Nom complet")
    email = st.text_input("Adresse e-mail")
    telephone = st.text_input("Numéro de téléphone")
    mot_de_passe_admin = st.text_input(
        "Mot de passe administrateur",
        type="password",
        help="Laisse ce champ vide si tu n'es pas administrateur.",
    )

    # --- Boîte : demande pour devenir administrateur ---
    with st.container(key="boite_demande_admin"):
        st.markdown(
            "<div class='boite-titre'>🛡️ Tu veux devenir administrateur ?</div>"
            "<div class='boite-texte'>Indique l'e-mail d'un administrateur que tu "
            "connais : il recevra ta demande dans sa boîte Gmail (un message "
            "« authorize ») et pourra t'autoriser. Laisse vide si tu veux "
            "seulement te connecter.</div>",
            unsafe_allow_html=True,
        )
        email_admin_connu = st.text_input("E-mail d'un administrateur que tu connais")

    valider = st.form_submit_button("Se connecter", type="primary")

if valider:
    if not nom or not email:
        st.error("Le nom et l'e-mail sont obligatoires.")
    elif "@" not in email:
        st.error("Merci de saisir une adresse e-mail valide.")
    else:
        est_admin = est_administrateur(email, mot_de_passe_admin)
        ouvrir_session(nom, email, telephone, est_admin)

        if est_admin:
            st.success(f"Bienvenue, {nom} ! Connecté(e) en tant qu'administrateur.")
        else:
            st.success(f"Bienvenue, {nom} ! Tes informations ont été enregistrées.")

        # Demande d'accès administrateur (facultative), envoyée après la connexion.
        if email_admin_connu.strip() and not est_admin:
            ok, message = demander_droits_administrateur(nom, email, email_admin_connu)
            (st.info if ok else st.warning)(message)
