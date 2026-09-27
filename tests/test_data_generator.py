"""Tests for data_generator module."""

import os
import tempfile
import pytest
import pandas as pd
from datetime import date, datetime, time, timedelta
from utils.data_generator import (
    DataGenerator,
    generate_messy_data,
    EVENT_CHOICES,
    JOIN_DATE_SPAN,
    LAST_LOGIN_SPAN,
    REGISTRATION_DATE_SPAN,
)


class TestGenerateMessyData:
    """Tests for generate_messy_data function."""

    def test_returns_dataframe(self):
        df = generate_messy_data(num_records=50)
        assert isinstance(df, pd.DataFrame)

    def test_correct_columns(self):
        df = generate_messy_data(num_records=50)
        expected_cols = [
            "ID",
            "Name",
            "Email",
            "Join_Date",
            "Last_Login",
            "Event_Attendance",
            "Role",
            "Event_Registered",
            "Registration_Date",
        ]
        for col in expected_cols:
            assert col in df.columns

    def test_record_count_includes_duplicates(self):
        df = generate_messy_data(num_records=100, messiness_level="medium")
        # Should have more rows than requested due to duplicates (~10%)
        assert len(df) > 100

    def test_low_messiness_fewer_duplicates(self):
        df = generate_messy_data(num_records=200, messiness_level="low")
        # Low = 3% duplicates, so ~206 rows
        assert len(df) < 220

    def test_high_messiness_more_duplicates(self):
        df = generate_messy_data(num_records=200, messiness_level="high")
        # High = 20% duplicates, so ~240 rows
        assert len(df) >= 220

    def test_save_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_data.csv")
            df = generate_messy_data(num_records=50, save_path=path)
            assert os.path.exists(path)
            loaded = pd.read_csv(path)
            assert len(loaded) == len(df)

    def test_invalid_num_records_raises(self):
        with pytest.raises(ValueError):
            generate_messy_data(num_records=-1)

    def test_zero_records_raises(self):
        with pytest.raises(ValueError):
            generate_messy_data(num_records=0)

    def test_invalid_messiness_raises(self):
        with pytest.raises(ValueError):
            generate_messy_data(num_records=50, messiness_level="extreme")

    def test_all_messiness_levels(self):
        for level in ["low", "medium", "high"]:
            df = generate_messy_data(num_records=50, messiness_level=level)
            assert len(df) > 0

    def test_roles_distribution(self):
        df = generate_messy_data(num_records=500, messiness_level="low")
        roles = df["Role"].unique()
        assert "Member" in roles
        # Member should be most common (80% probability)
        member_pct = (df["Role"] == "Member").mean()
        assert member_pct > 0.5

    def test_event_choices_used(self):
        df = generate_messy_data(num_records=200)
        for event in EVENT_CHOICES:
            assert event in df["Event_Registered"].values

    def test_messy_emails_present(self):
        df = generate_messy_data(num_records=200, messiness_level="high")
        # High messiness = 15% email errors, should have some "at" replacements
        has_at = df["Email"].str.contains(" at ", na=False).any()
        assert has_at

    def test_messy_names_present(self):
        df = generate_messy_data(num_records=200, messiness_level="high")
        # Some names should be all upper or all lower
        has_upper = df["Name"].str.isupper().any()
        has_lower = df["Name"].str.islower().any()
        assert has_upper or has_lower


class TestReferenceDate:
    """Generated dates are anchored on ``reference_date``, never on the wall clock."""

    @staticmethod
    def _date_offsets(df: pd.DataFrame, reference_date: date) -> list:
        # Join_Date is partly messed into strings; compare only the rows left as dates.
        return [(value - reference_date).days if isinstance(value, date) else None for value in df["Join_Date"]]

    def test_dates_fall_inside_windows_ending_at_reference_date(self):
        reference_date = date(2020, 1, 15)
        df = DataGenerator(seed=3, reference_date=reference_date).generate(num_records=300, messiness_level="low")

        join_dates = [value for value in df["Join_Date"] if isinstance(value, date)]
        assert join_dates
        assert all(reference_date - JOIN_DATE_SPAN <= value <= reference_date for value in join_dates)

        registration_dates = df["Registration_Date"].dropna()
        assert len(registration_dates) > 0
        assert all(reference_date - REGISTRATION_DATE_SPAN <= value <= reference_date for value in registration_dates)

        anchor = datetime.combine(reference_date, time.min)
        last_logins = df["Last_Login"].dropna()
        assert all(anchor - LAST_LOGIN_SPAN <= value <= anchor for value in last_logins)

    def test_same_seed_gives_same_offsets_for_any_reference_date(self):
        first, second = date(2021, 3, 10), date(2026, 4, 26)
        df_first = DataGenerator(seed=42, reference_date=first).generate(num_records=200, messiness_level="low")
        df_second = DataGenerator(seed=42, reference_date=second).generate(num_records=200, messiness_level="low")

        assert self._date_offsets(df_first, first) == self._date_offsets(df_second, second)
        assert df_first["Event_Attendance"].equals(df_second["Event_Attendance"])
