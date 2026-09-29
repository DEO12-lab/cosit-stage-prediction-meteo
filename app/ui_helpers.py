"""
src/ui_helpers.py
-------------------
Style CSS et composants partagés (fond, ombres, navbar, footer, splash).

Vue d'ensemble des fonctions :
- injecter_style_global()   : CSS commun, appelé une fois dans app_1.py
- afficher_splash()         : écran de démarrage plein écran (app_1.py)
- afficher_logo_sidebar()   : logo + nom en haut de la sidebar (app_1.py)
- logo_img_html()           : génère une balise <img> du logo, réutilisable
                               partout où l'ancienne icône ⛅ apparaissait
- afficher_barre_navigation(): bande noire pleine largeur avec TOUS les
                               liens de menu, utilisée uniquement sur
                               accueil.py
- afficher_barre_titre()    : bande noire pleine largeur avec juste le nom
                               de la page centré, utilisée sur les autres
                               pages (Connexion, Utilisateurs, Dashboard,
                               Historique)
- afficher_entete_logo()    : bloc "MétéoHub" centré sous la navbar
- afficher_footer()         : pied de page NON fixe, en flux normal
"""

import base64
from pathlib import Path

import streamlit as st


def injecter_style_global():
    st.markdown(
        """
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

            /* Header transparent et réduit (au lieu de complètement masqué) :
               garde assez de place pour que le bouton d'ouverture/fermeture
               de la sidebar reste cliquable, sans afficher de bandeau blanc. */
            header[data-testid="stHeader"] {
                background: transparent;
                height: 2.2rem;
                min-height: 2.2rem;
            }
            div[data-testid="stDecoration"] { display: none; }

            /* Empêche tout scroll horizontal parasite provoqué par les
               bandes en 100vw (navbar / barre-titre) plus bas */
            html, body {
                overflow-x: hidden;
            }

            /* Conteneur de référence commun : tous les blocs restent centrés
               et utilisent le même modèle de calcul des largeurs. */
            .block-container {
                width: 100%;
                max-width: 1060px;
                box-sizing: border-box;
                margin-left: auto;
                margin-right: auto;
                padding: 0.5rem 1.5rem 2rem 1.5rem;
            }

            /* Largeur commune pour la navigation, les cartes, le formulaire
               de prédiction et le pied de page. */
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
            section[data-testid="stSidebar"] * {
                color: #ffffff !important;
            }
            [data-testid="stSidebarNav"] a {
                border-radius: 8px;
                margin: 2px 6px;
            }
            [data-testid="stSidebarNav"] a:hover {
                background: rgba(255, 255, 255, 0.15);
            }

            /* ===================================================== */
            /* Navbar noire pleine largeur (page Accueil uniquement) */
            /* ===================================================== */
            .st-key-navbar_accueil {
                width: 100%;
                background: #0a0a0a;
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
                padding: 0.3rem 0.5rem;
                margin-bottom: 1.2rem;
            }
            /* Empêche les liens de s'empiler verticalement sur mobile :
               ils restent sur UNE seule ligne, quitte à défiler horizontalement */
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
                padding: 0.35rem 0.2rem;
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
            /* Bande titre noire pleine largeur (autres pages) */
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

            /* --- En-tête "MétéoHub" centrée (page d'accueil) --- */
            .entete-accueil {
                background: #ffffff;
                border-radius: 16px;
                padding: 1.4rem 1.5rem;
                box-shadow: 0 6px 18px rgba(15, 40, 90, 0.15);
                margin-bottom: 1.2rem;
                text-align: center;
            }

            /* --- Formulaires en carte avec ombre (box-shadow) --- */
            div[data-testid="stForm"] {
                background: #ffffff;
                padding: 2rem 2rem 1rem 2rem;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(15, 40, 90, 0.18);
                border: 1px solid #eef1f6;
            }
            /* Tout texte à l'intérieur du formulaire reste sombre, même en
               thème système sombre (titres, aide, texte des options...) */
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
                padding: 0.9rem 1rem 0.6rem 1rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(15, 40, 90, 0.10);
                margin-bottom: 1rem;
            }

            /* --- Couleurs forcées, indépendantes du thème système/menu --- */
            /* Streamlit change automatiquement les couleurs de texte et des
               champs en mode sombre (téléphone en Dark, ou menu ⋮ > Dark) ;
               sans ces règles, le texte devient illisible sur nos cartes
               claires. On fige donc explicitement chaque élément. */

            /* Libellés au-dessus des champs (ex: "Vitesse maximale du vent") */
            [data-testid="stWidgetLabel"] p,
            [data-testid="stWidgetLabel"] label,
            div[data-testid="stSlider"] label,
            div[data-testid="stNumberInput"] label,
            div[data-testid="stSelectbox"] label,
            div[data-testid="stTextInput"] label {
                color: #1a1a1a !important;
            }

            /* Champs texte / nombre (la boîte de saisie elle-même) */
            div[data-baseweb="input"],
            div[data-baseweb="base-input"] {
                background-color: #ffffff !important;
            }
            div[data-baseweb="input"] input,
            div[data-baseweb="base-input"] input {
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
            button[data-testid="stNumberInputStepDown"] svg {
                fill: #1a1a1a !important;
            }

            /* Liste déroulante (Mois) */
            div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                border-color: #d6d9dc !important;
            }
            div[data-baseweb="select"] span {
                color: #1a1a1a !important;
            }

            /* Valeur affichée au-dessus des sliders (ex: "0", "50") */
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
            div[data-testid="stMetric"] {
                background: #ffffff;
                padding: 1rem 1.2rem;
                border-radius: 12px;
                box-shadow: 0 4px 14px rgba(15, 40, 90, 0.12);
            }

            /* --- Tableau avec ombre (Utilisateurs / Historique) --- */
            div[data-testid="stDataFrame"] {
                box-shadow: 0 4px 14px rgba(15, 40, 90, 0.12);
                border-radius: 12px;
                overflow: hidden;
            }

            /* --- Footer NON fixe : en flux normal, en bas du contenu --- */
            .footer {
                background: #0b3d91;
                color: #e3f2fd;
                text-align: center;
                padding: 0.9rem 1rem;
                font-size: 0.85rem;
                border-radius: 10px;
                margin-top: 2.5rem;
            }
            .footer a { color: #ffd54f; text-decoration: none; margin: 0 0.4rem; }

            /* --- Responsive (mobile / écrans étroits) --- */
            @media (max-width: 640px) {
                .block-container {
                    width: 100%;
                    max-width: 100%;
                    padding-left: 0.8rem;
                    padding-right: 0.8rem;
                }
                .st-key-navbar_accueil,
                .barre-titre-noire,
                .entete-accueil,
                div[data-testid="stForm"],
                .footer {
                    width: 100%;
                    max-width: 100%;
                }
                div[data-testid="stForm"] { padding: 1.2rem; }
                .entete-accueil { padding: 1rem; }
                .footer { font-size: 0.75rem; padding: 0.7rem; }
                .barre-titre-noire span { font-size: 1.1rem; }
            }

            /* ===================================================== */
            /* VERROUILLAGE FINAL : mode clair forcé sur le formulaire */
            /* Placé en dernier exprès : à spécificité égale, la règle */
            /* la plus bas dans la feuille l'emporte sur celles définies */
            /* plus haut ou réinjectées par Streamlit en mode sombre.   */
            /* ===================================================== */

            /* 1) Variables CSS officielles de thème Streamlit, figées
                  pour TOUT l'appli, que le mode soit Light, Dark ou System */
            :root, [data-theme="dark"], .stApp {
                --text-color: #1a1a1a !important;
                --background-color: #ffffff !important;
                --secondary-background-color: #f0f2f6 !important;
                --primary-color: #1976d2 !important;
            }

            /* 2) Le formulaire entier et tout son contenu, en dur */
            div[data-testid="stForm"],
            div[data-testid="stForm"] * {
                background-color: transparent;
                color: #1a1a1a !important;
            }
            div[data-testid="stForm"] {
                background-color: #ffffff !important;
            }
            div[data-testid="stSlider"],
            div[data-testid="stNumberInput"],
            div[data-testid="stSelectbox"],
            div[data-testid="stTextInput"] {
                background-color: #fbfcfe !important;
            }

            /* 3) Les boîtes de saisie elles-mêmes (nombre, texte, liste) */
            div[data-testid="stForm"] input,
            div[data-testid="stForm"] textarea,
            div[data-testid="stForm"] select,
            div[data-testid="stForm"] div[data-baseweb="input"],
            div[data-testid="stForm"] div[data-baseweb="base-input"],
            div[data-testid="stForm"] div[data-baseweb="select"] > div {
                background-color: #ffffff !important;
                color: #1a1a1a !important;
                -webkit-text-fill-color: #1a1a1a !important;
                border-color: #d6d9dc !important;
            }

            /* 4) Boutons +/- des champs numériques */
            div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"],
            div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"] {
                background-color: #eef1f6 !important;
                color: #1a1a1a !important;
            }
            div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"] svg,
            div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"] svg {
                fill: #1a1a1a !important;
            }

            /* 5) Bouton "Prédire" : on garde le bleu/blanc voulu, pas le
                  texte sombre imposé par la règle générale ci-dessus */
            div[data-testid="stFormSubmitButton"] button,
            div[data-testid="stFormSubmitButton"] button * {
                color: #ffffff !important;
                background-color: #1976d2 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _encoder_image_base64(chemin: str):
    """Encode une image locale en base64, pour l'intégrer directement dans du HTML."""
    p = Path(chemin)
    if not p.exists():
        return None
    return base64.b64encode(p.read_bytes()).decode()


def logo_img_html(chemin_logo: str = "assets/logo.png", taille_px: int = 40) -> str:
    """Retourne une balise <img> HTML du logo, à insérer n'importe où (titres,
    sidebar, navbar...) à la place de l'ancienne icône ⛅. Si le fichier
    n'existe pas encore, retourne un emoji de secours pour que rien ne plante."""
    image_b64 = _encoder_image_base64(chemin_logo)
    if image_b64:
        return (
            f'<img src="data:image/png;base64,{image_b64}" '
            f'style="width:{taille_px}px;height:{taille_px}px;border-radius:8px;'
            f'object-fit:cover;vertical-align:middle;">'
        )
    return "<span>🌤️</span>"


def afficher_splash(chemin_logo: str = "assets/logo.png", duree_secondes: float = 1.8):
    """Écran de démarrage plein écran avec le logo, affiché une seule fois
    par session avant le reste de l'application."""
    import time

    image_b64 = _encoder_image_base64(chemin_logo)
    if image_b64:
        contenu_logo = (
            f'<img src="data:image/png;base64,{image_b64}" '
            'style="max-width:260px;width:60%;border-radius:24px;'
            'box-shadow:0 12px 30px rgba(0,0,0,0.35);">'
        )
    else:
        contenu_logo = '<span style="font-size:5rem;">🌤️</span>'

    st.markdown(
        f"""
        <style>
            .splash-overlay {{
                position: fixed;
                inset: 0;
                background: #1565C0;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 99999;
            }}
        </style>
        <div class="splash-overlay">
            {contenu_logo}
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(duree_secondes)


def afficher_logo_sidebar(chemin_logo: str = "assets/logo.png"):
    """Logo (vraie photo) + nom de l'app en haut de la sidebar."""
    logo_html = logo_img_html(chemin_logo, taille_px=32)
    st.sidebar.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:0.5rem;
                    padding:0.5rem 0 1rem 0;">
            {logo_html}
            <span style="font-size:1.1rem;font-weight:700;">MétéoHub</span>
        </div>
        <hr style="border-color: rgba(255,255,255,0.25);">
        """,
        unsafe_allow_html=True,
    )


def afficher_barre_navigation():
    """Bande noire pleine largeur, avec box-shadow, contenant TOUS les liens
    de navigation. Reste sur une seule ligne même sur mobile (pas d'empilement
    vertical) grâce au CSS .st-key-navbar_accueil. À appeler uniquement
    depuis accueil.py."""
    from nav import (
        page_accueil,
        page_connexion,
        page_utilisateurs,
        page_historique,
        page_dashboard,
    )

    with st.container(key="navbar_accueil"):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.page_link(page_accueil, label="Accueil")
        with col2:
            st.page_link(page_connexion, label="Connexion")
        with col3:
            st.page_link(page_utilisateurs, label="Utilisateurs")
        with col4:
            st.page_link(page_historique, label="Historique")
        with col5:
            st.page_link(page_dashboard, label="Power BI")


def afficher_barre_titre(nom_page: str):
    """Bande noire pleine largeur avec box-shadow, affichant seulement le nom
    de la page, centré. À appeler en haut de chaque page autre que l'accueil
    (Connexion, Utilisateurs, Dashboard, Historique)."""
    st.markdown(
        f"""
        <div class="barre-titre-noire">
            <span>{nom_page}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def afficher_entete_logo(chemin_logo: str = "assets/logo.png"):
    """Bloc centré : logo au-dessus, "MétéoHub" et le sous-titre en dessous,
    tout au milieu de l'écran (remplace l'ancienne disposition logo+titre
    côte à côte alignés à gauche)."""
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


def afficher_footer():
    """Pied de page NON fixe : s'affiche en flux normal, à la fin du contenu
    de la page, et défile avec le reste (ne reste pas collé en bas de l'écran)."""
    st.markdown(
        """
        <div class="footer">
            © 2026 <strong>Cosit Bénin</strong> —
            <a href="https://cosit-benin.com/" target="_blank">https://cosit-benin.com/</a> 
            |RCCM RB/PNO/21 B 3066 – IFU : 3202112275670 
            📞 |07 BP 265 – Tel : (+229) 01 69 00 39 96 / 01 60 59 58 75 
            ✉️   E-mail : cositbenin2021@gmail.com 
        </div>
        """,
        unsafe_allow_html=True,
    )
