# Configuration Guide

Community Pulse has two places where its behaviour is set:

1. **Code constants** in `utils/constants.py`, for everything the app itself decides (record counts, upload
   limits, cleaning defaults, score weights and thresholds).
2. **Streamlit's own options**, for the web server. The repository sets exactly one of them, in
   `.streamlit/config.toml`.

The app reads no environment variables of its own, no `.env` file and no Streamlit secrets. A variable such as
`LOG_LEVEL` or `DEFAULT_NUM_RECORDS` set in the shell changes nothing. The one environment switch in the
repository is `UPDATE_SNAPSHOTS=1`, read by `tests/test_visualizer.py` to rewrite the chart snapshots.

---

## Streamlit Configuration File

`.streamlit/config.toml` sets one option:

```toml
[server]
maxUploadSize = 5
```

`server.maxUploadSize` is in megabytes. With it, Streamlit refuses a larger upload itself, instead of buffering up
to its default of 200 MB in server memory before the app's own size check runs. Keep it equal to
`MAX_UPLOAD_SIZE_MB` in `utils/constants.py`; `tests/test_streamlit_config.py` checks that the two match and that
every key in the file is an option Streamlit defines.

Every other server option stays at Streamlit's default. Leave `server.enableCORS` and
`server.enableXsrfProtection` at their defaults (both on): turning CORS off lets any origin open the app's
WebSocket.

### Setting other Streamlit options

Streamlit reads each option from these places; a later one overrides an earlier one:

1. Streamlit's built-in default
2. the global `~/.streamlit/config.toml`
3. the project's `.streamlit/config.toml`
4. an environment variable named `STREAMLIT_<SECTION>_<OPTION>`, for example `STREAMLIT_SERVER_PORT`
5. a command-line flag passed to `streamlit run`

So a one-off port change needs no file edit:

```bash
streamlit run app.py --server.port 8502
# or
STREAMLIT_SERVER_PORT=8502 streamlit run app.py
```

`streamlit config show` prints the value each option ends up with. The full list of options is in the
[Streamlit configuration documentation](https://docs.streamlit.io/develop/api-reference/configuration/config.toml).

---

## Application Constants

All of these live in `utils/constants.py`. Change the constant, not a literal in the code that uses it.

### Sample data generator (sidebar)

| Constant | Value | Used for |
|---|---|---|
| `DEFAULT_NUM_RECORDS` | `500` | Starting value of the "Number of Records" slider |
| `MIN_RECORDS` / `MAX_RECORDS` | `100` / `1000` | Slider range |
| `RECORDS_STEP` | `50` | Slider step |
| `DEFAULT_MESSINESS` | `"medium"` | Starting value of the "Messiness Level" box |
| `MESSINESS_OPTIONS` | `["low", "medium", "high"]` | Choices in that box |

### Uploads

| Constant | Value | Effect |
|---|---|---|
| `MAX_UPLOAD_SIZE_MB` | `5` | A larger file is refused (and `server.maxUploadSize` above stops it earlier) |
| `MAX_UPLOAD_COLUMNS` | `50` | A header with more fields is refused before the file is parsed |
| `MAX_UPLOAD_ROWS` | `50000` | A file with more rows is refused |
| `REQUIRED_COLUMNS` | see [Data Schema](#data-schema) | A file missing any of them is refused |

### Health score

| Constant | Value |
|---|---|
| `HEALTH_SCORE_WEIGHT_COMPLETENESS` | `0.4` |
| `HEALTH_SCORE_WEIGHT_UNIQUENESS` | `0.3` |
| `HEALTH_SCORE_WEIGHT_FORMATTING` | `0.3` |
| `SCORE_THRESHOLDS` | `{"excellent": 90, "good": 70}` |

The three weights must sum to 1.0. [KPI_DEFINITIONS.md](./KPI_DEFINITIONS.md) describes the scores.

### Parsing and validation

| Constant | What it holds |
|---|---|
| `DATE_FORMATS` | `["ISO8601", "%m/%d/%Y", "%d-%m-%Y"]`, tried in that order before a last per-value pass |
| `MAX_DATE_CHARS` | `64`: a longer date cell is not parsed and stays blank |
| `EMAIL_PATTERN` | The one email shape used by both the cleaner and the Formatting score |
| `NAME_PATTERN` | Letters in any script, spaces, apostrophes, full stops and hyphens |

---

## Data Schema

An uploaded CSV must have these columns (`REQUIRED_COLUMNS`), spelled exactly like this:

```python
REQUIRED_COLUMNS = ["Name", "Email", "Role", "Join_Date", "Event_Attendance"]
```

Other columns are kept. The sample generator also writes `ID`, `Last_Login`, `Event_Registered` and
`Registration_Date`. The file must be comma-delimited; when a semicolon-, tab- or pipe-delimited header is read
as one column, the error message names the delimiter.

Data is held in the browser session only (`st.session_state`); nothing is written to the server's disk.

---

## Cleaning Pipeline

The five steps run in this order. Each one can be switched off in the sidebar under **Cleaning Pipeline →
Configure Cleaning Steps** (all are on by default, from `CLEANING_STEPS_DEFAULT`); **Run Cleaning Algorithms** on
the preparation tab runs the ones that are ticked.

1. **standardize_names**: a `Name` that is all upper case or all lower case is put in Title Case. Mixed-case names
   are left alone, and spacing is not changed.
2. **fix_emails**: each `Email` is lower-cased and stripped, `" at "` becomes `"@"`, and a row whose email is
   missing or still does not match `EMAIL_PATTERN` is dropped.
3. **remove_duplicates**: a row whose `Email` (lower-cased, surrounding spaces ignored) repeats an earlier row is
   dropped; the first is kept. Rows with no email are never treated as duplicates. Without an `Email` column whole
   rows are compared.
4. **clean_dates**: `Join_Date` only is parsed to a date. A value nothing can read is left blank, not guessed.
5. **handle_missing_values**: `Event_Attendance` only: a value that is missing or not a number becomes `0`. Other
   columns keep their missing values.

---

## Testing Configuration

pytest's settings are in `pyproject.toml` (`[tool.pytest.ini_options]`), and the coverage source list is in
`[tool.coverage.run]`.

```bash
# Run all tests (keeps __pycache__ folders out of the tree)
PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider

# With coverage, using the source list from pyproject.toml
pytest --cov --cov-report=term

# One file, or tests matching a pattern
pytest tests/test_cleaner.py
pytest -k "email"
```

Tests build their own data in memory or in temporary folders; no data file has to exist first.

---

## Deployment Configuration

### Streamlit Community Cloud

The live app needs only what is in the repository:

- `requirements.txt` for the Python packages
- `.streamlit/config.toml` for the upload cap above

No environment variables or secrets are needed.

### Docker

The repository has no Dockerfile. [DEVELOPMENT.md](./DEVELOPMENT.md#docker-deployment) has a minimal one to start
from.

---

## Further Reading

- [Streamlit configuration options](https://docs.streamlit.io/develop/api-reference/configuration/config.toml)
- [KPI_DEFINITIONS.md](./KPI_DEFINITIONS.md) for the scores
- [ERROR_HANDLING.md](./ERROR_HANDLING.md) for error messages
