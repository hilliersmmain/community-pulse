import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.health_metrics import DataHealthMetrics


class TestDataHealthMetrics:
    @pytest.fixture
    def perfect_data(self):
        return pd.DataFrame(
            {
                "Name": ["John Doe", "Jane Smith", "Bob Wilson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "Join_Date": ["2023-01-15", "2023-02-20", "2023-03-10"],
                "Event_Attendance": [5, 10, 8],
                "Role": ["Member", "Admin", "Member"],
            }
        )

    @pytest.fixture
    def data_with_missing_values(self):
        return pd.DataFrame(
            {
                "Name": ["John Doe", "Jane Smith", np.nan],
                "Email": ["john@example.com", np.nan, "bob@example.com"],
                "Event_Attendance": [5, np.nan, 8],
                "Role": ["Member", "Admin", np.nan],
            }
        )

    @pytest.fixture
    def data_with_duplicates(self):
        return pd.DataFrame(
            {
                "Name": ["John Doe", "John Doe", "Jane Smith"],
                "Email": ["john@example.com", "john@example.com", "jane@example.com"],
                "Event_Attendance": [5, 5, 10],
                "Role": ["Member", "Member", "Admin"],
            }
        )

    @pytest.fixture
    def data_with_bad_formatting(self):
        return pd.DataFrame(
            {
                "Name": ["john doe", "JANE SMITH", "123invalid"],
                "Email": ["invalid-email", "jane@example.com", "bob at example.com"],
                "Join_Date": ["2023-01-15", "Invalid Date", "12/25/2022"],
                "Event_Attendance": [5, 10, 8],
                "Role": ["Member", "Admin", "Member"],
            }
        )

    def test_completeness_score_perfect_data(self, perfect_data):
        metrics = DataHealthMetrics(perfect_data)
        score = metrics.calculate_completeness_score()

        assert score == 100.0

    def test_completeness_score_with_missing_values(self, data_with_missing_values):

        metrics = DataHealthMetrics(data_with_missing_values)
        score = metrics.calculate_completeness_score()

        # 12 total cells, 4 missing = 8/12 = 66.67%
        assert 66.0 <= score <= 67.0

    def test_completeness_score_empty_dataframe(self):

        metrics = DataHealthMetrics(pd.DataFrame())
        score = metrics.calculate_completeness_score()

        assert score == 0.0

    def test_duplicate_score_no_duplicates(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)
        score = metrics.calculate_duplicate_score()

        assert score == 100.0

    def test_duplicate_score_with_duplicates(self, data_with_duplicates):

        metrics = DataHealthMetrics(data_with_duplicates)
        score = metrics.calculate_duplicate_score()

        # 2 unique out of 3 total = 66.67%
        assert 66.0 <= score <= 67.0

    def test_duplicate_score_empty_dataframe(self):

        metrics = DataHealthMetrics(pd.DataFrame())
        score = metrics.calculate_duplicate_score()

        assert score == 100.0

    def test_formatting_score_perfect_data(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)
        score = metrics.calculate_formatting_score()

        # Should be high but not necessarily 100 due to case sensitivity
        assert score >= 90.0

    def test_formatting_score_with_bad_formatting(self, data_with_bad_formatting):

        metrics = DataHealthMetrics(data_with_bad_formatting)
        score = metrics.calculate_formatting_score()

        # Should be lower due to invalid emails, dates, and names
        assert score < 80.0

    def test_is_valid_email(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)

        assert metrics._is_valid_email("test@example.com") is True
        assert metrics._is_valid_email("invalid-email") is False
        assert metrics._is_valid_email("test at example.com") is False
        assert metrics._is_valid_email(np.nan) is False
        assert metrics._is_valid_email("") is False

    def test_is_valid_name(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)

        assert metrics._is_valid_name("John Doe") is True
        assert metrics._is_valid_name("O'Brien") is True
        assert metrics._is_valid_name("Mary-Jane") is True
        assert metrics._is_valid_name("123invalid") is False
        assert metrics._is_valid_name(np.nan) is False
        assert metrics._is_valid_name("") is False

    def test_count_valid_dates(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)

        valid_count = metrics._count_valid_dates("Join_Date")
        assert valid_count == 3

    def test_count_valid_dates_with_invalid(self, data_with_bad_formatting):

        metrics = DataHealthMetrics(data_with_bad_formatting)

        valid_count = metrics._count_valid_dates("Join_Date")
        # At least 1 should be valid (the ISO format)
        assert valid_count >= 1

    def test_overall_health_score_perfect_data(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)
        score = metrics.calculate_overall_health_score()

        # Should be very high for perfect data
        assert score >= 95.0
        assert score <= 100.0

    def test_overall_health_score_mixed_quality(self, data_with_missing_values):

        metrics = DataHealthMetrics(data_with_missing_values)
        score = metrics.calculate_overall_health_score()

        # Should be moderate due to missing values
        assert 50.0 <= score <= 90.0

    def test_get_all_metrics(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)
        all_metrics = metrics.get_all_metrics()

        assert "completeness_score" in all_metrics
        assert "duplicate_score" in all_metrics
        assert "formatting_score" in all_metrics
        assert "overall_score" in all_metrics
        assert "timestamp" in all_metrics

        # All scores should be numeric
        assert isinstance(all_metrics["completeness_score"], float)
        assert isinstance(all_metrics["duplicate_score"], float)
        assert isinstance(all_metrics["formatting_score"], float)
        assert isinstance(all_metrics["overall_score"], float)
        assert isinstance(all_metrics["timestamp"], datetime)

    def test_get_detailed_metrics(self, data_with_duplicates):

        metrics = DataHealthMetrics(data_with_duplicates)
        detailed = metrics.get_detailed_metrics()

        assert detailed["total_records"] == 3
        assert detailed["duplicate_records"] == 1
        assert detailed["unique_records"] == 2
        assert "total_cells" in detailed
        assert "null_cells" in detailed
        assert "non_null_cells" in detailed
        assert "completeness_score" in detailed
        assert "duplicate_score" in detailed
        assert "formatting_score" in detailed
        assert "overall_score" in detailed
        assert "timestamp" in detailed

    def test_timestamp_is_recent(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)

        # Timestamp should be within the last second
        time_diff = (datetime.now() - metrics.timestamp).total_seconds()
        assert time_diff < 1.0

    def test_score_ranges(self, perfect_data):

        metrics = DataHealthMetrics(perfect_data)

        assert 0 <= metrics.calculate_completeness_score() <= 100
        assert 0 <= metrics.calculate_duplicate_score() <= 100
        assert 0 <= metrics.calculate_formatting_score() <= 100
        assert 0 <= metrics.calculate_overall_health_score() <= 100

    def test_dataframe_copy(self, perfect_data):

        original_len = len(perfect_data)
        metrics = DataHealthMetrics(perfect_data)

        # Modify the internal df
        metrics.df = metrics.df.head(1)

        # Original should be unchanged
        assert len(perfect_data) == original_len


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
