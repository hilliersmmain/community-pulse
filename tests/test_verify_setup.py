"""Tests for the setup verifier (verify_setup.py at the repo root)."""

import collections
import importlib

import pytest

import verify_setup


@pytest.fixture
def broken_import(monkeypatch):
    """Make importing one named package raise `exc`; every other import behaves normally."""
    real_import_module = importlib.import_module

    def install(target, exc):
        def fake_import_module(name, *args, **kwargs):
            if name == target:
                raise exc
            return real_import_module(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", fake_import_module)

    return install


@pytest.mark.parametrize(
    "exc",
    [
        OSError("libnss3.so: cannot open shared object file"),
        ValueError("numpy.dtype size changed, may indicate binary incompatibility"),
        AttributeError("module 'numpy' has no attribute '_core'"),
    ],
    ids=["OSError", "ValueError", "AttributeError"],
)
def test_check_package_reports_non_import_errors(broken_import, exc):
    """A package whose import raises something other than ImportError is reported, not raised."""
    broken_import("kaleido", exc)

    ok, message = verify_setup.check_package("kaleido")

    assert ok is False
    assert "kaleido failed to import" in message
    assert str(exc) in message


def test_check_package_missing_package_still_says_not_installed(broken_import):
    broken_import("kaleido", ModuleNotFoundError("No module named 'kaleido'", name="kaleido"))

    ok, message = verify_setup.check_package("kaleido")

    assert (ok, message) == (False, "kaleido not installed")


def test_check_package_really_missing_package_says_not_installed():
    """No fake: the real importlib raises ModuleNotFoundError with name set for an absent package."""
    ok, message = verify_setup.check_package("no_such_package_for_verify_setup_test")

    assert (ok, message) == (False, "no_such_package_for_verify_setup_test not installed")


def test_check_package_installed_but_missing_native_library_is_not_called_not_installed(broken_import):
    """An ImportError that is not 'this package is absent' (here a missing shared library) is a broken install."""
    broken_import("kaleido", ImportError("libnss3.so: cannot open shared object file"))

    ok, message = verify_setup.check_package("kaleido")

    assert ok is False
    assert "failed to import" in message
    assert "libnss3" in message
    assert "not installed" not in message


def test_check_package_missing_transitive_import_is_not_called_not_installed(broken_import):
    """plotly is installed, but it needs tenacity: the missing module is tenacity, not plotly."""
    broken_import("plotly", ModuleNotFoundError("No module named 'tenacity'", name="tenacity"))

    ok, message = verify_setup.check_package("plotly")

    assert ok is False
    assert "plotly failed to import" in message
    assert "tenacity" in message
    assert "not installed" not in message


def test_main_still_prints_summary_when_an_optional_import_crashes(broken_import, capsys):
    """The real symptom: one crashing dependency used to kill the report before its Summary."""
    broken_import("kaleido", OSError("libnss3.so: cannot open shared object file"))

    verify_setup.main()

    output = capsys.readouterr().out
    assert "kaleido failed to import" in output
    assert "Summary" in output


VersionInfo = collections.namedtuple("VersionInfo", "major minor micro releaselevel serial")


def test_python_floor_is_3_10(monkeypatch):
    """pyproject.toml says requires-python >=3.10, so 3.9 fails the check and 3.10 passes it."""
    monkeypatch.setattr(verify_setup.sys, "version_info", VersionInfo(3, 9, 18, "final", 0))
    assert verify_setup.check_python_version() == (False, "Python 3.9.18 (requires 3.10+)")

    monkeypatch.setattr(verify_setup.sys, "version_info", VersionInfo(3, 10, 0, "final", 0))
    assert verify_setup.check_python_version() == (True, "Python 3.10.0")


def test_failure_footer_names_the_3_10_floor(monkeypatch, capsys):
    monkeypatch.setattr(verify_setup.sys, "version_info", VersionInfo(3, 9, 18, "final", 0))

    assert verify_setup.main() == 1
    assert "Ensure Python 3.10+ is installed" in capsys.readouterr().out


COMPONENT_MODULES = [
    "components.sidebar",
    "components.kpi_display",
    "components.comparison",
    "components.tab_preparation",
    "components.tab_analytics",
    "components.tab_explorer",
]


def test_imports_cover_every_components_module():
    checked = [module for module, _, _ in verify_setup.test_imports()]

    assert set(COMPONENT_MODULES) <= set(checked)


def test_project_structure_covers_the_components_package():
    checked = [item for item, _, _ in verify_setup.check_project_structure()]

    assert "components/" in checked
    assert {f"{module.replace('.', '/')}.py" for module in COMPONENT_MODULES} <= set(checked)


def test_main_fails_when_the_components_package_is_missing(broken_import, capsys):
    """A missing UI package used to leave every check green and print 'All checks passed'."""
    broken_import("components.sidebar", ModuleNotFoundError("No module named 'components'", name="components"))

    assert verify_setup.main() == 1
    output = capsys.readouterr().out
    assert "components.sidebar failed" in output
    assert "All checks passed" not in output
