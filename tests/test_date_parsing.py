"""Tests for date_parsing module."""

import time

import pandas as pd

from utils.date_parsing import parse_dates


class TestParseDates:
    """Tests for parse_dates."""

    def test_over_long_cell_is_skipped_not_parsed(self):
        # pandas' format="mixed" pass is quadratic in cell length; a 200,000-character cell
        # in a date column used to stall for many seconds (minutes at the 5 MB upload cap).
        values = pd.Series(["1" * 200_000, "2024-01-05"])
        start = time.perf_counter()
        out = parse_dates(values)
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"parse_dates took {elapsed:.1f}s on one over-long cell"
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
