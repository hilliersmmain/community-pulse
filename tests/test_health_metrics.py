import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.health_metrics import (
    DataHealthMetrics,
    FORMATTING_VALIDATORS,
    _find_validator,
    _validate_email_series,
    _validate_date_series,
    _validate_name_series,
    _validate_id_series,
)


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


# ---------------------------------------------------------------------------
# Tests for pluggable validator functions
# ---------------------------------------------------------------------------


class TestEmailValidator:
    """Unit tests for _validate_email_series."""

    def test_all_valid(self):
        s = pd.Series(["a@b.com", "test@example.org", "user+tag@domain.co.uk"])
        assert _validate_email_series(s) == 1.0

    def test_partial_valid(self):
        s = pd.Series(["a@b.com", "not-an-email", "another@valid.com", "bad"])
        result = _validate_email_series(s)
        assert result == pytest.approx(0.5, abs=0.01)

    def test_all_invalid(self):
        s = pd.Series(["bad", "no at sign", "missing@"])
        assert _validate_email_series(s) == 0.0

    def test_empty_series(self):
        assert _validate_email_series(pd.Series([], dtype=str)) == 1.0

    def test_all_nan_series(self):
        # Validator is called with non-null values; all-NaN → dropna → empty → 1.0
        s = pd.Series([np.nan, np.nan]).dropna()
        assert _validate_email_series(s) == 1.0


class TestDateValidator:
    """Unit tests for _validate_date_series."""

    def test_all_valid(self):
        s = pd.Series(["2023-01-15", "2022-12-31", "2021-06-01"])
        assert _validate_date_series(s) == 1.0

    def test_partial_valid(self):
        s = pd.Series(["2023-01-15", "not-a-date", "2022-05-20", "Unknown"])
        result = _validate_date_series(s)
        assert result == pytest.approx(0.5, abs=0.01)

    def test_all_invalid(self):
        s = pd.Series(["Unknown", "not-a-date", "nope"])
        assert _validate_date_series(s) == 0.0

    def test_empty_series(self):
        assert _validate_date_series(pd.Series([], dtype=str)) == 1.0

    def test_all_nan_series(self):
        s = pd.Series([np.nan, np.nan]).dropna()
        assert _validate_date_series(s) == 1.0


class TestNameValidator:
    """Unit tests for _validate_name_series."""

    def test_all_valid(self):
        s = pd.Series(["John Doe", "O'Brien", "Mary-Jane"])
        assert _validate_name_series(s) == 1.0

    def test_partial_valid(self):
        s = pd.Series(["John Doe", "123invalid", "Jane Smith", "99problems"])
        result = _validate_name_series(s)
        assert result == pytest.approx(0.5, abs=0.01)

    def test_all_invalid(self):
        s = pd.Series(["123", "456abc", "!!!"])
        assert _validate_name_series(s) == 0.0

    def test_empty_series(self):
        assert _validate_name_series(pd.Series([], dtype=str)) == 1.0

    def test_all_nan_series(self):
        s = pd.Series([np.nan, np.nan]).dropna()
        assert _validate_name_series(s) == 1.0


class TestIdValidator:
    """Unit tests for _validate_id_series."""

    def test_all_valid(self):
        s = pd.Series(["abc-123", "uuid-456", "1"])
        assert _validate_id_series(s) == 1.0

    def test_partial_valid(self):
        s = pd.Series(["abc", "", "def", "  "])
        result = _validate_id_series(s)
        assert result == pytest.approx(0.5, abs=0.01)

    def test_all_invalid(self):
        s = pd.Series(["", "   ", "  "])
        assert _validate_id_series(s) == 0.0

    def test_empty_series(self):
        assert _validate_id_series(pd.Series([], dtype=str)) == 1.0

    def test_all_nan_series(self):
        s = pd.Series([np.nan, np.nan]).dropna()
        assert _validate_id_series(s) == 1.0


# ---------------------------------------------------------------------------
# Tests for the validator registry (_find_validator)
# ---------------------------------------------------------------------------


class TestValidatorRegistry:
    """Test pattern matching in FORMATTING_VALIDATORS."""

    def test_email_exact_match(self):
        assert _find_validator("Email") is _validate_email_series

    def test_email_lower_match(self):
        assert _find_validator("email") is _validate_email_series

    def test_email_suffix_match(self):
        assert _find_validator("User_Email") is _validate_email_series

    def test_join_date_match(self):
        assert _find_validator("Join_Date") is _validate_date_series

    def test_registration_date_match(self):
        assert _find_validator("Registration_Date") is _validate_date_series

    def test_last_login_no_match(self):
        # Last_Login does not match the date pattern (known limitation — documented in health_metrics.py)
        assert _find_validator("Last_Login") is None

    def test_name_exact_match(self):
        assert _find_validator("Name") is _validate_name_series

    def test_name_suffix_match(self):
        assert _find_validator("Member_Name") is _validate_name_series

    def test_id_exact_match(self):
        assert _find_validator("ID") is _validate_id_series

    def test_id_suffix_match(self):
        assert _find_validator("User_ID") is _validate_id_series

    def test_unrecognised_column_returns_none(self):
        assert _find_validator("Role") is None
        assert _find_validator("Event_Attendance") is None
        assert _find_validator("Random_Column_XYZ") is None

    def test_first_match_wins(self):
        """A column name that matches multiple patterns uses the first registry entry."""
        # "User_Email" matches the email pattern but nothing else — just confirming priority
        assert _find_validator("User_Email") is _validate_email_series

    def test_column_no_validator_scores_100(self):
        """Columns without a matching validator contribute 100% (no penalty)."""
        df = pd.DataFrame({"Role": ["Member", "Admin", "Guest"], "Event_Attendance": [5, 10, 8]})
        metrics = DataHealthMetrics(df)
        assert metrics.calculate_formatting_score() == 100.0


# ---------------------------------------------------------------------------
# Backwards-compatibility test
# ---------------------------------------------------------------------------


class TestFormattingBackwardsCompat:
    """Ensure the existing Name/Email/Join_Date scenario produces the same score."""

    def test_classic_columns_unchanged(self):
        """
        A DataFrame with Name, Email, Join_Date (all valid) should still score 100.0.
        Previously the old hard-coded checks returned 100.0; the new registry must too.
        """
        df = pd.DataFrame(
            {
                "Name": ["John Doe", "Jane Smith", "Bob Wilson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "Join_Date": ["2023-01-15", "2023-02-20", "2023-03-10"],
                "Event_Attendance": [5, 10, 8],
                "Role": ["Member", "Admin", "Member"],
            }
        )
        metrics = DataHealthMetrics(df)
        assert metrics.calculate_formatting_score() == pytest.approx(100.0, abs=0.1)
        assert metrics.calculate_overall_health_score() == pytest.approx(100.0, abs=0.1)


# ---------------------------------------------------------------------------
# Bug-fix demonstration: Registration_Date now incurs a formatting penalty
# ---------------------------------------------------------------------------


class TestFormattingPenaltyOnNewColumns:
    """Demonstrate the bug fix: date-like columns beyond Join_Date now get validated."""

    def test_registration_date_bad_values_incur_penalty(self):
        """
        A DataFrame with Registration_Date where 70% of values are non-dates
        should now produce a formatting score < 100.
        Previously Registration_Date was silently ignored (scored as 100%).
        """
        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob", "Carol", "Dan", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"],
                "Registration_Date": [
                    "2023-01-15",  # valid
                    "2023-02-20",  # valid
                    "2023-03-10",  # valid
                    "not-a-date",  # invalid
                    "Unknown",  # invalid
                    "foo",  # invalid
                    "bar",  # invalid
                    "baz",  # invalid
                    "qux",  # invalid
                    "quux",  # invalid
                ],
            }
        )
        metrics = DataHealthMetrics(df)
        score = metrics.calculate_formatting_score()
        # 3/10 valid dates → 30% on Registration_Date; Name is all valid → 100%
        # Average = (30 + 100) / 2 = 65 — well below 100
        assert score < 100.0
        assert score < 70.0  # meaningful penalty

    def test_single_value_dataframe(self):
        """Edge case: DataFrame with a single row should not crash."""
        df = pd.DataFrame({"Email": ["user@example.com"], "Join_Date": ["2023-01-01"]})
        metrics = DataHealthMetrics(df)
        assert metrics.calculate_formatting_score() == pytest.approx(100.0, abs=0.1)

    def test_zero_row_dataframe(self):
        """Edge case: DataFrame with zero rows returns 100.0."""
        df = pd.DataFrame({"Email": pd.Series([], dtype=str), "Join_Date": pd.Series([], dtype=str)})
        metrics = DataHealthMetrics(df)
        assert metrics.calculate_formatting_score() == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
