"""Point d'entrée Streamlit — routeur vers les pages (ui/pages)."""

from __future__ import annotations

import streamlit as st

from ui import theme


def main() -> None:
    theme.apply_page_config()
    theme.inject_global_styles()

    with st.sidebar:
        st.caption(
            "Vos données ne sont pas sauvegardées sur le serveur ; elles restent uniquement "
            "en mémoire pour cette session (aucune écriture disque)."
        )

    pages = [
        st.Page(
            "ui/pages/01_import.py",
            title="Accueil & importation",
            icon=":material/home:",
            default=True,
        ),
        st.Page("ui/pages/03_exploration.py", title="Exploration", icon=":material/query_stats:"),
        st.Page(
            "ui/pages/06_parametres_avances.py",
            title="Métrique de similarité",
            icon=":material/tune:",
        ),
        st.Page(
            "ui/pages/04_recommandation.py",
            title="Recommandation",
            icon=":material/model_training:",
        ),
    ]
    nav = st.navigation(pages)

    with st.sidebar:
        st.divider()
        st.caption("Développé par GUENANON Ulysse")

    nav.run()


if __name__ == "__main__":
    main()
