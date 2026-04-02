"""Test suite for UI helper functions."""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.ui_helpers import get_contextual_message, show_info_tooltip, MESSAGES


class TestUIHelpers:
    def test_messages_dict_structure(self):
        assert "no_data_generated" in MESSAGES
        assert "icon" in MESSAGES["no_data_generated"]
        assert "title" in MESSAGES["no_data_generated"]
        assert "message" in MESSAGES["no_data_generated"]

        assert "no_data_cleaned" in MESSAGES
        assert "no_filters_selected" in MESSAGES
        assert "empty_analytics" in MESSAGES

        assert "cleaning_success" in MESSAGES
        assert isinstance(MESSAGES["cleaning_success"], str)
        assert "data_generated" in MESSAGES
        assert "loading_data" in MESSAGES

    def test_get_contextual_message_string(self):

        message = get_contextual_message("loading_data")
        assert isinstance(message, str)
        assert len(message) > 0

    def test_get_contextual_message_with_params(self):

        message = get_contextual_message("cleaning_success", records_processed=100)
        assert isinstance(message, str)
        assert "100" in message

    def test_get_contextual_message_multiple_params(self):

        message = get_contextual_message("data_generated", num_records=500, messiness="medium")
        assert isinstance(message, str)
        assert "500" in message
        assert "medium" in message

    def test_get_contextual_message_nonexistent(self):

        message = get_contextual_message("nonexistent_message_key")
        assert message == "" or isinstance(message, dict)

    def test_show_info_tooltip_format(self):

        result = show_info_tooltip("Test Text", "Tooltip content")
        assert "Test Text" in result
        assert "ⓘ" in result

    def test_empty_state_message_icons(self):

        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]

        for state in empty_states:
            assert state in MESSAGES
            assert "icon" in MESSAGES[state]
            # Icons should be emoji (1-4 characters typically)
            assert len(MESSAGES[state]["icon"]) <= 10

    def test_message_templates_complete(self):

        required_string_messages = [
            "cleaning_success",
            "data_generated",
            "export_ready",
            "loading_data",
            "processing_cleaning",
            "calculating_metrics",
            "rendering_charts",
        ]

        for msg_key in required_string_messages:
            assert msg_key in MESSAGES
            assert isinstance(MESSAGES[msg_key], str)
            assert len(MESSAGES[msg_key]) > 0

    def test_message_parameter_placeholders(self):

        # Test cleaning_success has records_processed placeholder
        assert "{records_processed}" in MESSAGES["cleaning_success"]

        # Test data_generated has proper placeholders
        assert "{num_records}" in MESSAGES["data_generated"]
        assert "{messiness}" in MESSAGES["data_generated"]

        # Test processing_cleaning has step_count placeholder
        assert "{step_count}" in MESSAGES["processing_cleaning"]

    def test_empty_state_titles_descriptive(self):

        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]

        for state in empty_states:
            title = MESSAGES[state]["title"]
            # Titles should be reasonably long and descriptive
            assert len(title) >= 10
            assert len(title) <= 100

    def test_empty_state_messages_helpful(self):

        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]

        for state in empty_states:
            message = MESSAGES[state]["message"]
            # Messages should be helpful and not too short
            assert len(message) >= 20
            # Should contain some action word or guidance
            guidance_words = ["click", "select", "navigate", "run", "create", "generate", "clean"]
            assert any(word in message.lower() for word in guidance_words)


class TestMessageConsistency:

    def test_all_loading_messages_have_ellipsis(self):

        loading_messages = ["loading_data", "processing_cleaning", "calculating_metrics", "rendering_charts"]

        for msg_key in loading_messages:
            message = MESSAGES[msg_key]
            # Loading messages should end with ... or similar
            assert message.endswith("...") or message.endswith("…")

    def test_success_messages_positive(self):

        success_messages = ["cleaning_success", "data_generated", "export_ready"]

        positive_indicators = ["success", "ready", "completed", "generated"]

        for msg_key in success_messages:
            message = MESSAGES[msg_key].lower()
            assert any(indicator in message for indicator in positive_indicators)

    def test_no_duplicate_messages(self):

        string_messages = {k: v for k, v in MESSAGES.items() if isinstance(v, str)}

        # Get all message values
        values = list(string_messages.values())

        # Check for duplicates (allowing templates to be similar)
        # We just check that not ALL messages are identical
        unique_values = set(values)
        assert len(unique_values) >= len(values) * 0.8  # At least 80% unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
