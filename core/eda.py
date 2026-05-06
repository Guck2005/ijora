"""Exploration de données (EDA) — KPIs, distributions, sous-échantillon heatmap."""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from core.validation import quality_report


def compute_dataset_signature(df: pd.DataFrame) -> str:
    """Empreinte stable du contenu (pour invalidation de cache UI)."""
    h = hashlib.sha256()
    h.update(str(len(df)).encode())
    h.update(pd.util.hash_pandas_object(df, index=True).values.tobytes())
    return h.hexdigest()


def compute_kpis(clean_df: pd.DataFrame) -> dict[str, Any]:
    """
    Indicateurs agrégés pour le tableau de bord EDA.
    Repose sur ``quality_report`` (contrat ``[user_id, item_id, rating]``).
    """
    q = quality_report(clean_df)
    return {
        "n_users": q["n_users"],
        "n_items": q["n_items"],
        "n_interactions": q["n_interactions"],
        "sparsity": q["sparsity"],
        "n_duplicates": q["n_duplicates"],
        "rating_mean": q["rating_mean"],
        "rating_min": q["rating_min"],
        "rating_max": q["rating_max"],
        "pct_missing": q["pct_missing"],
    }


def top_k_items(clean_df: pd.DataFrame, k: int = 10) -> pd.Series:
    """Top ``k`` items par nombre d'interactions (``value_counts``)."""
    return clean_df["item_id"].value_counts().head(k)


def top_k_users(clean_df: pd.DataFrame, k: int = 10) -> pd.Series:
    """Top ``k`` utilisateurs par nombre d'interactions."""
    return clean_df["user_id"].value_counts().head(k)


def subsample_pivot_for_heatmap(
    clean_df: pd.DataFrame,
    max_users: int = 50,
    max_items: int = 50,
) -> tuple[pd.DataFrame, bool]:
    """
    Matrice item × user (notes moyennes) restreinte aux **top** utilisateurs et items
    par volume d'interactions — évite les matrices complètes illisibles dans le navigateur.

    Retourne ``(pivot, subsampled)`` où ``subsampled`` indique si le jeu complet dépasse
    les plafonds ``max_users`` / ``max_items``.
    """
    required = {"user_id", "item_id", "rating"}
    if not required.issubset(clean_df.columns):
        missing = required - set(clean_df.columns)
        raise KeyError(f"Colonnes manquantes : {sorted(missing)}")
    df = clean_df[list(required)].copy()
    n_u = int(df["user_id"].nunique(dropna=True))
    n_i = int(df["item_id"].nunique(dropna=True))
    ku = min(max_users, max(1, n_u))
    ki = min(max_items, max(1, n_i))
    top_u = df["user_id"].value_counts().nlargest(ku).index
    top_i = df["item_id"].value_counts().nlargest(ki).index
    sub = df[df["user_id"].isin(top_u) & df["item_id"].isin(top_i)]
    pivot = sub.pivot_table(
        index="item_id",
        columns="user_id",
        values="rating",
        aggfunc="mean",
    )
    subsampled = (n_u > max_users) or (n_i > max_items)
    return pivot, subsampled
