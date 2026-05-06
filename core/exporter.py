"""Export léger des résultats (CSV en mémoire uniquement)."""

from __future__ import annotations

from io import BytesIO

import pandas as pd


def recommendations_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Sérialise un DataFrame de recommandations en CSV (UTF-8), sans écriture disque."""
    buf = BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue()
