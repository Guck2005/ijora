"""Recommandation item–item : top-N et explications (TP)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compute_item_popularity(clean_df: pd.DataFrame) -> pd.Series:
    """Nombre d'interactions par ``item_id`` (série indexée par item)."""
    s = clean_df.groupby("item_id", observed=True).size()
    s.name = "popularity"
    return s.astype(int)


def recommend_top_n(
    sim_matrix: np.ndarray,
    item_index: int,
    n: int,
    threshold: float,
    min_popularity: int,
    popularity_series: pd.Series,
) -> pd.DataFrame:
    """
    Recommande jusqu'à ``n`` items à partir de la ligne ``item_index`` de ``sim_matrix``.

    ``popularity_series`` doit partager le même ordre d'index que les lignes/colonnes
    de ``sim_matrix`` (un score de popularité par ligne).

    Colonnes retournées : ``item_id``, ``similarity_score``, ``popularity``.
    """
    if sim_matrix.ndim != 2 or sim_matrix.shape[0] != sim_matrix.shape[1]:
        raise ValueError("sim_matrix doit être carrée (items × items).")
    n_items = sim_matrix.shape[0]
    if not (0 <= item_index < n_items):
        raise IndexError(f"item_index hors bornes : {item_index} (n={n_items}).")
    if len(popularity_series) != n_items:
        raise ValueError(
            f"popularity_series ({len(popularity_series)}) "
            f"ne correspond pas à sim_matrix ({n_items})."
        )

    item_ids = popularity_series.index.astype(str)
    scores = sim_matrix[item_index].astype(np.float64, copy=True)
    pop = popularity_series.to_numpy(dtype=np.int64, copy=False)

    mask = (scores >= threshold) & (pop >= min_popularity)
    mask[item_index] = False

    eligible = np.flatnonzero(mask)
    if eligible.size == 0:
        return pd.DataFrame(columns=["item_id", "similarity_score", "popularity"])

    order = eligible[np.argsort(-scores[eligible], kind="stable")]
    top_idx = order[: max(0, min(n, order.size))]

    rows: list[dict[str, Any]] = [
        {
            "item_id": str(item_ids[i]),
            "similarity_score": float(scores[i]),
            "popularity": int(pop[i]),
        }
        for i in top_idx
    ]
    return pd.DataFrame(rows)


def explain_recommendation(
    clean_df: pd.DataFrame,
    target_item: str,
    recommended_item: str,
    top_k_users: int = 3,
) -> list[dict[str, Any]]:
    """
    Jusqu'à ``top_k_users`` utilisateurs ayant noté **à la fois** la cible et l'item recommandé.

    Chaque entrée : ``user_id``, ``rating_target``, ``rating_recommended``.
    """
    work = clean_df[["user_id", "item_id", "rating"]].copy()
    work["user_id"] = work["user_id"].astype(str)
    work["item_id"] = work["item_id"].astype(str)
    t, r = str(target_item), str(recommended_item)

    u_t = work.loc[work["item_id"] == t, ["user_id", "rating"]].rename(
        columns={"rating": "rating_target"},
    )
    u_r = work.loc[work["item_id"] == r, ["user_id", "rating"]].rename(
        columns={"rating": "rating_recommended"},
    )
    merged = u_t.merge(u_r, on="user_id", how="inner").dropna()
    merged = merged.sort_values("user_id").head(top_k_users)

    out: list[dict[str, Any]] = []
    for row in merged.itertuples(index=False):
        out.append(
            {
                "user_id": str(row.user_id),
                "rating_target": float(row.rating_target),
                "rating_recommended": float(row.rating_recommended),
            }
        )
    return out
