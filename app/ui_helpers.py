"""
app/ui_helpers.py

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
                background: transparent !important;
                height: 2.5rem;
                min-height: 2.5rem;
                position: relative !important;
                z-index: 9999 !important;
            }

            /* Le bouton d'ouverture/fermeture de la sidebar reste toujours accessible */
            header[data-testid="stHeader"] button {
                position: relative;
                z-index: 10000 !important;
            }
            div[data-testid="stDecoration"] { display: none; }

            /* Empêche tout scroll horizontal parasite provoqué par les
               bandes en 100vw (navbar / barre-titre) plus bas */
            html, body {
                overflow-x: hidden;
            }

            .block-container {
                width: 100%;
                max-width: 1100px;
                margin: 0 auto;
                padding-top: 0.5rem;
                padding-bottom: 2rem;
                padding-left: clamp(0.75rem, 3vw, 2rem);
                padding-right: clamp(0.75rem, 3vw, 2rem);
                box-sizing: border-box;
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

            /* 
               NAVBAR MÉTÉOHUB — RESPONSIVE
                */

            .st-key-navbar_accueil {
                width: 100%;
                background: #0a0a0a;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
                border-radius: 10px;
                padding: 0.35rem 0.5rem;
                margin: 0 auto 1.2rem auto;
                box-sizing: border-box;
            }

            .st-key-navbar_accueil div[data-testid="stHorizontalBlock"] {
                width: 100%;
                max-width: 1100px;
                margin: 0 auto;
                display: flex;
                flex-wrap: nowrap !important;
                align-items: center;
                justify-content: center;
                gap: 0.2rem;
            }

            .st-key-navbar_accueil div[data-testid="stPageLink"] {
                flex: 1 1 0;
                min-width: 0;
                background: transparent;
                box-shadow: none;
                padding: 0.45rem 0.25rem;
                border-radius: 8px;
                box-sizing: border-box;
                text-align: center;
            }

            .st-key-navbar_accueil div[data-testid="stPageLink"] a {
                width: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
            }

            .st-key-navbar_accueil div[data-testid="stPageLink"] a p,
            .st-key-navbar_accueil div[data-testid="stPageLink"] a span {
                color: #ffffff !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                white-space: nowrap !important;
            }

            .st-key-navbar_accueil div[data-testid="stPageLink"]:hover {
                background: rgba(255, 255, 255, 0.12);
            }

            /*  */
            /* Bande titre noire pleine largeur (autres pages) */
            /*  */
            .barre-titre-noire {
                position: relative;
                left: 50%;
                right: 50%;
                margin-left: -50vw;
                margin-right: -50vw;
                width: 100vw;
                background: #0a0a0a;
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
                width: 100%;
                max-width: 1000px;
                margin: 0 auto 1.5rem auto;
                background: #ffffff;
                border-radius: 16px;
                padding: clamp(1rem, 3vw, 1.5rem);
                box-shadow: 0 6px 18px rgba(15, 40, 90, 0.15);
                text-align: center;
                box-sizing: border-box;
            }

            /*  Formulaires en carte avec ombre (box-shadow)  */
            div[data-testid="stForm"] {
                width: 100%;
                max-width: 1000px;
                margin: 0 auto;
                background: #ffffff;
                padding: clamp(1rem, 4vw, 2rem);
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(15, 40, 90, 0.18);
                border: 1px solid #eef1f6;
                box-sizing: border-box;
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

            /*  Footer NON fixe : en flux normal, en bas du contenu  */
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

            /* 
               RESPONSIVE — TABLETTES
                */
            @media (max-width: 900px) {
                .block-container {
                    max-width: 100%;
                }

                .st-key-navbar_accueil {
                    border-radius: 8px;
                    padding: 0.3rem;
                }

                .st-key-navbar_accueil div[data-testid="stPageLink"] {
                    padding: 0.4rem 0.15rem;
                }

                .st-key-navbar_accueil div[data-testid="stPageLink"] a p,
                .st-key-navbar_accueil div[data-testid="stPageLink"] a span {
                    font-size: 0.8rem !important;
                }
            }

            /* 
               RESPONSIVE — TÉLÉPHONES
                */
            @media (max-width: 640px) {
                .block-container {
                    width: 100%;
                    max-width: 100%;
                    padding-left: 0.65rem;
                    padding-right: 0.65rem;
                }

                /* Navbar : une seule ligne, défilement horizontal si nécessaire */
                .st-key-navbar_accueil {
                    width: 100%;
                    margin-bottom: 1rem;
                    border-radius: 8px;
                    padding: 0.25rem;
                }

                .st-key-navbar_accueil div[data-testid="stHorizontalBlock"] {
                    overflow-x: auto;
                    overflow-y: hidden;
                    justify-content: flex-start;
                    gap: 0.15rem;
                    scrollbar-width: thin;
                }

                .st-key-navbar_accueil div[data-testid="stPageLink"] {
                    flex: 0 0 auto;
                    min-width: 82px;
                    padding: 0.4rem 0.25rem;
                }

                .st-key-navbar_accueil div[data-testid="stPageLink"] a p,
                .st-key-navbar_accueil div[data-testid="stPageLink"] a span {
                    font-size: 0.75rem !important;
                }

                /* Carte MétéoHub */
                .entete-accueil {
                    width: 100%;
                    padding: 1rem 0.75rem;
                    border-radius: 14px;
                    margin-bottom: 1rem;
                }

                .entete-accueil h2 {
                    font-size: 1.35rem !important;
                }

                .entete-accueil p {
                    font-size: 0.85rem !important;
                }

                /* Titre */
                h1 {
                    font-size: 1.45rem !important;
                    line-height: 1.25 !important;
                }

                /* Formulaire */
                div[data-testid="stForm"] {
                    width: 100%;
                    padding: 1rem 0.8rem;
                    border-radius: 14px;
                    box-shadow: 0 5px 16px rgba(15, 40, 90, 0.15);
                }

                /* Champs */
                div[data-testid="stSlider"],
                div[data-testid="stNumberInput"],
                div[data-testid="stSelectbox"],
                div[data-testid="stTextInput"] {
                    padding: 0.7rem 0.75rem 0.5rem 0.75rem;
                    margin-bottom: 0.75rem;
                }

                /* Footer */
                .footer {
                    font-size: 0.75rem;
                    padding: 0.7rem;
                }

                .barre-titre-noire span {
                    font-size: 1.1rem;
                }
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
            st.page_link(page_accueil, label="🏠 Accueil")
        with col2:
            st.page_link(page_connexion, label="🔐 Connexion")
        with col3:
            st.page_link(page_utilisateurs, label="👥 Utilisateurs")
        with col4:
            st.page_link(page_historique, label="🕘 Historique")
        with col5:
            st.page_link(page_dashboard, label="📊 Power BI")


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
            <h2 style="margin:0.6rem 0 0 0;">MétéoHub</h2>
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
            <a href="https://www.cosit.bj" target="_blank">www.cosit.bj</a> |
            📞 +229 00 00 00 00 |
            ✉️ contact@cosit.bj
        </div>
        """,
        unsafe_allow_html=True,
    )



# Variante de repli (NON utilisée par défaut) pour les bandes noires

# Si la technique 100vw (dans .st-key-navbar_accueil et .barre-titre-noire,
# plus haut) provoque un décalage horizontal ou une barre de défilement
# parasite sur certains navigateurs/téléphones, remplace dans ces deux
# blocs CSS les 4 lignes :
#
#     position: relative;
#     left: 50%;
#     right: 50%;
#     margin-left: -50vw;
#     margin-right: -50vw;
#     width: 100vw;
#
# par une seule ligne :
#
#     width: 100%;
#
# La bande ne débordera plus jusqu'aux bords de l'écran (elle s'arrêtera
# à la largeur du contenu, ~1000px max), mais elle reste garantie
# stable sur tous les navigateurs, sans aucun risque de scroll parasite.
