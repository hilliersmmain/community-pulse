import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.cleaner import DataCleaner


class TestDataCleaner:
    @pytest.fixture
    def sample_data_with_duplicates(self):
        return pd.DataFrame(
            {
                "Name": ["John Doe", "John Doe", "Jane Smith"],
                "Email": ["john@example.com", "john@example.com", "jane@example.com"],
                "Event_Attendance": [5, 5, 10],
                "Role": ["Member", "Member", "Admin"],
            }
        )

    @pytest.fixture
    def sample_data_with_invalid_emails(self):
        return pd.DataFrame(
            {
                "Name": ["Alice Brown", "Bob Jones", "Carol White"],
                "Email": ["alice at example.com", "bob@test.com", "invalid-email"],
                "Event_Attendance": [3, 7, 2],
                "Role": ["Member", "Guest", "Member"],
            }
        )

    @pytest.fixture
    def sample_data_with_mixed_case_names(self):
        return pd.DataFrame(
            {
                "Name": ["john doe", "JANE SMITH", "Bob Wilson"],
                "Email": ["john@test.com", "jane@test.com", "bob@test.com"],
                "Event_Attendance": [1, 2, 3],
                "Role": ["Member", "Admin", "Guest"],
            }
        )

    @pytest.fixture
    def sample_data_with_bad_dates(self):
        return pd.DataFrame(
            {
                "Name": ["Alex Turner", "Sam Lee", "Chris Evans"],
                "Email": ["alex@test.com", "sam@test.com", "chris@test.com"],
                "Join_Date": ["2023-01-15", "Unknown", "12/25/2022"],
                "Event_Attendance": [4, 5, 6],
                "Role": ["Member", "Member", "Admin"],
            }
        )

    @pytest.fixture
    def sample_data_with_missing_values(self):
        return pd.DataFrame(
            {
                "Name": ["David Kim", "Emma Davis", "Frank Miller"],
                "Email": ["david@test.com", "emma@test.com", "frank@test.com"],
                "Event_Attendance": [8, np.nan, np.nan],
                "Role": ["Admin", "Member", "Guest"],
            }
        )

    def test_remove_duplicates(self, sample_data_with_duplicates):
        cleaner = DataCleaner(sample_data_with_duplicates)
        cleaner.remove_duplicates()

        assert len(cleaner.clean_df) == 2
        assert any("duplicate" in msg.lower() for msg in cleaner.log)
        assert cleaner.clean_df["Email"].nunique() == 2

    def test_fix_emails(self, sample_data_with_invalid_emails):
        cleaner = DataCleaner(sample_data_with_invalid_emails)
        cleaner.fix_emails()

        assert len(cleaner.clean_df) == 2
        assert all("@" in str(email) for email in cleaner.clean_df["Email"])
        assert any("email" in msg.lower() for msg in cleaner.log)

        emails = cleaner.clean_df["Email"].tolist()
        assert "alice@example.com" in emails

    def test_standardize_names(self, sample_data_with_mixed_case_names):
        cleaner = DataCleaner(sample_data_with_mixed_case_names)
        cleaner.standardize_names()

        expected_names = ["John Doe", "Jane Smith", "Bob Wilson"]
        assert cleaner.clean_df["Name"].tolist() == expected_names
        assert any("name" in msg.lower() and "title case" in msg.lower() for msg in cleaner.log)

    def test_clean_dates(self, sample_data_with_bad_dates):
        cleaner = DataCleaner(sample_data_with_bad_dates)
        cleaner.clean_dates()

        assert pd.api.types.is_datetime64_any_dtype(cleaner.clean_df["Join_Date"])
        assert any("date" in msg.lower() for msg in cleaner.log)

        valid_dates = cleaner.clean_df["Join_Date"].dropna()
        assert len(valid_dates) >= 1

    def test_handle_missing_values(self, sample_data_with_missing_values):
        cleaner = DataCleaner(sample_data_with_missing_values)
        cleaner.handle_missing_values()

        assert cleaner.clean_df["Event_Attendance"].isna().sum() == 0

        expected = [8.0, 0.0, 0.0]
        assert cleaner.clean_df["Event_Attendance"].tolist() == expected
        assert any("attendance" in msg.lower() for msg in cleaner.log)

    def test_clean_all_pipeline(self):
        messy_data = pd.DataFrame(
            {
                "Name": ["john doe", "JANE SMITH", "john doe", "bob wilson"],
                "Email": ["john at test.com", "jane@test.com", "john at test.com", "invalid"],
                "Join_Date": ["2023-01-15", "Unknown", "2023-01-15", "2022-12-25"],
                "Event_Attendance": [5, np.nan, 5, 10],
                "Role": ["Member", "Admin", "Member", "Guest"],
            }
        )

        cleaner = DataCleaner(messy_data)
        result = cleaner.clean_all()

        assert len(result) >= 1
        assert len(cleaner.log) >= 4
        assert all(name.istitle() for name in result["Name"])
        assert result["Event_Attendance"].isna().sum() == 0
        assert pd.api.types.is_datetime64_any_dtype(result["Join_Date"])

    def test_clean_all_empty_dataframe(self):
        """Test clean_all handles empty DataFrame gracefully."""
        empty_df = pd.DataFrame(columns=["Name", "Email", "Join_Date", "Event_Attendance"])
        cleaner = DataCleaner(empty_df)
        result = cleaner.clean_all()
        assert len(result) == 0
        assert cleaner.end_timestamp is not None

    def test_timestamps_are_set(self):
        messy_data = pd.DataFrame(
            {
                "Name": ["John Doe", "Jane Smith"],
                "Email": ["john@test.com", "jane@test.com"],
                "Event_Attendance": [5, 10],
                "Role": ["Member", "Admin"],
            }
        )

        cleaner = DataCleaner(messy_data)

        assert cleaner.start_timestamp is not None
        assert isinstance(cleaner.start_timestamp, datetime)
        assert cleaner.end_timestamp is None

        cleaner.clean_all()

        assert cleaner.end_timestamp is not None
        assert isinstance(cleaner.end_timestamp, datetime)
        assert cleaner.end_timestamp >= cleaner.start_timestamp


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
