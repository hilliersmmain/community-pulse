"""Centralized data file IO with cache-aware helpers."""

from __future__ import annotations

import os
import pandas as pd
import streamlit as st

from utils.constants import DATA_DIR


def ensure_data_dir() -> None:
    """Ensure the project data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)


@st.cache_data(show_spinner=False)
def _read_csv_cached(path: str, mtime: float) -> pd.DataFrame:
    """Read CSV with cache invalidated by file modified time."""
    _ = mtime
    return pd.read_csv(path)


def load_csv(path: str) -> pd.DataFrame:
    """Load CSV from disk using mtime-keyed caching."""
    mtime = os.path.getmtime(path)
    return _read_csv_cached(path, mtime)


def save_csv(df: pd.DataFrame, path: str) -> None:
    """Persist CSV and clear stale read cache."""
    ensure_data_dir()
    df.to_csv(path, index=False)
    _read_csv_cached.clear()
