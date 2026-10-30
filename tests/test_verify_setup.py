"""Tests for the setup verifier (verify_setup.py at the repo root)."""

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
