"""
src/database.py
-----------------
Gestion de la base SQLite locale : utilisateurs (nom, e-mail, téléphone)
et historique des prédictions effectuées (utilisateur, date, résultat).
"""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_DB = BASE_DIR / "data" / "utilisateurs.db"


def initialiser_base():
    """Crée les tables nécessaires si elles n'existent pas encore.
    Ne recrée rien si elles existent déjà (sûr à appeler à chaque lancement)."""
    CHEMIN_DB.parent.mkdir(parents=True, exist_ok=True)
    connexion = sqlite3.connect(CHEMIN_DB)
    curseur = connexion.cursor()
    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL,
            telephone TEXT,
            date_inscription TEXT NOT NULL
        )
        """
    )
    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS historique_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_utilisateur TEXT NOT NULL,
            date_prediction TEXT NOT NULL,
            temperature_predite TEXT,
            probabilite_pluie TEXT,
            resultat TEXT
        )
        """
    )
    connexion.commit()
    connexion.close()


def ajouter_utilisateur(nom: str, email: str, telephone: str) -> None:
    """Insère un nouvel utilisateur dans la base."""
    connexion = sqlite3.connect(CHEMIN_DB)
    curseur = connexion.cursor()
    curseur.execute(
        "INSERT INTO utilisateurs (nom, email, telephone, date_inscription) "
        "VALUES (?, ?, ?, ?)",
        (nom, email, telephone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    connexion.commit()
    connexion.close()


def recuperer_utilisateurs():
    """Retourne tous les utilisateurs enregistrés, sous forme de DataFrame."""
    import pandas as pd

    connexion = sqlite3.connect(CHEMIN_DB)
    df = pd.read_sql_query("SELECT * FROM utilisateurs ORDER BY id DESC", connexion)
    connexion.close()
    return df


def ajouter_prediction(
    nom_utilisateur: str,
    temperature_predite,
    probabilite_pluie,
    resultat: str,
) -> None:
    """Enregistre une prédiction effectuée dans l'historique."""
    connexion = sqlite3.connect(CHEMIN_DB)
    curseur = connexion.cursor()
    curseur.execute(
        "INSERT INTO historique_predictions "
        "(nom_utilisateur, date_prediction, temperature_predite, probabilite_pluie, resultat) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            nom_utilisateur,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            str(temperature_predite),
            str(probabilite_pluie),
            resultat,
        ),
    )
    connexion.commit()
    connexion.close()


def recuperer_predictions():
    """Retourne tout l'historique des prédictions, sous forme de DataFrame."""
    import pandas as pd

    connexion = sqlite3.connect(CHEMIN_DB)
    df = pd.read_sql_query(
        "SELECT * FROM historique_predictions ORDER BY id DESC", connexion
    )
    connexion.close()
    return df
