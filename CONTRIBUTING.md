# Contributing

Thanks for helping improve Community Pulse.

## Local Setup

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install black flake8 mypy pytest-cov pre-commit
pre-commit install
```

## Verification Loop (Required Before Commit)

Run the project verification loop before every commit:

```bash
python scripts/verify_loop.py --localhost-check
```

This loop runs:
- Black checks
- Flake8 linting
- Mypy type checks
- Full test suite
- Coverage gate
- Optional localhost Streamlit smoke test
- `CLAUDE.md` regeneration via `scripts/update_claude_md.py`

Cursor also includes a project hook (`.cursor/hooks.json`) that blocks `git commit` when verification is stale or when files changed since the last successful verification.

## Branch and PR Workflow

1. Create a feature branch: `git checkout -b feature/<short-name>`
2. Make focused changes in small commits.
3. Run `python scripts/verify_loop.py --localhost-check`.
4. Update docs when behavior changes (`README.md`, `docs/`, and generated `CLAUDE.md`).
5. Open a PR with:
   - What changed
   - Why it changed
   - Test evidence (commands + result)
   - Any follow-up tasks

## Coding Standards

- Line length: 120
- Format with Black
- Lint with Flake8
- Type-check with mypy
- Prefer small, testable functions and clear module boundaries
