"""
src/accueil.py

Contenu de la page "Accueil" : navbar, en-tête et formulaire de
prédiction météo. Exécuté par st.navigation (voir nav.py et app_1.py).
"""

import os
import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import joblib

SRC_DIR = Path(__file__).resolve().parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from src.config import SEUIL_DECISION_PLUIE
from database import ajouter_prediction
from ui_helpers import afficher_barre_navigation, afficher_entete_logo, logo_img_html

CHEMIN_MODELE_TEMPERATURE = str(SRC_DIR.parent / "models" / "model_temperature.pkl")
CHEMIN_MODELE_PLUIE = str(SRC_DIR.parent / "models" / "model_pluie.pkl")
CHEMIN_LOGO = str(SRC_DIR / "assets" / "logo.png")


@st.cache_resource
def charger_modele(chemin):
    """Charge un modèle une seule fois, mis en cache entre les interactions."""
    if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
        return joblib.load(chemin)
    return None


modele_temperature = charger_modele(CHEMIN_MODELE_TEMPERATURE)
modele_pluie = charger_modele(CHEMIN_MODELE_PLUIE)


# Navbar noire pleine largeur + en-tête centrée


afficher_barre_navigation()
afficher_entete_logo(CHEMIN_LOGO)


# Formulaire de prédiction


logo_petit = logo_img_html(CHEMIN_LOGO, taille_px=40)
st.markdown(
    f"<h1 style='text-align:center;'>{logo_petit} Prédiction météo (Cotonou )</h1>",
    unsafe_allow_html=True,
)
st.write(
    "<p style='text-align:center;'>Veillez renseigner les conditions atmosphériques "
    "ci-dessous pour estimer la température et la probabilité de pluie.</p>",
    unsafe_allow_html=True,
)

with st.form("formulaire_meteo"):
    humidite = st.slider(
        "Humidité relative moyenne (%)", 0, 100, 70,
        help="Taux d'humidité de l'air dans la journée",
    )
    pression = st.number_input(
        "Pression atmosphérique moyenne (hPa)", value=1013.0,
        help="Valeur typique autour de 1013 hPa au niveau de la mer",
    )
    vent_vitesse = st.number_input("Vitesse maximale du vent (km/h)", value=15.0)
    vent_rafales = st.number_input("Rafales maximales de vent (km/h)", value=25.0)
    couverture_nuageuse = st.slider("Couverture nuageuse moyenne (%)", 0, 100, 50)
    mois = st.selectbox(
        "Mois", list(range(1, 13)), index=8,
        format_func=lambda m: [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
        ][m - 1],
    )
    duree_ensoleillement = st.number_input(
        "Durée d'ensoleillement (heures)", value=6.0,
        help="Nombre d'heures d'ensoleillement effectif dans la journée",
    )

    valider = st.form_submit_button("Prédire", type="primary")

if valider:
    caracteristiques = pd.DataFrame([{
        "humidite": humidite,
        "pression": pression,
        "vent_vitesse": vent_vitesse,
        "vent_rafales": vent_rafales,
        "nuages": couverture_nuageuse,
        "mois": mois,
        "sunshine_duration_heures": duree_ensoleillement,
    }])

    # Nom associé à cette prédiction : celui de l'utilisateur connecté
    # (mémorisé lors de la Connexion), sinon "Invité".
    nom_utilisateur = st.session_state.get("utilisateur_connecte", "Invité")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="resultat-prediction">
                <div class="resultat-titre">🌡️ Température estimée</div>
            """,
            unsafe_allow_html=True,
        )

        if modele_temperature is not None:
            prediction_temperature = modele_temperature.predict(caracteristiques)[0]

            st.markdown(
                f"""
                <div class="resultat-valeur">
                    {prediction_temperature:.1f} °C
                </div>
                """,
                unsafe_allow_html=True,
            )

            temperature_a_logger = f"{prediction_temperature:.1f} °C"

        else:
            st.markdown(
                """
                <div class="resultat-message">
                    Modèle de température pas encore disponible (démo).
                </div>
                <div class="resultat-valeur">
                    27.5 °C
                </div>
                """,
                unsafe_allow_html=True,
            )

            temperature_a_logger = "27.5 °C (démo)"

        st.markdown("</div>", unsafe_allow_html=True)


    with col2:

        st.markdown(
            """
            <div class="resultat-prediction">
                <div class="resultat-titre">🌧️ Probabilité de pluie</div>
            """,
            unsafe_allow_html=True,
        )

        if modele_pluie is not None:

            probabilite_pluie = modele_pluie.predict_proba(caracteristiques)[0][1]

            va_pleuvoir = probabilite_pluie >= SEUIL_DECISION_PLUIE

            st.markdown(
                f"""
                <div class="resultat-valeur">
                    {probabilite_pluie * 100:.0f} %
                </div>
                """,
                unsafe_allow_html=True,
            )

            if va_pleuvoir:
                st.markdown(
                    """
                    <div class="resultat-pluie">
                        🌧️ Pluie probable
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                resultat_a_logger = "Pluie probable"

            else:
                st.markdown(
                    """
                    <div class="resultat-pas-pluie">
                        ☀️ Pas de pluie attendue
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                resultat_a_logger = "Pas de pluie attendue"

            probabilite_a_logger = f"{probabilite_pluie * 100:.0f} %"

        else:

            st.markdown(
                """
                <div class="resultat-message">
                    Modèle de pluie pas encore disponible (démo).
                </div>

                <div class="resultat-valeur">
                    40 %
                </div>

                <div class="resultat-pas-pluie">
                    ☀️ Pas de pluie attendue (démo)
                </div>
                """,
                unsafe_allow_html=True,
            )

            probabilite_a_logger = "40 % (démo)"
            resultat_a_logger = "Pas de pluie attendue (démo)"

        st.markdown("</div>", unsafe_allow_html=True)


    # Enregistrement dans l'historique
    ajouter_prediction(
        nom_utilisateur=nom_utilisateur,
        temperature_predite=temperature_a_logger,
        probabilite_pluie=probabilite_a_logger,
        resultat=resultat_a_logger,
    )