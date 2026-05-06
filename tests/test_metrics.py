"""Tests métriques offline (Sprint 6)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from core.metrics import (
    coverage,
    intra_list_diversity,
    make_train_recommender,
    popularity_bias,
    precision_at_n,
    rating_bin_profile,
    train_test_split_per_user,
)


def test_train_test_split_per_user_preserves_users() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["a", "a", "a", "b", "b", "c"],
            "item_id": ["i1", "i2", "i3", "i1", "i2", "i1"],
            "rating": [1.0, 2.0, 3.0, 4.0, 5.0, 1.0],
        }
    )
    tr, te = train_test_split_per_user(df, test_ratio=0.3, seed=99)
    assert len(tr) + len(te) == len(df)
    assert set(tr["user_id"]) | set(te["user_id"]) == set(df["user_id"])


def test_train_test_split_reproducible() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["u"] * 10,
            "item_id": [f"i{k}" for k in range(10)],
            "rating": range(10),
        }
    )
    a1, b1 = train_test_split_per_user(df, seed=1)
    a2, b2 = train_test_split_per_user(df, seed=1)
    pd.testing.assert_frame_equal(a1, a2)


def test_precision_at_n_mock() -> None:
    train = pd.DataFrame(
        {
            "user_id": ["1", "1"],
            "item_id": ["A", "B"],
            "rating": [1.0, 2.0],
        }
    )
    test = pd.DataFrame(
        {
            "user_id": ["1", "1"],
            "item_id": ["A", "C"],
            "rating": [1.0, 3.0],
        }
    )

    def fn(_train: pd.DataFrame, seed: str, n: int) -> list[str]:
        if seed == "A":
            return ["C", "X"]
        return []

    p = precision_at_n(fn, train, test, n=5)
    assert p == pytest.approx(0.5)


def test_coverage_sample() -> None:
    train = pd.DataFrame(
        {
            "user_id": ["1", "2"],
            "item_id": ["A", "B"],
            "rating": [1.0, 2.0],
        }
    )

    def fn(_t: pd.DataFrame, seed: str, n: int) -> list[str]:
        return ["A"]

    c = coverage(fn, train, ["A", "B", "C"], n=2, max_targets=3, seed=0)
    assert c == pytest.approx(1.0 / 3.0)


def test_intra_list_diversity() -> None:
    sim = np.array([[1.0, 0.5, 0.0], [0.5, 1.0, 0.2], [0.0, 0.2, 1.0]], dtype=np.float64)
    mp = {"a": 0, "b": 1, "c": 2}
    d = intra_list_diversity(["a", "b", "c"], sim, mp)
    expected = 1.0 - float(np.mean([0.5, 0.0, 0.2]))
    assert d == pytest.approx(expected)


def test_popularity_bias() -> None:
    pop = pd.Series([10, 10, 1], index=["a", "b", "c"])
    b = popularity_bias(["a", "b"], pop)
    assert b > 1.0


def test_rating_bin_profile_sums_to_one_for_1_to_5() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    p = rating_bin_profile(s)
    assert abs(p.sum() - 1.0) < 1e-9


def test_make_train_recommender_small_graph() -> None:
    train = pd.DataFrame(
        {
            "user_id": ["1", "1", "2", "2"],
            "item_id": ["A", "B", "A", "C"],
            "rating": [5.0, 4.0, 3.0, 2.0],
        }
    )
    fn = make_train_recommender("cosine", 0.0, 0)
    out = fn(train, "A", 2)
    assert isinstance(out, list)


def test_train_test_split_on_realistic_fixture(realistic_ratings_small: pd.DataFrame) -> None:
    tr, te = train_test_split_per_user(realistic_ratings_small, test_ratio=0.25, seed=7)
    assert len(tr) + len(te) == len(realistic_ratings_small)
    assert set(tr["user_id"]) | set(te["user_id"]) == set(realistic_ratings_small["user_id"])

