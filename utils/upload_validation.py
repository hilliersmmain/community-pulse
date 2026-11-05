"""Validation helpers for uploaded CSV datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import pandas as pd

from utils.constants import MAX_UPLOAD_COLUMNS, MAX_UPLOAD_ROWS, REQUIRED_COLUMNS

# How much of an upload is read to count its header fields. Parsing a header of tens of thousands of
# columns takes pandas seconds, so the count is made on the raw bytes before pandas sees the file.
HEADER_PEEK_BYTES = 65536

# Delimiters a spreadsheet export may use instead of a comma, by the name the error message gives them.
_OTHER_DELIMITERS = {";": "semicolon", "\t": "tab", "|": "pipe"}

TOO_MANY_COLUMNS = f"Too many columns: uploads are limited to {MAX_UPLOAD_COLUMNS} columns."


@dataclass
class UploadValidationResult:
    """Validation result for an uploaded dataframe."""

    is_valid: bool
    errors: list[str]


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    """Return missing required columns."""
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


def validate_upload_header(raw: bytes) -> list[str]:
    """Reject an upload whose first line has too many fields, judged from the raw bytes, before any parsing."""
    first_line = raw[:HEADER_PEEK_BYTES].split(b"\n", 1)[0].decode("utf-8", errors="replace")
    field_count = len(next(csv.reader([first_line]), []))
    return [TOO_MANY_COLUMNS] if field_count > MAX_UPLOAD_COLUMNS else []


def _delimiter_hint(df: pd.DataFrame) -> str:
    """Name the delimiter when the whole header was read as one column, e.g. "Name;Email;Role"."""
    if len(df.columns) != 1:
        return ""
    header = str(df.columns[0])
    for delimiter, name in _OTHER_DELIMITERS.items():
        if delimiter in header:
            return f". The header looks {name}-delimited; re-save the file with commas as the delimiter."
    return ""


def validate_upload_dataframe(df: pd.DataFrame) -> UploadValidationResult:
    """Validate dataframe schema and basic constraints."""
    errors: list[str] = []

    missing_cols = validate_required_columns(df)
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}{_delimiter_hint(df)}")

    if len(df.columns) > MAX_UPLOAD_COLUMNS:
        errors.append(TOO_MANY_COLUMNS)

    if len(df.index) > MAX_UPLOAD_ROWS:
        errors.append(f"Row count exceeds limit ({MAX_UPLOAD_ROWS:,}).")

    return UploadValidationResult(is_valid=len(errors) == 0, errors=errors)
