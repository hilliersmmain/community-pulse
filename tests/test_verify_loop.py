"""Tests for scripts/verify_loop.py.

scripts/ is not a package, so the script is loaded by path. The check_localhost tests talk to throwaway servers on
127.0.0.1 over real sockets (no Streamlit): a port that never answers, one that resets the connection, one that
answers with garbage, and one that answers 500. The lint-step tests compare the script with .github/workflows/ci.yml.
"""

import contextlib
import importlib.util
import socket
import subprocess
import threading
import urllib.request
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "verify_loop.py"
CI_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"

# The flags that change what a lint step accepts. Reporting-only flags (--count, --statistics) are left out.
COMPARED_FLAGS = ("--check", "--line-length=", "--max-line-length=", "--max-complexity=", "--ignore=")
COMPARED_FLAGS += ("--ignore-missing-imports",)


@pytest.fixture(scope="module")
def verify_loop():
    spec = importlib.util.spec_from_file_location("verify_loop", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def short_request_timeout(verify_loop, monkeypatch):
    """check_localhost hard-codes a 2 s per-request timeout; shorten it so a hung port costs 0.3 s, not 2 s."""
    real_urlopen = urllib.request.urlopen
    monkeypatch.setattr(verify_loop, "urlopen", lambda url, timeout=2: real_urlopen(url, timeout=min(timeout, 0.3)))


@contextlib.contextmanager
def listener(handler=None):
    """Bind 127.0.0.1 on a free port; yield (url, hits).

    Without a handler the socket only listens: the kernel completes the TCP handshake from the backlog but nothing
    ever reads the request or answers, so the failure lands in the response read, not in connect. With a handler, a
    daemon thread accepts each connection, counts it, runs handler(conn) and closes it.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stop = threading.Event()
    hits: list = []
    thread = None
    try:
        server.bind(("127.0.0.1", 0))
        server.listen(1 if handler is None else 5)
        if handler is not None:
            server.settimeout(0.1)

            def serve():
                while not stop.is_set():
                    try:
                        conn, _ = server.accept()
                    except socket.timeout:
                        continue
                    except OSError:
                        return
                    hits.append(1)
                    with contextlib.closing(conn):
                        handler(conn)

            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
        yield f"http://127.0.0.1:{server.getsockname()[1]}", hits
    finally:
        stop.set()
        if thread is not None:
            thread.join(timeout=2)
        server.close()


def reset_connection(conn):
    """Close without reading the request: the client sees a reset or an empty reply, never a response."""


def reply_with_garbage(conn):
    conn.settimeout(1)
    conn.recv(4096)
    conn.sendall(b"this is not http\r\n\r\n")


def reply_with(status_line):
    def handler(conn):
        conn.settimeout(1)
        conn.recv(4096)
        conn.sendall(f"HTTP/1.1 {status_line}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode())

    return handler


def test_returns_true_when_server_answers_200(verify_loop):
    with listener(reply_with("200 OK")) as (url, _):
        assert verify_loop.check_localhost(url, timeout_seconds=2) is True


def test_returns_false_for_a_port_that_never_answers(verify_loop):
    """Read timeout (TimeoutError, an OSError): used to escape as a raw traceback instead of retrying."""
    with listener() as (url, _):
        assert verify_loop.check_localhost(url, timeout_seconds=1) is False


def test_returns_false_when_the_server_resets_the_connection(verify_loop):
    """ConnectionResetError / RemoteDisconnected: used to escape on the first attempt."""
    with listener(reset_connection) as (url, hits):
        assert verify_loop.check_localhost(url, timeout_seconds=1) is False
    assert hits, "the server never saw a connection, so this test did not exercise the reset path"


def test_returns_false_when_the_server_answers_something_that_is_not_http(verify_loop):
    """http.client.BadStatusLine is an HTTPException, not an OSError: needs its own except branch."""
    with listener(reply_with_garbage) as (url, hits):
        assert verify_loop.check_localhost(url, timeout_seconds=1) is False
    assert hits


def test_a_500_is_retried_with_a_pause_not_in_a_busy_loop(verify_loop):
    """urlopen raises HTTPError (a URLError) for 5xx; that path already sleeps 1 s between attempts."""
    with listener(reply_with("500 Internal Server Error")) as (url, hits):
        assert verify_loop.check_localhost(url, timeout_seconds=2) is False
    assert 1 <= len(hits) <= 4


def ci_args(tool, must_contain=None):
    """The arguments after `tool` on the one ci.yml line that runs it (and contains `must_contain`)."""
    lines = [raw.strip().split() for raw in CI_PATH.read_text().splitlines()]
    matches = [t for t in lines if t[:1] == [tool] and (must_contain is None or any(must_contain in x for x in t))]
    assert len(matches) == 1, f"expected one {tool} line with {must_contain!r} in ci.yml, found {len(matches)}"
    return matches[0][1:]


def script_args(verify_loop, label, strict=False):
    """The arguments after `python -m <tool>` of the verify_loop step whose label starts with `label`."""
    [command] = [cmd for step, cmd in verify_loop.lint_steps(strict) if step.startswith(label)]
    return command[3:]


def lint_paths(args):
    """The paths a lint command covers: its non-flag arguments, minus any trailing slash."""
    return {a.rstrip("/") for a in args if not a.startswith("-")}


def compared_flags(args):
    return {a for a in args if a.startswith(COMPARED_FLAGS)}


@pytest.mark.parametrize(
    "tool, ci_marker",
    [("black", "--check"), ("flake8", "--max-complexity"), ("mypy", None)],
)
def test_default_lint_steps_cover_what_ci_covers(verify_loop, tool, ci_marker):
    """The documented pre-PR gate must not pass what CI rejects: same paths and same rule flags per tool."""
    ci = ci_args(tool, ci_marker)
    local = script_args(verify_loop, tool)

    assert lint_paths(ci), f"no paths parsed from the ci.yml {tool} line"
    assert lint_paths(local) == lint_paths(ci)
    assert compared_flags(local) == compared_flags(ci)


def test_strict_also_lints_tests(verify_loop):
    for tool in ("flake8", "mypy"):
        default = lint_paths(script_args(verify_loop, tool))
        strict = lint_paths(script_args(verify_loop, tool, strict=True))
        assert "tests" not in default
        assert strict == default | {"tests"}


def test_normalized_changed_files_keeps_the_first_porcelain_path_whole(verify_loop, monkeypatch):
    """Review overflow O04: get_git_output stripped the first porcelain line's leading space, so ' M app.py' read as 'pp.py'."""
    porcelain = " M app.py\n?? notes.txt\nR  old.py -> new.py\n"
    monkeypatch.setattr(
        verify_loop.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 0, stdout=porcelain, stderr=""),
    )
    assert verify_loop.normalized_changed_files() == ["app.py", "new.py", "notes.txt"]
