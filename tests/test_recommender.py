"""Tests moteur de recommandation."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.recommender import compute_item_popularity, explain_recommendation, recommend_top_n


def test_compute_item_popularity() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["a", "a", "b"],
            "item_id": ["i1", "i2", "i1"],
            "rating": [1.0, 2.0, 3.0],
        }
    )
    p = compute_item_popularity(df)
    assert int(p["i1"]) == 2
    assert int(p["i2"]) == 1


def test_recommend_top_n_filters_and_excludes_self() -> None:
    sim = np.array(
        [
            [1.0, 0.9, 0.1],
            [0.9, 1.0, 0.2],
            [0.1, 0.2, 1.0],
        ],
        dtype=np.float64,
    )
    labels = pd.Index(["a", "b", "c"])
    pop = pd.Series([10, 1, 10], index=labels)
    out = recommend_top_n(sim, 0, n=5, threshold=0.05, min_popularity=5, popularity_series=pop)
    assert list(out["item_id"]) == ["c"]


def test_recommend_top_n_respects_threshold() -> None:
    sim = np.eye(3, dtype=np.float64)
    sim[0, 1] = 0.4
    sim[1, 0] = 0.4
    labels = pd.Index(["x", "y", "z"])
    pop = pd.Series([5, 5, 5], index=labels)
    out = recommend_top_n(sim, 0, n=5, threshold=0.5, min_popularity=0, popularity_series=pop)
    assert out.empty


def test_recommend_top_n_bad_index() -> None:
    sim = np.eye(2)
    pop = pd.Series([1, 1], index=pd.Index(["a", "b"]))
    with pytest.raises(IndexError):
        recommend_top_n(sim, 5, 1, 0.0, 0, pop)


def test_recommend_top_n_popularity_length() -> None:
    sim = np.eye(2)
    pop = pd.Series([1], index=pd.Index(["a"]))
    with pytest.raises(ValueError):
        recommend_top_n(sim, 0, 1, 0.0, 0, pop)


def test_explain_recommendation() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2", "u2", "u3"],
            "item_id": ["A", "B", "A", "B", "A"],
            "rating": [5.0, 4.0, 3.0, 2.0, 1.0],
        }
    )
    exp = explain_recommendation(df, "A", "B", top_k_users=3)
    assert len(exp) <= 3
    assert all("user_id" in d and "rating_target" in d for d in exp)
