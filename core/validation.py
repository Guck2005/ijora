"""Validation taille fichier, notes et rapport qualité (Sprint 1+)."""

from __future__ import annotations

from typing import Any, BinaryIO

import pandas as pd


def _byte_size(file: BinaryIO) -> int:
    if hasattr(file, "getvalue"):
        return len(file.getvalue())
    pos = file.tell()
    try:
        file.seek(0, 2)
        return int(file.tell())
    finally:
        file.seek(pos)


def validate_file_size(file: BinaryIO, max_mb: float = 50) -> dict[str, Any]:
    """
    Contrôle la taille d'un fichier en mémoire (UploadedFile, BytesIO).

    Retourne ``{ok: bool, warnings: list[str]}``.
    """
    warnings: list[str] = []
    size = _byte_size(file)
    max_bytes = int(max_mb * 1024 * 1024)
    if size > max_bytes:
        return {
            "ok": False,
            "warnings": [
                f"Fichier trop volumineux (~{size / (1024**2):.1f} Mo) : "
                f"plafond autorisé {max_mb} Mo."
            ],
        }
    if size > 40 * 1024 * 1024:
        warnings.append("Fichier volumineux (> 40 Mo) : le traitement peut être lent.")
    return {"ok": True, "warnings": warnings}


def validate_rating_column(series: pd.Series) -> dict[str, Any]:
    """
    Contrôle la numéricité des notes via ``pd.to_numeric(..., errors="coerce")``.

    Retourne ``ok``, ``n_invalid``, ``invalid_indices`` (positions 0..n-1 pour ``iloc``), ``dtype``.
    Les cellules vides / NaN ne sont pas comptées comme « non numériques ».
    """
    s = series.reset_index(drop=True)
    coerced = pd.to_numeric(s, errors="coerce")
    strv = s.astype(str).str.strip()
    missing = s.isna() | strv.eq("") | strv.str.lower().isin(("nan", "<na>", "none"))
    invalid_mask = coerced.isna() & ~missing
    invalid_idx = [int(i) for i, v in enumerate(invalid_mask) if v]
    return {
        "ok": len(invalid_idx) == 0,
        "n_invalid": len(invalid_idx),
        "invalid_indices": invalid_idx,
        "dtype": str(series.dtype),
    }


def quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """
    Indicateurs sur un jeu au format ``[user_id, item_id, rating]`` (noms exacts).
    """
    required = {"user_id", "item_id", "rating"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise KeyError(f"Colonnes manquantes : {sorted(missing)}")
    work = df[list(required)].copy()
    n_cells = work.shape[0] * work.shape[1]
    pct_missing = float(100.0 * work.isna().to_numpy().sum() / n_cells) if n_cells else 0.0
    n_duplicates = int(work.duplicated().sum())
    n_interactions = int(len(work))
    n_users = int(work["user_id"].nunique(dropna=True))
    n_items = int(work["item_id"].nunique(dropna=True))
    r = pd.to_numeric(work["rating"], errors="coerce")
    rating_min = float(r.min()) if r.notna().any() else float("nan")
    rating_max = float(r.max()) if r.notna().any() else float("nan")
    rating_mean = float(r.mean()) if r.notna().any() else float("nan")
    denom = n_users * n_items
    sparsity = float(1.0 - (n_interactions / denom)) if denom > 0 else 0.0
    return {
        "n_users": n_users,
        "n_items": n_items,
        "n_interactions": n_interactions,
        "pct_missing": pct_missing,
        "n_duplicates": n_duplicates,
        "rating_min": rating_min,
        "rating_max": rating_max,
        "rating_mean": rating_mean,
        "sparsity": sparsity,
    }
