"""
Fonction de chargement partagée, pour que les deux notebooks
lisent les données exactement de la même façon.
"""

import pandas as pd
from pathlib import Path

# Chemin absolu vers la racine du projet, peu importe d'où le script est lancé
BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_CSV_DEFAUT = BASE_DIR / "data" / "data_OPEN_METEO.csv"


def charger_donnees(chemin_csv=CHEMIN_CSV_DEFAUT, skip_rows=3):
    """Charge le CSV Open-Meteo et prépare les colonnes de base."""
    df = pd.read_csv(chemin_csv, skiprows=skip_rows)
    df["time"] = pd.to_datetime(df["time"])
    df["mois"] = df["time"].dt.month
    return df