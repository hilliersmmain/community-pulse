# API Documentation

Complete reference for all public APIs in the Community Pulse project.

---

## Table of Contents

1. [Data Generator](#data-generator)
2. [Data Cleaner](#data-cleaner)
3. [Health Metrics](#health-metrics)
4. [Visualizer](#visualizer)
5. [UI Helpers](#ui-helpers)

---

## Data Generator

**Module:** `utils/data_generator.py`

Functions for generating synthetic datasets with configurable quality issues.

### `generate_messy_data()`

```python
def generate_messy_data(
    num_records: int = 500, 
    save_path: Optional[str] = None, 
    messiness_level: str = "medium"
) -> pd.DataFrame
```

Generates a dataset with intentional data quality issues for cleaning demonstration.

**Parameters:**
- `num_records` (int, optional): Number of base records to generate. Default: 500. Final dataset may be larger due to added duplicates.
- `save_path` (str, optional): Path to save CSV file. If None, data is not saved to disk.
- `messiness_level` (str, optional): Controls level of data quality issues. Default: "medium"
  - `"low"`: 3% duplicates, 2% errors (well-maintained CRM)
  - `"medium"`: 10% duplicates, 5% errors (typical export)
  - `"high"`: 20% duplicates, 15% errors (legacy system)

**Returns:**
- `pd.DataFrame`: Generated dataset with columns:
  - `ID`: Sequential integer identifier
  - `Name`: Member name (with case inconsistencies)
  - `Email`: Email address (with format issues)
  - `Join_Date`: Date joined (various formats)
  - `Last_Login`: Last login timestamp (various formats)
  - `Event_Attendance`: Number of events attended
  - `Role`: Member role (Member, Organizer, Speaker, Volunteer)
  - `Event_Registered`: Event registration status
  - `Registration_Date`: Registration date

**Example:**
```python
from utils.data_generator import generate_messy_data

# Generate 100 records with medium messiness
df = generate_messy_data(num_records=100, messiness_level="medium")
print(f"Generated {len(df)} records")

# Generate and save to file
df = generate_messy_data(
    num_records=500,
    save_path="data/sample.csv",
    messiness_level="high"
)
```

**Data Quality Issues Introduced:**
- Duplicate records (controlled by messiness level)
- Inconsistent name capitalization (UPPER, lower, Title Case)
- Invalid email formats (e.g., "user at domain.com")
- Mixed date formats (YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY)
- Missing values (NaN) in various columns
- Text formatting issues (extra spaces, special characters)

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
- `df` (pd.DataFrame): Raw dataframe to clean

**Attributes:**
- `original_df`: Copy of original dataframe
- `df`: Working dataframe (modified during cleaning)
- `log`: List of log messages tracking cleaning operations
- `start_timestamp`: Timestamp when cleaner was initialized
- `end_timestamp`: Timestamp when cleaning completed

### Methods

#### `clean_all()`

```python
def clean_all(self, steps: list = None) -> pd.DataFrame
```

Execute all or selected cleaning steps in sequence.

**Parameters:**
- `steps` (list, optional): List of step names to execute. If None, executes all steps.
  - Available steps:
    - `"standardize_names"`: Convert names to Title Case
    - `"fix_emails"`: Validate and fix email formats
    - `"remove_duplicates"`: Remove duplicate records
    - `"clean_dates"`: Standardize date formats to YYYY-MM-DD
    - `"handle_missing_values"`: Fill missing values with defaults

**Returns:**
- `pd.DataFrame`: Cleaned dataframe

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

Convert all names to Title Case format (e.g., "john doe" → "John Doe").

**Modifies:** `self.df` in-place  
**Logs:** Records count of names standardized

#### `fix_emails()`

```python
def fix_emails(self) -> None
```

Validate and correct email formats. Removes invalid entries.

**Modifies:** `self.df` in-place  
**Logs:** Records count of emails fixed/removed

#### `remove_duplicates()`

```python
def remove_duplicates(self) -> None
```

Remove duplicate records based on Email and Name columns.

**Modifies:** `self.df` in-place  
**Logs:** Records count of duplicates removed

#### `clean_dates()`

```python
def clean_dates(self) -> None
```

Standardize all date columns to YYYY-MM-DD format.

**Modifies:** `self.df` in-place  
**Logs:** Records count of dates standardized

#### `handle_missing_values()`

```python
def handle_missing_values(self) -> None
```

Fill missing values with intelligent defaults (e.g., 0 for attendance).

**Modifies:** `self.df` in-place  
**Logs:** Records count of missing values filled

---

## Health Metrics

**Module:** `utils/health_metrics.py`

Calculate data quality metrics and health scores.

### `DataHealthMetrics`

```python
class DataHealthMetrics:
    def __init__(self, df: pd.DataFrame)
```

**Parameters:**
- `df` (pd.DataFrame): Dataframe to analyze

### Methods

#### `get_detailed_metrics()`

```python
def get_detailed_metrics(self) -> Dict[str, Union[int, float]]
```

Calculate comprehensive data quality metrics.

**Returns:**
- `dict`: Dictionary containing:
  - `total_records` (int): Total number of rows
  - `unique_records` (int): Count of unique records
  - `duplicate_records` (int): Count of duplicate rows
  - `null_cells` (int): Total count of null/missing values
  - `completeness_score` (float): Percentage of non-null values (0-100)
  - `duplicate_score` (float): Percentage of unique records (0-100)
  - `formatting_score` (float): Percentage of properly formatted data (0-100)
  - `overall_score` (float): Composite health score (0-100)

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

Calculate composite health score using weighted algorithm.

**Formula:**
```
Overall Score = (40% × Completeness) + (30% × Uniqueness) + (30% × Formatting)
```

**Returns:**
- `float`: Health score from 0-100

**Quality Thresholds:**
- 90-100: Excellent data quality
- 70-89: Good data quality
- 50-69: Fair data quality (needs improvement)
- 0-49: Poor data quality (critical issues)

---

## Visualizer

**Module:** `utils/visualizer.py`

Interactive chart generation using Plotly.

### `plot_attendance_trend()`

```python
def plot_attendance_trend(
    df: pd.DataFrame, 
    data_state: str = "cleaned"
) -> go.Figure
```

Create time-series line chart showing attendance trends over time.

**Parameters:**
- `df` (pd.DataFrame): Dataframe with `JoinDate` and `AttendanceCount` columns
- `data_state` (str, optional): Label for data state ("raw" or "cleaned"). Default: "cleaned"

**Returns:**
- `plotly.graph_objects.Figure`: Interactive line chart with:
  - Line plot of attendance over time
  - LOWESS smoothing trend line
  - Hover tooltips with detailed information
  - Export button for PNG download

**Example:**
```python
from utils.visualizer import plot_attendance_trend

fig = plot_attendance_trend(df, data_state='cleaned')
fig.show()  # Display in browser
fig.write_image("attendance.png")  # Save as image
```

**Features:**
- Automatic date parsing and sorting
- Statistical smoothing for trend visualization
- Responsive design with zoom/pan controls
- High-resolution export capability

### `plot_role_distribution()`

```python
def plot_role_distribution(
    df: pd.DataFrame, 
    data_state: str = "cleaned"
) -> go.Figure
```

Create pie chart showing member role demographics.

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

Create histogram showing distribution of attendance counts.

**Parameters:**
- `df` (pd.DataFrame): Dataframe with `AttendanceCount` column
- `data_state` (str, optional): Label for data state. Default: "cleaned"

**Returns:**
- `plotly.graph_objects.Figure`: Interactive histogram with:
  - Bar chart of attendance distribution
  - Mean line (red dashed)
  - Median line (green dotted)
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
  - Download button enabled
  - PNG export at 1920x1080 resolution
  - Modebar buttons configured

**Example:**
```python
from utils.visualizer import get_chart_export_config
import streamlit as st

config = get_chart_export_config()
st.plotly_chart(fig, config=config)
```

---

## UI Helpers

**Module:** `utils/ui_helpers.py`

Streamlit UI components and helper functions.

### `initialize_session_state()`

```python
def initialize_session_state() -> None
```

Initialize all Streamlit session state variables with default values.

**Example:**
```python
from utils.ui_helpers import initialize_session_state

initialize_session_state()
# Now st.session_state has all required keys
```

### `show_welcome_modal()`

```python
def show_welcome_modal() -> None
```

Display welcome modal for first-time users with tutorial information.

**Example:**
```python
from utils.ui_helpers import show_welcome_modal

if st.session_state.get('show_welcome', False):
    show_welcome_modal()
```

### `show_empty_state()`

```python
def show_empty_state(
    icon: str = "📊",
    title: str = "No Data Available",
    message: str = "Please generate or upload data to continue."
) -> None
```

Display empty state placeholder with icon, title, and message.

**Parameters:**
- `icon` (str): Emoji or icon to display
- `title` (str): Main heading text
- `message` (str): Descriptive message text

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
@contextmanager
def show_loading_message(message: str = "Processing your data...")
```

Context manager for displaying loading spinner during operations.

**Parameters:**
- `message` (str): Loading message to display

**Example:**
```python
from utils.ui_helpers import show_loading_message

with show_loading_message("Cleaning data..."):
    clean_df = cleaner.clean_all()
```

### `show_success_message()`

```python
def show_success_message(message: str, icon: str = "") -> None
```

Display success notification with custom message.

**Parameters:**
- `message` (str): Success message text
- `icon` (str, optional): Emoji to display. Default: ""

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
- `details` (str, optional): Technical error details (displayed in expander)

### `get_contextual_message()`

```python
def get_contextual_message(key: str, **kwargs) -> str
```

Get contextual message template with variable substitution.

**Parameters:**
- `key` (str): Message key from MESSAGES dictionary
- `**kwargs`: Variables to substitute in message template

**Returns:**
- `str`: Formatted message string

**Example:**
```python
from utils.ui_helpers import get_contextual_message

msg = get_contextual_message(
    "data_generated",
    num_records=500,
    messiness="medium"
)
print(msg)  # "Successfully generated 500 records with medium messiness"
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

All modules implement consistent error handling patterns.

**Common Exceptions:**
- `ValueError`: Invalid parameter values
- `KeyError`: Missing required columns in DataFrame
- `FileNotFoundError`: File path doesn't exist

**Example:**
```python
try:
    df = generate_messy_data(num_records=100)
    cleaner = DataCleaner(df)
    clean_df = cleaner.clean_all()
except ValueError as e:
    print(f"Invalid parameter: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Best Practices

### Data Generation
- Use `messiness_level="low"` for demos
- Use `messiness_level="high"` for testing cleaning algorithms
- Generate 500-1000 records for realistic performance testing

### Data Cleaning
- Always create a `DataCleaner` instance per cleaning operation
- Review `cleaner.log` to understand what was changed
- Compare before/after with `DataHealthMetrics`

### Visualization
- Use consistent `data_state` labels ("raw" vs "cleaned")
- Enable export config for all charts: `config=get_chart_export_config()`
- Set appropriate figure sizes for mobile responsiveness

### UI Components
- Initialize session state at app startup
- Use contextual messages for consistent UX
- Show loading indicators for operations >1 second

---

## Performance Notes

**Optimization Tips:**
- DataFrames are copied during cleaning to preserve original
- Use `df.copy()` when working with large datasets to avoid mutations
- Plotly charts are rendered client-side for better performance
- Caching with `@st.cache_data` recommended for expensive operations

**Typical Performance:**
| Operation | Dataset Size | Time | Memory |
|-----------|--------------|------|--------|
| Data Generation | 1,000 records | ~0.5s | <50 MB |
| Data Cleaning | 1,000 records | ~0.3s | <75 MB |
| Health Metrics | 1,000 records | ~0.1s | <30 MB |
| Chart Rendering | 1,000 records | ~0.2s | <100 MB |

---

## Further Reading

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Streamlit API Reference](https://docs.streamlit.io/)
- [Faker Documentation](https://faker.readthedocs.io/)

---

## Support

For issues or questions:
- GitHub Issues: [hilliersmmain/community_pulse/issues](https://github.com/hilliersmmain/community_pulse/issues)
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
