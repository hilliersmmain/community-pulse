# Security scan cost record — 2026-09-27

A whole-repository scan with the `claude-security` plugin (v0.11.0), followed by drafted patch files. This file holds only wall clock, counts and the assumptions the run made. The report and the patch files are kept outside this public repository, and nothing from them appears here: no finding titles, no code, no paths.

## Wall clock

| Stage | Start (UTC) | End (UTC) | Minutes |
|---|---|---|---|
| Whole session, from `launched_at` to this record | 19:11:45 | ~20:52 | **~100** |
| Setup: reading the plugin's recipes, then a check on a second session running this same job | 19:11:45 | 19:15 | ~3 |
| Scan workflow (inventory → research → sweep → panel) | ~19:15 | ~19:27 | **11.7** (699.5 s, measured by the workflow) |
| Report writing and rendering | 19:27 | 19:30 | ~3 |
| Patch phase (generate → verify → attack-path check, one finding at a time) | 19:30 | 20:49 | **~79** |
| Closing (patch products, backup copy, this record, commit) | 20:49 | ~20:52 | ~3 |

The budget was the provisional 120 minutes from `launched_at`, and the run finished inside it. The cost probe's record (`llm-gateway-api/docs/security-scan-<date>.md`) did not exist when this run started, because that scan was still running in another tab. So there was no probe wall clock to scale from, and this is the first finished measurement.

**For budgeting the next scans:** the patch phase, not the scan, is the long pole. Each finding took 13 to 20 minutes when it went through generate, verify and the attack-path check: 3 to 8 minutes to generate, 4 to 10 to verify, and about 3 for the attack-path check. A finding the verifier rejects costs about the same again if it gets a revision round.

## Size and effort

- Target: 79 tracked files, about 5,600 lines of Python including tests.
- Scan effort: `medium`, the plugin's default. It covered the whole repository, with no scope and no attack-surface focus, because the tree is small.
- The session ran with ultracode on.

## Counts

- Scan: 38 agents. 15 researchers covered 4 components, plus a breadth sweep. They raised 9 candidates, which deduplicated to 6, and each of those went to a three-voter panel (18 votes).
- **Verified findings: 5.** 3 MEDIUM and 2 LOW; none CRITICAL or HIGH.
  - All 5 were confirmed 3/3. One candidate was rejected 0/3.
  - The panel lowered two severities.
- Stamped verification status: `verified`.
- **Patch files written: 3 of 5.** The three cover one root cause and are byte-identical, so applying one closes all three findings.
- **Declined: 2.** Both failed the verifier's "does not change behaviour" claim. Each decline note lays out the trade-off for Sam to decide.

## Tokens

These are subagent tokens, as the harness reported them in each completion notice. The main session's own tokens were not measured, because no status line was visible to this agent.

| Stage | Agents | Subagent tokens |
|---|---|---|
| Scan workflow | 38 | 2,366,179 |
| Patch phase | 13 | 1,046,908 |
| **Total subagent** | **51** | **3,413,087** |

## Assumptions and stops

1. **Start confirmation.** The plugin normally asks a fixed "this may take a while and use many tokens" question before a scan. It was not asked, because the prompt file Sam wrote for this session says in words that he understands the scan may take a long time and use a lot of tokens. That sentence was taken as the "Yes".
2. **An earlier attempt at this job was stopped.** A previous tab launched at 19:00:15Z for the same job. Its workflow launch was refused at a permission prompt that offered only "No", so that tab relaunched the job, this session, with ultracode on. Here the workflow started normally. The earlier attempt left an empty report folder that holds no findings. It is gitignored and was not deleted, because deletes need Sam's OK.
3. **Subagent model.** All subagents ran on opus, the session model. Sam's standing default is sonnet unless he calls a session heavy; ultracode was read as that call.
4. **One root cause, three findings.** Three of the five findings describe one root cause from different sites. After the first patch passed verification and the attack-path check, the next two generators were given it as a reference. Each still had its own independent verifier and attack-path check. The three patches came out byte-identical, so apply only one of them.
5. **Order.** The two LOW findings were attempted smaller-first, to fit the budget.
6. **Reset by re-cloning.** After a rejection, the plugin's recipe resets the scratch clone with `git reset --hard` and `git clean`. Both are forbidden on this machine, so the scratch was removed and re-cloned instead, which gives the same clean slate.
7. **No revision rounds for the two declines.** The recipe allows one revision round after a rejection.
   - First decline: every alternative the verifier offered was a trade-off Sam has to choose. The round was skipped, which left time for the last finding.
   - Second decline: the rejection came at 20:49, with 8 minutes left before the 20:57 cutoff set for the patch phase. There was no room for a round.
8. **Tests in the patch phase.** A scratch clone has no `venv/`, so each test suite ran with the main checkout's venv. Every verifier re-measured the baseline at 207 passed, 1 skipped.
9. **Nothing from the report reaches git.** Nothing was applied, committed or pushed. The report and patches stay in the gitignored report folder, with a byte-identical copy under `~/.claude/backups/security-scans/`. `git status --porcelain` was empty after both were written, so the report folder is invisible to git.
