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

- **Python:** 3.9 or higher
- **pip:** Latest version recommended
- **Virtual Environment:** venv, conda, or pyenv
- **Git:** For version control
- **Operating System:** Windows, macOS, or Linux

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/hilliersmmain/community_pulse.git
   cd community_pulse
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
   # Install main dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (optional)
   pip install -e ".[dev]"
   ```

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

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Tests passing (70/70)
- [ ] Application runs without errors
- [ ] Can generate data and perform cleaning

---

## Project Architecture

### Directory Structure

```
community_pulse/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Modern Python packaging configuration
├── verify_setup.py                 # Installation verification script
│
├── utils/                          # Core business logic modules
│   ├── __init__.py                # Package initializer
│   ├── data_generator.py          # Synthetic data generation
│   ├── cleaner.py                 # Data cleaning pipeline
│   ├── health_metrics.py          # Quality scoring algorithms
│   ├── visualizer.py              # Plotly chart generation
│   └── ui_helpers.py              # Streamlit UI components
│
├── community_pulse/                # Additional modules
│   ├── __init__.py
│   └── demo_charts.py             # Demo visualization examples
│
├── tests/                          # Comprehensive test suite
│   ├── __init__.py
│   ├── test_data_generator.py     # Data generation tests
│   ├── test_cleaner.py            # Cleaning pipeline tests
│   ├── test_health_metrics.py     # Metrics calculation tests
│   ├── test_visualizer.py         # Chart rendering tests
│   ├── test_ui_helpers.py         # UI component tests
│   ├── test_demo_charts.py        # Demo tests
│   └── test_emoji_removal.py      # Text sanitization tests
│
├── docs/                           # Documentation
│   ├── API.md                     # API reference
│   ├── DEVELOPMENT.md             # This file
│   ├── ARCHITECTURAL_OVERVIEW.md  # System architecture
│   ├── KPI_DEFINITIONS.md         # Metric definitions
│   ├── SOP_DATA_CLEANING.md       # Cleaning procedures
│   └── screenshots/               # UI screenshots
│
├── .github/                        # GitHub configuration
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
│
├── .devcontainer/                  # Dev container configuration
│   └── devcontainer.json
│
├── .streamlit/                     # Streamlit configuration
│   └── config.toml
│
├── data/                           # Generated data (gitignored)
├── artifacts/                      # Project reports and analysis
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT License
└── README.md                       # Project overview
```

### Module Overview

#### `app.py` - Main Application
- Entry point for Streamlit dashboard
- Handles page layout and navigation
- Manages session state
- Coordinates all UI components

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

#### `utils/ui_helpers.py` - UI Components
- **Purpose:** Reusable Streamlit UI elements
- **Key Functions:** `show_welcome_modal()`, `show_empty_state()`, `show_loading_message()`
- **Use Case:** Consistent user experience

### Data Flow

```
User Input (Sidebar)
    ↓
Data Generation (data_generator.py)
    ↓
Raw DataFrame
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
- UI logic in `app.py` and `ui_helpers.py`
- Business logic in `utils/` modules
- Tests in separate `tests/` directory

**2. Immutability**
- DataCleaner creates copies to preserve originals
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

# Run specific test function
pytest tests/test_cleaner.py::test_standardize_names

# Run tests matching pattern
pytest -k "cleaner"
```

### Test Coverage

```bash
# Run with coverage report
pytest --cov=utils --cov=community_pulse

# Generate HTML coverage report
pytest --cov=utils --cov=community_pulse --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Test Structure

```python
# tests/test_cleaner.py example

import pytest
import pandas as pd
from utils.cleaner import DataCleaner

def test_standardize_names():
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
    assert cleaner.df['Name'].tolist() == expected
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
   git add .
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
        
        Modifies self.df in-place by removing emoji from
        Name and other text columns.
        """
        before_count = self.df['Name'].str.contains('[^\x00-\x7F]').sum()
        
        # Remove non-ASCII characters
        self.df['Name'] = self.df['Name'].str.replace(
            r'[^\x00-\x7F]+', '', regex=True
        )
        
        after_count = self.df['Name'].str.contains('[^\x00-\x7F]').sum()
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
    
    assert '😀' not in cleaner.df['Name'].iloc[0]
    assert 'John' in cleaner.df['Name'].iloc[0]
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

# Reinstall in development mode
pip install -e .
```

**Issue: Import errors**
```python
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /path/to/community_pulse
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
FROM python:3.9-slim

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
pwd  # Should show .../community_pulse
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

- **GitHub Issues:** [Report bugs or request features](https://github.com/hilliersmmain/community_pulse/issues)
- **Discussions:** [Ask questions](https://github.com/hilliersmmain/community_pulse/discussions)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Happy coding! 🚀**
