"""The Black version must be the same everywhere it is named.

CI, the pre-commit hook, requirements-dev.txt and pyproject.toml each pin Black on their own line. A formatter that
differs between the hook and CI reformats files the other one accepts, so the four pins are compared with each other.
The files are read as text (PyYAML is not in requirements.txt and tomllib needs Python 3.11).
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIN = r"black==(\d+(?:\.\d+)+)"


def exact_pins(relative_path):
    """Every `black==X` version named in the file."""
    return re.findall(PIN, (ROOT / relative_path).read_text())


def precommit_black_rev():
    """The `rev:` that follows the psf/black repo line in .pre-commit-config.yaml."""
    text = (ROOT / ".pre-commit-config.yaml").read_text()
    match = re.search(r"repo:\s*https://github\.com/psf/black\s*\n\s*rev:\s*v?(\d+(?:\.\d+)+)", text)
    assert match, "no psf/black repo with a rev in .pre-commit-config.yaml"
    return match.group(1)


def test_ci_pins_black_exactly():
    assert len(exact_pins(".github/workflows/ci.yml")) == 1, "ci.yml must install black==X exactly once"


@pytest.mark.parametrize("path", ["requirements-dev.txt", "pyproject.toml"])
def test_dev_requirements_pin_black_exactly(path):
    assert len(exact_pins(path)) == 1, f"{path} must name black==X exactly once (a >= floor lets it drift from CI)"


@pytest.mark.parametrize("path", ["requirements-dev.txt", "pyproject.toml", ".pre-commit-config.yaml"])
def test_every_black_pin_matches_ci(path):
    ci = exact_pins(".github/workflows/ci.yml")
    assert ci, "ci.yml names no black==X"
    here = [precommit_black_rev()] if path == ".pre-commit-config.yaml" else exact_pins(path)
    assert here == ci, f"{path} pins black {here}, ci.yml pins {ci}"
