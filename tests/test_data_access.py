"""Tests for the mtime-keyed CSV read cache in utils.data_access."""

import os

import pandas as pd
import pytest

import utils.data_access as da


@pytest.fixture(autouse=True)
def fresh_read_cache():
    """The st.cache_data store is global to the process: empty it around every test."""
    da._read_csv_cached.clear()
    yield
    da._read_csv_cached.clear()


def test_read_cache_is_bounded(monkeypatch):
    """Each new mtime is a new cache key; old keys must be evicted, not kept forever.

    'Generate New Data' rewrites the CSV without save_csv's cache clear, so every
    click adds a key. Count real reads: with max_entries=2, the first key is evicted
    by the third and the fourth call (key 1.0 again) has to re-read.
    """
    reads: list[str] = []

    def fake_read_csv(path):
        reads.append(path)
        return pd.DataFrame({"a": [1]})

    monkeypatch.setattr(da.pd, "read_csv", fake_read_csv)

    for mtime in (1.0, 2.0, 3.0, 1.0):
        da._read_csv_cached("bounded-cache-probe.csv", mtime)
    assert len(reads) == 4  # unbounded cache would stop at 3: key 1.0 never evicted

    # Guard against "bounded" meaning "not cached at all": a repeat key is a hit.
    da._read_csv_cached("bounded-cache-probe.csv", 1.0)
    assert len(reads) == 4


def test_load_csv_sees_out_of_band_rewrite(tmp_path):
    """load_csv must pick up a file rewritten without save_csv (the Generate button).

    The mtime argument is the only invalidation on that path: a constant key would
    serve the stale first frame forever.
    """
    path = tmp_path / "data.csv"

    path.write_text("a\n1\n")
    os.utime(path, (1_000_000_000.0, 1_000_000_000.0))
    assert len(da.load_csv(str(path))) == 1

    path.write_text("a\n1\n2\n3\n")  # out of band: no save_csv, no cache clear
    os.utime(path, (1_000_000_005.0, 1_000_000_005.0))
    assert len(da.load_csv(str(path))) == 3
