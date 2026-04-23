#!/usr/bin/env python3
"""Cursor hook: remind/ask before git commit if verification is stale."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VERIFY_STATE_PATH = PROJECT_ROOT / ".verification" / "last_verify_success.json"
MAX_AGE_HOURS = 4


def output(payload: dict) -> None:
    print(json.dumps(payload))


def parse_timestamp(raw: str) -> datetime | None:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_git_output(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def normalized_changed_files() -> list[str]:
    """Return changed file paths without staged/unstaged status prefixes."""
    lines = get_git_output("status", "--porcelain").splitlines()
    paths: set[str] = set()
    for line in lines:
        if len(line) < 4:
            continue
        raw_path = line[3:].strip()
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", maxsplit=1)[1].strip()
        if raw_path:
            paths.add(raw_path)
    return sorted(paths)


def current_changed_files_hash() -> str:
    changed = normalized_changed_files()
    return hashlib.sha256("\n".join(changed).encode("utf-8")).hexdigest()


def is_stale() -> tuple[bool, str]:
    if not VERIFY_STATE_PATH.exists():
        return True, "No verification record found."

    try:
        payload = json.loads(VERIFY_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True, "Verification record is unreadable."

    verified_at = parse_timestamp(payload.get("verified_at_utc", ""))
    if verified_at is None:
        return True, "Verification record is missing a valid timestamp."

    threshold = datetime.now(timezone.utc) - timedelta(hours=MAX_AGE_HOURS)
    if verified_at < threshold:
        return True, f"Last verification is older than {MAX_AGE_HOURS} hours."
    if payload.get("git_head", "") != get_git_output("rev-parse", "HEAD"):
        return True, "HEAD changed since last verification."
    if payload.get("changed_files_hash", "") != current_changed_files_hash():
        return True, "Working tree changed since last verification."
    return False, "Verification record is fresh."


def main() -> None:
    raw = sys.stdin.read() or "{}"
    try:
        event = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        output(
            {
                "permission": "ask",
                "user_message": (
                    "Could not parse commit-hook input. Run `python scripts/verify_loop.py --localhost-check` "
                    "before committing."
                ),
                "agent_message": "Commit hook received malformed event payload.",
            }
        )
        return
    command = event.get("command", "")

    if "git commit" not in command:
        output({"permission": "allow"})
        return

    stale, reason = is_stale()
    if stale:
        output(
            {
                "permission": "ask",
                "user_message": (
                    f"{reason} Run `python scripts/verify_loop.py --localhost-check` before commit "
                    "to confirm tests/docs/CLAUDE.md are current."
                ),
                "agent_message": "Commit gated by local verification freshness hook.",
            }
        )
        return

    output({"permission": "allow"})


if __name__ == "__main__":
    main()
