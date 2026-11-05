# Security scan cost record — 2026-09-27

A whole-repository scan with the `claude-security` plugin (v0.11.0), followed by drafted patch files. This file holds only the wall clock, the size of the target and the token cost, as a budget record for later scans. The report and the patch files are kept outside this public repository, and nothing from them appears here: no findings, no finding counts or severities, no code, no paths.

## Wall clock

| Stage | Start (UTC) | End (UTC) | Minutes |
|---|---|---|---|
| Whole session, from `launched_at` to this record | 19:11:45 | ~20:52 | **~100** |
| Setup: reading the plugin's recipes, then a check on a second session running this same job | 19:11:45 | 19:15 | ~3 |
| Scan workflow (inventory → research → sweep → panel) | ~19:15 | ~19:27 | **11.7** (699.5 s, measured by the workflow) |
| Report writing and rendering | 19:27 | 19:30 | ~3 |
| Patch phase (generate → verify → attack-path check, one finding at a time) | 19:30 | 20:49 | **~79** |
| Closing (patch products, backup copy, this record, commit) | 20:49 | ~20:52 | ~3 |

The budget was the provisional 120 minutes from `launched_at`, and the run finished inside it. There was no earlier measurement to scale from, so this is the first finished one.

**For budgeting the next scans:** the patch phase, not the scan, is the long pole. Each finding took 13 to 20 minutes when it went through generate, verify and the attack-path check: 3 to 8 minutes to generate, 4 to 10 to verify, and about 3 for the attack-path check. A finding the verifier rejects costs about the same again if it gets a revision round.

## Size and effort

- Target: 79 tracked files, about 5,600 lines of Python including tests.
- Scan effort: `medium`, the plugin's default. It covered the whole repository, with no scope and no attack-surface focus, because the tree is small.
- The session ran with ultracode on.

## Tokens

These are subagent tokens, as the harness reported them in each completion notice. The main session's own tokens were not measured, because no status line was visible to this agent.

| Stage | Agents | Subagent tokens |
|---|---|---|
| Scan workflow | 38 | 2,366,179 |
| Patch phase | 13 | 1,046,908 |
| **Total subagent** | **51** | **3,413,087** |
