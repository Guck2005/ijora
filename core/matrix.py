"""Matrice pivot item × utilisateur (orientation item–item, Sprint 4)."""

from __future__ import annotations

import pandas as pd

REQUIRED = ("user_id", "item_id", "rating")


def build_pivot_matrix(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Construit la matrice de notes **items en lignes**, **utilisateurs en colonnes**.

    Les doublons (même couple user, item) sont agrégés par **moyenne**.
    """
    missing = set(REQUIRED) - set(clean_df.columns)
    if missing:
        raise KeyError(f"Colonnes manquantes : {sorted(missing)}")
    return clean_df.pivot_table(
        index="item_id",
        columns="user_id",
        values="rating",
        aggfunc="mean",
    )


def build_item_index_map(pivot: pd.DataFrame) -> dict[str, int]:
    """Mapping stable ``item_id`` (str) → indice de ligne dans la matrice pivot / similarité."""
    return {str(idx): i for i, idx in enumerate(pivot.index)}
