"""
app/nav.py

Déclare une seule fois toutes les pages de l'app via st.Page.
"""

import streamlit as st

page_accueil = st.Page("accueil.py", title="Accueil", icon="🏠", default=True)
page_connexion = st.Page("1_connexion.py", title="Connexion", icon="🔐")
page_utilisateurs = st.Page("2_utilisateurs.py", title="Utilisateurs", icon="👥")
page_dashboard = st.Page("3_dashboard.py", title="Power BI", icon="📊")
page_historique = st.Page("4_historique.py", title="Historique", icon="🕘")

TOUTES_LES_PAGES = [
    page_accueil,
    page_connexion,
    page_utilisateurs,
    page_historique,
    page_dashboard,
]
