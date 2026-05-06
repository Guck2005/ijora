"""Thème clair, accents verts, typographie Satoshi (Fontshare)."""

from __future__ import annotations

import streamlit as st

# Vert secondaire (sidebar, surfaces) — aligné sur ``.streamlit/config.toml``
_GREEN_ACCENT = "#166534"
_GREEN_SURFACE = "#ecfdf5"
_GREEN_MUTED = "#14532d"

_SATOSHI = "'Satoshi', 'Segoe UI', system-ui, sans-serif"
# Ne pas appliquer Satoshi sur les glyphes Material (remplace la police des icônes).
_NO_STREAMLIT_ICON = (
    ':not([data-testid="stIconMaterial"])'
    ':not([data-testid="stIconEmoji"])'
    ':not([data-testid="stSpinnerIcon"])'
)
_SIDEBAR_TEXT_NODES = (
    '[data-testid="stSidebar"] '
    '*:not([data-testid="stIconMaterial"]):not([data-testid="stSpinnerIcon"])'
)


def apply_page_config() -> None:
    st.set_page_config(
        page_title="Ijora — RecoSaaS",
        page_icon=":material/analytics:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def plotly_template() -> str:
    return "plotly_white"


# Accent charte (graphiques Plotly)
PLOTLY_MARKER = "#166534"
PLOTLY_MARKER_ALT = "#22c55e"
PLOTLY_HEATMAP_SCALE = "Greens"


def inject_global_styles() -> None:
    """Satoshi partout (surcharge Source Sans du thème Streamlit / Base Web)."""
    st.markdown(
        f"""
        <link rel="preconnect" href="https://api.fontshare.com" crossorigin>
        <link
            href="https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700&display=swap"
            rel="stylesheet"
        >
        <style>
        /* Streamlit injecte « Source Sans Pro » sur labels, radios, boutons, nav…
           Il faut cibler toute l’UI avec !important, pas seulement les <p>. */
        html, body {{
            font-family: {_SATOSHI} !important;
            font-size: 16px !important;
        }}
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stSidebar"],
        [data-testid="stToolbar"] {{
            font-family: {_SATOSHI} !important;
            font-size: 16px !important;
            color: {_GREEN_MUTED} !important;
        }}
        /* Satoshi sur l’UI texte — pas sur les glyphes Material (sinon « home » collé au titre). */
        .stApp *{_NO_STREAMLIT_ICON},
        [data-testid="stSidebar"] *{_NO_STREAMLIT_ICON},
        [data-testid="stHeader"] *{_NO_STREAMLIT_ICON},
        [data-baseweb="typo"]:not([data-testid="stIconMaterial"]):not([data-testid="stIconEmoji"]),
        [data-baseweb="typo"] *{_NO_STREAMLIT_ICON},
        label:not([data-testid="stIconMaterial"]),
        button,
        [role="radiogroup"],
        [role="radiogroup"] *{_NO_STREAMLIT_ICON},
        [data-testid="stMarkdownContainer"] *{_NO_STREAMLIT_ICON} {{
            font-family: {_SATOSHI} !important;
        }}
        /* Police livrée par Streamlit (index.css) — doit rester après Satoshi */
        [data-testid="stIconMaterial"] {{
            font-family: "Material Symbols Rounded", sans-serif !important;
            font-feature-settings: "liga" !important;
            -webkit-font-feature-settings: "liga" !important;
            font-style: normal !important;
            font-weight: 400 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            white-space: nowrap !important;
        }}
        /* Paragraphes : 16px explicite */
        p,
        .stApp p,
        [data-testid="stAppViewContainer"] p,
        [data-testid="stSidebar"] p,
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stAlert"] p,
        div[data-testid="stAlertContent"] p {{
            font-size: 16px !important;
            line-height: 1.5 !important;
        }}
        /* Code / éditeurs : garder une police à chasse fixe */
        pre, code, kbd, samp,
        .stApp pre, .stApp code,
        [data-testid="stCodeBlock"],
        [data-testid="stCodeBlock"] *,
        textarea[data-testid="st.text_area"],
        div[data-baseweb="textarea"] textarea {{
            font-family: ui-monospace, "Cascadia Code", Consolas, monospace !important;
        }}
        h1, h2, h3, h4, h5, h6,
        [data-testid="stHeader"] h1,
        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3 {{
            font-family: {_SATOSHI} !important;
            font-size: 28px !important;
            font-weight: 700 !important;
            color: {_GREEN_MUTED} !important;
            letter-spacing: -0.02em;
        }}
        [data-testid="stSidebar"] {{
            background-color: {_GREEN_SURFACE} !important;
            border-right: 1px solid #bbf7d0 !important;
        }}
        {_SIDEBAR_TEXT_NODES} {{
            color: {_GREEN_MUTED} !important;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {_GREEN_ACCENT} !important;
            border-color: {_GREEN_ACCENT} !important;
            color: #ffffff !important;
        }}
        .stButton > button[kind="secondary"] {{
            border-color: {_GREEN_ACCENT} !important;
            color: {_GREEN_ACCENT} !important;
        }}
        a {{
            color: {_GREEN_ACCENT} !important;
        }}
        [data-baseweb="slider"] [role="slider"] {{
            background-color: {_GREEN_ACCENT} !important;
        }}
        div[data-testid="stExpander"] summary {{
            color: {_GREEN_MUTED} !important;
        }}
        /* st.tabs — Satoshi sur les labels et le contenu (Base Web peut garder Source Sans). */
        .stTabs,
        [data-testid="stTabs"],
        .stTabs *{_NO_STREAMLIT_ICON},
        [data-testid="stTabs"] *{_NO_STREAMLIT_ICON},
        [role="tablist"],
        [role="tablist"] *{_NO_STREAMLIT_ICON},
        [role="tab"] {{
            font-family: {_SATOSHI} !important;
        }}
        /* Tableaux Streamlit (Glide Data Grid, classes dvn-*) : Satoshi */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"],
        [data-testid="stDataFrame"] *,
        [data-testid="stDataEditor"] *,
        [data-testid="stDataFrame"] .dvn-scroll-inner,
        [data-testid="stDataFrame"] .dvn-stack,
        [data-testid="stDataFrame"] .dvn-hidden,
        [data-testid="stDataEditor"] .dvn-scroll-inner,
        [data-testid="stDataEditor"] .dvn-stack,
        [data-testid="stDataEditor"] .dvn-hidden,
        [data-testid="stDataFrame"] [class*="dvn-"],
        [data-testid="stDataEditor"] [class*="dvn-"] {{
            font-family: {_SATOSHI} !important;
        }}
        /* Padding haut : évite le titre coupé sous le chrome. */
        [data-testid="stMainBlockContainer"] {{
            padding-top: 1.75rem !important;
        }}
        .main .block-container {{
            padding-top: 1.75rem !important;
        }}
        [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            padding-top: 0.75rem !important;
        }}
        /* Menu multipage (st.navigation) : plus d’air entre les lignes et dans chaque lien. */
        [data-testid="stSidebar"] div[data-testid="stPageLink"] {{
            margin-bottom: 0.65rem !important;
        }}
        [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
            padding: 0.8rem 1.05rem !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }}
        /* Cartes étapes (page import) : même hauteur, fond vert charte. */
        div.ijora-import-steps {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 0.25rem;
        }}
        @media (max-width: 768px) {{
            div.ijora-import-steps {{
                grid-template-columns: 1fr;
            }}
        }}
        div.ijora-import-step {{
            box-sizing: border-box;
            background-color: {_GREEN_SURFACE} !important;
            border-left: 4px solid {_GREEN_ACCENT} !important;
            border-radius: 0.5rem;
            padding: 1rem 1rem 1.25rem 1rem;
            color: {_GREEN_MUTED} !important;
            font-family: {_SATOSHI} !important;
            font-size: 16px !important;
            line-height: 1.5 !important;
            min-height: 100%;
        }}
        div.ijora-import-step strong {{
            color: {_GREEN_ACCENT} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
