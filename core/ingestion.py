"""Ingestion CSV (RAM) et saisie manuelle — contrat sortie [user_id, item_id, rating]."""

from __future__ import annotations

import re
from io import StringIO
from typing import BinaryIO

import pandas as pd

STANDARD_COLUMNS: tuple[str, str, str] = ("user_id", "item_id", "rating")


def _read_bytes(file_buffer: BinaryIO | bytes) -> bytes:
    if isinstance(file_buffer, bytes):
        return file_buffer
    cur = file_buffer.tell()
    try:
        file_buffer.seek(0)
        return file_buffer.read()
    finally:
        file_buffer.seek(cur)


def _decode_csv_bytes(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")


def _guess_header_row(decoded: str) -> int | None:
    """Si la première ligne est essentiellement numérique (données sans en-tête), pas d'en-tête."""
    lines = [ln for ln in decoded.splitlines() if ln.strip()]
    if not lines:
        return 0
    first = lines[0].strip()
    parts = re.split(r"[\t,;]", first)
    if len(parts) < 3:
        return 0
    numeric = 0
    for p in parts:
        s = p.strip().replace(".", "", 1).replace("-", "", 1)
        if s.isdigit():
            numeric += 1
    if numeric >= 3:
        return None
    return 0


def load_csv(file_buffer: BinaryIO | bytes) -> pd.DataFrame:
    """
    Lit un CSV depuis un buffer (BytesIO, UploadedFile, bytes).
    Encodage : utf-8 puis latin-1. Séparateur : auto (sep=None, engine='python').
    """
    raw = _read_bytes(file_buffer)
    decoded = _decode_csv_bytes(raw)
    header = _guess_header_row(decoded)
    return pd.read_csv(
        StringIO(decoded),
        sep=None,
        engine="python",
        header=header,
    )


def _is_blank_cell(v: object) -> bool:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return True
    if isinstance(v, str) and not v.strip():
        return True
    return False


def build_manual_dataframe(rows: list[dict]) -> pd.DataFrame:
    """
    Construit un DataFrame à partir des lignes du st.data_editor.
    Filtre les lignes entièrement vides ; colonnes attendues : user_id, item_id, rating.
    """
    if not rows:
        return pd.DataFrame(columns=list(STANDARD_COLUMNS))
    df = pd.DataFrame(rows)
    for c in STANDARD_COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[list(STANDARD_COLUMNS)]
    mask = ~(
        df["user_id"].map(_is_blank_cell)
        & df["item_id"].map(_is_blank_cell)
        & df["rating"].map(_is_blank_cell)
    )
    return df.loc[mask].reset_index(drop=True)


def standardize(
    df: pd.DataFrame,
    user_col: str,
    item_col: str,
    rating_col: str,
) -> pd.DataFrame:
    """
    Retourne toujours un DataFrame à 3 colonnes [user_id, item_id, rating].
    """
    missing = {user_col, item_col, rating_col} - set(df.columns)
    if missing:
        raise KeyError(f"Colonnes absentes du DataFrame : {sorted(missing)}")
    out = df[[user_col, item_col, rating_col]].copy()
    out.columns = list(STANDARD_COLUMNS)
    out["rating"] = pd.to_numeric(out["rating"], errors="coerce")
    out["user_id"] = out["user_id"].astype(str)
    out["item_id"] = out["item_id"].astype(str)
    return out.reset_index(drop=True)
