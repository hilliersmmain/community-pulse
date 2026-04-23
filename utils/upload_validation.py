"""Validation helpers for uploaded CSV datasets."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from utils.constants import MAX_UPLOAD_ROWS, REQUIRED_COLUMNS


@dataclass
class UploadValidationResult:
    """Validation result for an uploaded dataframe."""

    is_valid: bool
    errors: list[str]


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    """Return missing required columns."""
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def validate_upload_dataframe(df: pd.DataFrame) -> UploadValidationResult:
    """Validate dataframe schema and basic constraints."""
    errors: list[str] = []

    missing_cols = validate_required_columns(df)
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")

    if len(df.index) > MAX_UPLOAD_ROWS:
        errors.append(f"Row count exceeds limit ({MAX_UPLOAD_ROWS:,}).")

    return UploadValidationResult(is_valid=len(errors) == 0, errors=errors)
