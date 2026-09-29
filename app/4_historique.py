"""
app/4_historique.py

Historique des prédictions effectuées sur la page Accueil : nom de
l'utilisateur (ou "Invité"), date/heure, température prédite,
probabilité de pluie et résultat obtenu.
"""

import sys
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import recuperer_predictions
from ui_helpers import afficher_barre_titre

afficher_barre_titre("Historique des prédictions")

df_predictions = recuperer_predictions()

if df_predictions.empty:
    st.info("Aucune prédiction enregistrée pour le moment. "
            "Rends-toi sur la page Accueil pour en effectuer une.")
else:
    st.write(f"**{len(df_predictions)}** prédiction(s) enregistrée(s).")
    st.dataframe(
        df_predictions.rename(columns={
            "nom_utilisateur": "Utilisateur",
            "date_prediction": "Date",
            "temperature_predite": "Température",
            "probabilite_pluie": "Probabilité de pluie",
            "resultat": "Résultat",
        }).drop(columns=["id"]),
        use_container_width=True,
        hide_index=True,
    )
