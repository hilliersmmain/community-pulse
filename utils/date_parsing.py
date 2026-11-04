"""Parse date columns that mix several formats."""

from __future__ import annotations

import pandas as pd

from utils.constants import DATE_FORMATS, MAX_DATE_CHARS


def parse_dates(values: pd.Series) -> pd.Series:
    """Parse a column of dates written in any of ``DATE_FORMATS``.

    Given no format, pandas infers one from the first value and turns every value in
    another format into NaT, so the result would depend on row order. Instead each
    format gets its own pass over whatever the earlier passes left unparsed, then a
    last per-value pass (``format="mixed"``) reads anything else it can. Values
    nothing can read, such as ``"Unknown"``, become NaT. Timestamps that carry a UTC offset are
    converted to UTC and returned without a zone, so the result is always ``datetime64[ns]``. A cell longer than
    ``MAX_DATE_CHARS`` is not tried at all and stays NaT: the ``"mixed"`` pass takes time
    quadratic in cell length, so one huge cell would stall the app.
    """
    if pd.api.types.is_datetime64_any_dtype(values):
        return values
    parsed = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")
    readable = values.notna() & (values.astype(str).str.len() <= MAX_DATE_CHARS)
    for date_format in [*DATE_FORMATS, "mixed"]:
        pending = parsed.isna() & readable
        if not pending.any():
            break
        # utc=True turns every offset into UTC, so one pass never yields a column of mixed zones (pandas would
        # give an object column of tz-aware Timestamps); tz_localize(None) then drops the zone. Cells with no
        # offset are read as UTC and come back unchanged.
        read = pd.to_datetime(values[pending], format=date_format, errors="coerce", utc=True)
        parsed[pending] = read.dt.tz_localize(None)
    return parsed
