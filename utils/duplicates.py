"""One definition of a duplicate record, shared by the KPI, the Duplicate Score and the cleaner."""

from __future__ import annotations

import pandas as pd


def duplicate_mask(df: pd.DataFrame) -> pd.Series:
    """Flag the rows that repeat an earlier row; the first row of each group is not flagged.

    Rows match on their Email, lower-cased and stripped of surrounding spaces, when the
    frame has an ``Email`` column. A missing or blank email matches nothing, so those rows
    are never flagged. Without an ``Email`` column whole rows are compared. The Duplicate
    Records KPI, the Duplicate Score and ``DataCleaner.remove_duplicates`` all call this, so
    on the same frame they agree. The full pipeline runs Fix Email Formats first, which can
    repair an address into a match, so it can remove more rows than the raw KPI counts
    (docs/KPI_DEFINITIONS.md).
    """
    if "Email" not in df.columns:
        return df.duplicated(keep="first")
    emails = df["Email"]
    key = emails.astype(str).str.lower().str.strip().where(emails.notna())
    key = key.where(key != "")
    return key.duplicated(keep="first") & key.notna()
