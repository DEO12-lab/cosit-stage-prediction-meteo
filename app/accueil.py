"""
app/accueil.py
-----------------
Page d'accueil, en 3 cartes (box-shadow) dans l'ordre :
1. Logo + nom de l'app
2. Connexion / inscription (obligatoire pour débloquer la carte suivante)
3. Formulaire de prédiction météo — puis les résultats, chacun dans une
   carte à deux parties (bandeau vert = titre, partie blanche = valeur).
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
from ui_helpers import (
    afficher_barre_navigation,
    afficher_entete_logo,
    afficher_resultat,
    logo_img_html,
)
from auth import connecter, deconnecter, inscrire, utilisateur_connecte

CHEMIN_MODELE_TEMPERATURE = str(SRC_DIR.parent / "models" / "model_temperature.pkl")
CHEMIN_MODELE_PLUIE = str(SRC_DIR.parent / "models" / "model_pluie.pkl")
CHEMIN_LOGO = str(SRC_DIR / "assets" / "logo.png")


@st.cache_resource
def charger_modele(chemin):
    if os.path.exists(chemin) and os.path.getsize(chemin) > 0:
        return joblib.load(chemin)
    return None


modele_temperature = charger_modele(CHEMIN_MODELE_TEMPERATURE)
modele_pluie = charger_modele(CHEMIN_MODELE_PLUIE)

# --- Carte navigation + Carte 1 (logo + nom) ---
afficher_barre_navigation()
afficher_entete_logo(CHEMIN_LOGO)

utilisateur = utilisateur_connecte()


# Carte 2 : connexion / inscription


if utilisateur is None:
    with st.container(key="boite_connexion"):
        st.markdown(
            '<div class="boite-titre"><i class="fa-solid fa-lock"></i>'
            "Connecte-toi pour accéder aux prédictions</div>"
            '<div class="boite-texte">Un compte est nécessaire pour utiliser le '
            "formulaire de prédiction ci-dessous.</div>",
            unsafe_allow_html=True,
        )

        onglet_connexion, onglet_inscription = st.tabs(["Se connecter", "Créer un compte"])

        with onglet_connexion:
            with st.form("formulaire_connexion"):
                email_c = st.text_input("Adresse e-mail")
                mdp_c = st.text_input("Mot de passe", type="password")
                valider_connexion = st.form_submit_button("Se connecter", type="primary")

            if valider_connexion:
                ok, message, utilisateur_trouve = connecter(email_c, mdp_c)
                if ok:
                    from auth import ouvrir_session
                    ouvrir_session(utilisateur_trouve)
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with onglet_inscription:
            with st.form("formulaire_inscription"):
                email_i = st.text_input("Adresse e-mail *")
                nom_i = st.text_input("Nom *")
                prenom_i = st.text_input("Prénom *")
                telephone_i = st.text_input("Numéro de téléphone")
                mdp_i = st.text_input("Mot de passe *", type="password")
                mdp_i_confirme = st.text_input("Confirmer le mot de passe *", type="password")
                valider_inscription = st.form_submit_button("Créer mon compte", type="primary")

            if valider_inscription:
                if mdp_i != mdp_i_confirme:
                    st.error("Les deux mots de passe ne correspondent pas.")
                else:
                    ok, message = inscrire(email_i, nom_i, prenom_i, telephone_i, mdp_i)
                    if ok:
                        ok2, _, utilisateur_cree = connecter(email_i, mdp_i)
                        if ok2:
                            from auth import ouvrir_session
                            ouvrir_session(utilisateur_cree)
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

else:
    with st.container(key="boite_connecte"):
        col_texte, col_bouton = st.columns([4, 1])
        with col_texte:
            st.markdown(
                f'<div class="boite-titre"><i class="fa-solid fa-circle-check" '
                f'style="color:#2e7d32;"></i>Connecté en tant que '
                f"{utilisateur['prenom']} {utilisateur['nom']}</div>",
                unsafe_allow_html=True,
            )
        with col_bouton:
            if st.button("Déconnexion", key="btn_deconnexion", use_container_width=True):
                deconnecter()
                st.rerun()

# 
# Carte 3 : formulaire de prédiction (verrouillé tant que non connecté)
# 

logo_petit = logo_img_html(CHEMIN_LOGO, taille_px=36)
st.markdown(
    f"<h1 style='text-align:center;font-size:1.6rem;'>{logo_petit} Prédiction météo (Cotonou)</h1>",
    unsafe_allow_html=True,
)

if utilisateur is None:
    st.info(
        "Le formulaire de prédiction est accessible après connexion — "
        "utilise la carte ci-dessus pour te connecter ou créer un compte."
    )
    st.stop()

st.write(
    "<p style='text-align:center;'>Renseigne les conditions atmosphériques "
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

    nom_complet = f"{utilisateur['prenom']} {utilisateur['nom']}"

    st.markdown('<div class="grille-resultats">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if modele_temperature is not None:
            prediction_temperature = modele_temperature.predict(caracteristiques)[0]
            afficher_resultat(
                "fa-solid fa-temperature-half", "Température estimée",
                f"{prediction_temperature:.1f} °C",
            )
            temperature_a_logger = f"{prediction_temperature:.1f} °C"
        else:
            afficher_resultat(
                "fa-solid fa-temperature-half", "Température estimée", "27.5 °C",
                message="Modèle pas encore disponible (démo).",
            )
            temperature_a_logger = "27.5 °C (démo)"

    with col2:
        if modele_pluie is not None:
            probabilite_pluie = modele_pluie.predict_proba(caracteristiques)[0][1]
            va_pleuvoir = probabilite_pluie >= SEUIL_DECISION_PLUIE
            alerte = (
                {"texte": "Pluie probable", "type": "pluie"} if va_pleuvoir
                else {"texte": "Pas de pluie attendue", "type": "sec"}
            )
            afficher_resultat(
                "fa-solid fa-cloud-rain", "Probabilité de pluie",
                f"{probabilite_pluie * 100:.0f} %", alerte=alerte,
            )
            resultat_a_logger = alerte["texte"]
            probabilite_a_logger = f"{probabilite_pluie * 100:.0f} %"
        else:
            afficher_resultat(
                "fa-solid fa-cloud-rain", "Probabilité de pluie", "40 %",
                message="Modèle pas encore disponible (démo).",
                alerte={"texte": "Pas de pluie attendue (démo)", "type": "sec"},
            )
            probabilite_a_logger = "40 % (démo)"
            resultat_a_logger = "Pas de pluie attendue (démo)"

    st.markdown("</div>", unsafe_allow_html=True)

    ajouter_prediction(
        nom_utilisateur=nom_complet,
        email_utilisateur=utilisateur["email"],
        temperature_predite=temperature_a_logger,
        probabilite_pluie=probabilite_a_logger,
        resultat=resultat_a_logger,
    )
