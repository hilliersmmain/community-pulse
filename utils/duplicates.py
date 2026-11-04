"""One definition of a duplicate record, shared by the KPI, the Duplicate Score and the cleaner."""

from __future__ import annotations

import pandas as pd


def duplicate_mask(df: pd.DataFrame) -> pd.Series:
    """Flag the rows that repeat an earlier row; the first row of each group is not flagged.

    Rows match on their Email, lower-cased and stripped of surrounding spaces, when the
    frame has an ``Email`` column. A missing email matches nothing, so those rows are never
    flagged. Without an ``Email`` column whole rows are compared. The Duplicate Records
    KPI, the Duplicate Score and ``DataCleaner.remove_duplicates`` all call this, so the
    dashboard counts exactly the rows the cleaner removes.
    """
    if "Email" not in df.columns:
        return df.duplicated(keep="first")
    emails = df["Email"]
    key = emails.astype(str).str.lower().str.strip().where(emails.notna())
    return key.duplicated(keep="first") & key.notna()
