"""
src/ui_helpers.py
-------------------
Style CSS et composants partagés.

- injecter_style_global()    : CSS commun + police d'icônes Font Awesome
                                (cdnjs), appelé une fois dans app.py
- afficher_splash()          : écran de démarrage plein écran
- afficher_logo_sidebar()    : logo + nom en haut de la sidebar
- logo_img_html()            : balise <img> du logo, réutilisable partout
- afficher_barre_navigation(): bande noire avec le menu (Accueil,
                                Historique, Compte) — page d'accueil
- afficher_barre_titre()     : bande noire avec juste le nom de la page,
                                pour Historique et Compte
- afficher_entete_logo()     : bloc "MétéoHub" centré, en haut de l'accueil
- afficher_resultat()        : carte de résultat divisée vert (titre) /
                                blanc (valeur), pour les prédictions
- afficher_footer()          : pied de page non fixe
- formater_date_heure()      : "2026-09-29 14:32:05" -> "29/09/2026 à 14:32"
"""

import base64
from datetime import datetime
from pathlib import Path

import streamlit as st


def injecter_style_global():
    st.markdown(
        """
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
        <style>
            /* --- Fond de page : dégradé vertical, jaune en haut, gris en bas --- */
            .stApp {
                background: linear-gradient(
                    180deg,
                    #ffd54f 0%,
                    #ffd54f 45%,
                    #d6d9dc 55%,
                    #d6d9dc 100%
                );
            }

            header[data-testid="stHeader"] {
                background: transparent;
                height: 2.2rem;
                min-height: 2.2rem;
            }
            div[data-testid="stDecoration"] { display: none; }
            html, body { overflow-x: hidden; }

            .block-container {
                width: 100%;
                max-width: 1060px;
                box-sizing: border-box;
                margin-left: auto;
                margin-right: auto;
                padding: 0.5rem 1.5rem 2rem 1.5rem;
            }

            .st-key-navbar_accueil,
            .barre-titre-noire,
            .entete-accueil,
            div[data-testid="stForm"],
            .footer {
                width: 100%;
                max-width: 100%;
                min-width: 0;
                box-sizing: border-box;
                margin-left: auto;
                margin-right: auto;
            }
            .st-key-navbar_accueil *,
            .entete-accueil *,
            div[data-testid="stForm"] * {
                box-sizing: border-box;
                min-width: 0;
            }

            /* --- Sidebar --- */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0b3d91 0%, #1976d2 100%);
            }
            section[data-testid="stSidebar"] * { color: #ffffff !important; }
            [data-testid="stSidebarNav"] a { border-radius: 8px; margin: 2px 6px; }
            [data-testid="stSidebarNav"] a:hover { background: rgba(255, 255, 255, 0.15); }

            /* ===================================================== */
            /* Navbar noire (page Accueil) : Accueil / Historique / Compte */
            /* ===================================================== */
            .st-key-navbar_accueil {
                width: 100%;
                background: #0a0a0a;
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
                padding: 0.3rem 0.5rem;
                margin-bottom: 1.2rem;
            }
            .st-key-navbar_accueil div[data-testid="stHorizontalBlock"] {
                display: flex;
                width: 100%;
                flex-wrap: nowrap !important;
                gap: 0.15rem;
                overflow-x: auto;
                box-sizing: border-box;
            }
            .st-key-navbar_accueil div[data-testid="column"] {
                flex: 1 1 0 !important;
                min-width: max-content;
            }
            .st-key-navbar_accueil div[data-testid="stPageLink"] {
                background: transparent;
                box-shadow: none;
                padding: 0.4rem 0.3rem;
                white-space: nowrap;
            }
            .st-key-navbar_accueil div[data-testid="stPageLink"]:hover {
                background: rgba(255, 255, 255, 0.10);
                border-radius: 8px;
            }
            .st-key-navbar_accueil div[data-testid="stPageLink"] a p,
            .st-key-navbar_accueil div[data-testid="stPageLink"] a span {
                color: #ffffff !important;
                font-weight: 600 !important;
                justify-content: center !important;
            }

            /* ===================================================== */
            /* Bande titre noire (Historique, Compte) */
            /* ===================================================== */
            .barre-titre-noire {
                width: 100%;
                background: #0a0a0a;
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
                padding: 0.5rem 0;
                margin-bottom: 1.2rem;
                text-align: center;
            }
            .barre-titre-noire span {
                color: #ffffff;
                font-weight: 700;
                font-size: 1.15rem;
                letter-spacing: 0.4px;
            }
            .barre-titre-noire i { margin-right: 0.5rem; }

            /* --- Carte 1 : logo + nom de l'app (page d'accueil) --- */
            .entete-accueil {
                background: #ffffff;
                border-radius: 16px;
                padding: 1.3rem 1.5rem;
                box-shadow: 0 6px 18px rgba(15, 40, 90, 0.15);
                margin-bottom: 1rem;
                text-align: center;
            }

            /* --- Formulaires en carte avec ombre --- */
            div[data-testid="stForm"] {
                background: #ffffff;
                padding: 1.8rem 1.8rem 1rem 1.8rem;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(15, 40, 90, 0.18);
                border: 1px solid #eef1f6;
                margin-bottom: 1rem;
            }
            div[data-testid="stForm"] p,
            div[data-testid="stForm"] span,
            div[data-testid="stForm"] label {
                color: #1a1a1a !important;
            }
            div[data-testid="stSlider"],
            div[data-testid="stNumberInput"],
            div[data-testid="stSelectbox"],
            div[data-testid="stTextInput"] {
                background: #fbfcfe;
                padding: 0.8rem 1rem 0.5rem 1rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(15, 40, 90, 0.10);
                margin-bottom: 0.8rem;
            }

            [data-testid="stWidgetLabel"] p,
            [data-testid="stWidgetLabel"] label,
            div[data-testid="stSlider"] label,
            div[data-testid="stNumberInput"] label,
            div[data-testid="stSelectbox"] label,
            div[data-testid="stTextInput"] label {
                color: #1a1a1a !important;
            }
            div[data-baseweb="input"], div[data-baseweb="base-input"] {
                background-color: #ffffff !important;
            }
            div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
                color: #1a1a1a !important;
                background-color: #ffffff !important;
                -webkit-text-fill-color: #1a1a1a !important;
            }
            button[data-testid="stNumberInputStepUp"],
            button[data-testid="stNumberInputStepDown"] {
                background-color: #eef1f6 !important;
                color: #1a1a1a !important;
            }
            button[data-testid="stNumberInputStepUp"] svg,
            button[data-testid="stNumberInputStepDown"] svg { fill: #1a1a1a !important; }
            div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                border-color: #d6d9dc !important;
            }
            div[data-baseweb="select"] span { color: #1a1a1a !important; }
            div[data-testid="stSlider"] [data-testid="stTickBarMin"],
            div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
                color: #555555 !important;
            }
            div[data-testid="stFormSubmitButton"] button {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0.6rem 2.2rem;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(25, 118, 210, 0.35);
                transition: background-color 0.2s ease, transform 0.1s ease;
            }
            div[data-testid="stFormSubmitButton"] button:hover {
                background-color: #0d47a1;
                transform: translateY(-1px);
            }
            div[data-testid="stTabs"] button[aria-selected="true"] p { color: #1976d2 !important; }
            div[data-testid="stTabs"] p { color: #1a1a1a !important; }

            div[data-testid="stDataFrame"] {
                box-shadow: 0 4px 14px rgba(15, 40, 90, 0.12);
                border-radius: 12px;
                overflow: hidden;
            }

            /* --- Footer non fixe --- */
            .footer {
                background: #0b3d91;
                color: #e3f2fd;
                text-align: center;
                padding: 0.9rem 1rem;
                font-size: 0.85rem;
                border-radius: 10px;
                margin-top: 1.5rem;
            }
            .footer a { color: #ffd54f; text-decoration: none; margin: 0 0.4rem; }
            .footer i { margin-right: 0.3rem; }

            /* --- Responsive --- */
            @media (max-width: 640px) {
                .block-container { max-width: 100%; padding-left: 0.8rem; padding-right: 0.8rem; }
                div[data-testid="stForm"] { padding: 1.1rem; }
                .entete-accueil { padding: 1rem; }
                .footer { font-size: 0.75rem; padding: 0.7rem; }
                .barre-titre-noire span { font-size: 1.05rem; }
                .grille-resultats { grid-template-columns: 1fr !important; }
                .grille-predictions { grid-template-columns: 1fr !important; }
            }

            /* ===================================================== */
            /* VERROUILLAGE : mode clair forcé, Light/Dark/System     */
            /* ===================================================== */
            :root, [data-theme="dark"], .stApp {
                --text-color: #1a1a1a !important;
                --background-color: #ffffff !important;
                --secondary-background-color: #f0f2f6 !important;
                --primary-color: #1976d2 !important;
            }
            div[data-testid="stForm"], div[data-testid="stForm"] * {
                background-color: transparent;
                color: #1a1a1a !important;
            }
            div[data-testid="stForm"] { background-color: #ffffff !important; }
            div[data-testid="stSlider"], div[data-testid="stNumberInput"],
            div[data-testid="stSelectbox"], div[data-testid="stTextInput"] {
                background-color: #fbfcfe !important;
            }
            div[data-testid="stForm"] input, div[data-testid="stForm"] textarea,
            div[data-testid="stForm"] select,
            div[data-testid="stForm"] div[data-baseweb="input"],
            div[data-testid="stForm"] div[data-baseweb="base-input"],
            div[data-testid="stForm"] div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                -webkit-text-fill-color: #1a1a1a !important;
                border-color: #d6d9dc !important;
            }
            div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"],
            div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"] {
                background-color: #eef1f6 !important;
                color: #1a1a1a !important;
            }
            div[data-testid="stFormSubmitButton"] button,
            div[data-testid="stFormSubmitButton"] button * {
                color: #ffffff !important;
                background-color: #1976d2 !important;
            }

            /* ===================================================== */
            /* Carte "connecte-toi" / "connecté en tant que" / Compte */
            /* ===================================================== */
            [class*="st-key-boite_"] {
                background: #ffffff;
                border-radius: 16px;
                padding: 1.1rem 1.3rem;
                margin-bottom: 1rem;
                border: 1px solid #eef1f6;
                border-left: 6px solid #1976d2;
                box-shadow: 0 8px 24px rgba(15, 40, 90, 0.22);
            }
            .st-key-boite_connecte { border-left-color: #2e7d32; }
            .boite-titre {
                font-weight: 700;
                font-size: 1.05rem;
                color: #0b3d91;
                margin-bottom: 0.4rem;
            }
            .boite-titre i { margin-right: 0.5rem; color: #1976d2; }
            .boite-texte { color: #1a1a1a; font-size: 0.92rem; margin-bottom: 0.3rem; }
            div[data-testid="stForm"] .boite-titre { color: #0b3d91 !important; }

            /* Carte Compte : informations utilisateur, texte simple */
            .carte-compte-ligne {
                display: flex;
                align-items: center;
                gap: 0.6rem;
                padding: 0.55rem 0;
                border-bottom: 1px solid #eef1f6;
                color: #1a1a1a;
            }
            .carte-compte-ligne:last-child { border-bottom: none; }
            .carte-compte-ligne i { width: 1.2rem; color: #1976d2; text-align: center; }
            .carte-compte-label { font-weight: 600; min-width: 140px; }

            /* ===================================================== */
            /* Résultats de prédiction : carte en 2 parties           */
            /* (bandeau vert = titre, partie blanche = résultat)      */
            /* ===================================================== */
            .grille-resultats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1rem;
                margin-top: 0.5rem;
            }
            .carte-resultat {
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(15, 40, 90, 0.20);
                border: 1px solid #d6d9dc;
            }
            .carte-resultat-titre {
                background: #2e7d32;
                color: #ffffff !important;
                font-weight: 700;
                font-size: 1rem;
                padding: 0.7rem 1rem;
            }
            .carte-resultat-titre i { margin-right: 0.5rem; }
            .carte-resultat-corps {
                background: #ffffff;
                color: #1a1a1a !important;
                padding: 1.1rem 1rem;
            }
            .carte-resultat-valeur {
                font-size: 1.8rem;
                font-weight: 700;
                color: #1a1a1a !important;
            }
            .carte-resultat-message { font-size: 0.85rem; color: #555555 !important; margin-bottom: 0.4rem; }
            .carte-resultat-alerte {
                margin-top: 0.6rem;
                border-radius: 8px;
                padding: 0.5rem 0.7rem;
                font-weight: 600;
                font-size: 0.9rem;
            }
            .carte-resultat-alerte.pluie {
                background-color: #ffebee !important;
                color: #b71c1c !important;
                border-left: 5px solid #d32f2f;
            }
            .carte-resultat-alerte.sec {
                background-color: #e8f5e9 !important;
                color: #1b5e20 !important;
                border-left: 5px solid #2e7d32;
            }

            /* ===================================================== */
            /* Cartes de prédictions (page Historique)                */
            /* ===================================================== */
            .grille-predictions {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
                gap: 1rem;
                margin-top: 0.5rem;
            }
            .carte-prediction {
                display: flex;
                flex-direction: column;
                background: #ffffff;
                border-radius: 14px;
                padding: 1rem 1.1rem;
                border: 1px solid #eef1f6;
                border-left: 6px solid #1976d2;
                box-shadow: 0 6px 18px rgba(15, 40, 90, 0.20);
            }
            .carte-prediction-ligne { color: #1a1a1a; margin: 0.12rem 0; overflow-wrap: anywhere; }
            .carte-prediction-ligne i { width: 1.1rem; color: #1976d2; margin-right: 0.3rem; }
            .carte-prediction-ligne strong { color: #0b3d91; }
            .carte-prediction-ligne:last-of-type { margin-bottom: 0.5rem; }
            .carte-prediction-date {
                margin-top: auto;
                padding-top: 0.5rem;
                border-top: 1px dashed #d6d9dc;
                font-size: 0.8rem;
                color: #555555;
            }
            .carte-prediction-date i { margin-right: 0.3rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def formater_date_heure(valeur) -> str:
    """"2026-09-29 14:32:05" -> "29/09/2026 à 14:32". Si le format n'est pas
    reconnu, retourne le texte d'origine."""
    try:
        return datetime.strptime(str(valeur), "%Y-%m-%d %H:%M:%S").strftime(
            "%d/%m/%Y à %H:%M"
        )
    except ValueError:
        return str(valeur)


def _encoder_image_base64(chemin: str):
    p = Path(chemin)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode()


def logo_img_html(chemin_logo: str = "assets/logo.png", taille_px: int = 40) -> str:
    """Balise <img> du logo. Si le fichier n'existe pas, une icône (pas un
    emoji) de secours est utilisée pour que rien ne plante."""
    image_b64 = _encoder_image_base64(chemin_logo)
    if image_b64:
        return (
            f'<img src="data:image/png;base64,{image_b64}" '
            f'style="width:{taille_px}px;height:{taille_px}px;border-radius:8px;'
            f'object-fit:cover;vertical-align:middle;">'
        )
    return '<i class="fa-solid fa-cloud-sun-rain" style="font-size:1.5rem;color:#1976d2;"></i>'


def afficher_splash(chemin_logo: str = "assets/logo.png", duree_secondes: float = 1.8):
    """Écran de démarrage plein écran avec le logo, une seule fois par session."""
    import time

    image_b64 = _encoder_image_base64(chemin_logo)
    if image_b64:
        contenu_logo = (
            f'<img src="data:image/png;base64,{image_b64}" '
            'style="max-width:260px;width:60%;border-radius:24px;'
            'box-shadow:0 12px 30px rgba(0,0,0,0.35);">'
        )
    else:
        contenu_logo = (
            '<i class="fa-solid fa-cloud-sun-rain" style="font-size:5rem;color:#ffffff;"></i>'
        )

    st.markdown(
        f"""
        <style>
            .splash-overlay {{
                position: fixed; inset: 0; background: #1565C0;
                display: flex; align-items: center; justify-content: center;
                z-index: 99999;
            }}
        </style>
        <div class="splash-overlay">{contenu_logo}</div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(duree_secondes)


def afficher_logo_sidebar(chemin_logo: str = "assets/logo.png"):
    logo_html = logo_img_html(chemin_logo, taille_px=32)
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:0.5rem;padding:0.5rem 0 1rem 0;">
            {logo_html}
            <span style="font-size:1.1rem;font-weight:700;">MétéoHub</span>
        </div>
        <hr style="border-color: rgba(255,255,255,0.25);">
        """,
        unsafe_allow_html=True,
    )


def afficher_barre_navigation():
    """Bande noire avec les 3 liens de menu (Accueil, Historique, Compte).
    À appeler uniquement depuis accueil.py."""
    from nav import page_accueil, page_historique, page_compte

    with st.container(key="navbar_accueil"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link(page_accueil, label="Accueil")
        with col2:
            st.page_link(page_historique, label="Historique des prédictions")
        with col3:
            st.page_link(page_compte, label="Compte")


def afficher_barre_titre(nom_page: str, icone: str = ""):
    """Bande noire avec le nom de la page centré. `icone` est une classe
    Font Awesome complète, ex: "fa-solid fa-clock-rotate-left"."""
    balise_icone = f'<i class="{icone}"></i>' if icone else ""
    st.markdown(
        f'<div class="barre-titre-noire">{balise_icone}<span>{nom_page}</span></div>',
        unsafe_allow_html=True,
    )


def afficher_entete_logo(chemin_logo: str = "assets/logo.png"):
    """Carte 1 : logo au-dessus, "MétéoHub" et le sous-titre en dessous, centrés."""
    logo_html = logo_img_html(chemin_logo, taille_px=64)
    st.markdown(
        f"""
        <div class="entete-accueil">
            {logo_html}
            <h2 style="margin:0.6rem 0 0 0;color:#0b3d91;">MétéoHub</h2>
            <p style="margin:0.2rem 0 0 0;color:#555;">
                Prévisions &amp; suivi météo de la ville de Cotonou
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def afficher_resultat(icone: str, titre: str, valeur: str, message: str = "", alerte: dict | None = None):
    """Une carte de résultat : bandeau vert (icône + titre), partie blanche
    (grande valeur + message optionnel + encart d'alerte optionnel).
    `alerte` = {"texte": "...", "type": "pluie" | "sec"} ou None."""
    bloc_message = f'<div class="carte-resultat-message">{message}</div>' if message else ""
    bloc_alerte = (
        f'<div class="carte-resultat-alerte {alerte["type"]}">'
        f'<i class="fa-solid {"fa-cloud-showers-heavy" if alerte["type"] == "pluie" else "fa-sun"}"></i> '
        f'{alerte["texte"]}</div>'
        if alerte else ""
    )
    html = (
        '<div class="carte-resultat">'
        f'<div class="carte-resultat-titre"><i class="{icone}"></i>{titre}</div>'
        '<div class="carte-resultat-corps">'
        f'{bloc_message}'
        f'<div class="carte-resultat-valeur">{valeur}</div>'
        f'{bloc_alerte}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def afficher_footer():
    st.markdown(
        """
        <div class="footer">
            © 2026 <strong>Cosit Bénin</strong> —
            <i class="fa-solid fa-globe"></i>
            <a href="https://www.cosit.bj" target="_blank">www.cosit.bj</a> |
            <i class="fa-solid fa-phone"></i> +229 00 00 00 00 |
            <i class="fa-solid fa-envelope"></i> contact@cosit.bj
        </div>
        """,
        unsafe_allow_html=True,
    )
