"""
pages/4_historique.py
------------------------
Historique des prédictions : un utilisateur connecté ne voit QUE ses
propres prédictions. Un administrateur peut activer une vue globale
pour voir celles de tout le monde. Un visiteur non connecté doit se
connecter pour voir son historique.

Chaque prédiction est présentée dans une carte (box-shadow) ; la date et
l'heure sont écrites en texte tout en bas de la carte.
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

afficher_barre_titre("Historique des prédictions")

utilisateur_connecte = st.session_state.get("utilisateur_connecte")
est_admin = st.session_state.get("est_admin", False)

if not utilisateur_connecte:
    st.warning(
        "Connecte-toi sur la page Connexion pour voir ton historique "
        "de prédictions."
    )
    st.stop()

voir_tout = False
if est_admin:
    voir_tout = st.checkbox(
        "🔓 Voir les prédictions de tous les utilisateurs (mode administrateur)"
    )
    df_predictions = recuperer_predictions() if voir_tout else recuperer_predictions(
        utilisateur_connecte
    )
else:
    st.caption(f"Affichage limité à tes propres prédictions, {utilisateur_connecte}.")
    df_predictions = recuperer_predictions(utilisateur_connecte)

if df_predictions.empty:
    st.info("Aucune prédiction enregistrée pour le moment. "
            "Rends-toi sur la page Accueil pour en effectuer une.")
    st.stop()

st.write(f"**{len(df_predictions)}** prédiction(s) enregistrée(s).")


def _texte(valeur) -> str:
    """Valeur de la base -> texte HTML sûr (les noms et résultats viennent
    de saisies utilisateur : on les échappe avant de les afficher)."""
    return escape(str(valeur)) if valeur not in (None, "") else "—"


cartes = []
for p in df_predictions.itertuples(index=False):
    ligne_utilisateur = (
        f"<div class='carte-prediction-ligne'>👤 <strong>{_texte(p.nom_utilisateur)}</strong></div>"
        if voir_tout
        else ""
    )
    cartes.append(
        "<div class='carte-prediction'>"
        f"{ligne_utilisateur}"
        f"<div class='carte-prediction-ligne'>🌡️ Température : <strong>{_texte(p.temperature_predite)}</strong></div>"
        f"<div class='carte-prediction-ligne'>🌧️ Probabilité de pluie : <strong>{_texte(p.probabilite_pluie)}</strong></div>"
        f"<div class='carte-prediction-ligne'>📋 Résultat : <strong>{_texte(p.resultat)}</strong></div>"
        f"<div class='carte-prediction-date'>🗓️ {escape(formater_date_heure(p.date_prediction))}</div>"
        "</div>"
    )

# Aucune ligne vide ni indentation dans le HTML : sinon Markdown le traiterait
# comme du code.
st.markdown(
    "<div class='grille-predictions'>" + "".join(cartes) + "</div>",
    unsafe_allow_html=True,
)
