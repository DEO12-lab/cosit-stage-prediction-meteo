"""
app/nav.py

Déclare les pages de l'app via st.Page. Les icônes utilisent la syntaxe
Material Symbols native de Streamlit (":material/nom:") — ce sont de
vraies icônes vectorielles, pas des emoji.
"""

import streamlit as st

page_accueil = st.Page("accueil.py", title="Accueil", icon=":material/home:", default=True)
page_historique = st.Page(
    "4_historique.py", title="Historique des prédictions", icon=":material/history:"
)
page_compte = st.Page("2_compte.py", title="Compte", icon=":material/person:")

TOUTES_LES_PAGES = [page_accueil, page_historique, page_compte]
