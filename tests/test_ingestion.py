"""Tests core ingestion / standardisation (Sprint 1)."""

from __future__ import annotations

from io import BytesIO

import pandas as pd
import pytest

from core.ingestion import build_manual_dataframe, load_csv, standardize
from core.validation import validate_file_size


def test_load_csv_utf8_with_header() -> None:
    raw = "user_id,item_id,rating\n1,10,4.5\n2,20,3\n"
    df = load_csv(BytesIO(raw.encode("utf-8")))
    assert list(df.columns) == ["user_id", "item_id", "rating"]
    assert len(df) == 2


def test_load_csv_latin1() -> None:
    raw = "nom;item;rating\ncaf\xe9;10;3\n".encode("latin-1")
    df = load_csv(BytesIO(raw))
    assert len(df) == 1
    assert "rating" in df.columns.str.lower()


def test_load_csv_no_header_tab() -> None:
    raw = "1\t10\t5\t978824268\n2\t20\t3\t978302109\n"
    df = load_csv(BytesIO(raw.encode("utf-8")))
    assert len(df) == 2
    assert len(df.columns) == 4


def test_standardize() -> None:
    df = pd.DataFrame({"u": ["a", "b"], "i": [1, 2], "r": [4.0, 5.0]})
    out = standardize(df, "u", "i", "r")
    assert list(out.columns) == ["user_id", "item_id", "rating"]
    assert out["user_id"].tolist() == ["a", "b"]
    assert out["rating"].tolist() == [4.0, 5.0]


def test_standardize_missing_column() -> None:
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(KeyError):
        standardize(df, "x", "y", "z")


def test_build_manual_dataframe_filters_empty() -> None:
    rows = [
        {"user_id": 1, "item_id": 2, "rating": 3.0},
        {"user_id": None, "item_id": None, "rating": None},
    ]
    out = build_manual_dataframe(rows)
    assert len(out) == 1


def test_validate_file_size_ok() -> None:
    buf = BytesIO(b"x" * 1024)
    r = validate_file_size(buf, max_mb=50)
    assert r["ok"] is True
    assert isinstance(r["warnings"], list)


def test_validate_file_size_too_large() -> None:
    buf = BytesIO(b"0" * (2 * 1024 * 1024))
    r = validate_file_size(buf, max_mb=1)
    assert r["ok"] is False


def test_load_books_sample_under_two_seconds() -> None:
    import time
    from pathlib import Path

    p = Path(__file__).resolve().parents[1] / "data" / "sample" / "books_sample.csv"
    if not p.is_file():
        pytest.skip("books_sample.csv absent")
    t0 = time.perf_counter()
    df = load_csv(p.read_bytes())
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, f"chargement trop lent: {elapsed:.2f}s"
    assert len(df) == 100
    assert len(df.columns) == 10
