"""
app/1_connexion.py

Formulaire de connexion / inscription : les informations saisies
(nom, e-mail, téléphone) sont enregistrées dans la base SQLite.
Le nom est aussi mémorisé dans la session pour être associé aux
prédictions faites ensuite sur la page Accueil (voir Historique).
"""

import sys
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import ajouter_utilisateur
from ui_helpers import afficher_barre_titre

afficher_barre_titre("Connexion")

st.write("Veillez renseigner vos informations pour accéder à l'application.")

with st.form("formulaire_connexion"):
    nom = st.text_input("Nom complet")
    email = st.text_input("Adresse e-mail")
    telephone = st.text_input("Numéro de téléphone")

    valider = st.form_submit_button("Se connecter", type="primary")

if valider:
    if not nom or not email:
        st.error("Le nom et l'e-mail sont obligatoires.")
    elif "@" not in email:
        st.error("Merci de saisir une adresse e-mail valide.")
    else:
        ajouter_utilisateur(nom, email, telephone)
        st.session_state["utilisateur_connecte"] = nom
        st.success(f"Bienvenue, {nom} ! Tes informations ont été enregistrées.")
