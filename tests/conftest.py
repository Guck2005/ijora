"""Fixtures partagées — jeu d’interactions réaliste (fichier CSV versionné)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

_FIXTURE_CSV = Path(__file__).resolve().parent / "fixtures" / "realistic_ratings.csv"


@pytest.fixture(scope="session")
def realistic_ratings_df() -> pd.DataFrame:
    """~1100 interactions, 35 users, 80 items, notes 1–5 (synthèse type MovieLens)."""
    if not _FIXTURE_CSV.is_file():
        pytest.skip(f"Fixture absente : {_FIXTURE_CSV}")
    return pd.read_csv(_FIXTURE_CSV)


@pytest.fixture(scope="session")
def realistic_ratings_small(realistic_ratings_df: pd.DataFrame) -> pd.DataFrame:
    """Sous-échantillon pour tests rapides (même distribution, moins de lignes)."""
    return realistic_ratings_df.head(400).copy()
