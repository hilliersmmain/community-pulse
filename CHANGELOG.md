# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **CI lint enforcement restored**: Flake8 complexity checks (`--max-complexity=10`) now fail correctly instead of being suppressed.
- **Bandit behavior restored to advisory**: Security scan output is retained in CI logs/artifacts, but low-severity findings (e.g., demo data generator `B311`) no longer fail the build.
- **CSV upload UX safety**: Invalid uploads no longer short-circuit sidebar rendering; downstream controls remain available.
- **Data generator refactor**: Split `generate_messy_data()` into smaller helpers to satisfy complexity linting while preserving behavior.
- **Upload contract clarified**: Required CSV schema documented as `Name`, `Email`, `Role`, `Join_Date`, and `Event_Attendance`.

## [2.0.0] - 2026-04-02

### Added
- **CSV Upload Feature**: Upload custom CSV files as alternative to synthetic data generation
  - Column validation ensures required fields (Name, Email) are present
  - Seamless integration with existing cleaning pipeline
- **Self-Modifying CLAUDE.md**: Script to auto-generate project documentation
  - Discovers modules, counts tests, measures coverage
  - Run with `python scripts/update_claude_md.py`

### Changed
- **Major Architecture Refactor**: Decomposed 883-line monolithic app.py into modular components
  - app.py reduced to 111-line thin orchestrator
  - Created `components/` package with 6 focused UI modules
  - Each component exposes a single `render()` function
- **Extracted Constants**: Created `utils/constants.py` for all configuration values
  - Eliminated magic numbers and strings throughout codebase
  - Centralized CSS, thresholds, defaults, and cleaning step configuration
- **CI Pipeline Hardened**: Black check now blocks builds, mypy added to pipeline
- **Test Suite Expanded**: 70 → 106 tests with comprehensive edge case coverage

### Fixed
- Redundant double deduplication in `cleaner.py` (was doing full-row + email dedup)
- Weak email regex in cleaner (now matches health_metrics standard)
- NaN-unsafe statistics calculation in visualizer
- Invalid type hint (`Optional[callable]` → `Optional[Callable]`)
- Duplicate CSS property in welcome modal
- Bare `except:` clause replaced with `except Exception:`
- README typos: "neruoscience", "Aritifical", "fundementals"
- Unused imports in demo_charts.py
- mypy type errors in health_metrics.py and cleaner.py

### Removed
- Dead code: `show_whats_new()` function call (session state always False)
- Commented-out PDF export and report sections
- Unused `stats_label` variable

## [1.0.0] - 2025-12-29

### Added
- **Interactive Streamlit Dashboard**
  - Real-time KPIs with dynamic health scoring
  - Configurable data cleaning pipeline with 5 steps
  - Before/after comparison visualizations
  - Tutorial mode for first-time users
  - Dark/light mode support

- **Data Cleaning Pipeline**
  - Name standardization (Title Case formatting)
  - Email validation and correction
  - Duplicate removal based on email/name matching
  - Date format standardization (YYYY-MM-DD)
  - Missing value handling with intelligent defaults

- **Interactive Analytics**
  - Time-series attendance trend charts with LOWESS smoothing
  - Distribution histograms with statistical overlays (mean, median)
  - Demographic pie charts with role breakdowns
  - High-resolution chart exports (PNG format via Plotly)
  - Responsive design supporting mobile/tablet views

- **Data Quality Metrics**
  - Composite health scoring algorithm (40% completeness, 30% uniqueness, 30% formatting)
  - Column-level diagnostics for granular insights
  - Real-time metric updates in sidebar
  - Detailed tooltips for all KPIs

- **Data Generation**
  - Synthetic data generator using Faker library
  - Configurable record count (100-1000)
  - Three messiness levels: low (3% issues), medium (10% issues), high (20% issues)
  - Realistic simulation of data quality problems

- **Export Functionality**
  - CSV export with timestamp naming
  - JSON export with formatted output
  - Separate export options for raw vs cleaned data
  - Chart export as high-resolution PNG images

- **UI/UX Features**
  - Welcome modal for new users
  - "What's New" panel highlighting recent updates
  - Contextual help messages and tooltips
  - Loading indicators for long operations
  - Success/error notifications with detailed feedback

### Documentation
- Comprehensive README with badges, screenshots, and live demo link
- [ARCHITECTURAL_OVERVIEW.md](./docs/ARCHITECTURAL_OVERVIEW.md) - System architecture and design patterns
- [KPI_DEFINITIONS.md](./docs/KPI_DEFINITIONS.md) - Detailed metric calculations
- [SOP_DATA_CLEANING.md](./docs/SOP_DATA_CLEANING.md) - Standard operating procedures
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- Full docstring coverage for all public functions
- Type hints for improved IDE support

### Infrastructure
- **CI/CD Pipeline**
  - GitHub Actions workflow for automated testing
  - 70 comprehensive unit tests with pytest
  - Python 3.11 compatibility testing
  - Automated test execution on push/PR

- **Deployment**
  - Streamlit Cloud deployment at [community-pulse.streamlit.app](https://community-pulse.streamlit.app/)
  - Dev container configuration for consistent development environment
  - Environment configuration examples

### Testing
- 70 unit tests covering all core modules:
  - `test_cleaner.py` - Data cleaning pipeline tests
  - `test_data_generator.py` - Synthetic data generation tests
  - `test_health_metrics.py` - Quality scoring tests
  - `test_visualizer.py` - Chart rendering tests
  - `test_ui_helpers.py` - UI component tests
  - `test_emoji_removal.py` - Text sanitization tests
- 85% test coverage (core modules)
- All tests passing (70/70)

### Performance
- Processes 1,000 records in <1 second
- Efficient pandas operations for data manipulation
- Optimized Plotly rendering for large datasets
- Memory usage <100MB for typical workloads

### Security
- Input validation for all user inputs
- No sensitive data stored in repository
- Secure handling of file uploads/downloads
- MIT License for open collaboration

## [0.1.0] - 2025-12-01

### Initial Development
- Basic data cleaning functionality
- Simple Streamlit interface
- Core data generation module
- Initial test suite

---

## Release Notes

### Version 1.0.0 Highlights

This release represents the first production-ready version of Community Pulse, featuring:

**For Data Analysts:**
- Automated data cleaning that reduces manual effort by 90%+
- Visual before/after comparisons to validate cleaning operations
- Export cleaned data in multiple formats (CSV, JSON)

**For Developers:**
- Well-documented, modular codebase following Python best practices
- Comprehensive test coverage ensuring reliability
- Easy to extend with new cleaning algorithms or visualizations

**For Hiring Managers:**
- Demonstrates production-ready software engineering skills
- Shows proficiency in data engineering, visualization, and web development
- Highlights testing, documentation, and deployment expertise

### Upgrade Instructions

First installation - no upgrade needed. See [README.md](./README.md) for setup instructions.

### Known Limitations

- Single-file processing only (multi-file batch processing planned for v2.0)
- In-memory processing (database backend planned for v2.0)
- Basic statistical overlays (advanced ML anomaly detection planned for v2.0)

### Future Roadmap

See [CONTRIBUTING.md](./CONTRIBUTING.md) for planned enhancements including:
- Multi-file upload and batch processing
- PostgreSQL database backend
- RESTful API for programmatic access
- Machine learning-based anomaly detection
- Advanced filtering with saved views
- Scheduled cleaning jobs
- Email reports and notifications

---

[2.0.0]: https://github.com/hilliersmmain/community_pulse/releases/tag/v2.0.0
[1.0.0]: https://github.com/hilliersmmain/community_pulse/releases/tag/v1.0.0
[0.1.0]: https://github.com/hilliersmmain/community_pulse/releases/tag/v0.1.0
