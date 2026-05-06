"""Tests export CSV."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from core.exporter import recommendations_to_csv_bytes


def test_recommendations_to_csv_bytes_roundtrip() -> None:
    df = pd.DataFrame(
        {"item_id": ["a", "b"], "similarity_score": [0.9, 0.8], "popularity": [3, 2]},
    )
    raw = recommendations_to_csv_bytes(df)
    back = pd.read_csv(BytesIO(raw))
    assert list(back.columns) == list(df.columns)
    assert len(back) == 2
