# Development Guide

Complete guide for developers who want to contribute to or extend Community Pulse.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Architecture](#project-architecture)
3. [Development Environment](#development-environment)
4. [Running Tests](#running-tests)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Adding New Features](#adding-new-features)
7. [Debugging Tips](#debugging-tips)
8. [Performance Optimization](#performance-optimization)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- **Python:** 3.10 or higher (CI tests 3.11 and 3.12)
- **pip:** Latest version recommended
- **Virtual Environment:** venv, conda, or pyenv
- **Git:** For version control
- **Operating System:** Windows, macOS, or Linux

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/hilliersmmain/community-pulse.git
   cd community-pulse
   ```

2. **Create virtual environment**
   ```bash
   # Using venv (recommended)
   python -m venv venv
   
   # Activate on Linux/macOS
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Install the app's dependencies
   pip install -r requirements.txt
   
   # Or, for development: the app's dependencies plus pytest, Black, flake8, mypy and pre-commit
   pip install -r requirements-dev.txt
   ```

   This is an application, not an installable package: `pip install -e .` fails with
   "Multiple top-level packages discovered in a flat-layout".

4. **Verify installation**
   ```bash
   # Run verification script
   python verify_setup.py
   
   # Run tests to ensure everything works
   pytest
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   Open your browser to `http://localhost:8501`

### First-Time Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] `pytest` reports 0 failed (an expected skip says AppTest does not surface plotly_chart)
- [ ] Application runs without errors
- [ ] Can generate data and perform cleaning

---

## Project Architecture

### Directory Structure

```
community-pulse/
├── app.py                          # Streamlit entry point: loads state, calls the components
├── requirements.txt                # App dependencies
├── requirements-dev.txt            # App dependencies plus test and lint tools
├── pyproject.toml                  # Project metadata and pytest, Black and coverage settings
├── verify_setup.py                 # Installation check
│
├── components/                     # The UI, one module per area
│   ├── sidebar.py                 # Data source, upload, cleaning steps, export, view
│   ├── kpi_display.py             # KPI tiles
│   ├── comparison.py              # Before/after comparison
│   ├── tab_preparation.py         # Cleaning tab
│   ├── tab_analytics.py           # Charts tab
│   └── tab_explorer.py            # Data table tab
│
├── utils/                          # Logic, no page layout
│   ├── constants.py               # Every tunable value
│   ├── data_generator.py          # Synthetic messy data
│   ├── cleaner.py                 # DataCleaner, the cleaning pipeline
│   ├── duplicates.py              # The one definition of a duplicate row
│   ├── date_parsing.py            # Mixed-format date parsing
│   ├── health_metrics.py          # Quality scores
│   ├── upload_validation.py       # Checks on uploaded CSVs
│   ├── visualizer.py              # Plotly charts
│   ├── session_keys.py            # st.session_state key names
│   └── ui_helpers.py              # Shared Streamlit helpers (welcome, tutorial, messages)
│
├── community_pulse/
│   └── demo_charts.py             # Writes static chart images to demo_outputs/ (gitignored)
│
├── scripts/
│   └── verify_loop.py             # Local Black, flake8, mypy, pytest and coverage loop
│
├── tests/                          # pytest suite, one test_*.py file per area
│   └── snapshots/                 # Chart snapshots for test_visualizer.py
│
├── docs/                           # Documentation, including this file
│   └── screenshots/               # UI screenshots
│
├── .github/
│   ├── workflows/ci.yml           # CI: Black, flake8, mypy, pytest, coverage, Bandit
│   ├── dependabot.yml             # Weekly dependency update PRs
│   └── ISSUE_TEMPLATE/            # Bug report and feature request forms
│
├── .devcontainer/devcontainer.json # Dev container / Codespaces
├── .streamlit/config.toml          # Streamlit options (one: the upload cap)
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

### Module Overview

#### `app.py` - Main Application
- Entry point for the Streamlit dashboard
- Initialises session state and picks the raw or cleaned data to show
- Calls the render functions in `components/`, which hold the UI itself

#### `utils/data_generator.py` - Data Generation
- **Purpose:** Generate synthetic datasets with quality issues
- **Key Function:** `generate_messy_data()`
- **Dependencies:** Faker, NumPy, Pandas
- **Use Case:** Creating realistic test data for demos

#### `utils/cleaner.py` - Data Cleaning
- **Purpose:** Clean and standardize messy data
- **Key Class:** `DataCleaner`
- **Pipeline Steps:** Name standardization, email validation, deduplication, date formatting, missing value handling
- **Use Case:** Automated data quality improvement

#### `utils/health_metrics.py` - Quality Metrics
- **Purpose:** Calculate data quality scores
- **Key Class:** `DataHealthMetrics`
- **Metrics:** Completeness, uniqueness, formatting, overall health
- **Use Case:** Quantifying data quality improvements

#### `utils/visualizer.py` - Visualizations
- **Purpose:** Generate interactive charts
- **Key Functions:** `plot_attendance_trend()`, `plot_role_distribution()`, `plot_attendance_histogram()`
- **Dependencies:** Plotly
- **Use Case:** Data exploration and presentation

#### `utils/ui_helpers.py` - UI Helpers
- **Purpose:** Reusable Streamlit UI elements
- **Key Functions:** `show_welcome_modal()`, `show_tutorial_step()`, `show_empty_state()`, `show_loading_message()`, `queue_flash()`
- **Use Case:** Consistent user experience

#### `components/` - The UI
- **Purpose:** One render function per part of the page: `render_sidebar()`, `render_kpi_section()`, `render_comparison()`, `render_preparation_tab()`, `render_analytics_tab()`, `render_explorer_tab()`
- **State:** The data lives in `st.session_state` (raw data under `"raw_df"`); nothing is written to disk

### Data Flow

```
User Input (Sidebar)
    ↓
Data Generation (data_generator.py) or CSV upload (upload_validation.py)
    ↓
Raw DataFrame (st.session_state)
    ↓
Data Cleaning (cleaner.py)
    ↓
Clean DataFrame
    ↓
┌─────────────────┬────────────────────┐
│                 │                    │
Health Metrics    Visualizations       Export
(health_metrics)  (visualizer)         (CSV/JSON)
    ↓                 ↓                   ↓
Dashboard KPIs    Interactive Charts   Downloads
```

### Design Patterns

**1. Separation of Concerns**
- UI in `components/`, wired together by `app.py`, with shared helpers in `utils/ui_helpers.py`
- Business logic in `utils/` modules
- Tests in separate `tests/` directory

**2. Immutability**
- DataCleaner copies its input: `raw_df` keeps the original, `clean_df` is the working copy
- Session state manages mutable UI state

**3. Logging**
- DataCleaner maintains execution log
- All operations are traceable

**4. Type Safety**
- Type hints throughout codebase
- Better IDE support and error detection

---

## Development Environment

### Recommended IDE Setup

**Visual Studio Code (Recommended)**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=120"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

**Extensions to Install:**
- Python (Microsoft)
- Pylance (Microsoft)
- Python Test Explorer
- GitLens

### Dev Container

Use the included dev container for consistent environment:

```bash
# Requires Docker and VS Code with Remote-Containers extension
code .
# Click "Reopen in Container" when prompted
```

Configuration at `.devcontainer/devcontainer.json`

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

The flake8 hook adds the `flake8-docstrings` plugin, which CI does not use, so `pre-commit run --all-files`
reports docstring codes (D1xx, D2xx, D4xx) on the current code. The CI lint gate is the Black, flake8 and mypy
steps in `.github/workflows/ci.yml`; `python scripts/verify_loop.py` runs those same steps locally.

Configured in `.pre-commit-config.yaml`:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black code formatting
- Flake8 linting
- MyPy type checking

---

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_cleaner.py

# Run one test (test_cleaner.py's tests are in a class, so the class is part of the id)
pytest tests/test_cleaner.py::TestDataCleaner::test_standardize_names

# Run tests matching pattern
pytest -k "cleaner"
```

### Test Coverage

```bash
# Run with coverage report (the source list is [tool.coverage.run] in pyproject.toml)
pytest --cov --cov-report=term

# Generate HTML coverage report
pytest --cov --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Test Structure

```python
# tests/test_cleaner.py example

import pandas as pd
from utils.cleaner import DataCleaner

class TestDataCleaner:
    def test_standardize_names(self):
        """Test that names are converted to Title Case."""
        # Arrange
        df = pd.DataFrame({
            'Name': ['john doe', 'JANE SMITH', 'Bob Wilson']
        })

        # Act
        cleaner = DataCleaner(df)
        cleaner.standardize_names()

        # Assert
        expected = ['John Doe', 'Jane Smith', 'Bob Wilson']
        assert cleaner.clean_df['Name'].tolist() == expected
```

### Writing New Tests

**Guidelines:**
1. One test per function/behavior
2. Use AAA pattern (Arrange, Act, Assert)
3. Test edge cases and error conditions
4. Keep tests independent and isolated
5. Use descriptive test names

**Example:**
```python
def test_data_generator_with_invalid_messiness_level():
    """Test that invalid messiness level raises ValueError."""
    with pytest.raises(ValueError):
        generate_messy_data(num_records=100, messiness_level="invalid")
```

---

## Code Style Guidelines

### Python Style (PEP 8 + Black)

**Line Length:** 120 characters maximum

**Formatting:**
```python
# Good
def my_function(param1: str, param2: int, param3: Optional[str] = None) -> Dict[str, Any]:
    """Clear docstring explaining purpose."""
    result = {"key": "value"}
    return result

# Bad
def my_function(param1,param2,param3=None):
    result={"key":"value"}
    return result
```

**Imports:**
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import pandas as pd
import streamlit as st
from faker import Faker

# Local
from utils.cleaner import DataCleaner
from utils.health_metrics import DataHealthMetrics
```

**Naming Conventions:**
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names over abbreviations

### Type Hints

**Always use type hints:**
```python
from typing import Optional, Dict, List, Union

def process_data(
    df: pd.DataFrame,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process data and return results."""
    ...
```

### Docstrings

**Use Google-style docstrings:**
```python
def calculate_score(df: pd.DataFrame, weights: Dict[str, float]) -> float:
    """
    Calculate weighted quality score for dataframe.
    
    Args:
        df: Input dataframe to score
        weights: Dictionary mapping metric names to weights
            Example: {"completeness": 0.4, "uniqueness": 0.3}
    
    Returns:
        float: Composite score from 0-100
    
    Raises:
        ValueError: If weights don't sum to 1.0
    
    Example:
        >>> df = pd.DataFrame({"col": [1, 2, 3]})
        >>> weights = {"completeness": 0.5, "uniqueness": 0.5}
        >>> score = calculate_score(df, weights)
        >>> print(f"Score: {score}%")
    """
    ...
```

### Comments

**When to comment:**
- Complex algorithms or business logic
- Non-obvious workarounds
- TODO/FIXME items

**When NOT to comment:**
- Obvious code (let code be self-documenting)
- Redundant docstrings

```python
# Good
# Using LOWESS smoothing to reduce noise in time series
smoothed = lowess(y, x, frac=0.3)

# Bad
# Set x to 5
x = 5
```

---

## Adding New Features

### Feature Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests First (TDD)**
   ```python
   # tests/test_new_feature.py
   def test_new_feature():
       # Write failing test first
       assert new_function() == expected_result
   ```

3. **Implement Feature**
   - Follow code style guidelines
   - Add type hints
   - Write comprehensive docstrings
   - Keep changes focused and minimal

4. **Run Tests**
   ```bash
   pytest tests/test_new_feature.py
   pytest  # All tests
   ```

5. **Update Documentation**
   - Update API.md if adding public functions
   - Update README.md if user-facing feature
   - Add CHANGELOG.md entry

6. **Commit Changes**
   ```bash
   git status                      # check nothing unexpected is listed
   git add path/to/changed_file.py tests/test_new_feature.py
   git commit -m "Add [feature]: Brief description"
   ```

7. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create pull request on GitHub
   ```

### Example: Adding a New Cleaning Step

```python
# utils/cleaner.py

class DataCleaner:
    # ... existing code ...
    
    def remove_emoji(self) -> None:
        """
        Remove emoji characters from text fields.
        
        Modifies self.clean_df in place by removing emoji from
        the Name column.
        """
        before_count = self.clean_df['Name'].str.contains('[^\x00-\x7F]').sum()
        
        # Remove non-ASCII characters
        self.clean_df['Name'] = self.clean_df['Name'].str.replace(
            r'[^\x00-\x7F]+', '', regex=True
        )
        
        after_count = self.clean_df['Name'].str.contains('[^\x00-\x7F]').sum()
        removed = before_count - after_count
        
        self.log.append(f"✓ Removed emoji from {removed} names")
```

**Add to tests:**
```python
# tests/test_cleaner.py

def test_remove_emoji():
    """Test that emoji are removed from names."""
    df = pd.DataFrame({
        'Name': ['John 😀', 'Jane Smith', 'Bob ❤️']
    })
    
    cleaner = DataCleaner(df)
    cleaner.remove_emoji()
    
    assert '😀' not in cleaner.clean_df['Name'].iloc[0]
    assert 'John' in cleaner.clean_df['Name'].iloc[0]
```

---

## Debugging Tips

### Streamlit Debugging

**Use st.write() for quick debugging:**
```python
import streamlit as st

st.write("Debug:", variable_name)
st.write("DataFrame shape:", df.shape)
st.write("Session state:", st.session_state)
```

**Check session state:**
```python
# Add debug panel
with st.expander("Debug Info"):
    st.write(st.session_state)
```

**Reload on changes:**
```bash
# Streamlit auto-reloads when files change
# Force reload: Click "Rerun" or press R
```

### Python Debugger

**Using pdb:**
```python
import pdb

def problematic_function():
    # Set breakpoint
    pdb.set_trace()
    
    # Code execution pauses here
    result = some_operation()
    return result
```

**Using VS Code debugger:**
1. Set breakpoint by clicking left of line number
2. Press F5 to start debugging
3. Use debug controls to step through code

### Common Issues

**Issue: Streamlit caching problems**
```python
# Clear cache
st.cache_data.clear()

# Or run with --server.runOnSave false
streamlit run app.py --server.runOnSave false
```

**Issue: Tests fail but code works**
```python
# Check for stale pyc files
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Reinstall the dependencies
pip install -r requirements-dev.txt
```

**Issue: Import errors**
```python
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd community-pulse
python -m pytest
```

---

## Performance Optimization

### Profiling

**Time profiling:**
```python
import time

start = time.time()
result = expensive_function()
print(f"Took {time.time() - start:.2f} seconds")
```

**Memory profiling:**
```python
import sys

df_memory = df.memory_usage(deep=True).sum() / 1024**2
print(f"DataFrame size: {df_memory:.2f} MB")
```

### Optimization Tips

**Pandas optimization:**
```python
# Good - vectorized operations
df['new_col'] = df['col1'] * df['col2']

# Bad - iterating rows
for idx, row in df.iterrows():
    df.at[idx, 'new_col'] = row['col1'] * row['col2']
```

**Streamlit caching:**
```python
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Cache expensive data loading."""
    return pd.read_csv(path)

@st.cache_resource
def create_connection():
    """Cache database connections."""
    return create_db_connection()
```

---

## Deployment

### Local Deployment

```bash
streamlit run app.py
```

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Deploy from main branch
5. Live at: `https://your-app-name.streamlit.app`

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
# Build and run
docker build -t community-pulse .
docker run -p 8501:8501 community-pulse
```

---

## Troubleshooting

### Installation Issues

**Problem: pip install fails**
```bash
# Update pip
python -m pip install --upgrade pip

# Try with --no-cache-dir
pip install --no-cache-dir -r requirements.txt
```

**Problem: Python version mismatch**
```bash
# Check version
python --version

# Use pyenv to manage versions
pyenv install 3.11
pyenv local 3.11
```

### Runtime Issues

**Problem: "Module not found" error**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Ensure in correct directory
pwd  # Should show .../community-pulse
```

**Problem: Streamlit won't start**
```bash
# Check if port is in use
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Use different port
streamlit run app.py --server.port=8502
```

---

## Resources

- **Python:** [python.org/docs](https://python.org/docs)
- **Pandas:** [pandas.pydata.org/docs](https://pandas.pydata.org/docs)
- **Streamlit:** [docs.streamlit.io](https://docs.streamlit.io)
- **Plotly:** [plotly.com/python](https://plotly.com/python)
- **Pytest:** [docs.pytest.org](https://docs.pytest.org)

---

## Getting Help

- **GitHub Issues:** [Report bugs, request features or ask questions](https://github.com/hilliersmmain/community-pulse/issues)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Happy coding! 🚀**
