"""
src/data_cleaning.py
---------------------
Nettoie et prépare les données météo brutes avant leur insertion en base.
"""

import pandas as pd
import numpy as np


def charger_donnees_brutes(chemin_csv: str) -> pd.DataFrame:
    """Lit le fichier CSV brut téléchargé (Kaggle, NASA POWER, etc.)."""
    return pd.read_csv(chemin_csv)


def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique une série de nettoyages :
    1. Suppression des doublons
    2. Conversion des types (dates, nombres)
    3. Traitement des valeurs manquantes
    4. Suppression des valeurs aberrantes
    """
    df = df.drop_duplicates()

    # Conversion de la colonne date en type datetime
    df["date_releve"] = pd.to_datetime(df["date_releve"], errors="coerce")

    # Conversion des colonnes numériques (les valeurs non convertibles deviennent NaN)
    colonnes_num = ["temperature", "precipitation", "humidite", "vent"]
    for col in colonnes_num:
       df[col] = pd.to_numeric(df[col], errors="coerce")

    # Suppression des lignes sans date (donnée inexploitable)
    df = df.dropna(subset=["date_releve"])

    # Remplacement des valeurs manquantes par la médiane de la station
    for col in colonnes_num:
       df[col] = df.groupby("nom_station")[col].transform(
           lambda x: x.fillna(x.median())
)

    # Suppression des valeurs aberrantes (ex. température > 55°C ou < 0°C au Bénin)
    df = df[df["temperature"].between(0, 55)]
    df = df[df["precipitation"] >= 0]

    return df.reset_index(drop=True)

def sauvegarder_donnees_propres(df: pd.DataFrame, chemin_sortie: str):
    """Enregistre le DataFrame nettoyé au format CSV, prêt pour l'insertion SQL."""
    df.to_csv(chemin_sortie, index=False)


if __name__ == "__main__":
    # Exécution autonome : permet de tester ce module seul avec
    # la commande : python src/data_cleaning.py
    brut = charger_donnees_brutes("data/raw/meteo_benin.csv")
    propre = nettoyer_donnees(brut)
    sauvegarder_donnees_propres(propre, "data/processed/meteo_clean.csv")
    print(f"{ len(propre)} lignes nettoyées et sauvegardées.")
