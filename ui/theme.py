"""Configuration visuelle commune (Sprint 0 : base ; police Satori au Sprint suivant)."""

from __future__ import annotations

import streamlit as st


def apply_page_config() -> None:
    st.set_page_config(
        page_title="Ijora — RecoSaaS",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
