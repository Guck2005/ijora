"""Tests sur le jeu de données réaliste versionné (``tests/fixtures/``)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from core.eda import compute_kpis, top_k_items, top_k_users
from core.matrix import build_pivot_matrix
from core.recommender import compute_item_popularity, recommend_top_n
from core.similarity import build_similarity_matrix


def test_realistic_fixture_schema(realistic_ratings_df: pd.DataFrame) -> None:
    assert list(realistic_ratings_df.columns) == ["user_id", "item_id", "rating"]
    assert len(realistic_ratings_df) >= 500
    assert realistic_ratings_df["rating"].between(1, 5).all()


def test_realistic_fixture_user_item_counts(realistic_ratings_df: pd.DataFrame) -> None:
    nu = realistic_ratings_df["user_id"].nunique()
    ni = realistic_ratings_df["item_id"].nunique()
    assert nu >= 20
    assert ni >= 40


def test_realistic_kpis_and_topk(realistic_ratings_small: pd.DataFrame) -> None:
    k = compute_kpis(realistic_ratings_small)
    assert k["n_interactions"] == len(realistic_ratings_small)
    ti = top_k_items(realistic_ratings_small, k=5)
    tu = top_k_users(realistic_ratings_small, k=5)
    assert len(ti) == 5
    assert len(tu) == 5
    assert ti.iloc[0] >= ti.iloc[-1]
    assert tu.iloc[0] >= tu.iloc[-1]


def test_realistic_pivot_similarity_recommend_flow(realistic_ratings_small: pd.DataFrame) -> None:
    pivot = build_pivot_matrix(realistic_ratings_small)
    assert pivot.shape[0] >= 3 and pivot.shape[1] >= 3
    sim = build_similarity_matrix(pivot, "cosine")
    assert sim.shape == (pivot.shape[0], pivot.shape[0])
    assert np.allclose(sim, sim.T, atol=1e-9)
    labels = pivot.index.astype(str)
    pop = compute_item_popularity(realistic_ratings_small).reindex(labels).fillna(0).astype(int)
    out = recommend_top_n(sim, 0, n=5, threshold=0.0, min_popularity=0, popularity_series=pop)
    assert isinstance(out, pd.DataFrame)
    if not out.empty:
        assert str(labels[0]) not in set(out["item_id"].astype(str))
