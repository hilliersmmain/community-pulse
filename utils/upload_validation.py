"""Validation helpers for uploaded CSV datasets."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
import pandas as pd

from utils.constants import HEADER_PEEK_BYTES, MAX_UPLOAD_COLUMNS, MAX_UPLOAD_ROWS, REQUIRED_COLUMNS

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


def _is_blank(row: list[str]) -> bool:
    """True for a row pandas skips: an empty line, or one holding only spaces or tabs (a line of commas is not)."""
    return len(row) == 0 or (len(row) == 1 and not row[0].strip())


def validate_upload_header(raw: bytes) -> list[str]:
    """Reject an upload whose header row has too many fields, judged from the raw bytes, before any parsing.

    The header is the first row that is not blank, as pandas reads it: blank lines before it are skipped, a
    quoted field may span lines, and lines may end in CR, LF or CRLF.
    """
    text = raw[:HEADER_PEEK_BYTES].decode("utf-8", errors="replace")
    header = next((row for row in csv.reader(io.StringIO(text, newline="")) if not _is_blank(row)), [])
    return [TOO_MANY_COLUMNS] if len(header) > MAX_UPLOAD_COLUMNS else []


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
