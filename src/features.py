"""
Préparation des features, commune aux deux modèles.
Renomme les colonnes brutes en noms simples, et convertit
sunshine_duration de secondes en heures.
"""

from config import (
    COLONNE_HUMIDITE, COLONNE_PRESSION, COLONNE_VENT_VITESSE,
    COLONNE_VENT_RAFALES, COLONNE_NUAGES, COLONNE_ENSOLEILLEMENT_BRUTE,
    COLONNE_TEMPERATURE, COLONNE_PRECIPITATION, SEUIL_PLUIE_MM,
    CIBLE_TEMPERATURE, CIBLE_PLUIE,
)


def preparer_features(df):
    """Renomme les colonnes brutes en noms simples utilisés partout ailleurs
    (analysis.py, visualization.py, model.py)."""
    df = df.copy()
    df["temperature"] = df[COLONNE_TEMPERATURE]
    df["precipitation"] = df[COLONNE_PRECIPITATION]
    df["humidite"] = df[COLONNE_HUMIDITE]
    df["pression"] = df[COLONNE_PRESSION]
    df["vent_vitesse"] = df[COLONNE_VENT_VITESSE]
    df["vent"] = df[COLONNE_VENT_VITESSE]  # alias attendu par model.py
    df["vent_rafales"] = df[COLONNE_VENT_RAFALES]
    df["nuages"] = df[COLONNE_NUAGES]
    df["sunshine_duration_heures"] = df[COLONNE_ENSOLEILLEMENT_BRUTE] / 3600
    return df


def creer_cible_temperature(df):
    return df[COLONNE_TEMPERATURE].rename(CIBLE_TEMPERATURE)


def creer_cible_pluie(df):
    cible = (df[COLONNE_PRECIPITATION] > SEUIL_PLUIE_MM).astype(int)
    return cible.rename(CIBLE_PLUIE)
