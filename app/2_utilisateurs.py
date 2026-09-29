"""
pages/2_utilisateurs.py
--------------------------
Liste des utilisateurs enregistrés — réservée aux administrateurs.
Un utilisateur normal (ou un visiteur non connecté) voit un message
d'accès refusé à la place de la liste.

Chaque utilisateur est présenté dans une carte (box-shadow) contenant ses
informations, avec juste en dessous le bouton rouge « Autoriser à devenir
administrateur ».
"""

import sys
from html import escape
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import emails_demandeurs_en_attente, recuperer_utilisateurs
from auth import autoriser_administrateur, emails_administrateurs
from ui_helpers import afficher_barre_titre, formater_date_heure

afficher_barre_titre("Utilisateurs")

if not st.session_state.get("est_admin", False):
    st.error(
        "🔒 Accès réservé aux administrateurs. "
        "Connecte-toi avec un compte administrateur pour voir cette page."
    )
    st.stop()

# Message laissé par l'action précédente (affiché après le rechargement)
message = st.session_state.pop("message_utilisateurs", None)
if message:
    st.success(message)

df_utilisateurs = recuperer_utilisateurs()

if df_utilisateurs.empty:
    st.info("Aucun utilisateur enregistré pour le moment.")
    st.stop()

st.write(f"**{len(df_utilisateurs)}** utilisateur(s) enregistré(s).")

admins = emails_administrateurs()
en_attente = emails_demandeurs_en_attente()

for utilisateur in df_utilisateurs.itertuples(index=False):
    email_norm = str(utilisateur.email).strip().lower()
    telephone = utilisateur.telephone if utilisateur.telephone else "—"

    with st.container(key=f"carte_utilisateur_{utilisateur.id}"):
        st.markdown(
            f"<div class='carte-utilisateur-nom'>{escape(str(utilisateur.nom))}</div>"
            f"<div class='carte-utilisateur-ligne'>✉️ {escape(str(utilisateur.email))}</div>"
            f"<div class='carte-utilisateur-ligne'>📞 {escape(str(telephone))}</div>"
            f"<div class='carte-utilisateur-ligne'>🗓️ Inscrit le "
            f"{escape(formater_date_heure(utilisateur.date_inscription))}</div>",
            unsafe_allow_html=True,
        )

        if email_norm in admins:
            st.markdown(
                "<span class='badge badge-admin'>✅ Autorisé à devenir administrateur</span>",
                unsafe_allow_html=True,
            )
        else:
            if email_norm in en_attente:
                st.markdown(
                    "<span class='badge badge-attente'>⏳ Demande en attente</span>",
                    unsafe_allow_html=True,
                )
            if st.button(
                "Autoriser à devenir administrateur",
                key=f"autoriser_{utilisateur.id}",
                type="primary",
                use_container_width=True,
            ):
                autoriser_administrateur(
                    utilisateur.email,
                    nom=str(utilisateur.nom),
                    par=st.session_state.get("email_connecte"),
                )
                st.session_state["message_utilisateurs"] = (
                    f"✅ {utilisateur.nom} est autorisé(e) à devenir administrateur. "
                    f"Communique-lui le mot de passe administrateur pour qu'il/elle "
                    f"puisse se connecter en tant que tel."
                )
                st.rerun()
