"""
app/2_utilisateurs.py

Liste des utilisateurs enregistrés via la page Connexion,
lue directement depuis la base SQLite.
"""

import sys
from pathlib import Path

import streamlit as st

SRC_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(SRC_DIR))
sys.path.append(str(SRC_DIR.parent))

from database import recuperer_utilisateurs
from ui_helpers import afficher_barre_titre

afficher_barre_titre("Utilisateurs")

df_utilisateurs = recuperer_utilisateurs()

if df_utilisateurs.empty:
    st.info("Aucun utilisateur enregistré pour le moment. "
            "Rends-toi sur la page Connexion pour en ajouter un.")
else:
    st.write(f"**{len(df_utilisateurs)}** utilisateur(s) enregistré(s).")
    st.dataframe(df_utilisateurs, use_container_width=True, hide_index=True)
