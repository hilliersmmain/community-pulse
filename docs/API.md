# API Documentation

Reference for the public functions and classes in the Community Pulse project.

---

## Table of Contents

1. [Data Generator](#data-generator)
2. [Data Cleaner](#data-cleaner)
3. [Health Metrics](#health-metrics)
4. [Visualizer](#visualizer)
5. [Upload Validation](#upload-validation)
6. [UI Helpers](#ui-helpers)

---

## Data Generator

**Module:** `utils/data_generator.py`

Functions for generating synthetic datasets with configurable quality issues.

### `generate_messy_data()`

```python
def generate_messy_data(
    num_records: int = 500,
    save_path: Optional[str] = None,
    messiness_level: str = "medium",
    reference_date: Optional[date] = None,
) -> pd.DataFrame
```

Generates a dataset with intentional data quality issues for cleaning demonstration.

**Parameters:**
- `num_records` (int, optional): Number of base records to generate. Default: 500. The returned frame is usually larger: a share of the rows (rounded down) is copied again as duplicates.
- `save_path` (str, optional): Path to save a CSV copy. Its directory is created if it does not exist. If None, nothing is written to disk.
- `messiness_level` (str, optional): Controls the level of data quality issues. Default: `"medium"`
  - `"low"`: 3% duplicates, 2% broken emails
  - `"medium"`: 10% duplicates, 5% broken emails
  - `"high"`: 20% duplicates, 15% broken emails
- `reference_date` (date, optional): The "today" every generated date is measured back from. If None, the current date is used.

**Returns:**
- `pd.DataFrame`: Generated dataset with columns:
  - `ID`: Random UUID string
  - `Name`: Member name (some all upper-case or all lower-case)
  - `Email`: Email address (some written as "user at domain.com")
  - `Join_Date`: Date joined (mixed formats, some `"Unknown"`)
  - `Last_Login`: Last login timestamp (some missing)
  - `Event_Attendance`: Number of events attended (some missing)
  - `Role`: Member role (`Member`, `Admin`, `Guest`)
  - `Event_Registered`: Event name, or `"No Event"`
  - `Registration_Date`: Registration date (blank when there is no registration)

**Raises:**
- `ValueError`: `num_records` is not a positive integer, or `messiness_level` is not `"low"`, `"medium"` or `"high"`.

**Example:**
```python
from utils.data_generator import generate_messy_data

# Generate 100 records with medium messiness
df = generate_messy_data(num_records=100, messiness_level="medium")
print(f"Generated {len(df)} records")

# Generate and save to file (the data/ directory is created if needed)
df = generate_messy_data(
    num_records=500,
    save_path="data/sample.csv",
    messiness_level="high"
)
```

For reproducible output, use the `DataGenerator` class: `DataGenerator(seed=1, reference_date=date(2026, 10, 1)).generate(500, "medium")` returns the same frame on every call.

**Data Quality Issues Introduced:**
- Duplicate records (controlled by messiness level)
- Names in all upper-case or all lower-case
- Invalid email formats (e.g., "user at domain.com")
- Mixed date formats in `Join_Date` (ISO, MM/DD/YYYY, DD-MM-YYYY) and the text `"Unknown"`
- Missing values (NaN) in `Event_Attendance` and `Last_Login`

---

## Data Cleaner

**Module:** `utils/cleaner.py`

Pipeline for cleaning and standardizing messy datasets.

### `DataCleaner`

Main class for data cleaning operations with execution logging.

```python
class DataCleaner:
    def __init__(self, df: pd.DataFrame)
```

**Parameters:**
- `df` (pd.DataFrame): Raw dataframe to clean. It is copied; the caller's frame is never changed.

**Attributes:**
- `raw_df`: Copy of the dataframe passed in
- `clean_df`: Working dataframe (modified during cleaning)
- `log`: List of log messages tracking cleaning operations
- `start_timestamp`: Timestamp when the cleaner was created
- `end_timestamp`: Timestamp when `clean_all()` finished (None before that)

No step raises for a missing column. `standardize_names`, `fix_emails`, `clean_dates` and `handle_missing_values` do nothing without their column; `remove_duplicates` falls back to comparing whole rows when there is no `Email` column.

### Methods

#### `clean_all()`

```python
def clean_all(self, steps=None) -> pd.DataFrame
```

Execute all or selected cleaning steps. The steps always run in the order listed below, whatever order the list gives them in. An empty frame is returned unchanged with the log message `No data to clean (empty DataFrame).`

**Parameters:**
- `steps` (list, optional): List of step names to execute. If None, executes all steps.
  - Available steps:
    - `"standardize_names"`: Title Case for names written all upper-case or all lower-case
    - `"fix_emails"`: Lower-case emails, repair " at ", drop rows with an invalid email
    - `"remove_duplicates"`: Remove rows that repeat an earlier Email
    - `"clean_dates"`: Parse `Join_Date` into dates; unreadable dates are left blank
    - `"handle_missing_values"`: Fill missing `Event_Attendance` with 0

**Returns:**
- `pd.DataFrame`: Cleaned dataframe (`clean_df`)

**Example:**
```python
from utils.cleaner import DataCleaner

# Clean with all default steps
cleaner = DataCleaner(raw_df)
clean_df = cleaner.clean_all()

# Clean with specific steps only
cleaner = DataCleaner(raw_df)
clean_df = cleaner.clean_all(steps=[
    'standardize_names',
    'fix_emails',
    'remove_duplicates'
])

# Access cleaning log
for message in cleaner.log:
    print(message)
```

#### `standardize_names()`

```python
def standardize_names(self) -> None
```

Convert names that are entirely upper-case or entirely lower-case to Title Case (e.g., "john doe" → "John Doe", "JANE ROE" → "Jane Roe"). Mixed-case names such as "McDonald" or "Jimmy Freeman MD" are left alone. Surrounding and repeated spaces are not changed.

**Modifies:** `self.clean_df["Name"]`
**Logs:** `Standardized Names to Title Case.`

#### `fix_emails()`

```python
def fix_emails(self) -> None
```

Lower-case and strip each email, replace " at " with "@", and keep it only if it fully matches `EMAIL_PATTERN` (`utils/constants.py`). Rows whose email is invalid or missing are removed.

**Modifies:** `self.clean_df` (drops rows)
**Logs:** `Fixed email formatting. Removed N invalid emails.`

#### `remove_duplicates()`

```python
def remove_duplicates(self) -> None
```

Remove rows whose Email, lower-cased and stripped of surrounding spaces, already appeared in an earlier row; the first row is kept. Rows with a missing or blank email are never treated as duplicates. Without an `Email` column, whole identical rows are removed instead. The rule lives in `utils/duplicates.py` (`duplicate_mask`), which the Duplicate Records KPI and the Duplicate Score also use.

**Modifies:** `self.clean_df` (drops rows)
**Logs:** `Removed N duplicate rows.`

#### `clean_dates()`

```python
def clean_dates(self) -> None
```

Parse the `Join_Date` column into datetime values with `utils.date_parsing.parse_dates`, which tries ISO 8601, then MM/DD/YYYY, then DD-MM-YYYY, then a per-value fallback. A date nothing can read (such as `"Unknown"`) is left blank (NaT), never guessed. Other date columns (`Last_Login`, `Registration_Date`) are not touched.

**Modifies:** `self.clean_df["Join_Date"]`
**Logs:** `Standardized Dates. Every date was readable.` or `Standardized Dates. Left N unreadable dates blank (not guessed).`, with `; N were already missing` before the full stop when some were.

#### `handle_missing_values()`

```python
def handle_missing_values(self) -> None
```

Fill missing `Event_Attendance` values with 0. A value that is not a number counts as missing. Other columns keep their missing values.

**Modifies:** `self.clean_df["Event_Attendance"]`
**Logs:** `Filled N missing Attendance records with 0.`

---

## Health Metrics

**Module:** `utils/health_metrics.py`

Calculate data quality metrics and health scores. The definitions are in [KPI_DEFINITIONS.md](KPI_DEFINITIONS.md).

### `DataHealthMetrics`

```python
class DataHealthMetrics:
    def __init__(self, df: pd.DataFrame)
```

**Parameters:**
- `df` (pd.DataFrame): Dataframe to analyze (copied)

### Methods

#### `get_detailed_metrics()`

```python
def get_detailed_metrics(self) -> Dict[str, Any]
```

Calculate comprehensive data quality metrics.

**Returns:**
- `dict`: Dictionary containing:
  - `total_records` (int): Total number of rows
  - `total_cells` (int): Rows × columns
  - `null_cells` (int): Total count of null/missing cells
  - `non_null_cells` (int): `total_cells - null_cells`
  - `duplicate_records` (int): Rows whose Email repeats an earlier row's (see `utils/duplicates.py`)
  - `unique_records` (int): `total_records - duplicate_records`
  - `completeness_score` (float): Percentage of non-null cells (0-100)
  - `duplicate_score` (float): Percentage of rows that are not duplicates (0-100)
  - `formatting_score` (float): Percentage of validly formatted values (0-100)
  - `overall_score` (float): Weighted health score (0-100)
  - `timestamp` (datetime): When the `DataHealthMetrics` object was created

`get_all_metrics()` returns only the four scores and the timestamp. The KPI row, the Data Explorer scores, the before/after comparison tiles and the Cleaning Summary use the cached wrappers `get_health_metrics(df)` and `get_health_score(df)` (`@st.cache_data`), so a frame they have already scored is not scored again. The sidebar's Quick Stats builds a `DataHealthMetrics` directly and recomputes it on each run.

**Example:**
```python
from utils.health_metrics import DataHealthMetrics

# Calculate metrics
health = DataHealthMetrics(df)
metrics = health.get_detailed_metrics()

print(f"Total Records: {metrics['total_records']}")
print(f"Health Score: {metrics['overall_score']}%")
print(f"Duplicates: {metrics['duplicate_records']}")
```

#### `calculate_overall_health_score()`

```python
def calculate_overall_health_score(self) -> float
```

Calculate composite health score using weighted algorithm, rounded to one decimal place.

**Formula:**
```
Overall Score = (40% × Completeness) + (30% × Uniqueness) + (30% × Formatting)
```

The weights are `HEALTH_SCORE_WEIGHT_COMPLETENESS`, `HEALTH_SCORE_WEIGHT_UNIQUENESS` and `HEALTH_SCORE_WEIGHT_FORMATTING` in `utils/constants.py`.

**Returns:**
- `float`: Health score from 0-100

**Quality Thresholds** (`SCORE_THRESHOLDS` in `utils/constants.py`, named in the Data Health Score tile's help text):
- 90 and above: Excellent
- 70 to under 90: Good
- Below 70: Needs Work

---

## Visualizer

**Module:** `utils/visualizer.py`

Interactive chart generation using Plotly. Each function returns an empty `go.Figure()` when its column is missing.

### `plot_attendance_trend()`

```python
def plot_attendance_trend(
    df: pd.DataFrame,
    data_state: str = "cleaned"
) -> go.Figure
```

Create a line chart of new members per month (the "Membership Growth Over Time" chart).

**Parameters:**
- `df` (pd.DataFrame): Dataframe with a `Join_Date` column
- `data_state` (str, optional): Label for data state ("raw" or "cleaned"), shown in the subtitle. Default: "cleaned"

**Returns:**
- `plotly.graph_objects.Figure`: Interactive line chart with:
  - New members per month; months with no joins count as zero
  - A straight least-squares trend line (`numpy.polyfit`, degree 1) when there are at least 3 months
  - A dotted mean line
  - Hover tooltips with the monthly and cumulative count

**Example:**
```python
from utils.visualizer import plot_attendance_trend

fig = plot_attendance_trend(df, data_state='cleaned')
fig.show()  # Display in browser
fig.write_image("attendance.png")  # Save as image (uses kaleido)
```

**Features:**
- Dates are parsed with `utils.date_parsing.parse_dates`; unreadable dates are dropped from the chart, and the subtitle says how many
- Zoom/pan controls and a PNG download button in the modebar

### `plot_role_distribution()`

```python
def plot_role_distribution(
    df: pd.DataFrame,
    data_state: str = "cleaned"
) -> go.Figure
```

Create pie chart showing member role demographics. Role labels are HTML-escaped, so uploaded text is shown as text.

**Parameters:**
- `df` (pd.DataFrame): Dataframe with `Role` column
- `data_state` (str, optional): Label for data state. Default: "cleaned"

**Returns:**
- `plotly.graph_objects.Figure`: Interactive pie chart

**Example:**
```python
from utils.visualizer import plot_role_distribution

fig = plot_role_distribution(df)
fig.show()
```

### `plot_attendance_histogram()`

```python
def plot_attendance_histogram(
    df: pd.DataFrame,
    data_state: str = "cleaned"
) -> go.Figure
```

Create histogram showing distribution of attendance counts. Values that are not numbers are left out.

**Parameters:**
- `df` (pd.DataFrame): Dataframe with `Event_Attendance` column
- `data_state` (str, optional): Label for data state. Default: "cleaned"

**Returns:**
- `plotly.graph_objects.Figure`: Interactive histogram with:
  - Bar chart of attendance distribution
  - Mean line (green dashed)
  - Median line (orange dotted)
  - Statistical annotations

**Example:**
```python
from utils.visualizer import plot_attendance_histogram

fig = plot_attendance_histogram(df)
fig.show()
```

### `get_chart_export_config()`

```python
def get_chart_export_config() -> Dict[str, Any]
```

Get standardized configuration for chart exports.

**Returns:**
- `dict`: Plotly configuration with:
  - Modebar shown, Plotly logo hidden
  - PNG download named `community_pulse_chart`, 1000 × 600 at scale 2
  - The `toImage` button added

**Example:**
```python
from utils.visualizer import get_chart_export_config
import streamlit as st

config = get_chart_export_config()
st.plotly_chart(fig, config=config)
```

---

## Upload Validation

**Module:** `utils/upload_validation.py`

Checks an uploaded CSV before the app uses it. Streamlit's own upload limit (`maxUploadSize = 5` under `[server]` in `.streamlit/config.toml`) refuses a file over 5 MB; the sidebar repeats the check against `MAX_UPLOAD_SIZE_MB` as a backstop, then calls these two functions.

### `validate_upload_header()`

```python
def validate_upload_header(raw: bytes) -> list[str]
```

Count the fields of the header row in the first `HEADER_PEEK_BYTES` of the raw bytes, before pandas parses anything. The header is the first row that is not blank (blank and whitespace-only lines are skipped, as pandas skips them); a quoted field may span lines, and lines may end in CR, LF or CRLF. Returns `["Too many columns: uploads are limited to 50 columns."]` when there are more than `MAX_UPLOAD_COLUMNS`, otherwise `[]`.

### `validate_upload_dataframe()`

```python
def validate_upload_dataframe(df: pd.DataFrame) -> UploadValidationResult
```

Returns an `UploadValidationResult` with `is_valid` and a list of `errors`:
- `Missing required columns: ...` for any of `Name`, `Email`, `Role`, `Join_Date`, `Event_Attendance` that is absent (names are case-sensitive). When the whole header was read as one column, the message adds a hint naming the delimiter, e.g. `The header looks semicolon-delimited; re-save the file with commas as the delimiter.`
- `Too many columns: uploads are limited to 50 columns.` over `MAX_UPLOAD_COLUMNS`
- `Row count exceeds limit (50,000).` over `MAX_UPLOAD_ROWS`

---

## UI Helpers

**Module:** `utils/ui_helpers.py`

Streamlit UI components and helper functions.

### `initialize_session_state()`

```python
def initialize_session_state() -> None
```

Set the welcome and tutorial flags (`show_welcome`, `tutorial_mode`, `tutorial_step`) in `st.session_state` if they are not set yet. The data itself is kept in `st.session_state["raw_df"]` by the sidebar, per browser session; nothing is written to disk.

**Example:**
```python
from utils.ui_helpers import initialize_session_state

initialize_session_state()
```

### `show_welcome_modal()`

```python
def show_welcome_modal() -> bool
```

Display the welcome panel for first-time users, with Dismiss, Start Tutorial and Get Started buttons. Returns False without drawing anything when `show_welcome` is not set.

**Example:**
```python
from utils.ui_helpers import show_welcome_modal

if st.session_state.get('show_welcome', False):
    show_welcome_modal()
```

### `show_tutorial_step()`

```python
def show_tutorial_step(step: int) -> bool
```

Draw the tutorial card for `step` (0 to 4) when the tutorial is on and has reached that step, with Skip Tutorial, Previous and Next buttons. Each caller passes the step it anchors: the sidebar 0, the KPI row 1, the Data Preparation tab 2 and 3, the Analytics tab 4.

### `show_empty_state()`

```python
def show_empty_state(
    icon: str = "",
    title: str = "No Data Available",
    message: str = "Get started by generating some data.",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None,
) -> None
```

Display empty state placeholder with icon, title, and message, and an optional action button.

**Parameters:**
- `icon` (str): Emoji or icon to display
- `title` (str): Main heading text
- `message` (str): Descriptive message text
- `action_label`, `action_callback` (optional): When both are given, a button with that label calls the callback

**Example:**
```python
from utils.ui_helpers import show_empty_state

if df is None:
    show_empty_state(
        icon="",
        title="No Data Generated",
        message="Click 'Generate New Data' to begin."
    )
```

### `show_loading_message()`

```python
def show_loading_message(message: str = "Processing your data...")
```

Return an `st.spinner` showing the message; use it as a context manager.

**Parameters:**
- `message` (str): Loading message to display

**Example:**
```python
from utils.ui_helpers import show_loading_message

with show_loading_message("Cleaning data..."):
    clean_df = cleaner.clean_all()
```

### `queue_flash()` and `show_flash()`

```python
def queue_flash(message: str) -> None
def show_flash() -> None
```

`st.rerun()` discards everything the current run drew, so a confirmation is queued instead: `queue_flash` keeps the message in session state, and `show_flash` (called near the top of `app.py`) shows it once as a toast on the next run. "Generate New Data", "Run Cleaning Algorithms" and the end of the tutorial confirm this way.

### `show_success_message()`

```python
def show_success_message(message: str, icon: str = "") -> None
```

Display success notification with custom message (`st.success`). The `icon` argument is accepted but not shown.

### `show_error_message()`

```python
def show_error_message(
    message: str,
    details: Optional[str] = None
) -> None
```

Display error notification with optional technical details.

**Parameters:**
- `message` (str): User-friendly error message
- `details` (str, optional): Technical error details (displayed in an "Error Details" expander)

### `get_contextual_message()`

```python
def get_contextual_message(key: str, **kwargs) -> str
```

Get contextual message template with variable substitution.

**Parameters:**
- `key` (str): Message key from MESSAGES dictionary
- `**kwargs`: Variables to substitute in message template

**Returns:**
- `str`: Formatted message string (empty for a key whose entry is not a plain string)

**Example:**
```python
from utils.ui_helpers import get_contextual_message

msg = get_contextual_message(
    "data_generated",
    num_records=500,
    messiness="medium"
)
print(msg)  # "Successfully generated 500 records with medium messiness level."
```

---

## Type Hints Reference

All modules use comprehensive type hints for better IDE support and code clarity.

**Common Types:**
```python
from typing import Optional, Dict, List, Union, Any
import pandas as pd
import plotly.graph_objects as go

# Function signatures use type hints
def func(df: pd.DataFrame, option: Optional[str] = None) -> Dict[str, Any]:
    ...
```

**Pandas Types:**
- `pd.DataFrame`: Tabular data
- `pd.Series`: Single column/row of data

**Plotly Types:**
- `go.Figure`: Interactive chart object

---

## Error Handling

The library code raises very little, on purpose.

**Exceptions you can see:**
- `ValueError`: `generate_messy_data()` (or `DataGenerator.generate()`) got a `num_records` that is not a positive integer, or an unknown `messiness_level`.
- `OSError` (or a subclass such as `FileNotFoundError`): `save_path` points somewhere the directory cannot be created or the file cannot be written.

**What does not raise:**
- `DataCleaner` never raises for a missing column: four steps skip it, and `remove_duplicates` compares whole rows when `Email` is missing.
- The `plot_*` functions return an empty figure when their column is missing.
- In the app, a missing column is caught earlier: the upload is rejected with `Missing required columns: ...` in the sidebar.

**Example:**
```python
try:
    df = generate_messy_data(num_records=100)
    cleaner = DataCleaner(df)
    clean_df = cleaner.clean_all()
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

---

## Best Practices

### Data Generation
- Use `messiness_level="low"` for demos
- Use `messiness_level="high"` for testing cleaning algorithms
- Pass a `seed` and a `reference_date` to `DataGenerator` for repeatable output

### Data Cleaning
- Always create a `DataCleaner` instance per cleaning operation
- Review `cleaner.log` to understand what was changed
- Compare before/after with `DataHealthMetrics`

### Visualization
- Use consistent `data_state` labels ("raw" vs "cleaned")
- Enable export config for all charts: `config=get_chart_export_config()`

### UI Components
- Initialize session state at app startup
- Use contextual messages for consistent UX
- Queue a confirmation with `queue_flash()` when the next line is `st.rerun()`

---

## Performance Notes

- `DataCleaner` and `DataHealthMetrics` copy the frame they are given, so the caller's frame is never changed
- Plotly charts are drawn in the browser
- The app caches health metrics with `@st.cache_data` (`get_health_metrics`, `get_health_score`)

---

## Further Reading

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Streamlit API Reference](https://docs.streamlit.io/)
- [Faker Documentation](https://faker.readthedocs.io/)

---

## Support

For issues or questions:
- GitHub Issues: [hilliersmmain/community-pulse/issues](https://github.com/hilliersmmain/community-pulse/issues)
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
