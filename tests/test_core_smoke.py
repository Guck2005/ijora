"""Fumée : le package core est importable sans Streamlit."""

from __future__ import annotations

import core


def test_core_version() -> None:
    assert core.__version__ == "0.1.0"
