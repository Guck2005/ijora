"""Cache Streamlit pour l'évaluation offline (Sprint 6)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.metrics import coverage, make_train_recommender, precision_at_n, train_test_split_per_user


@st.cache_data(show_spinner=False)
def cached_offline_evaluation(
    clean_df: pd.DataFrame,
    metric: str,
    threshold: float,
    min_popularity: int,
    n: int,
) -> dict[str, float]:
    """
    Split train/test + précision@N + couverture sur le **train** uniquement
    (évite le data leakage sur la similarité).
    """
    print("[st.cache_data] cached_offline_evaluation — calcul métriques offline")
    train_df, test_df = train_test_split_per_user(clean_df, test_ratio=0.2, seed=42)
    fn = make_train_recommender(metric, threshold, min_popularity)
    catalog = list(clean_df["item_id"].astype(str).unique())
    return {
        "precision_at_n": precision_at_n(fn, train_df, test_df, n=n),
        "coverage": coverage(fn, train_df, catalog, n=n),
    }
