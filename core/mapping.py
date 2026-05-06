"""Détection de colonnes (Sprint 2)."""

from __future__ import annotations

import re

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
