"""Tests for CSV upload validation logic."""

import pandas as pd
from utils.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS


class TestCSVUploadValidation:
    """Tests for CSV upload column validation."""

    def test_required_columns_defined(self):
        assert len(REQUIRED_COLUMNS) >= 2
        assert "Name" in REQUIRED_COLUMNS
        assert "Email" in REQUIRED_COLUMNS

    def test_valid_csv_has_required_columns(self):
        df = pd.DataFrame({"Name": ["Alice"], "Email": ["alice@test.com"], "Role": ["Member"]})
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        assert len(missing) == 0

    def test_missing_columns_detected(self):
        df = pd.DataFrame({"Name": ["Alice"], "Value": [1]})
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        assert "Email" in missing

    def test_empty_dataframe_has_columns(self):
        df = pd.DataFrame(columns=["Name", "Email", "Role"])
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        assert len(missing) == 0

    def test_optional_columns_list(self):
        assert isinstance(OPTIONAL_COLUMNS, list)
        assert "Join_Date" in OPTIONAL_COLUMNS
