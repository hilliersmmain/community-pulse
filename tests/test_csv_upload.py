"""Tests for CSV upload validation logic."""

import io

import pandas as pd
import pytest
from utils.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS, MAX_UPLOAD_ROWS, MAX_UPLOAD_COLUMNS
from utils.upload_validation import (
    validate_required_columns,
    validate_upload_dataframe,
    validate_upload_header,
)


class TestCSVUploadValidation:
    """Tests for CSV upload column validation."""

    def test_required_columns_defined(self):
        assert len(REQUIRED_COLUMNS) >= 5
        assert "Name" in REQUIRED_COLUMNS
        assert "Email" in REQUIRED_COLUMNS
        assert "Role" in REQUIRED_COLUMNS
        assert "Join_Date" in REQUIRED_COLUMNS
        assert "Event_Attendance" in REQUIRED_COLUMNS

    def test_valid_csv_has_required_columns(self):
        df = pd.DataFrame(
            {
                "Name": ["Alice"],
                "Email": ["alice@test.com"],
                "Role": ["Member"],
                "Join_Date": ["2025-01-01"],
                "Event_Attendance": [4],
            }
        )
        assert validate_required_columns(df) == []

    def test_missing_columns_detected(self):
        df = pd.DataFrame({"Name": ["Alice"], "Value": [1]})
        assert validate_required_columns(df) == ["Email", "Role", "Join_Date", "Event_Attendance"]

        result = validate_upload_dataframe(df)
        assert not result.is_valid
        assert result.errors == ["Missing required columns: Email, Role, Join_Date, Event_Attendance"]

    def test_empty_dataframe_has_columns(self):
        df = pd.DataFrame(columns=REQUIRED_COLUMNS)
        assert validate_required_columns(df) == []

    def test_upload_validation_rejects_missing_required_columns(self):
        df = pd.DataFrame({"Name": ["Ann"], "Role": ["Member"]})
        result = validate_upload_dataframe(df)
        assert not result.is_valid
        assert result.errors == ["Missing required columns: Email, Join_Date, Event_Attendance"]

    def test_optional_columns_list(self):
        assert isinstance(OPTIONAL_COLUMNS, list)
        assert "Join_Date" in OPTIONAL_COLUMNS

    def test_upload_validation_accepts_valid_dataframe(self):
        df = pd.DataFrame(
            {
                "Name": ["Alice"],
                "Email": ["alice@test.com"],
                "Role": ["Member"],
                "Join_Date": ["2025-01-01"],
                "Event_Attendance": [4],
            }
        )
        result = validate_upload_dataframe(df)
        assert result.is_valid
        assert result.errors == []

    def test_upload_validation_rejects_oversized_row_count(self):
        df = pd.DataFrame(
            {
                "Name": ["Alice"] * (MAX_UPLOAD_ROWS + 1),
                "Email": ["alice@test.com"] * (MAX_UPLOAD_ROWS + 1),
                "Role": ["Member"] * (MAX_UPLOAD_ROWS + 1),
                "Join_Date": ["2025-01-01"] * (MAX_UPLOAD_ROWS + 1),
                "Event_Attendance": [4] * (MAX_UPLOAD_ROWS + 1),
            }
        )
        result = validate_upload_dataframe(df)
        assert not result.is_valid
        assert any("Row count exceeds limit" in error for error in result.errors)


class TestDelimitedUploads:
    """W26: a ;- or tab-delimited file reads as one column, so every required column looks missing."""

    ALL_FIVE = "Missing required columns: Name, Email, Role, Join_Date, Event_Attendance"

    @staticmethod
    def _read(raw: bytes) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(raw))

    @pytest.mark.parametrize(
        ("delimiter", "kind"),
        [(";", "semicolon"), ("\t", "tab"), ("|", "pipe")],
    )
    def test_single_delimited_header_names_the_delimiter(self, delimiter, kind):
        header = delimiter.join(REQUIRED_COLUMNS)
        row = delimiter.join(["Ann", "a@x.com", "Member", "2025-01-01", "3"])
        result = validate_upload_dataframe(self._read(f"{header}\n{row}\n".encode()))
        assert not result.is_valid
        assert result.errors == [
            f"{self.ALL_FIVE}. The header looks {kind}-delimited; re-save the file with commas as the delimiter."
        ]

    def test_a_missing_column_in_a_comma_file_gets_no_delimiter_hint(self):
        result = validate_upload_dataframe(self._read(b"Name,Foo\nAnn,1\n"))
        assert result.errors == ["Missing required columns: Email, Role, Join_Date, Event_Attendance"]

    def test_a_single_plain_column_gets_no_delimiter_hint(self):
        result = validate_upload_dataframe(self._read(b"Name\nAnn\n"))
        assert result.errors == ["Missing required columns: Email, Role, Join_Date, Event_Attendance"]


class TestUploadWidth:
    """W14: no cap on the column count let a 220 KB file with 10,000 columns stall every rerun for over a minute."""

    TOO_MANY = f"Too many columns: uploads are limited to {MAX_UPLOAD_COLUMNS} columns."

    @staticmethod
    def _header(extra: int) -> list[str]:
        return REQUIRED_COLUMNS + [f"extra_{i}" for i in range(extra)]

    def test_upload_validation_rejects_too_many_columns(self):
        columns = self._header(MAX_UPLOAD_COLUMNS - len(REQUIRED_COLUMNS) + 1)
        assert len(columns) == MAX_UPLOAD_COLUMNS + 1
        result = validate_upload_dataframe(pd.DataFrame([["x"] * len(columns)], columns=columns))
        assert not result.is_valid
        assert result.errors == [self.TOO_MANY]

    def test_upload_validation_accepts_exactly_the_column_limit(self):
        columns = self._header(MAX_UPLOAD_COLUMNS - len(REQUIRED_COLUMNS))
        assert len(columns) == MAX_UPLOAD_COLUMNS
        result = validate_upload_dataframe(pd.DataFrame([["x"] * len(columns)], columns=columns))
        assert result.is_valid

    def test_header_check_rejects_a_wide_header_from_the_raw_bytes(self):
        raw = (",".join(self._header(MAX_UPLOAD_COLUMNS)) + "\nx\n").encode()
        assert validate_upload_header(raw) == [self.TOO_MANY]

    def test_header_check_accepts_a_header_at_the_limit(self):
        raw = (",".join(self._header(MAX_UPLOAD_COLUMNS - len(REQUIRED_COLUMNS))) + "\nx\n").encode()
        assert validate_upload_header(raw) == []

    def test_header_check_counts_a_quoted_comma_as_one_column(self):
        raw = b'"Last, First",Email\nx,y\n'
        assert validate_upload_header(raw) == []

    def test_header_check_only_reads_the_first_line_and_stays_fast(self):
        # The case from the finding: a header of nothing but commas cost pandas 9 s at 32,000 of them.
        raw = b"," * 100_000 + b"\nName,Email\n"
        assert validate_upload_header(raw) == [self.TOO_MANY]
        # A normal header followed by a huge body is not looked at beyond its first line.
        assert validate_upload_header(b"Name,Email\n" + b"," * 1_000_000) == []

    def test_header_check_skips_blank_lines_before_the_header(self):
        # pandas skips empty and whitespace-only lines, so a wide header after one used to reach it unchecked.
        wide = ",".join(self._header(MAX_UPLOAD_COLUMNS)).encode()
        for prefix in (b"\n", b"\r\n", b" \n", b"\t\r\n\n"):
            assert validate_upload_header(prefix + wide + b"\nx\n") == [self.TOO_MANY], prefix

    def test_header_check_reads_a_quoted_header_field_that_spans_lines(self):
        wide = ",".join(self._header(MAX_UPLOAD_COLUMNS)).encode()
        assert validate_upload_header(b'"Na\nme",' + wide + b"\nx\n") == [self.TOO_MANY]

    def test_header_check_accepts_a_cr_only_file_that_pandas_reads(self):
        # Classic Mac and Excel "CSV (Macintosh)" files end each line with a bare CR.
        raw = b"Name,Email,Role,Join_Date,Event_Attendance\rAnn,a@x.com,Member,2025-01-01,3\r"
        assert pd.read_csv(io.BytesIO(raw)).shape == (1, 5)
        assert validate_upload_header(raw) == []
        wide = ",".join(self._header(MAX_UPLOAD_COLUMNS)).encode()
        assert validate_upload_header(wide + b"\rx\r") == [self.TOO_MANY]
