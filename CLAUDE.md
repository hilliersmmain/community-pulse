# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

*Auto-generated on 2026-04-23 by `scripts/update_claude_md.py`*

## Project Overview

Community Pulse is a data analytics dashboard built with Streamlit that automates the data engineering lifecycle — ingestion, cleaning, validation, and visualization of community data. Live at https://community-pulse.streamlit.app/.

## Commands

```bash
# Run the app
streamlit run app.py

# Run all tests (108 tests collected, 60.22% coverage)
pytest

# Run a specific test file
pytest tests/test_cleaner.py -v

# Run a single test
pytest tests/test_cleaner.py::TestDataCleaner::test_remove_duplicates -v

# Coverage report
pytest --cov=utils --cov=community_pulse --cov-report=term-missing

# Format (Black, line-length 120)
black utils/ community_pulse/ components/ tests/ app.py

# Lint
flake8 utils/ community_pulse/ components/ --max-line-length=120 --ignore=E203,W503,E501

# Type check
mypy utils/ community_pulse/ components/ --ignore-missing-imports

# All pre-commit checks
pre-commit run --all-files

# Regenerate this file
python scripts/update_claude_md.py
```

## Architecture

**Data flow:** `DataGenerator / CSV Upload → DataCleaner → DataHealthMetrics → Visualizer → Streamlit UI`

### app.py (112 lines) — Thin orchestrator
Loads data, initializes state, calls component render functions.

### components/ — UI components
- `components/comparison.py`
- `components/kpi_display.py`
- `components/sidebar.py`
- `components/tab_analytics.py`
- `components/tab_explorer.py`
- `components/tab_preparation.py`

### utils/ — Core business logic
- `utils/cleaner.py`
- `utils/constants.py`
- `utils/data_access.py`
- `utils/data_generator.py`
- `utils/health_metrics.py`
- `utils/session_keys.py`
- `utils/ui_helpers.py`
- `utils/upload_validation.py`
- `utils/visualizer.py`

### Key modules
- `utils/cleaner.py` — `DataCleaner` class with 5-step pipeline: standardize_names → fix_emails → remove_duplicates → clean_dates → handle_missing_values
- `utils/health_metrics.py` — `DataHealthMetrics` class. Composite score = 40% completeness + 30% uniqueness + 30% formatting
- `utils/visualizer.py` — Plotly chart functions (attendance trend with LOWESS, role pie chart, attendance histogram)
- `utils/constants.py` — All configuration constants (DATA_PATH, defaults, CSS, thresholds)
- `community_pulse/demo_charts.py` — Demo chart generation for documentation

## Code Style

- **Black** with 120-char line length, targeting Python 3.9+
- **Flake8** ignoring E203, W503, E501
- Pre-commit hooks enforce formatting, linting, type checking, and security scanning (Bandit)
- CI runs on GitHub Actions: Black → Flake8 → mypy → pytest → coverage → Bandit

## Testing

Tests are in `tests/` and use pytest. Coverage is configured to measure `utils/` and `community_pulse/`. The CI pipeline uploads coverage to Codecov.
