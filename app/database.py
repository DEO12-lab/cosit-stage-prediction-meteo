"""
src/database.py
-----------------
Gestion de la base SQLite locale : utilisateurs (nom, e-mail, téléphone),
historique des prédictions effectuées (utilisateur, date, résultat),
administrateurs autorisés et demandes d'autorisation administrateur.
"""

import secrets
import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
CHEMIN_DB = BASE_DIR / "data" / "utilisateurs.db"

FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
# Durée pendant laquelle le lien reçu par e-mail reste utilisable.
DUREE_VALIDITE_DEMANDE_HEURES = 48


def _maintenant() -> str:
    return datetime.now().strftime(FORMAT_DATE)


def _normaliser_email(email: str) -> str:
    return (email or "").strip().lower()


def _hacher_jeton(jeton: str) -> str:
    """Seule l'empreinte du jeton est stockée : une fuite de la base ne
    permet donc pas d'utiliser les liens d'autorisation en attente."""
    return hashlib.sha256(jeton.encode()).hexdigest()


def _limite_validite() -> str:
    limite = datetime.now() - timedelta(hours=DUREE_VALIDITE_DEMANDE_HEURES)
    return limite.strftime(FORMAT_DATE)


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
    # E-mails autorisés à devenir administrateur (en plus de la liste fixe
    # EMAILS_ADMINISTRATEURS de auth.py).
    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS administrateurs (
            email TEXT PRIMARY KEY,
            autorise_par TEXT,
            date_autorisation TEXT NOT NULL
        )
        """
    )
    # Demandes envoyées par e-mail à un administrateur (jeton haché).
    curseur.execute(
        """
        CREATE TABLE IF NOT EXISTS demandes_admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_demandeur TEXT NOT NULL,
            email_demandeur TEXT NOT NULL,
            email_admin TEXT NOT NULL,
            jeton_hash TEXT NOT NULL UNIQUE,
            statut TEXT NOT NULL DEFAULT 'en_attente',
            date_demande TEXT NOT NULL
        )
        """
    )
    connexion.commit()
    connexion.close()


def utilisateur_existe(email: str) -> bool:
    """True si un utilisateur avec cet e-mail est déjà enregistré."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        ligne = connexion.execute(
            "SELECT 1 FROM utilisateurs WHERE lower(email) = ? LIMIT 1",
            (_normaliser_email(email),),
        ).fetchone()
    return ligne is not None


def ajouter_utilisateur(nom: str, email: str, telephone: str) -> None:
    """Insère un nouvel utilisateur dans la base (sauf si son e-mail y est
    déjà : évite les doublons quand la même personne se reconnecte)."""
    if utilisateur_existe(email):
        return
    connexion = sqlite3.connect(CHEMIN_DB)
    curseur = connexion.cursor()
    curseur.execute(
        "INSERT INTO utilisateurs (nom, email, telephone, date_inscription) "
        "VALUES (?, ?, ?, ?)",
        (nom, email, telephone, _maintenant()),
    )
    connexion.commit()
    connexion.close()


def recuperer_utilisateurs():
    """Retourne tous les utilisateurs enregistrés, sous forme de DataFrame.
    Réservé aux administrateurs — le contrôle d'accès se fait côté page
    (voir pages/2_utilisateurs.py et app/auth.py), pas ici : cette fonction
    reste volontairement simple, sans logique de permission."""
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
            _maintenant(),
            str(temperature_predite),
            str(probabilite_pluie),
            resultat,
        ),
    )
    connexion.commit()
    connexion.close()


def recuperer_predictions(nom_utilisateur: str | None = None):
    """Retourne l'historique des prédictions, sous forme de DataFrame.
    Si nom_utilisateur est fourni, ne retourne QUE les prédictions de cet
    utilisateur (c'est ce filtre qui garantit qu'un utilisateur normal ne
    voit jamais les prédictions des autres). Si None, retourne tout —
    réservé aux administrateurs, filtré côté page."""
    import pandas as pd

    connexion = sqlite3.connect(CHEMIN_DB)
    if nom_utilisateur is not None:
        df = pd.read_sql_query(
            "SELECT * FROM historique_predictions "
            "WHERE nom_utilisateur = ? ORDER BY id DESC",
            connexion,
            params=(nom_utilisateur,),
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM historique_predictions ORDER BY id DESC", connexion
        )
    connexion.close()
    return df


# ---------------------------------------------------------------------------
# Administrateurs et demandes d'autorisation
# ---------------------------------------------------------------------------

def ajouter_administrateur(email: str, autorise_par: str | None = None) -> None:
    """Autorise cet e-mail à devenir administrateur (sans effet s'il l'est déjà)."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        connexion.execute(
            "INSERT OR IGNORE INTO administrateurs "
            "(email, autorise_par, date_autorisation) VALUES (?, ?, ?)",
            (_normaliser_email(email), _normaliser_email(autorise_par or ""), _maintenant()),
        )


def recuperer_emails_administrateurs() -> set[str]:
    """E-mails autorisés à devenir administrateur (table administrateurs)."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        lignes = connexion.execute("SELECT email FROM administrateurs").fetchall()
    return {ligne[0] for ligne in lignes}


def creer_demande_admin(nom: str, email_demandeur: str, email_admin: str) -> str | None:
    """Enregistre une demande et retourne le jeton EN CLAIR (à placer dans le
    lien de l'e-mail ; il n'est jamais stocké tel quel).
    Retourne None si la même demande est déjà en attente et encore valide
    (évite d'inonder un administrateur d'e-mails)."""
    demandeur = _normaliser_email(email_demandeur)
    admin = _normaliser_email(email_admin)
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        deja = connexion.execute(
            "SELECT 1 FROM demandes_admin WHERE email_demandeur = ? "
            "AND email_admin = ? AND statut = 'en_attente' AND date_demande >= ?",
            (demandeur, admin, _limite_validite()),
        ).fetchone()
        if deja:
            return None
        jeton = secrets.token_urlsafe(32)
        connexion.execute(
            "INSERT INTO demandes_admin "
            "(nom_demandeur, email_demandeur, email_admin, jeton_hash, date_demande) "
            "VALUES (?, ?, ?, ?, ?)",
            (nom, demandeur, admin, _hacher_jeton(jeton), _maintenant()),
        )
    return jeton


def annuler_demande(jeton: str) -> None:
    """Supprime une demande (utilisé si l'e-mail n'a pas pu être envoyé)."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        connexion.execute(
            "DELETE FROM demandes_admin WHERE jeton_hash = ?", (_hacher_jeton(jeton),)
        )


def lire_demande(jeton: str) -> dict | None:
    """Retourne la demande liée à ce jeton si elle est en attente et non
    expirée, sinon None. Ne modifie rien."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        ligne = connexion.execute(
            "SELECT nom_demandeur, email_demandeur, email_admin FROM demandes_admin "
            "WHERE jeton_hash = ? AND statut = 'en_attente' AND date_demande >= ?",
            (_hacher_jeton(jeton), _limite_validite()),
        ).fetchone()
    if ligne is None:
        return None
    return {"nom": ligne[0], "email_demandeur": ligne[1], "email_admin": ligne[2]}


def approuver_demande(jeton: str) -> dict | None:
    """Consomme le jeton (usage unique) et autorise le demandeur.
    Retourne la demande approuvée, ou None si le jeton est inconnu,
    déjà utilisé ou expiré."""
    demande = lire_demande(jeton)
    if demande is None:
        return None
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion, connexion:
        # Le WHERE statut = 'en_attente' garantit qu'un double clic ou deux
        # onglets ne peuvent pas valider la même demande deux fois.
        modifiees = connexion.execute(
            "UPDATE demandes_admin SET statut = 'approuvee' "
            "WHERE jeton_hash = ? AND statut = 'en_attente'",
            (_hacher_jeton(jeton),),
        ).rowcount
        if modifiees == 0:
            return None
        connexion.execute(
            "INSERT OR IGNORE INTO administrateurs "
            "(email, autorise_par, date_autorisation) VALUES (?, ?, ?)",
            (demande["email_demandeur"], demande["email_admin"], _maintenant()),
        )
    return demande


def emails_demandeurs_en_attente() -> set[str]:
    """E-mails des personnes ayant une demande en attente (encore valide)."""
    with closing(sqlite3.connect(CHEMIN_DB)) as connexion:
        lignes = connexion.execute(
            "SELECT DISTINCT email_demandeur FROM demandes_admin "
            "WHERE statut = 'en_attente' AND date_demande >= ?",
            (_limite_validite(),),
        ).fetchall()
    return {ligne[0] for ligne in lignes}
