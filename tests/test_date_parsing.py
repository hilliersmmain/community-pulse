"""Tests for date_parsing module."""

import warnings

import pandas as pd

from utils.constants import MAX_DATE_CHARS
from utils.date_parsing import parse_dates


class TestParseDates:
    """Tests for parse_dates."""

    def test_over_long_cell_is_skipped_not_parsed(self, monkeypatch):
        # pandas' format="mixed" pass is quadratic in cell length; a 200,000-character cell in a date column
        # used to stall for many seconds (minutes at the 5 MB upload cap). Asserted structurally, not by
        # wall-clock: no value longer than MAX_DATE_CHARS may ever reach pd.to_datetime.
        seen_lengths: list[int] = []
        real_to_datetime = pd.to_datetime

        def spy(arg, *args, **kwargs):
            values = arg if isinstance(arg, (pd.Series, list)) else [arg]
            seen_lengths.extend(len(str(v)) for v in values)
            return real_to_datetime(arg, *args, **kwargs)

        monkeypatch.setattr(pd, "to_datetime", spy)
        values = pd.Series(["1" * 5000, "2024-01-05"])

        out = parse_dates(values)

        assert seen_lengths, "parse_dates never called pd.to_datetime, so this test checks nothing"
        assert max(seen_lengths) <= MAX_DATE_CHARS, f"a {max(seen_lengths)}-character cell reached pd.to_datetime"
        assert out.isna().tolist() == [True, False]
        assert out.iloc[1] == pd.Timestamp("2024-01-05")
        assert str(out.dtype) == "datetime64[ns]"

    def test_normal_cells_still_parse_beside_an_over_long_one(self):
        values = pd.Series(["1" * 200_000, "2024-01-05", "01/06/2024", "07-01-2024", "Jan 8, 2024", "Unknown", None])
        out = parse_dates(values)
        assert out.isna().tolist() == [True, False, False, False, False, True, True]
        assert out.iloc[1:5].tolist() == [
            pd.Timestamp("2024-01-05"),
            pd.Timestamp("2024-01-06"),
            pd.Timestamp("2024-01-07"),
            pd.Timestamp("2024-01-08"),
        ]

    def test_timestamps_with_two_utc_offsets_parse_to_one_naive_column(self):
        """W02: offsets across a DST change used to come back as an object column of tz-aware Timestamps."""
        values = pd.Series(["2023-01-05T10:30:00-05:00", "2023-07-05T10:30:00-04:00"])
        with warnings.catch_warnings():
            warnings.simplefilter("error")  # the old code also raised pandas FutureWarnings
            out = parse_dates(values)
        assert pd.api.types.is_datetime64_any_dtype(out)
        assert out.dt.tz is None
        assert out.dt.month.tolist() == [1, 7]
        # Offsets are converted to UTC, then the zone is dropped: 10:30-05:00 is 15:30 UTC, 10:30-04:00 is 14:30 UTC.
        assert out.tolist() == [pd.Timestamp("2023-01-05 15:30"), pd.Timestamp("2023-07-05 14:30")]

    def test_one_offset_everywhere_and_naive_plus_offset_also_give_datetimes(self):
        same = parse_dates(pd.Series(["2023-01-05T10:30:00-05:00", "2023-02-05T09:00:00-05:00"]))
        assert str(same.dtype) == "datetime64[ns]"
        mixed = parse_dates(pd.Series(["2023-01-05", "2023-07-05T10:30:00-04:00", "Unknown"]))
        assert str(mixed.dtype) == "datetime64[ns]"
        assert mixed.tolist()[:2] == [pd.Timestamp("2023-01-05"), pd.Timestamp("2023-07-05 14:30")]
        assert mixed.isna().tolist() == [False, False, True]

    def test_naive_dates_are_left_exactly_as_they_were(self):
        out = parse_dates(pd.Series(["2024-01-05", "01/06/2024", "07-01-2024"]))
        assert out.tolist() == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-06"), pd.Timestamp("2024-01-07")]
