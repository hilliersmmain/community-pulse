"""Data Health Metrics Module"""

import logging
import pandas as pd
import re
import streamlit as st
from datetime import datetime
from typing import Callable, Dict, Any, List, Optional, Tuple

from utils.constants import (
    HEALTH_SCORE_WEIGHT_COMPLETENESS,
    HEALTH_SCORE_WEIGHT_FORMATTING,
    HEALTH_SCORE_WEIGHT_UNIQUENESS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pluggable formatting validator registry
# ---------------------------------------------------------------------------
# Each entry is (column_name_regex, validator_callable).
# A validator receives a pd.Series of **non-null** values and returns a float
# in [0.0, 1.0] representing the fraction of values that match the expected
# format (1.0 = all valid, 0.0 = none valid).
#
# Rules:
#   - First matching pattern wins.
#   - Columns with no match are assumed valid (score 1.0) — no penalty.
#   - Patterns are matched with re.search (case-sensitive by default).
#
# To add a new validator, append or insert a (pattern, callable) tuple here.
# ---------------------------------------------------------------------------

# --- individual validator functions ----------------------------------------


def _validate_email_series(s: pd.Series) -> float:
    """Return fraction of values that look like valid e-mail addresses."""
    if s.empty:
        return 1.0
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    valid = s.apply(lambda v: bool(re.match(pattern, str(v).strip())))
    return float(valid.mean())


def _validate_date_series(s: pd.Series) -> float:
    """Return fraction of values that can be parsed as dates."""
    if s.empty:
        return 1.0
    try:
        parsed = pd.to_datetime(s, errors="coerce")
        return float(parsed.notna().mean())
    except Exception:
        return 0.0


def _validate_name_series(s: pd.Series) -> float:
    """Return fraction of values that look like human names (letters/spaces/hyphens/apostrophes)."""
    if s.empty:
        return 1.0
    pattern = r"^[a-zA-Z\s\'.-]+$"
    valid = s.apply(lambda v: bool(re.match(pattern, str(v).strip())) and len(str(v).strip()) > 0)
    return float(valid.mean())


def _validate_id_series(s: pd.Series) -> float:
    """Return fraction of values that are non-empty (numeric or non-empty string)."""
    if s.empty:
        return 1.0
    valid = s.apply(lambda v: str(v).strip() != "" if pd.notna(v) else False)
    return float(valid.mean())


# --- registry ---------------------------------------------------------------
# Patterns are matched with re.search against the column name.
# Order matters: more specific patterns should come first.

ValidatorFn = Callable[[pd.Series], float]
ValidatorRegistry = List[Tuple[str, ValidatorFn]]

FORMATTING_VALIDATORS: ValidatorRegistry = [
    # Email columns — exact "Email" / "email" or any column ending in "_email" / "_Email"
    (r"(?i)^email$|_email$", _validate_email_series),
    # Date columns — any column whose name contains "_Date", "Date_", "_date", or "date_"
    # Note: "Last_Login" does not match these patterns because it uses "Login" not "Date".
    # That is a known limitation; if you want Last_Login validated as a date you can add
    # a specific pattern like r"Last_Login" above this entry.
    (r"(?i)(^|_)date($|_)|_date$|^date_", _validate_date_series),
    # Name columns — exact "Name" or any column ending in "_Name" / "_name"
    (r"(?i)^name$|_name$", _validate_name_series),
    # ID columns — exact "ID" / "id" or any column ending in "_id" / "_ID"
    (r"(?i)^id$|_id$", _validate_id_series),
]


def _find_validator(column_name: str) -> Optional[ValidatorFn]:
    """Return the first matching validator for *column_name*, or None."""
    for pattern, fn in FORMATTING_VALIDATORS:
        if re.search(pattern, column_name):
            return fn
    return None


# ---------------------------------------------------------------------------


class DataHealthMetrics:
    """Calculate comprehensive health metrics for a dataset."""

    def __init__(self, df: pd.DataFrame):
        """Initialize the DataHealthMetrics calculator."""
        self.df = df.copy()
        self.timestamp = datetime.now()

    def calculate_completeness_score(self) -> float:
        """Calculate the completeness score based on non-null values."""
        if self.df.empty:
            return 0.0

        total_cells = self.df.size
        non_null_cells = total_cells - self.df.isna().sum().sum()

        return (non_null_cells / total_cells) * 100

    def calculate_duplicate_score(self) -> float:
        """Calculate the duplicate score based on unique records."""
        if len(self.df) == 0:
            return 100.0

        unique_rows = len(self.df.drop_duplicates())
        total_rows = len(self.df)

        return (unique_rows / total_rows) * 100

    def calculate_formatting_score(self) -> float:
        """Calculate the formatting score based on field validity.

        For each column that has a matching entry in FORMATTING_VALIDATORS,
        the validator is called on the non-null values of that column and
        returns a fraction in [0.0, 1.0].  Columns with no matching validator
        are assumed fully valid (1.0) and are excluded from the average so
        that unrecognised columns don't inflate or deflate the score.

        If the DataFrame is empty or no column has a validator, returns 100.0.
        """
        if self.df.empty:
            return 100.0

        scores = []
        for col in self.df.columns:
            validator = _find_validator(col)
            if validator is None:
                continue  # no validator → no penalty (not included in average)

            non_null = self.df[col].dropna()
            col_score = validator(non_null) * 100
            scores.append(col_score)

        return sum(scores) / len(scores) if scores else 100.0

    def _is_valid_email(self, email: str) -> bool:
        """Check if an email is in a valid format."""
        if pd.isna(email):
            return False

        email_str = str(email).strip()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email_str))

    def _is_valid_name(self, name: str) -> bool:
        """Check if a name is in a reasonable format."""
        if pd.isna(name):
            return False

        name_str = str(name).strip()
        pattern = r"^[a-zA-Z\s\'.-]+$"
        return bool(re.match(pattern, name_str)) and len(name_str) > 0

    def _count_valid_dates(self, column: str) -> int:
        """Count valid dates in a column."""
        try:
            parsed = pd.to_datetime(self.df[column], errors="coerce")
            return parsed.notna().sum()
        except Exception:
            logger.warning("Health metric date validation failed for column %s", column, exc_info=True)
            return 0

    def calculate_overall_health_score(self) -> float:
        """Calculate the overall health score as a weighted average."""
        completeness = self.calculate_completeness_score()
        uniqueness = self.calculate_duplicate_score()
        formatting = self.calculate_formatting_score()

        overall = (
            (completeness * HEALTH_SCORE_WEIGHT_COMPLETENESS)
            + (uniqueness * HEALTH_SCORE_WEIGHT_UNIQUENESS)
            + (formatting * HEALTH_SCORE_WEIGHT_FORMATTING)
        )

        return round(overall, 1)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all health metrics in a single dictionary."""
        return {
            "completeness_score": round(self.calculate_completeness_score(), 1),
            "duplicate_score": round(self.calculate_duplicate_score(), 1),
            "formatting_score": round(self.calculate_formatting_score(), 1),
            "overall_score": self.calculate_overall_health_score(),
            "timestamp": self.timestamp,
        }

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics including counts and percentages."""
        total_records = len(self.df)
        total_cells = self.df.size
        null_cells = self.df.isna().sum().sum()
        duplicates = total_records - len(self.df.drop_duplicates())

        return {
            "total_records": total_records,
            "total_cells": total_cells,
            "null_cells": null_cells,
            "non_null_cells": total_cells - null_cells,
            "duplicate_records": duplicates,
            "unique_records": total_records - duplicates,
            "completeness_score": round(self.calculate_completeness_score(), 1),
            "duplicate_score": round(self.calculate_duplicate_score(), 1),
            "formatting_score": round(self.calculate_formatting_score(), 1),
            "overall_score": self.calculate_overall_health_score(),
            "timestamp": self.timestamp,
        }


@st.cache_data(show_spinner=False)
def get_health_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Return detailed health metrics for *df*, cached by DataFrame content.

    Streamlit's default DataFrame hasher keys on shape + values, so a fresh
    cleaned DataFrame always gets its own cache entry separate from raw data.
    """
    return DataHealthMetrics(df).get_detailed_metrics()


@st.cache_data(show_spinner=False)
def get_health_score(df: pd.DataFrame) -> float:
    """Return overall health score for *df*, cached by DataFrame content."""
    return DataHealthMetrics(df).calculate_overall_health_score()
