"""
pages/2_compte.py
--------------------
Affiche, dans une seule carte (box-shadow), les informations du compte
de l'utilisateur actuellement connecté.
"""

import sys
from html import escape
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from ui_helpers import afficher_barre_titre, formater_date_heure
from auth import deconnecter, utilisateur_connecte

afficher_barre_titre("Mon compte", icone="fa-solid fa-user")

utilisateur = utilisateur_connecte()
if utilisateur is None:
    st.warning("Connecte-toi depuis la page Accueil pour voir ton compte.")
    st.stop()


def _l(icone: str, label: str, valeur: str) -> str:
    return (
        f"<div class='carte-compte-ligne'><i class='{icone}'></i>"
        f"<span class='carte-compte-label'>{label}</span><span>{escape(valeur)}</span></div>"
    )


with st.container(key="boite_connecte"):
    contenu = (
        _l("fa-solid fa-user", "Prénom", utilisateur["prenom"])
        + _l("fa-solid fa-user", "Nom", utilisateur["nom"])
        + _l("fa-solid fa-envelope", "E-mail", utilisateur["email"])
        + _l("fa-solid fa-phone", "Téléphone", utilisateur.get("telephone") or "—")
        + _l(
            "fa-regular fa-calendar",
            "Inscrit le",
            formater_date_heure(utilisateur.get("date_inscription", "")),
        )
    )
    st.markdown(contenu, unsafe_allow_html=True)

if st.button("Déconnexion", key="btn_deconnexion_compte"):
    deconnecter()
    st.rerun()
