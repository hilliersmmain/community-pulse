This session runs in `~/Projects/community-pulse`, link 1 of 2 of the community-pulse chain.
Nothing ran before it: `Prompts/` holds only this file, link 2 and `Archived/`. Mode `auto` —
the job edits application code and tests inside one public repo of mine; it touches no boot,
network, encryption or security control, publishes nothing for the first time, edits no
CLAUDE.md and makes no design choice I haven't made. Nobody is watching this tab: don't ask me
anything; where this prompt says stop, stop.

## The job, in my words

This repo has never had a `/code-review xhigh` here. Run one over the application code, fix
every finding the review confirms, get the suite fully green (it has one red test today —
finding zero, below), commit, push. Then hand off to link 2, the security scan, which has to
see reviewed code — the scan plugin refuses to patch from a report that no longer describes
the tree, so review-and-fix lands before the scan, never after. This is the second of two
chains I queued on 2026-09-27 to use the last of a Max window; a real review with real fixes.

## Established facts — use these, don't rediscover them

- HEAD was `2de715c` on `main`, tree clean, `main...origin/main` with nothing ahead, when this
  was written on 2026-09-27. `origin` is `https://github.com/hilliersmmain/community-pulse.git`,
  a PUBLIC repo. Re-run `git status --short --branch` yourself before relying on any of that.
- There is no `src/`. The application code is `community_pulse/` (98 lines), `components/`
  (807), `utils/` (1,352) and `app.py` (111). That set is the review target; a clean branch
  with no target reviews an empty diff.
- The `code-review` skill is model-invocable through the Skill tool in a session here (read
  back from a session's skill listing 2026-09-27): "Review the current diff, or a PR
  number/branch/path target ... at the given effort level ... `--fix` to apply the findings to
  the working tree after the review."
- The venv is `venv/` (not `.venv/`; its `.gitignore` line 2 is `venv/`). Measured 2026-09-27:
  `venv/bin/pytest tests/ -q` → `1 failed, 186 passed, 1 skipped`;
  `venv/bin/black --check --line-length=120 utils/ community_pulse/ tests/` → 24 files
  unchanged; `venv/bin/flake8 utils/ community_pulse/ --count --max-complexity=10
  --max-line-length=120 --ignore=E203,W503,E501 --statistics` → 0;
  `venv/bin/mypy utils/ community_pulse/ --ignore-missing-imports` → no issues in 12 files.
- **Finding zero, the red test:** `tests/test_visualizer.py::TestChartSnapshots::test_attendance_trend_snapshot`
  fails with `[attendance_trend.layout.annotations[0].text] mismatch: actual='Mean: 8.3 |
  Median: 8.5 | Total: 199' expected='Mean: 8.0 | Median: 8.0 | Total: 199'`. The same test
  passed at the same HEAD on 2026-09-20 locally (187 passed then) and on upstream CI run
  `35526471317` (`success`, 2026-09-20). So the cause is environment- or date-dependent, not the
  commit: installed plotly is 7.1.0 against a `plotly>=6.5.0` pin, and the sample data may be
  generated from today's date. Fix the cause; do not re-record the snapshot to match.
- Upstream CI (`.github/workflows/ci.yml`, Python 3.11 and 3.12) runs black, the two flake8
  passes, mypy, `pytest tests/ -v --tb=short`, a coverage run with `--cov-fail-under=70`, and
  bandit at `-lll -iii`. After your push read its conclusion with
  `gh run list -R hilliersmmain/community-pulse -L 1 --json databaseId,conclusion,headSha`.
- `gh run view --log` returns 0 bytes on this machine's gh 2.46.0. Read a job log with
  `gh api repos/hilliersmmain/community-pulse/actions/jobs/<job-id>/logs`; get the job id from
  `gh run view <run-id> -R hilliersmmain/community-pulse --json jobs -q '.jobs[] | "\(.databaseId) \(.name) \(.conclusion)"'`.
- The repo's `.gitignore` ignores `CLAUDE.md` (line 21) and `.claude/` (line 19) on purpose;
  the local CLAUDE.md is invisible to GitHub. Don't un-ignore either.
- Link 2 runs with the plugin's own orchestrator agent (`--agent claude-security:claude-security`,
  the `--` passthrough at the end of the chain block below). `cc-dispatch --dry-run` with that
  suffix was read back 2026-09-27: the flag lands before `--model`, as the launcher requires.
  Don't drop or move it.

## The work

1. `git status --short --branch`: clean and not behind. Run the suite, black, flake8 and mypy
   exactly as above and read the counts back. Hard stop if anything other than finding zero is
   red before you touch code: write what you saw, don't fix it, don't hand off.
2. Fix finding zero first, at its cause. Prove it by running that one test twice and the whole
   suite once: `1 failed` must become `0 failed`, `186 passed` must not drop.
3. Invoke the `code-review` skill with the argument
   `xhigh community_pulse/ components/ utils/ app.py`. Its subagents run on sonnet. Budget: 30
   minutes and roughly 350k subagent tokens (measured here 2026-09-13); if it is still running
   at 45 minutes, let it finish but do no other work meanwhile.
4. Fix every finding the review confirms as a correctness bug, and the reuse/simplification
   items where the change is local and mechanical. Leave alone, and list in the commit body as
   "logged, not fixed": anything that needs a design choice I haven't made, anything changing
   what the Streamlit app shows, anything outside the four target paths and `tests/`. Add or
   adjust a test for each bug fix.
5. Re-run the suite, black, flake8 and mypy. Passed count not below 187, skips not above 1.
6. Commit with a single-quoted or heredoc message (never backticks inside double quotes).
   `git push`. If it prompts for auth or fails, stop and say so rather than retrying blindly.
7. Confirm the new CI run on your commit reaches `success` with `gh run watch <run-id> -R
   hilliersmmain/community-pulse --exit-status` (give the Bash call a 10-minute timeout, never
   a foreground `sleep` loop). If it fails on a step your change touched, fix and push once
   more; if it fails only on the Codecov upload, that is not yours — say so and continue.

## Constraints

- `command grep`, never bare `grep`, in any command that decides something.
- Subagents run on sonnet, passed explicitly on every Agent call; scratch files go in this
  session's scratchpad directory, and nothing is written into the repo except the fixes, their
  tests and this file's move.
- Nothing here needs `sudo`, a browser or a hotkey.

## Done means

- `venv/bin/pytest tests/ -q` exits 0
- `venv/bin/flake8 utils/ community_pulse/ --count --select=E9,F63,F7,F82` exits 0
- `venv/bin/black --check --line-length=120 utils/ community_pulse/ tests/` exits 0
- **judgement:** finding zero is fixed at its cause, not by re-recording the snapshot
- **judgement:** every confirmed finding is either fixed with a test or listed as "logged, not
  fixed" with its reason in the commit body
- **judgement:** the CI run for the pushed commit reads `success`, or its only red step is the
  Codecov upload
- everything is committed and pushed; this file is `git mv`'d to `Prompts/Archived/`

## Then hand off

1. Run `/wrap` and apply its proposals on your judgement; say in one line what you dropped.
2. `git mv Prompts/01-auto-code-review-xhigh-and-fix-the-findings.md Prompts/Archived/ && git add -A && git commit -m 'link 01: code review xhigh and fixes' && git push`
3. Launch the next link:

```
cc-dispatch --chain --model opus --advisor fable --mode auto \
  --title "community-pulse link 2 of 2: security scan + draft patches" \
  --cwd ~/Projects/community-pulse \
  --check 'venv/bin/pytest tests/ -q' \
  --check 'venv/bin/flake8 utils/ community_pulse/ --count --select=E9,F63,F7,F82' \
  --prompt Prompts/02-auto-security-scan-the-repo-and-draft-patches.md \
  -- --agent claude-security:claude-security
```

Show me the line you ran and say the tab is open. Give the clock time and the next link's
expected cost: provisionally 120 minutes of opus with a fable advisor, to be revised from the
llm-gateway-api probe's `docs/security-scan-<date>.md` if that chain has already run — read it
if it exists and quote its wall clock instead. Hard stops — don't launch, say what blocked the
chain and stop: dispatch-session's generic ones; anything under "Done means" unmet; a red
suite at any point after your fixes; a review that never returned findings (an empty result is
a finding to write down, not a reason to re-run).
