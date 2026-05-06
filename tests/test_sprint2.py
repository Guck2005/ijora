"""Tests Sprint 2 — mapping, validation des notes, rapport qualité."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import pytest

from core.ingestion import load_csv, standardize
from core.mapping import suggest_mapping
from core.validation import quality_report, validate_rating_column


def test_suggest_mapping_movielens() -> None:
    s = suggest_mapping(["user_id", "item_id", "rating", "ts"])
    assert s["user_id"] == "user_id"
    assert s["item_id"] == "item_id"
    assert s["rating"] == "rating"


def test_suggest_mapping_ecommerce() -> None:
    s = suggest_mapping(["CustomerID", "ProductID", "stars"])
    assert s["user_id"] == "CustomerID"
    assert s["item_id"] == "ProductID"
    assert s["rating"] == "stars"


def test_suggest_mapping_rh() -> None:
    s = suggest_mapping(["Matricule", "FormationID", "Score_evaluation"])
    assert s["user_id"] == "Matricule"
    assert s["item_id"] == "FormationID"
    assert s["rating"] == "Score_evaluation"


def test_validate_rating_numeric_ok() -> None:
    s = pd.Series([1.0, 2.5, 3, "4"])
    r = validate_rating_column(s)
    assert r["ok"] is True
    assert r["n_invalid"] == 0


def test_validate_rating_invalid_strings() -> None:
    s = pd.Series([1.0, "bad", "", None])
    r = validate_rating_column(s)
    assert r["ok"] is False
    assert 1 in r["invalid_indices"]


def test_quality_report_basic() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["a", "a", "b"],
            "item_id": ["i1", "i2", "i1"],
            "rating": [1.0, 2.0, 3.0],
        }
    )
    rep = quality_report(df)
    assert rep["n_users"] == 2
    assert rep["n_items"] == 2
    assert rep["n_interactions"] == 3
    assert rep["n_duplicates"] == 0
    assert rep["sparsity"] == pytest.approx(1.0 - 3.0 / 4.0)


def test_quality_report_missing_key() -> None:
    with pytest.raises(KeyError):
        quality_report(pd.DataFrame({"a": [1]}))


def test_quality_report_books_sample_under_one_second() -> None:
    p = Path(__file__).resolve().parents[1] / "data" / "sample" / "books_sample.csv"
    if not p.is_file():
        pytest.skip("books_sample.csv absent")
    loaded = load_csv(p.read_bytes())
    mapped = standardize(loaded, loaded.columns[0], loaded.columns[1], loaded.columns[2])
    t0 = time.perf_counter()
    quality_report(mapped)
    elapsed = time.perf_counter() - t0
    assert elapsed < 1.0, f"quality_report trop lent: {elapsed:.2f}s"


