"""
app/database.py

Gestion de la base SQLite locale : comptes utilisateurs (nom, prénom,
e-mail, mot de passe haché) et historique des prédictions effectuées.

Chaque prédiction est maintenant rattachée à l'e-mail de l'utilisateur
(unique), pas seulement à son nom affiché : deux personnes portant le
même nom ne peuvent donc jamais voir les prédictions l'une de l'autre.
"""

import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_DB = BASE_DIR / "data" / "utilisateurs.db"

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"


def _maintenant() -> str:
    return datetime.now().strftime(FORMAT_DATE)


def _normaliser_email(email: str) -> str:
    return (email or "").strip().lower()


def _colonnes(curseur, table: str) -> set:
    return {ligne[1] for ligne in curseur.execute(f"PRAGMA table_info({table})")}


def initialiser_base():
    """Crée les tables nécessaires si elles n'existent pas encore, et fait
    évoluer le schéma des bases déjà existantes (ajoute les colonnes
    manquantes sans toucher aux données déjà présentes)."""
    CHEMIN_DB.parent.mkdir(parents=True, exist_ok=True)
    connexion = sqlite3.connect(CHEMIN_DB)
    curseur = connexion.cursor()

    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            telephone TEXT,
            date_inscription TEXT NOT NULL
        )
        """
    )
    colonnes_utilisateurs = _colonnes(curseur, "utilisateurs")
    if "prenom" not in colonnes_utilisateurs:
        curseur.execute("ALTER TABLE utilisateurs ADD COLUMN prenom TEXT NOT NULL DEFAULT ''")
    if "sel" not in colonnes_utilisateurs:
        curseur.execute("ALTER TABLE utilisateurs ADD COLUMN sel TEXT")
    if "mot_de_passe_hash" not in colonnes_utilisateurs:
        curseur.execute("ALTER TABLE utilisateurs ADD COLUMN mot_de_passe_hash TEXT")

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
    colonnes_predictions = _colonnes(curseur, "historique_predictions")
    if "email_utilisateur" not in colonnes_predictions:
        curseur.execute("ALTER TABLE historique_predictions ADD COLUMN email_utilisateur TEXT")

    connexion.commit()
    connexion.close()


# ---------------------------------------------------------------------------
# Comptes utilisateurs
# ---------------------------------------------------------------------------

def email_deja_utilise(email: str) -> bool:
    """True si un compte existe déjà avec cet e-mail."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        ligne = connexion.execute(
            "SELECT 1 FROM utilisateurs WHERE email = ? LIMIT 1",
            (_normaliser_email(email),),
        ).fetchone()
    return ligne is not None


def inscrire_utilisateur(
    email: str, nom: str, prenom: str, telephone: str, sel: str, mot_de_passe_hash: str
) -> bool:
    """Crée un nouveau compte. Retourne False si l'e-mail est déjà pris
    (double vérification, en plus de celle faite côté page)."""
    if email_deja_utilise(email):
        return False
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        connexion.execute(
            "INSERT INTO utilisateurs "
            "(nom, prenom, email, telephone, sel, mot_de_passe_hash, date_inscription) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                nom.strip(), prenom.strip(), _normaliser_email(email),
                (telephone or "").strip(), sel, mot_de_passe_hash, _maintenant(),
            ),
        )
    return True


def obtenir_utilisateur_par_email(email: str) -> dict | None:
    """Retourne le compte correspondant à cet e-mail (ou None), avec le
    sel et l'empreinte du mot de passe pour vérification côté auth.py."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        connexion.row_factory = sqlite3.Row
        ligne = connexion.execute(
            "SELECT * FROM utilisateurs WHERE email = ? LIMIT 1",
            (_normaliser_email(email),),
        ).fetchone()
    return dict(ligne) if ligne else None


# ---------------------------------------------------------------------------
# Historique des prédictions
# ---------------------------------------------------------------------------

def ajouter_prediction(
    nom_utilisateur: str,
    email_utilisateur: str,
    temperature_predite,
    probabilite_pluie,
    resultat: str,
) -> None:
    """Enregistre une prédiction, rattachée à l'e-mail (clé fiable) et au
    nom affiché (pour la lecture dans la carte)."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        connexion.execute(
            "INSERT INTO historique_predictions "
            "(nom_utilisateur, email_utilisateur, date_prediction, "
            "temperature_predite, probabilite_pluie, resultat) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                nom_utilisateur, _normaliser_email(email_utilisateur), _maintenant(),
                str(temperature_predite), str(probabilite_pluie), resultat,
            ),
        )


def recuperer_predictions(email_utilisateur: str):
    """Retourne UNIQUEMENT les prédictions de cet e-mail, sous forme de
    DataFrame — c'est ce filtre SQL qui garantit qu'un utilisateur ne voit
    jamais les prédictions de quelqu'un d'autre."""
    import pandas as pd

    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        df = pd.read_sql_query(
            "SELECT * FROM historique_predictions "
            "WHERE email_utilisateur = ? ORDER BY id DESC",
            connexion,
            params=(_normaliser_email(email_utilisateur),),
        )
    return df
