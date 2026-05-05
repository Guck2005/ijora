"""Page d'accueil — squelette Sprint 0."""

from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Hello RecoSaaS")
    st.caption("Ijora — plateforme SaaS de recommandation (TP Big Data / ML)")


render()
