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

    def test_clean_dates_reads_every_format_whatever_comes_first(self):
        # As read back from the CSV: strings in the generator's three formats. pandas used
        # to infer one format from the first value and turn the other two into NaT.
        df = pd.DataFrame({"Join_Date": ["06/02/2025", "2025-01-15", "15-03-2025", "Unknown", "2024-12-01"]})
        cleaner = DataCleaner(df)
        cleaner.clean_dates()

        parsed = cleaner.clean_df["Join_Date"]
        assert parsed[0] == pd.Timestamp("2025-06-02")
        assert parsed[1] == pd.Timestamp("2025-01-15")
        assert parsed[2] == pd.Timestamp("2025-03-15")
        assert parsed[4] == pd.Timestamp("2024-12-01")
        assert pd.isna(parsed[3])  # "Unknown" stays blank; it is not given the most common date
        assert "Left 1 unreadable dates blank" in cleaner.log[-1]

    def test_clean_dates_after_csv_round_trip_blanks_only_unknowns(self, tmp_path):
        from datetime import date
        from utils.data_generator import DataGenerator

        path = tmp_path / "generated.csv"
        DataGenerator(seed=7, reference_date=date(2026, 9, 1)).generate(
            num_records=500, messiness_level="medium", save_path=str(path)
        )
        df = pd.read_csv(path)
        n_unknown = int((df["Join_Date"] == "Unknown").sum())

        cleaner = DataCleaner(df)
        cleaner.clean_dates()

        assert n_unknown > 0
        assert cleaner.clean_df["Join_Date"].isna().sum() == n_unknown
        assert f"Left {n_unknown} unreadable dates blank" in cleaner.log[-1]

    def test_clean_dates_does_not_pile_unreadable_dates_onto_one_day(self):
        """W10: every unreadable date used to be filled with the single most common date, a fake spike."""
        dates = [f"2024-{m:02d}-{d:02d}" for m in range(1, 7) for d in range(1, 11)] + ["Unknown"] * 10
        cleaner = DataCleaner(pd.DataFrame({"Join_Date": dates}))
        cleaner.clean_dates()
        joined = cleaner.clean_df["Join_Date"]
        assert joined.value_counts().max() == 1
        assert joined.isna().sum() == 10
        assert pd.api.types.is_datetime64_any_dtype(joined)

    def test_clean_dates_counts_unreadable_and_already_missing_dates_separately(self):
        df = pd.DataFrame({"Join_Date": ["2024-01-05", "Unknown", None, "01/06/2024"]})
        cleaner = DataCleaner(df)
        cleaner.clean_dates()
        assert cleaner.clean_df["Join_Date"].isna().tolist() == [False, True, True, False]
        assert (
            cleaner.log[-1]
            == "Standardized Dates. Left 1 unreadable dates blank (not guessed); 1 were already missing."
        )

    def test_clean_dates_with_nothing_to_blank_says_so(self):
        cleaner = DataCleaner(pd.DataFrame({"Join_Date": ["2024-01-05", "01/06/2024"]}))
        cleaner.clean_dates()
        assert cleaner.log[-1] == "Standardized Dates. Every date was readable."

    def test_dates_left_blank_flow_through_the_chart_metrics_and_exports(self):
        """Every consumer of Join_Date copes with NaT: the chart plots the dated rows, completeness takes the hit."""
        from components.sidebar import export_json
        from utils.health_metrics import DataHealthMetrics
        from utils.visualizer import plot_attendance_trend

        df = pd.DataFrame(
            {
                "Name": ["A", "B", "C", "D"],
                "Email": ["a@x.com", "b@x.com", "c@x.com", "d@x.com"],
                "Role": ["Member"] * 4,
                "Join_Date": ["2024-01-05", "Unknown", "2024-03-02", "Unknown"],
                "Event_Attendance": [1, 2, 3, 4],
            }
        )
        cleaned = DataCleaner(df).clean_all()

        metrics = DataHealthMetrics(cleaned).get_detailed_metrics()
        assert metrics["null_cells"] == 2
        assert metrics["completeness_score"] == 90.0
        assert metrics["formatting_score"] == 100.0

        line = next(t for t in plot_attendance_trend(cleaned).data if t.name == "New Members")
        assert list(line.x) == ["2024-01", "2024-02", "2024-03"]
        assert sum(line.y) == 2

        assert export_json(cleaned).count('"Join_Date":null') == 2
        assert cleaned.to_csv(index=False).splitlines()[2] == "B,b@x.com,Member,,2"

    def test_a_cleaned_frame_with_no_readable_date_still_plots_as_an_empty_chart(self):
        from utils.visualizer import plot_attendance_trend

        cleaned = DataCleaner(pd.DataFrame({"Join_Date": ["Unknown", "n/a"]})).clean_all(["clean_dates"])
        assert cleaned["Join_Date"].isna().all()
        assert len(plot_attendance_trend(cleaned).data) == 0

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

    def test_clean_all_dedups_after_email_fix(self):
        """Duplicates that differ only in email formatting must collapse: fix_emails has to run before
        remove_duplicates, because remove_duplicates only lower-cases and never rewrites ' at ' to '@'."""
        df = pd.DataFrame(
            {
                "Name": ["Ann Lee", "Ann Lee"],
                "Email": ["ann@test.com", "ann at test.com"],
            }
        )

        result = DataCleaner(df).clean_all()

        assert len(result) == 1
        assert result["Email"].tolist() == ["ann@test.com"]

    def test_clean_all_empty_dataframe(self):
        """Test clean_all handles empty DataFrame gracefully."""
        empty_df = pd.DataFrame(columns=["Name", "Email", "Join_Date", "Event_Attendance"])
        cleaner = DataCleaner(empty_df)
        result = cleaner.clean_all()
        assert len(result) == 0
        assert cleaner.end_timestamp is not None

    def test_clean_all_selective_steps(self):
        """Test running only selected cleaning steps."""
        messy_data = pd.DataFrame(
            {
                "Name": ["john doe", "JANE SMITH"],
                "Email": ["john@test.com", "jane@test.com"],
                "Join_Date": ["2023-01-15", "2023-06-01"],
                "Event_Attendance": [5, 10],
                "Role": ["Member", "Admin"],
            }
        )
        cleaner = DataCleaner(messy_data)
        result = cleaner.clean_all(steps=["standardize_names"])
        # Only name standardization should have run
        assert len(cleaner.log) == 1
        assert "Standardized Names" in cleaner.log[0]

    def test_clean_all_no_steps(self):
        """Test running with empty steps list."""
        messy_data = pd.DataFrame(
            {
                "Name": ["John Doe"],
                "Email": ["john@test.com"],
                "Event_Attendance": [5],
                "Role": ["Member"],
            }
        )
        cleaner = DataCleaner(messy_data)
        result = cleaner.clean_all(steps=[])
        assert len(cleaner.log) == 0
        assert cleaner.end_timestamp is not None

    def test_remove_duplicates_no_email_column(self):
        """Test dedup falls back to drop_duplicates when no Email column."""
        df = pd.DataFrame({"Name": ["Alice", "Alice", "Bob"], "Value": [1, 1, 2]})
        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        assert len(cleaner.clean_df) == 2

    def test_remove_duplicates_keeps_every_row_missing_an_email(self):
        """Missing emails are not a match for each other (they used to become the string 'None')."""
        df = pd.DataFrame({"Name": ["A", "B", "C", "D"], "Email": ["a@x.com", np.nan, np.nan, "A@x.com"]})
        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        assert cleaner.clean_df["Name"].tolist() == ["A", "B", "C"]

    def test_remove_duplicates_ignores_case_and_surrounding_spaces_in_emails(self):
        """The shared duplicate key is the lower-cased, stripped Email (remove_duplicates used to skip the strip)."""
        df = pd.DataFrame({"Name": ["A", "B", "C"], "Email": ["a@x.com", " A@x.com ", "c@x.com"]})
        cleaner = DataCleaner(df)
        cleaner.remove_duplicates()
        assert cleaner.clean_df["Name"].tolist() == ["A", "C"]

    def test_standardize_names_leaves_missing_names_missing(self):
        df = pd.DataFrame({"Name": ["john doe", None, np.nan]})
        cleaner = DataCleaner(df)
        cleaner.standardize_names()
        assert cleaner.clean_df["Name"][0] == "John Doe"
        assert cleaner.clean_df["Name"][1:].isna().all()

    def test_handle_missing_values_treats_unreadable_attendance_as_missing(self):
        df = pd.DataFrame({"Event_Attendance": ["5", "unknown", None, 3]})
        cleaner = DataCleaner(df)
        cleaner.handle_missing_values()
        assert cleaner.clean_df["Event_Attendance"].tolist() == [5, 0, 0, 3]
        assert "Filled 2 missing" in cleaner.log[-1]

    def test_fix_emails_at_replacement(self):
        """Test that 'user at domain.com' becomes 'user@domain.com'."""
        df = pd.DataFrame({"Email": ["john at test.com", "valid@test.com"]})
        cleaner = DataCleaner(df)
        cleaner.fix_emails()
        emails = cleaner.clean_df["Email"].tolist()
        assert "john@test.com" in emails

    @pytest.mark.parametrize("bad", ["ann@x.com; bob@y.com", "ann smith@x.com", "a@b.c"])
    def test_fix_emails_drops_what_the_validator_rejects(self, bad):
        """fix_emails and the Formatting validator share EMAIL_PATTERN, so nothing it keeps scores as malformed (W05)."""
        cleaner = DataCleaner(pd.DataFrame({"Name": ["A"], "Email": [bad]}))
        cleaner.fix_emails()
        assert cleaner.clean_df.empty

    def test_every_email_fix_emails_keeps_is_valid_to_the_validator(self):
        from utils.health_metrics import _validate_email_series

        raw = ["Ann at X.com", " bob@y.org ", "c@d.e", "no at sign", "ok@x.com", "a@b@c.com", "x y@z.com", "q@z.co.uk"]
        cleaner = DataCleaner(pd.DataFrame({"Name": list("ABCDEFGH"), "Email": raw}))
        cleaner.fix_emails()
        kept = cleaner.clean_df["Email"]
        assert kept.tolist() == ["ann@x.com", "bob@y.org", "ok@x.com", "q@z.co.uk"]
        assert _validate_email_series(kept) == 1.0

    def test_one_email_pattern_lives_in_constants(self):
        import inspect

        from utils import cleaner, constants, health_metrics

        assert isinstance(constants.EMAIL_PATTERN, str)
        for module in (cleaner, health_metrics):
            assert "EMAIL_PATTERN" in inspect.getsource(module)
            assert "@[a-zA-Z0-9.-]+" not in inspect.getsource(module), f"{module.__name__} carries its own email regex"

    def test_standardize_names_leaves_mixed_case_alone(self):
        """Only all-upper or all-lower names are re-cased; credentials and Mc/De prefixes survive (W06)."""
        names = ["Jimmy Freeman MD", "Brenda Hardin PhD", "jane doe", "JOHN ROE", "McDonald", "John Smith III"]
        cleaner = DataCleaner(pd.DataFrame({"Name": names}))
        cleaner.standardize_names()
        expected = ["Jimmy Freeman MD", "Brenda Hardin PhD", "Jane Doe", "John Roe", "McDonald", "John Smith III"]
        assert cleaner.clean_df["Name"].tolist() == expected

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
