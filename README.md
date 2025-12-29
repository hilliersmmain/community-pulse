# Community Pulse: Data Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.52+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/)
[![Tests: 70/70](https://img.shields.io/badge/Tests-70%2F70%20passing-brightgreen)](./tests)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-brightgreen)](.)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://community-pulse.streamlit.app/)

**End-to-end data analytics project:** Transform messy CSV data into clean, actionable insights with automated data cleaning pipelines, interactive visualizations, and comprehensive data quality metrics.

---

## Overview

A **production-ready data analytics dashboard** demonstrating professional data engineering and visualization:

- **Automated Data Cleaning:** Pipeline handles standardization, deduplication, and validation
- **Interactive Analytics:** Real-time Plotly visualizations for trends and insights
- **Data Quality Metrics:** Health scoring for completeness, uniqueness, and formatting
- **Full Test Coverage:** 70 unit tests ensure reliability

---

## Key Features

### 1. **Dashboard with Real-Time KPIs**
Monitor data quality with health scores and metrics.

![Dashboard Overview](./docs/screenshots/dashboard-overview.png)

### 2. **Automated Cleaning Pipeline**
Configurable data cleaning with execution logs.

![Data Cleaning Pipeline](./docs/screenshots/data-cleaning-pipeline.png)

**Steps:** Name standardization • Email validation • Deduplication • Date formatting • Missing value handling

### 3. **Before/After Comparison**
Visualize cleaning impact with side-by-side metrics.

![Before/After Comparison](./docs/screenshots/before-after-comparison.png)

### 4. **Interactive Analytics**
Explore trends, distributions, and demographics.

![Analytics - Trends](./docs/screenshots/analytics-trends.png)
![Analytics - Distribution](./docs/screenshots/analytics-distribution.png)

### 5. **Data Explorer**
Inspect data with detailed health metrics.

![Data Explorer](./docs/screenshots/data-explorer.png)

### 6. **Additional Features**
- Synthetic data generation (100-1000 records, configurable quality)
- CSV/JSON export with timestamps
- High-resolution chart exports

---

## Quick Start

**Prerequisites:** Python 3.9+

```bash
# Clone and install
git clone https://github.com/hilliersmmain/community_pulse.git
cd community_pulse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open browser to `http://localhost:8501`

**Try the [Live Demo](https://community-pulse.streamlit.app/)** (no installation needed)

---

## Usage Guide

**Workflow:**
1. **Generate Data** — Adjust records (100-1000) and messiness level, click "Generate New Data"
2. **Configure Cleaning** — Toggle cleaning steps in sidebar or use defaults
3. **Run Cleaning** — Navigate to "Data Cleaning Ops" tab, click "Run Cleaning Algorithms"
4. **Analyze Results** — View analytics dashboard, filter by roles, explore charts
5. **Export** — Download CSV/JSON or export charts as PNG

---

## Project Structure

```
community_pulse/
├── app.py                    # Main Streamlit app
├── utils/                    # Core modules
│   ├── data_generator.py     # Synthetic data generation
│   ├── cleaner.py            # Data cleaning pipeline
│   ├── visualizer.py         # Plotly charts
│   ├── health_metrics.py     # Quality scoring
│   └── ui_helpers.py         # UI components
├── tests/                    # 70 unit tests
└── docs/                     # Documentation
```

---

## Testing

```bash
pytest                              # Run all 70 tests
pytest --cov=utils                  # Coverage report
python verify_setup.py              # Verify installation
```

**Status:** 70/70 tests passing ✓

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **Frontend** | Streamlit 1.52+ | Interactive web UI |
| **Data Processing** | Pandas 2.2+ | DataFrame manipulation |
| **Visualization** | Plotly 6.5+ | Interactive charts |
| **Testing** | pytest 9.0+ | 70 unit tests |
| **Data Generation** | Faker, NumPy | Synthetic data |

---

## How It Works

**Data Generation:** Creates realistic CSV with intentional quality issues (missing values, format errors, duplicates)

**Cleaning Pipeline:** Multi-step process with logging
```python
cleaner = DataCleaner(raw_df)
clean_df = cleaner.clean_all(steps=[
    'standardize_names', 'fix_emails', 'remove_duplicates', 
    'clean_dates', 'handle_missing_values'
])
```

**Health Scoring:** `Overall = 40% Completeness + 30% Uniqueness + 30% Formatting`

---

## Example Results

**Before:** 500 records • 50 duplicates (10%) • 23 missing values • Health: 72%  
**After:** 450 records • 0 duplicates • 0 missing values • Health: 98% (+26%)

---

## Deployment

**Streamlit Cloud (Recommended):** Push to GitHub → [share.streamlit.io](https://share.streamlit.io) → Deploy  
**Live Demo:** [community-pulse.streamlit.app](https://community-pulse.streamlit.app/)

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## Skills Demonstrated

**Python & Data Engineering**
- Modular architecture with reusable components
- Data transformation pipelines and validation
- Error handling and logging

**Data Analysis & Visualization**
- Interactive Plotly charts with statistical overlays
- Health scoring algorithms
- DataFrame operations (filtering, grouping, aggregation)

**Software Development**
- 70 comprehensive unit tests
- Type hints and documentation
- CI/CD deployment to Streamlit Cloud

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Enhancement Ideas:** Database backend • Multi-file upload • Advanced filtering • ML anomaly detection • API layer

---

## Documentation

**For Users:**
- [README.md](./README.md) — Project overview and quick start
- [CHANGELOG.md](./CHANGELOG.md) — Version history and release notes

**For Developers:**
- [API.md](./docs/API.md) — Complete API reference for all modules
- [DEVELOPMENT.md](./docs/DEVELOPMENT.md) — Developer setup and contribution guide
- [ARCHITECTURAL_OVERVIEW.md](./docs/ARCHITECTURAL_OVERVIEW.md) — System design and architecture
- [KPI_DEFINITIONS.md](./docs/KPI_DEFINITIONS.md) — Data quality metrics explained
- [SOP_DATA_CLEANING.md](./docs/SOP_DATA_CLEANING.md) — Standard operating procedures

**For Recruiters:**
- [PORTFOLIO.md](./PORTFOLIO.md) — Skills demonstration and project showcase
- [CONTRIBUTING.md](./CONTRIBUTING.md) — Contribution guidelines

---

## License

MIT License — see [LICENSE](./LICENSE)

---

## Author

**Samuel M. Hillier** • [@hilliersmmain](https://github.com/hilliersmmain)

---

## Built With

[Streamlit](https://streamlit.io) • [Plotly](https://plotly.com) • [Pandas](https://pandas.pydata.org) • [Faker](https://github.com/joke2k/faker)
