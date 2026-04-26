"""Test suite for UI helper functions.

Pure-Python message/template helpers are tested directly. Streamlit-rendering
helpers are exercised via ``streamlit.testing.v1.AppTest``, which spins up a
minimal scaffold script and lets us assert on rendered widgets and session
state without poking at Streamlit internals.
"""

import os
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from streamlit.testing.v1 import AppTest

from utils.ui_helpers import MESSAGES, get_contextual_message, show_info_tooltip

# ---------------------------------------------------------------------------
# Pure-Python helpers (no Streamlit context required)
# ---------------------------------------------------------------------------


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

    def test_get_contextual_message_dict_template_returns_empty_string(self):
        # Dict-shaped templates (empty-state messages) intentionally return ""
        # because they are not str.format-friendly.
        result = get_contextual_message("no_data_generated")
        assert result == ""

    def test_show_info_tooltip_format(self):
        result = show_info_tooltip("Test Text", "Tooltip content")
        assert "Test Text" in result
        assert "ⓘ" in result

    def test_show_info_tooltip_preserves_text_verbatim(self):
        # The function does not currently surface the tooltip body, but should
        # always preserve the visible label exactly as provided.
        for label in ["Hello", "Records: 42", ""]:
            result = show_info_tooltip(label, "anything")
            assert result.startswith(label)

    def test_empty_state_message_icons(self):
        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]
        for state in empty_states:
            assert state in MESSAGES
            assert "icon" in MESSAGES[state]
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
        assert "{records_processed}" in MESSAGES["cleaning_success"]
        assert "{num_records}" in MESSAGES["data_generated"]
        assert "{messiness}" in MESSAGES["data_generated"]
        assert "{step_count}" in MESSAGES["processing_cleaning"]

    def test_empty_state_titles_descriptive(self):
        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]
        for state in empty_states:
            title = MESSAGES[state]["title"]
            assert len(title) >= 10
            assert len(title) <= 100

    def test_empty_state_messages_helpful(self):
        empty_states = ["no_data_generated", "no_data_cleaned", "no_filters_selected", "empty_analytics"]
        for state in empty_states:
            message = MESSAGES[state]["message"]
            assert len(message) >= 20
            guidance_words = ["click", "select", "navigate", "run", "create", "generate", "clean"]
            assert any(word in message.lower() for word in guidance_words)


class TestMessageConsistency:
    def test_all_loading_messages_have_ellipsis(self):
        loading_messages = ["loading_data", "processing_cleaning", "calculating_metrics", "rendering_charts"]
        for msg_key in loading_messages:
            message = MESSAGES[msg_key]
            assert message.endswith("...") or message.endswith("…")

    def test_success_messages_positive(self):
        success_messages = ["cleaning_success", "data_generated", "export_ready"]
        positive_indicators = ["success", "ready", "completed", "generated"]
        for msg_key in success_messages:
            message = MESSAGES[msg_key].lower()
            assert any(indicator in message for indicator in positive_indicators)

    def test_no_duplicate_messages(self):
        string_messages = {k: v for k, v in MESSAGES.items() if isinstance(v, str)}
        values = list(string_messages.values())
        unique_values = set(values)
        assert len(unique_values) >= len(values) * 0.8


# ---------------------------------------------------------------------------
# AppTest-based tests: drive the helpers in a real Streamlit script context
# ---------------------------------------------------------------------------


class TestInitializeSessionState:
    """Verify ``initialize_session_state`` populates the four UX flags."""

    def test_initialize_sets_default_flags(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import initialize_session_state
            initialize_session_state()
            """)
        at = AppTest.from_string(script)
        at.run()
        assert at.exception == [] or len(at.exception) == 0
        assert at.session_state["show_welcome"] is True
        assert at.session_state["tutorial_mode"] is False
        assert at.session_state["tutorial_step"] == 0
        assert at.session_state["show_whats_new"] is False

    def test_initialize_does_not_overwrite_existing_values(self):
        # Simulate a returning user who has already dismissed the welcome modal:
        # initialize_session_state must leave their flags alone.
        script = textwrap.dedent("""
            import streamlit as st
            st.session_state["show_welcome"] = False
            st.session_state["tutorial_mode"] = True
            st.session_state["tutorial_step"] = 3
            st.session_state["show_whats_new"] = True
            from utils.ui_helpers import initialize_session_state
            initialize_session_state()
            """)
        at = AppTest.from_string(script)
        at.run()
        assert at.session_state["show_welcome"] is False
        assert at.session_state["tutorial_mode"] is True
        assert at.session_state["tutorial_step"] == 3
        assert at.session_state["show_whats_new"] is True


class TestShowWelcomeModal:
    """Drive the three buttons inside ``show_welcome_modal``."""

    SCAFFOLD = textwrap.dedent("""
        from utils.ui_helpers import initialize_session_state, show_welcome_modal
        initialize_session_state()
        show_welcome_modal()
        """)

    def test_modal_renders_three_buttons(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        labels = [b.label for b in at.button]
        assert "Dismiss" in labels
        assert "Start Tutorial" in labels
        assert "Get Started" in labels

    def test_modal_skipped_when_show_welcome_false(self):
        # When the flag is False the function returns early and renders nothing.
        script = textwrap.dedent("""
            import streamlit as st
            st.session_state["show_welcome"] = False
            from utils.ui_helpers import show_welcome_modal
            result = show_welcome_modal()
            st.write(f"result={result}")
            """)
        at = AppTest.from_string(script)
        at.run()
        # No buttons rendered — the modal short-circuited.
        assert len(at.button) == 0

    def test_dismiss_button_clears_show_welcome(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        # Find the Dismiss button by label and click it.
        for b in at.button:
            if b.label == "Dismiss":
                b.click()
                break
        at.run()
        assert at.session_state["show_welcome"] is False
        assert at.session_state["tutorial_mode"] is False

    def test_start_tutorial_button_enables_tutorial_mode(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        for b in at.button:
            if b.label == "Start Tutorial":
                b.click()
                break
        at.run()
        assert at.session_state["show_welcome"] is False
        assert at.session_state["tutorial_mode"] is True
        assert at.session_state["tutorial_step"] == 0

    def test_get_started_button_dismisses_without_tutorial(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.run()
        for b in at.button:
            if b.label == "Get Started":
                b.click()
                break
        at.run()
        assert at.session_state["show_welcome"] is False
        assert at.session_state["tutorial_mode"] is False


class TestShowEmptyState:
    """Verify ``show_empty_state`` renders text and the optional action button."""

    def test_empty_state_renders_title_and_message(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_empty_state
            show_empty_state(
                icon="X",
                title="Custom Title",
                message="Custom message body",
            )
            """)
        at = AppTest.from_string(script)
        at.run()
        # The HTML payload is sent through st.markdown — find the markdown block.
        rendered = "\n".join(m.value for m in at.markdown)
        assert "Custom Title" in rendered
        assert "Custom message body" in rendered
        assert "X" in rendered
        # No action button without action_label/action_callback
        assert len(at.button) == 0

    def test_empty_state_renders_action_button_and_invokes_callback(self):
        # Use a sentinel session_state key to confirm the callback ran on click.
        script = textwrap.dedent("""
            import streamlit as st
            from utils.ui_helpers import show_empty_state

            def _action():
                st.session_state["callback_fired"] = True

            show_empty_state(
                title="Need Data",
                message="Please generate",
                action_label="Do Thing",
                action_callback=_action,
            )
            """)
        at = AppTest.from_string(script)
        at.run()
        assert any(b.label == "Do Thing" for b in at.button)
        assert "callback_fired" not in at.session_state

        for b in at.button:
            if b.label == "Do Thing":
                b.click()
                break
        at.run()
        assert at.session_state["callback_fired"] is True

    def test_empty_state_default_arguments(self):
        # Calling with no kwargs must still render the default message.
        script = textwrap.dedent("""
            from utils.ui_helpers import show_empty_state
            show_empty_state()
            """)
        at = AppTest.from_string(script)
        at.run()
        rendered = "\n".join(m.value for m in at.markdown)
        assert "No Data Available" in rendered


class TestShowTutorialStep:
    """Cover the stepper in ``show_tutorial_step``."""

    @staticmethod
    def _scaffold(render_step: int) -> str:
        # The scaffold uses ``setdefault`` so the test can pre-load
        # ``session_state`` via ``AppTest.session_state[...] = ...`` and have it
        # persist across reruns triggered by button clicks.
        return textwrap.dedent(f"""
            import streamlit as st
            st.session_state.setdefault("tutorial_mode", False)
            st.session_state.setdefault("tutorial_step", 0)
            from utils.ui_helpers import show_tutorial_step
            show_tutorial_step({render_step})
            """)

    def test_tutorial_off_returns_false_no_widgets(self):
        at = AppTest.from_string(self._scaffold(render_step=0))
        at.session_state["tutorial_mode"] = False
        at.session_state["tutorial_step"] = 0
        at.run()
        assert len(at.button) == 0

    def test_tutorial_step_mismatch_renders_nothing(self):
        # tutorial_step=2 but the caller asks to render step 0 -> short-circuit
        at = AppTest.from_string(self._scaffold(render_step=0))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 2
        at.run()
        assert len(at.button) == 0

    def test_tutorial_step_match_renders_three_buttons(self):
        at = AppTest.from_string(self._scaffold(render_step=0))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 0
        at.run()
        labels = [b.label for b in at.button]
        # On step 0 there should be Skip + Next, no Previous yet.
        assert "Skip Tutorial" in labels
        assert "Next" in labels
        assert "Previous" not in labels

    def test_tutorial_step_advances_on_next(self):
        at = AppTest.from_string(self._scaffold(render_step=0))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 0
        at.run()
        for b in at.button:
            if b.label == "Next":
                b.click()
                break
        at.run()
        assert at.session_state["tutorial_step"] == 1

    def test_tutorial_step_previous_button_appears_after_step_zero(self):
        at = AppTest.from_string(self._scaffold(render_step=2))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 2
        at.run()
        labels = [b.label for b in at.button]
        assert "Previous" in labels
        for b in at.button:
            if b.label == "Previous":
                b.click()
                break
        at.run()
        assert at.session_state["tutorial_step"] == 1

    def test_tutorial_skip_disables_tutorial_mode(self):
        at = AppTest.from_string(self._scaffold(render_step=1))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 1
        at.run()
        for b in at.button:
            if b.label == "Skip Tutorial":
                b.click()
                break
        at.run()
        assert at.session_state["tutorial_mode"] is False

    def test_tutorial_completion_disables_mode_at_overflow(self):
        # 5 steps total (indices 0-4); step 5 triggers the completion branch.
        at = AppTest.from_string(self._scaffold(render_step=5))
        at.session_state["tutorial_mode"] = True
        at.session_state["tutorial_step"] = 5
        at.run()
        # Completion path disables tutorial_mode and renders a success message
        # with no buttons.
        assert at.session_state["tutorial_mode"] is False
        assert len(at.button) == 0


class TestShowWhatsNew:
    """Cover the What's New panel."""

    SCAFFOLD = textwrap.dedent("""
        import streamlit as st
        st.session_state.setdefault("show_whats_new", False)
        from utils.ui_helpers import show_whats_new
        show_whats_new()
        """)

    def test_whats_new_hidden_when_flag_false(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["show_whats_new"] = False
        at.run()
        assert len(at.button) == 0

    def test_whats_new_renders_dismiss_button(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["show_whats_new"] = True
        at.run()
        labels = [b.label for b in at.button]
        assert "Got it!" in labels

    def test_whats_new_dismiss_button_clears_flag(self):
        at = AppTest.from_string(self.SCAFFOLD)
        at.session_state["show_whats_new"] = True
        at.run()
        for b in at.button:
            if b.label == "Got it!":
                b.click()
                break
        at.run()
        assert at.session_state["show_whats_new"] is False


class TestNotificationHelpers:
    """Cover the success/error/warning/loading wrappers."""

    def test_show_loading_message_returns_spinner_context(self):
        # show_loading_message returns st.spinner(...) — verify it's a context
        # manager and the body executes.
        script = textwrap.dedent("""
            import streamlit as st
            from utils.ui_helpers import show_loading_message
            with show_loading_message("Working hard..."):
                st.write("inside-spinner")
            """)
        at = AppTest.from_string(script)
        at.run()
        rendered = "\n".join(m.value for m in at.markdown)
        assert "inside-spinner" in rendered

    def test_show_success_message_emits_st_success(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_success_message
            show_success_message("All good!")
            """)
        at = AppTest.from_string(script)
        at.run()
        success_messages = [s.value for s in at.success]
        assert any("All good!" in m for m in success_messages)

    def test_show_error_message_without_details(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_error_message
            show_error_message("Something broke")
            """)
        at = AppTest.from_string(script)
        at.run()
        error_messages = [e.value for e in at.error]
        assert any("Something broke" in m for m in error_messages)

    def test_show_error_message_with_details_renders_expander(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_error_message
            show_error_message("Cleaning failed", details="Traceback: ...")
            """)
        at = AppTest.from_string(script)
        at.run()
        # The details payload is rendered inside an st.code block.
        assert any("Traceback" in c.value for c in at.code)

    def test_show_warning_message_without_context(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_warning_message
            show_warning_message("Heads up")
            """)
        at = AppTest.from_string(script)
        at.run()
        warning_messages = [w.value for w in at.warning]
        assert any("Heads up" in m for m in warning_messages)

    def test_show_warning_message_with_context_emits_tip(self):
        script = textwrap.dedent("""
            from utils.ui_helpers import show_warning_message
            show_warning_message("Heads up", context="Try regenerating data")
            """)
        at = AppTest.from_string(script)
        at.run()
        info_messages = [i.value for i in at.info]
        assert any("Try regenerating data" in m for m in info_messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
