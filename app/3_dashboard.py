"""
app/3_dashboard.py

Intègre un rapport Power BI (publié sur le web) via une iframe.
"""

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from ui_helpers import afficher_barre_titre

afficher_barre_titre("Power BI")

# Remplace cette URL par le lien "Publier sur le web" de ton rapport Power BI.
URL_RAPPORT_POWERBI = "https://app.powerbi.com/view?r=REMPLACE_PAR_TON_LIEN"

if "REMPLACE_PAR_TON_LIEN" in URL_RAPPORT_POWERBI:
    st.warning(
        "Aucun rapport Power BI configuré pour le moment. "
        "Publie ton rapport sur le web depuis Power BI "
        "(Fichier > Publier sur le web) et colle le lien obtenu "
        "dans la variable URL_RAPPORT_POWERBI de ce fichier."
    )
else:
    components.iframe(URL_RAPPORT_POWERBI, height=650, scrolling=True)
