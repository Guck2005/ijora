"""Similarités cosinus et Pearson item–item, entièrement vectorisées (NumPy)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def cosine_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Similarité cosinus ligne à ligne (ex. items) sur vecteurs de notes utilisateur.

    Les ``NaN`` sont traités comme 0 **avant** le produit scalaire (absence = neutre).
    Les lignes de norme nulle produisent une ligne/colonne de zéros ; la diagonale vaut
    1 uniquement si la norme est strictement positive.
    """
    x = np.asarray(matrix, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0)
    norms = np.linalg.norm(x, axis=1)
    safe = np.where(norms == 0.0, 1.0, norms)
    denom = np.outer(safe, safe)
    sim = (x @ x.T) / denom
    zero = norms == 0.0
    sim[zero, :] = 0.0
    sim[:, zero] = 0.0
    np.fill_diagonal(sim, np.where(norms > 0.0, 1.0, 0.0))
    return sim


def pearson_similarity_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Similarité de Pearson entre lignes : centrage **par ligne** avec ``np.nanmean``
    (sans tenir compte des NaN), puis remplacement des NaN par 0, puis cosinus.
    """
    m = np.asarray(matrix, dtype=np.float64)
    row_means = np.nanmean(m, axis=1, keepdims=True)
    centered = m - row_means
    centered = np.nan_to_num(centered, nan=0.0)
    return cosine_similarity_matrix(centered)


def build_similarity_matrix(pivot: pd.DataFrame, metric: str) -> np.ndarray:
    """
    Calcule la matrice de similarité **items × items** alignée sur ``pivot.index``.

    ``metric`` : ``"cosine"`` / ``"cosinus"`` ou ``"pearson"``.
    """
    m = metric.strip().lower()
    mat = pivot.to_numpy(dtype=np.float64)
    if m in ("cosine", "cosinus"):
        return cosine_similarity_matrix(mat)
    if m == "pearson":
        return pearson_similarity_matrix(mat)
    raise ValueError(f"Métrique inconnue : {metric!r} (attendu cosinus ou pearson).")
