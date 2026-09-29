"""
Application Streamlit — Prédiction météo Cotonou
Point d'entrée (fichier passé à "streamlit run"). Ce fichier :
1. Affiche un écran de démarrage (splash screen) avec le logo, une
   seule fois par session, avant que quoi que ce soit d'autre
   n'apparaisse — comme sur une app mobile.
2. Configure la page, injecte le style commun (fond, sidebar, footer).
3. Déclare les pages disponibles et exécute celle choisie par
   l'utilisateur.
"""

import sys
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import initialiser_base
from ui_helpers import (
    afficher_splash,
    injecter_style_global,
    afficher_logo_sidebar,
    afficher_footer,
)
from nav import TOUTES_LES_PAGES

CHEMIN_LOGO = str(SRC_DIR / "assets" / "logo.png")

st.set_page_config(page_title="MétéoHub", page_icon=CHEMIN_LOGO, layout="wide")


# Splash screen : affiché une seule fois par session, avant tout le reste.


if "splash_affichee" not in st.session_state:
    st.session_state.splash_affichee = False

if not st.session_state.splash_affichee:
    afficher_splash(chemin_logo=CHEMIN_LOGO, duree_secondes=1.8)
    st.session_state.splash_affichee = True
    st.rerun()


# Application normale (affichée seulement après le splash)


initialiser_base()
injecter_style_global()
afficher_logo_sidebar(CHEMIN_LOGO)

page_courante = st.navigation(TOUTES_LES_PAGES)
page_courante.run()

afficher_footer()
