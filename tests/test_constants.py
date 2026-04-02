"""Tests for constants module."""

from utils.constants import (
    DATA_PATH,
    DEFAULT_NUM_RECORDS,
    DEFAULT_MESSINESS,
    MESSINESS_OPTIONS,
    MIN_RECORDS,
    MAX_RECORDS,
    RECORDS_STEP,
    CLEANING_STEPS_DEFAULT,
    SCORE_THRESHOLDS,
    CUSTOM_CSS,
)


class TestConstants:
    def test_data_path_is_string(self):
        assert isinstance(DATA_PATH, str)
        assert DATA_PATH.endswith(".csv")

    def test_defaults_are_valid(self):
        assert DEFAULT_NUM_RECORDS == 500
        assert DEFAULT_MESSINESS in MESSINESS_OPTIONS
        assert MIN_RECORDS < MAX_RECORDS
        assert RECORDS_STEP > 0

    def test_messiness_options(self):
        assert MESSINESS_OPTIONS == ["low", "medium", "high"]

    def test_cleaning_steps_default(self):
        assert isinstance(CLEANING_STEPS_DEFAULT, dict)
        assert len(CLEANING_STEPS_DEFAULT) == 5
        assert all(v is True for v in CLEANING_STEPS_DEFAULT.values())

    def test_score_thresholds(self):
        assert SCORE_THRESHOLDS["excellent"] > SCORE_THRESHOLDS["good"]

    def test_custom_css_contains_style(self):
        assert "<style>" in CUSTOM_CSS
        assert "</style>" in CUSTOM_CSS
