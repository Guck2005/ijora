"""Métriques offline : split train/test, précision, couverture, diversité, biais."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np
import pandas as pd

from core.matrix import build_item_index_map, build_pivot_matrix
from core.recommender import compute_item_popularity, recommend_top_n
from core.similarity import build_similarity_matrix


def train_test_split_per_user(
    clean_df: pd.DataFrame,
    test_ratio: float = 0.2,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pour chaque utilisateur, déplace environ ``test_ratio`` des interactions vers le test
    (sans vider le train : au moins une ligne train si l’utilisateur a ≥ 2 interactions).
    """
    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []
    for uid, g in clean_df.groupby("user_id", sort=False):
        rs = (hash(str(uid)) ^ (seed + 17)) % (2**32 - 1)
        g = g.sample(frac=1.0, random_state=rs)
        n = len(g)
        if n <= 1:
            train_parts.append(g)
            continue
        k_test = max(1, min(n - 1, int(round(n * test_ratio))))
        test_parts.append(g.iloc[:k_test])
        train_parts.append(g.iloc[k_test:])
    train_df = pd.concat(train_parts, axis=0).reset_index(drop=True)
    test_df = pd.concat(test_parts, axis=0).reset_index(drop=True)
    return train_df, test_df


def make_train_recommender(
    metric: str,
    threshold: float,
    min_popularity: int,
) -> Callable[[pd.DataFrame, str, int], list[str]]:
    """Usine : recommandations top-N à partir du **train** uniquement (pivot + similarité)."""
    m = metric.strip().lower()
    if m == "cosinus":
        m = "cosine"

    def recommender_fn(train_df: pd.DataFrame, seed_item_id: str, n: int) -> list[str]:
        pivot = build_pivot_matrix(train_df)
        if pivot.shape[0] < 2:
            return []
        labels = pd.Index(pivot.index.astype(str))
        sid = str(seed_item_id)
        if sid not in set(labels.astype(str)):
            return []
        sim = build_similarity_matrix(pivot, m)
        idx_map = build_item_index_map(pivot)
        pop = compute_item_popularity(train_df).reindex(labels).fillna(0).astype(int)
        item_idx = int(idx_map[sid])
        out = recommend_top_n(
            sim,
            item_idx,
            n,
            threshold,
            min_popularity,
            pop,
        )
        return [str(x) for x in out["item_id"].tolist()]

    return recommender_fn


def precision_at_n(
    recommender_fn: Callable[[pd.DataFrame, str, int], list[str]],
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    n: int = 5,
) -> float:
    """
    Pour chaque ligne ``(user_id, item_id)`` du test : recommandations à partir de la
    cible ``item_id`` sur le **train** ; les autres items du même utilisateur dans le
    test sont considérés comme **pertinents**. Précision micro-moyenne des hits / ``min(n, |R|)``.
    """
    if test_df.empty:
        return 0.0
    test_users = test_df.copy()
    test_users["user_id"] = test_users["user_id"].astype(str)
    test_users["item_id"] = test_users["item_id"].astype(str)

    scores: list[float] = []
    for row in test_users.itertuples(index=False):
        u = str(row.user_id)
        seed = str(row.item_id)
        rel = set(
            test_users.loc[test_users["user_id"] == u, "item_id"].astype(str).tolist(),
        )
        rel.discard(seed)
        if not rel:
            continue
        recs = recommender_fn(train_df, seed, n)
        rec_set = set(recs)
        hits = len(rel & rec_set)
        denom = min(n, len(rel))
        scores.append(hits / denom if denom else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def coverage(
    recommender_fn: Callable[[pd.DataFrame, str, int], list[str]],
    train_df: pd.DataFrame,
    items: Sequence[str] | pd.Index,
    n: int = 5,
    max_targets: int = 200,
    seed: int = 42,
) -> float:
    """
    Proportion d’items du catalogue présents au moins une fois dans un top-N,
    en tirant au plus ``max_targets`` items cibles aléatoirement.
    """
    rng = np.random.default_rng(seed)
    catalog = [str(x) for x in items]
    if not catalog:
        return 0.0
    if len(catalog) > max_targets:
        pick = rng.choice(np.array(catalog, dtype=object), size=max_targets, replace=False)
        targets = [str(x) for x in pick.tolist()]
    else:
        targets = catalog
    seen: set[str] = set()
    for t in targets:
        try:
            recs = recommender_fn(train_df, t, n)
        except (KeyError, ValueError, IndexError):
            continue
        seen.update(recs)
    return float(len(seen)) / float(len(catalog))


def intra_list_diversity(
    recommended_items: Sequence[str],
    sim_matrix: np.ndarray,
    item_to_idx: dict[str, int],
) -> float:
    """
    ``1 - moyenne`` des similarités **hors diagonale** pour les paires d’items recommandés.
    """
    idx = [item_to_idx[str(i)] for i in recommended_items if str(i) in item_to_idx]
    if len(idx) < 2:
        return 1.0
    sub = sim_matrix[np.ix_(idx, idx)]
    triu_i, triu_j = np.triu_indices(len(idx), k=1)
    if triu_i.size == 0:
        return 1.0
    m = float(np.mean(sub[triu_i, triu_j]))
    return float(1.0 - m)


def popularity_bias(
    recommended_items: Sequence[str],
    popularity_series: pd.Series,
) -> float:
    """
    Ratio ``moyenne popularité des recommandations / moyenne globale du catalogue``.
    > 1 indique un biais vers les items populaires.
    """
    if not recommended_items:
        return 0.0
    pop = popularity_series.astype(float)
    sub = pop.reindex([str(x) for x in recommended_items]).fillna(0.0)
    gmean = float(pop.mean()) if len(pop) else 0.0
    if gmean < 1e-12:
        return 0.0
    return float(sub.mean() / gmean)


def rating_bin_profile(ratings: pd.Series) -> np.ndarray:
    """
    Pourcentages sur 5 tranches ``[1,2), [2,3), …, [5,6)`` (notes hors plage ignorées).
    """
    r = pd.to_numeric(ratings, errors="coerce").dropna()
    if r.empty:
        return np.zeros(5, dtype=np.float64)
    vals = r.to_numpy(dtype=np.float64)
    counts = np.zeros(5, dtype=np.float64)
    for lo, hi in zip([1, 2, 3, 4, 5], [2, 3, 4, 5, 6], strict=False):
        counts[int(lo) - 1] = float(np.sum((vals >= lo) & (vals < hi)))
    total = counts.sum()
    if total == 0:
        return np.zeros(5, dtype=np.float64)
    return counts / total