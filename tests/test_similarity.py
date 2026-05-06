"""Tests similarité cosinus / Pearson (Sprint 4)."""

from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from core.ingestion import load_csv, standardize
from core.matrix import build_pivot_matrix
from core.similarity import (
    build_similarity_matrix,
    cosine_similarity_matrix,
    pearson_similarity_matrix,
)


def test_cosine_trivial_3x3_six_decimals() -> None:
    """TEST-41 : matrice 3×3, valeurs cosinus vérifiées à la main."""
    m = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )
    s = cosine_similarity_matrix(m)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    assert s[0, 1] == pytest.approx(0.0, abs=1e-6)
    assert s[0, 2] == pytest.approx(inv_sqrt2, abs=1e-6)
    assert s[1, 2] == pytest.approx(inv_sqrt2, abs=1e-6)
    assert s[0, 0] == pytest.approx(1.0, abs=1e-6)
    assert s[1, 1] == pytest.approx(1.0, abs=1e-6)
    assert s[2, 2] == pytest.approx(1.0, abs=1e-6)


def test_pearson_insensitive_generous_user_column() -> None:
    """TEST-42 : colonne « généreuse » — Pearson ≈ 1 entre items parallèles, cosinus < 1."""
    m = np.array(
        [
            [1.0, 12.0, 3.0],
            [2.0, 13.0, 4.0],
        ],
        dtype=np.float64,
    )
    cos = cosine_similarity_matrix(m)
    pea = pearson_similarity_matrix(m)
    assert pea[0, 1] == pytest.approx(1.0, abs=1e-5)
    assert cos[0, 1] < 0.999


def test_symmetry_cosine_and_pearson() -> None:
    """TEST-43 : S == S.T."""
    rng = np.random.default_rng(42)
    x = rng.normal(size=(8, 12))
    x[rng.random(x.shape) < 0.15] = np.nan
    for fn in (cosine_similarity_matrix, pearson_similarity_matrix):
        s = fn(x)
        assert np.allclose(s, s.T, atol=1e-10)


def test_diagonal_one_for_nonzero_norm() -> None:
    """TEST-44 : diagonale 1 pour lignes non nulles."""
    m = np.array([[1.0, 2.0], [3.0, 4.0], [0.5, 1.0]], dtype=np.float64)
    s = cosine_similarity_matrix(m)
    assert s[0, 0] == pytest.approx(1.0)
    assert s[1, 1] == pytest.approx(1.0)
    assert s[2, 2] == pytest.approx(1.0)


def test_build_similarity_matrix_dispatcher() -> None:
    p = pd.DataFrame([[1.0, 0.0], [0.0, 1.0]], index=["a", "b"], columns=["u1", "u2"])
    c = build_similarity_matrix(p, "cosinus")
    assert c.shape == (2, 2)
    p2 = build_similarity_matrix(p, "pearson")
    assert p2.shape == (2, 2)


def test_unknown_metric_raises() -> None:
    p = pd.DataFrame([[1.0]], index=["a"], columns=["u1"])
    with pytest.raises(ValueError):
        build_similarity_matrix(p, "jaccard")


def test_build_pivot_matrix() -> None:
    df = pd.DataFrame(
        {
            "user_id": ["u1", "u1", "u2"],
            "item_id": ["i1", "i2", "i1"],
            "rating": [1.0, 2.0, 3.0],
        }
    )
    pv = build_pivot_matrix(df)
    assert pv.shape == (2, 2)
    assert float(pv.loc["i1", "u1"]) == pytest.approx(1.0)


def test_similarity_books_sample_under_two_seconds() -> None:
    p = Path(__file__).resolve().parents[1] / "data" / "sample" / "books_sample.csv"
    if not p.is_file():
        pytest.skip("books_sample.csv absent")
    loaded = load_csv(p.read_bytes())
    c0, c1, c2 = loaded.columns[0], loaded.columns[1], loaded.columns[2]
    df = standardize(loaded, c0, c1, c2)
    pivot = build_pivot_matrix(df)
    t0 = time.perf_counter()
    build_similarity_matrix(pivot, "cosine")
    build_similarity_matrix(pivot, "pearson")
    elapsed = time.perf_counter() - t0
    assert elapsed < 2.0, f"similarité trop lente: {elapsed:.2f}s"


def test_no_forbidden_ml_imports_in_similarity_module() -> None:
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parents[1] / "core" / "similarity.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    banned = {"sklearn", "scipy", "surprise", "implicit"}
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = (alias.name or "").split(".")[0]
                if base in banned:
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = (node.module or "").split(".")[0]
            if base in banned:
                found.append(node.module or "")
    assert not found, f"imports interdits détectés : {found}"
