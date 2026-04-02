"""Tests for data_generator module."""

import os
import tempfile
import pytest
import pandas as pd
from utils.data_generator import generate_messy_data, EVENT_CHOICES


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
