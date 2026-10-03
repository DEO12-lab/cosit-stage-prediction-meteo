"""
app/4_historique.py

Historique des prédictions : chaque utilisateur ne voit QUE ses propres
prédictions (filtrées par e-mail, voir database.py). Chaque prédiction
est une carte (box-shadow) ; la date et l'heure sont en texte, en bas.
"""

import sys
from html import escape
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import recuperer_predictions
from ui_helpers import afficher_barre_titre, formater_date_heure
from auth import utilisateur_connecte

afficher_barre_titre("Historique des prédictions", icone="fa-solid fa-clock-rotate-left")

utilisateur = utilisateur_connecte()
if utilisateur is None:
    st.warning("Connecte-toi depuis la page Accueil pour voir ton historique.")
    st.stop()

df_predictions = recuperer_predictions(utilisateur["email"])

if df_predictions.empty:
    st.info("Aucune prédiction enregistrée pour le moment. "
            "Rends-toi sur la page Accueil pour en effectuer une.")
    st.stop()

st.write(f"**{len(df_predictions)}** prédiction(s) enregistrée(s).")


def _texte(valeur) -> str:
    return escape(str(valeur)) if valeur not in (None, "") else "—"


cartes = []
for p in df_predictions.itertuples(index=False):
    cartes.append(
        "<div class='carte-prediction'>"
        f"<div class='carte-prediction-ligne'><i class='fa-solid fa-temperature-half'></i>"
        f"Température : <strong>{_texte(p.temperature_predite)}</strong></div>"
        f"<div class='carte-prediction-ligne'><i class='fa-solid fa-cloud-rain'></i>"
        f"Probabilité de pluie : <strong>{_texte(p.probabilite_pluie)}</strong></div>"
        f"<div class='carte-prediction-ligne'><i class='fa-solid fa-circle-info'></i>"
        f"Résultat : <strong>{_texte(p.resultat)}</strong></div>"
        f"<div class='carte-prediction-date'><i class='fa-regular fa-clock'></i>"
        f"{escape(formater_date_heure(p.date_prediction))}</div>"
        "</div>"
    )

st.markdown(
    "<div class='grille-predictions'>" + "".join(cartes) + "</div>",
    unsafe_allow_html=True,
)
