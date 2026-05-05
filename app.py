"""Point d'entrée Streamlit — routeur vers les pages (ui/pages)."""

from __future__ import annotations

import streamlit as st

from ui import theme


def main() -> None:
    theme.apply_page_config()
    pages = [
        st.Page("ui/pages/home.py", title="Accueil", icon="🏠", default=True),
    ]
    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
