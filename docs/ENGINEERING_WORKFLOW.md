# Engineering Workflow

This project uses a repeatable quality loop designed to keep changes merge-ready.

## Ralph-Style Verification Loop

For each meaningful change:

1. Make a small focused update.
2. Run targeted tests when possible.
3. Run full verification:
   - `python scripts/verify_loop.py --localhost-check`
4. Commit only after the loop succeeds.

## What `verify_loop.py` Checks

- Black formatting checks
- Flake8 linting checks
- Mypy type checks
- Full pytest suite
- Coverage gate (`--cov-fail-under=70`)
- Optional Streamlit localhost smoke test

## Subagent-Driven Delivery Pattern

When implementing larger tasks:

1. Use one implementer subagent per task.
2. Run a spec-compliance review subagent.
3. Run a code-quality review subagent.
4. Re-run verification loop before merging.

This keeps context clean while preserving quality gates.
