# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Community Pulse is a data analytics dashboard built with Streamlit that automates the data engineering lifecycle — ingestion, cleaning, validation, and visualization of community data. Live at https://community-pulse.streamlit.app/.

## Commands

```bash
# Run the app
streamlit run app.py

# Run all tests (70 tests, 85% coverage)
pytest

# Run a specific test file
pytest tests/test_cleaner.py -v

# Run a single test
pytest tests/test_cleaner.py::TestDataCleaner::test_remove_duplicates -v

# Coverage report
pytest --cov=utils --cov=community_pulse --cov-report=term-missing

# Format (Black, line-length 120)
black utils/ community_pulse/ tests/ app.py

# Lint
flake8 utils/ community_pulse/ --max-line-length=120 --ignore=E203,W503,E501

# Type check
mypy utils/ community_pulse/ --ignore-missing-imports

# All pre-commit checks
pre-commit run --all-files
```

## Architecture

**Data flow:** `DataGenerator → DataCleaner → DataHealthMetrics → Visualizer → Streamlit UI`

- `app.py` — Main Streamlit application, orchestrates everything
- `utils/data_generator.py` — Generates synthetic community data with configurable messiness levels (low/medium/high)
- `utils/cleaner.py` — `DataCleaner` class with a 5-step pipeline: standardize_names → fix_emails → remove_duplicates → clean_dates → handle_missing_values. Preserves raw data and logs each step.
- `utils/visualizer.py` — Plotly chart functions (attendance trend with LOWESS, role pie chart, attendance histogram)
- `utils/health_metrics.py` — `DataHealthMetrics` class. Composite score = 40% completeness + 30% uniqueness + 30% formatting
- `utils/ui_helpers.py` — Streamlit UI components, session state management, tutorial system, message templates
- `community_pulse/demo_charts.py` — Demo chart generation

## Code Style

- **Black** with 120-char line length, targeting Python 3.9+
- **Flake8** ignoring E203, W503, E501
- Pre-commit hooks enforce formatting, linting, type checking, and security scanning (Bandit)
- CI runs on GitHub Actions: Black → Flake8 → pytest → coverage → Bandit

## Testing

Tests are in `tests/` and use pytest. Coverage is configured to measure `utils/` and `community_pulse/`. The CI pipeline uploads coverage to Codecov.
