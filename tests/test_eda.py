"""Tests du module EDA (Sprint 3)."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import pytest

from core.eda import (
    compute_dataset_signature,
    compute_kpis,
    subsample_pivot_for_heatmap,
    top_k_items,
    top_k_users,
)
from core.ingestion import load_csv, standardize


def test_compute_kpis() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["a", "a", "b"],
            "item_id": ["i1", "i2", "i1"],
            "rating": [1.0, 2.0, 3.0],
        }
    )
    k = compute_kpis(df)
    assert k["n_users"] == 2
    assert k["n_interactions"] == 3


def test_top_k_items_users() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2", "u3"],
            "item_id": ["a", "a", "a", "b"],
            "rating": [1.0, 2.0, 3.0, 4.0],
        }
    )
    ti = top_k_items(df, k=2)
    assert ti.index[0] == "a"
    tu = top_k_users(df, k=2)
    assert tu.index[0] == "u1"


def test_subsample_pivot_shape() -> None:
    df = pd.DataFrame(
        {
            "user_id": [f"u{i % 60}" for i in range(200)],
            "item_id": [f"i{i % 40}" for i in range(200)],
            "rating": [float(i % 5 + 1) for i in range(200)],
        }
    )
    pivot, sub = subsample_pivot_for_heatmap(df, max_users=3, max_items=4)
    assert pivot.shape[0] <= 4
    assert pivot.shape[1] <= 3
    assert sub is True


def test_subsample_small_universe_not_flagged() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["a", "b"],
            "item_id": ["x", "y"],
            "rating": [1.0, 2.0],
        }
    )
    _, sub = subsample_pivot_for_heatmap(df, max_users=50, max_items=50)
    assert sub is False


def test_dataset_signature_stable() -> None:
    df = pd.DataFrame({"user_id": ["1"], "item_id": ["2"], "rating": [3.0]})
    assert compute_dataset_signature(df) == compute_dataset_signature(df.copy())


def test_eda_pipeline_books_sample_under_three_seconds() -> None:
    p = Path(__file__).resolve().parents[1] / "data" / "sample" / "books_sample.csv"
    if not p.is_file():
        pytest.skip("books_sample.csv absent")
    loaded = load_csv(p.read_bytes())
    c0, c1, c2 = loaded.columns[0], loaded.columns[1], loaded.columns[2]
    df = standardize(loaded, c0, c1, c2)
    t0 = time.perf_counter()
    compute_kpis(df)
    top_k_items(df, 10)
    top_k_users(df, 10)
    subsample_pivot_for_heatmap(df, 50, 50)
    elapsed = time.perf_counter() - t0
    assert elapsed < 3.0, f"pipeline EDA trop lent: {elapsed:.2f}s"
