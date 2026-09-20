In `~/Projects/community-pulse`, `pyproject.toml` points four of its five `[project.urls]`
entries at the wrong repository name. The repo on GitHub is `hilliersmmain/community-pulse`
(hyphen) — `git remote -v` and `gh repo view hilliersmmain/community-pulse` both confirm it,
and it is public, MIT and not archived. The URLs use `community_pulse` (underscore), which is
the Python package name.

They are not dead links, and that is the one thing to get right before editing: on
2026-09-20 `https://github.com/hilliersmmain/community_pulse` returned **301**, and following
it landed on `https://github.com/hilliersmmain/community-pulse` with **200**. GitHub is
serving a rename redirect. So the job is not "fix a 404" — it is that a public resume repo's
package metadata should carry the canonical URL, and a GitHub rename redirect is not
something to depend on: it breaks the moment anyone registers the old name.

These are the current lines, read on 2026-09-20:

```
56	[project.urls]
57	Homepage = "https://github.com/hilliersmmain/community_pulse"
58	"Live Demo" = "https://community-pulse.streamlit.app/"
59	Documentation = "https://github.com/hilliersmmain/community_pulse/tree/main/docs"
60	"Bug Tracker" = "https://github.com/hilliersmmain/community_pulse/issues"
61	"Source Code" = "https://github.com/hilliersmmain/community_pulse"
```

Line 58, the Streamlit demo link, is already correct — leave it alone. Lines 57, 59, 60 and
61 each need `community_pulse` changed to `community-pulse` **in the URL only**.

Do not do a blind find-and-replace of `community_pulse` across the file or the repo. It is
the real, correct Python package/distribution name in other contexts — `[project] name`, the
`community_pulse/` directory, `import community_pulse`, the coverage `source` list. Only the
string `github.com/hilliersmmain/community_pulse` is wrong. Re-read the lines yourself before
editing rather than trusting the quotes above; line numbers move.

Before committing, prove each change: for each of the four URLs, curl the old form and the
new form and compare status codes.

```
curl -s -o /dev/null -w '%{http_code}\n' <url>                          # unfollowed status
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' -L <url>      # where it lands
```

Run the unfollowed one first — `-L` alone hides a redirect by returning the final 200.

Expect the new form to return 200 directly with no redirect, and the old form to return 301
to the new one. If the old form ever returns 200 without redirecting, stop and report it:
that would mean a separate repo now occupies the underscore name, which changes what these
links point a reader at.

There is more of the same outside `pyproject.toml`. A grep on 2026-09-20 found 21
occurrences of `github.com/hilliersmmain/community_pulse` in 7 files: 4 in `pyproject.toml`,
7 in `docs/GITHUB_OPTIMIZATION.md`, 3 in `CHANGELOG.md`, 3 in `docs/DEVELOPMENT.md`, 2 in
`PORTFOLIO.md`, 1 in `docs/API.md`, 1 in `docs/ERROR_HANDLING.md`. Re-run the grep to get the
current figure:

```
command grep -rn 'github.com/hilliersmmain/community_pulse' . --exclude-dir=venv --exclude-dir=.git
```

Fix `pyproject.toml` first and commit that on its own. Then report what the grep found and
ask the maintainer whether the other six files are in scope before touching them — `CHANGELOG.md`'s
release links and `docs/DEVELOPMENT.md`'s clone command are reader-facing in a different way
from a metadata block, and `docs/GITHUB_OPTIMIZATION.md` is partly a document *about* badge
markup rather than live links.

Working notes for this repo:

- The venv is `venv/`, CPython 3.12. System Python is 3.14 and cannot install this repo's
  pinned numpy/pandas. Run tests as
  `PYTHONDONTWRITEBYTECODE=1 ./venv/bin/pytest -q -p no:cacheprovider`.
- `CLAUDE.md` and `.claude/` are gitignored here on purpose, so read `CLAUDE.md` for the
  project rules but expect it never to appear in a diff.
- Commit locally on `main`. **Do not push.** This is a public repo under the maintainer's real name;
  pushing is outward-facing and needs his explicit say-so in the session.
- When the job is genuinely finished, `git mv Prompts/fix-pyproject-repo-urls.md
  Prompts/Archived/` as part of finishing, and include it in the commit.
