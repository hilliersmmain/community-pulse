"""The dev container must not turn off Streamlit's XSRF and CORS protection (scan F5, YC3)."""

import json
import re
from pathlib import Path

DEVCONTAINER = Path(__file__).resolve().parents[1] / ".devcontainer" / "devcontainer.json"


def _load() -> dict:
    # devcontainer.json allows // comments; json does not.
    return json.loads(re.sub(r"^\s*//.*$", "", DEVCONTAINER.read_text(), flags=re.MULTILINE))


def test_dev_container_keeps_xsrf_and_cors_protection_on():
    server = _load()["postAttachCommand"]["server"]
    assert server.startswith("streamlit run app.py")
    assert "enableXsrfProtection" not in server
    assert "enableCORS" not in server


def test_dev_container_opens_the_app_in_a_browser_tab():
    # The two flags existed for VS Code's embedded preview; a browser tab needs neither.
    assert _load()["portsAttributes"]["8501"]["onAutoForward"] == "openBrowser"
