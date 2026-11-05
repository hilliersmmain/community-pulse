"""Guard: every option in .streamlit/config.toml must be a real Streamlit option."""

from pathlib import Path

import streamlit.config as st_config

from utils.constants import MAX_UPLOAD_SIZE_MB

CONFIG_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "config.toml"


def _parse_toml(text: str) -> dict:
    """Parse TOML: tomllib on Python 3.11+, the `toml` package (a Streamlit dependency) on 3.10."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import toml

        return toml.loads(text)
    return tomllib.loads(text)


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


def unknown_options(config_path: Path) -> list[str]:
    """Return the dotted keys in a config file that Streamlit does not define.

    Streamlit warns on every run about an unknown option, and get_option raises RuntimeError
    ('Config key "..." not defined') for one.
    """
    unknown = []
    for name in _flatten(_parse_toml(config_path.read_text())):
        try:
            st_config.get_option(name)
        except RuntimeError:
            unknown.append(name)
    return unknown


def test_checker_flags_an_option_streamlit_does_not_define(tmp_path):
    """The check can fail: server.pythonVersion is the invalid option the project once shipped."""
    bad = tmp_path / "config.toml"
    bad.write_text('[server]\npythonVersion = "3.11"\n')
    assert unknown_options(bad) == ["server.pythonVersion"]


def test_checker_accepts_a_real_streamlit_option(tmp_path):
    good = tmp_path / "config.toml"
    good.write_text("[server]\nmaxUploadSize = 5\n")
    assert unknown_options(good) == []


def test_config_toml_exists_and_only_sets_valid_streamlit_options():
    assert CONFIG_PATH.is_file(), f"{CONFIG_PATH} is missing; docs/CONFIGURATION.md and docs/DEVELOPMENT.md list it"
    assert unknown_options(CONFIG_PATH) == []


def test_streamlit_itself_caps_uploads_at_the_apps_own_limit():
    """W17: Streamlit buffers up to 200 MB per upload by default, long before the app's own 5 MB check runs."""
    server = _parse_toml(CONFIG_PATH.read_text()).get("server", {})
    assert server.get("maxUploadSize") == MAX_UPLOAD_SIZE_MB
