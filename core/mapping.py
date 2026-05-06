"""Détection de colonnes et normalisation des notes (Sprint 2)."""

from __future__ import annotations

import re
from typing import Literal

import numpy as np
import pandas as pd

USER_PATTERN = re.compile(
    r"user|client|customer|utilisateur|acheteur|uid|matricule|employe|employee",
    re.IGNORECASE,
)
ITEM_PATTERN = re.compile(
    r"item|product|sku|film|movie|article|bien|formation|produit|asin",
    re.IGNORECASE,
)
RATING_PATTERN = re.compile(
    r"rating|rate|note|score|avis|stars|evaluation|eval",
    re.IGNORECASE,
)


def suggest_mapping(columns: list[str]) -> dict[str, str | None]:
    """
    Propose un mapping heuristique ``user_id`` / ``item_id`` / ``rating`` → nom de colonne source.
    Insensible à la casse ; complète avec les colonnes restantes si aucun motif ne correspond.
    """
    cols = list(columns)
    patterns = {
        "user_id": USER_PATTERN,
        "item_id": ITEM_PATTERN,
        "rating": RATING_PATTERN,
    }
    out: dict[str, str | None] = {k: None for k in patterns}
    used: set[str] = set()
    for role, pat in patterns.items():
        for c in cols:
            if c in used:
                continue
            if pat.search(str(c)):
                out[role] = c
                used.add(c)
                break
    rest = [c for c in cols if c not in used]
    for role in ("user_id", "item_id", "rating"):
        if out[role] is None and rest:
            out[role] = rest.pop(0)
    return out


def normalize_ratings(series: pd.Series, scale: Literal["0-1", "1-5"]) -> pd.Series:
    """
    Min-max sur les valeurs numériques finies ; ``scale`` cible [0,1] ou [1,5].
    Implémentation NumPy uniquement sur le vecteur numérique.
    """
    if scale not in ("0-1", "1-5"):
        raise ValueError('scale doit être "0-1" ou "1-5"')
    x = pd.to_numeric(series, errors="coerce").to_numpy(dtype=np.float64, copy=True)
    finite = np.isfinite(x)
    if not finite.any():
        return pd.Series(x, index=series.index, dtype="float64")
    xmin = float(np.nanmin(x))
    xmax = float(np.nanmax(x))
    out = np.full_like(x, np.nan, dtype=np.float64)
    if xmax <= xmin:
        fill = 0.5 if scale == "0-1" else 3.0
        out[finite] = fill
    else:
        t = (x[finite] - xmin) / (xmax - xmin)
        if scale == "0-1":
            out[finite] = t
        else:
            out[finite] = 1.0 + t * 4.0
    return pd.Series(out, index=series.index, dtype="float64")
