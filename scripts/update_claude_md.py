#!/usr/bin/env python3
"""Auto-generate CLAUDE.md from current project state.

Discovers modules, counts tests, reads config, and produces an up-to-date
CLAUDE.md so future Claude Code sessions have accurate context.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _find_python():
    """Return the best Python executable — prefer the project venv."""
    venv_python = PROJECT_ROOT / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def count_tests():
    """Run pytest --co -q to count tests without executing them."""
    try:
        result = subprocess.run(
            [_find_python(), "-m", "pytest", "--co", "-q", "tests/"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        # Line is like "== 106 tests collected in 0.42s =="
        for line in result.stdout.strip().splitlines():
            if "test" in line and "collected" in line:
                # Extract just the "N tests collected" part
                match = re.search(r"(\d+ tests? collected)", line)
                if match:
                    return match.group(1)
                return line.strip()
        return "unknown"
    except Exception:
        return "unknown"


def get_coverage_summary():
    """Run pytest with coverage and extract the total percentage."""
    try:
        result = subprocess.run(
            [
                _find_python(),
                "-m",
                "pytest",
                "--cov=utils",
                "--cov=community_pulse",
                "--cov-report=term",
                "-q",
                "--tb=no",
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        for line in result.stdout.strip().splitlines():
            if line.startswith("TOTAL"):
                parts = line.split()
                return parts[-1]  # e.g., "85%"
        return "unknown"
    except Exception:
        return "unknown"


def discover_modules(directory):
    """List Python modules in a directory."""
    modules = []
    path = PROJECT_ROOT / directory
    if not path.exists():
        return modules
    for f in sorted(path.iterdir()):
        if f.suffix == ".py" and f.name != "__init__.py":
            modules.append(f.stem)
    return modules


def get_app_line_count():
    """Count lines in app.py."""
    app_path = PROJECT_ROOT / "app.py"
    if app_path.exists():
        return sum(1 for _ in open(app_path))
    return 0


def _format_module_list(directory, modules):
    """Format a list of modules as markdown bullet points."""
    if not modules:
        return "- (none)"
    return "\n".join(f"- `{directory}/{m}.py`" for m in modules)


def generate_claude_md():
    """Generate the CLAUDE.md content."""
    test_count = count_tests()
    coverage = get_coverage_summary()
    utils_modules = discover_modules("utils")
    component_modules = discover_modules("components")
    app_lines = get_app_line_count()
    date_str = datetime.now().strftime("%Y-%m-%d")
    components_list = _format_module_list("components", component_modules)
    utils_list = _format_module_list("utils", utils_modules)

    content = f"""\
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

*Auto-generated on {date_str} by `scripts/update_claude_md.py`*

## Project Overview

Community Pulse is a data analytics dashboard built with Streamlit that automates the data engineering lifecycle — ingestion, cleaning, validation, and visualization of community data. Live at https://community-pulse.streamlit.app/.

## Commands

```bash
# Run the app
streamlit run app.py

# Run all tests ({test_count}, {coverage} coverage)
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

### app.py ({app_lines} lines) — Thin orchestrator
Loads data, initializes state, calls component render functions.

### components/ — UI components
{components_list}

### utils/ — Core business logic
{utils_list}

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
"""
    return content


def main():
    content = generate_claude_md()
    output_path = PROJECT_ROOT / "CLAUDE.md"
    output_path.write_text(content)
    print(f"Updated {output_path}")


if __name__ == "__main__":
    main()
