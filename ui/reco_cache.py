"""Cache Streamlit pour la matrice de similarité (Sprint 4 — ALGO-45)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.similarity import build_similarity_matrix


@st.cache_data(show_spinner=False)
def cached_similarity_matrix(
    file_hash: str | None,
    dataset_sig: str | None,
    metric: str,
    pivot: pd.DataFrame,
) -> pd.DataFrame:
    """
    Recalcule uniquement si la clé (fichier / signature / métrique / pivot) change.

    Le ``DataFrame`` pivot est haché par Streamlit ; ``file_hash`` et ``dataset_sig``
    renforcent la clé lorsque le contenu pivot est identique mais la session a changé.
    """
    fh = (file_hash or "")[:8]
    ds = (dataset_sig or "")[:8]
    print(
        "[st.cache_data] cached_similarity_matrix — calcul "
        f"(hash={fh!r}, sig={ds!r}, metric={metric})"
    )
    arr = build_similarity_matrix(pivot, metric)
    return pd.DataFrame(arr, index=pivot.index, columns=pivot.index)
