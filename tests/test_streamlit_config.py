"""Guard: every option in .streamlit/config.toml must be a real Streamlit option."""

import tomllib
from pathlib import Path

import streamlit.config as st_config

CONFIG_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "config.toml"


def _flatten(table: dict, prefix: str = "") -> list[str]:
    """Return dotted option names for every leaf key in a parsed TOML table."""
    names: list[str] = []
    for key, value in table.items():
        dotted = f"{prefix}{key}"
        if isinstance(value, dict):
            names.extend(_flatten(value, f"{dotted}."))
        else:
            names.append(dotted)
    return names


def test_config_toml_only_sets_valid_streamlit_options():
    """Streamlit warns on every run about an unknown option; get_option raises for one."""
    if not CONFIG_PATH.exists():
        return  # no file, nothing can be invalid
    options = _flatten(tomllib.loads(CONFIG_PATH.read_text()))
    for name in options:
        # Unknown keys raise RuntimeError ('Config key "..." not defined').
        st_config.get_option(name)
