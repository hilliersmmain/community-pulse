"""Tests for date_parsing module."""

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
