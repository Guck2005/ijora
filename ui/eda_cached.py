"""Cache Streamlit pour le bundle EDA (évite les recalculs au changement de page)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core import eda


@st.cache_data(show_spinner=False)
def load_eda_bundle(df: pd.DataFrame) -> dict:
    """
    Calcule une fois KPIs, tops et matrice heatmap pour un jeu donné.
    Streamlit déduplique via hachage du DataFrame — ne pas passer d'objets non hashables.
    """
    print("[st.cache_data] load_eda_bundle — calcul EDA (miss ou nouvelle entrée cache)")
    heat, sub = eda.subsample_pivot_for_heatmap(df, max_users=50, max_items=50)
    return {
        "kpis": eda.compute_kpis(df),
        "top_items": eda.top_k_items(df, 10),
        "top_users": eda.top_k_users(df, 10),
        "heatmap": heat,
        "heatmap_subsampled": sub,
    }
