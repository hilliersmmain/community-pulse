"""Tests for CSV upload validation logic."""

import pandas as pd
from utils.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS, MAX_UPLOAD_ROWS
from utils.upload_validation import validate_required_columns, validate_upload_dataframe


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
